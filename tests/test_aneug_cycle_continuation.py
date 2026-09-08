from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from torch import nn

from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_cycle_continuation import CONTINUATION_INVARIANTS
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256


class StochasticCycle(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(3, 8), nn.Dropout(0.3), nn.Linear(8, 240))

    def forward_cycle(self, case):
        out = self.network(case["coordinates"])
        return out.reshape(len(out), 80, 3).permute(1, 0, 2)


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        torch.manual_seed(5)
        self.cases = [dict(coordinates=torch.randn(4, 3), normals=torch.randn(4, 3),
                           vertex_weights=torch.ones(4) / 4, wss=torch.randn(80, 4, 3)) for _ in range(3)]
        self.opt = dict(seed=3, epochs=2, accumulation_cases=2, validation_interval=1,
                        checkpoint_interval=1, learning_rate=3e-4, weight_decay=1e-4,
                        step_size_epochs=1, gamma=0.75, gradient_clip_norm=1.0)
        self.provenance = {key: "synthetic" for key in CONTINUATION_INVARIANTS}
        self.provenance.update(torch=str(torch.__version__), cuda=None,
                               historical_test_already_opened=True, cycle_output_scale=1.0)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def run_curve(self, path, epochs, continuation=None, optimization=None, provenance=None):
        return train_cycles(StochasticCycle(), self.cases, self.cases[:1],
            optimization=optimization or dict(self.opt, epochs=epochs),
            reference_tawss_floor=1e-4, output_directory=self.root / path,
            provenance=provenance or self.provenance, device=torch.device("cpu"),
            continuation=continuation, log=lambda _: None)

    def prepare_parent(self):
        torch.manual_seed(31)
        self.run_curve("parent", 2)
        cp, result = self.root / "parent/checkpoints/epoch_002.pt", self.root / "parent/result.json"
        return dict(checkpoint=str(cp), checkpoint_sha256=file_sha256(cp),
                    parent_result=str(result), parent_result_sha256=file_sha256(result))

    def test_dropout_weights_optimizer_scheduler_and_selection_match_uninterrupted(self):
        torch.manual_seed(31)
        whole = self.run_curve("whole", 4)
        continuation = self.prepare_parent()
        torch.manual_seed(999)  # New process construction must not reset parent RNG.
        resumed = self.run_curve("resumed", 4, continuation)
        full = torch.load(self.root / "whole/checkpoints/epoch_004.pt", weights_only=True)
        part = torch.load(self.root / "resumed/checkpoints/epoch_004.pt", weights_only=True)
        for key, tensor in full["model_state_dict"].items():
            self.assertTrue(torch.equal(tensor, part["model_state_dict"][key]), key)
        for key, state in full["optimizer_state_dict"]["state"].items():
            for name, tensor in state.items():
                self.assertTrue(torch.equal(tensor, part["optimizer_state_dict"]["state"][key][name]))
        self.assertEqual(full["scheduler_state_dict"], part["scheduler_state_dict"])
        self.assertTrue(torch.equal(full["rng_state"]["torch_rng_state"], part["rng_state"]["torch_rng_state"]))
        for key in ("selected_validation", "selected_epoch", "training_cycle_exposures",
                    "training_phase_field_exposures", "optimizer_updates", "validation_cycle_forwards"):
            self.assertEqual(whole[key], resumed[key], key)
        self.assertEqual(resumed["segment_training_cycle_exposures"], 6)
        self.assertEqual(resumed["segment_optimizer_updates"], 4)
        self.assertFalse(resumed["continuation"]["new_independent_seed"])
        self.assertEqual(file_sha256(Path(continuation["checkpoint"])), continuation["checkpoint_sha256"])
        for epoch in (1, 2):
            self.assertEqual(file_sha256(self.root / f"parent/epochs/epoch_{epoch:03d}.json"),
                             file_sha256(self.root / f"resumed/epochs/epoch_{epoch:03d}.json"))

    def test_bad_hash_rejected_before_checkpoint_load(self):
        continuation = self.prepare_parent()
        continuation["checkpoint_sha256"] = "0" * 64
        with patch("aurora.aneug_cycle_continuation.torch.load") as load:
            with self.assertRaisesRegex(ValueError, "checkpoint hash"):
                self.run_curve("bad", 4, continuation)
            load.assert_not_called()

    def test_changed_optimization_or_data_is_not_silent_resume(self):
        continuation = self.prepare_parent()
        with self.assertRaisesRegex(ValueError, "optimization changed"):
            self.run_curve("bad_lr", 4, continuation,
                           optimization=dict(self.opt, epochs=4, learning_rate=1e-3))
        provenance = dict(self.provenance, train_loader_order_sha256="changed")
        with self.assertRaisesRegex(ValueError, "provenance invariant"):
            self.run_curve("bad_data", 4, continuation, provenance=provenance)

    def test_no_duplicate_training_of_completed_epoch_budget(self):
        continuation = self.prepare_parent()
        with self.assertRaisesRegex(ValueError, "extend total epoch"):
            self.run_curve("same_budget", 2, continuation)

    def test_earliest_best_survives_extension_and_scope_is_not_relabelled(self):
        evaluation = {"aggregate": {"field_relative_l2": 1.0}, "case_count": 1}
        with patch("aurora.aneug_architecture_development.evaluate_cycles", return_value=evaluation):
            continuation = self.prepare_parent()
            result = self.run_curve("tie", 4, continuation)
        self.assertEqual(result["selected_epoch"], 1)
        self.assertFalse(result["independent_confirmatory_evaluation"])
        self.assertGreater(result["elapsed_training_and_validation_seconds"],
                           result["segment_elapsed_training_and_validation_seconds"])


if __name__ == "__main__":
    unittest.main()

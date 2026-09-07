import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from torch import nn

from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_frozen_prior_reuse import load_completed_steady_prior
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256, _strict_atomic_torch_save
from aurora.aneug_steady_prior_training import train_steady_prior


class SyntheticInterruption(RuntimeError):
    pass


class TinyPrior(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, 8), nn.BatchNorm1d(8), nn.Dropout(.2), nn.Linear(8, 3))

    def forward(self, case):
        return self.net(case["coordinates"])


class StochasticCycle(nn.Module):
    def __init__(self, prior=None):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, 8), nn.Dropout(.3), nn.Linear(8, 240))
        self.prior = prior
        if prior is not None:
            prior.requires_grad_(False)
            prior.eval()

    def train(self, mode=True):
        super().train(mode)
        if self.prior is not None:
            self.prior.eval()
        return self

    def forward_cycle(self, case):
        x = case["coordinates"]
        if self.prior is not None:
            x = x + self.prior({"coordinates": x})
        y = self.net(x)
        return y.reshape(len(y), 80, 3).permute(1, 0, 2)


class InterruptedCycleRecoveryTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        torch.manual_seed(19)
        self.cases = [dict(coordinates=torch.randn(4, 3), normals=torch.randn(4, 3),
            vertex_weights=torch.ones(4) / 4, wss=torch.randn(80, 4, 3)) for _ in range(3)]
        self.opt = dict(seed=3, epochs=4, accumulation_cases=2, validation_interval=1,
            checkpoint_interval=1, learning_rate=3e-4, weight_decay=1e-4,
            step_size_epochs=2, gamma=.75, gradient_clip_norm=1.)
        self.provenance = {"synthetic": True, "inputs": "fixed", "model": "fixed"}
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_model(self, model, name, recovery=None, provenance=None):
        return train_cycles(model, self.cases, self.cases[:1], optimization=self.opt,
            reference_tawss_floor=1e-4, output_directory=self.root / name,
            provenance=self.provenance if provenance is None else provenance,
            device=torch.device("cpu"), interrupted_recovery=recovery, log=lambda _: None)

    def interrupt(self, model):
        def save_then_interrupt(path, value):
            _strict_atomic_torch_save(path, value)
            if path.name == "epoch_002.pt":
                raise SyntheticInterruption("synthetic process exit after a complete epoch checkpoint")
        with patch("aurora.aneug_architecture_development._strict_atomic_torch_save", save_then_interrupt):
            with self.assertRaises(SyntheticInterruption):
                self.run_model(model, "interrupted")
        self.assertFalse((self.root / "interrupted/result.json").exists())
        terminal = self.root / "terminal.json"
        terminal.write_text(json.dumps(dict(schema_version="aurora.interrupted_attempt_evidence.v3",
            state="F", run_count=1, exit_status=271, reason="walltime",
            scientific_result_present=False, recovery_authorized=True)))
        checkpoint = self.root / "interrupted/checkpoints/epoch_002.pt"
        return dict(checkpoint=str(checkpoint), checkpoint_sha256=file_sha256(checkpoint),
            terminal_evidence=str(terminal), terminal_evidence_sha256=file_sha256(terminal))

    def test_true_interruption_matches_uninterrupted_weights_optimizer_rng_and_best(self):
        torch.manual_seed(29)
        full = self.run_model(StochasticCycle(), "full")
        torch.manual_seed(29)
        recovery = self.interrupt(StochasticCycle())
        torch.manual_seed(999)
        resumed = self.run_model(StochasticCycle(), "resumed", recovery)
        a = torch.load(self.root / "full/checkpoints/epoch_004.pt", weights_only=True)
        b = torch.load(self.root / "resumed/checkpoints/epoch_004.pt", weights_only=True)
        for key in ("model_state_dict", "best_state_dict"):
            for name, value in a[key].items():
                torch.testing.assert_close(value, b[key][name], rtol=0, atol=0)
        for key, state in a["optimizer_state_dict"]["state"].items():
            for name, value in state.items():
                torch.testing.assert_close(value, b["optimizer_state_dict"]["state"][key][name], rtol=0, atol=0)
        self.assertEqual(a["scheduler_state_dict"], b["scheduler_state_dict"])
        torch.testing.assert_close(a["rng_state"]["torch_rng_state"], b["rng_state"]["torch_rng_state"], rtol=0, atol=0)
        for key in ("selected_validation", "selected_epoch", "training_cycle_exposures",
                    "training_phase_field_exposures", "optimizer_updates", "validation_cycle_forwards"):
            self.assertEqual(full[key], resumed[key])
        self.assertEqual(resumed["segment_training_cycle_exposures"], 6)
        self.assertIsNone(resumed["recovery_accounting"]["total_actual_training_cycle_exposures"])
        self.assertFalse(resumed["continuation"]["new_independent_seed"])
        self.assertEqual(file_sha256(Path(recovery["checkpoint"])), recovery["checkpoint_sha256"])
        for epoch in (1, 2):
            self.assertEqual((self.root / f"interrupted/epochs/epoch_{epoch:03d}.json").read_bytes(),
                             (self.root / f"resumed/epochs/epoch_{epoch:03d}.json").read_bytes())

    def test_legacy_missing_cost_remains_unknown_not_zero_or_pbs_training_time(self):
        recovery = self.interrupt(StochasticCycle())
        cp = torch.load(recovery["checkpoint"], weights_only=True)
        cp.pop("execution_accounting")
        legacy = self.root / "legacy.pt"
        torch.save(cp, legacy)
        recovery.update(checkpoint=str(legacy), checkpoint_sha256=file_sha256(legacy))
        result = self.run_model(StochasticCycle(), "legacy_resume", recovery)
        self.assertIsNone(result["elapsed_training_and_validation_seconds"])
        self.assertIsNone(result["peak_cuda_allocated_bytes"])
        self.assertGreater(result["segment_elapsed_training_and_validation_seconds"], 0)
        self.assertTrue(result["continuation"]["legacy_checkpoint_cost_unknown"])
        saved = torch.load(self.root / "legacy_resume/checkpoints/epoch_004.pt", weights_only=True)
        self.assertIsNone(saved["execution_accounting"]["elapsed_training_and_validation_seconds"])

    def test_live_clean_or_unapproved_parent_cannot_be_restored(self):
        recovery = self.interrupt(StochasticCycle())
        path = Path(recovery["terminal_evidence"])
        original = json.loads(path.read_text())
        for i, changed in enumerate((dict(state="R"), dict(run_count=0), dict(exit_status=0),
                                     dict(recovery_authorized=False), dict(scientific_result_present=True))):
            path.write_text(json.dumps(dict(original, **changed)))
            recovery["terminal_evidence_sha256"] = file_sha256(path)
            with self.assertRaisesRegex(ValueError, "terminal interrupted"):
                self.run_model(StochasticCycle(), f"bad_terminal_{i}", recovery)

    def test_hash_science_and_schedule_drift_are_rejected(self):
        recovery = self.interrupt(StochasticCycle())
        with self.assertRaisesRegex(ValueError, "artifact hash"):
            self.run_model(StochasticCycle(), "bad_hash", dict(recovery, checkpoint_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "science"):
            self.run_model(StochasticCycle(), "changed_inputs", recovery, provenance={"inputs": "other"})
        cp = torch.load(recovery["checkpoint"], weights_only=True)
        cp["history"][-1]["optimizer_updates"] += 1
        malformed = self.root / "malformed.pt"
        torch.save(cp, malformed)
        with self.assertRaisesRegex(ValueError, "exposure history"):
            self.run_model(StochasticCycle(), "bad_ledger", dict(recovery,
                checkpoint=str(malformed), checkpoint_sha256=file_sha256(malformed)))

    def test_validation_tie_preserves_earliest_epoch_across_interruption(self):
        evaluation = dict(case_count=1, aggregate=dict(field_relative_l2=1.))
        with patch("aurora.aneug_architecture_development.evaluate_cycles", return_value=evaluation):
            recovery = self.interrupt(StochasticCycle())
            result = self.run_model(StochasticCycle(), "ties", recovery)
        self.assertEqual(result["selected_epoch"], 1)

    def test_interruption_before_first_validation_does_not_invent_a_best(self):
        self.opt["validation_interval"] = 3
        torch.manual_seed(41)
        full = self.run_model(StochasticCycle(), "full_sparse_validation")
        torch.manual_seed(41)
        recovery = self.interrupt(StochasticCycle())
        result = self.run_model(StochasticCycle(), "sparse_validation_resume", recovery)
        self.assertEqual(full["selected_validation"], result["selected_validation"])
        self.assertEqual(result["validation_cycle_forwards"], 2)

    def test_recovery_cannot_be_combined_with_completed_extension(self):
        with self.assertRaisesRegex(ValueError, "separate from completed"):
            train_cycles(StochasticCycle(), self.cases, self.cases[:1], optimization=self.opt,
                reference_tawss_floor=1e-4, output_directory=self.root / "ambiguous",
                provenance=self.provenance, device=torch.device("cpu"),
                continuation={}, interrupted_recovery={}, log=lambda _: None)
        self.assertFalse((self.root / "ambiguous").exists())

    def test_frozen_prior_reuse_then_cycle_recovery_never_retrains_prior(self):
        class Stream:
            reads = 0
            def decode(inner, index):
                inner.reads += 1
                c = self.cases[index]
                return dict(coordinates=c["coordinates"], vertex_weights=c["vertex_weights"], steady_wss=c["wss"][0])
        stream = Stream()
        prior_opt = dict(self.opt, epochs=2, cases_per_epoch=3)
        prior_opt.pop("validation_interval")
        original = train_steady_prior(TinyPrior(), stream, [0, 1, 2], optimization=prior_opt,
            output_directory=self.root / "steady", provenance=self.provenance,
            device=torch.device("cpu"), log=lambda _: None)
        kwargs = dict(result_path=self.root / "steady/result.json",
            result_sha256=file_sha256(self.root / "steady/result.json"),
            checkpoint_path=self.root / "steady/prior.pt", checkpoint_sha256=original["prior_checkpoint_sha256"],
            expected_provenance=self.provenance, optimization=prior_opt, eligible_indices=[0, 1, 2],
            device=torch.device("cpu"))
        prior = TinyPrior()
        state = torch.get_rng_state().clone()
        reused, receipt = load_completed_steady_prior(prior, **kwargs)
        self.assertTrue(torch.equal(state, torch.get_rng_state()))
        self.assertEqual(reused, original)
        self.assertEqual(receipt["new_steady_label_exposures"], 0)
        self.assertFalse(prior.training)
        self.assertTrue(all(not p.requires_grad for p in prior.parameters()))
        torch.manual_seed(39)
        full = self.run_model(StochasticCycle(copy.deepcopy(prior)), "full_film")
        torch.manual_seed(39)
        recovery = self.interrupt(StochasticCycle(copy.deepcopy(prior)))
        other_prior = TinyPrior()
        load_completed_steady_prior(other_prior, **kwargs)
        resumed = self.run_model(StochasticCycle(other_prior), "resumed_film", recovery)
        self.assertEqual(full["selected_validation"], resumed["selected_validation"])
        self.assertEqual(stream.reads, 6)
        self.assertFalse(other_prior.training)
        self.assertTrue(all(p.grad is None for p in other_prior.parameters()))
        for name, value in prior.state_dict().items():
            torch.testing.assert_close(value, other_prior.state_dict()[name], rtol=0, atol=0)
        for changed in (dict(expected_provenance={"other": True}), dict(eligible_indices=[1, 0, 2]),
                        dict(optimization=dict(prior_opt, epochs=3)), dict(checkpoint_sha256="0" * 64)):
            with self.assertRaises(ValueError):
                load_completed_steady_prior(TinyPrior(), **dict(kwargs, **changed))


if __name__ == "__main__":
    unittest.main()

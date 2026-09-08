import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import torch

from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_cycle_continuation import CONTINUATION_INVARIANTS
from aurora.aneug_cycle_sampling import KEY, sampling_contract, epoch_examples, epoch_order
from aurora.aneug_paired_steady_supervision import PairedSteadySupervision
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256, _strict_atomic_torch_save
from aurora.aneug_release_730_label_efficiency import balanced_epoch_indices
from aurora.aneug_surface_transfer import build_paired_surface_transfer_model
from test_aneug_cycle_continuation import StochasticCycle
from test_aneug_paired_steady_supervision import StochasticMixed, Stream
from test_aneug_surface_transfer import geometry, topology


class CycleSamplingTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(12)
        self.cases = [dict(geometry(), wss=torch.randn(80, 4, 3)) for _ in range(3)]
        self.opt = dict(seed=17, epochs=4, accumulation_cases=2, validation_interval=1,
                        checkpoint_interval=1, learning_rate=3e-4, weight_decay=1e-4,
                        step_size_epochs=2, gamma=.75, gradient_clip_norm=1.)
        self.provenance = {key: "synthetic" for key in CONTINUATION_INVARIANTS}
        self.provenance.update(torch=str(torch.__version__), cuda=None,
                               historical_test_already_opened=True, cycle_output_scale=1.)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def mixed(self):
        return PairedSteadySupervision(Stream(), (2, 4, 9, 10), seed=91, loss_weight=.7)

    def run_curve(self, name, *, epochs=4, examples=7, supervision=None,
                  continuation=None, recovery=None, model=None, provenance=None):
        return train_cycles(model if model is not None else
                            (StochasticMixed() if supervision else StochasticCycle()),
            self.cases, self.cases[:1], optimization=dict(self.opt, epochs=epochs),
            reference_tawss_floor=1e-4, output_directory=self.root / name,
            provenance=self.provenance if provenance is None else provenance,
            device=torch.device("cpu"), log=lambda _: None,
            transient_examples_per_epoch=examples, steady_supervision=supervision,
            continuation=continuation, interrupted_recovery=recovery)

    def checkpoint(self, name, epoch=4):
        return torch.load(self.root / name / f"checkpoints/epoch_{epoch:03d}.pt", weights_only=True)

    def assert_state_equal(self, a, b):
        for key in ("model_state_dict", "best_state_dict"):
            for name, value in a[key].items():
                torch.testing.assert_close(value, b[key][name], rtol=0, atol=0)
        for index, state in a["optimizer_state_dict"]["state"].items():
            for name, value in state.items():
                torch.testing.assert_close(value, b["optimizer_state_dict"]["state"][index][name], rtol=0, atol=0)
        self.assertEqual(a["scheduler_state_dict"], b["scheduler_state_dict"])
        torch.testing.assert_close(a["rng_state"]["torch_rng_state"], b["rng_state"]["torch_rng_state"], rtol=0, atol=0)

    def test_balanced_production_budgets_match_existing_schedule_without_consuming_global_rng(self):
        random.seed(30)
        state = random.getstate()
        for count in (58, 146, 292, 584):
            for seed in (20260901, 20260902, 20260903, 20260904, 20260905):
                for epoch in (1, 2, 250):
                    order = epoch_order(count, 584, seed, epoch)
                    self.assertEqual(tuple(order), balanced_epoch_indices(count,
                        training_seed=seed, epoch=epoch, exposures=584))
                    self.assertEqual(len(order), 584)
                    self.assertEqual(set(order), set(range(count)))
                    counts = [order.count(i) for i in range(count)]
                    self.assertLessEqual(max(counts) - min(counts), 1)
        self.assertEqual(random.getstate(), state)

    def test_unique_count_and_exposures_are_not_conflated(self):
        for suffix, supervision in (("T", None), ("TS", self.mixed())):
            result = self.run_curve(suffix, epochs=2, supervision=supervision)
            self.assertEqual(result["train_cases"], 3)
            self.assertEqual(result["training_cycle_exposures"], 14)
            self.assertEqual(result["training_phase_field_exposures"], 1120)
            self.assertEqual(result["optimizer_updates"], 8)
            self.assertEqual(result["validation_cycle_forwards"], 2)
            self.assertEqual(result["provenance"][KEY], sampling_contract(3, 7, 17))
            if supervision:
                self.assertEqual(supervision.stream.reads, supervision.indices(1, 7) + supervision.indices(2, 7))
                self.assertEqual(result["steady_exposures"], 14)
                self.assertEqual(result["total_training_field_exposures"], 14 * 81)
            else:
                self.assertEqual(result["steady_exposures"], 0)
        self.assertNotIn(KEY, self.provenance)

    def test_explicit_single_visit_retains_default_stochastic_learning(self):
        for suffix, mixed in (("T", False), ("TS", True)):
            results = []
            for name, examples in (("default", None), ("explicit", 3)):
                torch.manual_seed(94)
                results.append(self.run_curve(name + suffix, examples=examples,
                    supervision=self.mixed() if mixed else None))
            self.assert_state_equal(self.checkpoint("default" + suffix), self.checkpoint("explicit" + suffix))
            for key in ("selected_epoch", "selected_validation", "training_cycle_exposures", "optimizer_updates"):
                self.assertEqual(results[0][key], results[1][key])
            self.assertNotIn(KEY, results[0]["provenance"])

    def test_completed_extension_restores_repeated_T_and_TS_exactly(self):
        for suffix, mixed in (("T", False), ("TS", True)):
            torch.manual_seed(94)
            full = self.run_curve("whole" + suffix, supervision=self.mixed() if mixed else None)
            torch.manual_seed(94)
            self.run_curve("parent" + suffix, epochs=2, supervision=self.mixed() if mixed else None)
            root = self.root / ("parent" + suffix)
            cp, result = root / "checkpoints/epoch_002.pt", root / "result.json"
            continuation = dict(checkpoint=str(cp), checkpoint_sha256=file_sha256(cp),
                parent_result=str(result), parent_result_sha256=file_sha256(result))
            torch.manual_seed(999)
            stream = self.mixed() if mixed else None
            resumed = self.run_curve("resumed" + suffix, continuation=continuation, supervision=stream)
            self.assert_state_equal(self.checkpoint("whole" + suffix), self.checkpoint("resumed" + suffix))
            self.assertEqual(full["selected_validation"], resumed["selected_validation"])
            self.assertEqual(resumed["segment_training_cycle_exposures"], 14)
            self.assertEqual(resumed["segment_optimizer_updates"], 8)
            if stream:
                self.assertEqual(stream.stream.reads, stream.indices(3, 7) + stream.indices(4, 7))
                self.assertEqual(resumed["segment_steady_exposures"], 14)
            for examples in (None, 8):
                with self.assertRaisesRegex(ValueError, "sampling changed"):
                    self.run_curve(f"changed{suffix}{examples}", examples=examples,
                        continuation=continuation, supervision=self.mixed() if mixed else None)

    def test_real_interruption_restores_repeated_exposures_and_unknown_discarded_cost(self):
        torch.manual_seed(94)
        full = self.run_curve("whole")
        def interrupted_save(path, payload):
            _strict_atomic_torch_save(path, payload)
            if path.name == "epoch_002.pt":
                raise InterruptedError("synthetic stopped process")
        torch.manual_seed(94)
        with patch("aurora.aneug_architecture_development._strict_atomic_torch_save", interrupted_save):
            with self.assertRaises(InterruptedError):
                self.run_curve("interrupted")
        self.assertFalse((self.root / "interrupted/result.json").exists())
        terminal = self.root / "terminal.json"
        terminal.write_text(json.dumps(dict(schema_version="aurora.interrupted_attempt_evidence.v3",
            state="F", run_count=1, exit_status=271, reason="walltime",
            scientific_result_present=False, recovery_authorized=True)))
        cp = self.root / "interrupted/checkpoints/epoch_002.pt"
        recovery = dict(checkpoint=str(cp), checkpoint_sha256=file_sha256(cp),
                        terminal_evidence=str(terminal), terminal_evidence_sha256=file_sha256(terminal))
        torch.manual_seed(999)
        resumed = self.run_curve("recovered", recovery=recovery)
        self.assert_state_equal(self.checkpoint("whole"), self.checkpoint("recovered"))
        self.assertEqual(full["selected_validation"], resumed["selected_validation"])
        self.assertEqual(resumed["training_cycle_exposures"], 28)
        self.assertEqual(resumed["segment_training_cycle_exposures"], 14)
        self.assertEqual(resumed["segment_optimizer_updates"], 8)
        self.assertIsNone(resumed["recovery_accounting"]["total_actual_training_cycle_exposures"])

    def test_production_width_selective_T_and_TS_use_actual_full_cycle_updates(self):
        for mixed in (False, True):
            model = build_paired_surface_transfer_model(topology(), torch.arange(80, dtype=torch.float64) / 80,
                variant="selective_transfer", auxiliary_steady=mixed, output_scale=1.,
                width=128, heads=4, bank_width=32, operators=4, adapter_width=32, mode_chunk=8)
            self.assertGreater(sum(p.numel() for p in model.parameters()), 2_000_000)
            before = model.router_frequency.weight.detach().clone()
            result = self.run_curve(f"production{mixed}", epochs=1, model=model,
                supervision=self.mixed() if mixed else None)
            self.assertEqual(result["phase_count"], 80)
            self.assertEqual(result["training_cycle_exposures"], 7)
            self.assertTrue(all(p.grad is not None for p in model.parameters()))
            self.assertTrue(bool(((before - model.router_frequency.weight).abs().sum(1) > 0).all()))

    def test_invalid_or_unbound_sampling_fails_before_output_creation(self):
        for value in (True, 0, 2, -1, 3.0):
            name = "bad" + str(value)
            with self.assertRaises(ValueError):
                self.run_curve(name, examples=value)
            self.assertFalse((self.root / name).exists())
        for value in (None, dict(sampling_contract(3, 7, 17), examples_per_epoch=8)):
            with self.assertRaises(ValueError):
                self.run_curve("bad_provenance", provenance=dict(self.provenance, **{KEY: value}))
        with self.assertRaises(ValueError):
            self.run_curve("orphan", examples=None,
                provenance=dict(self.provenance, **{KEY: sampling_contract(3, 7, 17)}))
        with self.assertRaises(ValueError):
            epoch_examples({KEY: dict(sampling_contract(3, 7, 17), training_seed=18)}, 3, 17)
        for key in ("unique_training_cases", "training_seed"):
            value = dict(sampling_contract(1, 7, 0), **{key: key == "unique_training_cases"})
            with self.assertRaises(ValueError):
                epoch_examples({KEY: value}, 1, 0)


if __name__ == "__main__":
    unittest.main()

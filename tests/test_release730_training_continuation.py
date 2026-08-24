from __future__ import annotations

import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.release730_training_continuation import (
    Release730TrainingContinuationError,
    make_training_checkpoint,
    restore_training_checkpoint,
    validate_interrupted_attempt_record,
)


class Release730TrainingContinuationTests(unittest.TestCase):
    def test_only_noncomplete_nonzero_terminal_record_can_resume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempt.status.json"
            interrupted = {"job_id": "1.server", "exit_code": 271, "complete": False}
            path.write_text(json.dumps(interrupted) + "\n", encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                validate_interrupted_attempt_record(path, digest), interrupted
            )
            completed = {"job_id": "1.server", "exit_code": 0, "complete": True}
            path.write_text(json.dumps(completed) + "\n", encoding="utf-8")
            completed_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(
                Release730TrainingContinuationError,
                "prior_attempt_not_interrupted",
            ):
                validate_interrupted_attempt_record(path, completed_digest)

    def test_complete_state_and_rng_are_restored_exactly(self) -> None:
        random.seed(31)
        torch.manual_seed(31)
        model = torch.nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.75)
        loss = model(torch.ones(2, 3)).square().mean()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        scheduler.step()
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        history = [
            {
                "epoch": 1,
                "optimizer_steps": 1,
                "training_loss": float(loss.item()),
                "validation_field_relative_l2": 0.7,
                "learning_rate": scheduler.get_last_lr()[0],
            }
        ]
        payload = make_training_checkpoint(
            schema_version="test.checkpoint.v1",
            protocol_id="test_protocol",
            epoch=1,
            optimizer_steps=1,
            validation_field_relative_l2=0.7,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            best_field_relative_l2=0.7,
            best_epoch=1,
            stale_epochs=0,
            history=history,
            smoke={"finite_forward_backward": True},
            elapsed_seconds_accumulated=2.5,
            provenance={"public_commit": "a" * 40, "config_sha256": "b" * 64},
        )
        expected_python = random.random()
        expected_torch = torch.rand(4)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with torch.no_grad():
                for parameter in model.parameters():
                    parameter.add_(10.0)
            restored = restore_training_checkpoint(
                path,
                schema_version="test.checkpoint.v1",
                protocol_id="test_protocol",
                expected_provenance={
                    "public_commit": "a" * 40,
                    "config_sha256": "b" * 64,
                },
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                maximum_epochs=5,
            )
            for key, value in model.state_dict().items():
                torch.testing.assert_close(value, state[key], rtol=0.0, atol=0.0)
            self.assertEqual(restored["epoch"], 1)
            self.assertEqual(random.random(), expected_python)
            torch.testing.assert_close(torch.rand(4), expected_torch, rtol=0.0, atol=0.0)

    def test_provenance_drift_fails_before_restore(self) -> None:
        torch.manual_seed(7)
        model = torch.nn.Linear(2, 1)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1)
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        payload = make_training_checkpoint(
            schema_version="test.checkpoint.v1",
            protocol_id="test_protocol",
            epoch=1,
            optimizer_steps=1,
            validation_field_relative_l2=1.0,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            best_field_relative_l2=1.0,
            best_epoch=1,
            stale_epochs=0,
            history=[{"epoch": 1}],
            smoke={"finite_forward_backward": True},
            elapsed_seconds_accumulated=1.0,
            provenance={"config_sha256": "a" * 64},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with self.assertRaisesRegex(
                Release730TrainingContinuationError,
                "checkpoint_provenance_config_sha256",
            ):
                restore_training_checkpoint(
                    path,
                    schema_version="test.checkpoint.v1",
                    protocol_id="test_protocol",
                    expected_provenance={"config_sha256": "b" * 64},
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    maximum_epochs=5,
                )


if __name__ == "__main__":
    unittest.main()

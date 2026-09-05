import json
from pathlib import Path

import pytest
import torch

from aurora.aneug_release_730_icce_consumer_benchmark import (
    ICCEConsumerBenchmarkError,
    _cycle_parameter_contract,
    summarize_latency_ms,
    validate_consumer_benchmark_config,
    validate_pair,
)


ROOT = Path(__file__).resolve().parents[1]


class FixtureModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.backbone = torch.nn.Linear(2, 3)
        self.single_field_head = torch.nn.Linear(2, 3)


def test_config_is_prospective_validation_only_consumer_scope() -> None:
    payload = json.loads(
        (ROOT / "configs/aneug_release_730_icce_consumer_benchmark_v1.json").read_text()
    )
    validate_consumer_benchmark_config(payload)
    payload["evaluation_partition"] = "locked_test"
    with pytest.raises(ICCEConsumerBenchmarkError, match="benchmark_contract"):
        validate_consumer_benchmark_config(payload)
    payload["evaluation_partition"] = "validation"
    payload["validation_loader_order_sha256"] = "not-a-digest"
    with pytest.raises(ICCEConsumerBenchmarkError, match="validation_order"):
        validate_consumer_benchmark_config(payload)


def test_latency_summary_reports_p50_p95_and_throughput() -> None:
    summary = summarize_latency_ms([1.0, 2.0, 3.0, 4.0])
    assert summary["p50_ms"] == pytest.approx(2.5)
    assert summary["p95_ms"] == pytest.approx(3.85)
    assert summary["throughput_complete_cycles_per_second"] == pytest.approx(400.0)


def test_cycle_parameter_contract_discards_training_only_head() -> None:
    contract = _cycle_parameter_contract(FixtureModel())
    assert contract["training_model_parameter_count"] == 18
    assert contract["discarded_auxiliary_head_parameter_count"] == 9
    assert contract["deployed_cycle_parameter_count"] == 9
    assert len(contract["cycle_architecture_signature_sha256"]) == 64


def test_pair_requires_identical_deployed_cycle_path() -> None:
    base = {
        "status": "complete_validation_only_consumer_measurement",
        "training_seed": 20260901,
        "validation_loader_order_sha256": "a" * 64,
        "cuda_device_name": "NVIDIA TITAN RTX",
        "gpu_total_memory_bytes": 1,
        "nvidia_driver_version": "525.85.12",
        "torch_version": "2.5.1",
        "torch_cuda_version": "11.8",
        "deployed_cycle_parameter_count": 9,
        "cycle_architecture_signature_sha256": "b" * 64,
        "auxiliary_head_invocation_count": 0,
    }
    pair = validate_pair(
        [{**base, "method_id": "T"}, {**base, "method_id": "T_plus_S_regime_separated"}]
    )
    assert pair["adds_inference_parameters_or_operations"] is False
    changed = {**base, "method_id": "T_plus_S_regime_separated"}
    changed["deployed_cycle_parameter_count"] = 10
    with pytest.raises(ICCEConsumerBenchmarkError, match="pair_identity"):
        validate_pair([{**base, "method_id": "T"}, changed])

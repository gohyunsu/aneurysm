"""Validation-only consumer-GPU benchmark for the ICCE revision.

This module contains no dataset loader and no locked-test path.  It receives the
fixed 73-case validation sequence and a restored model from the private runtime.
The reported model-forward timing excludes host-to-device transfer; a distinct
staging-plus-forward measurement makes that boundary observable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch


PROTOCOL_ID = "aneug_release_730_icce_consumer_benchmark_v1"


class ICCEConsumerBenchmarkError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEConsumerBenchmarkError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_consumer_benchmark_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(payload)
    _require(
        config.get("protocol_id") == PROTOCOL_ID
        and config.get("status") == "prospective_measurement_pending"
        and config.get("evaluation_partition") == "validation"
        and config.get("validation_case_count") == 73
        and config.get("batch_size_cases") == 1
        and config.get("warmup_forwards") == 10
        and config.get("measurement_repeats") == 10
        and config.get("fixed_validation_order") is True
        and config.get("cuda_synchronize_before_and_after") is True,
        "benchmark_contract",
    )
    _require(
        _is_sha256(config.get("validation_loader_order_sha256")),
        "validation_order",
    )
    _require(
        config.get("expected_cuda_device_name") == "NVIDIA TITAN RTX"
        and config.get("hardware_class")
        == "commodity_consumer_class_discrete_gpu"
        and config.get("model_forward_scope")
        == "device_resident_geometry_to_complete_80_phase_cycle"
        and config.get("secondary_scope")
        == "host_resident_geometry_staging_plus_complete_80_phase_cycle"
        and config.get("raw_latency_observations_retained") is True,
        "hardware_scope",
    )
    _require(
        config.get("methods") == ["T", "T_plus_S_regime_separated"]
        and config.get("training_seed") == 20_260_901
        and config.get("auxiliary_head_discarded_at_inference") is True
        and config.get("locked_test_fields_read") is False
        and config.get("processed_only_extra_fields_read") is False
        and config.get("clinical_or_device_claim") is False
        and config.get("paper_claim_before_measurement") is False,
        "method_scope",
    )
    return config


def _quantile(values: Sequence[float], probability: float) -> float:
    parsed = sorted(float(value) for value in values)
    _require(
        bool(parsed)
        and 0.0 <= probability <= 1.0
        and all(math.isfinite(value) and value >= 0.0 for value in parsed),
        "latency_values",
    )
    position = probability * (len(parsed) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return parsed[lower]
    fraction = position - lower
    return parsed[lower] * (1.0 - fraction) + parsed[upper] * fraction


def summarize_latency_ms(values: Sequence[float]) -> dict[str, float | int]:
    parsed = [float(value) for value in values]
    _require(
        bool(parsed)
        and all(math.isfinite(value) and value > 0.0 for value in parsed),
        "latency_values",
    )
    mean = sum(parsed) / len(parsed)
    variance = sum((value - mean) ** 2 for value in parsed) / len(parsed)
    return {
        "observation_count": len(parsed),
        "mean_ms": mean,
        "standard_deviation_ms": math.sqrt(variance),
        "p50_ms": _quantile(parsed, 0.50),
        "p95_ms": _quantile(parsed, 0.95),
        "minimum_ms": min(parsed),
        "maximum_ms": max(parsed),
        "throughput_complete_cycles_per_second": 1000.0 / mean,
    }


def _cycle_parameter_contract(model: torch.nn.Module) -> dict[str, Any]:
    head = getattr(model, "single_field_head", None)
    _require(isinstance(head, torch.nn.Module), "single_field_head")
    total = sum(parameter.numel() for parameter in model.parameters())
    auxiliary = sum(parameter.numel() for parameter in head.parameters())
    cycle = total - auxiliary
    _require(total > auxiliary > 0 and cycle > 0, "parameter_count")
    architecture = [
        [name, list(parameter.shape), str(parameter.dtype)]
        for name, parameter in model.named_parameters()
        if not name.startswith("single_field_head.")
    ]
    signature = hashlib.sha256(
        json.dumps(architecture, separators=(",", ":"), sort_keys=False).encode(
            "utf-8"
        )
    ).hexdigest()
    return {
        "training_model_parameter_count": total,
        "discarded_auxiliary_head_parameter_count": auxiliary,
        "deployed_cycle_parameter_count": cycle,
        "cycle_architecture_signature_sha256": signature,
    }


def _geometry_only(
    cpu_case: Mapping[str, Any], device: torch.device
) -> dict[str, torch.Tensor]:
    _require("coordinates" in cpu_case and "wss" in cpu_case, "validation_case")
    geometry: dict[str, torch.Tensor] = {}
    for key, value in cpu_case.items():
        if key == "wss":
            continue
        _require(isinstance(value, torch.Tensor), f"geometry_tensor:{key}")
        geometry[key] = value.to(device=device, non_blocking=False)
    return geometry


@torch.no_grad()
def benchmark_complete_cycle(
    model: torch.nn.Module,
    validation_cases: Sequence[Mapping[str, Any]],
    device: torch.device,
    config: Mapping[str, Any],
    *,
    method_id: str,
    validation_loader_order_sha256: str,
    runtime_metadata: Mapping[str, str],
) -> dict[str, Any]:
    """Benchmark one restored checkpoint on the fixed validation order."""

    protocol = validate_consumer_benchmark_config(config)
    _require(
        device.type == "cuda"
        and torch.cuda.is_available()
        and len(validation_cases) == 73
        and method_id in protocol["methods"]
        and validation_loader_order_sha256
        == protocol["validation_loader_order_sha256"],
        "runtime_scope",
    )
    gpu_name = torch.cuda.get_device_name(device)
    _require(gpu_name == protocol["expected_cuda_device_name"], "gpu_name")
    _require(
        isinstance(runtime_metadata.get("cpu_model"), str)
        and bool(runtime_metadata["cpu_model"].strip())
        and isinstance(runtime_metadata.get("nvidia_driver_version"), str)
        and bool(runtime_metadata["nvidia_driver_version"].strip()),
        "runtime_metadata",
    )
    repetitions = int(protocol["measurement_repeats"])
    warmups = int(protocol["warmup_forwards"])
    model.eval()
    parameter_contract = _cycle_parameter_contract(model)
    auxiliary_invocations = 0

    def count_auxiliary_invocation(
        _module: torch.nn.Module, _inputs: tuple[Any, ...], _output: Any
    ) -> None:
        nonlocal auxiliary_invocations
        auxiliary_invocations += 1

    hook = model.single_field_head.register_forward_hook(count_auxiliary_invocation)
    try:
        for index in range(warmups):
            geometry = _geometry_only(validation_cases[index % 73], device)
            prediction = model.forward_cycle(geometry)
            _require(
                tuple(prediction.shape) == (80, 13_902, 3),
                "prediction_shape",
            )
            del prediction, geometry
        torch.cuda.synchronize(device)

        forward_matrix = [[0.0] * 73 for _ in range(repetitions)]
        torch.cuda.reset_peak_memory_stats(device)
        resident_before = int(torch.cuda.memory_allocated(device))
        for case_index, cpu_case in enumerate(validation_cases):
            geometry = _geometry_only(cpu_case, device)
            torch.cuda.synchronize(device)
            for repeat_index in range(repetitions):
                torch.cuda.synchronize(device)
                started_ns = time.perf_counter_ns()
                prediction = model.forward_cycle(geometry)
                torch.cuda.synchronize(device)
                forward_matrix[repeat_index][case_index] = (
                    time.perf_counter_ns() - started_ns
                ) / 1_000_000.0
                _require(
                    tuple(prediction.shape) == (80, 13_902, 3),
                    "prediction_shape",
                )
                del prediction
            del geometry
        forward_peak = int(torch.cuda.max_memory_allocated(device))

        staged_matrix = [[0.0] * 73 for _ in range(repetitions)]
        torch.cuda.reset_peak_memory_stats(device)
        for repeat_index in range(repetitions):
            for case_index, cpu_case in enumerate(validation_cases):
                torch.cuda.synchronize(device)
                started_ns = time.perf_counter_ns()
                geometry = _geometry_only(cpu_case, device)
                prediction = model.forward_cycle(geometry)
                torch.cuda.synchronize(device)
                staged_matrix[repeat_index][case_index] = (
                    time.perf_counter_ns() - started_ns
                ) / 1_000_000.0
                _require(
                    tuple(prediction.shape) == (80, 13_902, 3),
                    "prediction_shape",
                )
                del prediction, geometry
        staged_peak = int(torch.cuda.max_memory_allocated(device))
    finally:
        hook.remove()
    _require(auxiliary_invocations == 0, "auxiliary_head_invoked")
    forward_values = [value for row in forward_matrix for value in row]
    staged_values = [value for row in staged_matrix for value in row]
    expected_observations = 73 * repetitions
    _require(
        len(forward_values) == len(staged_values) == expected_observations,
        "observation_count",
    )
    properties = torch.cuda.get_device_properties(device)
    return {
        "schema_version": "aurora.aneug_release_730_icce_consumer_benchmark.v1",
        "protocol_id": PROTOCOL_ID,
        "status": "complete_validation_only_consumer_measurement",
        "method_id": method_id,
        "training_seed": int(protocol["training_seed"]),
        "validation_case_count": 73,
        "validation_loader_order_sha256": validation_loader_order_sha256,
        "batch_size_cases": 1,
        "warmup_forwards": warmups,
        "measurement_repeats": repetitions,
        "cpu_model": runtime_metadata["cpu_model"],
        "cuda_device_name": gpu_name,
        "gpu_total_memory_bytes": int(properties.total_memory),
        "cuda_compute_capability": [int(properties.major), int(properties.minor)],
        "nvidia_driver_version": runtime_metadata["nvidia_driver_version"],
        "torch_version": str(torch.__version__),
        "torch_cuda_version": str(torch.version.cuda),
        **parameter_contract,
        "auxiliary_head_invocation_count": auxiliary_invocations,
        "auxiliary_head_discarded_at_inference": True,
        "model_forward_only": {
            "scope": protocol["model_forward_scope"],
            "host_to_device_transfer_included": False,
            "target_wss_loaded_to_device": False,
            "metric_computation_included": False,
            "resident_gpu_memory_bytes_before_measurement": resident_before,
            "peak_allocated_gpu_memory_bytes": forward_peak,
            "summary": summarize_latency_ms(forward_values),
            "raw_latency_ms_by_repeat_and_case_order": forward_matrix,
        },
        "host_staging_plus_forward": {
            "scope": protocol["secondary_scope"],
            "host_to_device_transfer_included": True,
            "raw_file_loading_included": False,
            "target_wss_loaded_to_device": False,
            "metric_computation_included": False,
            "peak_allocated_gpu_memory_bytes": staged_peak,
            "summary": summarize_latency_ms(staged_values),
            "raw_latency_ms_by_repeat_and_case_order": staged_matrix,
        },
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_identifiers_included": False,
        "clinical_or_device_claim": False,
        "paper_claim": False,
    }


def validate_pair(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    _require(len(results) == 2, "pair_count")
    by_method = {str(result.get("method_id")): result for result in results}
    _require(
        set(by_method) == {"T", "T_plus_S_regime_separated"}
        and all(
            result.get("status")
            == "complete_validation_only_consumer_measurement"
            for result in by_method.values()
        ),
        "pair_methods",
    )
    t_result = by_method["T"]
    proposed = by_method["T_plus_S_regime_separated"]
    keys = (
        "training_seed",
        "validation_loader_order_sha256",
        "cuda_device_name",
        "gpu_total_memory_bytes",
        "nvidia_driver_version",
        "torch_version",
        "torch_cuda_version",
        "deployed_cycle_parameter_count",
        "cycle_architecture_signature_sha256",
    )
    _require(all(t_result.get(key) == proposed.get(key) for key in keys), "pair_identity")
    _require(
        t_result.get("auxiliary_head_invocation_count") == 0
        and proposed.get("auxiliary_head_invocation_count") == 0,
        "pair_auxiliary_head",
    )
    return {
        "status": "complete_paired_validation_only_consumer_measurement",
        "methods": ["T", "T_plus_S_regime_separated"],
        "same_cycle_architecture_and_parameter_count": True,
        "auxiliary_head_invoked_by_either_method": False,
        "adds_inference_parameters_or_operations": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    validate_consumer_benchmark_config(
        json.loads(args.config.read_text(encoding="utf-8"))
    )
    print(PROTOCOL_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

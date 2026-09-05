"""Train-only cycle representation evidence, not a learned-model benchmark.

The processed release stores ordered snapshots, not verified timestamps. This
audit explicitly uses the nominal index grid i/T. It retains every endpoint,
includes the even-grid Nyquist component and never fits or selects a model.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_cycle_decoders import RealPeriodicBasis
from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_train_audit import (
    _ordered_digest, _scalar_summary, _vertex_areas, file_sha256,
    index_case_records, selected_training_records, validate_split_evidence,
)
from aurora.aneug_release_730_ghd_gps_baseline import _strict_atomic_json


LABELS = ["x", "y", "z", "x_normal", "y_normal", "z_normal",
          "wss_x", "wss_y", "wss_z"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_config(config: Mapping[str, Any]) -> None:
    require(config.get("schema_version") == "aurora.cycle_representation_audit.v3", "schema")
    require(config.get("phase_grid") == "nominal_snapshot_index_i_over_80", "phase grid")
    require(config.get("physical_timestamps_verified") is False, "timestamp claim")
    require(config.get("historical_test_already_opened") is True, "test history")
    require(config.get("field_partition") == "train_only", "field partition")
    require(config.get("expected_shape") == [80, 13902, 9], "release shape")
    require(config.get("cutoffs") == [0, 2, 4, 8, 16, 24, 32, 40], "cutoff inventory")
    require(config.get("automatic_model_selection") is False, "no automatic selection")


@torch.no_grad()
def audit_cycle(reference: torch.Tensor, areas: torch.Tensor,
                cutoffs: Sequence[int]) -> dict[str, Any]:
    """One admitted physical field. FFT and dense basis independently agree."""
    field = reference.detach().cpu().to(torch.float64)
    weight = areas.detach().cpu().to(torch.float64)
    require(field.ndim == 3 and field.shape[-1] == 3 and field.shape[0] >= 3,
            "field shape")
    require(weight.shape == (field.shape[1],), "area shape")
    require(bool(torch.isfinite(field).all() and torch.isfinite(weight).all()), "finite")
    require(bool((weight >= 0).all() and weight.sum() > 0), "positive area support")
    count = field.shape[0]
    require(bool(cutoffs) and list(cutoffs) == sorted(set(cutoffs)), "ordered cutoffs")
    require(all(isinstance(k, int) and not isinstance(k, bool)
                and 0 <= k <= count // 2 for k in cutoffs), "cutoff range")
    weight = weight / weight.sum()
    energy = (field.square() * weight[None, :, None]).sum()
    require(bool(energy > 0), "nonzero field energy")
    spectrum = torch.fft.rfft(field, dim=0, norm="ortho")
    multiplicity = torch.full((count // 2 + 1,), 2.0, dtype=field.dtype)
    multiplicity[0] = 1
    if count % 2 == 0:
        multiplicity[-1] = 1
    mode_energy = (spectrum.abs().square() * weight[None, :, None]).sum((1, 2)) * multiplicity
    parseval_error = abs(float(mode_energy.sum() / energy - 1))
    require(parseval_error < 1e-10, "FFT Parseval numerical integrity")
    oscillatory_energy = mode_energy[1:].sum()
    has_oscillation = bool(oscillatory_energy > torch.finfo(field.dtype).eps * energy)
    phase_grid = torch.arange(count, dtype=field.dtype) / count
    full_basis = RealPeriodicBasis(phase_grid, count // 2)
    dense = full_basis.decode(full_basis.encode(field))
    dense_error = torch.sqrt(((dense - field).square() * weight[None, :, None]).sum() / energy)
    reference_tawss = torch.linalg.vector_norm(field, dim=-1).mean(0)
    mean_tawss = (reference_tawss * weight).sum()
    rows = []
    for cutoff in cutoffs:
        truncated = spectrum.clone()
        truncated[cutoff + 1:] = 0
        prediction = torch.fft.irfft(truncated, n=count, dim=0, norm="ortho")
        error_by_phase = ((prediction - field).square() * weight[None, :, None]).sum((1, 2))
        numerator = error_by_phase.sum()
        prediction_tawss = torch.linalg.vector_norm(prediction, dim=-1).mean(0)
        rows.append({
            "max_frequency": cutoff,
            "real_coefficients": 1 + 2 * cutoff - int(count % 2 == 0 and cutoff == count // 2),
            "field_relative_l2": float(torch.sqrt(numerator / energy)),
            "discarded_energy_relative_l2": float(torch.sqrt(mode_energy[cutoff + 1:].sum() / energy)),
            "oscillatory_relative_l2": float(torch.sqrt(numerator / oscillatory_energy)) if has_oscillation else None,
            "maximum_phase_error_over_cycle_rms": float(torch.sqrt(error_by_phase.max() / (energy / count))),
            "tawss_normalized_absolute_error": float(((prediction_tawss - reference_tawss).abs() * weight).sum() / mean_tawss),
        })
    boundary_energy = ((field[-1] - field[0]).square() * weight[:, None]).sum()
    return {
        "phase_count": count,
        "frequency_energy_fraction": (mode_energy / energy).tolist(),
        "oscillatory_energy_fraction": float(oscillatory_energy / energy),
        "has_numerically_resolved_oscillation": has_oscillation,
        "boundary_step_over_cycle_rms": float(torch.sqrt(boundary_energy / (energy / count))),
        "parseval_relative_discrepancy": parseval_error,
        "dense_full_basis_relative_l2": float(dense_error),
        "cutoffs": rows,
    }


def iter_training_fields(transient: Mapping[str, Any], normalizer: Mapping[str, Any],
                         train_order: Sequence[str], excluded: Sequence[str], *,
                         expected_shape: tuple[int, int, int]):
    """Stream one train field; nontrain records are used only for ID indexing."""
    require(list(normalizer["label"]) == LABELS, "normalizer labels")
    mean = normalizer["tensor_norm"]["mean"].detach().cpu().double().reshape(1, 1, -1)
    std = normalizer["tensor_norm"]["std"].detach().cpu().double().reshape(1, 1, -1)
    require(mean.shape == std.shape == (1, 1, 9), "normalizer shape")
    require(bool(torch.isfinite(mean).all() and torch.isfinite(std).all()
                 and (std >= 0).all()), "normalizer values")
    ordered, indexed = index_case_records(transient["registered_data_list"])
    require(ordered == [str(x) for x in transient["mesh_data"]["cases"]], "case order")
    require(set(ordered) == set(train_order) | set(excluded), "complete admission coverage")
    records = selected_training_records(indexed, train_order, excluded)
    faces = transient["mesh_data"]["faces_list"][0].detach().cpu().long()
    require(faces.ndim == 2 and faces.shape[1] == 3 and faces.numel() > 0, "faces shape")
    require(bool((faces >= 0).all() and (faces < expected_shape[1]).all()), "face indices")
    for case_id, record in zip(train_order, records):
        require(list(record["labels"]) == LABELS, "record labels")
        values = record["tensor"].detach().cpu().double()
        require(tuple(values.shape) == expected_shape and bool(torch.isfinite(values).all()), "record tensor")
        physical = values * (std + 1e-5) + mean
        areas, _, _ = _vertex_areas(physical[0, :, :3], faces, torch)
        yield case_id, physical[..., 6:9], areas, sorted(str(key) for key in record.keys())


def aggregate(rows: Sequence[Mapping[str, Any]], cutoffs: Sequence[int]) -> dict[str, Any]:
    require(bool(rows), "no completed cases")
    summaries = []
    for i, cutoff in enumerate(cutoffs):
        selected = [row["cutoffs"][i] for row in rows]
        require(all(row["max_frequency"] == cutoff for row in selected), "paired cutoff order")
        metrics = {}
        for key in selected[0]:
            if key not in {"max_frequency", "real_coefficients"}:
                values = [row[key] for row in selected if row[key] is not None]
                metrics[key] = {"case_count": len(values), **(_scalar_summary(values) if values else {})}
        summaries.append({"max_frequency": cutoff, "real_coefficients": selected[0]["real_coefficients"],
                          "metrics": metrics})
    return {"case_count": len(rows), "cutoffs": summaries,
            "frequency_energy_fraction_case_mean": torch.tensor(
                [row["frequency_energy_fraction"] for row in rows], dtype=torch.float64).mean(0).tolist(),
            "boundary_step_over_cycle_rms": _scalar_summary([row["boundary_step_over_cycle_rms"] for row in rows]),
            "dense_full_basis_relative_l2": _scalar_summary([row["dense_full_basis_relative_l2"] for row in rows])}


def run(args: argparse.Namespace) -> dict[str, Any]:
    config = json.loads(args.config.read_text())
    validate_config(config)
    require(bool(os.environ.get("PBS_JOBID")), "scientific execution requires allocated PBS job")
    require(not args.output.exists(), "fresh output directory required")
    reader_path = args.public_root / config["reader_config"]
    reader = json.loads(reader_path.read_text())
    source, split = reader["source"], reader["split"]
    paths = {
        "transient": (args.transient, source["processed_v5_sha256"], source["processed_v5_bytes"]),
        "steady_normalizer": (args.steady, source["steady_norm_sha256"], source["steady_norm_bytes"]),
        "public_split": (args.public_root / "results/aneug_release_730_split_r3_20260818.json", split["public_result_sha256"], None),
        "private_split": (args.private_split, split["private_manifest_sha256"], None),
        "audit_public": (args.public_root / "results/aneug_release_730_train_audit_r2_20260818.json", split["train_audit_public_sha256"], None),
        "audit_private": (args.private_train_audit, split["train_audit_private_sha256"], None),
    }
    for label, (path, digest, size) in paths.items():
        require(path.is_file() and (size is None or path.stat().st_size == size), label + " size")
        require(file_sha256(path) == digest, label + " SHA256")
        print(json.dumps({"stage": "asset_verified", "asset": label}), flush=True)
    public_split = json.loads(paths["public_split"][0].read_text())
    private_split = json.loads(args.private_split.read_text())
    # These immutable source manifests record the HISTORICAL split/audit state.
    # Their test_opened=false is not a current untouched-test claim.
    buckets = validate_split_evidence(reader, public_split, private_split)
    audit_private = json.loads(args.private_train_audit.read_text())
    audit_public = json.loads(paths["audit_public"][0].read_text())
    require(audit_public["integrity_pass"] is True, "historical audit integrity")
    require(audit_private["validation_test_or_extra_statistics_included"] is False, "audit scope")
    train_order = audit_private["loader_order_case_ids"]
    require(len(train_order) == 584 and set(train_order) == set(buckets["train"]), "train membership")
    require(_ordered_digest(train_order) == split["train_loader_order_sha256"], "train order")
    torch.set_num_threads(4)
    steady = safe_torch_load(args.steady, torch)
    normalizer = {"label": steady["label"], "tensor_norm": steady["tensor_norm"]}
    del steady
    transient = safe_torch_load(args.transient, torch)
    rows, record_keys = [], set()
    excluded = buckets["validation"] + buckets["test"] + buckets["extra"]
    for index, (case_id, field, areas, keys) in enumerate(iter_training_fields(
            transient, normalizer, train_order, excluded,
            expected_shape=tuple(config["expected_shape"])), start=1):
        result = audit_cycle(field, areas, config["cutoffs"])
        rows.append(result)
        record_keys.update(keys)
        _strict_atomic_json(args.output / "cases" / f"{index:03d}.json", {"case_id": case_id, **result})
        if index % 25 == 0 or index == 584:
            print(json.dumps({"stage": "train_cycle_audit", "completed": index, "expected": 584}), flush=True)
    require(len(rows) == 584, "complete train audit")
    result = {
        "schema_version": "aurora.private.cycle_representation_result.v3",
        "status": "complete_train_representation_audit_not_model_result",
        "config_sha256": file_sha256(args.config), "reader_config_sha256": file_sha256(reader_path),
        "source_assets_sha256": {key: value[1] for key, value in paths.items()},
        "source_commit": os.environ["AURORA_EXPECTED_COMMIT"], "job_id": os.environ["PBS_JOBID"],
        "torch_version": str(torch.__version__), "phase_grid": config["phase_grid"],
        "physical_timestamps_verified": False, "record_metadata_keys": sorted(record_keys),
        "archive_metadata_keys": sorted(str(key) for key in transient.keys()),
        "historical_test_already_opened": True,
        "field_reads": {"train_cases": 584, "validation_cases": 0, "test_cases": 0, "extra_cases": 0},
        "steady_case_fields_decoded": 0, "automatic_model_selection": False,
        "summary": aggregate(rows, config["cutoffs"]),
    }
    _strict_atomic_json(args.output / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    for name in ("public-root", "transient", "steady", "private-split", "private-train-audit", "output"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    validate_config(json.loads(args.config.read_text()))
    if args.validate_only:
        print(json.dumps({"stage": "cycle_audit_config_valid", "dataset_reads": 0}))
        return 0
    require(all(getattr(args, name.replace("-", "_")) is not None for name in (
        "public-root", "transient", "steady", "private-split", "private-train-audit", "output")), "paths required")
    result = run(args)
    print(json.dumps({"stage": "cycle_audit_complete", "cases": result["summary"]["case_count"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

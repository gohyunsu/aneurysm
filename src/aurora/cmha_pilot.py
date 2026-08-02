"""Patient-grouped CMHA G1 pilot.

This module deliberately implements a small, auditable linear baseline.  Its
purpose is to test whether the real-CFD summary variables contain incremental
rupture-status information before the expensive AURORA operator is trained.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import shlex
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from torch import nn


CLINICAL_FILE = "clinical_all.csv"
MORPHOLOGY_FILE = "morphological_aneurysm_artery.csv"
HEMODYNAMIC_FILE = "hemodynamic_aneurysm_artery.csv"

CLINICAL_EXCLUDE = {
    "number",
    "Rupture",
    "Has aneurysm",
    "Shape",
    "location",
}
MORPHOLOGY_CONTEXT = {"Shape", "location"}


@dataclass(frozen=True)
class Cohort:
    labels: np.ndarray
    groups: np.ndarray
    matrices: dict[str, np.ndarray]
    feature_names: dict[str, list[str]]
    audit: dict[str, object]
    source_files: list[Path]


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path.name}")
        return list(reader.fieldnames), rows


def _as_float(value: str) -> float | None:
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def _encode_columns(
    rows: Sequence[dict[str, str]],
    columns: Sequence[str],
    *,
    max_categories: int = 20,
) -> tuple[np.ndarray, list[str]]:
    encoded: list[np.ndarray] = []
    names: list[str] = []
    for column in columns:
        values = [str(row.get(column, "")).strip() for row in rows]
        numeric = [_as_float(value) for value in values]
        observed = sum(bool(value) for value in values)
        numeric_count = sum(value is not None for value in numeric)

        if observed and numeric_count / observed >= 0.95:
            encoded.append(
                np.asarray(
                    [np.nan if value is None else value for value in numeric],
                    dtype=np.float64,
                )[:, None]
            )
            names.append(column)
            continue

        categories = sorted({value for value in values if value})
        if not categories or len(categories) > max_categories:
            continue
        # Drop the first category to avoid a redundant column in the linear model.
        for category in categories[1:]:
            encoded.append(
                np.asarray([float(value == category) for value in values], dtype=np.float64)[
                    :, None
                ]
            )
            names.append(f"{column}={category}")

    if not encoded:
        raise ValueError("No usable columns were found")
    return np.concatenate(encoded, axis=1), names


def load_cmha_cohort(data_root: Path) -> Cohort:
    """Load the 105-lesion CMHA table set without exporting source identifiers.

    The released tables are row-aligned.  Six multi-aneurysm patients use a
    suffixed identifier in the morphology table and repeat the patient identifier
    in clinical/hemodynamic tables.  We preserve the clinical patient identifier
    only in memory as the grouping key and never write it to run artifacts.
    """

    clinical_path = data_root / CLINICAL_FILE
    morphology_path = data_root / MORPHOLOGY_FILE
    hemodynamic_path = data_root / HEMODYNAMIC_FILE
    paths = [clinical_path, morphology_path, hemodynamic_path]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    clinical_columns, clinical_all = _read_csv(clinical_path)
    morphology_columns, morphology = _read_csv(morphology_path)
    hemodynamic_columns, hemodynamic = _read_csv(hemodynamic_path)
    clinical = [
        row for row in clinical_all if str(row.get("Rupture", "")).strip() in {"0", "1"}
    ]

    lengths = {len(clinical), len(morphology), len(hemodynamic)}
    if lengths != {105}:
        raise ValueError(
            "Expected 105 row-aligned aneurysm records; "
            f"got clinical={len(clinical)}, morphology={len(morphology)}, "
            f"hemodynamics={len(hemodynamic)}"
        )

    clinical_ids = [row["number"].strip() for row in clinical]
    morphology_ids = [row["number"].strip() for row in morphology]
    hemodynamic_ids = [row["number"].strip() for row in hemodynamic]
    clinical_hemo_matches = sum(
        clinical_id == hemodynamic_id
        for clinical_id, hemodynamic_id in zip(clinical_ids, hemodynamic_ids)
    )
    morphology_compatible = sum(
        morphology_id == clinical_id or morphology_id.startswith(f"{clinical_id}_")
        for clinical_id, morphology_id in zip(clinical_ids, morphology_ids)
    )
    if clinical_hemo_matches < 104 or morphology_compatible != 105:
        raise ValueError(
            "Released-table row alignment did not satisfy the predeclared audit: "
            f"clinical/hemodynamic={clinical_hemo_matches}, "
            f"morphology-compatible={morphology_compatible}"
        )

    labels = np.asarray([int(row["Rupture"].strip()) for row in clinical], dtype=np.int64)
    group_map = {identifier: index for index, identifier in enumerate(dict.fromkeys(clinical_ids))}
    groups = np.asarray([group_map[identifier] for identifier in clinical_ids], dtype=np.int64)

    clinical_features = [
        column for column in clinical_columns if column not in CLINICAL_EXCLUDE
    ]
    morphology_context = [
        column for column in clinical_columns if column in MORPHOLOGY_CONTEXT
    ]
    morphology_features = [
        column for column in morphology_columns if column != "number"
    ]
    hemodynamic_features = [
        column
        for column in hemodynamic_columns
        if column != "number" and "location" not in column.lower()
    ]

    x_clinical, n_clinical = _encode_columns(clinical, clinical_features)
    x_context, n_context = _encode_columns(clinical, morphology_context)
    x_morphology, n_morphology = _encode_columns(morphology, morphology_features)
    x_hemodynamic, n_hemodynamic = _encode_columns(hemodynamic, hemodynamic_features)

    x_clinical_morphology = np.concatenate(
        [x_clinical, x_context, x_morphology], axis=1
    )
    x_full = np.concatenate([x_clinical_morphology, x_hemodynamic], axis=1)

    group_sizes = Counter(groups.tolist())
    conflicting_groups = 0
    for group in sorted(group_sizes):
        group_labels = set(labels[groups == group].tolist())
        conflicting_groups += int(len(group_labels) > 1)

    audit = {
        "lesions": int(len(labels)),
        "patients": int(len(group_sizes)),
        "multi_lesion_patients": int(sum(size > 1 for size in group_sizes.values())),
        "patients_with_mixed_lesion_status": int(conflicting_groups),
        "class_counts": {
            "unruptured": int((labels == 0).sum()),
            "ruptured": int((labels == 1).sum()),
        },
        "row_alignment": {
            "clinical_hemodynamic_exact": int(clinical_hemo_matches),
            "morphology_patient_or_lesion_suffix": int(morphology_compatible),
            "expected_rows": 105,
        },
        "identifier_policy": (
            "Source identifiers remain in memory only; splits and artifacts use "
            "integer group indices and anonymous row indices."
        ),
        "evidence_status": (
            "exploratory_row_alignment; confirm against the release data dictionary "
            "before a confirmatory run"
        ),
    }
    return Cohort(
        labels=labels,
        groups=groups,
        matrices={
            "clinical": x_clinical,
            "clinical_morphology": x_clinical_morphology,
            "clinical_morphology_hemodynamics": x_full,
        },
        feature_names={
            "clinical": n_clinical,
            "clinical_morphology": n_clinical + n_context + n_morphology,
            "clinical_morphology_hemodynamics": (
                n_clinical + n_context + n_morphology + n_hemodynamic
            ),
        },
        audit=audit,
        source_files=paths,
    )


def grouped_stratified_folds(
    labels: np.ndarray,
    groups: np.ndarray,
    n_splits: int,
    seed: int,
) -> list[np.ndarray]:
    """Return lesion indices for deterministic, approximately stratified group folds."""

    unique_groups = np.unique(groups)
    if len(unique_groups) < n_splits:
        raise ValueError("The number of groups must be at least n_splits")

    rng = random.Random(seed)
    records: list[tuple[int, np.ndarray, int, int, float]] = []
    for group in unique_groups:
        indices = np.flatnonzero(groups == group)
        positive = int(labels[indices].sum())
        negative = int(len(indices) - positive)
        records.append((int(group), indices, positive, negative, rng.random()))
    records.sort(key=lambda item: (-len(item[1]), -abs(item[2] - item[3]), item[4]))

    target_positive = float(labels.sum()) / n_splits
    target_negative = float((1 - labels).sum()) / n_splits
    folds: list[list[int]] = [[] for _ in range(n_splits)]
    fold_positive = [0] * n_splits
    fold_negative = [0] * n_splits

    for _, indices, positive, negative, _ in records:
        order = list(range(n_splits))
        rng.shuffle(order)

        def score(fold: int) -> tuple[float, int]:
            class_cost = (
                ((fold_positive[fold] + positive - target_positive) ** 2)
                / (target_positive + 1.0)
                + ((fold_negative[fold] + negative - target_negative) ** 2)
                / (target_negative + 1.0)
            )
            return class_cost, len(folds[fold])

        chosen = min(order, key=score)
        folds[chosen].extend(indices.tolist())
        fold_positive[chosen] += positive
        fold_negative[chosen] += negative

    result = [np.asarray(sorted(fold), dtype=np.int64) for fold in folds]
    if any(len(fold) == 0 for fold in result):
        raise RuntimeError("Grouped fold assignment produced an empty fold")
    return result


def _rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2.0 + 1.0
        start = end
    return ranks


def classification_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    labels = np.asarray(labels, dtype=np.int64)
    probabilities = np.clip(np.asarray(probabilities, dtype=np.float64), 1e-7, 1 - 1e-7)
    positive = labels == 1
    negative = ~positive
    if not positive.any() or not negative.any():
        raise ValueError("Both classes are required")

    ranks = _rankdata(probabilities)
    auroc = (
        ranks[positive].sum() - positive.sum() * (positive.sum() + 1) / 2.0
    ) / (positive.sum() * negative.sum())

    order = np.argsort(-probabilities, kind="mergesort")
    ordered_labels = labels[order]
    precision = np.cumsum(ordered_labels) / np.arange(1, len(labels) + 1)
    auprc = float((precision * ordered_labels).sum() / positive.sum())

    prediction = probabilities >= 0.5
    sensitivity = float(prediction[positive].mean())
    specificity = float((~prediction[negative]).mean())
    balanced_accuracy = (sensitivity + specificity) / 2.0

    ece = 0.0
    for lower in np.linspace(0.0, 0.9, 10):
        upper = lower + 0.1
        in_bin = (probabilities >= lower) & (
            probabilities <= upper if upper >= 1.0 else probabilities < upper
        )
        if in_bin.any():
            ece += float(in_bin.mean()) * abs(
                float(labels[in_bin].mean()) - float(probabilities[in_bin].mean())
            )

    return {
        "auroc": float(auroc),
        "auprc": auprc,
        "balanced_accuracy": float(balanced_accuracy),
        "brier": float(np.mean((probabilities - labels) ** 2)),
        "ece_10": float(ece),
    }


def _standardize(
    train: np.ndarray, test: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    median = np.nanmedian(train, axis=0)
    median = np.where(np.isfinite(median), median, 0.0)
    train = np.where(np.isfinite(train), train, median)
    test = np.where(np.isfinite(test), test, median)
    mean = train.mean(axis=0)
    std = train.std(axis=0)
    std = np.where(std > 1e-8, std, 1.0)
    return (train - mean) / std, (test - mean) / std


def _fit_predict(
    features: np.ndarray,
    labels: np.ndarray,
    train_indices: np.ndarray,
    test_indices: np.ndarray,
    *,
    l2: float,
    epochs: int,
    learning_rate: float,
    seed: int,
    device: torch.device,
) -> np.ndarray:
    x_train, x_test = _standardize(features[train_indices], features[test_indices])
    y_train = labels[train_indices]

    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    model = nn.Linear(x_train.shape[1], 1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_function = nn.BCEWithLogitsLoss()
    x_tensor = torch.as_tensor(x_train, dtype=torch.float32, device=device)
    y_tensor = torch.as_tensor(y_train[:, None], dtype=torch.float32, device=device)

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        logits = model(x_tensor)
        penalty = sum(parameter.square().sum() for parameter in model.parameters())
        loss = loss_function(logits, y_tensor) + l2 * penalty
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.inference_mode():
        probabilities = torch.sigmoid(
            model(torch.as_tensor(x_test, dtype=torch.float32, device=device))
        )
    return probabilities[:, 0].detach().cpu().numpy()


def _select_l2(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    train_indices: np.ndarray,
    candidates: Sequence[float],
    *,
    inner_splits: int,
    epochs: int,
    learning_rate: float,
    seed: int,
    device: torch.device,
) -> float:
    local_labels = labels[train_indices]
    local_groups = groups[train_indices]
    folds = grouped_stratified_folds(local_labels, local_groups, inner_splits, seed)
    scores: dict[float, list[float]] = {candidate: [] for candidate in candidates}
    all_local = np.arange(len(train_indices), dtype=np.int64)

    for candidate in candidates:
        for fold_index, validation_local in enumerate(folds):
            training_local = np.setdiff1d(all_local, validation_local, assume_unique=True)
            probabilities = _fit_predict(
                features,
                labels,
                train_indices[training_local],
                train_indices[validation_local],
                l2=candidate,
                epochs=epochs,
                learning_rate=learning_rate,
                seed=seed * 100 + fold_index,
                device=device,
            )
            scores[candidate].append(
                classification_metrics(labels[train_indices[validation_local]], probabilities)[
                    "auprc"
                ]
            )
    return max(candidates, key=lambda candidate: (np.mean(scores[candidate]), -candidate))


def _bootstrap_delta(
    labels: np.ndarray,
    groups: np.ndarray,
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    samples: int,
    seed: int,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    unique_groups = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique_groups}
    deltas: list[float] = []
    for _ in range(samples):
        sampled_groups = rng.choice(unique_groups, size=len(unique_groups), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled_groups])
        sampled_labels = labels[indices]
        if len(np.unique(sampled_labels)) < 2:
            continue
        deltas.append(
            classification_metrics(sampled_labels, candidate[indices])["auprc"]
            - classification_metrics(sampled_labels, reference[indices])["auprc"]
        )
    values = np.asarray(deltas, dtype=np.float64)
    return {
        "estimate": float(
            classification_metrics(labels, candidate)["auprc"]
            - classification_metrics(labels, reference)["auprc"]
        ),
        "ci95_low": float(np.quantile(values, 0.025)),
        "ci95_high": float(np.quantile(values, 0.975)),
        "bootstrap_samples": int(len(values)),
        "bootstrap_unit": "patient",
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(args: argparse.Namespace) -> dict[str, object]:
    if args.require_cuda and not torch.cuda.is_available():
        raise RuntimeError("CUDA was required but is not available inside the allocation")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cohort = load_cmha_cohort(args.data_root)
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_lines = [f"{_sha256(path)}  {path.name}" for path in cohort.source_files]
    (output_dir / "dataset_manifest.sha256").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )
    (output_dir / "command.txt").write_text(
        shlex.join([sys.executable, *sys.argv]) + "\n", encoding="utf-8"
    )

    configuration = {
        "outer_splits": args.outer_splits,
        "inner_splits": args.inner_splits,
        "repeats": args.repeats,
        "seeds": list(range(args.repeats)),
        "l2_candidates": args.l2,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "bootstrap_samples": args.bootstrap_samples,
        "model": "linear_logistic_regression",
        "selection_metric": "inner_oof_auprc",
        "split_unit": "patient",
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    all_indices = np.arange(len(cohort.labels), dtype=np.int64)
    predictions: dict[str, list[np.ndarray]] = defaultdict(list)
    selected_l2: dict[str, list[float]] = defaultdict(list)

    for repeat in range(args.repeats):
        outer_folds = grouped_stratified_folds(
            cohort.labels, cohort.groups, args.outer_splits, seed=repeat
        )
        repeat_predictions = {
            feature_set: np.full(len(cohort.labels), np.nan, dtype=np.float64)
            for feature_set in cohort.matrices
        }
        for outer_index, test_indices in enumerate(outer_folds):
            train_indices = np.setdiff1d(all_indices, test_indices, assume_unique=True)
            for feature_set, features in cohort.matrices.items():
                l2 = _select_l2(
                    features,
                    cohort.labels,
                    cohort.groups,
                    train_indices,
                    args.l2,
                    inner_splits=args.inner_splits,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    seed=repeat * 100 + outer_index,
                    device=device,
                )
                selected_l2[feature_set].append(l2)
                repeat_predictions[feature_set][test_indices] = _fit_predict(
                    features,
                    cohort.labels,
                    train_indices,
                    test_indices,
                    l2=l2,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    seed=repeat * 1000 + outer_index,
                    device=device,
                )
        for feature_set, values in repeat_predictions.items():
            if not np.isfinite(values).all():
                raise RuntimeError(f"Missing OOF predictions for {feature_set}")
            predictions[feature_set].append(values)

    mean_predictions = {
        feature_set: np.mean(np.stack(values, axis=0), axis=0)
        for feature_set, values in predictions.items()
    }
    aggregate_metrics = {
        feature_set: {
            **classification_metrics(cohort.labels, values),
            "feature_count": int(cohort.matrices[feature_set].shape[1]),
            "selected_l2_counts": {
                str(value): count
                for value, count in sorted(Counter(selected_l2[feature_set]).items())
            },
        }
        for feature_set, values in mean_predictions.items()
    }
    delta = _bootstrap_delta(
        cohort.labels,
        cohort.groups,
        mean_predictions["clinical_morphology"],
        mean_predictions["clinical_morphology_hemodynamics"],
        samples=args.bootstrap_samples,
        seed=20260803,
    )
    gate = (
        "supports_incremental_utility"
        if delta["ci95_low"] > 0
        else "does_not_establish_incremental_utility"
    )
    result: dict[str, object] = {
        "schema_version": "aurora.cmha_g1_pilot.v1",
        "evidence_status": "exploratory",
        "cohort_audit": cohort.audit,
        "hardware": {
            "device": str(device),
            "device_name": (
                torch.cuda.get_device_name(0) if device.type == "cuda" else platform.processor()
            ),
            "torch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
        },
        "configuration": configuration,
        "metrics": aggregate_metrics,
        "g1_incremental_hemodynamic_auprc": {**delta, "pilot_interpretation": gate},
        "limitations": [
            "Released-table row alignment is audited but not yet confirmed by a formal case map.",
            "This is a single-center, cross-sectional status analysis, not prospective risk.",
            "The linear pilot tests incremental signal; it is not the AURORA operator.",
            "Feature vocabulary is derived without outcomes from the full released table.",
        ],
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "environment.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "torch": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_device_count": torch.cuda.device_count(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "status.json").write_text(
        json.dumps({"status": "complete", "evidence_status": "exploratory"}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-splits", type=int, default=5)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--epochs", type=int, default=250)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--l2", type=float, nargs="+", default=[1e-4, 1e-3, 1e-2, 1e-1])
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--require-cuda", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "status.json").write_text(
        json.dumps({"status": "running", "pid": os.getpid()}, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        result = run(args)
    except Exception as error:
        (args.output / "status.json").write_text(
            json.dumps(
                {"status": "failed", "error_type": type(error).__name__, "error": str(error)},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        raise
    print(json.dumps(result["g1_incremental_hemodynamic_auprc"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

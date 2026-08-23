"""Lazy steady-field access for the release-730 matched-information cells.

The public scope and exposure utilities decide *which* leakage-audited rows a
future T+S training cell may consume and in what order.  This module closes a
separate implementation boundary: it decodes exactly one scheduled row at a
time from the mmap-backed processed archive.  It deliberately contains no
model, loss weight, optimizer, activation, or GPU entry point.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Iterator, Mapping, Sequence

import torch

from aurora.aneug_release_730_steady_exposure_schedule import _cycle_order
from aurora.aneug_release_730_steady_exposure_schedule import ordered_digest
from aurora.aneug_release_730_train_audit import _vertex_areas


class MatchedSteadyStreamError(RuntimeError):
    """Raised when a lazy steady-field read violates the matched contract."""


EXPECTED_LABELS = (
    "x",
    "y",
    "z",
    "x_normal",
    "y_normal",
    "z_normal",
    "wss_x",
    "wss_y",
    "wss_z",
)


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise MatchedSteadyStreamError(reason)


class ExposureDigest:
    """Incrementally reproduce the schedule's newline-joined prefix digest."""

    def __init__(self) -> None:
        self._digest = hashlib.sha256()
        self.count = 0

    def update(self, index: int) -> None:
        _require(int(index) >= 0, "exposure_index")
        if self.count:
            self._digest.update(b"\n")
        self._digest.update(str(int(index)).encode("utf-8"))
        self.count += 1

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def epoch_exposure_indices(
    eligible_indices: Sequence[int],
    *,
    epoch: int,
    cases_per_epoch: int,
    seed: int,
) -> Iterator[int]:
    """Yield one epoch without materializing the full multi-epoch prefix."""

    normalized = tuple(int(value) for value in eligible_indices)
    _require(
        len(normalized) > 0
        and len(set(normalized)) == len(normalized)
        and all(value >= 0 for value in normalized),
        "eligible_indices",
    )
    _require(epoch >= 0 and cases_per_epoch > 0, "epoch")
    start = epoch * cases_per_epoch
    stop = start + cases_per_epoch
    size = len(normalized)
    first_cycle = start // size
    last_cycle = (stop - 1) // size
    for cycle in range(first_cycle, last_cycle + 1):
        order = _cycle_order(normalized, seed, cycle)
        cycle_start = cycle * size
        left = max(start, cycle_start) - cycle_start
        right = min(stop, cycle_start + size) - cycle_start
        yield from order[left:right]


class MatchedSteadyStream:
    """Validate archive metadata once and decode only explicitly requested rows."""

    def __init__(
        self,
        archive: Mapping[str, Any],
        eligible_indices: Sequence[int],
        *,
        ghd_mean: torch.Tensor,
        ghd_std: torch.Tensor,
        faces: torch.Tensor,
        expected_rows: int = 14_392,
        expected_nodes: int = 13_902,
        expected_eligible_rows: int = 13_985,
        expected_ordered_index_digest: str = (
            "292946acf8857942a68df1626ca58cf46f5260b0d64b277439b42a92d5bd4629"
        ),
    ) -> None:
        _require(isinstance(archive, Mapping), "archive")
        _require(
            {"label", "tensor_norm", "tensor", "ghd_dict", "case_name"}.issubset(
                archive
            ),
            "archive_keys",
        )
        _require(tuple(str(value) for value in archive["label"]) == EXPECTED_LABELS, "labels")
        tensor = archive["tensor"]
        ghd = archive["ghd_dict"]["ghd"]
        _require(
            tuple(int(value) for value in tensor.shape)
            == (expected_rows, expected_nodes, 9),
            "tensor_shape",
        )
        _require(
            tuple(int(value) for value in ghd.shape) == (expected_rows, 432),
            "ghd_shape",
        )
        _require(len(archive["case_name"]) == expected_rows, "case_names")
        normalized_indices = tuple(int(value) for value in eligible_indices)
        _require(
            len(normalized_indices) == expected_eligible_rows
            and len(set(normalized_indices)) == len(normalized_indices)
            and tuple(sorted(normalized_indices)) == normalized_indices
            and normalized_indices[0] >= 0
            and normalized_indices[-1] < expected_rows,
            "eligible_indices",
        )
        _require(
            ordered_digest(normalized_indices) == expected_ordered_index_digest,
            "eligible_index_digest",
        )
        normalizer = archive["tensor_norm"]
        decoder_mean = normalizer["mean"].detach().cpu().to(torch.float32).reshape(-1)
        decoder_std = normalizer["std"].detach().cpu().to(torch.float32).reshape(-1)
        _require(
            decoder_mean.shape == decoder_std.shape == (9,)
            and bool(torch.isfinite(decoder_mean).all().item())
            and bool(torch.isfinite(decoder_std).all().item())
            and bool((decoder_std > 0).all().item()),
            "normalizer",
        )
        normalized_ghd_mean = ghd_mean.detach().cpu().to(torch.float32).reshape(-1)
        normalized_ghd_std = ghd_std.detach().cpu().to(torch.float32).reshape(-1)
        _require(
            normalized_ghd_mean.shape == normalized_ghd_std.shape == (432,)
            and bool(torch.isfinite(normalized_ghd_mean).all().item())
            and bool(torch.isfinite(normalized_ghd_std).all().item())
            and bool((normalized_ghd_std > 0).all().item()),
            "ghd_normalizer",
        )
        normalized_faces = faces.detach().cpu().to(torch.int64)
        _require(
            normalized_faces.ndim == 2
            and normalized_faces.shape[1] == 3
            and normalized_faces.numel() > 0
            and int(normalized_faces.min().item()) >= 0
            and int(normalized_faces.max().item()) < expected_nodes,
            "faces",
        )
        self._tensor = tensor
        self._ghd = ghd
        self._eligible = frozenset(normalized_indices)
        self._decoder_mean = decoder_mean
        self._decoder_std = decoder_std
        self._ghd_mean = normalized_ghd_mean
        self._ghd_std = normalized_ghd_std
        self._faces = normalized_faces
        self.nodes = int(expected_nodes)

    def decode(self, index: int) -> dict[str, torch.Tensor]:
        """Read and decode one eligible row, never an advanced-indexed cohort."""

        row_index = int(index)
        _require(row_index in self._eligible, "ineligible_row")
        normalized = self._tensor[row_index].detach().cpu().to(torch.float32)
        raw_ghd = self._ghd[row_index].detach().cpu().to(torch.float32)
        _require(normalized.shape == (self.nodes, 9), "row_shape")
        _require(raw_ghd.shape == (432,), "row_ghd_shape")
        _require(
            bool(torch.isfinite(normalized).all().item())
            and bool(torch.isfinite(raw_ghd).all().item()),
            "row_finite",
        )
        physical = normalized * (self._decoder_std.reshape(1, 9) + 1e-5)
        physical = physical + self._decoder_mean.reshape(1, 9)
        coordinates = physical[:, :3].to(torch.float64)
        center = coordinates.mean(dim=0, keepdim=True)
        centered = coordinates - center
        coordinate_scale = torch.sqrt(torch.mean(torch.sum(centered.square(), dim=-1)))
        _require(
            bool(torch.isfinite(coordinate_scale).item())
            and float(coordinate_scale.item()) > 0.0,
            "coordinate_scale",
        )
        weights, normals, twice_area = _vertex_areas(coordinates, self._faces, torch)
        _require(
            bool((weights > 0).all().item()) and bool((twice_area > 0).all().item()),
            "mesh",
        )
        ghd = (raw_ghd - self._ghd_mean) / self._ghd_std
        _require(bool(torch.isfinite(ghd).all().item()), "normalized_ghd")
        return {
            "coordinates": (centered / coordinate_scale).to(torch.float32).contiguous(),
            "normals": normals.to(torch.float32).contiguous(),
            "vertex_weights": (weights / weights.sum()).to(torch.float32).contiguous(),
            "ghd": ghd.contiguous(),
            "steady_wss": physical[:, 6:9].to(torch.float32).contiguous(),
        }


def single_field_relative_squared_error(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    vertex_weights: torch.Tensor,
) -> torch.Tensor:
    """Area-weighted relative squared error for one steady vector field."""

    _require(
        prediction.ndim == reference.ndim == 2
        and prediction.shape == reference.shape
        and prediction.shape[1] == 3,
        "field_shape",
    )
    _require(vertex_weights.shape == (prediction.shape[0],), "weight_shape")
    _require(
        bool(torch.isfinite(prediction).all().item())
        and bool(torch.isfinite(reference).all().item())
        and bool(torch.isfinite(vertex_weights).all().item())
        and bool((vertex_weights > 0).all().item()),
        "field_finite",
    )
    numerator = torch.sum(vertex_weights * torch.sum((prediction - reference) ** 2, dim=-1))
    denominator = torch.sum(vertex_weights * torch.sum(reference**2, dim=-1))
    loss = numerator / torch.clamp(denominator, min=1e-12)
    _require(bool(torch.isfinite(loss).item()) and math.isfinite(float(loss.item())), "loss")
    return loss

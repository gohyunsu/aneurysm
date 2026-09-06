"""Size-preserving geometry inputs, fitted on admitted transient training only.

The legacy reader divides every mesh by its own RMS radius. Keeping only those
coordinates and normals identifies all positive uniform dilations, regardless
of a model's capacity. Retain the decoded radius and divide centered positions
by ONE training-derived isotropic reference instead. This is an input-fidelity
correction/control, not a new network or an empirical accuracy claim.
"""
from __future__ import annotations

import math
from typing import Mapping, Sequence

import torch

PROFILE = "centered_decoded_coordinates_over_transient_train_rms_v1"
RADIUS = "physical_coordinate_rms"
APPLIED = "geometry_scale_reference_rms"


def _radius(case):
    value = case[RADIUS]
    if (not isinstance(value, torch.Tensor) or value.numel() != 1
            or not value.is_floating_point() or not bool(torch.isfinite(value).all())
            or not bool((value > 0).all())):
        raise ValueError("positive finite decoded geometry radius required")
    return value.detach().reshape(())


def fit_geometry_scale(train_cases: Sequence[Mapping], *, expected_train_cases: int):
    """No label, validation, steady or held-out value participates in this fit."""
    if (type(expected_train_cases) is not int or expected_train_cases < 1
            or len(train_cases) != expected_train_cases):
        raise ValueError("explicit admitted training membership count required")
    radii = torch.stack([_radius(case).cpu().double() for case in train_cases])
    reference = float(radii.square().mean().sqrt())
    if not math.isfinite(reference) or reference <= 0:
        raise ValueError("finite positive training geometry RMS required")
    return dict(schema_version="aurora.geometry_scale.v1", profile=PROFILE,
                train_case_count=len(train_cases), reference_rms=reference,
                minimum_train_radius=float(radii.min()), maximum_train_radius=float(radii.max()),
                fit_inputs="admitted_transient_training_geometry_only",
                decoded_coordinate_unit="source_units_not_claimed_millimetres_or_metres",
                target_statistics_used=False, validation_geometry_used=False,
                steady_geometry_used=False, test_or_extra_geometry_used=False)


def _reference(contract):
    reference = contract.get("reference_rms")
    if (contract.get("schema_version") != "aurora.geometry_scale.v1"
            or contract.get("profile") != PROFILE
            or isinstance(reference, bool) or not isinstance(reference, (int, float))
            or not math.isfinite(reference) or reference <= 0
            or contract.get("fit_inputs") != "admitted_transient_training_geometry_only"
            or any(contract.get(key) is not False for key in
                   ("target_statistics_used", "validation_geometry_used", "steady_geometry_used", "test_or_extra_geometry_used"))):
        raise ValueError("explicit training-only size-preserving coordinate contract required")
    return reference


def apply_geometry_scale(case: Mapping, contract: Mapping):
    """Replace coordinates only; no mutation, field rescaling or GHD conversion."""
    reference = _reference(contract)
    if APPLIED in case:
        raise ValueError("geometry scale transform already applied")
    coordinates = case["coordinates"]
    radius = _radius(case)
    if (coordinates.ndim != 2 or coordinates.shape[1] != 3
            or not coordinates.is_floating_point() or not bool(torch.isfinite(coordinates).all())):
        raise ValueError("finite [N,3] legacy centered coordinates required")
    result = dict(case)
    result["coordinates"] = (coordinates.double() * (radius.to(coordinates.device).double() / reference)).to(coordinates.dtype)
    result[APPLIED] = radius.new_tensor(reference)
    return result


class SizePreservingSteadyStream:
    """Keep the original eligible-row reader and deterministic exposure schedule."""
    def __init__(self, stream, contract):
        _reference(contract)
        self.stream, self.contract = stream, dict(contract)

    def decode(self, index):
        return apply_geometry_scale(self.stream.decode(index, retain_coordinate_scale=True), self.contract)

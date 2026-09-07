"""Post-hoc temporal error decomposition of an already predicted vector cycle.

This is an evaluator, not a loss, filter, model, or new physical-time claim.
All snapshots remain on the nominal uniform index grid. Parseval contributions
sum to squared physical field rL2; DC and oscillatory errors are not conflated
with steady CFD. A numerically empty reference band still contributes error
to the full-field denominator, but its band-relative rL2 is undefined.
"""
from __future__ import annotations

import math
import statistics
from typing import Mapping, Sequence

import torch


NUMERICAL_SUPPORT_FRACTION = 64 * torch.finfo(torch.float64).eps
COMMON_FIELD_ENERGY_FLOOR = 1e-12


@torch.no_grad()
def cycle_error_spectrum(prediction: torch.Tensor, reference: torch.Tensor,
                         areas: torch.Tensor) -> dict:
    """Return one case's area/uniform-phase-weighted, physical-vector errors.

    No independent phase/vertex samples are created. No endpoint is removed,
    interpolated or equalized. Fourier bins mean cycles per nominal sampled
    cycle, not verified Hz. This routine consumes supplied arrays only; the
    caller must separately enforce cohort and selected-checkpoint provenance.
    """
    arrays = (prediction, reference, areas)
    if any(not torch.is_tensor(x) or not x.is_floating_point() for x in arrays):
        raise ValueError("real floating physical fields and area weights required")
    p, r, w = (x.detach().cpu().to(torch.float64) for x in arrays)
    if (p.shape != r.shape or r.ndim != 3 or r.shape[-1] != 3
            or r.shape[0] < 3 or r.shape[1] < 1 or w.shape != (r.shape[1],)):
        raise ValueError("matching [phase,node,3] fields and [node] areas required")
    if (not all(bool(torch.isfinite(x).all()) for x in (p, r, w))
            or not bool((w >= 0).all() and w.sum() > 0)):
        raise ValueError("finite fields and nonnegative nonempty area support required")
    w = w / w.sum()
    count = r.shape[0]
    reference_energy = float((r.square() * w[None, :, None]).sum() / count)
    error_energy = float(((p - r).square() * w[None, :, None]).sum() / count)
    if not math.isfinite(reference_energy) or reference_energy <= 0 or not math.isfinite(error_energy):
        raise ValueError("finite nonzero reference energy and finite error energy required")
    # Retain the shared field_loss denominator even for extremely small fields.
    denominator = max(reference_energy, COMMON_FIELD_ENERGY_FLOOR)
    multiplicity = torch.full((count // 2 + 1,), 2., dtype=torch.float64)
    multiplicity[0] = 1.
    if count % 2 == 0:
        multiplicity[-1] = 1.

    def energies(field):
        # Expanded/broadcast tensors can have zero strides unsupported by MKL.
        spectrum = torch.fft.rfft(field.contiguous(), dim=0, norm="ortho")
        return (spectrum.abs().square() * w[None, :, None]).sum((1, 2)) * multiplicity / count

    ref_modes, err_modes = energies(r), energies(p - r)
    ref_discrepancy = abs(float(ref_modes.sum()) - reference_energy) / reference_energy
    err_discrepancy = abs(float(err_modes.sum()) - error_energy) / max(reference_energy, error_energy)
    if max(ref_discrepancy, err_discrepancy) > 1e-10:
        raise ArithmeticError("time-domain and Fourier-domain energies disagree")

    def band(start, stop):
        ref = float(ref_modes[start:stop].sum())
        err = float(err_modes[start:stop].sum())
        supported = ref > NUMERICAL_SUPPORT_FRACTION * reference_energy
        return dict(reference_energy_fraction=ref / reference_energy,
                    squared_error_contribution=err / denominator,
                    reference_support_resolved=supported,
                    band_relative_l2=math.sqrt(err / ref) if supported else None)

    return dict(schema_version="aurora.cycle_error_spectrum.v3",
        phase_grid="nominal_uniform_snapshot_index", physical_timestamps_verified=False,
        phase_count=count, frequency_indices=list(range(len(ref_modes))),
        frequency_reference_energy_fraction=(ref_modes / reference_energy).tolist(),
        frequency_squared_error_contribution=(err_modes / denominator).tolist(),
        field_relative_l2=math.sqrt(error_energy / denominator),
        field_relative_squared_error=error_energy / denominator,
        field_energy_denominator=denominator,
        common_field_energy_floor=COMMON_FIELD_ENERGY_FLOOR,
        reference_cycle_mean_squared_vector_norm=reference_energy,
        dc=band(0, 1), oscillatory=band(1, len(ref_modes)),
        numerical_support_fraction=NUMERICAL_SUPPORT_FRACTION,
        parseval_relative_discrepancy=max(ref_discrepancy, err_discrepancy))


def summarize_spectra(rows: Sequence[Mapping]) -> dict:
    """Equal-case summary, not vertex/phase pooling or a significance test.

    Mean squared contributions sum to mean squared rL2, NOT the square of
    mean rL2. Band-relative means explicitly report their supported case count.
    """
    if not rows:
        raise ValueError("nonempty case rows required")
    count = rows[0]["phase_count"]
    for row in rows:
        if (row["schema_version"] != "aurora.cycle_error_spectrum.v3"
                or row["phase_count"] != count
                or row["phase_grid"] != "nominal_uniform_snapshot_index"
                or row["physical_timestamps_verified"] is not False
                or row["frequency_indices"] != list(range(count // 2 + 1))):
            raise ValueError("matching complete-cycle spectral conventions required")
        energy = row["reference_cycle_mean_squared_vector_norm"]
        if (not math.isfinite(energy) or energy <= 0
                or row["common_field_energy_floor"] != COMMON_FIELD_ENERGY_FLOOR
                or row["field_energy_denominator"] != max(energy, COMMON_FIELD_ENERGY_FLOOR)):
            raise ValueError("common field denominator differs")
        for key in ("frequency_reference_energy_fraction", "frequency_squared_error_contribution"):
            values = row[key]
            if len(values) != count // 2 + 1 or not all(math.isfinite(x) and x >= 0 for x in values):
                raise ValueError("finite nonnegative complete frequency inventory required")
        if (not math.isfinite(row["field_relative_l2"]) or row["field_relative_l2"] < 0
                or not math.isclose(sum(row["frequency_reference_energy_fraction"]), 1., rel_tol=1e-10)
                or not math.isclose(sum(row["frequency_squared_error_contribution"]),
                    row["field_relative_squared_error"], rel_tol=1e-10, abs_tol=1e-12)
                or not math.isclose(row["field_relative_l2"] ** 2,
                    row["field_relative_squared_error"], rel_tol=1e-10, abs_tol=1e-12)):
            raise ValueError("case-level energy accounting differs")
        for name, start, stop in (("dc", 0, 1), ("oscillatory", 1, count // 2 + 1)):
            band = row[name]
            ref = sum(row["frequency_reference_energy_fraction"][start:stop])
            err = sum(row["frequency_squared_error_contribution"][start:stop])
            support = ref > NUMERICAL_SUPPORT_FRACTION
            relative = band["band_relative_l2"]
            if (row["numerical_support_fraction"] != NUMERICAL_SUPPORT_FRACTION
                    or band["reference_support_resolved"] is not support
                    or not math.isclose(band["reference_energy_fraction"], ref, rel_tol=1e-10, abs_tol=1e-12)
                    or not math.isclose(band["squared_error_contribution"], err, rel_tol=1e-10, abs_tol=1e-12)
                    or (not support and relative is not None)
                    or (support and (relative is None or not math.isfinite(relative) or relative < 0
                        or not math.isclose(relative ** 2,
                            err * row["field_energy_denominator"] / energy / ref,
                            rel_tol=1e-10, abs_tol=1e-12)))):
                raise ValueError("band support or contribution differs from frequency inventory")
    summaries = {}
    for name in ("dc", "oscillatory"):
        supported = [row[name]["band_relative_l2"] for row in rows
                     if row[name]["reference_support_resolved"]]
        if any(x is None or not math.isfinite(x) or x < 0 for x in supported):
            raise ValueError("finite supported band errors required")
        summaries[name] = dict(
            case_mean_reference_energy_fraction=statistics.fmean(row[name]["reference_energy_fraction"] for row in rows),
            case_mean_squared_error_contribution=statistics.fmean(row[name]["squared_error_contribution"] for row in rows),
            band_relative_l2_supported_case_count=len(supported),
            supported_case_mean_band_relative_l2=statistics.fmean(supported) if supported else None)
    return dict(schema_version="aurora.cycle_error_spectrum_summary.v3", case_count=len(rows),
        phase_count=count, sample_unit="geometry case", uncertainty_estimated=False,
        case_mean_field_relative_l2=statistics.fmean(row["field_relative_l2"] for row in rows),
        case_mean_field_relative_squared_error=statistics.fmean(row["field_relative_squared_error"] for row in rows),
        frequency_indices=rows[0]["frequency_indices"],
        case_mean_frequency_squared_error_contribution=[statistics.fmean(
            row["frequency_squared_error_contribution"][k] for row in rows) for k in range(count // 2 + 1)],
        **summaries)

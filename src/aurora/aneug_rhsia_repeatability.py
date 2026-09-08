"""Separate native repeatability from geometry-cache effects without changing a model.

This is a numerical implementation audit, not an accuracy gate or a weaker
comparator. It never replaces attention, changes weights, or loosens a failed
componentwise comparison. All comparisons, including failures of that original
tolerance, are reported alongside native-native variation and state changes.
"""
from __future__ import annotations

import torch


def discrepancy(reference, value, *, atol=1e-5, rtol=1e-5):
    if reference.shape != value.shape or not reference.is_floating_point():
        raise ValueError("matching floating tensors required")
    if not bool(torch.isfinite(reference).all() and torch.isfinite(value).all()):
        raise ValueError("nonfinite numerical comparison")
    error = value.double() - reference.double()
    denominator = reference.double().norm().clamp_min(1e-30)
    return dict(elements=reference.numel(), max_abs=float(error.abs().max()),
                relative_l2=float(error.norm() / denominator),
                rms_abs=float(error.square().mean().sqrt()),
                original_componentwise_failures=int((~torch.isclose(reference, value, atol=atol, rtol=rtol)).sum()),
                original_atol=atol, original_rtol=rtol)


def _clone_tensors(mapping):
    return {key: value.detach().clone() for key, value in mapping.items()}


def _changed(before, after):
    if before.keys() != after.keys():
        return sorted(set(before) | set(after))
    return [key for key in before if not torch.equal(before[key], after[key])]


@torch.no_grad()
def audit_repeatability(model, features, waveform, *, period, output_scale,
                        phases=(0, 39, 79), repeats=3, log=lambda value: None):
    """Inspect the actual native methods, with no forward hooks/backend patch.

    The fixed-encoding path isolates decoder variation; two fresh encodings
    isolate encoder variation; the public full-cycle method tests the actual
    evaluation cache. A strict-deterministic probe reports unsupported ops
    instead of disabling the diagnostic or silently changing the algorithm.
    Its flags are restored even on failure. Fresh native calls remain the
    comparator, never reference CFD targets.
    """
    if model.training or repeats < 2 or not phases or any(type(p) is not int or not 0 <= p < model.phases for p in phases):
        raise ValueError("eval model, repeated calls and valid native phases required")
    device = features["batch"].device
    state_before = _clone_tensors(model.state_dict())
    features_before = _clone_tensors(features)
    wave_before = waveform.clone()
    rng_before = torch.get_rng_state().clone()
    cuda_rng_before = torch.cuda.get_rng_state_all() if device.type == "cuda" else []
    encoded = model._encode_geometry(features, 1)
    encoded_before = _clone_tensors(encoded)
    other_encoding = model._encode_geometry(features, 1)
    encoder = {key: discrepancy(encoded[key], other_encoding[key]) for key in ("x", "edges")}
    del other_encoding
    rows = []
    for phase in phases:
        phase_tensor = torch.tensor([phase], device=device)
        natives = [model.forward_snapshot(features, phase_tensor, waveform, period=period, output_scale=output_scale)
                   for _ in range(repeats)]
        fixed = [model._decode_snapshot(encoded, phase_tensor, waveform, period, output_scale)
                 for _ in range(repeats)]
        row = dict(phase=phase,
            native_native=[discrepancy(natives[0], value) for value in natives[1:]],
            fixed_decoder_repeat=[discrepancy(fixed[0], value) for value in fixed[1:]],
            fixed_encoded_native=[discrepancy(natives[0], value) for value in fixed],
            encoded_mutation_names=_changed(encoded_before, encoded))
        rows.append(row)
        log(dict(stage="rhsia_repeatability_phase", **row))
    cycle = model.forward_cycle(features, waveform, period=period, output_scale=output_scale)
    if tuple(cycle.shape) != (model.phases, len(features["batch"]), 3):
        raise RuntimeError("actual full-cycle shape differs")
    cached = []
    for phase in phases:
        native = model.forward_snapshot(features, torch.tensor([phase], device=device), waveform,
                                        period=period, output_scale=output_scale)
        cached.append(dict(phase=phase, **discrepancy(native, cycle[phase])))
    state_changes = _changed(state_before, model.state_dict())
    input_changes = _changed(features_before, features)
    rng_changed = not torch.equal(rng_before, torch.get_rng_state())
    if device.type == "cuda":
        rng_changed |= any(not torch.equal(x, y) for x, y in zip(cuda_rng_before, torch.cuda.get_rng_state_all()))
    original = dict(enabled=torch.are_deterministic_algorithms_enabled(),
                    warn_only=torch.is_deterministic_algorithms_warn_only_enabled())
    strict = dict(available=False)
    try:
        torch.use_deterministic_algorithms(True, warn_only=False)
        p = torch.tensor([phases[0]], device=device)
        first = model.forward_snapshot(features, p, waveform, period=period, output_scale=output_scale)
        second = model.forward_snapshot(features, p, waveform, period=period, output_scale=output_scale)
        strict = dict(available=True, native_native=discrepancy(first, second))
    except RuntimeError as error:
        # Preserve the exact unsupported numerical operation; do not relabel
        # its absence as equivalent outputs or a scientifically failed model.
        strict = dict(available=False, exception_type=type(error).__name__, message=str(error))
    finally:
        torch.use_deterministic_algorithms(original["enabled"], warn_only=original["warn_only"])
    report = dict(schema_version="aurora.rhsia_native_repeatability.v3", encoder_repeat=encoder,
        phase_comparisons=rows, actual_cycle_native=cached,
        parameter_or_buffer_mutations=state_changes, input_mutations=input_changes,
        waveform_mutated=not torch.equal(wave_before, waveform), default_eval_RNG_changed=rng_changed,
        strict_determinism=strict, original_determinism=original,
        final_parameter_or_buffer_mutations=_changed(state_before, model.state_dict()),
        original_componentwise_tolerance_unchanged=True,
        field_accuracy_measured=False, caching_equivalence_claim=False,
        result_requires_interpretation=True, reference_CFD_targets_used=False)
    log(dict(stage="rhsia_repeatability_complete", **report))
    return report

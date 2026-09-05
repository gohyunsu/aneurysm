"""Native snapshot computation with an explicit phase/steady exposure ledger.

The released dataset enumerates geometry x phase, not one sampled phase per
geometry. ``phases_per_geometry == phase_count`` retains that enumeration.
A smaller value is an explicitly labelled compute-budget adaptation, never a
source-equivalent epoch. The physical cycle-relative objective is also a task
adaptation, not the author's normalized MSE recipe. No split is selected here.
"""
from __future__ import annotations

import hashlib
import copy
import math
import random
import time
from pathlib import Path
from typing import NamedTuple

import torch

from aurora.aneug_release_730_ghd_gps_baseline import (
    _strict_atomic_json, _strict_atomic_torch_save, extended_case_metrics, file_sha256,
)
from aurora.aneug_release_730_matched_steady_stream import epoch_exposure_indices
from aurora.aneug_release_730_response_local_candidate import _valid_support_osi
from aurora.release730_training_continuation import capture_rng_state


class Snapshot(NamedTuple):
    regime: str
    index: int
    phase: int


def _rng(seed, *parts):
    digest = hashlib.sha256(":".join(map(str, (seed, *parts))).encode()).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def snapshot_epoch(train_cases, phases, phases_per_geometry, eligible_steady, *,
                   steady_samples, seed, epoch):
    """Shuffled native samples; T order and phase choices are paired across T/T+S.

    Each geometry traverses independent deterministic shuffled phase cycles.
    Subsampling therefore has balanced long-run coverage, not a permanently
    restricted phase subset. Steady rows use the existing audited cyclic pool.
    The returned indices are private runtime data, not a public manifest.
    """
    for value in (train_cases, phases, phases_per_geometry, epoch):
        if type(value) is not int or value < 1:
            raise ValueError("positive integer sample dimensions required")
    if phases < 3 or phases_per_geometry > phases or type(seed) is not int or seed < 0:
        raise ValueError("invalid phase count or seed")
    if type(steady_samples) is not int or steady_samples < 0:
        raise ValueError("nonnegative steady sample count required")
    transient = []
    start = (epoch - 1) * phases_per_geometry
    for index in range(train_cases):
        for cycle in range(start // phases, (start + phases_per_geometry - 1) // phases + 1):
            order = list(range(phases))
            _rng(seed, "phase", index, cycle).shuffle(order)
            left, right = max(0, start - cycle * phases), min(phases, start + phases_per_geometry - cycle * phases)
            transient.extend(Snapshot("T", index, p) for p in order[left:right])
    _rng(seed, "transient_order", epoch).shuffle(transient)
    if not steady_samples:
        return transient
    steady = [Snapshot("S", i, -1) for i in epoch_exposure_indices(
        eligible_steady, epoch=epoch - 1, cases_per_epoch=steady_samples, seed=seed)]
    positions = set(_rng(seed, "regime_interleave", epoch).sample(
        range(len(transient) + len(steady)), len(steady)))
    transient_iter, steady_iter = iter(transient), iter(steady)
    return [next(steady_iter) if i in positions else next(transient_iter)
            for i in range(len(transient) + len(steady))]


def reference_energy(reference, weights):
    if reference.ndim == 2:
        reference = reference[None]
    if (reference.ndim != 3 or reference.shape[-1] != 3
            or weights.shape != (reference.shape[1],)
            or not bool(torch.isfinite(reference).all() and torch.isfinite(weights).all())
            or not bool((weights > 0).all())):
        raise ValueError("finite vector reference and positive surface weights required")
    return (weights[None] * reference.square().sum(-1)).sum() / reference.shape[0]


def snapshot_loss(prediction, reference, weights, cycle_energy):
    """Averaging all T snapshots equals the existing physical cycle field loss.

    Normalize by FULL reference-cycle energy, not the sampled phase's energy.
    The analogous S denominator is its single-field reference energy.
    """
    if (prediction.shape != reference.shape or prediction.ndim != 2
            or prediction.shape[-1] != 3 or weights.shape != (len(prediction),)
            or not bool(torch.isfinite(prediction).all() and torch.isfinite(reference).all())
            or not bool(torch.isfinite(weights).all() and (weights > 0).all())
            or not math.isfinite(float(cycle_energy)) or float(cycle_energy) < 0):
        raise ValueError("invalid physical snapshot objective inputs")
    return (weights * (prediction - reference).square().sum(-1)).sum() / max(float(cycle_energy), 1e-12)


def validate_optimization(config, phases):
    for key in ("epochs", "phases_per_geometry", "accumulation_snapshots", "microbatch_graphs", "validation_interval",
                "checkpoint_interval", "step_size_epochs", "progress_interval_updates"):
        if type(config.get(key)) is not int or config[key] < 1:
            raise ValueError(f"positive integer required: {key}")
    for key in ("seed", "steady_samples_per_epoch"):
        if type(config.get(key)) is not int or config[key] < 0:
            raise ValueError(f"nonnegative integer required: {key}")
    for key in ("learning_rate", "gamma", "gradient_clip_norm", "steady_loss_weight"):
        if not math.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"positive finite value required: {key}")
    if (not math.isfinite(config["weight_decay"]) or config["weight_decay"] < 0
            or config["phases_per_geometry"] > phases or phases < 3
            or config["microbatch_graphs"] > config["accumulation_snapshots"]):
        raise ValueError("invalid weight decay or phase budget")


def collate_graphs(features, device):
    """Batch disconnected single-geometry meshes without inventing KNN edges."""
    if not features:
        raise ValueError("nonempty graph microbatch required")
    keys = set(features[0])
    if not {"edge_index", "batch"} <= keys or any(set(f) != keys for f in features):
        raise ValueError("consistent explicit graph feature keys required")
    pieces = {key: [] for key in keys}
    counts, offset = [], 0
    for i, feature in enumerate(features):
        nodes, edges = len(feature["batch"]), feature["edge_index"]
        if (nodes < 1 or feature["batch"].dtype != torch.long or feature["batch"].ndim != 1
                or bool((feature["batch"] != 0).any()) or edges.dtype != torch.long
                or edges.ndim != 2 or edges.shape[0] != 2 or not edges.numel()
                or bool((edges < 0).any() or (edges >= nodes).any())):
            raise ValueError("each sample must be a valid single graph")
        for key in keys - {"batch", "edge_index"}:
            if feature[key].ndim < 1 or len(feature[key]) != nodes:
                raise ValueError("node descriptor shape differs from graph")
            pieces[key].append(feature[key].to(device))
        pieces["batch"].append(torch.full((nodes,), i, dtype=torch.long, device=device))
        pieces["edge_index"].append(edges.to(device) + offset)
        counts.append(nodes)
        offset += nodes
    return {key: torch.cat(value, dim=1 if key == "edge_index" else 0) for key, value in pieces.items()}, counts


@torch.no_grad()
def evaluate_snapshots(model, cases, features_for, waveform, *, period, output_scale,
                       reference_tawss_floor, device):
    """All phases, exact same physical metric functions as the cycle trainer."""
    if not cases or not math.isfinite(reference_tawss_floor) or reference_tawss_floor <= 0:
        raise ValueError("nonempty validation and positive train-only OSI floor required")
    model.eval()
    rows = []
    for index, case in enumerate(cases):
        features = {k: v.to(device) for k, v in features_for(index, case).items()}
        prediction = model.forward_cycle(features, waveform, period=period, output_scale=output_scale)
        reference, weights, normals = (case[k].to(device) for k in ("wss", "vertex_weights", "normals"))
        if prediction.shape != reference.shape or not bool(torch.isfinite(prediction).all()):
            raise RuntimeError("nonfinite or incompatible full-cycle prediction")
        row = extended_case_metrics(prediction, reference, weights, normals)
        row["osi_mae"], row["osi_coverage"] = _valid_support_osi(
            prediction, reference, weights, reference_tawss_floor)
        rows.append(row)
    return {"case_count": len(rows), "per_case_without_identifiers": rows,
            "aggregate": {key: sum(row[key] for row in rows) / len(rows) for key in rows[0]}}


def _restore(path, expected_hash, model, optimizer, scheduler, config, contract, device):
    if file_sha256(path) != expected_hash:
        raise ValueError("snapshot continuation checkpoint hash mismatch")
    state = torch.load(path, map_location="cpu", weights_only=True)
    old = state.get("optimization", {})
    if (state.get("schema_version") != "aurora.private.rhsia_snapshot_checkpoint.v3"
            or state.get("contract") != contract
            or {k: v for k, v in old.items() if k != "epochs"}
            != {k: v for k, v in config.items() if k != "epochs"}):
        raise ValueError("snapshot continuation scientific contract differs")
    completed = state["completed_epoch"]
    if not 0 < completed < config["epochs"] or completed > old["epochs"]:
        raise ValueError("snapshot continuation epoch range")
    if [r["epoch"] for r in state["history"]] != list(range(1, completed + 1)):
        raise ValueError("snapshot continuation history incomplete")
    n, k, s = contract["train_cases"], config["phases_per_geometry"], config["steady_samples_per_epoch"]
    expected = (completed * n * k, completed * s,
                completed * math.ceil((n * k + s) / config["accumulation_snapshots"]))
    ledger = state["ledger"]
    if tuple(ledger[key] for key in ("training_phase_field_exposures", "steady_exposures", "optimizer_updates")) != expected:
        raise ValueError("snapshot continuation exposure ledger differs")
    total, accumulation, micro = n * k + s, config["accumulation_snapshots"], config["microbatch_graphs"]
    forwards_per_epoch = (total // accumulation) * math.ceil(accumulation / micro) + math.ceil((total % accumulation) / micro)
    if ledger["training_model_forward_calls"] != completed * forwards_per_epoch:
        raise ValueError("snapshot continuation graph forward ledger differs")
    if (len(ledger["phase_histogram"]) != contract["phases"]
            or sum(ledger["phase_histogram"]) != expected[0]
            or not set(state["steady_seen_indices"]) <= set(contract["eligible_steady_indices"])):
        raise ValueError("snapshot continuation phase or steady coverage differs")
    model.load_state_dict(state["model_state_dict"], strict=True)
    optimizer.load_state_dict(state["optimizer_state_dict"])
    scheduler.load_state_dict(state["scheduler_state_dict"])
    rng = state["rng_state"]
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    if device.type == "cuda":
        if not rng["cuda_rng_state_all"]:
            raise ValueError("CUDA continuation RNG absent")
        torch.cuda.set_rng_state_all(rng["cuda_rng_state_all"])
    elif rng["cuda_rng_state_all"]:
        raise ValueError("CUDA-to-CPU continuation is not exact")
    return state


def train_snapshots(model, train, validation, *, train_features, validation_features,
                    waveform, period, output_scale, optimization, reference_tawss_floor,
                    output_directory, provenance, device, steady_stream=None,
                    eligible_steady=(), steady_features=None, continuation=None, log=print):
    """Real disconnected-graph batching, mixed T/S accumulation, cycle evaluation.

    Microbatch-1 accumulation is NOT author's batch-10 normalization. A real
    graph batch of ten is supported separately. Initialization is seeded before
    construction. Static descriptor providers may cache deterministic geometry;
    learned encodings are freshly computed at every training snapshot.
    """
    if not train or not validation:
        raise ValueError("admitted nonempty train/validation required")
    phases = int(train[0]["wss"].shape[0])
    validate_optimization(optimization, phases)
    if getattr(model, "phases", phases) != phases:
        raise ValueError("model and reference phase counts differ")
    if any(case["wss"].shape[0] != phases for case in (*train, *validation)):
        raise ValueError("inconsistent full-cycle phase count")
    for value in (period, output_scale, reference_tawss_floor):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("positive finite period and train-only scales required")
    has_steady = optimization["steady_samples_per_epoch"] > 0
    eligible = tuple(eligible_steady)
    if has_steady != (steady_stream is not None and steady_features is not None and bool(eligible)):
        raise ValueError("steady sampling requires an admitted stream and geometry provider")
    if not has_steady and (steady_stream is not None or steady_features is not None or eligible):
        raise ValueError("transient-only run must not receive a steady field stream")
    if len(set(eligible)) != len(eligible) or any(type(i) is not int or i < 0 for i in eligible):
        raise ValueError("unique nonnegative eligible steady indices required")
    # CPU energy scalars; do not send all 80 reference phases for one training snapshot.
    energies = [float(reference_energy(case["wss"], case["vertex_weights"])) for case in train]
    contract = dict(provenance=dict(provenance), train_cases=len(train), validation_cases=len(validation),
                    phases=phases, eligible_steady_indices=list(eligible), period=period,
                    output_scale=output_scale, reference_tawss_floor=reference_tawss_floor,
                    model_shapes={k: list(v.shape) for k, v in model.state_dict().items()})
    output_directory = Path(output_directory)
    if output_directory.exists():
        raise FileExistsError(output_directory)
    model.to(device)
    waveform = waveform.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=optimization["learning_rate"], weight_decay=optimization["weight_decay"])
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=optimization["step_size_epochs"], gamma=optimization["gamma"])
    history, artifacts, seen = [], [], set()
    ledger = dict(training_phase_field_exposures=0, steady_exposures=0, optimizer_updates=0,
                  training_model_forward_calls=0, validation_cycle_forwards=0, phase_histogram=[0] * phases)
    best_value, best_epoch, best_state, best_validation = math.inf, 0, None, None
    completed, previous_seconds, previous_peak = 0, 0.0, 0
    receipt = None
    if continuation is not None:
        state = _restore(Path(continuation["checkpoint"]), continuation["sha256"], model, optimizer,
                         scheduler, optimization, contract, device)
        completed, history, ledger = state["completed_epoch"], state["history"], state["ledger"]
        best_value, best_epoch = state["best_value"], state["best_epoch"]
        best_state, best_validation = state["best_state_dict"], state["best_validation"]
        seen = set(state["steady_seen_indices"])
        previous_seconds, previous_peak = state["elapsed_seconds"], state["peak_cuda_allocated_bytes"]
        receipt = dict(checkpoint_sha256=continuation["sha256"], completed_epoch=completed,
                       parent_ledger=copy.deepcopy(ledger), same_seed_continuation=True)
    output_directory.mkdir(parents=True)
    for row in history:
        _strict_atomic_json(output_directory / "epochs" / f"epoch_{row['epoch']:03d}.json", row)
    if receipt is not None:
        _strict_atomic_json(output_directory / "continuation.json", receipt)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    started = time.monotonic()
    for epoch in range(completed + 1, optimization["epochs"] + 1):
        model.train()
        samples = snapshot_epoch(len(train), phases, optimization["phases_per_geometry"], eligible,
            steady_samples=optimization["steady_samples_per_epoch"], seed=optimization["seed"], epoch=epoch)
        loss_sums, connected = {"T": 0.0, "S": 0.0}, set()
        counts = {"T": 0, "S": 0}
        tick = time.monotonic()
        for offset in range(0, len(samples), optimization["accumulation_snapshots"]):
            batch = samples[offset:offset + optimization["accumulation_snapshots"]]
            optimizer.zero_grad(set_to_none=True)
            for micro_offset in range(0, len(batch), optimization["microbatch_graphs"]):
                micro = batch[micro_offset:micro_offset + optimization["microbatch_graphs"]]
                feature_list, labels = [], []
                for sample in micro:
                    if sample.regime == "T":
                        case = train[sample.index]
                        feature_list.append(train_features(sample.index, case))
                        reference, energy = case["wss"][sample.phase], energies[sample.index]
                    else:
                        case = steady_stream.decode(sample.index)
                        feature_list.append(steady_features(sample.index, case))
                        reference = case["steady_wss"]
                        energy = float(reference_energy(reference, case["vertex_weights"]))
                    labels.append((reference.to(device), case["vertex_weights"].to(device), energy))
                features, sizes = collate_graphs(feature_list, device)
                prediction = model.forward_snapshot(features, torch.tensor([s.phase for s in micro], device=device),
                    waveform, period=period, output_scale=output_scale)
                if prediction.shape != (sum(sizes), 3):
                    raise RuntimeError("batched snapshot shape differs")
                losses = []
                for sample, predicted, (reference, weights, energy) in zip(micro, prediction.split(sizes), labels):
                    loss = snapshot_loss(predicted, reference, weights, energy)
                    if not bool(torch.isfinite(loss)):
                        raise RuntimeError("nonfinite snapshot loss")
                    multiplier = optimization["steady_loss_weight"] if sample.regime == "S" else 1.0
                    losses.append(loss * multiplier / len(batch))
                    loss_sums[sample.regime] += float(loss.detach())
                    counts[sample.regime] += 1
                    if sample.regime == "T":
                        ledger["training_phase_field_exposures"] += 1
                        ledger["phase_histogram"][sample.phase] += 1
                    else:
                        ledger["steady_exposures"] += 1
                        seen.add(sample.index)
                torch.stack(losses).sum().backward()
                ledger["training_model_forward_calls"] += 1
            # An all-steady microbatch correctly has no temporal gradients.
            connected.update(name for name, p in model.named_parameters() if p.grad is not None)
            torch.nn.utils.clip_grad_norm_(model.parameters(), optimization["gradient_clip_norm"], error_if_nonfinite=True)
            optimizer.step()
            ledger["optimizer_updates"] += 1
            if offset == 0 or ledger["optimizer_updates"] % optimization["progress_interval_updates"] == 0:
                log(dict(stage="rhsia_snapshot_progress", epoch=epoch, epoch_transient_snapshots=counts["T"],
                         epoch_steady_snapshots=counts["S"], optimizer_updates=ledger["optimizer_updates"]))
        missing = [name for name, p in model.named_parameters() if p.requires_grad and name not in connected]
        if missing:
            raise RuntimeError(f"disconnected parameters across complete mixed epoch: {missing}")
        scheduler.step()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        row = dict(epoch=epoch, transient_relative_squared_error=loss_sums["T"] / counts["T"],
                   steady_relative_squared_error=loss_sums["S"] / counts["S"] if counts["S"] else None,
                   training_epoch_seconds=time.monotonic() - tick,
                   learning_rate_next_epoch=scheduler.get_last_lr()[0],
                   training_phase_field_exposures=ledger["training_phase_field_exposures"],
                   steady_exposures=ledger["steady_exposures"], optimizer_updates=ledger["optimizer_updates"])
        if epoch % optimization["validation_interval"] == 0 or epoch == optimization["epochs"]:
            tick = time.monotonic()
            evaluation = evaluate_snapshots(model, validation, validation_features, waveform,
                period=period, output_scale=output_scale, reference_tawss_floor=reference_tawss_floor, device=device)
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            ledger["validation_cycle_forwards"] += len(validation)
            row["validation"], row["validation_seconds"] = evaluation["aggregate"], time.monotonic() - tick
            value = evaluation["aggregate"]["field_relative_l2"]
            if not math.isfinite(value):
                raise RuntimeError("nonfinite validation selection metric")
            if value < best_value:
                best_value, best_epoch, best_validation = value, epoch, evaluation
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        history.append(row)
        _strict_atomic_json(output_directory / "epochs" / f"epoch_{epoch:03d}.json", row)
        log(dict(stage="rhsia_snapshot_epoch", **row))
        if epoch == 1 or epoch % optimization["checkpoint_interval"] == 0 or epoch == optimization["epochs"]:
            path = output_directory / "checkpoints" / f"epoch_{epoch:03d}.pt"
            _strict_atomic_torch_save(path, dict(schema_version="aurora.private.rhsia_snapshot_checkpoint.v3",
                completed_epoch=epoch, contract=contract, optimization=dict(optimization), history=history,
                ledger=ledger, steady_seen_indices=sorted(seen), best_value=best_value, best_epoch=best_epoch,
                best_state_dict=best_state, best_validation=best_validation,
                model_state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
                optimizer_state_dict=optimizer.state_dict(), scheduler_state_dict=scheduler.state_dict(),
                rng_state=capture_rng_state(), elapsed_seconds=previous_seconds + time.monotonic() - started,
                peak_cuda_allocated_bytes=max(previous_peak, torch.cuda.max_memory_allocated(device) if device.type == "cuda" else 0)))
            artifacts.append(dict(file=str(path.relative_to(output_directory)), sha256=file_sha256(path), bytes=path.stat().st_size))
    if best_state is None:
        raise RuntimeError("no full-cycle validation checkpoint selected")
    selected = output_directory / "selected.pt"
    _strict_atomic_torch_save(selected, dict(model_state_dict=best_state, epoch=best_epoch, contract=contract))
    result = dict(schema_version="aurora.private.rhsia_snapshot_result.v3",
        status="completed_validation_development", provenance=dict(provenance), optimization=dict(optimization),
        train_cases=len(train), validation_cases=len(validation), phase_count=phases,
        sampling_identity="full_geometry_phase_enumeration" if optimization["phases_per_geometry"] == phases else "balanced_phase_subsampling_adaptation",
        objective_identity="physical_cycle_relative_squared_error_not_author_normalized_MSE",
        microbatch_graphs=optimization["microbatch_graphs"],
        batch_identity="graph_batch10" if optimization["microbatch_graphs"] == optimization["accumulation_snapshots"] == 10 else "explicit_graph_microbatch_gradient_accumulation",
        **ledger, training_complete_cycle_forwards=0,
        training_cycle_equivalent_phase_exposures=ledger["training_phase_field_exposures"] / phases,
        training_geometry_graph_encodings=ledger["training_phase_field_exposures"] + ledger["steady_exposures"],
        training_geometry_encoder_forward_calls=ledger["training_model_forward_calls"],
        validation_geometry_encoder_forwards=ledger["validation_cycle_forwards"],
        validation_conditioned_graph_forwards=ledger["validation_cycle_forwards"] * phases,
        unique_transient_geometries=len(train), unique_steady_geometries=len(seen),
        selected_epoch=best_epoch, checkpoint_selection="lowest_validation_field_rL2_then_earliest",
        selected_validation=best_validation, reference_tawss_floor=reference_tawss_floor,
        parameter_count=sum(p.numel() for p in model.parameters()), checkpoints=artifacts,
        selected_checkpoint_sha256=file_sha256(selected), raw_predictions_stored=0,
        elapsed_training_and_validation_seconds=previous_seconds + time.monotonic() - started,
        peak_cuda_allocated_bytes=max(previous_peak, torch.cuda.max_memory_allocated(device) if device.type == "cuda" else 0),
        timing_includes_feature_assembly_and_transfer=True,
        device=str(device), device_name=torch.cuda.get_device_name(device) if device.type == "cuda" else "CPU",
        independent_confirmatory_evaluation=False, result_is_architectural_novelty_evidence_by_itself=False)
    if receipt is not None:
        result["continuation"] = receipt
    _strict_atomic_json(output_directory / "result.json", result)
    return result

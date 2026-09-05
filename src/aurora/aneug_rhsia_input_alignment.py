"""Geometry-only reconciliation of released RHSIA descriptors.

Returned row/case mappings are PRIVATE evidence. This module never reads WSS,
fits a normalizer, selects a split, or calls methods on a serialized Meshes.
GHD matching uses the released constructor's deformation-coefficient equation,
not the misleading ``lambda`` variable name as an eigenvalue interpretation.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

import torch


def coefficient_rows(ghd, mean, std, modes=8):
    if ghd.ndim != 2 or ghd.shape[1] % 3:
        raise ValueError("GHD matrix shape")
    shape = (1, -1, 3)
    x = ghd.reshape(len(ghd), -1, 3)[:, :modes]
    mu, sigma = mean.reshape(shape)[:, :modes], std.reshape(shape)[:, :modes]
    if x.shape[1:] != (modes, 3) or mu.shape != (1, modes, 3) or sigma.shape != (1, modes, 3):
        raise ValueError("GHD normalizer shape")
    if not all(bool(torch.isfinite(v).all()) for v in (x, mu, sigma)):
        raise ValueError("nonfinite GHD metadata")
    # Preserve the upstream operation order/dtype before comparison conversion.
    return (x * sigma + mu).reshape(len(x), -1).float().cpu()


def align_rows(expected, released, *, rtol=1e-5, atol=1e-7):
    """Map source rows to descriptor rows; never resolve ambiguous IDs by order.

    Exact float32 matches are preferred. Only unmatched rows use bounded-memory
    elementwise tolerance checks, with every candidate retained. No nearest-
    neighbor tie breaking or performance-dependent matching tolerance exists.
    """
    expected, released = expected.float().cpu(), released.float().cpu()
    if expected.ndim != 2 or expected.shape != released.shape:
        raise ValueError("coefficient cohort shape mismatch")
    if not bool(torch.isfinite(expected).all() and torch.isfinite(released).all()):
        raise ValueError("nonfinite coefficients")
    lookup = defaultdict(list)
    for index, row in enumerate(released):
        lookup[row.contiguous().numpy().tobytes()].append(index)
    matches, exact_count, tolerant_count = [], 0, 0
    for row in expected:
        candidates = lookup.get(row.contiguous().numpy().tobytes(), [])
        if candidates:
            exact_count += 1
        else:
            candidates = torch.where(torch.isclose(released, row, rtol=rtol, atol=atol).all(1))[0].tolist()
            tolerant_count += bool(candidates)
        matches.append(candidates)
    mapping = [c[0] if len(c) == 1 else None for c in matches]
    unique = all(v is not None for v in mapping) and len(set(mapping)) == len(mapping)
    return {
        "unique_bijection": unique, "source_to_encoder_row": mapping,
        "candidate_rows": matches, "exact_source_rows": exact_count,
        "tolerance_source_rows": tolerant_count,
        "unmatched_source_rows": sum(not c for c in matches),
        "ambiguous_source_rows": sum(len(c) > 1 for c in matches),
        "positional_max_abs_error": float((expected - released).abs().max()),
        "rtol": rtol, "atol": atol,
    }


def boundary_components(faces, nodes):
    """Canonical-mesh opening components, with NO inlet/outlet semantics."""
    faces = faces.long().cpu()
    if faces.ndim != 2 or faces.shape[1] != 3 or not faces.numel():
        raise ValueError("triangle faces required")
    if int(faces.min()) < 0 or int(faces.max()) >= nodes:
        raise ValueError("face index range")
    if bool((faces.sort(1).values.diff(dim=1) == 0).any()):
        raise ValueError("repeated triangle vertex")
    edges = torch.cat((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    edges, counts = torch.unique(edges.sort(1).values, dim=0, return_counts=True)
    if bool((counts > 2).any()):
        raise ValueError("nonmanifold edge")
    adjacency = defaultdict(set)
    for a, b in edges[counts == 1].tolist():
        adjacency[a].add(b)
        adjacency[b].add(a)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("boundary is not a union of closed loops")
    remaining, components = set(adjacency), []
    while remaining:
        stack, component = [min(remaining)], set()
        while stack:
            node = stack.pop()
            if node not in component:
                component.add(node)
                stack.extend(adjacency[node] - component)
        remaining -= component
        components.append(sorted(component))
    return {
        "components": components, "component_sizes": [len(c) for c in components],
        "boundary_nodes": len(adjacency), "interior_nodes": nodes - len(adjacency),
        "semantic_inlet_outlet_labels_available": False,
        "ordering": "minimum registered vertex index; anonymous opening IDs only",
    }


def audit_loaded_inputs(encoder: Mapping[str, Any], transient: Mapping[str, Any],
                        steady: Mapping[str, Any], development_case_ids: Sequence[str],
                        *, progress=lambda _: None):
    mesh = transient["mesh_data"]
    records = transient["registered_data_list"]
    case_ids = [str(r["case"]) for r in records]  # metadata only
    mesh_ids = [str(v) for v in mesh["cases"]]
    if len(set(case_ids)) != len(case_ids) or len(set(mesh_ids)) != len(mesh_ids):
        raise ValueError("duplicate transient IDs")
    if set(case_ids) != set(mesh_ids):
        raise ValueError("transient mesh/record membership differs")
    admitted = list(development_case_ids)
    if len(set(admitted)) != len(admitted) or not set(admitted) <= set(case_ids):
        raise ValueError("invalid development case admission")
    t_expected = coefficient_rows(mesh["ghd"], mesh["ghd_mean"], mesh["ghd_std"])
    s_meta = steady["ghd_dict"]
    s_expected = coefficient_rows(s_meta["ghd"], s_meta["mean_ghd"], s_meta["std_ghd"])
    t_match = align_rows(t_expected, encoder["ghd_lambda"].reshape(len(t_expected), -1))
    s_match = align_rows(s_expected, encoder["ghd_lambda_steady"].reshape(len(s_expected), -1))
    nodes = int(encoder["ghd_eigvec"].shape[0])
    shapes = {"ghd_eigvec": (nodes, 8), "cot_eigvec": (len(case_ids), nodes, 16),
              "cot_lambda": (len(case_ids), 16, 1),
              "cot_eigvec_steady": (len(s_expected), nodes, 16),
              "cot_lambda_steady": (len(s_expected), 16, 1)}
    for key, expected in shapes.items():
        if tuple(encoder[key].shape) != expected:
            raise ValueError(f"descriptor shape: {key}")
    # Full geometry-descriptor integrity, including metadata rows excluded from
    # model fitting. No aggregate statistic from these rows becomes a normalizer.
    nonfinite = {}
    for key in shapes:
        value, bad = encoder[key], 0
        for chunk in value.split(16, dim=0):
            bad += int((~torch.isfinite(chunk)).sum())
        nonfinite[key] = bad
        progress({"stage": "spectral_finiteness", "key": key, "nonfinite": bad})
    hierarchy_equal = {}
    for key in ("faces_list", "edge_index_list", "idx_list"):
        a, b = encoder[key], mesh[key]
        hierarchy_equal[key] = len(a) == len(b) and all(torch.equal(x.cpu(), y.cpu()) for x, y in zip(a, b))
    hierarchy_equal["ds_factors"] = list(encoder["ds_factors"]) == list(mesh["ds_factors"])
    opening = boundary_components(encoder["faces_list"][0], nodes)
    # Read fields only by explicitly selecting xyz; never materialize a [N,9]
    # row, call .clone() on a whole record, or inspect held-out geometry here.
    mesh_state = vars(encoder["meshes"])
    padded = mesh_state.get("_verts_padded")
    listed = mesh_state.get("_verts_list")
    by_id, mesh_row = dict(zip(case_ids, records)), dict(zip(mesh_ids, range(len(mesh_ids))))
    geometry_checks = []
    if t_match["unique_bijection"]:
        for index, case_id in enumerate(admitted):
            row = t_match["source_to_encoder_row"][mesh_row[case_id]]
            record = by_id[case_id]
            xyz = [list(record["labels"]).index(name) for name in ("x", "y", "z")]
            original = record["tensor"][0, :, xyz].float().cpu()
            cached = (padded[row] if padded is not None else listed[row]).float().cpu()
            if original.shape != (nodes, 3) or cached.shape != (nodes, 3):
                raise ValueError("geometry coordinate shape")
            finite = bool(torch.isfinite(original).all() and torch.isfinite(cached).all())
            geometry_checks.append({"case_id": case_id, "encoder_row": row,
                "finite": finite, "bit_exact": finite and torch.equal(original, cached),
                "within_float_tolerance": finite and torch.allclose(original, cached, rtol=1e-5, atol=1e-7),
                "max_abs_error": float((original - cached).abs().max()) if finite else None})
            if (index + 1) % 50 == 0:
                progress({"stage": "development_geometry_checked", "cases": index + 1})
    geometry_ok = len(geometry_checks) == len(admitted) and all(c["within_float_tolerance"] for c in geometry_checks)
    return {
        "schema_version": "aurora.rhsia_input_alignment.v3",
        "coefficient_row_alignment_verified": t_match["unique_bijection"] and s_match["unique_bijection"],
        "development_geometry_alignment_verified": geometry_ok,
        "source_transient_case_order_matches_mesh": case_ids == mesh_ids,
        "transient": t_match, "steady": s_match,
        "transient_case_ids_in_mesh_order": mesh_ids,
        "steady_case_ids_in_source_order": [str(v) for v in steady["case_name"]],
        "spectral_nonfinite_counts": nonfinite, "hierarchy_equal": hierarchy_equal,
        "boundary": opening, "development_geometry": geometry_checks,
        "geometry_rows_checked": len(geometry_checks), "wss_field_values_read": 0,
        "learned_statistics_fitted": False, "new_test_or_extra_record_tensors_read": 0,
        "steady_cotangent_eigenpair_geometry_consistency_verified": False,
        "note": "Row/mesh identity and finiteness do not independently validate the cached Laplacian operator or eigenpair residuals.",
    }

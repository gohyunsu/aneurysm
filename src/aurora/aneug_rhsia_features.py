"""Admitted geometry-to-RHSIA input assembly; no archive or WSS access.

Coordinates/normals follow the common development reader. Cached eigenmodes
are scalar features on the registered vertices; this does not recertify their
Laplacian under the common reader's coordinate transformation. Deformation
coefficients retain their released meaning rather than being called eigenvalues.
"""
from __future__ import annotations

import torch
from torch.nn import functional as F

from aurora.aneug_rhsia_graph_transformer import surface_scalar_gradients
from aurora.aneug_rhsia_input_alignment import boundary_components


def canonical_opening_types(faces: torch.Tensor, nodes: int):
    """0=interior, 1..K=anonymous loops in the registered template's order.

    Compute once on the common connectivity and permute labels with vertices.
    These are neither patient IDs nor anatomical inlet/outlet classifications.
    """
    boundary = boundary_components(faces, nodes)
    labels = torch.zeros(nodes, dtype=torch.long, device=faces.device)
    for index, component in enumerate(boundary["components"], 1):
        labels[torch.tensor(component, device=faces.device)] = index
    return labels, len(boundary["components"]) + 1


@torch.no_grad()
def single_graph_features(*, coordinates, normals, faces, edge_index, node_types,
                          node_type_count, ghd_modes, ghd_coefficients,
                          cotangent_modes, cotangent_eigenvalues):
    """Build the actual node/mode tensors consumed by RHSIAGraphTransformer.

    All arrays must already belong to the same admitted geometry; the private
    reader joins them through the completed row-alignment evidence. This pure
    assembler cannot select a case, read a target, or fit held-out statistics.
    No additional normalization or clipping is silently introduced.
    """
    nodes = len(coordinates)
    if (coordinates.shape != (nodes, 3) or normals.shape != (nodes, 3)
            or ghd_modes.shape != (nodes, 8) or ghd_coefficients.shape != (8, 3)
            or cotangent_modes.shape != (nodes, 16)
            or cotangent_eigenvalues.shape not in ((16,), (16, 1))):
        raise ValueError("RHSIA geometry/descriptor shapes")
    if (type(node_type_count) is not int or node_type_count < 1
            or node_types.dtype != torch.long or node_types.shape != (nodes,)
            or bool((node_types < 0).any() or (node_types >= node_type_count).any())):
        raise ValueError("RHSIA explicit node types")
    if (edge_index.dtype != torch.long or edge_index.ndim != 2 or edge_index.shape[0] != 2
            or edge_index.numel() == 0
            or bool((edge_index < 0).any() or (edge_index >= nodes).any())):
        raise ValueError("RHSIA mesh edges")
    values = (coordinates, normals, ghd_modes, ghd_coefficients,
              cotangent_modes, cotangent_eigenvalues)
    if not all(x.is_floating_point() and bool(torch.isfinite(x).all()) for x in values):
        raise ValueError("RHSIA nonfinite or nonfloating geometry input")
    device, dtype = coordinates.device, coordinates.dtype
    if not all(x.device == device for x in (*values, faces, edge_index, node_types)):
        raise ValueError("RHSIA geometry device mismatch")
    normals, ghd_modes, ghd_coefficients, cotangent_modes, cotangent_eigenvalues = (
        x.to(dtype=dtype) for x in values[1:])
    ghd_gradient = surface_scalar_gradients(coordinates, faces, ghd_modes)
    cot_gradient = surface_scalar_gradients(coordinates, faces, cotangent_modes)
    ghd = torch.cat((ghd_modes[..., None], ghd_gradient,
                     ghd_coefficients[None].expand(nodes, -1, -1)), -1)
    cot = torch.cat((cotangent_modes[..., None], cot_gradient,
                     cotangent_eigenvalues.reshape(1, 16, 1).expand(nodes, -1, -1)), -1)
    return {
        "node_features": torch.cat((coordinates, normals, F.one_hot(node_types, node_type_count).to(dtype)), -1),
        "ghd_descriptors": ghd.contiguous(), "cot_descriptors": cot.contiguous(),
        "edge_index": edge_index, "batch": torch.zeros(nodes, dtype=torch.long, device=device),
    }


def resample_repeated_waveform(values: torch.Tensor, *, cycles=5, samples=1000):
    """Released CFD signal -> one cycle using an explicitly declared index grid.

    The released signal has five bit-identical segments and one trailing value.
    The trailing value is not included in the cycle. Linear index resampling
    is an input convention, not verification of physical phase timestamps or
    identity with the differently named waveform in author training code.
    """
    if (values.ndim != 1 or not values.is_floating_point()
            or not bool(torch.isfinite(values).all())
            or type(cycles) is not int or cycles < 1
            or type(samples) is not int or samples < 8):
        raise ValueError("finite repeated waveform and sample dimensions required")
    count, remainder = divmod(values.numel(), cycles)
    if count < 8 or remainder not in (0, 1):
        raise ValueError("waveform cannot be partitioned into repeated segments")
    first = values[:count]
    if any(not torch.equal(first, values[i * count:(i + 1) * count]) for i in range(1, cycles)):
        raise ValueError("waveform segments differ; do not invent a shared cycle")
    return F.interpolate(first[None, None], size=samples, mode="linear", align_corners=True)[0, 0]

# Sheng/RHSIA direct comparator: implementation identity

Native snapshot/masked-joint training is now implemented separately; see
[the training recipe and exposure ledger](aneug-rhsia-snapshot-training-v3.md).
It supports genuine graph batches as well as explicitly labelled accumulation,
with common physical rather than author-normalized-MSE optimization. Actual
full-size GPU timing and sufficiently trained baseline results remain pending.

An opt-in [separate conditioning normalization control](aneug-rhsia-conditioning-v3.md)
is a declared optimization adaptation. The default remains unchanged, and
equal state-dict shapes do not make the two conditioning recipes equivalent.

Full-cycle evaluation reuses the unchanged geometry encoding within one call,
then evaluates all 80 native phase-conditioned GPS passes. The cache is local,
evaluation-only and never survives an optimizer update. Regression tests compare
every phase with ordinary snapshot calls. This preserves model outputs; it is
not a one-shot sequence architecture or an independently measured speedup.
Report one spectral encoder pass and 80 conditioned graph passes per cycle.

`aneug_rhsia_graph_transformer.py` is a publication-aligned reimplementation
of the direct [Sheng et al. prior](https://arxiv.org/html/2601.19876v2), not a
proposed architecture and not a byte-exact author training reproduction.

The model uses actual PyG 2.5.3 GPSConv, GINE and Performer attention, with
the source-sized defaults of 64 hidden channels and eight graph blocks. It
retains per-node GHD8/cotangent16 mode descriptions, surface gradients and
boundary type inputs, and injects time/waveform conditioning at every block.
Steady samples use phase -1 and zero features after temporal biases, through
bias-free injections. Phase 79 is a valid sample, not a missing-time mask.
The output is one physical WSS snapshot using a supplied train-only scale.

## Explicit source/paper differences

- The released `ghd_lambda` arrays are deformation xyz coefficients, not
  eigenvalues. Our seven-channel GHD tokens contain mode value, surface
  gradient and those three coefficients. Five-channel cotangent tokens contain
  mode value, surface gradient and eigenvalue. Do not claim that the missing
  canonical Laplacian eigenvalues have been recovered.
- The paper specifies waveform 1-D U-Net conditioning; the released class
  is three strided convolutions. Our explicit U-Net recipe uses flow and first
  and second derivatives with caller-specified period. Hyperparameters are
  part of the reimplementation and need reasonable baseline optimization.
- Unlike the inspected released encoder's first-node broadcast, the spectral
  Transformer operates on the modes at every node. This follows the stated
  positional role and avoids silently discarding almost all local descriptors.
- Spectral sign augmentation, normalization and boundary labels are the
  caller's responsibility. Do not pass GHD xyz coefficients as invariant
  scalars and claim E(3) equivariance for the whole pipeline.

## Actual assets, not fabricated substitutes

The immutable [processed directory](https://huggingface.co/datasets/whding123/AneuG-Flow/tree/9dd418083899deddd93a67f9a6fca7a14304fa36/processed_data)
contains `graph_encoder_cot16_ghd_8_dual_v5.pth` (13,664,498,427 bytes).
The same release includes `cfd/waveform.txt` (7,984,221 bytes). These may
restore much of the missing input path without downloading raw CFD. Exact
hashes, case correspondence and runtime evidence stay private. The different
filename `waveform_yiying.txt` in author training code still requires explicit
reconciliation; do not assert byte identity merely because both are waveforms.

Node-wise spectral encoding is chunked and activation-checkpointed so the
source-sized feedforward layers need not retain every vertex/mode activation
at once. This changes memory/recomputation cost, not the learned equations.
Value and gradient equivalence are tested with deterministic dropout disabled.

Ten synthetic tests exercise real forward/backward connections, area-weighted
surface gradients, node permutation, per-node spectral locality, phase79,
post-bias steady masking and rejection of cross-graph edges. These tests do
not establish dataset correspondence, convergence or scientific performance.

## Remaining scientific integration

`aneug_rhsia_features.py` now assembles the model's actual geometry tensors:
coordinates/normals, anonymous opening one-hots, GHD8 mode/gradient/deformation
tokens and cotangent16 mode/gradient/eigenvalue tokens. The caller must use the
private audited row mapping. No WSS value or statistical fit is accepted by the
assembler. Opening identities follow the common registered template, not
inferred anatomical inlet/outlet semantics. Gradients are computed in the common
reader's per-case centered/RMS-scaled coordinates; cached mode values are retained.
This is a declared common-input adaptation, not recertification of a Laplacian
after coordinate transformation or the paper's dataset-wide coordinate recipe.

The waveform helper takes one of the verified identical five segments, excludes
the optional trailing value and linearly resamples on an explicit index grid.
The caller supplies the period convention. Neither the helper nor its tests
establish physical phase timestamps or identity with `waveform_yiying.txt`.
Four synthetic tests check exact channel meanings, permutation and malformed
inputs. Admitted-data memory/forward/backward and snapshot ledgers remain next.

Provide admitted geometry/boundary/spectral features and recover or document
the waveform sampling convention. Use native snapshot-aware training with
phase-field, encoder-forward and optimizer-update ledgers. Evaluate all 80
phases with the common physical metric and measure full-cycle cost. One
snapshot is not one complete-cycle exposure. No real-data training, selected
checkpoint or strong-baseline performance is claimed by this source module.
# Input reconciliation before scientific training

`aneug_rhsia_input_alignment.py` checks the released geometry encoder against
the admitted source archives. It applies the upstream GHD deformation equation,
matches rows without assuming order or resolving duplicate coefficients by
index, and independently compares only train/validation xyz against cached
Meshes state. WSS columns and held-out record tensors are never accessed.
Full descriptor finiteness and hierarchy are audited, but this does not prove
that cached eigenpairs solve the intended Laplacian. That interpretation stays
explicitly separate. Boundary loops are genuine topological features; their
canonical index order must not be presented as anatomical inlet/outlet labels.
All returned case/row mappings are private evidence, not public dataset assets.

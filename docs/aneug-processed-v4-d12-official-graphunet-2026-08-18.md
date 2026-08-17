# D12 direct released Graph U-Net baseline

## Why this baseline comes before a new gate

The earlier field-rL2 ceiling of 0.35 was an internal screening heuristic. It
was not calibrated by executing a direct prior model on the same D5 split, so
D12 does not use it as an acceptance or stopping rule. D11 remains a valuable
matched reimplementation result, but it is not the released baseline.

## What is executed directly

D12 imports `PyGGraphUNetwTemporalEmbedding` from the clean official
`WenHaoDing/AneuG-Flow` checkout at commit `4a090a0…`. The class and its
forward method are not copied or modified. Its released configuration is kept:
six geometry/normal inputs, 512 hidden channels, three dynamic TopK levels,
0.25 pooling at each level, residual decoding, and phase plus waveform
embeddings. The source hashes are pinned in the executable config.

This is a direct execution of a released model class through a protocol
adapter, not an end-to-end reproduction. The public trainer uses a random
90/10 split, DDP, release-normalized tensors, a composite loss, optional steady
data and wandb. D12 instead uses the same 406/51 component split, physical
target scaling, mesh normals, area-weighted relative field loss and validation
metrics as the other AURORA models. The pinned code and dataset do not contain
the referenced `waveform_yiying.txt`; D12 therefore supplies an all-zero
waveform, which adds no information beyond the phase embedding. PyTorch3D is
not used by this model, although two transitively imported official files have
an unused `Meshes` import; the adapter supplies only that import symbol.

## Evidence role

Every coverage epoch visits each of the 406×80 train case-phase pairs exactly
once in a deterministic shuffled order. Validation reconstructs all 80 phases
for each of the 51 validation cases and reports the same field, TAWSS, OSI,
coverage and tangency metrics. Checkpoints are append-only at every validation
check. There is no absolute pass/fail threshold. The result becomes the direct
prior reference for later validation studies of spatial capacity, geometric
encoding, periodic decoders and cycle-functional consistency. Outer and
auxiliary values remain unread.

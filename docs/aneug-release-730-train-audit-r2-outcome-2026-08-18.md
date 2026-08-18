# Release-730 train audit R2 outcome

Corrected CPU-only PBS job `117037.ECE-util1` exited 0 after 7 minutes 10
seconds. It inspected exactly 584 training cases and used no GPU. Validation,
locked-test and processed-only field read counts are all zero. The public
result SHA-256 is
`3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587`;
no model was fitted or selected.

All registered integrity checks passed: finite train tensors and GHD,
80-by-13,902-by-9 shape, exactly static geometry, valid/nondegenerate shared
faces, physical decode/round-trip error at `3.55e-15`, finite cycle endpoints
and exact source/split identities. The exact train loader-order hash is private
and now provides one common ordering and train-derived normalization source for
all later comparators.

## Descriptive findings, not gates

- Area-weighted mean TAWSS has train median `8.413` and 5th--95th percentiles
  `5.494--12.209`; mean OSI has median `0.00785` and 5th--95th percentiles
  `0.00366--0.01946`.
- Complete-cycle response RMS has median `11.454` and 5th--95th percentiles
  `7.759--16.230`, supporting explicit amplitude separation as a candidate,
  not proving that a learned response manifold will work.
- Phase-79-to-0 relative jump is tightly concentrated near one percent
  (median `0.01166`, 95th percentile `0.01456`) but has maximum `0.36399`.
  A periodic decoder must not be imposed before a train-only attribution
  distinguishes a true source discontinuity from a low-denominator or isolated
  case effect.
- Stored normals agree directionally with geometry-derived normals (casewise
  5th-percentile absolute cosine median `0.9910`), but their norm reaches
  `0.000151`. Reference WSS also has nonzero normal-component ratios: casewise
  median-ratio median `0.0211`, and casewise p95-ratio median `0.1107`.
  Therefore hard unit-normal division or hard tangent projection is not yet a
  justified primary-output operation.

## Consequence

The data are fit for train/validation model development, but the prior
architecture sketch is narrowed. Primary comparators must predict the raw
released vector field under one shared physical metric. A tangent parameterization
or periodic representation is allowed only after a train-only attribution
quantifies the exceptional cycle and near-zero-normal support. Any physical
regularizer should be soft and reference-calibrated unless the target itself is
redefined prospectively for every model.

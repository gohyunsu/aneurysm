# Release-730 complete-cycle response oracle

This diagnostic asks whether the 584 training WSS cycles span a useful
low-dimensional response space for the 73 validation geometries. It is not a
learned surrogate, a rank-selection rule or a paper performance result.

The basis is fit from raw released physical Cartesian WSS. Each complete cycle
is weighted by uniform phase quadrature and the mean normalized vertex area of
the training geometries, divided by its own weighted RMS amplitude, and then
centered. Right singular vectors are recovered through the 584 by 584 case
Gram matrix. All ranks 0, 16, 32, 64, 128 and 256 are reported without an
automatic winner.

Validation reconstruction deliberately uses the true validation amplitude and
true response coefficients. It therefore measures an optimistic representation
ceiling, not what a geometry encoder can predict. The same raw physical field
metric and derived TAWSS, OSI, mean-vector, low-TAWSS, peak-phase and mesh-normal
component endpoints used by the direct Graph U-Net adapter are reported. No
tangent projection or phase-boundary closure modifies the reference or oracle
field.

A weak high-rank ceiling rejects the global response branch before learned
model development. A strong low-rank ceiling only makes coefficient prediction
eligible; it does not show that geometry contains enough information to infer
those coefficients or the amplitude. Learned response-only, local-only and
combined variants must still be compared on the same validation split.

Execution is serialized behind the currently running direct released-class
baseline because introai9 provides the sole authorized GPU. A fresh private
activation must bind that job's terminal record, the Quality-passed source and
the exact split/audit artifacts. The 73-case locked test and 79 processed-only
extras remain sealed, the basis stays outside Git, and no numeric oracle result
is public or entered as learned model performance.

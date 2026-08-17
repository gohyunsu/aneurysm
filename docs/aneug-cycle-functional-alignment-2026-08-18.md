# Complete-cycle functional-alignment kernel

## Role

This dataset-free kernel prepares the D13C same-backbone objective ablation. It
does not select an architecture, loss weight, performance threshold or paper
claim. D11, D12 and D14 remain field-only controls; only after those direct
baselines and D13A's representation ceiling are available can a train/
validation development run bind this kernel.

All loss terms are computed from the same decoded transient WSS field. There
are no independent TAWSS or OSI heads that could disagree with the field. The
objective exposes four terms separately:

1. area/phase-weighted relative field error;
2. area-weighted mean-vector error normalized by reference TAWSS energy, which
   remains defined even for a fully reversing zero-mean cycle;
3. area-weighted TAWSS error; and
4. robust OSI error on reference-defined active support.

The support floor and all loss coefficients are explicit inputs. They must be
defined from training data and selected using validation development; the
kernel does not infer them or convert them into an absolute pass/fail rule.
RRT is excluded because it is algebraically redundant with mean-vector
magnitude. The failed D9A hard post-hoc projection is also excluded: gradients
instead pass through the complete predicted cycle.

## Required controlled comparison

On one fixed backbone and initialization policy, compare field only, field plus
TAWSS/mean vector, field plus OSI, and the complete objective. Report every
trial with field, mean-vector, TAWSS, OSI, active-support coverage and compute.
A functional gain can support the paper only if its paired field trade-off is
competitive with the empirical direct-baseline distribution; no numerical
cutoff is set before those baselines run.

## Synthetic guarantees

The tests require exact-cycle zero loss, finite backward propagation, common
rotation and scale invariance, explicit reference-only OSI support, finite
zero-prediction behavior, double-precision autograd agreement and fail-closed
input validation. These are numerical properties only, not scientific
evidence.

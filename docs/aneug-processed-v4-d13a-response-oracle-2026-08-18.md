# D13A complete-cycle response-manifold oracle

## Question

Before building a learned POD or hybrid residual model, D13A asks whether the
406 training WSS cycles span a useful low-dimensional response manifold for
the 51 validation geometries. It is a representation ceiling, not a surrogate
and not evidence of generalization from geometry.

Each train cycle is weighted by uniform phase quadrature and the mean
train-mesh vertex area. Its weighted RMS amplitude is separated, the normalized
cycle is centered, and right singular vectors are recovered from the 406×406
case Gram matrix. The public rank grid is 0, 16, 32, 64, 128 and 256. All ranks
are reported; D13A does not select one.

For validation reconstruction, the projection deliberately uses the true WSS
cycle to obtain both coefficients and RMS amplitude. This makes the result an
optimistic upper bound on representation error. Reconstructed Cartesian fields
are projected to the validation mesh tangent plane before the standard field,
TAWSS and OSI metrics. No oracle value may be reported as learned prediction
performance.

## Interpretation

- A weak rank-256 ceiling rejects the output-response branch before training.
- A strong field ceiling with weak TAWSS/OSI supports adding functionally
  aligned training and a local residual rather than increasing rank blindly.
- A strong low-rank ceiling only makes coefficient prediction eligible; it
  does not establish that geometry contains enough information to predict the
  oracle coefficients or amplitude.

D13A stays non-executable until D12 has a terminal record, the exact D13A
source passes Quality and a private activation binds both. It uses the existing
406/51 cache, never reads outer/auxiliary values, saves a private basis asset
outside Git, includes no case identifiers and has no absolute pass threshold.
The result and basis both bind the public commit, config, activation, cache
manifest and predecessor D12 terminal-record hashes.

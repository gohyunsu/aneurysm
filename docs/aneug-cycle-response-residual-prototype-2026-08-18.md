# Complete-cycle response plus tangent-residual prototype

This dataset-free module makes the performance-oriented D13B candidate
concrete without selecting or running it before direct evidence exists. It is
not an experiment result, a rank decision or a novelty claim.

The global branch predicts a positive weighted response amplitude and
coordinates in D13A's train-only, energy-normalized complete-cycle basis. The
decoded Cartesian cycle is projected to each geometry's tangent plane and
rescaled to retain the predicted weighted amplitude. Separating amplitude from
pattern prevents a large-magnitude case from dominating the response
coordinates.

The local branch is an interchangeable complete-cycle geometry backbone. D11
is the current candidate; D14 may replace it only if the same-information
Transolver control is empirically competitive. A case-conditioned gate mixes
the tangent residual with the global response. Its weighted overlap with the
response basis is reported as a soft complementarity penalty. We deliberately
avoid a hard projection: D9A already showed that an exact post-hoc constraint
can move an otherwise useful field and severely damage OSI.

Four later rows isolate the mechanism: response only, local backbone only,
response plus local residual, and the same two-branch model with complete-cycle
functional alignment. Rank and backbone remain unselected until D12 terminates
and D13A reports every registered oracle rank. There is no absolute performance
threshold; later comparisons use paired validation endpoints, uncertainty,
coverage and measured compute. Outer and auxiliary values remain sealed.

The decoder copies only the selected basis rows into independent storage.
Consequently a rank-16 or rank-32 run does not silently retain the full
rank-256 basis allocation on the GPU; parameter/memory comparisons reflect the
declared rank rather than an implementation view.

The architectural variants also have real compute boundaries. A response-only
model may be constructed without a local backbone and never evaluates one; a
local-only forward never evaluates the response head. Thus the ablation does
not charge an unused branch to one row or attribute its hidden compute to
another.

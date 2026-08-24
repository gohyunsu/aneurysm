# Complete-cycle response plus raw-Cartesian residual prototype

This dataset-free module makes the performance-oriented release-730 candidate
concrete without selecting or running it before direct evidence exists. It is
not an experiment result, a rank decision or a novelty claim.

The global branch predicts a positive weighted response scale and coordinates
in the release-730 oracle's train-only, energy-normalized complete-cycle basis.
It applies the oracle's reconstruction exactly: the centered mean-plus-basis
pattern is multiplied by the predicted scale and unweighted without an extra
pattern renormalization. Separating scale from pattern prevents a
large-magnitude case from dominating the response coordinates.

The local branch is an interchangeable complete-cycle geometry backbone. The
release-730 GHD-GPS/GINE comparator is the current candidate; Transolver may
replace it only if the same-information control is empirically competitive. A
case-conditioned gate mixes the raw Cartesian residual with the global
response. Its weighted overlap with the response basis is a detached reported
diagnostic, not an optimized penalty or a hidden loss-weight choice. The
registered branch ablations, rather than a decomposition regularizer, establish
the roles of the two branches. No branch or final output is hard-projected
tangent: the release-730 oracle and common evaluator retain the raw released
Cartesian target, and train attribution found nonzero normal components and
unreliable stored normals.

Four later rows isolate the mechanism: response only, local backbone only,
response plus local residual, and the same two-branch model with complete-cycle
functional alignment. Rank and backbone remain unselected until the terminal
release-730 Graph U-Net record is preserved and the response oracle reports
every registered rank. There is no absolute performance threshold; later
comparisons use paired validation endpoints, uncertainty, coverage and measured
compute. Locked test and processed-only auxiliary values remain sealed.

The decoder copies only the selected basis rows into independent storage.
Consequently a rank-16 or rank-32 run does not silently retain the full
rank-256 basis allocation on the GPU; parameter/memory comparisons reflect the
declared rank rather than an implementation view.

The architectural variants also have real compute boundaries. A response-only
model may be constructed without a local backbone and never evaluates one; a
local-only forward never evaluates the response head. Thus the ablation does
not charge an unused branch to one row or attribute its hidden compute to
another.

The shared wrapper also owns the common single-field auxiliary head required
by future T+M/T+S cells. That head is intentionally inactive during a cycle
forward. The field-anchored backward path therefore omits a parameter tensor
only when both the field and functional objectives report it as unused; a
one-sided dependency fails closed. Active cycle-parameter gradients are
combined exactly as before, and the inactive auxiliary head remains without a
gradient. This is runtime compatibility for the predeclared ablation, not an
architecture, objective or optimization change.

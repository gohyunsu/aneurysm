# D14 modern irregular-mesh comparator

D14 prepares a strong, same-information Transolver control before selecting an
AURORA method. Transolver introduced physics-slice attention for PDEs on
general geometries at ICML 2024. Its official irregular-mesh defaults use eight
256-wide blocks, eight heads and 32 learned slices. The exact MIT repository is
pinned at `75e0f67643806a81cd1d3f6adc88dd8c02416fe7`.

The control receives the same geometry information as D11: coordinates,
mesh-derived normals, relative vertex area and all 432 cached GHD coefficients.
It predicts the complete 80-phase Cartesian WSS cycle in one forward pass and
then applies the same deterministic tangent projection, field loss and
validation metrics. This tests whether modern physics attention improves the
backbone without confounding it with the proposed response basis or functional
objective.

This is an adaptation, not an exact Transolver reproduction. The upstream
AirfRANS task, four steady output channels and trainer are replaced by the D5
split, transient WSS output and AURORA evaluator; GHD conditioning is new. The
source-inspired module is redistributed with its MIT notice. All deviations are
machine-readable in the config.

D14 has no absolute pass threshold. It will be compared with D11 and D12 using
paired validation field and functional errors, coverage and measured compute.
It remains non-executable until D12 has a terminal record, this exact source
passes Quality and a fresh private activation binds both. Outer and auxiliary
values remain sealed, and D14 is never itself a novelty claim.

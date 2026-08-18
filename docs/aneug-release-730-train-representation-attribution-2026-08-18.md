# Train-only representation attribution

The release-730 train audit supports use of the data but does not support two
previously assumed target transformations. One training case has an unusually
large phase-79-to-0 jump, stored normal magnitudes approach zero, and the raw
reference vectors retain measurable normal components. Hard periodic closure
or hard tangent projection could therefore alter the supervised target rather
than encode a harmless prior.

This bounded CPU analysis reads only the 584 training fields and reports all
80 adjacent cyclic jumps per case, the boundary-to-interior jump ratio, stored
normal support, agreement with mesh-derived unit normals, and normal-component
ratios under both normal definitions. Validation, locked test and the 79
processed-only extra fields remain unread. Per-case identifiers stay private;
only aggregate distributions and counts may be public.

The analysis has no pass threshold and cannot select an architecture. Every
strong comparator will initially predict the same raw physical Cartesian WSS.
The result may justify a soft diagnostic or a representation ablation, but it
cannot delay the new-split direct baselines or create a paper claim by itself.

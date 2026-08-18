# Prediction-blind confirmatory CFD figure protocol

The sole paper-facing surface figure is selected only after the model,
checkpoints, endpoint definitions and one-time outer opening are frozen. This
public module does not open outer data. It fixes the selection logic now so a
visually favorable candidate error cannot determine the examples later.

For each of the 51 outer reference cycles, the selector computes
triangle-area-weighted mean OSI over valid reference support. Stable 10th,
50th and 90th percentile ranks provide low, median and high reference OSI
burden cases. Within each selected surface, the trace vertex is the lowest
ordinal vertex nearest the area-weighted 90th percentile of valid reference
OSI. Neither selection step accepts a baseline or candidate tensor.

Reference, strongest frozen direct control, and frozen candidate use the same
canonical orthographic camera, coordinates and mask. TAWSS uses the full range
of the three selected references; OSI uses its physical [0, 0.5] range. No
candidate-dependent clipping is permitted. Each row also shows absolute error
and the same reference-selected vertex's 80-phase WSS magnitude/direction
trace. This is an interpretability figure for synthetic CFD, not clinical risk
evidence.

# Numerical repeatability of the direct snapshot comparator

A componentwise cached/native assertion alone cannot tell whether geometry
reuse is incorrect or whether unchanged native GPU calls vary numerically.
The numerical audit holds the model and admitted inputs fixed and reports:

- Two fresh geometry encodings: node and edge feature discrepancies.
- Three unchanged native calls at each of phases0,39,79.
- Three decoder calls with one fixed geometry encoding at each phase.
- The actual public80-phase cycle method against fresh native snapshots.
- Mutations of encoded inputs, model parameters/buffers and supplied features;
  evaluation RNG changes are reported independently.
- A strict-deterministic native repeat, or the exact unsupported-operation
  message. Original deterministic flags are restored afterwards.

For every comparison, maximum absolute, RMS and relative-L2 discrepancies
accompany counts failing the original1e-5 absolute/relative componentwise
tolerances. That tolerance is not loosened. The report neither measures CFD
accuracy nor declares cached evaluation correct merely because native calls
also vary. Finite small native variation, state stability, encoder/decoder
localization and the physical scale of differences must be interpreted
together before choosing an evaluation path. A material deterministic cache
discrepancy requires implementation repair; a nondeterministic-operation error
is evidence about the numerical environment, not a model-performance verdict.

The audit adds no forward hooks, attention replacement, dimension reduction,
training update or reference target. Its fixture tests verify instrumentation
only. Actual source-sized GPU results are private and separately required;
they do not by themselves replace a sufficiently trained strong comparator.

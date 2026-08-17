# D9A frozen-checkpoint projection attribution

D9 failed its single-seed validation development screen. The direct baseline
was infeasible, and the moment-POD output improved TAWSS but substantially
degraded field and OSI error. D9 remains failed and the outer split remains
sealed.

D9A asks one narrower, no-fit question: does applying exact cycle-moment
projection only during validation create the moment-specific tradeoff? It
loads the frozen D9 moment checkpoint and the same 51-case validation cache.
For each case, one model forward produces the raw moment-POD field; the exact
projector then acts on those same predicted moments and residual. The evaluator
reports identical field, TAWSS, OSI and coverage metrics for both modes, their
paired direction, internal moment residuals and projection displacement.

D9A does not train, select a checkpoint, read train-case values, access outer
or auxiliary cases, change a threshold or authorize repair. Its numeric output
is private. A later repair may be registered only after this diagnostic and
the already observed direct optimization trajectory jointly support a single,
prospectively bounded failure hypothesis.

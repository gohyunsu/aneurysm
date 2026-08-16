# Cycle-moment projection prototype · 2026-08-16

**State:** synthetic-only and non-executable. This prototype reads no dataset,
does not select the future architecture and cannot submit a job. D6 remains
unactivated.

## Question

The conditional application mechanism requires a transient tangent field whose
own mean vector and TAWSS agree with the two quantities predicted by the model.
Before spending GPU compute, this prototype asks whether that reconstruction is
mathematically feasible and numerically usable.

Let \(m\in\mathbb R^3\) be a tangent mean vector, let
\(a\geq\|m\|\) be a predicted mean magnitude, and let \(r_t\) be a tangent
residual with \(E_t[r_t]=0\). Define

\[
\tau_t(s)=m+s r_t,\qquad
F(s)=E_t[\|\tau_t(s)\|],\qquad s\geq0.
\]

Then \(E_t[\tau_t(s)]=m\) for every \(s\). Convexity of the norm makes
\(F\) convex. Its right derivative at zero is zero when \(m\neq0\), because
\(E_t[r_t]=0\); therefore it is non-decreasing for \(s\geq0\). If the residual
is nonzero, the reverse triangle inequality gives

\[
F(s)\geq sE_t[\|r_t\|]-\|m\|,
\]

so a finite root exists for every strict target \(a>\|m\|\). The prototype
uses this bound to bracket a vectorized scalar solve at each vertex.

## Non-unique Jensen-boundary case

When \(a=\|m\|\), a purely collinear residual can change WSS magnitude over
the cycle without changing either moment. Thus the feasible scale need not be
unique. Always choosing \(s=0\) would erase valid pulsatility. The implemented
rule instead selects the feasible scale closest to the raw scale \(s=1\). For
strict Jensen-interior targets the root is unique under nondegenerate residual
variation; for boundary targets the closest-root rule is part of the
prospective mechanism and must be ablated if the method ever becomes eligible.

## What the tests establish

Synthetic tests verify:

- simultaneous mean-vector and mean-magnitude agreement;
- tangent output after deterministic normal projection;
- fail-closed behavior for a Jensen-infeasible target or inactive residual;
- rotation equivariance of the projection itself;
- preservation of collinear unidirectional magnitude pulsatility at the
  Jensen boundary; and
- finite autograd values in a nondegenerate interior example.

These are implementation properties, not scientific evidence. Exact
self-consistency with predicted moments can still be consistently wrong
relative to CFD. The mechanism is ineligible unless D6 passes and a later
same-backbone baseline gate observes material functional error at matched
field error. No method name, model claim or paper result is created.

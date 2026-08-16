# Transient WSS functional metric kernel

Status: **synthetic-only, method-free and non-executable**  
Date: **2026-08-16 KST**

## Why this exists

The same-task AneuG prior already reports TAWSS, OSI and RRT. These quantities
are established evaluation endpoints, not AURORA novelty. A future matched
baseline study nevertheless needs one unambiguous implementation. Historical
P0 code used uniform means and silently clamped singular denominators; those
bytes remain provenance, while this kernel fixes the policy for future work.

For explicit normalized phase quadrature weights \(w_t\),

\[
m=\sum_t w_t\tau_t,\qquad
a=\sum_t w_t\lVert\tau_t\rVert,
\]

\[
\operatorname{OSI}=\frac12\left(1-\frac{\lVert m\rVert}{a}\right),
\qquad
\operatorname{RRT}=\frac{1}{(1-2\operatorname{OSI})a}
=\frac{1}{\lVert m\rVert}.
\]

Phase weights are mandatory: the kernel never silently assumes uniform time
sampling. OSI is undefined at inactive TAWSS nodes, and RRT is undefined where
the mean-vector magnitude is inactive. The implementation returns NaN plus an
explicit validity mask rather than replacing a singular value with an
arbitrarily large finite number. Any future comparison mask or denominator
floor must be learned from D5-train data and registered before validation.

## Property evidence

Synthetic tests cover constant and reversing cycles, nonuniform quadrature,
rotation, physical rescaling, phase replication, the exact RRT redundancy and
fail-closed malformed input. These prove formula implementation, not agreement
with CFD, baseline failure, method superiority or clinical relevance.

No real field, validation/outer record, loader, model, scheduler, PBS/GPU,
paper result or static-site file is opened. D6 still requires separate human
activation, and `junjinyong` remains forbidden.

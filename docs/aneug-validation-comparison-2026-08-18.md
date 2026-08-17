# Paired validation comparison without an invented pass line

This result-pending utility compares the direct prior, strong modern control,
and method combinations on the same 51 validation components. It reports raw
means, paired candidate-minus-reference deltas, percentile bootstrap intervals,
the probability of a favorable paired direction, and the multi-endpoint Pareto
set. It never turns those continuous quantities into an automatic winner or an
absolute pass/fail threshold.

Pairing is valid only when a private activation binds exact result hashes to
the same cache manifest and loader order. Rows remain identifier-free, so
mixing another split or a differently ordered result must fail before this
utility is used. The resampling unit is a synthetic geometry component, not a
patient or clinical site, and the interval is descriptive validation
uncertainty rather than population inference.

Core endpoints are conventional field relative L2, TAWSS normalized absolute
error, valid-support OSI MAE and OSI coverage. Mean-vector error is retained
when every compared method reports it. Parameter count, memory, training time
and inference latency remain separate compute descriptors rather than being
hidden inside a hand-weighted score. Architecture and objective rows stay
distinct so capacity gains cannot masquerade as functional-loss gains.

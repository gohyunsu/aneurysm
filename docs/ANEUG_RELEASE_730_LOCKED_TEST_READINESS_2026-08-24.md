# Release-730 one-time locked-test readiness

## Outcome

The final confirmatory boundary is now implemented but deliberately
non-executable. After validation-only development and all twenty fresh-seed C0
cells finish, one private activation may evaluate the frozen checkpoints on
the 73-case locked test in a single GPU job. No test field has been opened by
this implementation work.

## Exact batch

The batch contains five prospectively fixed training seeds and four cells per
seed: selected control and selected proposal, each trained with transient-only
information (T) and with the identical leakage-audited steady information
(T+S). Every checkpoint, validation result and terminal record must exist,
match its SHA-256 and agree on model identity before the test-access marker is
created. T0 performs no training, optimization, checkpoint selection or model
repair.

The evaluator uses the same ordered 73 geometries for all twenty cells and
reports case-level field rL2, mean-vector error, TAWSS error, OSI MAE and OSI
prediction-valid coverage. Crossed seed/case bootstrap contrasts preserve the
registered proposal-minus-control sign. Field, TAWSS and OSI errors are the
three claim endpoints; mean-vector error is supporting and coverage remains a
diagnostic rather than a gate.

## Test order and sealed scope

The public test digest identifies the case set, not its private loader order.
The fresh T0 activation must therefore bind a separate ordered-test SHA-256,
which the evaluator recomputes from the private split before any test tensor is
indexed. The 79 processed-only extras remain outside the selected record set.
No case identifier is written to the metric result, figure selection or figure
payload.

## Prediction-blind figure

Before loading any model, the batch selects three cases from reference-only
area-weighted OSI burden at the predeclared 0.1, 0.5 and 0.9 quantiles and one
reference-only trace vertex per case. The figure uses the prospectively named
seed `20260903` and the T+S control/proposal cells; it does not choose a best
seed from test outcomes. Only those three references and predictions are kept
in a compact loader-free payload. Rendering can then consume that artifact
without reopening the dataset or checkpoints.

## Execution boundary

The config, evaluator and PBS wrapper require a fresh private T0 activation,
the exact twenty-checkpoint manifest, completed five-seed validation evidence,
the validation-only selection record and the train-only response basis. The
PBS wrapper permits exactly one GPU job and records whether locked-test access
began even if the process terminates. This is readiness only: no activation,
checkpoint manifest, T0 job, result, figure or paper claim currently exists.


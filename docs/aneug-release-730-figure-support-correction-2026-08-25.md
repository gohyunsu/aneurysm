# Release-730 figure support correction

## Identified gap

The result-pending manuscript and endpoint contract use OSI only on a
train-frozen reference-TAWSS support. The prepared confirmatory-figure selector
instead used the generic numerical `1e-12` activity epsilon. Consequently,
low-activity nodes with unstable OSI could determine the reported low/median/
high reference-burden cases and trace vertices even though those nodes do not
belong to the registered OSI endpoint support.

## Prospective correction

Before any T0 activation or locked-test field read, the release-730 selector
now requires the common `reference_tawss_floor` stored by all twenty frozen C0
checkpoints. The one-time preflight fails closed if those train-only values are
missing or disagree. Reference-only case burden, trace-vertex selection and
the rendered OSI support all use that same floor. Prediction values still
cannot affect cases, vertices, camera, colour limits or trace limits; a
prediction that is inactive on reference support is masked rather than
imputed.

This changes no dataset, split, model, objective, endpoint, seed, threshold,
checkpoint rule or result. It opens no locked-test or processed-only field and
creates no performance claim. The historical 51-case selector remains
unchanged by default because the generic helper retains its original numerical
epsilon unless an explicit train-frozen floor is supplied.

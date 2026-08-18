# Release-730 train-only objective-scale audit

The released transient trainer does not apply its frame MSE directly to the
stored WSS channels when `renormalize_transient=True`. It first derives, from
the training partition, a population standard deviation at each phase over
cases and nodes, averages that standard deviation over phase, adds its coded
`1e-6` epsilon, and rescales each WSS component before MSE. The resulting
effective quadratic weight is `(std + 1e-6)^2`. The active released-class
adapter uses unit channel weights in the stored steady-normalized coordinates.

This CPU-only audit reproduces the upstream statistic on exactly the 584
training cases. It reads no validation, locked-test or 79 processed-only-extra
field, fits no model, uses no GPU, defines no materiality threshold and cannot
authorize a sensitivity run automatically. Its numeric result remains private.

The exact audit completed successfully on `introai9` after scheduler recovery.
It read all 584 registered training fields and zero validation, locked-test or
79-extra fields, used GPU 0 and fitted no model. The result is stored in the
private evidence repository. It records a bounded component-wise weighting
difference but, by contract, neither publishes the numeric vector nor triggers
an objective-only sensitivity. That decision waits for the active direct
baseline's terminal validation trajectory.

The audit answers one bounded attribution question: is the upstream channel
weight vector sufficiently anisotropic that an otherwise identical objective-
only sensitivity could materially strengthen the direct comparator? It does
not evaluate performance, choose a model or interrupt the active Graph U-Net.

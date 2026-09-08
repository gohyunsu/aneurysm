# Mean and oscillatory prediction error

The transfer hypothesis concerns what steady supervision helps the complete
transient prediction learn. A reference-only Fourier reconstruction audit does
not answer this question: it characterizes representation capacity, not a
trained model's errors. `aneug_cycle_error_spectrum` evaluates the difference
between an actual predicted physical vector cycle and its reference.

For each case, orthonormal real FFT energies use vertex-area weights, uniform
phase averaging, and multiplicity two for conjugate pairs. DC and the even-grid
Nyquist bin each count once. No snapshot is dropped or endpoint equalized.
Frequencies are indices on the nominal sampled cycle, not independently
verified physical Hz. DC denotes the transient cycle mean, not steady CFD.

Every frequency's squared error is divided by the **same full reference cycle
energy**, retaining the common evaluator's 1e-12 energy floor. Their sum equals
squared physical vector-WSS rL2. Report DC versus
all oscillatory frequencies as the primary decomposition; retain every bin so
there is no performance-selected Fourier cutoff. Band-relative rL2 is also
available where the reference band exceeds a disclosed float64 numerical
support floor. Unsupported relative errors are null, not zero. Their error
still contributes to the full-field denominator and cannot disappear from the
evaluation.

Aggregate cases equally. Mean squared contributions sum to mean squared rL2,
not the square of mean rL2. Report reference-supported case counts alongside
band-relative means. Frequencies, phases and vertices are not independent
samples; uncertainty must use paired cases and repeated training seeds.

This post-hoc evaluator does not read archives, train, select checkpoints,
change the field loss, smooth predictions, or reopen any test set. A private
evaluation runner must bind actual checkpoints, admitted validation order,
common physical decoder and this source before producing scientific values.
Tests use synthetic arrays only and are not evidence of improved transfer.
Existing training sources and live jobs remain unchanged.

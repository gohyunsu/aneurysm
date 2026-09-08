# Train-only cardiac-cycle representation audit

This supports the architecture-v3 decoder decision; it is not a new model,
an accuracy admission gate, or a substitute for strong direct baselines.

The pinned author's `new_version/loaders.py:get_fluent_ascii_raw_data_reduced`
keeps the final 80 snapshots when more are present. Its registration path
stores `case`, `labels` and `tensor`, without preserving a physical time array.
The audit therefore labels its grid **nominal snapshot index i/80** and records
the actual processed metadata keys. It does not invent a waveform, assert
verified physical timestamps, or force the first and last samples to be equal.
If authoritative timing is recovered, check it and adapt the representation.

Only the original 584 training fields are decoded. Existing hashes, partition
membership and training order are checked; the source normalizer only reverses
the author's encoding. The steady case fields, validation fields, old-test
fields and processed extras are not decoded. All case and aggregate evidence
stays private. Source manifests describing a historically unopened test are
not used to deny that the original model pair later opened it.

For cutoffs 0/2/4/8/16/24/32/40 the CPU audit reports per-case, surface-area-
weighted field reconstruction rL2, discarded spectral energy, oscillatory-only
error, worst-phase error and same-field TAWSS error. It reports quantiles and
maxima, not just a cohort average. The full 80-dimensional real basis retains
the even-grid Nyquist column. Dense basis reconstruction and FFT/Parseval
calculations cross-check numerical correctness independently. Constant cycles
have explicitly undefined oscillatory-relative error, not NaN or fabricated 0.

Each completed case is saved incrementally so an interrupted analysis retains
inspectable partial evidence. Only all 584 cases produce a complete result.
No cutoff is selected automatically. The learned decoder is selected later on
validation alongside a full-output control; these oracle errors are never
reported as learned performance. OSI evaluation remains part of the common
model evaluator, not a new inconsistent threshold in this representation audit.

Run the public module via `cluster/pbs_aneug_cycle_representation_v3.pbs` on an
authorized account/queue with four CPUs, 64 GB memory, zero GPUs, a clean pinned
checkout and a private fresh job root. The script does not require a new copy
of the 43 GB dataset and never changes existing GPU training sources.

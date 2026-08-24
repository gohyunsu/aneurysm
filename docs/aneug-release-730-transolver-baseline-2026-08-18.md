# Release-730 Transolver strong comparator

This comparator adapts the original ICML 2024 Transolver physics-slice design
to the completed 584/73 AneuG-Flow protocol. It is a same-information strong
control, not an upstream-task reproduction and not the proposed method.

The model uses centered/scaled coordinates, recomputed mesh unit normals,
relative vertex area and the train-standardized 432-D GHD descriptor. Eight
256-wide blocks with eight heads and 32 slices follow the official AirfRANS
capacity defaults. One forward predicts all 80 Cartesian WSS phases. The
adapter adds GHD conditioning and a complete-cycle output because neither is
part of the upstream AirfRANS task.

Unlike the historical v4 D14 preparation, the output is not tangent-projected.
Training and evaluation use the raw released physical Cartesian field, the
train-only vector RMS scale and the same primary and secondary endpoints as
the release-730 Graph U-Net and GHD-GPS/GINE controls. No hard phase closure,
absolute threshold or automatic winner is defined. Test and the 79
processed-only cases remain unread.

Under the active evidence-led order, execution requires preserved Graph U-Net,
response-oracle and GHD-GPS terminal records plus a fresh private activation.
The runner recomputes the oracle and GHD-GPS terminal hashes before loading any
data. A diagnosed infrastructure or evidence change may still reprioritize the
independent comparator through a separately versioned contract; stale
activations cannot silently bypass the current order. One seed remains
validation development; multi-seed confirmation and the locked test are
separate later stages.

The shared loader now verifies the producer-derived validation order
`aac001b3...d4dc30` before field access, and the terminal result emits both
case-set and order digests. Terminal-status writes are atomic. The prior
activation predates this provenance correction and cannot authorize the
corrected bytes; create a fresh activation before execution.

The PBS envelope likewise requests the queue's 72-hour default. The prior
24-hour request was shorter than the completed Graph U-Net's observed
28:41:19 despite the same 80-epoch minimum and a materially larger operator.
Only the resource request changes; model, seed, objective, epoch ceiling,
patience, validation cadence and checkpoint rule remain fixed, and actual
rather than requested GPU-hours are reported.

The same exact-state continuation contract applies to Transolver. Version-2
periodic checkpoints retain current/best model state, optimizer, scheduler,
patience state, full history, accumulated time and all RNG states. Only a
fresh activation binding an actual noncomplete/nonzero-exit terminal record
and checkpoint digest can resume into a new run root. Both file hashes are
recomputed before restoration; a completed run, provenance drift, partial
state or one-sided environment binding fails closed.

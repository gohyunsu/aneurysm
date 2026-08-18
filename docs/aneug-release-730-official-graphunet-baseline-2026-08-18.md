# Release-730 official Graph U-Net baseline

This is the first direct prior on the completed 584/73 release-aligned split.
It imports the released `PyGGraphUNetwTemporalEmbedding` class unchanged from
the exact upstream commit. It is a protocol adapter, not an end-to-end
reproduction: the release does not contain the waveform file referenced by
the trainer, and the paper split, single-GPU environment and common physical
evaluation differ from upstream.

The split provenance needs one further distinction. The AneuG-Flow paper's
reported 4.67% experiment is a steady-WSS 80/20 evaluation, not this transient
task. The pinned transient helper uses a nominal 90/10 ratio but performs no
shuffle: it takes the leading eligible `stable_*` entries in archive order as
test cases. The active immutable config's phrase `released random 90/10 split`
is therefore imprecise and is superseded by this clarification; it means the
released helper's order-slice 90/10 path. The running bytes are not changed.
Our keyed, field-blind 584/73/73 assignment additionally supplies a distinct
validation partition and locked test, while making no unavailable lineage
claim.

The adapter retains the released six normalized coordinate/normal inputs,
phase embedding and physical log-magnitude term. Its frame MSE is computed
directly in the stored steady-normalized coordinates. A later direct source
audit found that the upstream default `renormalize_transient=True` first
rescales this residual with train-transient channel statistics. This bounded
channel weighting is therefore an additional declared adapter difference: the
active row is not an objective reproduction. It uses the common zero waveform
because every released case shares one inlet waveform and the referenced file
is absent. No boundary-condition generalization is claimed. The only
log-magnitude stabilization clamps undefined `log(0)` support.

Predictions are decoded to the raw released physical Cartesian WSS. There is
no hard tangent projection or periodic closure. Checkpoint selection uses the
case-mean area/phase-weighted physical field relative L2 on the 73 development
cases. TAWSS, OSI, mean-vector, low-TAWSS, peak-phase and normal-component
errors are secondary endpoints from that same field. The 73-case locked test
and 79 processed-only extras remain unread.

One seed is validation development, not a paper result. There is no absolute
pass threshold or automatic winner. Its purpose is to establish a credible
direct-prior reference before optimizing the GHD-GPS/GINE, Transolver or
global-response-plus-local-residual candidates.

The healthy active run is preserved rather than stopped or silently relabelled.
After its terminal record, an objective-only sensitivity is warranted only if
exact train-only scale ratios and its validation failure mode indicate that
the upstream weighting can materially strengthen this comparator. Such a
sensitivity must hold model, split, seed, schedule, log term, evaluator and
sealed scope fixed.

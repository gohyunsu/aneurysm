# Release-730 official Graph U-Net baseline

This is the first direct prior on the completed 584/73 release-aligned split.
It imports the released `PyGGraphUNetwTemporalEmbedding` class unchanged from
the exact upstream commit. It is a protocol adapter, not an end-to-end
reproduction: the release does not contain the waveform file referenced by
the trainer, and the paper split, single-GPU environment and common physical
evaluation differ from upstream.

The adapter retains the released six normalized coordinate/normal inputs,
phase embedding, normalized frame MSE and physical log-magnitude term. It
uses the common zero waveform because every released case shares one inlet
waveform and the referenced file is absent. No boundary-condition
generalization is claimed. The only numerical stabilization clamps undefined
`log(0)` support.

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

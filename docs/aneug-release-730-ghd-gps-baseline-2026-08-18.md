# Release-730 GHD-GPS/GINE strong comparator

This comparator asks whether the released 432-D geometry descriptor plus a
mesh-local/global U-Net is a stronger geometry-to-cycle baseline than the
released Graph U-Net under the completed 584/73 protocol. It is a matched
reimplementation of relevant AneuG/RHSIA ingredients, not an exact RHSIA
reproduction and not the proposed method.

The network uses physical coordinates, recomputed mesh normals, relative
vertex area and train-standardized GHD coefficients. GINE-style local blocks
operate at the fine and middle resolutions, exact attention operates only on
the coarsest registered mesh, and one forward pass emits all 80 Cartesian WSS
phases. Pure PyTorch blocks replace PyG, torch-scatter, Performer and
PyTorch3D; no 14,000-case steady augmentation or separately reconstructed
cotangent encoding is used. These differences must remain explicit.

Training uses only train-derived GHD statistics and physical vector-WSS scale.
Checkpoint selection uses the 73-case validation field metric. Predictions are
evaluated in raw released physical Cartesian space, without hard tangent
projection, phase-boundary closure or an absolute pass threshold. TAWSS, OSI,
mean-vector, low-TAWSS, peak-phase and mesh-normal component errors are derived
from the same predicted field. The locked 73-case test and 79 processed-only
extras remain unread.

One seed is development evidence. The job is deliberately non-executable
until the currently running released-class Graph U-Net has a preserved
terminal record and a fresh private activation binds that record, the
Quality-passed source, split manifest and train audit. It is prioritized ahead
of Transolver and all proposed-method ablations because a credible direct
strong comparator is needed before architectural claims are meaningful.

Before field access, the shared loader now recomputes the exact stored
validation order and requires `aac001b3...d4dc30`; terminal results emit both
case-set and ordered-loader digests. Checkpoint and terminal-status writes are
atomic. The earlier activation predates this correction and is superseded for
execution provenance; a fresh activation is required after the response
oracle terminates. The activation must contain a valid response-oracle terminal
record SHA-256, and the runner recomputes that SHA-256 from an explicitly bound
read-only terminal-record file before any data load. This enforces the serial
order in code rather than relying only on the operations log.

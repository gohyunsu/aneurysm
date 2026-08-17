# D11 official-style strong-baseline adaptation

D10 showed that extending the original custom scalar--vector backbone's
optimization horizon materially improves its validation field accuracy but
does not satisfy the frozen feasibility gate. Applying a cycle-functional
readout to that backbone would confound a weak base predictor with the proposed
interface. D11 therefore changes the backbone before any functional method is
trained.

The released AneuG source contains GraphGPS/GINE modules, but the exact RHSIA
training route is not fully exposed by the public trainer. The pinned introai9
runtime also contains neither PyG/torch-scatter nor PyTorch3D, and the current
cache does not contain the separately reconstructed cotangent encodings used by
the released module. D11 is consequently a matched reimplementation, not a
reproduction. Its traceable shared elements are Cartesian geometry/normal
inputs, GHD conditioning, edge-conditioned local messages, global attention,
a graph U-Net hierarchy and direct vector-WSS supervision. Declared differences
are pure-Torch scatter, exact attention only on 869 coarse vertices, use of the
cached 432-D GHD vector, full-cycle output and no steady-data augmentation.

One validation-development job reuses the exact 406/51 cache and seed 1103. It
uses a 251-epoch StepLR schedule anchored to the direct-prior setup, early
stopping only after epoch 80, and the unchanged area-weighted field metric and
0.35 feasibility gate. A pass permits separate registration of a same-backbone
cycle-functional readout; it does not authorize that method, multi-seed
confirmation, outer access or a paper claim. A failure remains useful evidence
and may motivate a new-ID, explicitly diagnosed iteration under the current
flexible rerun policy. Numeric results stay private.

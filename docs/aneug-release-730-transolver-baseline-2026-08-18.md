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

Execution requires the released Graph U-Net terminal record and a fresh
private activation. GHD-GPS/GINE and the response oracle are normally
prioritized before this control, but they are not hard prerequisites: their
terminal hashes are recorded when available, and the order may change after a
diagnosed infrastructure or evidence update. This preserves one-GPU serial
execution without turning a planning preference into an arbitrary permanent
gate. One seed remains validation development; multi-seed confirmation and the
locked test are separate later stages.

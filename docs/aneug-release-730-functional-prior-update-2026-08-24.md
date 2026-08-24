# Release-730 functional-fidelity direct-prior update · 2026-08-24

**Status:** primary-source literature audit only. This update changes no data,
split, model, activation, GPU job, result or sealed scope.

## Why this update matters

The active question is not whether an aneurysm surrogate can generate a
cardiac-cycle field. That task and most obvious architectural ingredients are
already occupied. The remaining paper claim must be narrower and must be
earned by matched evidence.

## Direct-prior boundary

| Source | What it already establishes | Consequence for AURORA |
|---|---|---|
| [AneuG-Flow](https://papers.neurips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf) | 14,000 steady and 730 pulsatile CFD cases, registered surface WSS, one common transient inlet waveform and steady Graph U-Net baselines | Dataset scale, registration and geometry-to-WSS learning are not contributions. |
| [Sheng et al. v2](https://arxiv.org/html/2601.19876v2) | GHD/GPS transient vector-WSS prediction, complete-sequence decoding, mixed steady/transient supervision, a separately predicted steady-WSS FiLM prior, a 512-mode surrogate, label-efficiency and post-hoc TAWSS/OSI/RRT evaluation | Steady augmentation, steady anchoring, sequence or modal decoding, label-efficiency and derived-functional reporting are direct prior art. |
| [Garnier et al. v1](https://arxiv.org/html/2512.09013) | Autoregressive full-cycle aneurysm flow prediction with derived WSS/TAWSS/OSI; lower OSI accuracy is attributed to near-wall directional fluctuations under an overall-flow objective, and shear-metric multi-task supervision is named as future work | The domain failure motivation and the obvious remedy of adding shear-metric supervision are already anticipated. A functional loss alone is not novelty. |
| [Kheiri et al.](https://doi.org/10.1016/j.cjph.2026.04.015) | POD with Transformer/LSTM for pulsatile cerebral-aneurysm hemodynamics in six normal/dilated patient-specific MCA cases | POD or reduced-order temporal prediction is not a novel component. The small intervention-specific study is context, not a matched AneuG comparator. |
| [PaNO](https://arxiv.org/abs/2606.03038v1) | Generic field/readout mismatch and readout-aligned optimization in another PDE domain | The broad claim that accurate fields can miss downstream endpoints is not AURORA novelty. |

Garnier et al. and the peer-reviewed Lannelongue et al. study are related but
not interchangeable records. The former uses a 51M sparse graph Transformer,
101 standardized pretraining geometries, 13 real fine-tuning geometries and a
MATCH validation set; the latter evaluates a smaller MeshGraphNet family on
105 semi-idealized geometries. Both narrow generic transient-aneurysm GNN
claims, while Garnier et al. states the OSI failure most directly.

## Residual claim and falsifier

The only defensible active proposition is:

> Under identical transient-only and leakage-audited steady-information
> conditions, a single decoded complete-cycle surface-WSS field with a
> train-output response/local representation and direct cycle-functional
> training improves physical field error, TAWSS and valid-support OSI together
> relative to strong same-target controls.

This is an application-specific mechanism-and-evidence claim, not a new-GNN,
new-POD or new-loss claim. It is deleted if any of the following holds:

- GHD--GPS or Transolver removes the apparent functional deficit;
- the response oracle does not support a useful train-output subspace;
- the candidate improves TAWSS/OSI only by paying a material field-error tax;
- a field-only or local-only matched control performs equivalently;
- the direction fails across fresh seeds or the one-time locked test; or
- the gain appears only with proposal-only steady information.

## Experiment consequence

No new baseline is added from this audit. The cited studies use different
volumetric targets, geometries, boundary-condition regimes or intervention
questions and are not fair drop-in AneuG comparators. Preserve the registered
serial ladder:

1. train-only response oracle;
2. GHD--GPS/GINE complete-cycle comparator;
3. full-cycle Transolver comparator;
4. bounded response/local/functional ablations;
5. selected control/candidate under matched T and T+S;
6. fresh-seed confirmation and one-time locked test.

The 13,985 eligible steady rows remain a matched information factor for the
selected control and candidate. They are not a novelty claim and are never
available only to the proposal.

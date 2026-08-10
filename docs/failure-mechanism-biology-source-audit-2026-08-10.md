# 2026-08-10 Failure-mechanism and biology source audit

## Decision

This is a fresh source-only audit, not a continuation or repair of the closed
Aneumo generation-lineage P0. Before comparing candidates, the admission rule
was fixed at eight 0--5 axes and 32/40: biomedical importance, target
identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value, and ISBI-schedule feasibility.

All six candidates remain below admission. The best, cause-specific
false-positive risk control for CTA aneurysm detection, scores **30.5/40**.
Active shortlist, selected primary problem, method, architecture, executable
P0, GPU training, outer test and submission identity therefore remain **zero**.
No image, mask, histology, spatial-transcriptomic, patient-table or
controlled-access payload was read. Scores are not repaired after the direct
prior and unit audit.

| Rank | Frozen candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Cause-specific false-positive risk control | 5.0 | 3.0 | 1.0 | 3.0 | 4.5 | 5.0 | 5.0 | 4.0 | **30.5** | reject |
| 2 | Post-release TopAneu attachment consistency | 5.0 | 3.0 | 2.0 | 2.5 | 4.0 | 4.5 | 5.0 | 3.0 | **29.0** | reject |
| 3 | Directional topology for small-lesion bifurcation errors | 4.5 | 4.5 | 0.0 | 2.0 | 3.5 | 5.0 | 5.0 | 3.5 | **28.0** | reject |
| 4 | Synthetic-avatar structural fidelity for rupture status | 2.5 | 5.0 | 0.5 | 5.0 | 1.0 | 5.0 | 2.0 | 4.5 | **25.5** | reject |
| 5 | Angiography-to-preclinical tissue-ingrowth translation | 4.0 | 3.5 | 0.5 | 1.5 | 2.0 | 5.0 | 5.0 | 3.0 | **24.5** | reject |
| 6 | Imaging-to-spatial wall-cell-state alignment | 5.0 | 1.0 | 2.5 | 1.0 | 1.5 | 3.0 | 5.0 | 2.0 | **21.0** | reject |

The ordering is by total score. The total is always the arithmetic sum of the
displayed cells. “Reject” means reject this candidate
version before data access or compute; it is not a judgment that the source
paper or dataset is poor.

## Candidate · Cause-specific false-positive risk control · 30.5/40

The strongest idea was to predict not only whether a candidate is false, but
which confounder generated it--extracranial background, vein, artery or
nonvascular tissue--and to abstain under an explicit per-cause risk budget.
This would make errors readable and could be evaluated as a selective decision
problem rather than another scalar detector score.

The [direct Scientific Reports study](https://www.nature.com/articles/s41598-025-33083-7)
already narrows the residual gap substantially. It trained CPM-Net and a 3D
CNN--Transformer on 1,186 open CTAs with 1,373 annotated aneurysms, evaluated
143 held-out private CTAs and 843 public RSNA CTAs, and manually categorized
false positives into extracranial, venous, arterial and nonvascular causes. Its
brain, artery, vein and cavernous-sinus masks removed many false positives with
small or dataset-dependent true-positive loss. This directly occupies anatomy-
compartment filtering and an interpretable cause taxonomy.

The key labels are not released as a public training target. The 143-case
reviewed set is available only from the authors on request. The public RSNA
evaluation used model-generated boxes because official supervision is point/
presence/location rather than aneurysm-extent boxes. The
[RSNA registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
also specifies controlled access, noncommercial use and no redistribution; no
terms were accepted on the user's behalf. A new calibrated head would therefore
choose a cause ontology without a public casewise reference, while the strongest
anatomy filter is already a direct baseline. This is an attractive evaluation
layer, not yet an independently identifiable ISBI method.

## Candidate · Post-release TopAneu attachment consistency · 29.0/40

The [current TopAneu page](https://topaneu-26.grand-challenge.org/) now states
open use with attribution, approximately 850 CTA/MRA scans, more than 50
vessel-specific classes, silver vessel masks and June 2026 training release.
It simultaneously requires a verified Grand Challenge account before joining.
The agent did not create or verify an account, request admission, accept terms,
or read images, NIfTI masks or JSON.

This is a useful source clarification but does not change the scientific
boundary of the earlier attachment audit. The benchmark directly defines
vessel-specific classification and segmentation. ARAN-style patient-specific
centerline graphs, vessel-distance attention, joint aneurysm/vessel heads,
anatomy prompts and hierarchical taxonomy losses remain direct controls. A
single attachment variable could still enforce mask--location consistency, but
the hard labels do not expose a reference distribution for ambiguous multi-
parent bifurcations. The new landing-page wording therefore improves source
clarity, not residual novelty or target identifiability enough to cross 32.

## Candidate · Directional topology for small-lesion bifurcation errors · 28.0/40

The July 2026 preprint
[*Shape Over Intensity*](https://arxiv.org/abs/2607.05317) already proposes the
Smooth Euler Characteristic Transform as a directional representation for
aneurysm--bifurcation discrimination on a stratified RSNA subset. It reports
small-lesion and leave-one-scanner-out analyses across four manufacturers.
Consequently, directional topology, persistence summaries, plug-in filtering,
small-lesion specialization and scanner-stratified validation are direct prior,
not a residual architecture proposal.

The exact curated candidate manifest and casewise error labels were not
identified as a standalone public asset, and RSNA access remains controlled.
Adding a GNN, persistent-homology branch, conformal wrapper or a new name would
not create an independent contribution. This candidate receives zero residual-
gap points precisely because the proposed method identity already exists.

## Candidate · Imaging-to-spatial wall-cell-state alignment · 21.0/40

The 2026
[human brain-aneurysm atlas](https://www.nature.com/articles/s41593-026-02326-9)
is biologically important. It profiles 227,663 neurovascular cells from 14
aneurysms and 11 control vessels; cell-resolution spatial transcriptomics uses
six unruptured aneurysm donors and three non-aneurysmal donors. The work links
smooth-muscle loss, activated perivascular fibroblasts and specialized
macrophages to wall remodeling. An interactive viewer and analysis code are
public, while sequencing is deposited in dbGaP.

The audited source does not release a casewise bridge from preoperative CTA/MRA,
aneurysm surface coordinates or CFD fields to the excised spatial section. Cell
counts are not independent patient units, and surgically acquired tissue is a
selected subset of aneurysms. Without paired imaging--tissue registration, an
image-to-cell-state model would learn a cross-cohort association or invent
spatial correspondence. The idea is visually strong and scientifically
important, but its target is not identified.

## Candidate · Angiography-to-preclinical tissue-ingrowth translation · 24.5/40

The [preclinical tissue-ingrowth study](https://www.nature.com/articles/s41598-026-43798-w)
trains a ResNet-50 U-Net++ on 64 high-resolution histology images and reports
strong sac and ingrowth segmentation. It publishes plugin code and a viewer,
but the datasets are available only from the corresponding author on reasonable
request. The paper already occupies automated sac/ingrowth segmentation,
quantification, expert agreement and an interpretable histology overlay.

A more ambitious idea would predict histologic healing from peri-procedural or
follow-up angiography. The source is a preclinical animal model and the audited
boundary exposes neither a public paired angiography--histology manifest nor a
human clinical outcome cohort. Histology images from the same animal are not
independent treatment responses. Cross-modal contrastive learning, U-Net++ and
generic domain adaptation cannot substitute for the missing paired endpoint.

## Candidate · Synthetic-avatar structural fidelity for rupture status · 25.5/40

The [ICAN public record](https://www.data.gouv.fr/datasets/dataset-to-develop-diagnostic-and-predictive-tools-addressing-ia-rupture-risk)
explicitly describes its downloadable clinical table as **simulated** and
provides Python/R notebooks under CC BY-SA for computational reproducibility.
It is not a newly released real cohort and contains no medical images.

The direct 2026 [CLEO study](https://www.nature.com/articles/s41746-026-02999-3)
already evaluates closed-loop synthetic tabular generation, privacy and
train-synthetic/test-real utility on 1,035 real multicenter aneurysm records.
It also states that empirical nearest-neighbor privacy audits are not formal
differential-privacy guarantees. AURORA cannot use an arbitrary number of
simulated rows as independent patients or as external clinical validation.
Generic tabular diffusion/GAN generation, privacy metrics and structural-
fidelity penalties are direct priors and are outside the current medical-image
identity.

## Consequence for model and experiments

There is no current GNN, U-Net, Transformer, neural operator, multimodal graph,
or foundation-model architecture. The most tempting paths fail for different
reasons:

- CTA error mechanisms: public casewise cause labels are absent and direct
  anatomy/topology filters already occupy the method.
- Wall biology: paired imaging--tissue coordinates and independent donors are
  insufficient.
- Healing: the public paired angiography--histology endpoint is absent.
- Synthetic clinical data: simulated rows do not create real patient evidence.

No candidate reaches 32, so no `introai9` P0 or GPU job is created. This is a
normal source-gate stop, not a server failure. The closed Aneumo lineage P0 is
not repaired or rerun. Future execution remains PBS-only on `introai9` after a
genuinely new or materially revised candidate passes source admission and a
separate method-free P0. `junjinyong` remains excluded from connection, query,
submission and monitoring.

# Context–treatment source audit

**Frozen decision · 2026-08-10 KST:** all five candidates are below the
unchanged **32/40** source-admission line. The strongest candidate,
ordered parent-vessel context sufficiency for cross-sectional rupture status,
scores **31.5/40**. It is rejected without score repair, VTK or spreadsheet
payload access, P0, method/architecture selection, PBS submission or GPU use.
AURORA therefore still has no active primary problem, model, outer test or
submission identity.

This batch was triggered by a genuinely new open AneuSI release, paired in-vitro
black-blood/4D-flow MRI treatment records, DIVA-seg and a public latent-shape
implementation. The question is not whether these resources are useful. It is
whether their *residual* problem—after direct prior work and the effective
independent unit are accounted for—supports a distinct ISBI method paper.

## 1. Frozen candidate screen

The eight axes are scientific importance, target identifiability, residual
novelty, asset readiness, effective independent unit, strong-baseline
feasibility, interpretable-figure value and schedule fit, each scored 0–5.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Ordered parent-vessel context sufficiency for rupture status | 4.0 | 4.5 | 0.5 | 5.0 | 4.0 | 5.0 | 5.0 | 3.5 | **31.5** | reject |
| Paired black-blood-to-4D-flow treatment response | 4.5 | 4.0 | 0.5 | 4.5 | 0.5 | 5.0 | 5.0 | 3.5 | **27.5** | reject |
| Device-conditioned counterfactual treatment selection | 5.0 | 2.5 | 1.0 | 4.5 | 0.5 | 4.5 | 5.0 | 3.0 | **26.0** | reject |
| Morphology-decision-preserving TOF segmentation | 4.5 | 4.0 | 0.5 | 1.0 | 4.0 | 5.0 | 5.0 | 3.0 | **27.0** | reject |
| External latent-shape calibration | 4.0 | 3.5 | 0.5 | 4.0 | 4.0 | 5.0 | 5.0 | 4.0 | **30.0** | reject |

The 31.5 is not rounded to 32, supplemented with an unrelated candidate or
used to reopen the closed AneuX preprocessing-orbit version.

## 2. AneuSI: excellent open context orbit, occupied endpoint

The [AneuSI paper](https://doi.org/10.1016/j.cmpb.2026.109525) reports automatic
aneurysm/neck isolation for 102 aneurysm cases from 99 patients. Seven clipping
factors produce 714 isolated models and 2,592 cuts. The official
[MIT-licensed implementation](https://github.com/grupomoccai/AneuSI) is pinned
for this audit at commit `5b4c454ede46c4cd56d3831cb24748c7e1521eca`
and tree `21ee76c85c1ddb00961879d737b5c994dbc3b711`; its bundled Aneurisk data
declare CC BY-NC 3.0.

This creates a useful *ordered same-case context orbit*: a local sac and neck
can be compared with progressively longer parent-vessel context without
pretending that the cuts are independent patients. That design is ideal for an
ablation of context sufficiency and produces interpretable surface figures.
It is not, by itself, an independent method contribution. Size ratio and parent-
vessel morphology are classical rupture correlates; point-cloud rupture models
already isolate aneurysm plus parent vessel; semantic vessel graphs already
combine local vascular structure and rupture classification. A 2026 autonomous
CTA pipeline additionally reports aneurysm/parent-artery morphology at much
larger clinical scale. Generic crop tokens, hierarchical pooling, graph context
or an E(3)-equivariant encoder do not create a new estimand.

There is also a frozen asset-risk flag. The paper reports 102 cases, while the
repository tree and `examples/cases.txt` expose 103 named model, centerline and
automated-neck entries; two `C0074` variants are present and the audited tree
metadata show duplicated model content for that pair. This may be an intentional
variant, but no case-level spreadsheet was opened to resolve it. The audit read
only repository metadata and the small case-name file. It did **not** open the
179,570-byte spreadsheet or any VTK member. The source discrepancy is not
silently repaired and does not authorize a P0 below the score line.

## 3. Paired treatment MRI: strong physical pairing, two anatomies

The 2026 [Communications Medicine paper](https://doi.org/10.1038/s43856-026-01413-z)
studies black-blood MRI and 4D-flow MRI after flow-modulating treatment in vitro.
The public [4D-flow record](https://doi.org/10.5281/zenodo.17183575) contains 33
datasets and the [black-blood record](https://doi.org/10.5281/zenodo.17191239)
contains 38 datasets. Both describe five models derived from only two patient
anatomies and 15 devices.

Within a physical model, device state and modality are valuable paired controls.
They do not provide 33 or 38 independent patients. The accompanying paper already
uses both modalities to quantify treatment effect, so modality-to-modality
response prediction has only 0.5/5 residual novelty. Counterfactual treatment
selection is not identified either: there is no clinical action policy,
longitudinal occlusion/recanalization outcome or many-anatomy treatment series.
No 23.2-GB 4D-flow archive or 3.4-GB black-blood archive was downloaded.

## 4. DIVA-seg: morphology-aware evaluation is direct prior

The [DIVA-seg paper](https://doi.org/10.3174/ajnr.A9231) reports 57 labeled
training, 14 test, 518 unlabeled and 82 external labeled TOF-MRA cases. It
explicitly evaluates whether pseudo-label training preserves clinical 3D
morphometry and reports proportional bias for volume, surface area, sphericity
and shape index. This is exactly the distinction that would make segmentation
more useful than a Dice-only paper, but it also directly occupies the proposed
decision-preserving evaluation. No audited public image/mask payload was found,
so a new executable candidate cannot be built from the paper counts alone.

## 5. Latent shape: public control, not residual novelty

The 2026 [latent-shape paper](https://doi.org/10.1016/j.cmpb.2026.109445)
reports 958 aneurysm surfaces and a two-dimensional deep latent space for
reconstruction, synthesis and rupture-label classification. Its
[public code and weights](https://github.com/PepeEulzer/aneurysm-latent-space)
make a strong direct control, but the source meshes are not bundled in the
audited repository. External calibration, VAE replacement, equivariant latent
encoding or uncertainty attached to this representation does not supply an
independent endpoint. A public implementation is not equivalent to a public
external patient cohort.

## 6. Decision boundary

- AneuSI is catalogued as a source-level context/control asset, not as an active
  training cohort or a repair of the closed AneuX preprocessing-orbit candidate.
- Parent-vessel context, size ratio, semantic vessel graphs, point-cloud rupture
  classification, generic crop consistency, latent shape, paired modality
  regression and morphology-aware segmentation metrics are direct priors or
  controls—not contribution statements.
- No spreadsheet, VTK mesh, MRI archive, model weight or patient image was
  opened or downloaded in this audit. No executable P0 is registered because
  the best score is 31.5/40.
- Consequently there is no PBS or GPU experiment to run or monitor. This is a
  source-gate early stop, not a server failure.
- Any future AURORA execution remains restricted to `introai9` PBS.
  `junjinyong` is excluded from connection, query, submission and monitoring.
- Only a materially new source/task unit may receive a fresh score. The current
  candidate is not repaired by counting cuts or device scans as patients.

The negative result is useful: it prevents a visually attractive context or
treatment architecture from becoming a paper whose novelty is only a renamed
combination of already published components.

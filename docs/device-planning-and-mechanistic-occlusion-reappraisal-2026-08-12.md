# Device planning and mechanistic occlusion reappraisal

**Date:** 2026-08-12  
**Decision:** reject all six fresh formulations; active lead, P0, method and compute remain zero  
**Latest best:** 26.5/40; no candidate satisfies the prospective non-compensatory gate

## Executive judgment

Two recent sources materially narrow the apparent gap between aneurysm imaging
and treatment. The July 2026 NeurAneuNet study already maps pre-operative 3D
rotational angiography to Pipeline Embolization Device (PED) size and landing
zones, and evaluates AI-assisted planning with clinicians. The May 2026
device-thrombosis preprint already couples coiling, flow diversion and
stent-assisted coiling to acute fibrin formation, contrast transport and
virtual DSA.

Together they make a tempting paper identity—"add hemodynamics to device
planning"—scientifically insufficient. The meaningful residual question is
stronger: can a planned intervention be selected for a patient-level,
prospectively defined outcome rather than merely imitate a deployed device or
simulate one assumed mechanism? That question is important and potentially
novel, but no public, versioned asset presently joins pre-operative 3D imaging,
device geometry and placement, post-device hemodynamics or thrombus, and
long-term occlusion or safety at the patient level. Architecture cannot repair
that missing estimand.

## What NeurAneuNet actually establishes

The exact primary source is [Wen et al., 2026](https://doi.org/10.1002/cns.71047)
(PMID `42484549`, PMCID `PMC13390615`, published 2026-07-22). Its reported
development material is counted in aneurysms/cases:

| source partition | reported unit | role |
|---|---:|---|
| non-PED subset | 390 aneurysms | segmentation and parent-vessel measurement |
| PED-treated subset | 210 aneurysms | measurement validation and PED planning |
| PED train / validation / test | 147 / 21 / 42 cases | device size and landing-zone models |
| clinical reader cohort | 21 cases | six-reader AI-assistance experiment |

The public article does not explicitly establish that the 147/21/42 split is
patient-disjoint. AURORA therefore preserves the reported case counts without
silently converting them to unique patients.

The clinical cohort is useful but its target is bounded. Three senior
neurointerventionists defined the reference PED by consensus after considering
post-operative device wall apposition, length and diameter. The source reports
top-1 agreement of 20/21 (95.2%), a 44.8% planning-time reduction and NASA-TLX
reduction from 33 to 21. These are source results, not AURORA results. The
reference is expert-consensus deployment adequacy; it is not randomized
treatment benefit, durable occlusion, retreatment, complication or patient
utility.

The authors themselves state that the data come from one institutional
healthcare system, only Pipeline Flex/Shield are represented, hemodynamic
simulation is absent, and post-procedural safety and long-term occlusion were
not evaluated. Data are not public and require author request, ethics approval
and a data-use agreement. The inspected paper states no public source-code
release. U-Net++, attention, WGAN, knowledge graphs, tensor decomposition and a
KAN are consequently direct-prior components, not an AURORA novelty menu.

## What the device-thrombosis source actually establishes

The exact source is
[Holzberger et al., arXiv:2605.03536v1](https://arxiv.org/abs/2605.03536).
It combines:

- device-resolved coiling, flow diversion and stent-assisted coiling;
- pulsatile hemodynamics and an acute fibrin/porosity model;
- contrast-agent transport and projection-based virtual DSA;
- treatment comparisons on three representative Flow Diverter 2016 challenge
  geometries.

This is a strong direct prior for mechanism-aligned occlusion and clinically
familiar virtual angiographic assessment. It is not a statistical patient
cohort: there are three geometries, treatment configurations are repeated
within geometry, and the modeled clot covers the first minutes after device
placement. The manuscript discusses missing endothelial, anticoagulant and
long-term biological mechanisms and presents no clinical follow-up validation.
The inspected v1 manuscript has no data- or code-availability section and no
versioned simulation-output release link.

The source also sharpens, but does not activate, the surface-vector hypothesis.
Its observation that stable **volume-flow vortices** can influence modeled
fibrin formation is physical motivation for structure-aware evaluation. It does
not establish that signed **surface-WSS critical points**, their cardiac-cycle
worldlines, or any particular Hodge representation are stable, causal or
predictive of thrombus. Volume vortex organization and wall-tangent vector-field
topology must not be treated as interchangeable evidence.

## Why the obvious public bridges are still insufficient

Existing public fragments do not form a joined confirmatory cohort:

- the paired 4D-flow/black-blood MRI releases contain 33 and 38 datasets but
  only two source patient anatomies and five models, four of which modify one
  basilar parent anatomy;
- the public flow-diversion table contains 126 subjects and 141 procedures but
  no versioned joined pre-operative 3D image, deployed device field and
  long-term image outcome contract;
- the three virtual-thrombosis geometries are mechanistic demonstrations, not
  patient-disjoint development and confirmation sets;
- NeurAneuNet's clinically rich 3DRA/device material is request-only and its
  endpoint is expert-consensus device planning rather than durable benefit;
- MARTA and other clinical outcome models already occupy generic
  treatment-specific risk prediction without releasing the required joined
  image/device/outcome rows.

Multi-source pretraining would not solve this. Dataset identity is confounded
with modality, device, geometry family, acquisition protocol and target, so a
network could learn source membership while appearing to learn intervention
response.

## Prospective non-compensatory screen

Axis order is importance, identifiability, residual novelty, asset readiness,
effective independent unit, strong-baseline feasibility, interpretable
evidence and ISBI schedule fit. Admission requires total at least 32 and all
critical floors. A large total cannot compensate for a missing target or
patient-level asset.

| candidate | axis scores | total | decision |
|---|---|---:|---|
| Paired in-vitro multi-device response ranking | 5 / 4 / 1 / 3 / 1 / 4.5 / 5 / 3 | **26.5** | Two source anatomies; direct paired-MRI analysis already exists |
| Selective certificate for expert-consensus PED planning | 5 / 4 / 1.5 / 0.5 / 1 / 5 / 5 / 3 | **25.0** | Generic calibration plus no public planning rows or external action target |
| Mechanistic clot-to-virtual-DSA surrogate | 5 / 5 / 0.5 / 1 / 1 / 4 / 5 / 3 | **24.5** | Task directly occupied; three geometries and no released output cohort |
| Expert imitation versus outcome-optimality audit | 5 / 3.5 / 2.5 / 0.5 / 1 / 4 / 5 / 3 | **24.5** | Meaningful estimand, but no joined outcome asset |
| Surface-flow structure as a clot-organization predictor | 5 / 2.5 / 2.5 / 1 / 1 / 4 / 5 / 3 | **24.0** | Surface endpoint is unverified and matched clot/WSS data are absent |
| Outcome-grounded counterfactual PED planner | 5 / 4 / 3 / 0.5 / 1 / 3 / 5 / 2 | **23.5** | Potentially novel, but treatment counterfactual is unidentified |

Scores are frozen and will not be repaired upward. The strongest residual
novelty belongs to an inoperable counterfactual target; the highest executable
score belongs to a two-anatomy phantom study. Neither is an active lead.

## Minimal future evidence contract

A future version may re-enter only with a lawful, versioned cohort that exposes
all of the following at the same patient and lesion unit:

1. pre-operative 3D angiography and parent-vessel/aneurysm geometry;
2. exact device family, size, deployment and landing-zone representation;
3. a registered early post-device flow, contrast or thrombus observation;
4. a prospectively defined delayed occlusion, retreatment or safety endpoint;
5. patient-disjoint development and fresh confirmation, with device and center
   shift declared in advance;
6. clinically meaningful comparators: expert planning, geometry-only planning,
   deployment simulation and outcome prediction;
7. a falsifier showing whether hemodynamics changes decisions beyond geometry
   without degrading calibration or patient-level safety.

Only that source change could open a method-free asset P0. It would still not
authorize a model, architecture or GPU run.

## Final operational decision

- Active lead, shortlist, primary problem, P0/P1, method, architecture, outer
  test, result row and manuscript claim remain zero.
- NeurAneuNet and device-thrombosis/virtual-DSA are added as direct priors.
- Outcome-grounded device planning remains a future evaluation template, not a
  paper identity.
- Surface-vector remains an inactive hypothesis; no material E0 or observed
  field-error-matched structure failure was found.
- No medical-image, spreadsheet, model, simulation output or archive payload
  was downloaded in this update.
- No scientific server was queried and no job was created.

Future gate-authorized execution is restricted to `introai9` PBS. Login-node GPU
commands are prohibited. `junjinyong` was not and must never be accessed,
queried, used for transfer, submitted to or monitored.

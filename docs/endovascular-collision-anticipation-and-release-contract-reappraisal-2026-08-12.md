# Endovascular collision anticipation and release-contract reappraisal

**Decision date:** 2026-08-12  
**Decision:** reject all six fresh formulations; open no terms acceptance,
payload, P0/P1, method, architecture, scientific-server query, PBS/GPU job,
outer test or paper claim.

## Executive judgment

The clinically meaningful residual question is not whether a catheter--wall
collision can be recognized after it is visible, but whether a system can warn
before first contact with enough lead time to change an action. That distinction
is real. It is not, however, identified by the current public CathAction
contract.

The source paper already benchmarks catheter action anticipation, current-frame
collision detection, catheter/guidewire segmentation and phantom-to-animal
domain adaptation. The 2026 CATHACTION challenge explicitly invites
cross-domain, joint and foundation-style methods for segmentation and collision
detection. Architecture naming or combining those tasks is therefore not a
residual contribution.

The exact public Hugging Face revision contains four large archives, but the
dataset card describes collision data as image/label paths with phantom
training and phantom/animal validation. It does not declare chronological
collision-onset sequences, warning horizons, animal/specimen/anatomy identities
or a human collision split. Action annotations have video IDs and temporal
segments, but are held in a different archive and no immutable action--tool-
mask--collision join is declared. The new human archive is segmentation-only
in the public file name and card. Thus a pre-contact warning target cannot be
constructed prospectively from inspected metadata without opening an
unapproved archive and inventing unit semantics.

The best score is 26.5/40. One row has residual novelty 3.0/5, but fails target,
asset and independent-unit floors. A novel-sounding question without a
timestamped event contract is not an experiment.

## 1. Exact source state

The original [CathAction paper](https://arxiv.org/abs/2408.13126) reports 569
videos, approximately 500,000 annotated frames for action understanding and
collision detection, and about 25,000 catheter/guidewire segmentation masks.
Its two acquisition domains are silicon phantoms and live animals. It directly
benchmarks five task families:

- catheter action anticipation;
- action recognition;
- catheter and guidewire segmentation;
- collision detection;
- phantom-to-animal domain adaptation.

The [2026 challenge page](https://endomiccai.github.io/cathation/) describes
more than 600,000 frames and names phantom, animal and human X-ray domains. It
focuses on tool segmentation and collision detection and invites domain
generalization, adaptation, joint learning and foundation-style approaches.
The inspected submission description specifies only a NIfTI segmentation
output contract; a collision-warning or time-to-event output interface is not
declared. This is an unresolved public interface, not a claim that the future
challenge evaluation is invalid.

The exact [Hugging Face release](https://huggingface.co/datasets/airvlab/CathAction)
at `8b04056f0f4fa4b04d8454728f000730af0d5560` was last modified on
2026-05-18. Official API metadata says public, `gated=false`, license tag
CC BY-NC-SA 4.0 and 56,678,352,136 used bytes. The card nevertheless asks the
user to complete a download form and agree to the license before download.
AURORA did neither.

The immutable four-file LFS manifest is:

| Archive | Bytes | LFS SHA-256 | Last material commit |
|---|---:|---|---|
| `collision_detection.zip` | 4,349,341,729 | `e8f89936903ba0efef72c23c9bcb2322ac89999a338a5dd9d9042bf5fcdedb77` | 2024-10-30 |
| `segmentation_animal_phantom.zip` | 9,882,697,706 | `c92d69b5dda2948fca4c47637a7c4800dfdaa323120d409a8fb8e9ece0e02c35` | renamed 2026-05-18 |
| `segmentation_human_train.zip` | 143,049,194 | `087c8f971e0455ad67d092a944df75ee7244cbead10e1091c26046ea271e2cf5` | renamed 2026-05-18 |
| `video_action_understanding.zip` | 41,808,377,811 | `d6333df4f526d22b8de8fe7faf7a627d3c3c3298675ee54ab3779e91639acee9` | 2024-10-30 |

No archive body, central directory, image, label, feature or patient record was
opened. The release is material, but public metadata do not establish the
independent experimental unit or cross-archive identity.

## 2. Detection is not anticipation

Current-frame collision detection asks whether contact is visible now.
Pre-contact anticipation asks whether first contact will occur after a declared
lead time using only frames available before that time. A valid warning task
needs at least:

1. an ordered sequence ID and acquisition frame rate;
2. a prospectively defined first-contact onset and ambiguity rule;
3. observation, buffer and warning horizons fixed before model development;
4. negative risk windows from complete no-collision sequences;
5. specimen/anatomy/procedure grouping so adjacent frames never cross splits;
6. a policy metric penalizing late, repeated and premature alarms;
7. untouched domain- or specimen-held-out confirmation.

The action archive's `video_id`, `start_frame` and `stop_frame` fields support
action anticipation. The collision card instead declares image paths and
bounding-box labels. Metadata do not prove that collision samples retain the
complete pre-onset temporal context or map to the action videos. Treating file
names or neighboring frames as independent examples would inflate evidence and
could leak one event across development and validation.

## 3. Human segmentation does not create human collision evidence

The 143,049,194-byte human archive is named
`segmentation_human_train.zip`. No public case count, patient/procedure ID,
centre, acquisition protocol, expert-reference process, validation split or
collision label is declared in the inspected card. It may be useful for the
challenge's segmentation task after lawful access, but it cannot be counted as
a human collision-warning cohort.

Similarly, a tool mask does not identify the vessel wall, contact force or
clinical injury. A thin guidewire touching a projected boundary in fluoroscopy
is not automatically a 3D wall collision. A future paper must keep visible
contact labels, physical force, perforation and patient harm as separate
constructs.

## 4. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at
least 32 and every critical floor.

| Candidate | Axis scores | Total | Binding rejection |
|---|---:|---:|---|
| Pre-contact collision-onset anticipation | 5.0/2.0/3.0/2.5/1.0/5.0/4.5/3.5 | **26.5** | No declared chronological collision onset, horizon or independent sequence unit |
| Phantom-to-animal collision calibration | 4.5/4.0/0.5/3.0/1.5/5.0/4.0/4.0 | **26.5** | Current collision/domain-adaptation task is direct prior; specimen grouping absent |
| Human tool-segmentation domain generalization | 4.0/4.0/0.5/3.5/1.0/5.0/4.0/4.0 | **26.0** | Challenge directly occupies task; human case/unit/split contract absent |
| Action-conditioned collision early warning | 5.0/1.5/2.5/2.0/1.0/5.0/4.5/3.0 | **24.5** | No immutable action-video to collision-event identity join |
| Segmentation-conditioned collision detection | 4.5/2.0/1.0/2.5/1.0/5.0/4.5/3.5 | **24.0** | Separate archives do not establish paired mask/contact reference |
| Aneurysm-specific navigation-safety transfer | 5.0/0.5/3.0/0.5/0.5/4.0/4.5/2.0 | **20.0** | No intracranial-aneurysm anatomy, procedure or outcome target is declared |

The 26.5 tie illustrates two distinct failure modes. Pre-contact warning has
some conceptual novelty but no identifiable event asset. Cross-domain
collision calibration has a more executable label but is already a source
benchmark and lacks independent-unit semantics.

## 5. Material re-entry contract

Only a new versioned release may request a fresh audit, and only if it declares:

- complete chronological collision sequences with frame rate and first-contact
  onset/adjudication;
- stable procedure, specimen, anatomy and domain identifiers;
- action, tool mask and collision labels joined by immutable sequence/frame ID;
- train/validation/test split grouped above the frame and event level;
- complete collision-negative sequences;
- a lawful human collision cohort or an explicit phantom/animal-only claim;
- fixed warning horizons and event-level early/late/false-alarm metrics.

The first authorized experiment would be method-free: verify event counts,
onset stability, risk-window construction, grouping and trivial motion/history
baselines. A pass would not select a network. Only a stable baseline failure
could open bounded validation-only development of the smallest mechanism-linked
temporal model.

## 6. Operational boundary

- Download form and license acceptance: **not completed**.
- Archive/image/label/feature/patient payload access: **zero**.
- Active lead, primary problem, P0/P1, method, architecture, scientific-server
  query, PBS/GPU job, outer test, result row, C21 and claim: **zero**.
- The four-file exact release state is watch-only. A change can request a
  manual source audit, never automatic download or model selection.
- Historical surface-vector job `115645.ECE-util1` remains immutable
  execution-incomplete/no-verdict and is not repaired or rerun.
- Future gate-authorized work is `introai9` PBS-only with no login-node GPU.
- `junjinyong` must never be accessed, queried, transferred to, submitted to or
  monitored.

## Primary sources

- CathAction paper: <https://arxiv.org/abs/2408.13126>
- CATHACTION 2026 challenge: <https://endomiccai.github.io/cathation/>
- Exact public dataset card: <https://huggingface.co/datasets/airvlab/CathAction>
- Surgical workflow anticipation direct prior:
  <https://doi.org/10.1109/TMRB.2024.3517137>
- Uncertainty-aware surgical anticipation direct prior:
  <https://arxiv.org/abs/2007.00548>

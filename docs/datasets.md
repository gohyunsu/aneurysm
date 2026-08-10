# 데이터셋 인벤토리와 통합 방안

> **Schema 6.6 Aneumo outcome · 2026-08-10:** The BC-transport P0 created only
> an execution-incomplete status. No aggregate records which members completed,
> which arrays parsed or whether coordinates/velocity responses were valid.
> Thus no fresh Aneumo asset semantics are claimed and no additional acquisition,
> P1, training, validation/test or GPU use is authorized. The historical pinned
> release and compact pilot remain provenance, not an active dataset role.

> **Schema 6.5 Aneumo role · 2026-08-10:** Aneumo is currently a conditional
> source-audit asset for same-geometry anchor-conditioned velocity transport.
> P0 may range-read only archive `1.zip`, historical train family 1/cases 1–2,
> all eight flows and 16 exact members. It may sample 1,024 aligned nodes and
> emit aggregate semantics, but may not persist fields, analyze pressure, read
> validation/test families, train a model or open an outer test. The historical
> 32-family compact pilot establishes the future split only; it is not a current
> training authorization. P0 is `introai9` CPU/PBS only.

> **Schema 6.4 TopAneu role:** Public code, mappings, evaluators, templates and
> checksum/path manifests were audited without reading medical members. The
> resulting method formulation is rejected at a fresh maximum of 31.5/40, so
> TopAneu is not a current acquisition, training, validation or outer-test
> asset. User terms remain unaccepted, but even future acceptance does not
> reopen the rejected P0-R. Patient images/masks and patient location-JSON
> content remain unread.

> **TopAneu-26 material-release role · 2026-08-10:** Official public metadata
> describe 417 scans from 409 patients, 52-class location masks/JSON, 3-class
> type masks and organizer-predicted silver vessel masks, with UMCU reserved for
> testing. For AURORA this is currently a **terms-gated source candidate only**.
> The user has not explicitly accepted the download terms; no image, mask or
> location-JSON payload has been read. If terms are accepted, P0-R must first
> establish patient grouping, source/centre lineage, factor-map validity,
> empty/multiple same-leaf support, mask–JSON agreement and silver-label
> provenance. Silver vessels may be train-time privileged information only and
> must not be a test-time input. No P0/model/GPU/outer-test use is authorized.

> **Current outcome · 2026-08-10:** The exact `introai9` P0-v2a created no
> aggregate result, so completed HEAD/range counts and verified server-side
> bytes are unknown. Local discovery remains metadata-only evidence; no full
> object, reader or case ID was accessed. The candidate closes without v2b.

> **Current access boundary · 2026-08-10:** AneuG-Flow dataset commit
> `9dd418083899deddd93a67f9a6fca7a14304fa36` and official code commit
> `4a090a0f12538deef6fcea88b81afe78ce38152e` are pinned under CC BY-SA 4.0.
> Discovery read only metadata plus four exact 1 MiB ranges from the 9.63 GB
> steady and 23.74 GB transient objects. No full object, torch payload or case
> identifier was accessed; patient/case count, physical WSS recovery, 80-frame
> schema and topology remain unaudited. The next permitted action is the same
> bounded preflight on `introai9`, not training.

> **2026-08-10 4D-CTA AAA asset boundary:** Zenodo `19182978`은 CC BY 4.0,
> 단일 1,857,980,948-byte ZIP, 20 patient/3 centre와 환자별 2--10 cardiac
> phase를 보고한다. Wall/ILT surface, FE mesh, strain, tension, SII와 RSII가
> 포함되지만 phase·vertex·mesh node는 독립 환자 수를 늘리지 않는다. P01--P10은
> PRAEVAorta, P11--P20은 nnInteractive assistance를 사용해 centre/acquisition과
> processing이 부분 confounded하다. Metadata/article만 읽었고 ZIP/NRRD/VTP/INP
> payload는 0이다. 현재 역할은 **source-rejected future figure/reproducibility
> asset**, train/validation/test asset이 아니다.

> **2026-08-10 TopBrain 2.0 correction:** Zenodo revision 4 licenses the sole
> design PDF under `CC BY 4.0`; it does not provide or license medical images,
> masks or a casewise manifest. The challenge remains under construction with
> Join registration but without executable task navigation. Schema 6.0 and
> source-watch v2 preserve payload/P0/model/GPU at 0.

> **2026-08-10 TopBrain 2.0 asset boundary:** The official Zenodo record has
> one 139,840-byte design PDF and no verified patient image, vessel mask,
> aneurysm annotation, clinical table, split or held-out-test payload. Planned
> counts (Task 1: 215 train/123 test; Task 2: 315/183) are not available units.
> Aneurysm-bearing TopAneu volumes are planned robustness cases for vessel
> anatomy, not lesion labels. Current role: watch-only rejected source, never a
> train/validation/test asset.

> **2026-08-10 RSNA-ICA registry correction:** AWS registry metadata reports
> 4,000+ scans, 40+ radiologists, about 200 AI-segmented studies and 18
> institutions, but the bucket is `ControlledAccess` and no terms/request or
> payload access occurred. The wiki is still `Coming soon`; the registry says
> CT while public competition implementations use CTA/MRA/T1-post/T2, so exact
> release modalities and center/reader manifests remain unaudited. Supplied
> voxel masks are 13-class vessel anatomy, not aneurysm extent. Current role:
> source-only rejected candidate, not a train/validation/test asset.

> **2026-08-10 broad-registry asset boundary:** LargeIA는 공식 record상
> 1,338 internal CTA/1,489 aneurysm/6 institution과 138 external CTA/
> 101 aneurysm/2 institution의 voxel mask·age·sex·rupture status를 보고하지만
> restricted request가 필요하다. 사용자를 대신한 request/terms acceptance와
> payload access는 0이다. 2015 CFD Challenge는 five DICOM anatomy와 28 solver
> submissions/26 teams를 제공하지만 solver submission을 patient로 세지 않는다.
> Longitudinal SIG, aSAH hydrocephalus와 VWI public objects는 supplement/table이고
> synthetic DSA는 2026-10-31까지 embargo다. 어느 source에도 train, outer-test
> 또는 current-model role을 부여하지 않는다.

> **2026-08-10 registry-gap asset boundary:** Zenodo exact-title query 49건 중
> 새로 식별한 rupture-status record `7536330`/`7757069`는 각각 578,924,037/
> 2,321,552,713-byte test blob이지만 public development cohort, exact case
> lineage와 prospective endpoint가 없다. VWE Dryad/Zenodo는 41 unruptured
> aneurysm의 3,572-byte scalar table이며 image/wall-map/CFD field가 아니다.
> vortex-cfd는 cohort가 없는 software이고, transcriptomic record는 43 labeled
> post-presentation wall samples에서 시작하나 casewise CTA/MRA bridge가 없으며,
> autopsy record는 aggregate paper/PNG뿐이다. Metadata와 file manifest만 읽었고
> CSV/PKL/ZIP/image/mesh/field/RNA/patient payload는 0이다. 어느 source에도
> active training 또는 outer-test role을 부여하지 않는다.

> **2026-08-10 method--asset viability boundary:** Royal OpenNeuro exact
> `0760bf8…`은 63 patient/85 aneurysm의 image, mask와 STL을 제공하지만 mask와
> STL은 independent reference가 아니라 같은 annotation pipeline의 표현이다.
> AneuG-Flow dataset/code는 `9dd4180…`/`4a090a0…`, IAVS는 `2e40088…`으로
> unchanged이고 IAVS는 README-only다. RSNA는 controlled terms 미수락 및
> per-reader manifest 0, cited CQ500-IA public Git remote는 unresolved다. 새
> training role이나 payload access를 열지 않는다.

> **2026-08-10 current reconstruction/annotation boundary:** OpenNeuro
> `ds003949` lineage는 284 subject/198 aneurysm과 permissive data/code/weight를
> 보고하고 VP-UNet은 246 coarse-label subject와 38 precise-label test를 쓴다.
> 그러나 real weak/independent precise same-subject prospective manifest가 없어
> active training role을 부여하지 않는다. The 600-model study is available on
> request; raw sparse-view DSA projections and legacy biplane development assets
> are not public; PhantomX has one effective anatomy. No patient payload was
> read. All are rejected source history, not active datasets.

> **2026-08-10 current source boundary:** 새 batch에서 image, mask, reviewed
> FP-cause label, histology, spatial transcriptomics, patient table와 controlled
> payload를 읽지 않았다. RSNA와 TopAneu terms를 대신 수락하지 않았고, ICAN
> downloadable table은 simulated data다. Human spatial atlas와 preclinical
> ingrowth source에는 paired preoperative-image/tissue 또는 angiography/
> histology manifest가 없다. 이들은 source history이지 active training data가
> 아니다.

> **2026-08-10 Aneumo lineage audit:** 10,660 generated geometries map to 427
> base families. Official steady validation is case-disjoint but shares all 20
> base families with training. Aneumo's current role is therefore a pinned
> metadata-only historical P0 source, not training data. The exact P0 ended
> before its first small source completed, so no registered parser check ran.
> GitHub says CC BY 4.0 while the pinned Hugging Face card says CC BY-NC-ND 4.0.
> This candidate version is closed with no archive/member/LFS object, P1 or
> model authority.

> **2026-08-10 longitudinal-MRA growth audit:** OpenNeuro `ds005096`은 CC0,
> 63 patient/85 aneurysm/24 longitudinal patient와 126 raw angiogram path를
> 제공한다. 동일 session에 acquisition 두 개가 있는 independent subject는
> `sub-006`, `sub-013`, `sub-015`, `sub-028` 네 명이다. Expert derivative는
> subject당 한 selected session에만 있다. 2026 direct prior는 16 public
> patient/19 aneurysm/6 growth를 retained subset으로 사용했다. Git tree와
> `dataset_description.json`만 감사했고 annotation spreadsheet, participant
> table, sidecar, NIfTI, segmentation, Slicer/STL payload는 열지 않았다. 최고
> 31.5/40이며 training role/P0/model/GPU는 0이다.

> **2026-08-10 longitudinal-perfusion audit:** Dryad
> `10.5061/dryad.0zpc86784`는 CC0 version 7, 62 patient, 291 original exam과
> 873 MNI-normalized TMax/CBF/MTT map을 보고한다. 독립 clinical endpoint는
> DCI 9건이며 paper의 302 interpolated exam을 추가 patient로 세지 않는다.
> Figshare `10.6084/m9.figshare.1354056.v3`는 10 aneurysm의 2,516-byte summary
> CSV 하나, VWE Dryad `10.5061/dryad.p2ngf1vrg`는 41 unruptured aneurysm의
> 3,572-byte CSV 하나다. Official record/embedded README/file manifest만
> 감사했고 standalone JSON/XLSX/NIfTI/ZIP/CSV/image/mesh/field payload는 열지
> 않았다. 모두 rejected source history이며 training role/P0/model/GPU는 0이다.

> **2026-08-10 FSI–wall audit:** AnXplore의 논문 단위와 공개 파일 단위를
> 분리한다. 논문은 101 semi-idealized aneurysm에서 rigid와 FSI simulation을
> 비교하지만 official repository의 확인된 `full_dataset` tree는 101
> `Fluid_*.vtk` mesh를 노출한다. 이는 101 paired rigid/FSI time-resolved
> solution field가 아니다. `caseA`의 Fluid/Solid 예시는 schema 이해용 예시이지
> full paired target cohort의 증거가 아니다. Animal inverse-mechanics Dryad와
> five-aneurysm micro-CT thickness study도 source-only direct evidence이며 AURORA
> training role을 부여하지 않는다. Mesh, field와 image payload는 접근하지
> 않았고 최고 31.0/40, P0/model/GPU 0이다.

> **2026-08-10 acquisition–flow audit:** CMRx4DFlow2026 reports over 400 cases,
> 138 fully sampled training cases and cerebrovascular 10/20 validation/test
> cases, but access is challenge/Synapse-gated and independent research use is
> embargoed until December 2026. It is therefore watch-only for the current ISBI
> clock. Zenodo `10.5281/zenodo.14981710` reports 8 dual-VENC scans from 4
> printed states of one paraophthalmic aneurysm anatomy; scan count is not an
> independent-anatomy count. No CMRx or 6.2 GB aneurysm payload was accessed.

> **2026-08-10 treatment–surveillance audit:** Mendeley
> `10.17632/nzzx92ky6r.2` reports 126 subjects/141 flow-diverter procedures,
> complications and first/second DSA follow-up; it is a source-rejected treatment
> control because device assignment is observational and exact occlusion time is
> interval-censored. Zenodo `10.5281/zenodo.6654502` is a restricted 22-patient
> paired TOF-MRA source whose paper directly reports kappa 0.98. No spreadsheet,
> presentation, DSA/MRA or patient payload was accessed. Best score 30.0/40;
> P0/model/GPU 0.

> **2026-08-10 lineage rule:** AneuX의 Aneurisk 101 lesion, AneuriskData mirror의
> 24 named model folder와 새 CFD의 76 selected geometry는 source ancestry만으로
> 동일 case라 병합하지 않는다. Exact patient/lesion/acquisition/geometry/cut/
> resolution/derived-field manifest가 없으면 서로 다른 release의 near-isometric
> surface도 같은 lineage로 확정하지 않는다. 반대로 CFD pretraining과 rupture
> evaluation에 동일 lineage가 확인되면 naive split 결과는 unseen-geometry
> evidence로 사용하지 않는다. 이번 audit은 archive나 member payload를 열지
> 않았으며 active dataset role을 만들지 않았다.

> **2026-08-10 source-only additions:** AneuSI는 99 paper patients/102 reported
> cases, repository 103 named cases와 seven-clip same-case context orbit을 가진
> control asset이다. 102/103 mapping이 미해결이고 spreadsheet/VTK payload는
> 열지 않아 training cohort가 아니다. Paired treatment MRI는 33 4D-flow와 38
> black-blood datasets를 보고하지만 five models/two source patient anatomies다.
> Archive는 받지 않았고 repeated scan을 patient로 세지 않는다. 둘 다
> [`context–treatment source audit`](context-treatment-source-audit-2026-08-10.md)의
> rejected source history다.

> **2026-08-10 topology–procedure source audit:** Figshare
> `10.6084/m9.figshare.32270130.v2`의 README는 3 CFD WSS cardiac-cycle case와
> figure용 2 MRI case를 보고하지만 same-case pair는 없다. Three WSS archives
> 3,189,493,388 bytes, velocity archive 309,081,947 bytes와 MATLAB archive
> 10,059 bytes는 내려받지 않았다. Zenodo `17894703`은 1,167,744,043-byte
> MAXIMUS weights이지 source image/mimic-label dataset이 아니며 역시 받지 않았다.
> Rheology/slip v1.0.0은 one aneurysm `case01`이다. 다섯 후보가 모두 32 미만이라
> P0/model/GPU는 0이다. 상세 근거는
> [`topology–procedure audit`](topology-procedure-source-audit-2026-08-10.md)에 있다.

> **2026-08-10 hemodynamic–endpoint source audit:** Zenodo
> `10.5281/zenodo.19455127`은 76 Aneurisk geometry의 1.4 GB OpenFOAM-derived
> VTP surface fields, MD5 `8c66e7bb359d04bd1a5d6db6da3f3926`, CC BY 4.0을
> 보고한다. Inflow는 두 population age-group waveform을 inlet diameter로
> scaling한 것이며 실측 patient-specific BC가 아니다. Record의 zero-pressure
> outlet 요약과 paper의 resistance-pressure 조건도 일치하지 않는다. Curvature
> surrogate 31.0/40을 포함한 다섯 후보가 모두 32 미만이므로 archive/VTP를 받지
> 않았고 P0/model/GPU는 0이다. 상세 근거는
> [`hemodynamic–endpoint audit`](hemodynamic-endpoint-source-audit-2026-08-10.md)에 있다.

> **2026-08-10 PINN rupture-status direct-prior audit:** AneuX는 750 aneurysm
> domes, 668 vessel trees와 605 patients를 보고한다. 2026년 direct prior는 735
> labeled lesions에 geometry-conditioned PINN hemodynamics와 clinical fusion을
> 이미 적용했지만 primary split의 patient grouping, patient-specific BC와
> CFD/in-vivo validation은 확인되지 않는다. AneuX status와 synthetic CFD를
> 병합해 이 joint estimand를 만들 수 없다. Residual candidate는 23.5/40으로
> 기각됐고 payload/P0/model/GPU는 0이다. 상세 근거는
> [`direct-prior audit`](pinn-rupture-direct-prior-audit-2026-08-10.md)에 있다.

> **2026-08-10 vascular-semantics audit:** TopBrain 25 paired CTA/MRA patient,
> healthy IXI 100 MRA, VesselVerse source-reported 950 images, one-anatomy CTA
> phantom, NeckSpline-derived neck loops와 ADAM longitudinal metadata를 source-only로
> 비교했다. 최고 TopBrain도 29.5/40이며 target이 48-class anatomy이지 aneurysm
> endpoint가 아니다. VesselVerse는 email-request gated이고 “expert”에 algorithm
> output을 포함한다. Phantom data URL은 HTTP 404였다. Payload/P0/model/GPU는
> 0이며 상세 근거는
> [`vascular-semantics source audit`](vascular-semantics-source-audit-2026-08-10.md)에 있다.

> **2026-08-10 IAVS watch-only:** Paper metadata는 641개 3D MRA, 587개
> aneurysm–parent-vessel annotation과 CFD outcome을 보고한다. 그러나 official
> repository exact `2e40088…`은 README 한 파일, release 0, explicit license 0,
> payload/code 0이다. Dataset role이나 source score를 부여하지 않는다.
> [`source-watch`](source-watch.md)는 release 변화를 감지해도 fresh source audit만
> 요청하며 download, terms acceptance, P0, model과 GPU를 자동 허용하지 않는다.

> **2026-08-10 INSTED clarification:** Official Codabench는 published 2024
> challenge, CC BY-NC, 160 train(healthy/IA/stenosis 32/64/64)과 40 closed test를
> 확인한다. Train asset은 signup 뒤 Files에서 제공되며 이번 audit에서 signup,
> terms acceptance와 payload download는 하지 않았다. Challenge-design PDF의
> 5-year survival 문장은 template example이고 실제 label은 IA/stenosis box와
> segmentation이다. Historical IAIA score 26/40은 그대로다. 자세한 근거는
> [`INSTED source clarification`](insted-source-clarification-2026-08-10.md)에 있다.

> **2026-08-09 source-delta audit:** OpenNeuro longitudinal, RSNA controlled,
> VICTORIA, IntrA, IAIA와 flow-diverter sources를 source-only로 비교했다. 최고
> OpenNeuro growth도 31.5/40이며 public longitudinal unit 24와 동일 cohort direct
> prior 때문에 기각했다. RSNA terms는 수락되지 않았고, IntrA staging은 repository
> skeleton뿐이다. 어느 새 payload도 읽지 않았으며 active dataset role, P0,
> method와 GPU는 0이다. 상세 표는
> [`source-delta audit`](source-delta-audit-2026-08-09.md)을 따른다.

> **2026-08-09 DIAS source audit, rejected 31/40:** Official Zenodo v3는
> `DIAS.zip` 292,444,663 byte, MD5 `780f32df6fb2a5de5d476f385cf2e83b`,
> CC BY 4.0을 명시한다. 원 논문은 60 patient/120 DSA sequence, 60 fully
> annotated sequence와 4--14 arterial-phase frame을 보고한다. Summary의 753
> frame과 collection section의 762 image는 payload audit 전 unresolved다.
> Full-sequence/minimum-projection DSC는 0.7822/0.7802다. Dataset payload와
> identifier는 읽지 않았고 known `introai9` root에 staged DIAS asset도 찾지
> 못했다. Source score가 gate 미달이므로 P0, model과 GPU를 열지 않으며 향후
> 사용하더라도 patient-grouped external DSA segmentation baseline 역할뿐이다.

> **2026-08-09 AneuX preprocessing-orbit P0, execution-incomplete/closed:** Official AneuX v1.0은
> 750 aneurysm dome, 668 vessel tree, 605 source-reported patient, 3 mesh
> resolution, dome/ninja/cut1/cut2와 area-005 기준 170 morphometric feature를
> 기술한다. 637/750 row에 patientID가 보고된다. 현재는 record, file size/MD5와
> content-description만 확인한 뒤 exact P0를 `introai9` CPU/PBS에서 한 번
> 실행했다. Initial tabular transport가 bounded attempt를 소진해 complete/partial
> ZIP과 CSV parse는 0이고 model HEAD/range·central directory·mesh payload에도
> 도달하지 않았다. 13개 scientific check는 미평가이며 same-source repair/rerun,
> P1, method·GPU·outer test 없이 후보를 닫았다. AneuX status는 cross-sectional
> association일 뿐 prospective rupture risk가 아니다. Official GitHub README의
> CC BY 4.0 표기와 Zenodo v1.0 배포 record의 CC BY-NC 4.0+추가 attribution
> 조건이 충돌하므로, 실제 파일 배포 record의 더 엄격한 조건을 적용한다.

> **2026-08-09 AneuG-Flow closed P0:** Current dataset commit
> `9dd4180…`의 processed steady/transient 두 파일 identity와 CC BY-SA 4.0
> license를 source-only로 확인했다. Transient assembled object는 steady
> `tensor_norm`에 의존하므로 두 archive를 하나의 physical-WSS recovery pair로
> 다룬다. Dataset page/NeurIPS paper의 730 pulsatile case와 RHSIA의 808은 같은
> release라고 가정하지 않는다. Exact CPU-only P0는 exit 28로 종료됐고
> processed/partial payload와 aggregate가 0이어서 schema, count, geometry,
> topology와 normalization gate는 미평가다. Repair/rerun이나 P1은 없으며
> candidate를 닫았다. Synthetic geometry case를 patient로 세거나
> source waveform을 patient-specific physiology로 부르지 않는다.

> **2026-08-09 inverse-counterfactual source audit:** Current Aneumo의
> `Connection.csv`/`MPs.csv`와 pinned 64-case cache는 base-family deformation과
> aneurysm morphometry를 제공하지만 released healthy counterpart·ostium/edit
> pair를 식별하지 않는다. 초기 10,000-model preprint의 aneurysm-free count를
> 현재 10,660-geometry release에 소급하지 않는다. IntrA의 103 whole-vessel
> model/116 annotated local segment도 real healthy counterfactual 정답이 아니며
> repository license가 명시되지 않았다. 따라서 inverse healthy-vessel editing은
> 27.0/40으로 기각했고 payload/model/GPU는 열지 않았다. 상세 근거는
> [`inverse-aneurysm-editing-audit-2026-08-09.md`](inverse-aneurysm-editing-audit-2026-08-09.md)를
> 따른다.

> **2026-08-09 open-CTA P0 outcome:** Zenodo `15697196`의 ZIP64 central
> directory와 `Metadata.csv`만 먼저 range-read해 172 case, 122 lesion과 24
> multi-lesion case를 확인했다. DICOM header·PixelData와 STL payload를 읽기
> 전에 physical-coordinate lesion-instance grid-commutation 후보와 P0를
> 고정했다. Exact `b437875…` 실행은 일부 header prefix 접근 뒤 DICOM
> undefined-length Procedure Code Sequence에서 exit 1이었다. PixelData는
> decode·inspect하지 않았고 STL에는 도달하지 않았다. Scientific gate는
> 미평가이며 parser repair/rerun 없이 후보를 닫았다. 현재 active problem,
> primary problem/method/GPU는 0이다. 상세 근거는
> [`open-cta-physical-grid-audit-2026-08-09.md`](open-cta-physical-grid-audit-2026-08-09.md)를
> 따른다.

> **2026-08-09 TopAneu source audit:** Live page는 417 scan/409 unique patient,
> 52-class location, lesion/type mask와 organizer-predicted silver vessel mask를
> 기술한다. Verified account와 terms가 필요하며 사용자가 동의했다고 확인되지
> 않았으므로 payload는 읽지 않았다. Patient-specific vascular attachment 가설은
> 29/40 조건부 lead일 뿐 active primary가 아니다. Open CTA는 TopAneu
> supervision의 대체물이 아니다.

> **2026-08-09 closed candidate:** Goal-oriented hemodynamic segmentation의
> primary data 후보는 CMHA뿐이었다. 공식 record는 99 patients/105 MCA
> aneurysms, 44 controls의 NIfTI CTA, aneurysm–artery STL, aneurysm STL과
> 5개 table을 CC BY 4.0으로 제공한다. Exact `ef547a4…` asset component는
> 5/9로 실패했다. 99 patient-level case directory와 105 lesion row의 explicit
> linkage가 없어 required CTA+2 STL triplet은 0/105였고 NIfTI/STL header는
> 열지 않았다. 따라서 training cohort가 아니며 후보를 닫았다. OpenNeuro
> ds005096은 TOF-MRA external
> stress 후보이고 CMHA와 patient를 합치지 않는다. 2026 multi-center CTA
> Zenodo `15697196`은 172 series/122 aneurysm STL의 parent-vessel supervision을
> payload audit하기 전에는 primary domain으로 쓰지 않는다.

> **2026-08-09 supervision-semantics decision:** RSNA Intracranial Aneurysm
> Detection 2025의 selection-aware mixed-granularity lesion-set 후보는
> 기각됐다. 공개 1위 구현과 2위 report에서 약 178건에 제공된 segmentation은
> aneurysm extent가 아니라 13-class Circle-of-Willis vessel anatomy이며,
> official aneurysm supervision은 center point와 presence/territory label이다.
> 따라서 일부 공식 aneurysm mask가 비무작위로 선택된 cohort라는 전제가
> 성립하지 않는다. Controlled payload는 읽지 않았고 method/GPU/outer test도
> 열지 않았다. RSNA는 다른 task가 fresh audit를 통과할 경우에만 future
> challenge benchmark가 될 수 있다. 상세 근거는
> [`rsna-supervision-semantics-audit-2026-08-09.md`](rsna-supervision-semantics-audit-2026-08-09.md)를
> 따른다.

> **2026-08-09 source-only substitution screen:** CADA, ADAM, IntrA와 TopCoW의
> 공식 metadata·access·annotation 범위를 비교했지만 image/annotation payload는
> 읽지 않았다. CADA/ADAM은 fully supervised challenge이고 IntrA/TopCoW는 각각
> local surface segment/vascular anatomy라 기각된 study-level non-random
> annotation-selection 문제를 대체하거나 구제하지 않는다. 어느 대안도
> active problem, method/GPU 또는 outer test를 열지 않는다.

> **2026-08-08 candidate snapshot, closed 2026-08-09:** 공개 in-vitro 4D-flow MRI release들을
> 새 end-to-end cohort로 합치지 않는다. 2021 release는 한 aneurysm phantom의
> 3 resolution × 3 acceleration development view, Zenodo `14981710`은 네
> aneurysm/flow-diverter phantom의 dual-VENC view, 새 `17183575`는 33 scan의
> intervention/multi-VENC/noise-control asset이다. 그러나 마지막 자료도 실제로는
> 5 base geometry·22 model/device state·2 source patient anatomy다. 현재
> I0a metadata/header audit은 exact source `f7b4e024…`에서 14/14를 통과했다.
> I0b는 2021의 27 processed RAW만 읽도록 등록됐지만 exact `0ebdb344…`의
> one-shot run이 `h5py` import에서 종료돼 archive request, field staging과
> REC read는 모두 0이었다. Gate는 미평가이고 no-rerun rule로 branch를
> 닫았다. 두 2025 release의 독립성은 unresolved이다.
> CFD를 MRI ground truth로 부르거나 phantom을 clinical cohort로 해석하지 않는다.

> **2026-08-03 AURORA 역할 갱신:** 데이터셋은 하나의 end-to-end cohort로
> 합치지 않는다. Aneumo/AneuG-Flow는 BC-aware operator pretraining,
> BenchAnXplore는 transient baseline, CMHA는 real-CFD utility gate,
> AneuX는 external rupture-status stress test로 분리한다. 현재 실험 계약은
> [`experiment-protocol.md`](experiment-protocol.md)를 따른다.

> **2026-08-03 asset audit:** `introai9`에서 Aneumo, AneuG-Flow,
> BenchAnXplore, CMHA, AneuX, Aneurisk의 원본 또는 추출 자산을 확인했다.
> 내부 경로는 공개하지 않는다. 자산 존재만으로 G0를 통과한 것은 아니며,
> manifest·license·unit·case mapping 검증 상태는
> [`server-execution.md`](server-execution.md)에 기록한다.

> **가용 범위 정정:** Aneumo 공식 release의 `1.zip` 중앙 디렉터리를
> byte-range로 감사한 결과, geometry 1--40마다 같은 좌표의 8개 steady
> mass-flow condition이 확인됐다. Geometry 1의 두 internal NPY member는
> CRC와 `(N,7)=xyz+pressure+velocity` contract를 실제 검증했다. 전체
> archive를 받지 않는 32 base-family × 2 deformation × 8 condition
> selective pilot이 `configs/aneumo_g2_pilot_v1.json`에 사전 등록됐고
> staging 전이다. AneuG-Flow는 geometry archive만 확인됐으며 공식
> benchmark는 BC variation을 제공하지 않는다. BenchAnXplore coarse
> archive는 105개 HDF5/XDMF case, case당 80 velocity timestep이 완전하게
> 확인됐다. “공개 규모”, “감사된 구조”, “학습 가능한 local cache”를
> 구분한다.

> **2026-08-08 boundary-asset 정정:** 위 selective compact cache는 internal
> NPY만 staging했지만 official Aneumo ZIP 전체에는 case별 `.msh`, `.stl`,
> `internal.vtu`, `inlet/outlet/wall.vtp`가 있다. Archive 1/case 1 header에서
> PolyData connectivity와 `Points/U/p` array를 확인했다. 이 one-case
> discovery는 전체 자산 감사가 아니다. Exact source `fb1c21a`의 V1b가 20
> archives·64 cases의 384 required member와 60 train representative VTP를
> 검사해 8/8을 통과했다. Validation/test payload와 field array는 읽지 않았다.
> 후속 V1c는 20 train representative×3 patch×3 flow의 geometry-only
> q-invariance·topology·area/frame·coordinate-frame audit에서 8/8을
> 통과했다. 60/60 patch가 exact q-invariant였고 minimum polygon-valid
> fraction은 1.0이었다. Exact source `369317a`의 V1d는 validation geometry
> decode 전에 고정한 train 40, validation 12, test 0 case의 520 geometry
> payload를 감사해 9/9을 통과했다. 156/156 patch가 q-invariant였고 52/52
> case의 exact boundary-volume correspondence를 확인했다. 이 asset pass로
> 등록한 V1e는 exact `c62838b`에서 6/9로 실패했다. Boundary는 matched
> geometry-only control보다 3/3 seed에서 좋았지만 absolute train/validation/
> response learnability 기준은 모두 실패했다. 따라서 boundary asset utility만
> 보존하며 test, missing-condition method와 current Aneumo 3D line은 열지 않는다.

## 핵심 비교

| 자료 | 직접 제공하는 것 | 규모/범위 | 적합한 용도 | 신뢰도 메모 |
|---|---|---:|---|---|
| TopAneu 2026 | CTA/MRA, 52-class location mask/JSON, lesion type mask, predicted vessel mask | live train 417 scan/409 patient | explicit user terms 수락 뒤 P0-R asset/semantics audit 후보 | MICCAI challenge; vessel mask는 silver; new factorized leaf-risk source lead 33/40, historical attachment candidate 29/40 rejected; payload/P0/method/GPU 없음 |
| RSNA-ICA 2025 | Multisite CT/MR angiography, study/location labels, aneurysm center points와 일부 13-class vessel-anatomy segmentation | official description: >4,000 scans, 18 institutions, 13 locations; second-place report: 4,348 series/178 vessel-mask cases | rejected for mixed-granularity lesion-selection task; possible future benchmark only after a new task audit | controlled access; not staged; no official voxel aneurysm mask; no redistribution |
| CADA 2020 | 3DRA와 task별 center/mask supervision | detection 109 volume/127 lesion; segmentation 110 volume/128 lesion | user access 뒤 fully supervised external detection/segmentation stress test | registration required; CC BY-NC-ND 4.0; selection-aware cohort 아님 |
| ADAM 2020 | TOF-MRA+structural MR, center/radius와 consensus binary mask | 113 scans; 93 positive, 20 negative; 일부 baseline/follow-up | user access 뒤 MRA fully supervised baseline | registration/confidentiality agreement; subject-group split 필수; selection-aware cohort 아님 |
| IntrA | Reconstructed vessel surface와 local aneurysm/healthy segments | 103 full vessel models; 1,694 healthy/215 aneurysm segment; 116 manual part annotations | license audit 뒤 surface anatomy pretraining/sanity | raw MRA와 whole-study negative/cardinality 없음; selection rule·payload license 재감사 필요 |
| TopCoW 2024 | CTA/MRA CoW masks, ROI와 vascular graph | permanent 14.4 GB release plus external subsets | anatomy encoder/topology control | aneurysm label이 아니며 listed LargeIA/Lausanne external subsets는 aneurysm-free |
| AneuriskWeb | surface/centerline/morphology, 일부 배포본의 영상·annotation 여부 확인 필요 | 약 100 | geometry·형태 baseline | 배포본/미러별 asset 차이를 checksum으로 확인 |
| Aneurisk CFD curvature 2026 / Zenodo 19455127 | OpenFOAM-derived VTP surface geometry, morphology and hemodynamic fields | 76 selected anterior-circulation geometries, 1.4 GB | source-rejected curvature/hemodynamic control only | CC BY 4.0; archive 미접근; two population age-group inflows scaled by diameter, not measured patient BC; record/paper outlet summary mismatch; best source candidate 31/40 |
| AneuX v1.0 | 동일 lesion의 3 mesh resolution × 최대 4 cut, 170 morphometrics, cross-sectional status | 750 lesion, 605 source-reported patient | closed preprocessing-orbit P0 history | initial tabular transport exhaustion; 13-check gate 미평가; no rerun/P1/model/GPU; CC BY-NC 4.0; real CFD 아님 |
| CMHA / Gong et al. 2024 | NIfTI CTA, aneurysm–artery STL, aneurysm STL, clinical/morphology/hemodynamic summaries | 99 unique patients/105 MCA IA + 44 controls | closed goal-oriented S0a asset history; 새 task에는 fresh audit 필요 | CC BY 4.0; 15.56 GB; 6 multi-lesion patient; asset 5/9 fail, exact lesion-level linkage unsupported; public CFD is summary only |
| OpenNeuro ds005096 | TOF-MRA, selected-session voxel masks/STL/Slicer scene | 63 patients/85 IA; 24 longitudinal patients | external modality/geometry stress only | one annotated session per subject; longitudinal supervised-growth cohort 아님 |
| Open multi-center CTA 2026 / Zenodo 15697196 | raw CTA DICOM, case metadata, 122 aneurysm STL | 172 series: 90 controls/82 IA cases, 24 multi-lesion case, 3 centers | closed physical-grid P0 history; no active primary role | P0 execution-incomplete after partial header prefixes; no PixelData/STL; scientific gate unevaluated; no parser repair/rerun/model/GPU |
| BenchAnXplore / npj DM 2026 | 105 semi-idealized geometry의 coarse CFD trajectories | 80 frames/case, 0.01 s | GNN surrogate benchmark | ICA sidewall 중심; patient CTA 입력자료가 아님 |
| Aneumo | 10,660 geometry × 8 steady mass flow, pressure/velocity | 85,280 steady CFD | paired BC response | CC BY-NC-ND; base-family split·비재배포 |
| AneuG-Flow / 관련 synthetic set | exact processed steady norm + transient WSS/mesh pair; source page 730 pulsatile case | 33.38 GB selected processed pair; full repo 2.63 TB | closed cycle-functional P0 history; active training role 없음 | CC BY-SA 4.0; P0 exit 28 before payload/result; scientific gate unevaluated; no repair/rerun/P1; patient/clinical evidence 아님 |
| 4D-flow MRI multiresolution phantom 2021 | 같은 ICA aneurysm phantom의 3 voxel-size × 3 acceleration processed velocity | 1 physical phantom, 9 selected protocols | closed I0b candidate; field 미접근 | CC BY 4.0; execution-incomplete/no verdict/no rerun, 반복 측정·독립 geometry 부족 |
| 4D-flow MRI dual-VENC phantoms 2025 | 네 aneurysm/flow-diverter phantom의 raw four-encoding dual-VENC acquisition | 4 physical phantoms, 8 acquisitions | 보존된 metadata/header candidate | CC BY 4.0; REC 미접근, M4 filename/header 불일치 명시 |
| 4D-flow MRI intervention phantoms 2025 | untreated/device-treated, multi-VENC, pump-off four-encoding raw acquisitions | 33 scans, 22 physical states, 5 base geometry, 2 source anatomies | 보존된 task-unit discovery | CC BY 4.0; scan/device를 patient로 세지 않음, REC 미접근, `14981710` overlap unresolved |

숫자와 확장자는 원 배포본을 받은 뒤 자동 inventory로 확정한다. 정리글의 “Aneurisk CFD 포함”은 현재 프로젝트의 샘플 관찰만으로 확인되지 않았으므로 `unknown`으로 시작한다.

## 권장 canonical 구조

```text
dataset_root/
  raw/<dataset_name>/                 # 원본 보존, 수정 금지
  unified/cases/<case_id>/
    imaging/volume.nii.gz             # 있으면; DICOM은 raw/dicom
    geometry/vessel.vtp
    geometry/aneurysm.vtp
    geometry/centerline.vtp           # optional
    annotation/segmentation.nii.gz    # optional
    metadata/clinical.json
    metadata/morphology.csv
    simulation/cfd/                   # h5/xdmf/cas.gz 원본 paired asset
    derived/hemodynamics/features.csv
  manifests/case_manifest.csv
  splits/geometry_disjoint.json
```

`.vtp`는 point/cell attributes를 보존하기 좋아 canonical mesh로 삼되, STL은 raw에 남긴다. NIfTI 변환은 단순 확장자 변경이 아니라 orientation, affine, voxel spacing을 보존하는 변환이어야 한다. HDF5/XDMF와 Fluent CAS는 역변환·재구성하지 말고 paired raw asset으로 보존한다.

## 병합하지 말아야 할 것

- AneuX의 geometry-only case에 GNN이 생성한 WSS를 `real_cfd`로 저장하지 않는다.
- 서로 다른 환자/기관의 동일 ID를 파일명으로 추정해 합치지 않는다.
- rupture label, future rupture risk, treatment decision을 같은 `label` 필드로 뭉치지 않는다.
- node-level CFD와 case-level summary를 같은 학습 split에 섞지 않는다.
- image–mesh–CFD를 매핑할 수 없는 case는 삭제하지 말고 `unmatched`로 보고한다.

## CMHA 현재 주의사항

- aneurysm 통계표는 105개 병변/99명 환자로 관찰됐다.
- 6명은 다병변이며 병변별 status가 달라 patient-group split이 필수다.
- morphology table의 lesion suffix와 clinical/hemodynamic table의 반복
  patient identifier는 row alignment로는 호환되지만 공식 case map 확인 전
  exploratory로만 사용한다.
- 정의가 확인되지 않은 `PHASE`, `ELAPSS` 열은 target을 거의 분리하므로
  baseline에서 제외한다.

## 단계별 통합

1. 원본 archive의 SHA-256, 출처 URL, license, 다운로드 날짜를 기록한다.
2. 모든 파일을 `dataset/case/source_asset` 3중 키로 inventory한다.
3. case identifier mapping table을 수동 검토한다.
4. mesh의 units, coordinate frame, watertightness, normals, duplicate points를 검사한다.
5. CFD field가 node/cell 중 어디에 저장됐는지와 시간축·단위를 기록한다.
6. 공통 clinical/morphology 컬럼만 canonical table에 넣고 원본 column은 그대로 보존한다.
7. 실제 target별로 split을 다시 만든다: surrogate는 geometry-disjoint, rupture는 patient/site-disjoint.

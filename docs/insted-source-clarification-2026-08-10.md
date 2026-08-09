# INSTED/IAIA source clarification · 2026-08-10

상태: **source semantics corrected · historical 26.0/40 rejection preserved ·
no new score/payload/P0/model/GPU**

## 무엇을 바로잡는가

2026-08-09 source-delta audit은 Zenodo record만 기준으로 IAIA를
`proposal-only`라고 요약했다. 이 표현은 해당 Zenodo artifact가 challenge-design
PDF뿐이라는 뜻에서는 맞지만, 전체 source의 현재 상태를 충분히 설명하지 못한다.

[공식 Codabench competition](https://www.codabench.org/competitions/2139/)은
`INSTED: Intracranial Aneurysm and Intracranial Artery Stenosis Detection and
Segmentation Challenge (2024)`로 published 상태다. Public API는 CC BY-NC terms,
160 training case와 40 closed-test case를 확인한다. Training set은 healthy 32,
aneurysm 64, stenosis 64이며 가입 뒤 challenge Files에서 받도록 안내한다.
각 lesion case에는 bounding box와 box 내부 segmentation mask가 있다.

공식 code repository
[`e48a9ba16398cca309d932813cda7dd3dc3e4cb9`](https://github.com/XiaogouNaix/INSTED2024/tree/e48a9ba16398cca309d932813cda7dd3dc3e4cb9)은
loader example, ingestion/scoring code와 evaluation notebook을 공개한다. Dataset
payload 자체는 repository root에 없다.

## 5-year survival 문구는 target이 아니다

[BIAS challenge-design PDF](https://zenodo.org/records/10990482)의 page 11에는
case 정의를 설명하는 **예시 bullet** 안에 “5 years after the first image”의
binary survival 문장이 있다. 바로 뒤의 challenge-specific answer는 training과
test case가 3D TOF-MRA이고 aneurysm 또는 stenosis의 bounding box와 segmentation을
annotate한다고 명시한다. 뒤의 metric도 IA/stenosis F1, AP, Dice, HD95와 stenosis
percentage·long/short axis error다. Survival, rupture, time-to-event와 follow-up
metric은 없다.

따라서 이 예시 문장을 prospective aneurysm outcome으로 인용하지 않는다.
INSTED는 5-year survival/rupture prediction dataset이 아니다.

## 연구 결정

- Historical source score **26.0/40**과 rejection을 그대로 보존한다. 당시
  score를 결과 뒤에 고치지 않는다.
- `proposal-only` 표현은 `published, signup-gated segmentation challenge; Zenodo
  artifact is design-only`로 정정한다.
- Corrected asset semantics만으로 6점의 admission gap이 사라지지 않는다.
  Joint aneurysm/stenosis detection·segmentation은 challenge 자체가 점유하며,
  U-Net, multitask head, vessel prior, anatomy token과 generic cross-pathology
  representation은 독립 novelty가 아니다.
- Agent는 signup, terms acceptance와 `Full dataset` download를 수행하지 않았다.
  Image, mask, bounding-box pickle과 identifier payload access는 0이다.
- Fresh source score, executable P0, method, architecture, GPU와 outer test는
  등록하지 않는다. AURORA scientific execution은 계속 `introai9`만 사용하고
  `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

이 clarification은 source metadata 오류를 바로잡는 기록이지 closed candidate의
repair round나 re-entry가 아니다.

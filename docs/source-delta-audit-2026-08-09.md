# 2026-08-09 신규 source-delta audit

상태: **completed source-only audit · best 31.5/40 · active shortlist 0 ·
no P0/method/architecture/GPU/outer test · not submission-ready**

이 감사는 닫힌 DIAS, AneuX, Open-CTA 또는 RSNA 후보의 repair가 아니다. 2026년
공개 1차 자료의 변화와 `introai9`에 이미 존재하는 자산 범위만 다시 확인해,
독립적인 새 biomedical-imaging 문제를 만들 수 있는지를 사전 40점 rubric으로
평가했다. `tmp/`의 팀 대화는 2026-08-02 이후 갱신되지 않아 새 결정 근거로
추가된 private context는 없다.

## 판정

| 순위 | fresh candidate | 중요성 | 식별성 | residual gap | asset | 독립 단위 | baseline | figure | 일정 | 합계 | 판정 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | OpenNeuro paired-surface growth detection | 5.0 | 4.5 | 0.5 | 4.5 | 2.0 | 5.0 | 5.0 | 5.0 | **31.5** | reject |
| 2 | RSNA anatomy-indexed point-set detection | 5.0 | 4.5 | 1.5 | 1.0 | 5.0 | 5.0 | 5.0 | 3.5 | **30.5** | reject |
| 3 | VICTORIA reader-distribution neck curves | 4.5 | 4.5 | 2.0 | 4.0 | 0.5 | 5.0 | 5.0 | 5.0 | **30.5** | reject |
| 4 | IntrA topology-aware bifurcation control | 4.5 | 4.0 | 0.5 | 0.5 | 4.0 | 5.0 | 5.0 | 5.0 | **28.5** | reject |
| 5 | IAIA joint aneurysm–stenosis learning | 4.0 | 3.0 | 1.0 | 0.5 | 4.0 | 5.0 | 4.5 | 4.0 | **26.0** | reject |
| 6 | Flow-diverter DSA outcome modeling | 5.0 | 2.0 | 1.0 | 2.5 | 3.0 | 5.0 | 3.0 | 4.0 | **25.5** | reject |

자동 admission line은 32.0/40이다. 가장 높은 후보도 31.5이므로 점수 가중치나
문제 문구를 결과 뒤에 고치지 않는다. 새 payload, executable P0, method name,
architecture, seed, threshold, checkpoint와 GPU job은 만들지 않는다.

## 후보별 냉정한 이유

### 1. Longitudinal surface growth · 31.5/40

[OpenNeuro longitudinal cohort](https://pmc.ncbi.nlm.nih.gov/articles/PMC11139857/)
는 63 patient, 85 aneurysm과 24 longitudinal patient를 공개한다. 그러나
[Bayesian Aneurysm Growth Detection via Surface Displacement Modeling](https://arxiv.org/abs/2604.06649)은
이미 같은 공개 cohort를 사용해 surface registration, normal displacement,
parent-vessel internal control과 calibrated posterior를 결합하고 public external
AUC 0.87을 보고한다. 공개 cohort의 실질 종단 단위가 24 patient이므로, GNN,
surface transformer 또는 uncertainty head를 더하는 것은 독립 novelty도 충분한
confirmatory evidence도 아니다.

### 2. RSNA point-set detection · 30.5/40

[공식 AWS record](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
는 이제 18 institution, 40명 이상의 radiologist와 4,000건 이상의 CT/MR scan을
기술하지만 **Controlled Access**다. 사용자가 해당 non-commercial terms를
수락했다고 확인되지 않았고 payload는 읽지 않았다. 또한 공식 segmentation은
13-class Circle-of-Willis anatomy이며 aneurysm extent mask가 아니다. Aneurysm
supervision은 center point, presence와 territory다. 이 의미론은 기존
[RSNA supervision audit](rsna-supervision-semantics-audit-2026-08-09.md)을
뒤집지 않는다. Anatomy prompt, weak label, point process, set prediction, GNN,
FROC와 conformal risk는 이미 직접 선행 또는 표준 control이다.

### 3. VICTORIA neck distribution · 30.5/40

[VICTORIA](https://pmc.ncbi.nlm.nih.gov/articles/PMC8354974/)는 55 participant,
그중 20 physician이 5개 aneurysm geometry에 그린 neck curve와 downstream CFD
변동을 제공한다. Reader 수 55를 독립 geometry 55개로 세지 않는다. 실질
generalization 단위가 5 geometry이므로 reader-distribution calibration은 유용한
annotation study이지만 headline learned method의 outer evidence가 될 수 없다.

### 4. IntrA topology control · 28.5/40

[IntrA](https://github.com/intra3d2019/IntrA)는 103 whole-vessel model, 1,909 local
segment와 116 expert-annotated aneurysm segment를 보고한다. `introai9`에서 확인한
staging은 README, split과 preview image뿐이며 mesh payload는 없다. 더 중요한
문제는 surface segmentation, foundation 3D feature transfer와 최근의 persistent-
topology 기반 aneurysm/bifurcation 구분이 이미 직접 경쟁한다는 점이다. 따라서
topology loss나 false-positive head를 붙이는 것은 새 contribution이 아니다.

### 5. IAIA와 flow-diverter outcome · 26.0/25.5

[IAIA 2024 record](https://zenodo.org/doi/10.5281/zenodo.10990481)는 현재 challenge
proposal만 제공해 image/label payload와 독립 단위를 감사할 수 없다.
[flow-diverter clinical dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC9163419/)은
126 subject, 141 procedure의 tabular/제한적 angiographic 자료를 제공하지만,
학습 가능한 imaging sequence와 follow-up endpoint의 연결이 headline 영상 방법을
식별하기에 부족하다. Morphology, angiographic parametric imaging, CFD와 treatment-
outcome ML도 이미 밀집한 직접 선행이다.

## `introai9` 실행 경계

- 실제 credential-managed login boundary에서 public-key 접속을 확인했다.
- PBS 조회 시 현재 AURORA job은 0개였다.
- 알려진 dataset root를 bounded, read-only로 감사했고 Aneumo, AneuG-Flow,
  BenchAnXplore, CMHA, AneuX와 Aneurisk 계열 자산을 확인했다. 새 후보의 payload를
  열거나 서버 절대경로를 공개하지 않았다.
- IntrA는 repository skeleton만 있고 mesh payload는 확인되지 않았다.
- Login node에서 `nvidia-smi`나 GPU 학습을 실행하지 않았다.
- `junjinyong`에는 접속, 조회, 제출 또는 모니터링하지 않았다.

로컬 SSH config에 `introai9` 별칭이 없었던 것은 과학적·GPU 실패가 아니다.
서버 가이드가 지정한 실제 login boundary의 공개키 접속은 성공했다. 별칭이나
endpoint는 private `SERVER_GUIDE.md`에서만 관리한다.

## 다음 허용 작업

1. 동일 후보를 즉시 재명명하거나 rubric을 다시 가중해 32점으로 올리지 않는다.
2. 진짜 새 release, supervision semantics 또는 독립 단위가 생기면 별도 version으로
   다시 source audit한다.
3. RSNA는 사용자의 명시적 terms 수락과 fresh payload/semantics audit 없이는
   접근하지 않는다. 수락 자체도 method 또는 GPU 권한이 아니다.
4. fresh candidate가 32점 이상일 때만 `introai9`의 CPU/PBS에서 prospective,
   method-free P0를 등록한다.
5. P0 뒤 task adequacy가 통과한 경우에만 architecture와 scheduler-allocated GPU
   runtime smoke를 정의한다.

따라서 현재 가장 합리적인 실험 결정은 **GPU를 돌리지 않는 것**이다. 이는 계산
부족이 아니라, 직접 선행과 독립 표본 단위를 통과하지 못한 가설에 compute를
투입해 사후 novelty를 만드는 일을 막는 registered early stop이다.

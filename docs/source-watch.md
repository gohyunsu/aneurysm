# Public source watch · IAVS + TopBrain 2.0 + TRELLIS + Aneumo

> **2026-08-11 v4 decision:** the same fail-closed metadata contract now also
> watches the official Aneumo GitHub repository and Hugging Face dataset for a
> genuinely material real-case/undeformed-case mapping release. A live refresh
> matched all five frozen snapshots. Aneumo GitHub remains exact `701d53dd…`,
> has no release and no GitHub-recognized license; Hugging Face remains exact
> `f801adee…`, has 370 entries under `CC-BY-NC-ND-4.0` and no filename marker
> for a real, undeformed, AneuX or mapping asset. Maintainer plans for a future
> linked release are a watch signal, not an E0 pass. No payload was downloaded,
> no scientific server was queried and no P0/model/GPU authority was created.

> **2026-08-11 v3 decision:** One fail-closed read-only contract now separates
> two different kinds of evidence change. IAVS/TopBrain material changes can
> request only a fresh problem/source audit. A TRELLIS stated-code change can
> request only a direct-prior baseline-feasibility review. Neither route is
> asset access, score repair, P0 registration, method selection or compute
> authorization.

> **2026-08-11 live v3 refresh:**
> `same_as_all_frozen_snapshots=true`, `manual_review_triggered=false` and exit
> code 0. IAVS remains exact `2e40088d…` and README-only; TopBrain 2.0 remains
> Zenodo revision 4 with one design PDF and an under-construction challenge;
> the TRELLIS stated repository API remains HTTP 404. No server was queried.

> **2026-08-11 direct-prior note:** A separate TRELLIS surface-feature paper
> review changed the future baseline boundary, not the watched asset state. Its
> stated code repository currently returns 404 and supplies no material E0
> source. See [`trellis-surface-feature-direct-prior-delta-2026-08-11.md`](trellis-surface-feature-direct-prior-delta-2026-08-11.md).

> **Historical v2 refresh:** the 2026-08-11 two-source watch returned
> `same_as_all_frozen_snapshots=true`. IAVS remains exact `2e40088d…`,
> README-only, with no release, license, code or payload. TopBrain 2.0 remains a
> design-PDF/under-construction source with no material task route. This creates
> no source re-audit, P0, method or GPU authorization. The separate schema-7.5
> inverse-flow audit was triggered by a new published direct prior, not by a
> watched asset change. No server was queried.

상태: **watch-only · 다섯 official public states 모두 frozen snapshot과 동일 ·
manual review 0 · no medical payload/source-score repair/P0/model/GPU**

## 왜 감시하는가

[IAVS 논문](https://arxiv.org/abs/2512.01319)은 641개의 3D MRA와 587개의
aneurysm–parent-vessel annotation, hemodynamic analysis outcome, standardized CFD
applicability evaluation을 보고한다. 공개된다면 현재 CMHA에서 막힌 명시적
lesion–vessel–CFD 연결을 다시 평가할 가치가 있다.

그러나 이 기대를 현재 데이터 가용성과 혼동하지 않는다. 2026-08-10에 확인한
[공식 저장소](https://github.com/AbsoluteResonance/IAVS)의 `main`은 exact
`2e40088d9eaa671c592929a154b7b2cf99f9320a`이고, 90-byte `README.md` 한 파일만
있다. Release는 0개이고 GitHub가 인식하는 license도 없다. README는 dataset,
code와 model weight를 논문 채택 뒤 공개한다고 명시한다.

## novelty에 미치는 영향

IAVS 논문 자체가 global localization과 fine segmentation의 two-stage baseline,
mask-to-CFD 변환과 CFD Applicability Score를 제안한다. 따라서 향후 자산이
공개돼도 다음은 독립 contribution이 아니다.

- vessel-aware segmentation 뒤 CFD solver success를 보고하는 것
- Dice에 topology 또는 CFD score를 단순 추가하는 것
- U-Net, GNN, Transformer나 uncertainty head를 붙이는 것

남을 수 있는 gap은 실제 release와 독립 단위를 감사한 뒤에만 정의한다. 예를
들어 calibrated segmentation distribution이 solver failure와 여러 physical
functional의 risk를 얼마나 보존하는지 같은 질문도 uncertainty propagation,
task-based segmentation과 topology direct prior를 다시 대조해야 한다. 현재는
가설이나 모델로 등록하지 않는다.

TopBrain 2.0은 별도의 이유로 감시한다. 공식 Zenodo revision 4는 139,840-byte
설계 PDF 하나만 제공하며 그 **설계 객체**는 `CC BY 4.0`이다. 이 라이선스를
아직 공개되지 않은 환자 영상·mask의 라이선스로 확장하지 않는다. Challenge
page는 `Under construction`이고 Join registration은 열려 있지만 Data,
Evaluation, Rules, Submission task route는 없다. 따라서 29/40 기각과 payload,
P0, model, GPU 0 경계는 변하지 않는다.

TRELLIS는 task asset이 아니라 **direct-prior baseline feasibility** 때문에
감시한다. 논문에 적힌
[`clementhrv/trellis_for_intra`](https://github.com/clementhrv/trellis_for_intra)는
2026-08-11 repository API에서 HTTP 404다. 향후 repository가 공개되더라도 그
사실은 phase-resolved WSS asset, E0 pass 또는 proposal 선택을 뜻하지 않는다.
코드와 license를 읽어 faithful TRELLIS-style control을 재현할 수 있는지 별도로
검토할 이유만 생긴다. 논문의 feature encoder, rendering과 concatenation은 이미
direct prior이므로 repository 공개를 novelty로 바꾸지 않는다.

Aneumo는 과거 33.5/40 BC-transport source candidate와 닫힌 one-shot P0를
사후 수리하기 위해 감시하는 것이 아니다. Official repository issue에서
maintainer는 synthetic variant와 연결된 추가 real undeformed case/CFD 결과를
향후 공개할 계획이라고 답했다. 현재 GitHub/Hugging Face metadata에는 그
mapping을 식별할 수 있는 manifest가 없다. 따라서 revision이나 filename
inventory 변화는 fresh source re-audit만 요청하며, historical score/P0를
되살리거나 payload download를 자동화하지 않는다.

## 기계적 감시 계약

[`configs/source_watch_v4.json`](../configs/source_watch_v4.json)은 IAVS의 현재
commit, root entry, release count와 license, TopBrain 2.0의 Zenodo revision,
design-object license, exact file inventory와 challenge navigation, TRELLIS의
stated repository HTTP 404 상태, Aneumo GitHub/Hugging Face의 exact revision,
license/access state와 filename-manifest hash를 고정한다. 기존 v1--v3는
historical contract로 보존한다.
[`scripts/audit_source_watch.py`](../scripts/audit_source_watch.py)는 GitHub의
공식 metadata와 Zenodo/Grand Challenge page만 읽고 다음 변화를 감지한다.

1. 새 commit과 non-README code/payload가 함께 나타남
2. versioned release가 생김
3. 명시적 repository license가 생김
4. 공식 versioned dataset record가 별도로 확인됨 · manual review
5. TopBrain 2.0의 Zenodo revision/file/license가 바뀜
6. challenge의 under-construction 표지가 사라지거나 Data/Evaluation/Rules/
   Submission navigation이 생김
7. TRELLIS stated repository가 공개되거나 code/release/license가 나타남
8. Aneumo official GitHub release/license/root inventory가 바뀜
9. Aneumo Hugging Face revision/license/access state나 370-entry manifest가
   바뀌거나 real/undeformed/AneuX/mapping marker가 나타남

1--6과 8--9의 변화가 있어도 자동 결과는 **fresh source audit 요청**뿐이다. 7은
**direct-prior baseline-feasibility review 요청**만 만든다. 자동 download, 약관
수락, 점수 재가중, frozen snapshot 갱신, P0 등록, model/architecture 선택,
GPU와 outer test는 모두 금지된다. Payload P0는 explicit license/사용자-confirmed terms,
machine-auditable manifest, independent-unit semantics와 새 direct-prior audit을
갖춘 후보가 frozen 32/40 source gate를 통과한 뒤에만 별도 version으로 등록할
수 있다.

```bash
PYTHONPATH=src python scripts/audit_source_watch.py \
  --config configs/source_watch_v4.json \
  --validate-only

PYTHONPATH=src python scripts/audit_source_watch.py \
  --config configs/source_watch_v4.json \
  --fetch --fail-on-change
```

두 번째 명령은 source state를 stdout에 출력한다. Frozen state와 같으면 0,
material change면 근거를 출력한 뒤 3을 반환한다. HTTP rate limit, transport,
schema failure는 change signal로 바꾸지 않고 command 자체를 실패시킨다.

[`source-watch.yml`](../.github/workflows/source-watch.yml)은 월·목요일 02:17 UTC와
manual dispatch에 같은 명령을 실행한다. Workflow permission은 `contents: read`뿐이고
snapshot commit, issue/PR 생성, artifact download 또는 server login을 수행하지
않는다. 실패는 사람이 evidence version을 명시적으로 열어야 한다는 알림이지,
자동 연구 상태 전이가 아니다.

Scientific CPU/PBS와 향후 gate-authorized GPU는 `introai9`에서만 수행한다.
이 public metadata watch는 `introai9`도 조회하지 않는다. `junjinyong`은 접속·조회·
제출·모니터링하지 않고 login node GPU 명령도 실행하지 않는다.

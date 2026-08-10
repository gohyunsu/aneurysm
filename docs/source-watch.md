# Public source watch · IAVS

상태: **watch-only · README-only repository · release 0 · explicit repository
license 0 · payload/code 0 · no source score/P0/model/GPU**

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

## 기계적 감시 계약

[`configs/source_watch_v1.json`](../configs/source_watch_v1.json)은 현재 commit,
root entry, release count와 license를 고정한다.
[`scripts/audit_source_watch.py`](../scripts/audit_source_watch.py)는 GitHub의
공식 metadata만 읽고 다음 1--3 변화를 자동 감지한다. 4는 별도의 1차 출처를
사람이 확인해 붙이는 수동 trigger다.

1. 새 commit과 non-README code/payload가 함께 나타남
2. versioned release가 생김
3. 명시적 repository license가 생김
4. 공식 versioned dataset record가 별도로 확인됨 · manual review

변화가 있어도 자동 결과는 **fresh source audit 요청**뿐이다. 자동 download,
약관 수락, 점수 재가중, P0 등록, model/architecture 선택, GPU와 outer test는
모두 금지된다. Payload P0는 explicit license/사용자-confirmed terms,
machine-auditable manifest, independent-unit semantics와 새 direct-prior audit을
갖춘 후보가 frozen 32/40 source gate를 통과한 뒤에만 별도 version으로 등록할
수 있다.

```bash
PYTHONPATH=src python scripts/audit_source_watch.py \
  --config configs/source_watch_v1.json \
  --validate-only

PYTHONPATH=src python scripts/audit_source_watch.py \
  --config configs/source_watch_v1.json \
  --fetch
```

두 번째 명령은 source state를 출력할 뿐 파일을 다운로드하거나 실행 권한을
바꾸지 않는다. Scientific CPU/PBS와 향후 gate-authorized GPU는 `introai9`에서만
수행한다. `junjinyong`은 접속·조회·제출·모니터링하지 않고 login node GPU
명령도 실행하지 않는다.

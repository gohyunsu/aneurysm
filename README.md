# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)

AURORA는 합성 뇌동맥류 표면에서 전체 cardiac cycle의 vector wall shear
stress(WSS)를 예측하는 ICCE 2027 연구입니다. 현재 목표는 강한 직접 선행
baseline과 비교하여, steady에서 전이할 공간 정보와 transient에서 학습할
시간 응답을 구분하는 구조의 성능과 필요성을 검증하는 것입니다.

새 아키텍처의 우수성은 아직 검증되지 않았습니다. 기존 연구와 완료된 결과는
보존하되, 감독 방식 비교만으로 새로운 GNN이나 새로운 multi-task 구조를
주장하지 않습니다. [현재 개발 계획](docs/icce-architecture-development-v3.md)

## 현재 범위

| 항목 | 범위 |
|---|---|
| 제출 목표 | ICCE 2027 CSH · 최대 6쪽 IEEE conference 원고 |
| 주 데이터 | 공식 AneuG-Flow transient 730개 |
| 기존 partition | 584 / 73 / 73 train/validation/test |
| 독립 단위 | geometry 및 GHD duplicate component; 730개를 환자 730명으로 해석하지 않음 |
| Steady | processed 14,392개 중 overlap 제외 후 13,985 rows; 공식 논문의 14,000 기술과 구분 |
| 추가 79개 | 공식 main cohort 및 독립 외부 검증으로 사용하지 않음 |
| 현재 구현 | 기존 GHD–GPS/GINE 및 새로운 내부 masked-time/Fourier-only decoder controls |
| 다음 단계 | 직접 선행 소스의 실행 충실도, 실제 phase grid, 강한 baseline adapter와 GPU 비교 |

기존 test는 원래 T 대 separated T+S 비교에서 이미 개방되었습니다.
새 모델은 train/validation에서 개발하며, 기존 test의 추가 평가를 미개방
확증 실험이라고 부르지 않습니다. 완료된 연구 결과와 미완료 개발을 구분하고,
새 모델 성능은 실제 결과가 생길 때만 보고합니다.

## 연구 질문과 아키텍처

> 풍부한 steady supervision에서 전이 가능한 공간 정보와 transient의
> 주기 응답을 구조적으로 구분하면, 강한 기존 방법보다 정확하고 데이터
> 효율적인 complete-cycle WSS 예측이 가능한가?

우선 후보는 공유 공간 연산, transient 전용 평균/진동 응답, 형상·시간 성분별
선택적 전이로 구성합니다. Steady WSS를 transient 평균이나 특정 phase와
같다고 강제하지 않으며, 추론에는 실제 steady CFD를 요구하지 않습니다.

현재 추가된 코드는 이 후보 전체가 아니라 비교 실험의 기초입니다.

- Masked-time control: steady의 시간 특징을 마스킹하는 공유 decoder.
- Fourier-only ablation: 명시적 phase grid에서 전체 주기를 재구성하는 decoder.
- Full-spectrum 및 cutoff reconstruction: 표현 오차와 학습 오차를 구분하는 도구.

[구현](src/aurora/aneug_cycle_decoders.py) ·
[합성 입력 테스트](tests/test_aneug_cycle_decoders.py)

## 강한 비교와 novelty 경계

직접 우선순위는 Sheng/RHSIA Graph Transformer의 masked steady augmentation과
sequence + predicted-steady FiLM입니다. LinearNO, 현재 separated GHD–GPS/GINE,
재사용 가능한 Transolver, released Graph U-Net을 비교하고 LaB-GATr의 기하학적
strong control 역할을 평가합니다.

원 구현, 충실한 재구현과 task adaptation을 구분합니다. 기존 GHD–GPS를
RHSIA의 정확한 재현으로 부르지 않습니다. 기존 mean-tied shared control 또한
원저자의 masked joint training과 다릅니다.

GNN, steady augmentation, Fourier 표현, 일반 adapter와 residual 자체는
선행 기술입니다. Fourier-only, 일반 task adapter, 항상 공유하는 구조와
선택적 전이를 비교하여 실제 구조의 필요성을 확인합니다. 단순 모델이
동등하거나 우수하면 더 단순한 모델을 채택합니다.

## 데이터·실험 원칙

- Geometry의 모든 phase와 변형은 동일 partition에 둡니다.
- Normalization, loss scale과 표현 선택은 허용된 training/development 정보만 씁니다.
- Proposal-only steady 정보를 허용하지 않고 T/T+S 조건을 분리합니다.
- Field rL2를 주 지표로, 같은 vector field의 TAWSS와 valid-support OSI를 보조 지표로 씁니다.
- Case 단위 paired uncertainty와 여러 seed로 평가하며 vertex/phase를 독립 표본으로 세지 않습니다.
- 데이터 exposure, optimizer update, tuning budget, GPU 시간·메모리를 별도로 기록합니다.
- 실제 one-shot 또는 phase-conditioned 경로의 전체 80-phase 추론 비용을 비교합니다.
- 기존 유효 결과를 재사용하며, 같은 scientific cell의 동시 중복 제출을 피합니다.
- 수리·재실행은 사유와 변경을 기록해 허용하고, 이전 72-cell grid 완주를 새 목표의 전제조건으로 삼지 않습니다.

고정 waveform, 공통 connectivity와 synthetic geometry의 한계를 명시합니다.
임의 실제 mesh, 새로운 BC, 독립 환자나 임상 파열 위험에 대한 일반화로
확대 해석하지 않습니다.

## 코드·논문 관리

공개 저장소에는 코드, protocol과 공개 문서를 둡니다. 원고, 비공개 split
식별자, 미공개 결과와 raw PBS evidence는 별도 private 저장소에서 관리합니다.
공개 사이트는 유지보수하지 않습니다. 기존 site 파일은 역사적 자산입니다.

과거 single-seed 개발 결과와 선택 과정은 Git 이력과 날짜별 문서에 보존합니다.
현재 목적·다음 행동은 [AGENTS.md](AGENTS.md)와
[architecture-development v3](docs/icce-architecture-development-v3.md)를 따릅니다.

```text
src/aurora/   모델, source reader, evaluator
configs/      실험 설정과 데이터 계약
cluster/      scheduler 실행 wrapper
tests/        합성 입력 및 회귀 테스트
docs/         현재 계획과 날짜별 근거
```

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

원고의 모든 숫자는 검증된 결과와 연결하며, 실제 표면 그림은 동일 camera와
색상 범위로 비교합니다. 계산하지 않은 실시간성이나 consumer-device 성능을
주장하지 않습니다. 상세 변경은 [CHANGELOG.md](CHANGELOG.md)에 기록합니다.

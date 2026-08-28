# Release-730 GHD same-field functional fine-tuning

## 결정 근거

Validation 개발에서 GHD–GPS가 Graph U-Net과 Transolver보다 낮은 physical vector-WSS
field error를 보였고 direct selector가 이를 control로 선택했다. 반면 rank-64
response+local-residual은 response-only와 구분되는 개선을 보이지 못했으며 GHD–GPS보다
field, TAWSS, OSI에서 모두 열세였다. 따라서 이 단계는 실패한 candidate에 기능 손실을
덧붙이지 않고, 가장 강한 직접 comparator에서 functional objective 자체의 효과를
분리한다.

이 결정은 global response나 local residual이 일반적으로 무효라는 뜻이 아니다. 현재
release-730 split, rank, backbone과 single seed에서 최종 proposal로 채택할 근거가
없다는 제한된 결론이다. 두 결과와 paired analysis는 negative ablation으로 보존한다.

## Prospective comparison

세 objective cell은 exact terminal seed-1103 GHD–GPS best checkpoint에서 시작한다.

| Cell | Backward objective | Checkpoint selection |
|---|---|---|
| `field_only` | normalized physical field loss | common four-endpoint utility |
| `all_scalarized` | field + mean(mean-vector, TAWSS, OSI) | common four-endpoint utility |
| `all_field_anchored` | field gradient + conflict-controlled functional gradient | common four-endpoint utility |

세 cell 모두 동일한 GHD-conditioned GPS/GINE U-Net, train 584, validation 73, seed 1103,
initial checkpoint, optimizer schedule과 evaluator를 사용한다. Functional values는 별도
prediction head가 아니라 동일한 80-phase vector field에서 계산한다. Train-term scale은
584 train cases의 initial-checkpoint error만 사용하고, checkpoint utility scale은 73
validation cases의 공통 initial checkpoint에서 고정한다.

공통 utility는 field endpoint ratio와 mean-vector, TAWSS, OSI endpoint ratio 평균의
합이다. 이는 objective마다 유리한 checkpoint rule을 쓰지 않기 위한 개발 선택
도구이며 임상 utility 또는 paper endpoint가 아니다. Epoch 0의 exact GHD checkpoint를
후보로 유지하므로 fine-tuning이 모든 endpoint를 악화시키면 원 모델이 선택된다.

## Scope and safeguards

- 공식 cohort와 split은 584/73/locked-73이며 80 phases는 geometry와 함께 유지한다.
- Runner에는 locked-test 또는 processed-only extra 경로가 없다.
- Normalizer와 loss scale은 train-only이고 model/checkpoint 선택은 validation-only다.
- 각 objective는 별도 fresh activation과 output root를 사용한다.
- 동일 scientific cell을 동시에 복제하지 않는다. 실패한 scheduler envelope는 결과로
  세지 않으며 exact checkpoint와 terminal hash가 있을 때 resume할 수 있다.
- 절대 성능 threshold나 자동 paper claim은 없다.
- 모든 validation row는 single-seed development evidence다.

## 다음 결정

세 cell이 끝나면 case-paired field, mean-vector, TAWSS, OSI difference와 compute를 함께
비교한다. Field accuracy를 희생하지 않으면서 functional endpoint를 개선하는 objective가
있을 때만 이를 다음 T/T+S 단계로 보낸다. 개선이 없으면 GHD–GPS field-only를 유지하고
functional-alignment contribution을 폐기한다.

그다음 steady stage는 동일 GHD backbone과 선택 objective 안에서 T와 T+S를 대칭
비교한다. Eligible steady rows는 transient validation/test/extras overlap audit를 통과한
범위만 사용하고, 추가 encoder pass와 exposure compute를 그대로 보고한다. Steady 효과가
확인된 뒤에만 label-efficiency와 multi-seed confirmation을 수행하며, 모든 개발 선택이
고정되기 전에는 locked test를 열지 않는다.

# In-PI-MGN 재현 실험

## 원 논문 설정

BenchAnXplore: 105 geometry, case당 80 frame, Δt=0.01 s, 95 train/10 test, light mesh는 25k nodes·120k elements 미만. hidden/latent 128, message passing 15, Adam 1e-4, 20 epochs, noise 0.003로 정리되어 있다.

## 현재 run 기록

2026-06-24 종료된 공개 기록은 one-step validation RMSE와 50-step rollout RMSE를 사용했고, 논문 표의 목표치와 큰 차이를 보였다. 기록된 원인 후보는 test split 차이, 공개 mask 차이, physics operator 구현 차이, one-step 중심 학습이다. 따라서 실패가 아니라 **재현성 audit의 출발점**으로 기록한다.

## 검증 순서

1. 논문 dataset availability의 checksum·파일 목록과 local HDF5/XDMF를 비교한다.
2. tetrahedral cell에서 6개 undirected pair를 만든 뒤 양방향 edge로 확장하는지 확인한다.
3. self-loop·duplicate edge 제거 여부, node type mask, wall exclusion을 고정한다.
4. velocity/position/time/inflow/acceleration의 단위와 normalization을 기록한다.
5. data-only MGN → In-MGN → PI-MGN → In-PI-MGN ablation을 같은 split에서 실행한다.
6. one-step, 50-step, mass flux, divergence residual, wall WSS/TAWSS를 함께 보고한다.
7. geometry-disjoint OOD와 inflow-disjoint OOD를 분리한다.

## 연구 결론의 기준

RMSE 하나가 낮아도 vortex topology, wall field, conserved mass가 틀리면 surrogate는 충분히 검증된 것이 아니다. 특히 WSS/OSI는 벽면 gradient에 민감하므로 mesh resolution과 wall interpolation sensitivity를 함께 보고한다.

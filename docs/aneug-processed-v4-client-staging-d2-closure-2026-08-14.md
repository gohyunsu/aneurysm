# AneuG processed-v4 D2 closure

## 판정

D2는 **transport-incomplete / no schema or scientific verdict**로 닫혔다.
Client에는 official transient v4가 exact size와 full SHA-256으로 확보됐지만,
introai9 transient object는 public-rounded 10.17GB partial에서 멈췄다. 허용된 SFTP
session 3/3을 모두 사용했으므로 같은 계약의 repair, resume 또는 네 번째 session은
없다.

이 결과는 AneuG-Flow 데이터셋, 60GB 저장 계획, tensor schema 또는 연구 질문의
실패가 아니다. 서버의 두 exact object가 모두 존재해야 실행할 수 있는 one-shot
checksum/schema PBS를 제출하지 않았으므로 field, case count, 80 phase, vector WSS,
mesh/case order와 geometry linkage는 이번 버전에서 평가되지 않았다.

## 확보된 것과 확보되지 않은 것

| 자산 | 현재 증거 | 해석 |
|---|---:|---|
| Client steady v4 | 9,632,510,050 bytes · official SHA-256 match | server size match 뒤 client copy 삭제 |
| Server steady v4 | 9,632,510,050 bytes | exact size · full server hash는 PBS 미실행 |
| Client transient v4 | 23,744,862,051 bytes · official SHA-256 match | exact client object · payload parse 0 |
| Server transient v4 | 10.17 GB · public-rounded | incomplete-only partial · exact object 아님 |
| Schema PBS | 0 attempt · marker 0 | checksum/schema verdict 없음 |
| Science/model/GPU | 0 | dataset/task/method 성능 판정 없음 |

## 세션 이력

1. SFTP session 1은 orchestration-turn interruption에서 닫혔고
   public-rounded 2.64GB server partial을 보존했다.
2. Session 2는 같은 client object와 remote partial을 `reput`으로 재개했다.
   두 번째 turn-lifecycle interruption에서 public-rounded 6.27GB를 보존했다.
3. 마지막 session 3은 turn과 분리한 Windows OpenSSH batch `reput`이었다.
   remote SSH connection reset과 broken pipe 뒤 public-rounded 10.17GB에서
   종료됐다. Endpoint와 exact private log metadata는 공개 저장소에 싣지 않는다.

세 오류는 모두 transport/orchestration evidence다. Client exact checksum이
일치하므로 source corruption으로 해석하지 않는다. 반대로 client checksum만으로
server exactness나 schema pass를 주장하지 않는다.

## 닫힌 경계

- D1 3/3과 D2 SFTP 3/3은 서로 다른 계약이며 각각 독립적으로 닫혀 있다.
- D2 checksum/schema PBS는 제출되지 않았으므로 그 one-shot budget은 소비되지
  않았지만, incomplete server input 때문에 실행 권한도 열리지 않는다.
- Server partial을 complete로 rename하지 않는다.
- Scientific P0, architecture selection, GPU training, validation/test, paper result와
  contribution은 모두 0이다.
- `junjinyong`은 사용하지 않는다.

다음 acquisition은 D2의 disguised repair가 될 수 없다. 명시적인 human selection을
받은 materially distinct version 또는 검증된 외부 transport 변화가 필요하다. 그 전에는
현재 exact client object와 server partial을 보존하고, 이미 확보된 BenchAnXplore/AneuX를
engineering·OOD 역할 이상으로 과장하지 않는다.

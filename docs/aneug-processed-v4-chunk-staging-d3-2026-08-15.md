# AneuG processed-v4 D3 · fixed-chunk acquisition

## 결정

사용자는 2026-08-15에 **D3 fixed-chunk transport**를 명시적으로 선택했다. D3는
닫힌 D2 monolithic reput의 네 번째 session이나 repair가 아니다. 이미 client에서
exact size와 SHA-256이 확인된 transient v4 하나를 다시 내려받지 않고, 1 GiB 이하의
서로 독립적으로 검증 가능한 23개 object로 순차 전송한다.

이 단계의 목적은 데이터 획득과 schema admission뿐이다. Scientific P0, architecture,
GPU training, validation/test, paper result와 contribution은 모두 닫혀 있다.

## 고정된 partition

| 항목 | 값 |
|---|---:|
| Source object | 23,744,862,051 bytes |
| Full SHA-256 | 141541ed…51c9 |
| Full chunk | 22 × 1,073,741,824 bytes |
| Final chunk | 122,541,923 bytes |
| Total | 23 chunks · exact byte sum |

Client에는 source와 현재 생성 중인 chunk 하나만 동시에 둔다. 각 chunk는 index,
offset, bytes와 SHA-256이 담긴 private manifest에 결박한다. Server size와 SHA-256이
모두 맞은 뒤에만 해당 local chunk를 지우며, 완료된 server chunk는 다시 올리지 않는다.
한 chunk가 중단되면 동일 chunk만 한 차례 resume할 수 있고, 세 번째 session이나 다른
내용으로의 교체는 없다.

## 60 GB 저장 상한

D2 partial을 보존한 채 23개 chunk를 모두 확보했을 때 server peak는
43,550,459,845 bytes다. 이 상태에서 곧바로 full object를 조립하면 상한을 넘으므로
다음 순서를 비보상적으로 고정한다.

1. 23개 server chunk의 size와 SHA-256을 모두 검증한다.
2. 그 뒤에만 closed D2 partial을 제거한다.
3. PBS CPU finalizer가 새 temporary object를 순서대로 조립한다.
4. Full 23,744,862,051-byte size와 SHA-256이 모두 맞은 뒤 atomic publish한다.
5. 그 뒤에만 23개 chunk를 제거한다.

재조립 순간 최대치는 steady + chunks + assembling object = 57,122,234,152 bytes로
60,000,000,000-byte 상한 안이다. Transport 성공 뒤에는 steady + transient =
33,377,372,101 bytes이고, schema 성공 뒤 compact norm을 남기고 steady 원본을
지우면 23,744,862,051 bytes다.

## 실행 경계

- Chunk transport: Windows OpenSSH SFTP → introai9; 외부 server download 없음.
- Transport finalizer: PBS 1회, CPU 4, 8 GB, GPU 0. 어떤 결과든 동일 finalizer 종료.
- Schema gate: finalizer가 full identity를 통과한 뒤 PBS 1회, CPU 4, 64 GB, GPU 0.
- Schema는 weights-only/mmap으로 case count, 80 phase, vector-WSS label, mesh order,
  geometry linkage와 작은 normalization metadata만 감사한다.
- Schema pass는 geometry leakage grouping과 split freeze만 허용한다.
- junjinyong은 접근·조회·전송·제출·모니터링하지 않는다.

D3 실패는 발생한 단계의 transport/schema verdict만 만든다. 데이터셋이나 과학 질문의
실패로 바꾸어 쓰지 않으며, closed D1/D2 결과도 성공으로 relabel하지 않는다.

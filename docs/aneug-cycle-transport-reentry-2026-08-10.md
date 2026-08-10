# AneuG-Flow cycle-functional P0-v2a transport re-entry

> **Outcome · closed:** Exact source `690035ae…` was submitted once on
> `introai9` as CPU/PBS job `115467.ECE-util1`. It reached scheduler state E
> with exit 1 after 8 seconds, but produced only a 319-byte
> execution-incomplete status. No aggregate result or raw PBS output
> materialized. Consequently the number of completed HEAD/range operations,
> verified bytes and transport/scientific gates are unevaluated; low-level cause
> is unresolved. The sole repair round is consumed. P0-v2a closes without
> rerun, P0-v2b, P1, method, architecture, GPU, outer test or paper claim.
> See `results/aneug_cycle_transport_p0_v2a_execution_20260810.json`.


**Prospective status · 2026-08-10 KST:** the historical P0-v1 remains closed as
execution-incomplete with no scientific verdict. A separate, one-round,
CPU-only transport preflight is preregistered for `introai9` PBS. It reads two
HEAD responses and four exact 1 MiB ranges—4 MiB total—and cannot download or
deserialize either full processed object. P0-v2a does not select a primary
problem, method, architecture, GPU experiment, outer test or paper claim.

## 1. Why this is a new version rather than a repaired result

The source-only candidate
**cycle-functional-compatible transient WSS surrogation** scored 33/40 under the
unchanged eight-axis admission rule. Historical P0-v1 then exited with code 28
before its first 9.63 GB object completed. No partial file, result JSON or raw
scheduler log survived, so the low-level cause was unresolved and the 16-check
scientific asset gate was never evaluated.

P0-v1 is not relabelled, rerun or used as positive evidence. The current
development rule permits a distinct prospective re-entry only when one failure
hypothesis, one changed layer, a total compute/data budget and a maximum repair
round are frozen first. P0-v2a therefore tests one hypothesis:

> whole-object transfer without a process-level preflight obscured whether the
> exact Hugging Face/Xet objects were reachable from the PBS environment.

Only the transport layer changes. Source commit, object identities, scientific
question, direct-prior boundary and no-model/no-GPU rule remain fixed. There is
one repair round; failure closes v2a without v2b.

## 2. Frozen public source identity

The official [AneuG-Flow dataset](https://huggingface.co/datasets/whding123/AneuG-Flow)
is pinned at `9dd418083899deddd93a67f9a6fca7a14304fa36` under CC BY-SA 4.0.
The [NeurIPS 2025 dataset paper](https://papers.nips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf)
reports 730 pulsatile synthetic geometries. The official code is pinned at
`4a090a0f12538deef6fcea88b81afe78ce38152e`.

| Object | Full size | Linked SHA-256 | Xet hash |
|---|---:|---|---|
| steady normalization source | 9,632,510,050 | `0c03c1d9…0177f` | `3325d68e…86a00` |
| transient registered source | 23,744,862,051 | `141541ed…51c9` | `3779ed53…393f4` |

The 2026-08-10 discovery read no tensor object. Two public HEAD requests
returned the exact repository commit, linked size, linked SHA-256, Xet hash and
`Accept-Ranges: bytes`. Four bounded local range requests froze the following
transport identities:

| Object/range | Inclusive bytes | Length | SHA-256 |
|---|---:|---:|---|
| steady prefix | 0–1,048,575 | 1 MiB | `c427dc13…3b845` |
| steady suffix | 9,631,461,474–9,632,510,049 | 1 MiB | `416f4c70…e5b1b` |
| transient prefix | 0–1,048,575 | 1 MiB | `ee53973d…82a87` |
| transient suffix | 23,743,813,475–23,744,862,050 | 1 MiB | `2a2d95cf…22ce` |

These 4 MiB are transport identity observations, not P0, case access, WSS
recovery or scientific evidence. The ephemeral bytes are not committed.

## 3. Exact v2a contract

The machine contract is
[`configs/aneug_cycle_transport_p0_v2a.json`](../configs/aneug_cycle_transport_p0_v2a.json).
One `introai9` PBS job requests 2 CPU, 4 GB RAM, GPU 0 and 15 minutes. It runs:

1. one HEAD operation per object;
2. one prefix and one suffix range per object;
3. retry count 0, 10-second connect timeout, 45/90-second curl deadlines and a
   separate process deadline;
4. exact final HTTP status, repository commit, size, linked ETag, range support,
   Xet hash, `Content-Range`, byte length and SHA-256 checks;
5. aggregate-only output with no URL token, remote path, byte payload or case ID.

The total payload budget is exactly 4,194,304 bytes. Resume, full-object
download, PyTorch/pickle deserialization, model code, GPU and outer-test access
are forbidden.

## 4. What pass and fail mean

- **Pass:** only the exact full-object route and byte-range identity are
  reachable under the bounded PBS contract. It authorizes registration of one
  separate v2b full-payload/weights-only reader gate with its own transfer and
  walltime budget.
- **Fail:** v2a closes after its single repair round. There is no v2b, P1,
  method, architecture or GPU work.
- **Neither outcome:** changes the 33/40 source score, repairs P0-v1, or proves
  that cycle-functional error is nontrivial.

The closest method remains RHSIA's transient-WSS graph Transformer with GHD and
steady augmentation. Generic graph attention, E(3) layers, functional losses,
direct TAWSS/OSI/RRT heads, POD/Fourier/DCT decoders and neural-operator
functional debiasing remain direct priors or controls. A method can be designed
only after v2b and a separate method-free P1 show a real field–functional task
gap.

All execution is restricted to `introai9` PBS. `junjinyong` must not be
connected to, queried, used for transfer/submission or monitored for AURORA.

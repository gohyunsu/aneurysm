# AneuG reference-floor source G0 execution record

Status: **execution-incomplete · no source-feasibility verdict · no scientific
verdict · exact contract closed**

## Outcome

The exact public source at commit `01ae2184facd76c9b2056557263fc92dff22831c`
was deployed as a clean detached checkout. Config, evaluator, test and PBS
wrapper hashes matched the prospective contract. The only authorized
CPU-only PBS attempt then ran as `116204.ECE-util1` on `introai9`.

PBS allocated four CPUs, 8 GB memory and zero GPUs. The job ended at state
`E`, exit status 2, after 2 minutes 14 seconds with 14,256 kB resident memory
and zero reported CPU time. Its minimal result reports
`public_source_request_failed`; the raw PBS log is empty. Consequently the
failed request and low-level cause cannot be identified and must not be
inferred. The source-feasibility gate and scientific gate were not evaluated.

## Artifact boundary

The private result is 408 bytes at SHA-256
`524df994071abad681d5369ea741b8dc0a680ae895aa568a62308fcfacfb4338`.
No aggregate source inventory or persistent probe/download cache materialized.
The empty raw PBS log has the standard empty-file SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
The public execution record is
[`results/aneug_reference_floor_g0_execution_20260814.json`](../results/aneug_reference_floor_g0_execution_20260814.json).
It exposes no private path or source credential.

## What this does and does not change

This outcome does not show that AneuG-Flow is absent, invalid or scientifically
unsuitable. It also does not repair the unresolved generator lineage or confirm
the transient WSS target. The separate read-only acquired-asset audit remains
valid: local AneuG geometry, BenchAnXplore, AneuX, CMHA and Aneurisk assets were
observed independently of this source request.

The prospective one-shot rule applies to incomplete outcomes. Therefore:

- this exact G0 may not be repaired or resubmitted;
- the candidate remains 31.0/40 inactive;
- scientific P0/P1, field access, method and trained architecture remain
  unauthorized;
- GPU, validation/test, outer test and paper claims remain closed; and
- any further study must be a materially different acquired-data task/version,
  not a disguised G0 retry.

No login-node GPU command ran. No action was performed on `junjinyong`.

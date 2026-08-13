# Aneumo response-fidelity P0 v3 execution record

Status: **execution-incomplete · no scientific verdict · 0/12 evaluated ·
exact contract closed**

## Outcome

After administrator-confirmed recovery, the public source, immutable P0 bytes,
private activation manifest, cache, base container and network-free runtime
wheel were pinned before field access. The final no-field preflight passed the
exact source/hash checks, clean checkout check, queue check, eight activation
tests and actual-manifest validation. The one authorized CPU-only PBS attempt
then ran as job `116146.ECE-util1`.

PBS allocated four CPUs, 16 GB memory and zero GPUs. The job finalized with
exit status 1 after 34 seconds, 19 CPU-seconds and 160,404 kB resident memory.
The one-shot status record says `execution_incomplete` and
`scientific_gate_evaluated=false`. No aggregate result materialized, so none of
the twelve registered endpoint-stability checks was evaluated. This is neither
a scientific pass nor a scientific failure.

## Artifact boundary

The only scientific-job artifact that materialized was the 313-byte private
status record at SHA-256
`4f517743c69cbe3a8be0f717118db989644e389675f9ff6136ff063f480db4c6`.
The requested PBS output file did not materialize. PBS trace records a post-job
file-processing error, but it does not expose the process-level cause. Without
an aggregate or raw PBS output, the low-level failure cause and the extent of
authorized train-field-array access are unknown. They must not be guessed from
runtime or memory use.

The public aggregate execution record is
[`results/aneumo_response_fidelity_p0_v3_execution_20260813.json`](../results/aneumo_response_fidelity_p0_v3_execution_20260813.json).
It exposes no private server path, field value or manuscript result.

## Scientific decision

The prospective one-shot rule applies even to execution-incomplete outcomes.
Therefore:

- same-contract repair and resubmission are forbidden;
- P1, method selection, architecture selection and GPU training remain closed;
- pressure and validation/test fields remain closed;
- outer testing, RF-C1--RF-C3 and manuscript claims remain closed; and
- the 32.5/40 source score is preserved only as conditional source history,
  not as an active paper identity or evidence of performance.

No action was performed on `junjinyong`.

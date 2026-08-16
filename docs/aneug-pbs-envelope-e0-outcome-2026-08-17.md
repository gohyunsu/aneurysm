# Data-free PBS envelope E0 outcome

E0 ran once on introai9 as PBS job `116512.ECE-util1` with CPU 1, 2 GB,
GPU 0 and a five-minute limit. It finalized F/exit 0 after five seconds.
The exact checkout, clean worktree, Python 3.9.12, Torch 2.6.0+cu118, job and
work-directory variables, wrapper-first persistent write and atomic JSON all
passed. The internal attempt log, status, completion marker and public result
materialized.

PBS nevertheless recorded `Post job file processing error`; the separately
requested scheduler stdout and stderr did not materialize. E0 therefore closes
with the runner envelope passed but full scheduler-output envelope failed. The
diagnostic is complete: future jobs must persist their own logs before shell
profile initialization or scientific access and must not rely on PBS stdout or
stderr delivery.

This finding does not identify D6's exact failing pre-runner line. Because E0's
persistent wrapper files survived the same scheduler staging error, post-job
staging alone does not explain why D6 created none. No dataset path, tensor,
field, split, private manifest, metric, method, model, training, validation,
outer test or GPU was accessed. There is no scientific or dataset verdict.

E0 is closed 1/1 and may never be repaired or rerun. D6 remains closed. The
only permitted continuation is design and registration of a fresh scientific
contract that incorporates the proven wrapper boundary; field access or model
execution still requires that separate contract. The public site was not
changed. Never use junjinyong.

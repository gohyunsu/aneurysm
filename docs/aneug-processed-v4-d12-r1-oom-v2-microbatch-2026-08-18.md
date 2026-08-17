# D12 R1 OOM and effective-batch-preserving retry

D12 R1 (`116607.ECE-util1`) imported and instantiated the exact released Graph
U-Net, then failed in the registered physical-batch-32 forward/backward smoke
before the first optimizer step. The 48 GB A6000 could not allocate the next
sparse GCN aggregation buffer. The immutable R1 directory contains its start
marker, internal traceback, exit status and final PBS record. It contains no
checkpoint, validation metric or scientific outcome; outer and auxiliary
values were never available to the runner.

The v2 correction keeps the released class and forward source, seed, 406/51
split, effective batch 32, area-weighted relative field objective, AdamW
settings, schedule and complete-cycle validation unchanged. It processes each
effective batch as four physical microbatches of eight. Every microbatch
numerator is divided by the single reference-energy denominator of the full
effective batch before backpropagation, so the accumulated objective equals
the registered batch-32 objective. The released model contains neither
batch-normalization nor dropout, avoiding microbatch-dependent state or masks.

The first v2 smoke executes all four microbatches and a complete accumulated
backward before training. A failure remains execution evidence; a pass proceeds
to the descriptive direct-prior comparison without an absolute performance
gate. The longer PBS envelope permits the high-cost snapshot model to finish
or early-stop, but does not change the maximum 80 coverage epochs. Outer,
auxiliary, method-combination and paper-claim authority remain closed.

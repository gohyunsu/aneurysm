# AneuG processed-v4 D6 v2 outcome

The sole D6 v2 attempt used exact Quality-passed source
`5a5f516d455e93dd32ce8da9bb2fe065817ff8e8` on introai9 PBS with CPU 4,
64 GB and GPU 0. Job `116501.ECE-util1` finalized F/exit 1 after two seconds
of walltime, zero recorded CPU time and 9,140 kB memory. The scheduler trace
records a post-job file-processing error.

Neither joined PBS output nor the private wrapper record directory
materialized. Because the source creates the record directory and attempt
marker before hashing or loading either processed object, their absence proves
that the runner did not start. Train/validation/outer/auxiliary cases evaluated
are 0/0/0/0. No source hash was completed inside the job and no scientific gate
was evaluated.

This is execution-incomplete, not a dataset defect, scientific failure or
scientific pass. D6 v2 is closed at 1/1. It may never be resumed, repaired,
rerun or relabelled. Bounded baseline development, model selection, GPU
training, validation/outer access, paper result and claim remain unauthorized.

The raw scheduler trace, absolute paths and private activation records remain
private. The public site is outside this workflow. junjinyong was not accessed.

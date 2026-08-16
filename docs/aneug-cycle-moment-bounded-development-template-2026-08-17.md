# Conditional bounded GPU development template

This template is non-executable and conditional on a separately selected D7
field-admission version completing with a scientific pass. D7 is currently
dormant, so the present GPU/model/data authority is zero.

## Resource observation and cap

A read-only introai9 PBS census on 2026-08-17 found `coss_agpu` enabled and
started with one running job and at most two GPUs per user, and `coss_a6gpu`
with one running job and one GPU per user. Both expose a 72-hour default
walltime. Scheduler fields did not identify GPU models and node availability
was heterogeneous; node names are not treated as hardware identity.

Any future selected contract therefore uses one GPU per job, one job at a
time, an explicit 24-hour job limit and a first-allocation runtime smoke that
records device, driver, CUDA, Torch, memory and container hashes. No A100,
A6000 or other device is assumed before that allocation.

The nonfungible total cap is 360 requested GPU-hours: R0 12, R1 220, one
possible R2 repair 108 and one-shot C0 outer evaluation 20. Accepted failed or
preempted jobs consume their round budget. Unused hours cannot create a new
variant. There are at most 32 accepted GPU jobs, 29 training jobs and one
repair round. Each variant–seed pair has one accepted PBS attempt; an accepted
failure or preemption cannot be resubmitted under the same identity.

## Prospective rounds

- **R0:** runtime, data pipeline and exact-code feasibility only; seed 17,
  maximum two jobs, train access only and no performance/reproduction claim.
- **R1:** frozen validation-only development. The primary direct/readout pair
  uses seeds 1103/2207/3301/4409/5501. Controls use the first three. Outer and
  auxiliary values remain sealed.
- **R2:** optional single-hypothesis repair only. It uses fresh primary-pair
  seeds 6607/7703/8807/9901/11113 and creates a new version. It may change only
  the registered optimizer schedule/length, cone parameterization or gradient
  accumulation corresponding to one train-diagnostic attribution. No second
  repair exists.
- **C0:** one outer evaluation of frozen rows/checkpoints. It performs no
  training and cannot be rerun, repaired or relabelled.

## Selection conjunction

Candidate/direct field-error ratio must have a component-bootstrap upper bound
at most 1.02. TAWSS-error and valid-support OSI-MAE point ratios must each be at
most 0.95 and their bootstrap upper bounds below one. At least four of five
paired seeds must improve both functionals. These requirements form one
noncompensatory conjunction under 10,000 component bootstrap draws with fixed
seed 271828. RRT is redundant secondary. Invalid predictions are penalized and
coverage is reported.

Every accepted job, failed variant, seed, commit, config, checkpoint and
resource use is private-ledgered. PBS scheduler stdout/stderr is not evidence;
the early internal persistent record proven by E0 is mandatory.

This file creates no selected development contract, GPU runner, PBS wrapper,
field read, model, outer access, result table, figure or paper claim. The public
site is not maintained. Never use junjinyong.

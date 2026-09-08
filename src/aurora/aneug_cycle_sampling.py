"""Explicit balanced cycle exposure schedules, separate from unique labels.

No dataset is opened and no subset is selected here. The caller must supply
only admitted unique training cases and fit their preprocessing separately.
Equal exposures/updates do not establish equal GPU time or model capacity.
"""
from __future__ import annotations

import random


KEY = "cycle_sampling"
SCHEMA = "aurora.balanced_cycle_sampling.v1"


def sampling_contract(unique_cases: int, examples_per_epoch: int, seed: int):
    if (type(unique_cases) is not int or unique_cases < 1
            or type(examples_per_epoch) is not int or examples_per_epoch < unique_cases
            or type(seed) is not int or seed < 0):
        raise ValueError("positive unique cases, covering exposure count and nonnegative seed required")
    return dict(schema_version=SCHEMA, algorithm="balanced_repeated_permutations_v1",
                unique_training_cases=unique_cases, examples_per_epoch=examples_per_epoch,
                training_seed=seed, round_seed_stride=1_000_003)


def epoch_examples(provenance, unique_cases: int, seed: int):
    """Absence means the preserved legacy one-visit-per-case schedule."""
    if KEY not in provenance:
        if type(unique_cases) is not int or unique_cases < 1:
            raise ValueError("positive unique training count required")
        return unique_cases
    value = provenance[KEY]
    if (not isinstance(value, dict) or any(type(value.get(key)) is not int for key in
            ("unique_training_cases", "examples_per_epoch", "training_seed", "round_seed_stride"))):
        raise ValueError("explicit cycle sampling contract required")
    expected = sampling_contract(unique_cases, value.get("examples_per_epoch"), seed)
    if value != expected:
        raise ValueError("cycle sampling contract differs from admitted cases or seed")
    return expected["examples_per_epoch"]


def epoch_order(unique_cases: int, examples: int, seed: int, epoch: int):
    """Balanced repeated shuffles; the first round is the legacy exact order."""
    sampling_contract(unique_cases, examples, seed)
    if type(epoch) is not int or epoch < 1:
        raise ValueError("positive one-based epoch required")
    order = []
    round_index = 0
    while len(order) < examples:
        permutation = list(range(unique_cases))
        random.Random(seed + epoch + round_index * 1_000_003).shuffle(permutation)
        order.extend(permutation[:examples - len(order)])
        round_index += 1
    return order

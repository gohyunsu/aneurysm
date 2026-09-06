"""One admitted steady field per complete transient cycle, with explicit cost.

The caller supplies the already audited lazy stream and eligible rows. This
module neither opens an archive nor decides scientific eligibility. Its sample
order is independent of model/RNG state and can be reconstructed on resume
without reading any field. A steady field is never duplicated over phases.
"""
from __future__ import annotations

import math

from .aneug_release_730_matched_steady_stream import epoch_exposure_indices
from .aneug_release_730_steady_exposure_schedule import ordered_digest


class PairedSteadySupervision:
    def __init__(self, stream, eligible_indices, *, seed: int, loss_weight: float):
        eligible = tuple(eligible_indices)
        if (not eligible or len(set(eligible)) != len(eligible)
                or any(type(i) is not int or i < 0 for i in eligible)):
            raise ValueError("unique explicitly eligible integer steady rows required")
        if type(seed) is not int or seed < 0:
            raise ValueError("nonnegative steady schedule seed required")
        if isinstance(loss_weight, bool) or not math.isfinite(loss_weight) or loss_weight <= 0:
            raise ValueError("positive steady weight required; use no stream for T-only")
        if not callable(getattr(stream, "decode", None)):
            raise ValueError("audited lazy stream with decode required")
        self.stream, self.eligible = stream, eligible
        self._eligible_set = frozenset(eligible)
        self.seed, self.loss_weight = seed, float(loss_weight)

    @property
    def contract(self):
        return dict(schedule="one_steady_field_per_transient_cycle_v1",
                    eligible_case_count=len(self.eligible),
                    eligible_order_sha256=ordered_digest(self.eligible),
                    seed=self.seed, loss_weight=self.loss_weight,
                    steady_equals_cycle_mean=False)

    def indices(self, epoch: int, train_cases: int):
        if type(epoch) is not int or epoch < 1 or type(train_cases) is not int or train_cases < 1:
            raise ValueError("one-based epoch and positive train case count required")
        return list(epoch_exposure_indices(self.eligible, epoch=epoch - 1,
                                          cases_per_epoch=train_cases, seed=self.seed))

    def decode(self, row: int):
        # The underlying audited stream also checks eligibility before access.
        if row not in self._eligible_set:
            raise ValueError("steady row not admitted")
        return self.stream.decode(row)

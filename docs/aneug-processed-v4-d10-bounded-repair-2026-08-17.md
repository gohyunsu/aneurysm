# D10 bounded validation repair

D9 failed and remains immutable negative development evidence. D9A then showed
that exact projection is numerically correct but creates a large field/OSI
tradeoff when applied only at validation. Separately, the D9 direct field error
improved at every epoch and selected the final epoch after its cosine learning
rate had decayed tenfold. The pinned official AneuG trainer defaults to 251
epochs, while D9 used 20; official settings are duration rationale only because
its random split, sampler, architecture and losses are not a matched local row.

D10 prospectively caps development at two repair rounds and two training jobs.
Round 1 tests only the optimization-horizon hypothesis: the same direct model,
seed, cache, loss, metric, threshold and cosine family run for at most 251
epochs, with a 60-epoch minimum and patience 25. Field rL2 must remain at or
below the original 0.35 threshold. Failure abandons the custom backbone for an
official-architecture adaptation; it does not trigger another horizon search.

Round 2 is closed. It may receive a separate implementation and private
activation only if Round 1 passes. Its sole change is to score moment training
through the same exact projection used at validation. A Round 2 pass would
permit fresh-seed prospective validation re-entry, not outer access or a paper
claim. All numeric results remain private, all existing attempts remain
append-only, and the outer/auxiliary cases stay sealed.

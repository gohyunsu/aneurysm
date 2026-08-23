# Release-730 response-oracle comparison

This result-pending utility compares every registered response-oracle rank to
the completed released Graph U-Net adapter on the identical 73 validation
geometries. It exists because the historical comparison tool is fixed to the
obsolete v4 51-case protocol and cannot safely parse the release-730 result
schemas.

The comparison accepts only the exact private Graph U-Net and response-oracle
result roles, zero locked-test/79-extra reads, identifier-free rows, exact
result hashes, both terminal-record hashes and the shared frozen validation
case-set and ordered-loader digests. For each rank it
reports raw metric means and 10,000 paired case-resample percentile intervals
for field rL2, TAWSS error, OSI MAE and OSI coverage. It also reports the
metric Pareto set and a rank-only Pareto set that treats active basis storage
as an explicit cost. Before any oracle values are observed, R1 candidate
nomination is fixed to the minimum, lower-median and maximum positive ranks on
that storage-aware front (or all positive ranks when at most three remain).
Rank zero stays a reported mean-response control rather than consuming a
learned-coordinate candidate slot.

No absolute cutoff, learned-model interpretation, final rank selection or
global-branch decision is emitted. Nomination only bounds the ranks that may
enter learned validation. The oracle uses true validation amplitude and
coefficients: a favorable result is only a representation ceiling. Every
learned response-only rank must still earn its place through validation
prediction, and later comparisons must include the strongest learned
backbone. The tool remains non-executable until both exact results exist and a
fresh private activation binds their result, terminal and ordering hashes. It
never reads the locked test or
processed-only extras and never publishes numeric development results.

# AneuG-Flow processed-v4 client staging D2

## Why this is not D1 attempt 4

D1 is immutable closed history: three introai9 compute-node HTTPS attempts,
partial bytes zero and no schema verdict. D2 never asks a compute or login node
to download from the public source. It uses a separately verified client route:

`official HTTPS → sequential exact client cache → Windows OpenSSH SFTP → introai9 PBS checksum/schema`

Before registration, HEAD requests confirmed both exact object identities. One
67,108,864-byte transient range was read to a null sink only to measure route
feasibility; HTTP 206 returned at 5,697,265 bytes/s. Nothing was persisted or
parsed and no scientific metric was computed. Full-object access begins only
after the D2 source passes Quality.

## Storage and sequencing

D2 first downloads and checksums the 9,632,510,050-byte steady v4 object,
uploads it as temporary server input, then removes the client steady copy. It
then downloads and checksums the 23,744,862,051-byte transient v4 object and
uploads it. This makes the maximum client payload one transient object, the
server peak 33,377,372,101 bytes and the maximum simultaneous new bytes
57,122,234,152—below the 60 GB workflow cap. V5, raw blood/wall, 14,000-case
steady CFD and `cfd/` remain excluded.

Each role may resume the same partial object for at most three client sessions
and three SFTP sessions. Endpoint, revision, size and SHA-256 cannot change.
Private local/server paths are never published.

## One-shot schema gate

Only after both server file sizes match does one introai9 CPU/PBS job verify
both SHA-256 values and run the weights-only, memory-mapped schema/linkage
audit. Any outcome closes that schema contract; there is no repair or rerun.
A pass deletes the full steady object after writing the compact norm manifest
and opens only geometry near-duplicate grouping and a development-split freeze.
It does not open scientific P0, method selection, GPU training, outer test or a
paper result.

## Current transport state

Steady v4 completed in client session 1 at exact size 9,632,510,050 bytes and
full official SHA-256 `0c03c1d9…0177f`. Its payload was not parsed. Server
objects remain 0/2, transient has not started and the one-shot schema gate is
untouched. Next, upload this exact object through Windows OpenSSH SFTP, verify
server size, remove the client steady copy and begin transient acquisition.

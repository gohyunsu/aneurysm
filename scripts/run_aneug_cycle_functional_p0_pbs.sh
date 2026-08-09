#!/usr/bin/env bash
#PBS -N aurora_aneug_p0
#PBS -q coss_agpu
#PBS -l select=1:ncpus=8:mem=128gb
#PBS -l walltime=06:00:00
#PBS -j oe

set -euo pipefail

: "${AURORA_P0_REPO:?set the exact clean public checkout path}"
: "${AURORA_P0_DATA_DIR:?set a private writable source-cache directory}"
: "${AURORA_P0_OUTPUT:?set a private aggregate-result path}"
: "${AURORA_P0_CONTAINER:?set the pinned readable Singularity image}"
: "${AURORA_P0_SOURCE_COMMIT:?set the exact registered public commit}"

cd "$AURORA_P0_REPO"

OBSERVED_COMMIT="$(git rev-parse HEAD)"
if [[ "$OBSERVED_COMMIT" != "$AURORA_P0_SOURCE_COMMIT" ]]; then
  echo "source commit mismatch" >&2
  exit 90
fi
if [[ -n "$(git status --short)" ]]; then
  echo "source checkout is not clean" >&2
  exit 91
fi

CONFIG="$AURORA_P0_REPO/configs/aneug_cycle_functional_p0.json"
mkdir -p "$AURORA_P0_DATA_DIR" "$(dirname "$AURORA_P0_OUTPUT")"

read_config_value() {
  local role="$1"
  local key="$2"
  singularity exec --cleanenv \
    --bind "$AURORA_P0_REPO:/workspace:ro" \
    "$AURORA_P0_CONTAINER" \
    python -c "import json; print(json.load(open('/workspace/configs/aneug_cycle_functional_p0.json'))['source']['processed_files']['$role']['$key'])"
}

download_exact() {
  local role="$1"
  local name
  local url
  name="$(read_config_value "$role" name)"
  url="$(read_config_value "$role" url)"
  local destination="$AURORA_P0_DATA_DIR/$name"
  local partial="$destination.partial"
  if [[ -e "$destination" || -e "$partial" ]]; then
    echo "registered P0 requires an empty destination for $name" >&2
    exit 92
  fi
  curl --fail --location --retry 0 --output "$partial" "$url"
  mv "$partial" "$destination"
}

download_exact steady
download_exact transient

STEADY_NAME="$(read_config_value steady name)"
TRANSIENT_NAME="$(read_config_value transient name)"

singularity exec --cleanenv \
  --bind "$AURORA_P0_REPO:/workspace:ro,$AURORA_P0_DATA_DIR:/data:ro,$(dirname "$AURORA_P0_OUTPUT"):/output" \
  "$AURORA_P0_CONTAINER" \
  env PYTHONPATH=/workspace/src \
  python /workspace/scripts/audit_aneug_cycle_functional_p0.py \
    --config /workspace/configs/aneug_cycle_functional_p0.json \
    --steady "/data/$STEADY_NAME" \
    --transient "/data/$TRANSIENT_NAME" \
    --source-commit "$AURORA_P0_SOURCE_COMMIT" \
    --output "/output/$(basename "$AURORA_P0_OUTPUT")"

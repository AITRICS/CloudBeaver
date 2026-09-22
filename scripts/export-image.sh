#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# shellcheck disable=SC1091
. "$project_dir/scripts/image-target.sh"

target=${1:-}
resolve_image_target "$target"

mkdir -p "$project_dir/image"
output="$project_dir/image/$tar_name"

docker image save --output "$output" "$image_tag"
ls -lh "$output"

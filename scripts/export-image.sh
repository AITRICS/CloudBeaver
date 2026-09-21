#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
image_name=${IMAGE_NAME:-cloudbeaver:26.2.0-r1}
architecture=$(docker image inspect "$image_name" --format '{{.Architecture}}')
mkdir -p "$project_dir/image"
output="$project_dir/image/cloudbeaver_26.2.0-r1_${architecture}.tar"

docker image save --output "$output" "$image_name"
ls -lh "$output"

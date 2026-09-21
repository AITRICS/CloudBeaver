#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
image_name=${IMAGE_NAME:-cloudbeaver:26.2.0-r1}
base_image=${BASE_IMAGE:-dbeaver/cloudbeaver:26.2.0}
output_dir="$project_dir/build/output"
plugin_src=$(mktemp -d)
cid=""

cleanup() {
  if [ -n "$cid" ]; then
    docker rm "$cid" >/dev/null 2>&1 || true
  fi
  rm -rf "$plugin_src"
}
trap cleanup EXIT

cid=$(docker create "$base_image")
docker cp "$cid:/opt/cloudbeaver/server/plugins/." "$plugin_src/"
docker rm "$cid" >/dev/null
cid=""

python3 "$project_dir/build/patch_plugins.py" "$plugin_src" "$output_dir"
docker build --pull=false --tag "$image_name" "$project_dir"
docker image inspect "$image_name" --format 'built {{.RepoTags}} {{.Id}} {{.Architecture}}'

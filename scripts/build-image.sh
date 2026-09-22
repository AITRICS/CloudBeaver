#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# shellcheck disable=SC1091
. "$project_dir/scripts/image-target.sh"

target=${1:-}
resolve_image_target "$target"

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

docker pull --platform "$platform" "$base_image"

cid=$(docker create --platform "$platform" "$base_image")
docker cp "$cid:/opt/cloudbeaver/server/plugins/." "$plugin_src/"
docker rm "$cid" >/dev/null
cid=""

python3 "$project_dir/build/patch_plugins.py" "$plugin_src" "$output_dir"
DOCKER_BUILDKIT=1 docker build \
  --platform "$platform" \
  --pull=false \
  --tag "$image_tag" \
  "$project_dir"

if [ "$target" = "m-chip" ]; then
  docker tag "$image_tag" cloudbeaver:26.2.0-r1
fi

docker image inspect "$image_tag" --format 'built {{.RepoTags}} {{.Id}} {{.Architecture}} {{.Os}}'
"$project_dir/scripts/export-image.sh" "$target"

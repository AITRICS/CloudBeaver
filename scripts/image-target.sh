# 대상별 Docker 플랫폼. linux와 intel-mac은 둘 다 linux/amd64다.
resolve_image_target() {
  case "$1" in
    linux)
      platform=linux/amd64
      image_tag=cloudbeaver:26.2.0-r1-amd64
      tar_name=cloudbeaver_26.2.0-r1_linux_amd64.tar
      ;;
    intel-mac)
      platform=linux/amd64
      image_tag=cloudbeaver:26.2.0-r1-amd64
      tar_name=cloudbeaver_26.2.0-r1_linux_amd64.tar
      ;;
    m-chip)
      platform=linux/arm64
      image_tag=cloudbeaver:26.2.0-r1-arm64
      tar_name=cloudbeaver_26.2.0-r1_mac_arm64.tar
      ;;
    *)
      echo "usage: $0 linux|intel-mac|m-chip" >&2
      echo "  linux      x86_64 Linux" >&2
      echo "  intel-mac  Intel Mac (linux/amd64, linux tar와 동일)" >&2
      echo "  m-chip     Apple Silicon Mac" >&2
      exit 1
      ;;
  esac
}

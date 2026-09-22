# CloudBeaver

`cloudbeaver:26.2.0-r1`

## 지원 DB

아래 버전의 DB를 지원한다.

| DB | 버전 |
|---|---|
| Oracle (Modern) | 19c, 21c, 23ai, 26ai |
| Oracle (Compatibility) | 11.2.0.4, 12c, 18c, 19c, 21c |
| Oracle (Legacy) | 9i, 10g, 11g |
| MySQL | 8.0.36, 8.0.40, 8.4.7 |
| SQL Server (Modern) | 2016~2025 |
| SQL Server (Legacy) | 2008 R2~2014 |

## 구성

| 경로 | 역할 |
|---|---|
| `Dockerfile` | 이미지 빌드 |
| `docker-compose.yml` | 실행 설정 |
| `drivers/` | 내장 JDBC 드라이버 |
| `build/` | CloudBeaver 드라이버 프로필 패치 |
| `scripts/` | 이미지 빌드와 tar export |
| `image/` | 미리 말아 둔 이미지 tar. GitHub 용량 제한으로 레포에는 올리지 않으며, 빌드가 안 되면 로컬 tar를 사용한다 |
| `workspace/` | 실행 중 저장되는 설정. 레포에는 빈 폴더만 두고, 첫 기동 때 CloudBeaver가 채운다 |

## 이미지 빌드

로컬에 `dbeaver/cloudbeaver:26.2.0`과 `python3`가 있어야 한다. JDBC JAR는 `drivers/`에 들어 있으므로 드라이버 다운로드는 필요 없다. 대상 아키텍처의 베이스 이미지가 없으면 Docker Hub pull이 필요하다.

```sh
./scripts/build-image.sh linux       # x86_64 Linux → linux/amd64
./scripts/build-image.sh intel-mac   # Intel Mac → linux/amd64 (linux tar와 동일)
./scripts/build-image.sh m-chip      # Apple Silicon Mac → linux/arm64
```

대상 서버에서 `uname -m`이 `x86_64`면 `linux`, `arm64`/`aarch64`면 `m-chip`이다. Intel Mac도 `x86_64`라 `linux`와 같은 amd64 이미지가 나온다.

만들어지는 tar:

| 대상 | tar |
|---|---|
| Linux / Intel Mac | `image/cloudbeaver_26.2.0-r1_linux_amd64.tar` |
| M칩 Mac | `image/cloudbeaver_26.2.0-r1_mac_arm64.tar` |

빌드가 안 되면 tar를 로드한다.

```sh
# x86_64 Linux, Intel Mac
docker load -i image/cloudbeaver_26.2.0-r1_linux_amd64.tar

# Apple Silicon Mac
docker load -i image/cloudbeaver_26.2.0-r1_mac_arm64.tar
```

로드 후 태그가 `cloudbeaver:26.2.0-r1-amd64` 또는 `cloudbeaver:26.2.0-r1-arm64`로 들어간다. Compose가 쓰는 이름은 `cloudbeaver:26.2.0-r1`이므로 한 번 맞춰 준다.

```sh
# Linux / Intel Mac
docker tag cloudbeaver:26.2.0-r1-amd64 cloudbeaver:26.2.0-r1

# M칩 Mac
docker tag cloudbeaver:26.2.0-r1-arm64 cloudbeaver:26.2.0-r1
```

## 실행

```sh
docker compose up -d
```

브라우저에서 `http://<서버IP>:8978` 로 접속한다. 설정은 `./workspace`에 남는다.

같은 서버의 DB에 붙을 때 Host에 `localhost`를 넣으면 안 된다. CloudBeaver 컨테이너 자신이다. DB 서버 IP를 넣는다.

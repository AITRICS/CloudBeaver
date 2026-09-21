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

로컬에 `dbeaver/cloudbeaver:26.2.0`과 `python3`가 있어야 한다. JDBC JAR는 `drivers/`에 들어 있으므로 빌드 때 인터넷이 필요 없다.

```sh
./scripts/build-image.sh
```

`cloudbeaver:26.2.0-r1` 이미지가 만들어진다. tar를 다시 뽑을 때는 `./scripts/export-image.sh` 한다.

빌드가 안 되면 `image/`의 tar를 로드한다.

```sh
docker load -i image/cloudbeaver_26.2.0-r1_<arch>.tar
```

## 실행

```sh
docker compose up -d
```

브라우저에서 `http://<서버IP>:8978` 로 접속한다. 설정은 `./workspace`에 남는다.

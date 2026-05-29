# epics-github-actions

GitHub Actions for workflows that need [EPICS Base](https://epics-controls.org/) or [PVXS](https://mdavidsaver.github.io/pvxs/) installed.

All three actions accept a `method` input that selects how EPICS is provided:

| `method` | How it works | Requires |
|---|---|---|
| `conda` *(default)* | Installs packages from [conda-forge](https://conda-forge.org/) via [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) | nothing extra |
| `docker` | Pulls a pre-built image from [epics-containers](https://github.com/epics-containers), installs thin wrapper scripts on `$PATH` | Docker (ubuntu runners only); GHCR login step (see [docker example](#docker)) |
| `compile` | Downloads source from GitHub and builds with `make` / `cmake`, result is cached | C++ compiler, ~5–10 min first run; **EPICS Base ≥ 7.0.9** (older releases fail to compile on modern Clang/GCC) |

After any of these setup actions, `caget`, `caput`, `softIoc`, etc. are available as plain shell commands in subsequent `bash` steps.

---

## Actions

### `setup-epics`

Installs `epics-base`.

```yaml
- uses: jacomago/epics-github-actions/setup-epics@v1
  with:
    method: conda          # 'conda' | 'docker' | 'compile'

    # conda options
    epics-version: ''      # pin version, e.g. "7.0.9" (default: latest)
    environment-name: epics

    # docker options
    image: 'ghcr.io/epics-containers/epics-base-developer:7.0.10ec1'
    network-name: epics-net

    # compile options
    install-prefix: '${{ github.workspace }}/.epics'
```

**Outputs:** `epics-host-arch`

**Environment variables set for all methods:** `EPICS_HOST_ARCH`

Additional variables per method:
- `conda`: `EPICS_BASE`, `LD_LIBRARY_PATH` (Linux only)
- `docker`: `EPICS_DOCKER_IMAGE`, `EPICS_DOCKER_NETWORK`
- `compile`: `EPICS_BASE`, `LD_LIBRARY_PATH` / `DYLD_LIBRARY_PATH`

---

### `setup-pvxs`

Installs `epics-base` **and** `pvxs`. Adds `pvxget`, `pvxput`, `pvxmonitor`, `pvxinfo`, `softIocPVX`.

```yaml
- uses: jacomago/epics-github-actions/setup-pvxs@v1
  with:
    method: conda

    # conda options
    pvxs-version: ''       # e.g. "1.5.1" (default: latest)
    epics-version: ''
    environment-name: epics

    # docker options
    image: 'ghcr.io/epics-containers/epics-base-developer:7.0.10ec1'
    network-name: epics-net

    # compile options
    install-prefix: '${{ github.workspace }}/.epics'
```

**Outputs:** `epics-host-arch`

**Environment variables set for all methods:** `EPICS_HOST_ARCH`

Additional variables per method:
- `conda`: `EPICS_BASE`, `PVXS`, `LD_LIBRARY_PATH` (Linux only)
- `docker`: `EPICS_DOCKER_IMAGE`, `EPICS_DOCKER_NETWORK`, `PVXS_DOCKER_IMAGE`
- `compile`: `EPICS_BASE`, `LD_LIBRARY_PATH` / `DYLD_LIBRARY_PATH`

---

### `start-softioc`

Starts a `softIocPVA` (or `softIocPVX`) instance and waits until it is ready. Pass the same `method` as used in `setup-epics` / `setup-pvxs`.

```yaml
- uses: jacomago/epics-github-actions/start-softioc@v1
  with:
    method: conda            # must match setup-epics / setup-pvxs
    db-file: path/to/records.db
    macros: 'P=TEST:,R=REC:'
    use-pvxs: 'false'        # 'true' → softIocPVX (requires setup-pvxs)
    wait-pv: 'TEST:STATUS'   # poll this PV until the IOC is up (recommended)
    wait-timeout: '10'       # fallback sleep if wait-pv is not set
    poll-timeout: '30'       # seconds to poll wait-pv before giving up

    # docker method only
    container-name: softioc
    docker-image: ''         # defaults to PVXS_DOCKER_IMAGE / EPICS_DOCKER_IMAGE
    docker-network: ''       # defaults to EPICS_DOCKER_NETWORK
```

`wait-pv` is recommended — polls up to `poll-timeout` seconds (default 30) instead of a fixed sleep.

When `method: docker`, `start-softioc` also sets `EPICS_CA_AUTO_ADDR_LIST=NO`,
`EPICS_CA_ADDR_LIST`, `EPICS_PVA_AUTO_ADDR_LIST`, and `EPICS_PVA_ADDR_LIST` to
restrict channel access to the IOC container.

---

## Example workflows

### conda (default)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jacomago/epics-github-actions/setup-epics@v1
      - uses: jacomago/epics-github-actions/start-softioc@v1
        with:
          db-file: ioc/db/records.db
          macros: P=MY:
          wait-pv: MY:HEARTBEAT
      - name: Read PVs
        shell: bash
        run: caget MY:HEARTBEAT MY:STATUS
```

### docker

GHCR requires an authenticated pull even for public images. Add `docker/login-action` before the setup step.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest   # Docker required
    permissions:
      packages: read
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: jacomago/epics-github-actions/setup-epics@v1
        with:
          method: docker
      - uses: jacomago/epics-github-actions/start-softioc@v1
        with:
          method: docker
          db-file: ioc/db/records.db
          macros: P=MY:
          wait-pv: MY:HEARTBEAT
      - name: Read PVs
        shell: bash
        run: caget MY:HEARTBEAT MY:STATUS
```

### compile

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jacomago/epics-github-actions/setup-epics@v1
        with:
          method: compile
          epics-version: '7.0.9'
      - uses: jacomago/epics-github-actions/start-softioc@v1
        with:
          method: compile
          db-file: ioc/db/records.db
          macros: P=MY:
          wait-pv: MY:HEARTBEAT
      - name: Read PVs
        shell: bash
        run: caget MY:HEARTBEAT MY:STATUS
```

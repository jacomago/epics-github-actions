# epics-github-actions

GitHub Actions for workflows that need [EPICS Base](https://epics-controls.org/) or [PVXS](https://mdavidsaver.github.io/pvxs/) installed.

All three actions accept a `method` input that selects how EPICS is provided:

| `method` | How it works | Requires |
|---|---|---|
| `conda` *(default)* | Installs packages from [conda-forge](https://conda-forge.org/) via [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) | nothing extra |
| `docker` | Pulls a pre-built image from [epics-containers](https://github.com/epics-containers), installs thin wrapper scripts on `$PATH` | Docker (ubuntu runners only) |
| `compile` | Downloads source from GitHub and builds with `make` / `cmake`, result is cached | C++ compiler, ~5–10 min first run |

After any of these setup actions, `caget`, `caput`, `softIocPVA`, etc. are available as plain shell commands in subsequent `bash` steps.

---

## Actions

### `setup-epics`

Installs `epics-base`.

```yaml
- uses: jacomago/epics-github-actions/setup-epics@v1
  with:
    method: conda          # 'conda' | 'docker' | 'compile'

    # conda options
    epics-version: ''      # pin version, e.g. "7.0.8" (default: latest)
    environment-name: epics

    # docker options
    image: 'ghcr.io/epics-containers/epics-base:7.0.8r1.0'
    network-name: epics-net

    # compile options
    install-prefix: '${{ github.workspace }}/.epics'
```

**Outputs:** `epics-host-arch`

**Environment variables set for all methods:** `EPICS_HOST_ARCH`

Additional variables per method:
- `conda`: `LD_LIBRARY_PATH` (Linux only)
- `docker`: `EPICS_DOCKER_IMAGE`, `EPICS_DOCKER_NETWORK`
- `compile`: `EPICS_BASE`, `LD_LIBRARY_PATH` / `DYLD_LIBRARY_PATH`

---

### `setup-pvxs`

Installs `epics-base` **and** `pvxs`. Adds `pvget`, `pvput`, `pvmonitor`, `pvinfo`, `softIocPVX`.

```yaml
- uses: jacomago/epics-github-actions/setup-pvxs@v1
  with:
    method: conda

    # conda options
    pvxs-version: ''       # e.g. "1.3.1" (default: latest)
    epics-version: ''
    environment-name: epics

    # docker options
    image: 'ghcr.io/epics-containers/pvxs:1.3.1r1.0'
    network-name: epics-net

    # compile options
    install-prefix: '${{ github.workspace }}/.epics'
```

**Outputs:** `epics-host-arch`

---

### `start-softioc`

Starts a `softIocPVA` (or `softIocPVX`) instance and waits until it is ready. Pass the same `method` as used in `setup-epics` / `setup-pvxs`.

```yaml
- uses: jacomago/epics-github-actions/start-softioc@v1
  with:
    method: conda            # must match setup-epics / setup-pvxs
    db-file: path/to/records.db
    macros: 'P=TEST:,R=REC:'
    ioc-name: softioc
    use-pvxs: 'false'        # 'true' → softIocPVX (requires setup-pvxs)
    wait-pv: 'TEST:STATUS'   # poll this PV until the IOC is up (recommended)
    wait-timeout: '10'       # fallback sleep if wait-pv is not set
    container-name: softioc  # docker method only
```

`wait-pv` is recommended — polls `caget` up to 30 s instead of a fixed sleep.

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

```yaml
jobs:
  test:
    runs-on: ubuntu-latest   # Docker required
    steps:
      - uses: actions/checkout@v4
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
          epics-version: '7.0.8'
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

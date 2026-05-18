# epics-github-actions

GitHub Actions for workflows that need [EPICS Base](https://epics-controls.org/) or [PVXS](https://mdavidsaver.github.io/pvxs/) installed. Tools are provided via pre-built Docker images (e.g. from [epics-containers](https://github.com/epics-containers)) without requiring micromamba or conda.

> **Note:** Docker must be available on the runner. All GitHub-hosted **ubuntu** runners include Docker out of the box. macOS GitHub-hosted runners have Docker Desktop available but it may not be started automatically — ensure Docker is running before using these actions on macOS.

## Actions

### `setup-epics`

Pulls a pre-built EPICS Docker image, creates a shared Docker network, and installs thin wrapper scripts (`caget`, `caput`, `camonitor`, `cainfo`, `softIocPVA`) onto `$PATH`.

```yaml
- uses: jacomago/epics-github-actions/setup-epics@v1
  with:
    image: 'ghcr.io/epics-containers/epics-base:7.0.8r1.0'   # Docker image to pull
    network-name: 'epics-net'                                   # Docker network for CA/PVA
```

**Outputs:** `epics-host-arch`

**Environment variables set:**
- `EPICS_HOST_ARCH` — architecture string for the current runner
- `EPICS_DOCKER_IMAGE` — image used, consumed by `start-softioc`
- `EPICS_DOCKER_NETWORK` — network name, consumed by `start-softioc`

After this step, `caget`, `caput`, `camonitor`, `cainfo`, and `softIocPVA` are available as plain shell commands (each delegates to `docker run --rm --network <network> <image> <cmd>`). No `micromamba-shell` is required.

---

### `setup-pvxs`

Pulls a pre-built PVXS Docker image, creates a shared Docker network, and installs wrapper scripts for both CA tools (`caget`, `caput`, `camonitor`, `cainfo`, `softIocPVA`) and PVXS tools (`pvget`, `pvput`, `pvmonitor`, `pvinfo`, `softIocPVX`).

```yaml
- uses: jacomago/epics-github-actions/setup-pvxs@v1
  with:
    image: 'ghcr.io/epics-containers/pvxs:1.3.1r1.0'   # Docker image to pull
    network-name: 'epics-net'                             # Docker network for CA/PVA
```

**Outputs:** `epics-host-arch`

**Environment variables set:**
- `EPICS_HOST_ARCH`
- `EPICS_DOCKER_IMAGE`, `PVXS_DOCKER_IMAGE` — image used
- `EPICS_DOCKER_NETWORK`

---

### `start-softioc`

Starts a `softIocPVA` (or `softIocPVX`) instance as a detached Docker container on the shared network, then waits until it is ready.

```yaml
- uses: jacomago/epics-github-actions/start-softioc@v1
  with:
    db-file: path/to/records.db   # path relative to workspace root
    macros: 'P=TEST:,R=REC:'      # passed to softIoc -m
    ioc-name: softioc              # passed to softIoc -n
    use-pvxs: 'false'             # set 'true' to use softIocPVX (requires setup-pvxs)
    wait-pv: 'TEST:STATUS'        # poll this PV until the IOC is up
    wait-timeout: '10'            # fallback sleep (seconds) if wait-pv is not set
    container-name: 'softioc'     # Docker container name (default: softioc)
```

`wait-pv` is recommended — the step exits as soon as `caget` succeeds (up to 30 attempts, 1 s apart) instead of waiting a fixed time.

**Environment variables set:**
- `SOFTIOC_CONTAINER` — the Docker container name, useful for `docker logs` in subsequent steps.

---

## Example workflow

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

## How it works

1. `setup-epics` / `setup-pvxs` pull the Docker image and create a bridge network (`epics-net` by default).
2. Thin wrapper scripts are written to `$RUNNER_TEMP/epics-wrappers/` and added to `$PATH`. Each wrapper runs:
   ```bash
   exec docker run --rm --network epics-net <image> <cmd> "$@"
   ```
3. `start-softioc` launches the IOC as a named detached container on the same network, mounting the `.db` file read-only at `/db/ioc.db`.
4. All subsequent `caget`/`pvget` calls (via wrappers) reach the IOC container through the shared Docker network.

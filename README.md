# epics-github-actions

GitHub Actions for workflows that need [EPICS Base](https://epics-controls.org/) or [PVXS](https://mdavidsaver.github.io/pvxs/) installed. Packages are provided via [conda-forge](https://conda-forge.org/) using [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html).

## Actions

### `setup-epics`

Installs `epics-base` into a conda environment.

```yaml
- uses: jacomago/epics-github-actions/setup-epics@v1
  with:
    epics-version: ''      # pin a version, e.g. "7.0.8" (default: latest)
    environment-name: epics
```

**Outputs:** `epics-host-arch`

After this step, `caget`, `caput`, `camonitor`, `softIocPVA`, and friends are available inside `micromamba-shell` steps and via `$GITHUB_ENV`-exported `EPICS_HOST_ARCH`.

---

### `setup-pvxs`

Installs `epics-base` **and** `pvxs` into a conda environment.

```yaml
- uses: jacomago/epics-github-actions/setup-pvxs@v1
  with:
    pvxs-version: ''       # pin pvxs version (default: latest)
    epics-version: ''      # pin epics-base version (default: latest)
    environment-name: epics
```

**Outputs:** `epics-host-arch`

Adds `pvget`, `pvput`, `pvmonitor`, `pvinfo`, and `softIocPVX`.

---

### `start-softioc`

Starts a `softIocPVA` (or `softIocPVX`) instance in the background and waits until it is ready.

```yaml
- uses: jacomago/epics-github-actions/start-softioc@v1
  with:
    db-file: path/to/records.db
    macros: 'P=TEST:,R=REC:'   # passed to softIoc -m
    ioc-name: softioc           # passed to softIoc -n
    use-pvxs: 'false'           # set 'true' to use softIocPVX
    wait-pv: 'TEST:STATUS'      # poll this PV until the IOC is up
    wait-timeout: '10'          # fallback sleep if wait-pv is not set
    environment-name: epics
```

`wait-pv` is recommended — the step exits as soon as `caget` succeeds (up to 30 attempts, 1 s apart) instead of waiting a fixed time.

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
        shell: micromamba-shell {0}
        run: caget MY:HEARTBEAT MY:STATUS
```

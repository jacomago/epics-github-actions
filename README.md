# epics-github-actions

GitHub Actions for workflows that need [EPICS Base](https://epics-controls.org/) or [PVXS](https://mdavidsaver.github.io/pvxs/) installed. EPICS base and pvxs are **compiled from source** and the result is cached via `actions/cache`, so the first run takes ~5-10 minutes but subsequent runs restore from cache in seconds.

## Actions

### `setup-epics`

Downloads and compiles `epics-base` from source, installs it to a configurable prefix, and exports `EPICS_BASE`, `PATH`, and `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH` for all subsequent steps.

Build dependencies (`libreadline-dev`, `perl`) are installed automatically on Linux runners. macOS runners already have them via Xcode CLT.

```yaml
- uses: jacomago/epics-github-actions/setup-epics@v1
  with:
    epics-version: '7.0.8'                         # EPICS base release tag (default: 7.0.8)
    install-prefix: '${{ github.workspace }}/.epics' # installation directory (default)
```

**Outputs:** `epics-host-arch`, `epics-base-path`

After this step, `caget`, `caput`, `camonitor`, `softIocPVA`, and friends are available in all subsequent `shell: bash` steps. The environment variables `EPICS_BASE`, `EPICS_HOST_ARCH`, and `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH` are set.

**Cache key:** `epics-base-<version>-<OS>-<arch>`

---

### `setup-pvxs`

Compiles `epics-base` and `pvxs` from source. Calls `setup-epics` internally, then clones and builds pvxs with cmake.

```yaml
- uses: jacomago/epics-github-actions/setup-pvxs@v1
  with:
    pvxs-version: '1.3.1'                           # pvxs git tag (default: 1.3.1)
    epics-version: '7.0.8'                          # EPICS base release tag (default: 7.0.8)
    install-prefix: '${{ github.workspace }}/.epics' # installation directory (default)
```

**Outputs:** `epics-host-arch`, `epics-base-path`

Adds `pvget`, `pvput`, `pvmonitor`, `pvinfo`, and `softIocPVX`.

**Cache keys:**
- `epics-base-<version>-<OS>-<arch>` (for EPICS base)
- `pvxs-<pvxs-version>-epics-<epics-version>-<OS>-<arch>` (for pvxs)

---

### `start-softioc`

Starts a `softIocPVA` (or `softIocPVX`) instance in the background and waits until it is ready. Requires `setup-epics` or `setup-pvxs` to have run first.

```yaml
- uses: jacomago/epics-github-actions/start-softioc@v1
  with:
    db-file: path/to/records.db
    macros: 'P=TEST:,R=REC:'   # passed to softIoc -m
    ioc-name: softioc           # passed to softIoc -n
    use-pvxs: 'false'           # set 'true' to use softIocPVX
    wait-pv: 'TEST:STATUS'      # poll this PV until the IOC is up
    wait-timeout: '10'          # fallback sleep if wait-pv is not set
```

`wait-pv` is recommended — the step exits as soon as `caget` succeeds (up to 30 attempts, 1 s apart) instead of waiting a fixed time. The IOC log is written to `$RUNNER_TEMP/softioc.log`.

---

## Example workflow

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - uses: jacomago/epics-github-actions/setup-epics@v1
        with:
          epics-version: '7.0.8'

      - uses: jacomago/epics-github-actions/start-softioc@v1
        with:
          db-file: ioc/db/records.db
          macros: P=MY:
          wait-pv: MY:HEARTBEAT

      - name: Read PVs
        shell: bash
        run: caget MY:HEARTBEAT MY:STATUS
```

## Notes

- **Compilation time:** The first run compiles EPICS base (~5-10 min) and/or pvxs (~2-5 min). Subsequent runs restore from `actions/cache` and skip compilation.
- **Linux dependencies:** `libreadline-dev` and `perl` are installed automatically via `apt-get` on Linux runners.
- **macOS:** `readline` and `perl` are pre-installed via Xcode CLT; `cmake` is pre-installed on GitHub macOS runners.
- **Environment:** `EPICS_BASE`, `PATH`, and `LD_LIBRARY_PATH` (Linux) / `DYLD_LIBRARY_PATH` (macOS) are exported to `$GITHUB_ENV`/`$GITHUB_PATH` for all subsequent steps.
- **Idempotent builds:** Compilation is skipped if the target binary already exists (e.g., after cache restore).
- **Shell injection safety:** All action inputs are passed to shell scripts via `env:` variables, never interpolated directly into `run:` scripts.

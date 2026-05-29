# Contributing

## Updating dependencies

### EPICS Base version

The default EPICS Base version for the `compile` method is set in two places in `setup-epics/action.yml`:

1. The `VERSION` env var in the "Compile EPICS Base" step
2. The cache key in the "Restore EPICS Base cache" step

The same default also appears in the `setup-pvxs/action.yml` cache key (so cache keys stay aligned).

**Minimum supported version for compile is 7.0.9.** Older releases fail to build on modern Clang (macOS) and GCC (Linux) due to C++ template issues fixed in 7.0.9.

Steps to update:
1. Replace the version string in `setup-epics/action.yml` (VERSION env + cache key)
2. Replace the EPICS version in the `setup-pvxs/action.yml` cache key
3. Update the example in `README.md` (`epics-version` compile example)
4. Update the input description example in `setup-epics/action.yml`

### PVXS version

The default PVXS version for the `compile` method is set in two places in `setup-pvxs/action.yml`:

1. The `VERSION` env var in the "Compile pvxs" step
2. The cache key in the "Restore pvxs cache" step

The `docker` method default image tag also encodes the version.

Steps to update:
1. Replace the version string in `setup-pvxs/action.yml` (VERSION env + cache key + input description example)
2. Update the default `image:` in `setup-pvxs/action.yml`
3. Update the `pvxs-version` and `image` examples in `README.md`

### Docker images

Both actions use the same image, which bundles epics-base (CA tools + `softIoc`)
and pvxs (`pvxget`, …, `softIocPVX`):
- `ghcr.io/epics-containers/epics-base-developer:<tag>` — see [epics-containers packages](https://github.com/orgs/epics-containers/packages)

Before updating a tag, verify it exists on `ghcr.io/epics-containers`:
```bash
docker pull ghcr.io/epics-containers/epics-base-developer:<new-tag>
```

Steps to update:
1. Update `default:` for the `image` input in `setup-epics/action.yml`
2. Update `default:` for the `image` input in `setup-pvxs/action.yml`
3. Update the `image:` examples in `README.md`

### GitHub Actions versions

The following third-party actions are used across the workflow files and composite action files:

| Action | Used in |
|--------|---------|
| `actions/checkout` | `.github/workflows/*.yml` |
| `actions/cache` | `setup-epics/action.yml`, `setup-pvxs/action.yml` |
| `mamba-org/setup-micromamba` | `setup-epics/action.yml`, `setup-pvxs/action.yml` |
| `docker/login-action` | `.github/workflows/test.yml`, `.github/workflows/release.yml` |

When bumping a version, update **all** files listed above consistently.

## Running tests

The CI is split into three workflows:

- **`test.yml`** — triggers on every pull request; runs the full matrix (conda + compile + docker × ubuntu + macOS). Open a draft PR to trigger this.
- **`push.yml`** — triggers on push to `main`; runs a fast conda smoke test only.
- **`release.yml`** — triggers on tag push (`v*`); runs the full matrix and creates a GitHub Release.

To run tests locally you can use [`act`](https://github.com/nektos/act):
```bash
act pull_request -W .github/workflows/test.yml
```

## Making a release

1. Ensure all tests pass on `main`.
2. Tag the commit:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. The `release.yml` workflow runs the full matrix and creates a GitHub Release automatically on success.

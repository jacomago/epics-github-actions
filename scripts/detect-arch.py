import platform
m = platform.machine()
s = platform.system()
mapping = {
    ('Linux',  'x86_64'):  'linux-x86_64',
    ('Linux',  'aarch64'): 'linux-aarch64',
    ('Darwin', 'x86_64'):  'darwin-x86_64',
    ('Darwin', 'arm64'):   'darwin-aarch64',
}
arch = mapping.get((s, m))
if arch is None:
    raise SystemExit(f"Unsupported platform: {s}-{m}. Add it to scripts/detect-arch.py.")
print(arch)

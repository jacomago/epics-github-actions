import platform
m = platform.machine()
s = platform.system()
mapping = {
    ('Linux',  'x86_64'):  'linux-x86_64',
    ('Linux',  'aarch64'): 'linux-aarch64',
    ('Darwin', 'x86_64'):  'darwin-x86_64',
    ('Darwin', 'arm64'):   'darwin-aarch64',
}
print(mapping.get((s, m), f'{s.lower()}-{m}'))

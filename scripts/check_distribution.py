"""Reject oversized distributions and accidental repository/credential payloads."""

import sys
import tarfile
import zipfile
from pathlib import Path


def check(directory: Path) -> None:
    archives = list(directory.glob('*.tar.gz')) + list(directory.glob('*.whl'))
    if len(archives) != 2:
        raise ValueError('Expected exactly one sdist and one wheel')
    for archive in archives:
        if archive.stat().st_size > 5_000_000:
            raise ValueError(f'{archive.name} exceeds the 5 MB release limit')
        if archive.name.endswith('.tar.gz'):
            with tarfile.open(archive) as source:
                entries = source.getmembers()
                if any(e.issym() or e.islnk() for e in entries):
                    raise ValueError('Unexpected archive links')
                names = ['/'.join(e.name.split('/')[1:]) for e in entries if e.isfile()]
            allowed = ('src/coarse/', 'pyproject.toml', 'README.md', 'LICENSE',
                       'CHANGELOG.md', 'PKG-INFO', '.gitignore')
            if any(not n.startswith(allowed) for n in names):
                raise ValueError('Unexpected source distribution payload')
        else:
            with zipfile.ZipFile(archive) as source:
                names = source.namelist()
        for host in ('claude_code', 'codex', 'gemini_cli'):
            if not any(n.endswith(f'coarse/_skills/{host}/SKILL.md') for n in names):
                raise ValueError(f'Missing bundled {host} skill')
        if any('/.env' in n or '..' in Path(n).parts for n in names):
            raise ValueError('Unsafe archive path')
        print(f'{archive.name}: {archive.stat().st_size} bytes; contents verified')


if __name__ == '__main__':
    check(Path(sys.argv[1] if len(sys.argv) > 1 else 'dist'))

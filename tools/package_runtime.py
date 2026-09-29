"""Build the production addon; optionally install an explicit offline fixture.

The runtime payload never contains tests, source artwork, or executable fixture
commands. Installation replaces the isolated addon's directory entries, so old
hard links and removed debug superloads cannot survive a new install.
"""
from pathlib import Path
import argparse
import hashlib
import re
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
RUNTIME = WORKSPACE / 'demo/checkerboard-v3/session/runtime'
FIXTURE = ROOT / 'tests/fixture/tome-checker-fixture'
RUNTIME_FOLDERS = ('data', 'hooks', 'superload', 'overload')


def runtime_files(source=ROOT):
    files = [source / 'init.lua']
    if (source / 'COPYING').is_file():
        files.append(source / 'COPYING')
    for folder in RUNTIME_FOLDERS:
        files.extend(p for p in (source / folder).rglob('*') if p.is_file())
    if source == ROOT:
        files = [p for p in files if p.relative_to(source).as_posix() != 'data/audit.lua']
    return sorted(files)


def payload(source, files):
    return {p.relative_to(source): p for p in files}


def fixture_payload():
    files = payload(FIXTURE, runtime_files(FIXTURE))
    # Historical scene names remain available, in the fixture namespace only.
    for source in (ROOT / 'tests').glob('*.lua'):
        files[Path('data') / ('monster-' + source.name)] = source
    return files


def install_payload(name, files):
    assert (RUNTIME / 't-engine').is_file(), 'Use the existing isolated test runtime only'
    addons = RUNTIME / 'game/addons'
    addons.mkdir(parents=True, exist_ok=True)
    target = addons / name
    assert target.parent.resolve() == addons.resolve() and not target.is_symlink()
    with tempfile.TemporaryDirectory(prefix='.' + name + '-', dir=addons) as staging:
        pending = Path(staging) / name
        pending.mkdir()
        for relative, source in files.items():
            assert not relative.is_absolute() and '..' not in relative.parts
            dst = pending / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dst)
        # Unlink the old tree without writing through its legacy hard links.
        if target.exists():
            shutil.rmtree(target)
        pending.rename(target)
    return target


def install_runtime():
    return install_payload('tome-checker-revised', payload(ROOT, runtime_files()))


def install_fixture():
    return install_payload('tome-checker-fixture', fixture_payload())


def build_package():
    match = re.search(r'addon_version\s*=\s*\{([^}]+)\}', (ROOT / 'init.lua').read_text())
    version = '.'.join(part.strip() for part in match[1].split(','))
    files = runtime_files()
    out = ROOT / 'dist' / ('tome-checker-revised-' + version + '.teaa')
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        for source in files:
            # PNG is already compressed. SDL_image probes seek backwards in
            # the stream; the supported engine fails on deflated ZIP streams
            # even though fs.readAll + in-memory decoding succeeds. Keep image
            # bytes stored for reliable TEAA loading; Lua/JSON stay deflated.
            method = zipfile.ZIP_STORED if source.suffix.lower() == '.png' else zipfile.ZIP_DEFLATED
            archive.write(source, source.relative_to(ROOT), compress_type=method)
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert all(i.compress_type == zipfile.ZIP_STORED for i in archive.infolist()
                   if i.filename.lower().endswith('.png')), 'PNG streams must support native SDL_image seeking'
        assert not any(n.startswith(('.git', 'art/', 'tests/', 'tools/')) for n in names)
        assert 'data/audit.lua' not in names
        assert 'superload/mod/dialogs/Birther.lua' not in names
        assert 'superload/mod/class/Zone.lua' not in names
        for name in names:
            if not name.endswith('.lua'):
                continue
            source = archive.read(name).decode()
            assert not any(marker in source for marker in (
                '/checker-command.txt', '/board-test-command.txt',
                '/data-checker-revised/audit', 'function _M:checkerStage',
                'function _M:alternateZoneTier1',
            )), 'Fixture code leaked into ' + name
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    (out.parent / 'runtime-SHA256SUMS').write_text(sha + '  ' + out.name + '\n')
    return out, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', action='store_true', help='Install production files only in the isolated runtime')
    parser.add_argument('--fixture', action='store_true', help='Also explicitly install the standalone offline test addon')
    args = parser.parse_args()
    if args.fixture and not args.runtime:
        parser.error('--fixture requires --runtime')
    out, sha = build_package()
    if args.runtime:
        print('Installed', install_runtime())
        if args.fixture:
            print('Installed', install_fixture())
    print(out)
    print(sha)


if __name__ == '__main__':
    main()

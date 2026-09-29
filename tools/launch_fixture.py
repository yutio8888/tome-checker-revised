"""Cold launch the isolated offline fixture with explicit HUD/addon choices.

Every launch archives its previous fixture home and starts fresh settings,
unless --keep-home asks to reuse the existing one (save/reload acceptance
testing only). No normal user home is read or written. --dry-run prints the
plan without writes; --prepare-only installs/configures the fixture without
starting any processes. --load omits -n so the engine loads the existing
savefile for the fixture player name instead of birthing a new one.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from package_runtime import ROOT as ADDON, fixture_payload, install_payload, payload, runtime_files

ROOT = ADDON.parents[2]
OUT = ROOT / 'demo/checkerboard-v3'
SESSION = OUT / 'session'
RUNTIME = SESSION / 'runtime'
SOURCE = ROOT / 'tmp/battle-companion-validation-20260914/runtime'
DEPS = ROOT / 'tmp/worktrees/yron-profile-20260912/tmp/profile/deps/root/usr'
# Environment repair only, never a product path: the older profile under DEPS no
# longer carries every shared library the engine links against on this host.
# When the workspace build dependencies are present, append their lib directory
# so the isolated engine still resolves e.g. libSDL2_ttf without touching DEPS.
BUILD_DEPS = ROOT / '.build-deps/root/usr/lib'


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hud', choices=('Board', 'Minimalist', 'Classic'), help='Default: Board; Minimalist with --without-board')
    parser.add_argument('--without-board', action='store_true', help='Do not install or load Board HUD')
    parser.add_argument('--without-tokens', action='store_true', help='Use native actors/terrain without the production token addon')
    parser.add_argument('--without-fixture', action='store_true', help='Use normal character creation with cheat disabled; no local command bridge')
    parser.add_argument('--hero-token', action='store_true', help='Explicitly use the fixed Cornac Berserker demo image (fixture only)')
    parser.add_argument('--birth', metavar='RACE:SUBRACE:SEX:CLASS',
                        help='Fixture-only character, e.g. Elf:Shalore:Female:Archmage, '
                             'Human:Higher:Male:Warrior/Bulwark or Construct:Runic Golem:Male:None. '
                             'Default: Human:Cornac:Male:Berserker')
    parser.add_argument('--terrain', choices=('vanilla', 'blockout', 'refined'), help='Default: refined with tokens; vanilla without tokens')
    parser.add_argument('--shaders', action='store_true', help='Enable shaders in the isolated test fixture')
    parser.add_argument('--tiles', type=int, choices=(48, 64, 96), default=64)
    parser.add_argument('--resolution', choices=('1920x1080', '1366x768'), default='1920x1080')
    parser.add_argument('--locale', choices=('en_US', 'zh_hans', 'zh_hant'), default='en_US')
    parser.add_argument('--teaa', action='append', default=[], metavar='ADDON=PATH',
                        help='Install an already built .teaa for checker-revised or board-hud instead of a '
                             'directory payload, so discovery loads the archive itself. Repeatable.')
    parser.add_argument('--prepare-only', action='store_true', help='Install/configure only; do not launch processes')
    parser.add_argument('--dry-run', action='store_true', help='Print selected addons, settings and command without writing')
    # Save/reload acceptance testing only: a cold launch normally archives the
    # previous fixture home and writes fresh settings so every run starts from
    # known defaults. That destroys any savefile written by a prior launch
    # before a reload test can read it back. --keep-home reuses the existing
    # session/home untouched (no archive, no settings rewrite) so a savefile
    # written in a previous launch survives into this one. --load drops the
    # native '-n' (new game) flag so the engine's own Savefile:check() path
    # (engine/Module.lua instanciate) loads the existing save for '-u<name>'
    # instead of going to character creation. Both are test-tooling only.
    parser.add_argument('--keep-home', action='store_true', help='Reuse the existing session home instead of archiving it (needed to reload a save written by a previous launch)')
    parser.add_argument('--load', action='store_true', help='Omit -n so the engine loads the existing savefile for the fixture player name instead of birthing a new one')
    args = parser.parse_args(argv)
    args.hud = args.hud or ('Minimalist' if args.without_board else 'Board')
    args.terrain = args.terrain or ('vanilla' if args.without_tokens else 'refined')
    if args.without_board and args.hud == 'Board':
        parser.error('--hud Board requires Board HUD; remove --without-board or choose a native HUD')
    if args.without_tokens and args.terrain != 'vanilla':
        parser.error('--without-tokens supports only --terrain vanilla')
    if args.birth is not None:
        if args.without_fixture:
            parser.error('--birth requires the explicit offline fixture')
        parts = args.birth.split(':')
        if len(parts) != 4 or not all(re.fullmatch(r"[A-Za-z][A-Za-z' ]*(/[A-Za-z][A-Za-z' ]*)?", p) for p in parts) \
                or '/' in ''.join(parts[:3]) or parts[2] not in ('Male', 'Female'):
            parser.error('--birth expects RACE:SUBRACE:Male|Female:CLASS (CLASS may be Class/Subclass)')
    if args.hero_token and (args.without_tokens or args.without_fixture):
        parser.error('--hero-token requires both the token addon and explicit offline fixture')
    packages = {}
    for entry in args.teaa:
        addon, _, path = entry.partition('=')
        if addon not in ('checker-revised', 'board-hud') or not path:
            parser.error('--teaa expects checker-revised=PATH or board-hud=PATH')
        package = Path(path).resolve()
        if not package.is_file() or package.suffix != '.teaa':
            parser.error('--teaa needs an existing .teaa file: ' + path)
        # Discovery only inspects `<module short name>-*` entries, so the archive
        # must keep a tome-<addon>-*.teaa file name inside game/addons.
        if not package.name.startswith('tome-' + addon + '-'):
            parser.error('--teaa file must be named tome-' + addon + '-<version>.teaa')
        packages[addon] = package
    if 'checker-revised' in packages and args.without_tokens:
        parser.error('--teaa checker-revised conflicts with --without-tokens')
    if 'board-hud' in packages and args.without_board:
        parser.error('--teaa board-hud conflicts with --without-board')
    args.teaa = packages
    return args


def launch_plan(args):
    addons = []
    if not args.without_tokens:
        addons.append('checker-revised')
    if not args.without_board:
        addons.append('board-hud')
    if not args.without_fixture:
        addons.append('checker-fixture')
    extra = 'set_addons={' + ','.join(json.dumps(addon) for addon in addons) + '}'
    if not args.without_fixture:
        extra += ';no_birth_popup=true;checker_fixture=true;checker_demo=true'
        if args.hero_token:
            extra += ';checker_hero=true'
        if args.birth:
            # Validated above to letters, spaces, apostrophes and separators, so
            # a JSON string literal is also a valid Lua string literal here.
            extra += ';checker_birth=' + json.dumps(args.birth)
    command = [str(RUNTIME / 't-engine'), '--no-steam', '--no-web', '--flush-stdout',
               '--home', str(SESSION / 'home'), '-Mtome']
    if not args.load:
        command.append('-n')
    command += ['-uForestWaterStudy', '-E' + extra]
    return dict(addons=addons, teaa={k: str(v) for k, v in args.teaa.items()},
                hud=args.hud, terrain=args.terrain, tokens=not args.without_tokens,
                fixture=not args.without_fixture, hero_token=args.hero_token, birth=args.birth,
                shaders=args.shaders, tiles=args.tiles, resolution=args.resolution,locale=args.locale,
                keep_home=args.keep_home, load=args.load,
                home=str(SESSION / 'home'), command=command)


def assert_stopped():
    metadata = SESSION / 'processes.json'
    if not metadata.exists():
        return
    previous = json.loads(metadata.read_text())
    # The display server may be the bundled binary or the system fallback, so
    # compare against the path actually recorded by the launch that started it.
    xvfb_path = previous.get('xvfb_path') or str(DEPS / 'bin/Xvfb-local')
    for kind, expected in (('game', str(RUNTIME / 't-engine')), ('xvfb', xvfb_path)):
        pid = previous.get(kind)
        proc = Path('/proc') / str(pid) / 'cmdline'
        if pid and proc.exists() and expected.encode() in proc.read_bytes():
            raise SystemExit('Fixture is still running. Stop the existing fixture before a cold launch.')


def prepare_runtime(plan):
    assert_stopped()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for name in ('t-engine', 'bootstrap'):
        dst = RUNTIME / name
        if not dst.exists():
            if (SOURCE / name).is_dir():
                shutil.copytree(SOURCE / name, dst, copy_function=os.link)
            else:
                shutil.copy2(SOURCE / name, dst)
    (RUNTIME / 'game/addons').mkdir(parents=True, exist_ok=True)
    for src in (SOURCE / 'game').iterdir():
        if src.name == 'addons':
            continue
        dst = RUNTIME / 'game' / src.name
        if not dst.exists():
            if src.is_dir():
                shutil.copytree(src, dst, copy_function=os.link)
            else:
                os.link(src, dst)
    selected = set(plan['addons'])
    for addon in ('checker-revised', 'board-hud', 'checker-fixture'):
        target = RUNTIME / 'game/addons' / ('tome-' + addon)
        # A previous fixture used a Board .teaa. A directory install plus a
        # stale archive can make discovery select the wrong version, or make
        # a supposedly disabled addon remain available. Preserve those local
        # archives outside addon discovery before installing this selection.
        packages = list(target.parent.glob(target.name + '.teaa'))
        packages += list(target.parent.glob(target.name + '-*.teaa'))
        if packages:
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            archive = SESSION / 'previous-addon-packages' / stamp
            archive.mkdir(parents=True)
            for package in packages:
                package.rename(archive / package.name)
        if addon not in selected:
            assert not target.is_symlink(), 'Unexpected addon symlink in isolated runtime'
            if target.exists():
                shutil.rmtree(target)
            continue
        if addon in plan.get('teaa', {}):
            # Install the already built archive itself, unchanged, and leave no
            # directory install of the same addon behind: discovery must pick the
            # .teaa, so the run observes the packaged addon and not loose files.
            assert not target.is_symlink(), 'Unexpected addon symlink in isolated runtime'
            if target.exists():
                shutil.rmtree(target)
            source = Path(plan['teaa'][addon])
            installed = target.parent / source.name
            shutil.copy2(source, installed)
            digest = hashlib.sha256(installed.read_bytes()).hexdigest()
            assert digest == hashlib.sha256(source.read_bytes()).hexdigest(), 'Installed .teaa differs from the built package'
            plan.setdefault('teaa_installed', {})[addon] = dict(path=str(installed), sha256=digest)
            continue
        if addon == 'checker-fixture':
            files = fixture_payload()
        else:
            source = ROOT / 'game/addons' / ('tome-' + addon)
            files = payload(source, runtime_files(source))
        install_payload('tome-' + addon, files)

    fixture_home = SESSION / 'home'
    assert not fixture_home.is_symlink(), 'Unexpected fixture home symlink'
    if plan['keep_home'] and fixture_home.exists():
        # Save/reload acceptance only: leave the home (savefile, settings,
        # module state) exactly as the previous launch left it, so a savefile
        # written by a prior process, and any in-game Options change the
        # engine wrote back into settings/, both survive into this launch.
        plan['keep_home_reused'] = True
    else:
        if fixture_home.exists():
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            previous = SESSION / 'previous-homes' / stamp
            previous.parent.mkdir(parents=True, exist_ok=True)
            fixture_home.rename(previous)
        settings = fixture_home / '.t-engine/4.0/settings'
        settings.mkdir(parents=True)
        # A fresh home deliberately excludes persisted Minimalist geometry, prior
        # shader experiments and saved HUD overrides. Keep native log fading (3s).
        settings.joinpath('checker.cfg').write_text(f'''cheat = {str(plan['fixture']).lower()}
audio.enable = false
window = {{size="{plan['resolution']} Windowed"}}
firstrun = true
firstrun_gdpr = true
disable_all_connectivity = true
allow_online_events = false
tome.upload_charsheet = false
tome.autoassign_talents_on_birth = true
locale = "{plan['locale']}"
tome.gfx = {{tiles="shockbolt",size="{plan['tiles']}x{plan['tiles']}",tiles_custom_dir="",tiles_custom_moddable=false,tiles_custom_adv=false}}
tome.uiset_mode = "{plan['hud']}"
tome.log_fade = 3
tome.checker_tokens_enabled = {str(plan['tokens']).lower()}
tome.checker_terrain_mode = "{plan['terrain']}"
display_fps = 10
fbo_active = false
shaders_active = {str(plan['shaders']).lower()}
particles_density = 5
aa_text = false
''')
    (SESSION / 'launch-plan.json').write_text(json.dumps(plan, indent=2) + '\n')


def start(plan):
    display = next(':' + str(n) for n in range(160, 190)
                   if not Path('/tmp/.X11-unix/X' + str(n)).exists())
    env = dict(os.environ)
    env.pop('LD_PRELOAD', None)
    # BUILD_DEPS is only a fallback: its SDL2_image links libjxl/libavif that
    # this host may lack, so append it only when the engine does not already
    # resolve every library through DEPS plus the system.
    libs = [DEPS / 'lib/x86_64-linux-gnu']
    probe_env = dict(env, LD_LIBRARY_PATH=str(libs[0]))
    if not shutil.which('ldd') or 'not found' in subprocess.run(
            ['ldd', str(RUNTIME / 't-engine')], env=probe_env,
            capture_output=True, text=True).stdout:
        libs.append(BUILD_DEPS)
    env.update(DISPLAY=display, SDL_FRAMEBUFFER_ACCELERATION='0', LIBGL_ALWAYS_SOFTWARE='1',
               ALSOFT_DRIVERS='null', SDL_VIDEO_WINDOW_POS='0,0',
               LD_LIBRARY_PATH=os.pathsep.join(str(p) for p in libs if p.is_dir()),
               MESA_SHADER_CACHE_DIR=str(SESSION / 'mesa-cache'))
    # The bundled Xvfb-local needs the profile's own shared libraries. On hosts
    # that no longer provide them (libselinux), fall back to the system server.
    # Only the display server changes; the game still runs against DEPS.
    xvfb_env = dict(env)
    argv = [str(DEPS / 'bin/Xvfb-local'), display, '-screen', '0', plan['resolution'] + 'x24',
            '-nolisten', 'tcp', '-ac', '-fp', str(DEPS / 'share/fonts/X11/misc')]
    probe = subprocess.run([argv[0], '-help'], cwd=DEPS, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode not in (0, 1):
        system = shutil.which('Xvfb')
        if not system:
            raise RuntimeError('Neither the bundled nor a system Xvfb is usable')
        argv[0] = system
        xvfb_env.pop('LD_LIBRARY_PATH', None)
        if not (DEPS / 'share/fonts/X11/misc/fonts.dir').exists():
            del argv[-2:]
    with (SESSION / 'xvfb.log').open('w') as log:
        xvfb = subprocess.Popen(argv, cwd=DEPS, env=xvfb_env, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
    try:
        for _ in range(50):
            if xvfb.poll() is not None:
                raise RuntimeError('Fixture Xvfb exited; inspect session/xvfb.log')
            if Path('/tmp/.X11-unix/X' + display[1:]).exists():
                break
            time.sleep(.1)
        else:
            raise RuntimeError('Fixture Xvfb did not become ready')
        with (SESSION / 'game.log').open('w') as log:
            process = subprocess.Popen(plan['command'], cwd=RUNTIME, env=env,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    except Exception:
        xvfb.terminate()
        xvfb.wait(timeout=5)
        raise
    (SESSION / 'processes.json').write_text(json.dumps(dict(game=process.pid, xvfb=xvfb.pid,
        xvfb_path=argv[0], display=display, command=plan['command'],
        addons=plan['addons'], hud=plan['hud']), indent=2) + '\n')
    print('Launched', process.pid, 'display', display, 'HUD', plan['hud'], 'addons', ', '.join(plan['addons']))


def main(argv=None):
    args = arguments(argv)
    plan = launch_plan(args)
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    prepare_runtime(plan)
    if args.prepare_only:
        print('Prepared', SESSION / 'launch-plan.json')
    else:
        start(plan)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Dead-asset deletion check inside the running isolated fixture (one terrain mode).

This is a driver, not a launcher. Cold start a fresh fixture first with
`launch_fixture.py --shaders --tiles 64 --terrain MODE --resolution 1920x1080`,
then run `capture_dead_assets.py MODE`. It checks Trollmire (fixture start) and
Kor'Pul DEFAULT (seed 537201) in that one mode:

* every image our terrain/token code installed on the current level resolves to
  an existing file that the engine can decode (`fs.exists` + `loadImage`);
* the whole reachable set from `audit_dead_assets.py` (+ the fixture hero) exists
  and decodes inside the installed addon, and none of the deleted paths exist;
* every `Loading tile checker-revised+...` line the engine logged names a file
  that is on disk;
* one unedited 1920x1080 64px screenshot per map.

Output goes only to evidence/dead-assets-20260928/<MODE>/. Staged scene with
frozen AI; not a natural-combat or save-load claim.
"""
import json
import re
import shutil
import subprocess
import sys
import time

from capture_korpul import Fixture, HOME, LOG, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/dead-assets-20260928'
DELETED = ROOT / 'docs/dead-assets-20260927/DELETED.txt'
SEED = 537201

CHECK = r"""
local Map=require 'engine.Map';local m=game.level.map
local function real(p) local r=p:match('^checker%-revised%+(.+)$');return r and '/data-checker-revised/gfx/'..r end
local out,bad,used={}, {}, {}
local function chk(p,kind)
 if not p then return end
 local r=real(p)
 if not r then return end
 used[p]=(used[p] or 0)+1
 if used[p]==1 and not (fs.exists(r) and core.display.loadImage(r)) then bad[#bad+1]=kind..':'..p end
end
local function ident(g)
 if not g then return end
 if g.subtype=='grass' then
  if g.change_level or g.change_zone then return 'exit' end
  if g.does_block_move then if g.name=='tree' or g.name=='tall thick tree' then return 'tree' end return end
  if g.road then return 'road' end
  if g.name=='flower' then return 'flower' end
  if g.name=='grass' then return 'grass' end
 elseif g.subtype=='water' and (g.name=='deep water' or g.name=='bog water') then return 'water' end
end
local forest,refined,top,supported,unpainted,foreign=0,0,0,0,0,0
for y=0,m.h-1 do for x=0,m.w-1 do
 local g=m(x,y,Map.TERRAIN)
 if g then
  if ident(g) then supported=supported+1 end
  local s=g._checker_terrain
  if s then
   forest=forest+1
   assert(g.replace_display==s.display and s.display.image==s.image,'replace_display out of sync at '..x..','..y)
   chk(s.image,'forest')
   if s.image:find('+refined/',1,true) then refined=refined+1 else top=top+1 end
  elseif ident(g) then unpainted=unpainted+1 end
  local rd=g.replace_display
  if rd and rd.image and rd.image:find('^checker%-revised%+') and not s then foreign=foreign+1;chk(rd.image,'replace') end
 end
end end
local kp,kfile,kover,kpaint=0,0,0,0
for key,rec in pairs(m._checker_korpul or {}) do
 kp=kp+1
 if rec.file then kfile=kfile+1;chk(rec.file,'korpul') end
 if rec.overlay then kover=kover+1;chk(rec.overlay,'korpul-stair') end
 if rec.painted then kpaint=kpaint+1 end
end
local tokens,ids=0,{}
for _,e in pairs(game.level.entities) do
 local s=e._checker_token
 if s and s.display then tokens=tokens+1;ids[#ids+1]=tostring(s.id);chk(s.display.image,'token') end
end
table.sort(ids)
-- The full reachable set (+ hero) must exist and decode inside the installed
-- addon; the deleted list must be absent from it.
local reach_n,reach_bad,gone_n,gone_bad=0,{},0,{}
local f=assert(fs.open('/dead-assets-expect.txt','r'));local body=f:read(10000000);f:close()
for kind,p in body:gmatch('(%a+)\t([^\n]+)') do
 local r='/data-checker-revised/gfx/'..p
 if kind=='keep' then reach_n=reach_n+1
  if not (fs.exists(r) and core.display.loadImage(r)) then reach_bad[#reach_bad+1]=p end
 else gone_n=gone_n+1
  if fs.exists(r) then gone_bad[#gone_bad+1]=p end
 end
end
local list={};for p,n in pairs(used) do list[#list+1]=p..'='..n end;table.sort(list)
local lines={
 'zone='..game.zone.short_name,'layout='..tostring(game.zone.is_hideout and 'HIDEOUT' or 'DEFAULT'),
 'option_mode='..require('mod.class.CheckerOptions').terrainMode(),'checker_mode='..tostring(game.checker_mode),
 'tile='..tostring(config.settings.tome.gfx.size),'turn='..game.turn,
 'forest_cells='..forest,'forest_refined='..refined,'forest_toplevel='..top,
 'forest_supported='..supported,'forest_supported_unpainted='..unpainted,'foreign_checker_replace='..foreign,
 'korpul_records='..kp,'korpul_files='..kfile,'korpul_overlays='..kover,'korpul_painted='..kpaint,
 'tokens='..tokens,'token_ids='..table.concat(ids,','),
 'reachable_checked='..reach_n,'reachable_bad='..table.concat(reach_bad,','),
 'deleted_checked='..gone_n,'deleted_present='..table.concat(gone_bad,','),
 'bad='..table.concat(bad,','),'used='..table.concat(list,','),
}
local o=assert(fs.open('/dead-assets-result.txt','w'));o:write(table.concat(lines,'\n')..'\n');o:close()
"""


def expect_file():
    audit = json.loads(subprocess.run([sys.executable, str(ROOT / 'tools/audit_dead_assets.py'), '--json'],
                                      capture_output=True, text=True, check=True).stdout)
    assert audit['dead_total'] == 0 and not audit['missing_from_disk'], 'audit not clean'
    keep = sorted({n for names in audit['reachable_by_origin'].values() for n in names} | set(audit['referenced_only']))
    gone = [line.split('\t')[2] for line in DELETED.read_text().splitlines() if line and not line.startswith('#')]
    body = ''.join(f'keep\t{p[len("data/gfx/"):]}\n' for p in keep)
    body += ''.join(f'gone\t{p[len("data/gfx/"):]}\n' for p in gone)
    (HOME / 'dead-assets-expect.txt').write_text(body)
    return len(keep), len(gone)


def wait_ready(timeout=300):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if LOG.exists() and '[CheckerFixture] BIRTH' in LOG.read_text(errors='replace'):
            time.sleep(3)
            return
        time.sleep(1)
    raise RuntimeError('fixture never reached BIRTH')


def main():
    mode = sys.argv[1]
    assert mode in ('vanilla', 'blockout', 'refined')
    wait_ready()
    fixture = Fixture()
    fixture.log_start = 0  # the whole cold-start log belongs to this run
    out = OUT / mode
    (out / 'screenshots').mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('shaders') and plan.get('terrain') == mode \
        and plan.get('resolution') == '1920x1080' and plan.get('tiles') == 64, plan
    installed = SESSION / 'runtime/game/addons/tome-checker-revised'
    for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Game.lua'):
        assert digest(installed / rel) == digest(ROOT / rel), f'installed {rel} differs; relaunch'
    inst_gfx = sorted(p.relative_to(installed).as_posix() for p in (installed / 'data/gfx').rglob('*') if p.is_file())
    repo_gfx = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/gfx').rglob('*') if p.is_file())
    assert inst_gfx == repo_gfx, 'installed data/gfx differs from repository'
    keep, gone = expect_file()
    result = dict(mode=mode, launch=plan, installed_gfx_files=len(inst_gfx), expect_keep=keep,
                  expect_gone=gone, staged=True, frozen_ai=True, edited=False, maps={}, shots=[])

    def check(label):
        (HOME / 'dead-assets-result.txt').unlink(missing_ok=True)
        fixture.lua(CHECK)
        data = dict(line.split('=', 1) for line in (HOME / 'dead-assets-result.txt').read_text().splitlines())
        shutil.copy2(HOME / 'dead-assets-result.txt', out / f'check-{label}.txt')
        return data

    def shot(name):
        fixture.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';"
                    "game:setupDisplayMode(false);game.player:playerFOV();"
                    "game.level.map:centerViewAround(game.player.x,game.player.y);game.level.map.changed=true")
        time.sleep(1.5)
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        cap = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                             capture_output=True, text=True, timeout=25)
        fixture.transcript.append(cap.stdout + cap.stderr)
        fixture.check_log()
        assert cap.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        target = out / 'screenshots' / source.name
        shutil.copy2(source, target)
        result['shots'].append(dict(file=f'{mode}/screenshots/{target.name}', sha256=digest(target),
                                    resolution=[1920, 1080], tile=64))

    def verify(label, data, zone):
        assert data['zone'] == zone, data
        assert data['option_mode'] == mode, data
        assert not data['bad'] and not data['reachable_bad'] and not data['deleted_present'], data
        assert int(data['reachable_checked']) == keep and int(data['deleted_checked']) == gone, data
        assert data['foreign_checker_replace'] == '0', data
        forest, korpul = int(data['forest_cells']), int(data['korpul_files'])
        if zone == 'trollmire':
            assert data['checker_mode'] == mode
            if mode == 'vanilla':
                assert forest == 0
            else:
                assert forest > 0 and data['forest_supported_unpainted'] == '0', data
                if mode == 'blockout':
                    assert data['forest_refined'] == '0', 'blockout must use top-level tiles only'
                else:
                    assert data['forest_toplevel'] == '0', 'refined must use refined/ tiles only'
        else:
            assert forest == 0
            # Kor'Pul supports refined only; blockout falls back to vanilla there.
            expected = 'refined' if mode == 'refined' else 'vanilla'
            assert data['checker_mode'] == expected, data
            assert (korpul > 0) == (mode == 'refined'), data
        assert int(data['tokens']) > 0, 'staged creatures should carry tokens'
        result['maps'][label] = data

    def save():
        (out / 'check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (out / 'validation-transcript.txt').write_text(''.join(fixture.transcript).rstrip() + '\n')

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
                    "game.player:playerFOV();game.level.map.changed=true")
        time.sleep(1)
        verify('trollmire', check('trollmire'), 'trollmire')
        shot(f'dead-assets-{mode}-trollmire-64')
        save()
        fixture.lua("korpul_scene=assert(loadfile('/data-checker-fixture/monster-live_korpul_scene.lua'))();"
                    f"korpul_scene.enter('DEFAULT',{SEED});korpul_scene.dismissFixturePrompts();"
                    "korpul_scene.refresh();korpul_scene.stage();korpul_scene.dismissFixturePrompts();"
                    "korpul_scene.refresh()")
        time.sleep(1)
        # Painted Kor'Pul records are produced by display; refresh once more after a frame.
        fixture.lua("korpul_scene.refresh()")
        time.sleep(1)
        verify('korpul-default', check('korpul-default'), 'ruins-kor-pul')
        shot(f'dead-assets-{mode}-korpul-default-64')
        # After the Kor'Pul screenshot, records painted during that frame are included.
        verify('korpul-default-after-shot', check('korpul-default-after-shot'), 'ruins-kor-pul')
        # Every checker image the engine actually loaded this session must exist on disk.
        log = LOG.read_text(errors='replace')
        loaded = sorted(set(re.findall(r'Loading tile\tchecker-revised\+(\S+\.png)', log)))
        missing = [p for p in loaded if not (ROOT / 'data/gfx' / p).is_file()]
        deleted = {line.split('\t')[2] for line in DELETED.read_text().splitlines() if line and not line.startswith('#')}
        requested_deleted = [p for p in loaded if 'data/gfx/' + p in deleted]
        result['engine_loaded_checker_images'] = loaded
        result['engine_loaded_missing'] = missing
        result['engine_loaded_deleted'] = requested_deleted
        assert not missing and not requested_deleted, (missing, requested_deleted)
        suspicious = sorted(set(l.strip() for l in log.splitlines()
                                if re.search(r'checker-revised\S*\.png|data-checker-revised/gfx', l)
                                and re.search(r'(?i)error|fail|not exist|could not', l)))
        result['checker_error_lines'] = suspicious
        assert not suspicious, suspicious
        fixture.check_log()
        result['complete'] = True
        save()
        print('PASS', mode, 'loaded', len(loaded), 'checker images;', len(result['shots']), 'screenshots')
    finally:
        save()
        shutil.copy2(LOG, out / 'game.log')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Capture Kor'Pul 0.6.0 in the running disposable offline fixture.

This is a driver, not a launcher. It refuses incomplete art/catalogs and writes
only evidence/runtime-v060. --layout DEFAULT or HIDEOUT redoes one layout while
preserving the other layout's capture metadata.
"""

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT.parents[2] / "demo/checkerboard-v3/session"
HOME = SESSION / "home/.t-engine/4.0/tome"
LOG = SESSION / "game.log"
OUT = ROOT / "evidence/runtime-v060"
SHOTS = OUT / "screenshots"
SEEDS = {"DEFAULT": 537201, "HIDEOUT": 537202}
IDS = {"degenerated skeleton warrior": "degenerated-skeleton-warrior",
       "degenerated skeleton archer": "degenerated-skeleton-archer",
       "skeleton mage": "skeleton-mage", "grey mold": "grey-mold"}
FAIL_PATTERN = re.compile(r"\bFAIL\b|Lua Error|\[CheckerRefined\] ERROR")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path):
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def catalogs():
    token_path = ROOT / "data/token-manifest.json"
    tokens = json.loads(token_path.read_text())
    assets = tokens.get("assets")
    if tokens.get("version") != "0.6.0" or not isinstance(assets, list) or len(assets) != 29:
        raise RuntimeError("requires reviewed 0.6.0 catalog with exactly 29 tokens")
    ids = {item["id"] for item in assets}
    if len(ids) != 29 or not set(IDS.values()).issubset(ids):
        raise RuntimeError("29-token catalog lacks one of the four Kor'Pul identities")
    token_hashes = {}
    for item in assets:
        image = ROOT / "data/gfx/tokens" / (item["id"] + ".png")
        if not image.is_file() or digest(image) != item["runtime_sha256"]:
            raise RuntimeError(f"missing or mismatched runtime token: {item['id']}")
        token_hashes[item["id"]] = digest(image)
    terrain_manifest = ROOT / "data/terrain-korpul-manifest.lua"
    terrain_dir = ROOT / "data/gfx/refined/korpul"
    terrain_pngs = sorted(terrain_dir.glob("*.png"))
    if not terrain_manifest.is_file() or len(terrain_pngs) != 196:
        raise RuntimeError("requires reviewed Kor'Pul terrain manifest and 196 runtime PNGs")
    return {
        "tokens": {"path": "data/token-manifest.json", "sha256": digest(token_path),
                   "manifest": tokens, "png_sha256": token_hashes},
        "terrain": {"path": "data/terrain-korpul-manifest.lua",
                    "sha256": digest(terrain_manifest),
                    "png_sha256": {p.name: digest(p) for p in terrain_pngs}},
    }


class Fixture:
    def __init__(self):
        self.log_start = LOG.stat().st_size if LOG.exists() else 0
        self.transcript = []

    def new_log(self, offset=None):
        if not LOG.exists():
            return ""
        offset = self.log_start if offset is None else offset
        size = LOG.stat().st_size
        if size < offset:
            raise RuntimeError("game.log was truncated or rotated during capture")
        with LOG.open("rb") as stream:
            stream.seek(offset)
            return stream.read().decode("utf-8", "replace")

    def check_log(self):
        text = self.new_log()
        match = FAIL_PATTERN.search(text)
        if match:
            raise RuntimeError(f"new game.log contains {match.group(0)!r}; inspect current capture log")

    def lua(self, code):
        result = subprocess.run([sys.executable, str(ROOT / "tools/fixture_debug.py"), code],
                                capture_output=True, text=True, timeout=55)
        self.transcript.append(result.stdout + result.stderr)
        self.check_log()
        if result.returncode or not re.search(r"(?:^|\n)PASS\r?\n", result.stdout):
            raise RuntimeError(f"fixture Lua command failed: {result.stdout[-2000:]} {result.stderr[-1000:]}")
        return result.stdout

    def shot(self, name, layout, tile, mode, state):
        self.lua("korpul_scene.dismissFixturePrompts();korpul_capture_assert()")
        source = HOME / (name + ".png")
        source.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, str(ROOT / "tools/fixture_command.py"),
                                 "shot", name], capture_output=True, text=True, timeout=25)
        self.transcript.append(result.stdout + result.stderr)
        self.check_log()
        if result.returncode or not source.is_file() or png_size(source) != (1920, 1080):
            raise RuntimeError(f"missing or wrong-size engine screenshot: {name}: {result.stdout} {result.stderr}")
        SHOTS.mkdir(parents=True, exist_ok=True)
        destination = SHOTS / source.name
        shutil.copy2(source, destination)
        return {"file": "screenshots/" + destination.name,
                "sha256": digest(destination), "resolution": [1920, 1080], "tile": tile,
                "zone": "ruins-kor-pul", "layout": layout, "level": 1,
                "seed_input": SEEDS[layout], "mode": mode, "source_kind": "arranged",
                "ai_frozen": True, "arranged": True, "edited": False,
                "shaders": True, "hero_native_in_native_mode": mode == "native",
                "state": state}


def fixture_precheck(fixture):
    plan = json.loads((SESSION / "launch-plan.json").read_text())
    if not (plan.get("fixture") and plan.get("tokens") and plan.get("shaders")
            and plan.get("resolution") == "1920x1080"):
        raise RuntimeError("requires running offline fixture with tokens, shaders and 1920x1080")
    fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                "assert(__module_extra_info.checker_demo);"
                "if not game.checker_staged then game:checkerStage() end;assert(game.checker_staged);"
                "assert(core.shader.active(4));"
                "local T=require('mod.class.CheckerTerrain');assert(T.ready(),'KorPul terrain not ready');"
                "local n=0;for _ in pairs(T.assets.files) do n=n+1 end;assert(n==196,'terrain asset count');"
                "local K=require('mod.class.CheckerTokens');assert(#K.catalog==29,'29-token catalog required');"
                "for _,id in ipairs{'degenerated-skeleton-warrior','degenerated-skeleton-archer','skeleton-mage','grey-mold'} do assert(K.by_id[id],id) end")
    return plan


def copy_tsv(source_name, output_name):
    source = HOME / source_name
    if not source.is_file() or source.stat().st_size == 0:
        raise RuntimeError(f"missing fresh fixture TSV: {source_name}")
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / output_name
    shutil.copy2(source, destination)
    if digest(source) != digest(destination):
        raise RuntimeError(f"TSV copy mismatch: {source_name}")
    return {"file": output_name, "sha256": digest(destination)}


def validate_inventory(path, layout):
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or {(r["zone"], r["layout"]) for r in rows} != {("ruins-kor-pul", layout)}:
        raise RuntimeError(f"wrong or empty final inventory: {path}")
    for name, token in IDS.items():
        scope = "direct" if layout == "DEFAULT" or name == "grey mold" else "shared-import"
        matches = [r for r in rows if r["candidate"] == name and r["scope"] == scope]
        if len(matches) != 1:
            raise RuntimeError(f"missing unique {layout} inventory candidate: {name}")
        row = matches[0]
        kind, subtype = ("immovable", "molds") if name == "grey mold" else ("undead", "skeleton")
        if not (row["name"] == name and row["type"] == kind and row["subtype"] == subtype
                and not row["define_as"] and row["image"] and row["status"] == "covered"
                and row["token"] == token and row["reason"] == "exact-identity"):
            raise RuntimeError(f"{layout} final native/token identity mismatch: {name}: {row}")


SNAPSHOT = r"""
do
 local Map=require 'engine.Map';local m=game.level.map
 local actors={}
 for _,a in ipairs(korpul_scene.actors) do
  actors[#actors+1]={ref=a,name=a.name,x=a.x,y=a.y,life=a.life,max_life=a.max_life,rank=a.rank}
 end
 local rules={}
 for y=0,m.h-1 do for x=0,m.w-1 do
  local g=m(x,y,Map.TERRAIN)
  rules[#rules+1]=table.concat({tostring(g and g.define_as),tostring(g and g.type),
   tostring(g and g.subtype),tostring(g and g.does_block_move),tostring(g and g.block_sight),
   tostring(g and g.block_sense),tostring(g and g.block_esp),tostring(g and g.air_level),
   tostring(g and g.dig),tostring(g and g.is_door),tostring(g and g.door_opened),
   tostring(g and g.door_closed),tostring(g and g.can_pass)},':')
 end end
 korpul_capture_baseline={turn=game.turn,player=game.player,px=game.player.x,py=game.player.y,
  life=game.player.life,max_life=game.player.max_life,actors=actors,rules=table.concat(rules,'|')}
 function korpul_capture_assert()
  local b=korpul_capture_baseline;assert(b and game.turn==b.turn and game.player==b.player)
  assert(game.player.x==b.px and game.player.y==b.py and game.player.life==b.life and game.player.max_life==b.max_life,
   'mode/zoom changed hero life or position')
  for _,v in ipairs(b.actors) do local a=v.ref
   assert(a.name==v.name and a.x==v.x and a.y==v.y and a.life==v.life and a.max_life==v.max_life and a.rank==v.rank,
    'mode/zoom changed staged actor rules or state')
  end
  local now={}
  for y=0,m.h-1 do for x=0,m.w-1 do local g=m(x,y,Map.TERRAIN)
   now[#now+1]=table.concat({tostring(g and g.define_as),tostring(g and g.type),
    tostring(g and g.subtype),tostring(g and g.does_block_move),tostring(g and g.block_sight),
    tostring(g and g.block_sense),tostring(g and g.block_esp),tostring(g and g.air_level),
    tostring(g and g.dig),tostring(g and g.is_door),tostring(g and g.door_opened),
    tostring(g and g.door_closed),tostring(g and g.can_pass)},':')
  end end
  assert(table.concat(now,'|')==b.rules,'mode/zoom changed terrain rules')
 end
end
"""


METRICS = r"""
do
 local T=require 'mod.class.CheckerTerrain';local Map=require 'engine.Map';local m=game.level.map
 local kinds={floor=0,wall=0,hardwall=0,['door-closed']=0,['door-open']=0,other=0}
 for y=0,m.h-1 do for x=0,m.w-1 do
  local kind=T.classify(m(x,y,Map.TERRAIN));kinds[kind or 'other']=kinds[kind or 'other']+1
 end end
 local memory,visible=0,0
 for key in pairs(m._checker_korpul or {}) do
  memory=memory+1;local x=key%m.w;local y=math.floor(key/m.w)
  if T.visible(m,x,y) then visible=visible+1 end
 end
 assert(kinds.floor>0 and kinds.wall+kinds.hardwall>0 and memory>0,
  'no classified native KorPul floor/walls or visible-memory records')
 print('KORPUL_METRICS',kinds.floor,kinds.wall,kinds.hardwall,kinds['door-closed'],kinds['door-open'],kinds.other,memory,visible)
end
"""


def view(fixture, tile):
    fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                "korpul_scene.refresh();korpul_capture_assert()")


def mode(fixture, selected):
    if selected == "native":
        fixture.lua("game:checkerSetTokensEnabled(false);game:checkerSetMode('vanilla');"
                    "korpul_scene.refresh();korpul_capture_assert();"
                    "assert(game.checker_mode=='vanilla' and not game:checkerTokensEnabled());"
                    "assert(not game.player._checker_token,'native hero must retain native display');"
                    "for _,a in ipairs(korpul_scene.actors) do assert(not a._checker_token,'native actor retained token') end")
    else:
        checks = ";".join(f"assert(korpul_scene.actors[{i}]._checker_token and "
                          f"korpul_scene.actors[{i}]._checker_token.id=='{token}','{token}')"
                          for i, token in enumerate(IDS.values(), 1))
        fixture.lua("game:checkerSetMode('refined');game:checkerSetTokensEnabled(true);"
                    "korpul_scene.refresh();korpul_capture_assert();"
                    "assert(game.checker_mode=='refined' and game:checkerTokensEnabled());" + checks)


def metrics(fixture):
    offset = LOG.stat().st_size if LOG.exists() else 0
    fixture.lua(METRICS)
    match = re.search(r"KORPUL_METRICS\s+((?:\d+\s+){7}\d+)", fixture.new_log(offset))
    if not match:
        raise RuntimeError("terrain classification metrics absent from fixture output")
    values = [int(v) for v in match.group(1).split()]
    return dict(zip(("floor", "wall", "hardwall", "door_closed", "door_open", "other",
                     "memory_records", "visible_memory_records"), values))


def capture_layout(fixture, layout):
    lower = layout.lower()
    for name in (f"korpul-natural-{lower}.tsv", f"korpul-scene-{lower}.tsv",
                 f"korpul-inventory-final-{lower}.tsv"):
        (HOME / name).unlink(missing_ok=True)
    fixture.lua("korpul_scene=assert(loadfile('/data-checker-fixture/monster-live_korpul_scene.lua'))();"
                f"korpul_scene.enter('{layout}',{SEEDS[layout]});"
                "korpul_scene.dismissFixturePrompts();korpul_scene.refresh();"
                f"assert((game.zone.is_hideout and 'HIDEOUT' or 'DEFAULT')=='{layout}')")
    natural = copy_tsv(f"korpul-natural-{lower}.tsv", f"korpul-natural-{lower}.tsv")
    fixture.lua("local audit=assert(loadfile('/data-checker-fixture/monster-live_korpul_inventory.lua'))();"
                f"audit.run('korpul-inventory-final-{lower}','{layout}')")
    inventory = copy_tsv(f"korpul-inventory-final-{lower}.tsv",
                         f"korpul-inventory-final-{lower}.tsv")
    validate_inventory(OUT / inventory["file"], layout)
    fixture.lua("korpul_scene.stage();assert(#korpul_scene.actors=="
                + ("6" if layout == "HIDEOUT" else "4") + ");"
                + ";".join(f"assert(korpul_scene.actors[{i}].name=='{name}')"
                           for i, name in enumerate(IDS, 1)) + ";"
                "korpul_scene.dismissFixturePrompts();korpul_scene.refresh()")
    scene = copy_tsv(f"korpul-scene-{lower}.tsv", f"korpul-scene-{lower}.tsv")
    fixture.lua(SNAPSHOT)
    shots = []
    actual_metrics = None
    for tile in (64, 96):
        view(fixture, tile)
        mode(fixture, "native")
        shots.append(fixture.shot(f"korpul-{lower}-native-{tile}", layout, tile, "native", "paired"))
        fixture.lua("korpul_capture_assert()")
        mode(fixture, "refined")
        if actual_metrics is None:
            actual_metrics = metrics(fixture)
        shots.append(fixture.shot(f"korpul-{lower}-refined-{tile}", layout, tile, "refined", "paired"))
        fixture.lua("korpul_capture_assert()")
    view(fixture, 48)
    mode(fixture, "refined")
    shots.append(fixture.shot(f"korpul-{lower}-refined-48", layout, 48, "refined", "internal-pressure"))
    fixture.lua("korpul_capture_assert()")
    return {"layout": layout, "seed_input": SEEDS[layout], "level": 1,
            "ai_frozen": True, "arranged": True, "hero_native_in_native_mode": True,
            "inventory": inventory, "natural": natural, "scene": scene,
            "terrain_classification": actual_metrics, "shots": shots,
            "note": "scene actors are arranged; natural TSV is a separate unarranged level sample"}


def write_capture(catalog, plan, selected):
    captures = {}
    for layout in SEEDS:
        if layout in selected:
            continue
        path = OUT / ("capture-" + layout.lower() + ".json")
        if path.is_file():
            data = json.loads(path.read_text())
            if data.get("layout") != layout:
                raise RuntimeError(f"invalid prior per-layout capture: {path}")
            if data.get("catalog_sha256") != catalog["tokens"]["sha256"] or data.get("terrain_sha256") != catalog["terrain"]["sha256"]:
                raise RuntimeError(f"prior {layout} capture uses another catalog; rerun both layouts")
            captures[layout] = data
    captures.update(selected)
    for layout, data in selected.items():
        path = OUT / ("capture-" + layout.lower() + ".json")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    all_shots = [shot for layout in SEEDS if layout in captures for shot in captures[layout]["shots"]]
    combined = {"version": "0.6.0", "runtime": True, "edited": False, "shaders": True,
                "resolution": [1920, 1080], "launch": plan, "catalog": catalog,
                "layouts": captures, "shots": all_shots}
    (OUT / "capture.json").write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n")


def write_report():
    files = [OUT / f"korpul-inventory-final-{layout.lower()}.tsv" for layout in SEEDS]
    available = [str(path) for path in files if path.is_file()]
    if not available:
        raise RuntimeError("no final inventory TSVs")
    result = subprocess.run([sys.executable, str(ROOT / "tools/report_korpul_inventory.py"), *available],
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f"inventory summary failed: {result.stderr}")
    (OUT / "inventory-summary.md").write_text(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", choices=("DEFAULT", "HIDEOUT", "both"), default="both")
    args = parser.parse_args()
    selected_layouts = list(SEEDS) if args.layout == "both" else [args.layout]
    catalog = catalogs()  # Refuse before contacting the fixture if exports are incomplete.
    fixture = Fixture()
    plan = fixture_precheck(fixture)
    selected = {}
    for layout in selected_layouts:
        layout_log_offset = LOG.stat().st_size if LOG.exists() else 0
        transcript_start = len(fixture.transcript)
        selected[layout] = capture_layout(fixture, layout)
        selected[layout]["catalog_sha256"] = catalog["tokens"]["sha256"]
        selected[layout]["terrain_sha256"] = catalog["terrain"]["sha256"]
        fixture.check_log()
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"validation-{layout.lower()}.txt").write_text(
            "".join(fixture.transcript[transcript_start:]) + "\n" + fixture.new_log(layout_log_offset))
    fixture.check_log()
    write_capture(catalog, plan, selected)
    write_report()
    print("Captured", sum(len(data["shots"]) for data in selected.values()),
          "unedited Kor'Pul engine screenshots in", OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Capture four native HIDEOUT thieves in an already running offline fixture.

This driver never starts the game. It writes only evidence/runtime-v061 and
keeps baseline and temporarily enhanced hero-detection evidence distinct.
"""

import csv
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size


OUT = ROOT / "evidence/runtime-v061"
SHOTS = OUT / "screenshots"
SEED = 537203
IDS = ("cutpurse", "rogue", "thief", "bandit")
IMAGES = {name: f"npc/humanoid_human_{name}.png" for name in IDS}
PHASES = (("baseline", (("native", 64), ("refined", 64))),
          ("detected", (("native", 64), ("refined", 64),
                        ("refined", 96), ("refined", 48))))


def preflight(fixture):
    manifest_path = ROOT / "data/token-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assets = manifest.get("assets")
    if manifest.get("version") != "0.6.1" or not isinstance(assets, list) or len(assets) != 33:
        raise RuntimeError("requires completed 0.6.1 catalog with 33 tokens")
    by_id = {item["id"]: item for item in assets}
    if len(by_id) != 33 or not set(IDS).issubset(by_id):
        raise RuntimeError("catalog lacks unique exact thief identities")
    for item in assets:
        image = ROOT / "data/gfx/tokens" / (item["id"] + ".png")
        if not image.is_file() or digest(image) != item["runtime_sha256"]:
            raise RuntimeError(f"runtime token hash mismatch: {item['id']}")
    terrain = ROOT / "data/terrain-korpul-manifest.lua"
    if not terrain.is_file() or len(list((ROOT / "data/gfx/refined/korpul").glob("*.png"))) != 196:
        raise RuntimeError("requires reviewed Kor'Pul terrain assets")
    installed_scene = (SESSION / "runtime/game/addons/tome-checker-fixture/data/"
                       "monster-live_thief_scene.lua")
    if (not installed_scene.is_file()
            or digest(installed_scene) != digest(ROOT / "tests/live_thief_scene.lua")):
        raise RuntimeError("fixture must contain the current live_thief_scene.lua")
    plan = json.loads((SESSION / "launch-plan.json").read_text())
    if not (plan.get("fixture") and plan.get("tokens") and plan.get("shaders")
            and plan.get("resolution") == "1920x1080"):
        raise RuntimeError("requires existing 1920x1080 offline checker fixture with shaders")
    fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                "assert(__module_extra_info.checker_demo and core.shader.active(4));"
                "if not game.checker_staged then game:checkerStage() end;"
                "assert(game.checker_staged);"
                "local K=require('mod.class.CheckerTokens');assert(#K.catalog==33);"
                "for _,id in ipairs{'cutpurse','rogue','thief','bandit'} do assert(K.by_id[id],id) end")
    return {"launch": plan, "manifest_sha256": digest(manifest_path),
            "terrain_manifest_sha256": digest(terrain)}


def copy_from_fixture(name, destination):
    source = HOME / name
    if not source.is_file() or source.stat().st_size == 0:
        raise RuntimeError(f"missing fixture output: {name}")
    target = OUT / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if digest(source) != digest(target):
        raise RuntimeError(f"fixture output changed during copy: {name}")
    return {"file": destination, "sha256": digest(target)}


def read_state(tsv, phase, mode):
    with (OUT / tsv["file"]).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != 4 or [row["name"] for row in rows] != list(IDS):
        raise RuntimeError(f"incomplete thief scene: {tsv['file']}")
    for row in rows:
        name = row["name"]
        if (row["phase"] != phase or row["type"] != "humanoid"
                or row["subtype"] != "human" or row["image"] != IMAGES[name]
                or row["define_as"] != ("THIEF_BANDIT" if name == "bandit" else "")):
            raise RuntimeError(f"native identity changed: {row}")
        expected = name if mode == "refined" else "native"
        if row["token"] != expected:
            raise RuntimeError(f"wrong {mode} token for {name}: {row['token']}")
        if name == "cutpurse" and row["talent_stealth"] != "0":
            raise RuntimeError("cutpurse unexpectedly gained native Stealth")
        if name != "cutpurse" and int(row["talent_stealth"]) < 1:
            raise RuntimeError(f"{name} lacks its native Stealth talent")
        if not 0 <= float(row["see_chance"]) <= 100:
            raise RuntimeError(f"invalid native canSee chance for {name}")
        if phase == "detected" and (row["hero_can_see"] != "true"
                                    or float(row["see_chance"]) != 100):
            raise RuntimeError(f"humanoid ESP did not give certain detection for {name}")
    return {row["name"]: {"actor_gate": row["hero_can_see"] == "true",
                           "map_seens": row["map_seens"] == "true",
                           "map_infovs": row["map_infovs"] == "true",
                           "active_stealth": row["active_stealth"] == "true",
                           "stealth": row["stealth"],
                           "see_chance": row["see_chance"]} for row in rows}


def set_mode(fixture, mode):
    if mode == "native":
        fixture.lua("game:checkerSetTokensEnabled(false);game:checkerSetMode('vanilla');"
                    "thief_scene.refresh();assert(game.checker_mode=='vanilla');"
                    "assert(not game:checkerTokensEnabled() and not game.player._checker_token);"
                    "for _,a in ipairs(thief_scene.actors) do assert(not a._checker_token) end")
    else:
        fixture.lua("game:checkerSetMode('refined');game:checkerSetTokensEnabled(true);"
                    "thief_scene.refresh();assert(game.checker_mode=='refined' and game:checkerTokensEnabled());"
                    "for i,id in ipairs{'cutpurse','rogue','thief','bandit'} do "
                    "assert(thief_scene.actors[i]._checker_token and "
                    "thief_scene.actors[i]._checker_token.id==id,id) end")


def capture_shot(fixture, phase, mode, tile):
    stem = f"thieves-hideout-{phase}-{mode}-{tile}"
    fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                "thief_scene.refresh();"
                f"assert(thief_scene.phase=='{phase}');thief_scene.dump('{phase}')")
    tsv = copy_from_fixture(f"thief-scene-{phase}.tsv", stem + ".tsv")
    rules = copy_from_fixture(f"thief-rules-{phase}.txt", stem + "-rules.txt")
    hero = (OUT / rules["file"]).read_text().splitlines()[0].split("\t")
    if len(hero) != 7:
        raise RuntimeError("incomplete hero rule state")
    if phase == "detected" and float(hero[6]) < 1:
        raise RuntimeError("detected phase lacks temporary humanoid ESP")
    state = read_state(tsv, phase, mode)
    source = HOME / (stem + ".png")
    source.unlink(missing_ok=True)
    result = subprocess.run([sys.executable, str(ROOT / "tools/fixture_command.py"),
                             "shot", stem], capture_output=True, text=True, timeout=25)
    fixture.transcript.append(result.stdout + result.stderr)
    fixture.check_log()
    if result.returncode or not source.is_file() or png_size(source) != (1920, 1080):
        raise RuntimeError(f"missing engine screenshot {stem}: {result.stdout} {result.stderr}")
    SHOTS.mkdir(parents=True, exist_ok=True)
    target = SHOTS / source.name
    shutil.copy2(source, target)
    fixture.lua(f"thief_scene.dump('{phase}')")
    if digest(HOME / f"thief-rules-{phase}.txt") != rules["sha256"]:
        raise RuntimeError(f"{stem} changed rule state during screenshot")
    return {"file": "screenshots/" + target.name, "sha256": digest(target),
            "resolution": [1920, 1080], "tile": tile, "zone": "ruins-kor-pul",
            "layout": "HIDEOUT", "level": 1, "seed_input": SEED,
            "turn": int(hero[0]), "hero_xy": [int(hero[1]), int(hero[2])],
            "phase": phase, "mode": mode, "source_kind": "arranged", "arranged": True,
            "ai_frozen": True, "edited": False, "shaders": True,
            "hero_native_in_native_mode": mode == "native",
            "observer": "temporary fixture hero humanoid ESP" if phase == "detected" else "fixture hero baseline",
            "actor_state_tsv": tsv, "rule_state": rules,
            "visibility_expected": state,
            "visibility_note": "actor_gate is native cached hero:canSee; true does not guarantee a visible pixel"}


def main():
    # Refuse incomplete catalogs before contacting the running fixture.
    fixture = Fixture()
    info = preflight(fixture)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("korpul-natural-hideout.tsv", "thief-scene-baseline.tsv",
                 "thief-scene-detected.tsv", "thief-rules-baseline.txt",
                 "thief-rules-detected.txt"):
        (HOME / name).unlink(missing_ok=True)
    fixture.lua("thief_scene=assert(loadfile('/data-checker-fixture/monster-live_thief_scene.lua'))();"
                f"thief_scene.enter({SEED});thief_scene.stage();"
                "thief_scene.dismissFixturePrompts();thief_scene.refresh();"
                "assert(#thief_scene.actors==4 and thief_scene.phase=='baseline')")
    natural = copy_from_fixture("korpul-natural-hideout.tsv", "thieves-natural-hideout.tsv")
    shots = []
    baseline_actors = None
    for phase, views in PHASES:
        fixture.lua(f"thief_scene.setObservation('{phase}');assert(thief_scene.phase=='{phase}')")
        rule_digest = None
        for mode, tile in views:
            set_mode(fixture, mode)
            shot = capture_shot(fixture, phase, mode, tile)
            actor_rules = {name: (v["active_stealth"], v["stealth"])
                           for name, v in shot["visibility_expected"].items()}
            if baseline_actors is None:
                baseline_actors = actor_rules
            elif actor_rules != baseline_actors:
                raise RuntimeError("observation phase changed thief Stealth state")
            if rule_digest is None:
                rule_digest = shot["rule_state"]["sha256"]
            elif shot["rule_state"]["sha256"] != rule_digest:
                raise RuntimeError(f"{phase} native rules or visibility changed across art modes/zoom")
            shots.append(shot)
    # Return observer to its baseline native stat after every capture. This
    # deliberately does not claim a new canSee roll equals the original one.
    fixture.lua("thief_scene.setObservation('baseline');"
                "assert(not thief_scene.detection_handle and thief_scene.phase=='baseline')")
    fixture.check_log()
    capture = {"version": "0.6.1", "runtime": True, "edited": False,
               "resolution": [1920, 1080], "catalog": info,
               "natural": natural, "shots": shots,
               "note": "four arranged native actors; natural TSV is a separate unarranged sample; detected phase temporarily gives the fixture hero humanoid ESP"}
    (OUT / "capture-thieves.json").write_text(json.dumps(capture, ensure_ascii=False, indent=2) + "\n")
    (OUT / "validation-thieves.txt").write_text("".join(fixture.transcript) + "\n" + fixture.new_log())
    print(f"Captured {len(shots)} unedited HIDEOUT thief screenshots in {OUT}")


if __name__ == "__main__":
    main()

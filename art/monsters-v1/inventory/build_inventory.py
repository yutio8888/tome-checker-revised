#!/usr/bin/env python3
"""Reproduce the bounded, static monster-art inventory (does not execute Lua).

This is a lexical audit of nine small, manually reviewed NPC definition files
and the Trollmire uniques, not a general Lua parser or a runtime spawn tracer.
"""
from pathlib import Path
import csv
import re
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
MASTER = ROOT / "documentation/board-visual-audit-2026-09-26/images.csv"
FAMILIES = ["troll", "canine", "bear", "snake", "plant", "rodent", "vermin", "swarm", "aquatic_critter"]
FIRST = {"forest troll", "wolf", "brown bear", "large brown snake", "giant venus flytrap"}


def write_csv(name, fields, rows):
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def first(pattern, text, default=""):
    match = re.search(pattern, text, re.M)
    return match.group(1) if match else default


def blocks(text):
    starts = list(re.finditer(r"^newEntity\s*\{", text, re.M))
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        yield text[match.start():end], text.count("\n", 0, match.start()) + 1


def normalized_name(text):
    return re.sub(r"[^a-z0-9]", "_", text.lower())


def main():
    images = [r for r in csv.DictReader(MASTER.open()) if r["category"] == "shockbolt/npc"]
    assert len(images) == 835 and len({r["rgba_sha256"] for r in images}) == 832
    write_csv("npc-sources.csv", list(images[0]), images)
    summary = []
    for scope in ["base", "ashes-urhrok", "cults", "orcs"]:
        rows = [r for r in images if r["scope"] == scope]
        summary.append({"scope": scope, "files": len(rows), "unique_rgba": len({r["rgba_sha256"] for r in rows})})
    summary.append({"scope": "ALL", "files": len(images), "unique_rgba": len({r["rgba_sha256"] for r in images})})
    write_csv("source-summary.csv", ["scope", "files", "unique_rgba"], summary)
    base_images = {r["relative_path"].removeprefix("shockbolt/"): r for r in images if r["scope"] == "base"}
    entities = []
    for family in FAMILIES + ["trollmire_uniques"]:
        source = ("game/modules/tome/data/zones/trollmire/npcs.lua" if family == "trollmire_uniques"
                  else f"game/modules/tome/data/general/npcs/{family}.lua")
        text = (ROOT / source).read_text()
        base = {}
        for block, line in blocks(text):
            name = first(r'^\tname\s*=\s*"([^"]+)"', block)
            for key in ("type", "subtype", "rank"):
                # Only the leading un-named base entity is inherited here.
                if not name:
                    base[key] = first(r'\b' + key + r'\s*=\s*"?([\w.]+)', block)
            if not name:
                continue
            actor_type = first(r'\btype\s*=\s*"([^"]+)"', block.split("\tdesc", 1)[0], base.get("type", "unknown"))
            subtype = first(r'\bsubtype\s*=\s*"([^"]+)"', block.split("\tdesc", 1)[0], base.get("subtype", "unknown"))
            # Inline name/display image or an explicit image line; ignore nested resolvers.
            direct_lines = "\n".join(s for s in block.splitlines() if re.match(r'^\t(?:name|display|image)\s*=', s))
            raw_image = first(r'\bimage\s*=\s*"([^"]+)"', direct_lines)
            resolved_image = raw_image or f"npc/{actor_type}_{normalized_name(subtype)}_{normalized_name(name)}.png"
            nice_line = first(r'^\t(resolvers\.nice_tile[^\n]+)', block)
            nice_images = re.findall(r'\bimage\s*=\s*"([^"]+)"', nice_line)
            sprite = nice_images[-1] if len(nice_images) > 1 else resolved_image
            nice_h = first(r'\bdisplay_h\s*=\s*(\d+)', nice_line, "2" if "tall=1" in nice_line else "1")
            nice_y = first(r'\bdisplay_y\s*=\s*(-?\d+)', nice_line, "-1" if "tall=1" in nice_line else "0")
            image_row = base_images.get(sprite, {})
            unique = bool(re.search(r'\bunique\s*=\s*true', block.split("\tdesc", 1)[0]))
            rank = first(r'^\trank\s*=\s*([\d.]+)', block, base.get("rank", "unknown"))
            level_range = first(r'^\tlevel_range\s*=\s*\{([^}]+)\}', block)
            min_level = int(level_range.split(",")[0].strip()) if level_range else 0
            if name in FIRST:
                phase = "P1_five_masters"
            elif name == "Aluin the Fallen":
                phase = "DEFER_lategame_backup_guardian"
            elif name in {"squid", "ink squid"}:
                phase = "DEFER_not_direct_flooded_spawn"
            elif min_level >= 10:
                phase = "P3_later_family_extension"
            elif unique:
                phase = "P2_unique_separate_master"
            elif family == "aquatic_critter":
                phase = "P2_flooded_aquatics"
            elif family in {"rodent", "vermin", "swarm"}:
                phase = "P2_additional_silhouettes"
            else:
                phase = "P2_family_variants"
            if family == "aquatic_critter":
                default_pool, flooded_pool = "not_direct", "squid_rarity_removed" if "squid" in name else "direct"
            elif family in {"rodent", "canine"}:
                default_pool, flooded_pool = "direct", "all_lua_fallback"
            elif family == "trollmire_uniques":
                default_pool = "guardian" if name == "Prox the Mighty" else "treasure" if name.startswith("Bill ") else "backup_guardian" if name.startswith("Aluin ") else "not_default_guardian"
                flooded_pool = "guardian" if name == "Shax the Slimy" else "treasure" if name.startswith("Bill ") else "backup_guardian" if name.startswith("Aluin ") else "not_flooded_guardian"
            else:
                default_pool = flooded_pool = "direct"
            note = ""
            if name == "Shax the Slimy":
                note = "基础image为Prox；nice_tile.add_mos实际图为Shax。"
            elif name == "Aluin the Fallen":
                note = "35级后备守护者；自动图名存在64×64原图，后续单独制作，不属于本轮早期巨魔沼泽样本。"
            elif not raw_image:
                note = "按NPC.lua:33默认命名规则推导；未运行实体实例化。"
            entities.append(dict(phase=phase, family=family, name=name,
                define_as=first(r'\bdefine_as\s*=\s*"([^"]+)"', block),
                type=actor_type, subtype=subtype, unique=str(unique).lower(), rank=rank,
                level_range=level_range, image_in_definition=raw_image,
                default_image=resolved_image, nicer_display_image=sprite,
                nice_tile=str(bool(nice_line)).lower(), display_h=nice_h, display_y=nice_y,
                pixel_width=image_row.get("width", "unknown"), pixel_height=image_row.get("height", "unknown"),
                asset_found=str(bool(image_row)).lower(), default_pool=default_pool, flooded_pool=flooded_pool,
                source=source, source_line=line, notes=note))
    assert len([e for e in entities if e["phase"] == "P1_five_masters"]) == 5
    for e in entities:
        if e["phase"] == "P1_five_masters":
            assert e["pixel_width"] == e["pixel_height"] == "64" and e["nice_tile"] == "false", e
    write_csv("trollmire-entities.csv", list(entities[0]), entities)
    counts = Counter(e["family"] for e in entities)
    print({"npc_files": len(images), "exact_rgba": 832, "bounded_entity_rows": len(entities), "families": dict(counts)})
    print("Missing base source sprites:", [(e["name"], e["nicer_display_image"]) for e in entities if e["asset_found"] == "false"])


if __name__ == "__main__":
    main()

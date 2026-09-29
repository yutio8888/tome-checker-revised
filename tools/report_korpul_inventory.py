#!/usr/bin/env python3
"""Summarize detached Kor'Pul inventory TSVs; never loads or runs the game.

Usage: python3 tools/report_korpul_inventory.py DEFAULT.tsv HIDEOUT.tsv
The Lua audit resolves active-zone prototypes off-map. This report cannot
establish natural encounters, room occurrence, escorts, or screenshot results.
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ZONE = "ruins-kor-pul"
LAYOUTS = ("DEFAULT", "HIDEOUT")
FIELDS = {"zone", "layout", "level", "turn", "scope", "candidate", "name",
          "type", "subtype", "define_as", "image", "token", "status", "reason", "source"}
FIRST_FOUR = {
    "degenerated skeleton warrior": ("undead", "skeleton", "degenerated-skeleton-warrior"),
    "degenerated skeleton archer": ("undead", "skeleton", "degenerated-skeleton-archer"),
    "skeleton mage": ("undead", "skeleton", "skeleton-mage"),
    "grey mold": ("immovable", "molds", "grey-mold"),
}
THIEVES = ("cutpurse", "rogue", "thief", "bandit")
BOSSES = {"DEFAULT": ("SHADE", "The Shade", "undead", "skeleton"),
          "HIDEOUT": ("THE_POSSESSED", "The Possessed", "humanoid", "human")}


def read_tsv(paths):
    rows = defaultdict(list)
    contexts = []
    for path in paths:
        with Path(path).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if not reader.fieldnames or not FIELDS.issubset(reader.fieldnames):
                raise ValueError(f"{path}: missing audit columns: {sorted(FIELDS - set(reader.fieldnames or []))}")
            file_rows = list(reader)
        if not file_rows:
            raise ValueError(f"{path}: empty audit")
        context = {(r["zone"], r["layout"], r["level"], r["turn"]) for r in file_rows}
        if len(context) != 1:
            raise ValueError(f"{path}: mixed zone/layout/level/turn")
        zone, layout, level, turn = next(iter(context))
        if zone != ZONE or layout not in LAYOUTS or not level or not turn:
            raise ValueError(f"{path}: unexpected or incomplete context {context}")
        contexts.append({"file": str(path), "zone": zone, "layout": layout,
                         "level": level, "turn": turn, "rows": len(file_rows)})
        rows[layout].extend(file_rows)
    return rows, contexts


def selected(rows, scope, candidate):
    return [r for r in rows if r["scope"] == scope and r["candidate"] == candidate]


def identity(row, name, kind, subtype, define_as=""):
    return (row["name"] == name and row["type"] == kind
            and row["subtype"] == subtype and row["define_as"] == define_as
            and bool(row["image"]))


def summarize_sample(samples, expected_identity, expected_token=None):
    if not samples:
        return {"result": "NO_TSV_ROW", "observed": []}
    observed = []
    for row in samples:
        valid_identity = identity(row, *expected_identity)
        exact = (valid_identity and row["status"] == "covered"
                 and row["token"] == expected_token and row["reason"] == "exact-identity")
        native = (valid_identity and row["status"] == "fallback"
                  and not row["token"] and bool(row["reason"]))
        if expected_token:
            result = "EXACT" if exact else "NOT_EXACT"
        else:
            result = "EXPECTED_NATIVE_FALLBACK" if native else "NOT_NATIVE_FALLBACK"
        observed.append({"result": result, "status": row["status"], "name": row["name"],
                         "image": row["image"], "token": row["token"],
                         "reason": row["reason"], "level": row["level"],
                         "turn": row["turn"], "source": row["source"]})
    good = "EXACT" if expected_token else "EXPECTED_NATIVE_FALLBACK"
    return {"result": good if all(r["result"] == good for r in observed) else "REVIEW",
            "observed": observed}


def report(rows, contexts):
    result = {"basis": "detached finishEntity candidates in active zone; no map encounter evidence",
              "contexts": contexts, "layouts": {}}
    for layout in LAYOUTS:
        current = rows[layout]
        first = {}
        for name, (kind, subtype, token) in FIRST_FOUR.items():
            scope = "direct" if layout == "DEFAULT" or name == "grey mold" else "shared-import"
            first[name] = summarize_sample(selected(current, scope, name),
                                           (name, kind, subtype, ""), token)
        thieves = {}
        for name in THIEVES:
            scope = "direct" if layout == "HIDEOUT" else "shared-import"
            define_as = "THIEF_BANDIT" if name == "bandit" else ""
            thieves[name] = summarize_sample(selected(current, scope, name),
                                             (name, "humanoid", "human", define_as))
        boss_id, boss_name, kind, subtype = BOSSES[layout]
        boss = summarize_sample(selected(current, "fixed-boss", boss_id),
                                (boss_name, kind, subtype, boss_id))
        room_rows = [r for r in current if r["scope"] == "conditional-room"]
        escort_rows = [r for r in current if r["scope"] == "escort"]
        result["layouts"][layout] = {
            "first_four": first, "thieves_expected_native_fallback": thieves,
            "boss_expected_native_fallback": {boss_name: boss},
            "room_candidates": {"candidate_rows": len(room_rows),
                                "unavailable": sorted({r["candidate"] for r in room_rows
                                                       if r["status"] == "unavailable"}),
                                "actual_room_occurrence": "UNVERIFIED_BY_TSV"},
            "escort_candidates": {"candidate_rows": len(escort_rows),
                                  "actual_escort_spawn": "UNVERIFIED_BY_TSV"},
            "natural_generation": "UNVERIFIED_BY_TSV",
        }
    return result


def markdown(data):
    lines = ["# Kor'Pul detached inventory summary", "",
             "TSV records off-map `finishEntity` candidates. Natural encounters, room occurrence, escorts and screenshots remain unverified by this report.", ""]
    for layout in LAYOUTS:
        item = data["layouts"][layout]
        contexts = [c for c in data["contexts"] if c["layout"] == layout]
        lines += [f"## {layout}", "",
                  "Audit input: " + (", ".join(f"{c['file']} (level {c['level']}, turn {c['turn']})" for c in contexts) or "none"), "",
                  "| Category | Candidate | Result | Observed native image / reason |", "| --- | --- | --- | --- |"]
        groups = (("first four", item["first_four"]),
                  ("thieves; native fallback expected", item["thieves_expected_native_fallback"]),
                  ("boss; native fallback expected", item["boss_expected_native_fallback"]))
        for label, group in groups:
            for name, sample in group.items():
                detail = "; ".join(f"{r['image']} / {r['reason']}" for r in sample["observed"]) or "—"
                lines.append(f"| {label} | {name} | {sample['result']} | {detail.replace('|', '/')} |")
        room = item["room_candidates"]
        lines += ["", f"Room candidates: {room['candidate_rows']} detached rows; actual room occurrence **UNVERIFIED**.",
                  "Unavailable room candidates: " + (", ".join(room["unavailable"]) or "none reported") + ".",
                  f"Escort candidates: {item['escort_candidates']['candidate_rows']} detached rows; actual escort spawn **UNVERIFIED**.",
                  "Natural generation and encounter rate: **UNVERIFIED**.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", nargs="+", help="TSV from tests/live_korpul_inventory.lua")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    args = parser.parse_args()
    try:
        rows, contexts = read_tsv(args.tsv)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    data = report(rows, contexts)
    print(json.dumps(data, ensure_ascii=False, indent=2) if args.json else markdown(data))


if __name__ == "__main__":
    main()

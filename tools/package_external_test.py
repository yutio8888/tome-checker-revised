"""Build a reproducible, offline external-test ZIP from production TEAA files.

Run package_runtime.py first. This tool never builds an addon or touches a game
installation; it only checks existing archives and wraps them for distribution.
"""

from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ADDONS = ROOT.parent
VERSION = "0.6.33"
HUD_VERSION = "0.2.8"
CHECKER_NAME = "tome-checker-revised.teaa"
HUD_NAME = "tome-board-hud.teaa"
INSTALL_NAME = "INSTALL.zh-CN.md"
SAFE_ROOTS = {"data", "hooks", "superload", "overload"}
SAFE_SUFFIXES = {".lua", ".png", ".json"}
FORBIDDEN_PARTS = {".git", "art", "demo", "docs", "evidence", "fixture", "tests", "tools"}
FIXTURE_MARKERS = (
    b"/checker-command.txt",
    b"/board-test-command.txt",
    b"/data-checker-revised/audit",
    b"function _M:checkerStage",
    b"function _M:alternateZoneTier1",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def metadata(lua: bytes, key: str) -> str:
    match = re.search(rb"\b" + key.encode() + rb"\s*=\s*\{([^}]+)\}", lua)
    if not match:
        raise ValueError(f"Missing {key} in addon init.lua")
    parts = [part.strip() for part in match.group(1).split(b",")]
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid {key} in addon init.lua")
    return ".".join(part.decode("ascii") for part in parts)


def validate_addon(path: Path, expected_version: str, expected_short_name: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing regular production archive: {path}")
    data = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)) or "init.lua" not in names:
            raise ValueError(f"Duplicate entries or missing init.lua: {path}")
        for entry in entries:
            name = entry.filename
            parts = name.split("/")
            if (not parts or name.startswith("/") or "\\" in name or
                    any(part in ("", ".", "..") for part in parts) or
                    any(part.lower() in FORBIDDEN_PARTS for part in parts) or
                    entry.is_dir() or
                    (name not in ("init.lua", "COPYING") and parts[0] not in SAFE_ROOTS) or
                    (name not in ("init.lua", "COPYING") and Path(name).suffix.lower() not in SAFE_SUFFIXES) or
                    (entry.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError(f"Non-production archive member: {name}")
            if name in ("data/audit.lua", "superload/mod/dialogs/Birther.lua",
                        "superload/mod/class/Zone.lua"):
                raise ValueError(f"Fixture member in archive: {name}")
            if name.endswith(".lua") and any(marker in archive.read(entry) for marker in FIXTURE_MARKERS):
                raise ValueError(f"Fixture command in archive: {name}")
            if name.lower().endswith(".png") and entry.compress_type != zipfile.ZIP_STORED:
                raise ValueError(f"PNG must use stored ZIP entries for native image loading: {name}")
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt production archive: {path}")
        init = archive.read("init.lua")
        if metadata(init, "addon_version") != expected_version:
            raise ValueError(f"Wrong addon version in {path}")
        if metadata(init, "version") != "1.7.6":
            raise ValueError(f"Wrong ToME version in {path}")
        if not re.search(rb"\bshort_name\s*=\s*['\"]" + expected_short_name.encode() + rb"['\"]", init):
            raise ValueError(f"Wrong addon identity in {path}")
        if not re.search(rb"\bfor_module\s*=\s*['\"]tome['\"]", init):
            raise ValueError(f"Wrong target module in {path}")
    return data


def build(output: Path) -> tuple[Path, str]:
    checker = ROOT / "dist" / f"tome-checker-revised-{VERSION}.teaa"
    payload = {
        CHECKER_NAME: validate_addon(checker, VERSION, "checker-revised"),
    }
    hud = ADDONS / "tome-board-hud" / "dist" / f"tome-board-hud-{HUD_VERSION}.teaa"
    payload[HUD_NAME] = validate_addon(hud, HUD_VERSION, "board-hud")
    guide = ROOT / "docs" / "external-test-v0633" / INSTALL_NAME
    payload[INSTALL_NAME] = guide.read_bytes()
    checksums = "".join(f"{digest(payload[name])}  {name}\n" for name in sorted(payload))
    payload["SHA256SUMS"] = checksums.encode("ascii")

    output.parent.mkdir(parents=True, exist_ok=True)
    pending = output.with_name(output.name + ".pending")
    try:
        with zipfile.ZipFile(pending, "w", zipfile.ZIP_STORED, strict_timestamps=True) as archive:
            for name in sorted(payload):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, payload[name])
        with zipfile.ZipFile(pending) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(payload):
                raise ValueError("External-test ZIP validation failed")
        pending.replace(output)
    finally:
        pending.unlink(missing_ok=True)
    return output, digest(output.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"tome-checker-revised-external-test-{VERSION}-hud-{HUD_VERSION}.zip")
    args = parser.parse_args()
    path, sha = build(args.output)
    print(path)
    print(f"SHA256 {sha}")


if __name__ == "__main__":
    main()

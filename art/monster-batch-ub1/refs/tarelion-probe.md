<!-- Copied verbatim from <workspace>/tmp/rotation/R20-scratch/REPORT.md (R20 isolated-fixture probe, 2026-10-01). Pinned as UB-1 render evidence for Archmage Tarelion. -->

commandcode/deepseek/deepseek-v4.1-flash

# R20 — In-game probe: resolved appearance of Archmage Tarelion (`TARELION`)

Scope: offline isolated fixture only (`demo/checkerboard-v3`), no normal saves, no
online chat, no repo edits/commits. All artifacts written under
`tmp/rotation/R20-scratch/`.

## Question

Planning (`tmp/rotation/R17-scratch/UB-SELECTION.md` §4.1) predicts that the unique
actor **Archmage Tarelion** (`define_as = "TARELION"`,
`game/modules/tome/data/zones/town-angolwen/npcs.lua:121`, using the
`resolvers.nice_tile{tall=true}` shorthand) resolves at runtime to:

- `image = "invis.png"`
- exactly one `add_mos` entry `{ image = "npc/humanoid_shalore_archmage_tarelion.png", display_h = 2, display_y = -1 }`
- no actor shader

## Method

- Build provenance: `git archive HEAD` of `game/addons/tome-checker-revised`
  (HEAD `7f747921d1e4ba933a056e011e2c119e31f6a44f`, version `0.6.31`) extracted to
  `tmp/rotation/R20-scratch/archive/`; packaged with **that copy's**
  `tools/package_runtime.py` into
  `tmp/rotation/R20-scratch/tome-checker-revised-0.6.31.teaa`
  (sha256 `3641b4fe984af12ec4642a7bb1b0841f2c841821940e015e7132b4747f5aba5d`).
  The installed copy in the fixture session matched that sha byte-for-byte.
- Launch (only via `tools/launch_fixture.py`):
  `--teaa checker-revised=<R20 teaa> --shaders --tiles 64 --resolution 1920x1080
  --terrain refined` (HUD Board, addons `checker-revised,board-hud,checker-fixture`,
  default fixture birth `Human:Cornac:Male:Berserker`, `en_US`). Tokens ON
  (`tome.checker_tokens_enabled = true`).
- Spawn: loaded the native list with the zone class
  (`game.zone.npc_class:loadList('/data/zones/town-angolwen/npcs.lua', true)`),
  selected the prototype `name == "Archmage Tarelion" and define_as == "TARELION"`,
  then `game.zone:finishEntity(game.level, 'actor', proto)` (clone + `resolve()`)
  and `game.zone:addEntity(...)` next to the hero. `a.on_added` fired, so
  `resolvers.sustains_at_birth()` ran exactly as for a real actor. Level: Trollmire L1
  (spawn method is zone-independent), 64px tiles.

## Dumped fields (spawned actor, `r20_tarelion.json` / `r20_tarelion2.json`)

| field | value |
| --- | --- |
| name | `Archmage Tarelion` |
| define_as | `TARELION` |
| unique | `Archmage Tarelion` (truthy) |
| type / subtype | `humanoid` / `shalore` |
| image | `invis.png` |
| shader | `false` (nil) |
| shader_args | `false` (nil) |
| add_mos | exactly one entry, key `"1"` |
| add_mos[1].image | `npc/humanoid_shalore_archmage_tarelion.png` |
| add_mos[1].display_h | `2` |
| add_mos[1].display_y | `-1` |
| add_mos[1].display_w / display_x / display_scale | absent (nil) |
| add_mos[1] keys | exactly `image`, `display_h`, `display_y` (no `shader`, no `_isshaderaura`) |
| rank / faction | `4` / `angolwen` |
| CheckerTokens.identify(a) | `false` (nil) |
| CheckerTokens.explain(a) | `nil` → `checker_reason = "unknown-unique"` |
| `Tokens.appearance` export | not exported (local helper); verdict comes from `explain`/`identify` |
| rendered_token / replace_display | `false` / `false` (native presentation kept) |
| native PNG on disk | 64×128 RGBA (matching the packaged/zone file) |
| active sustains | `T_ARCANE_POWER, T_BODY_OF_STONE, T_CRYSTALLINE_FOCUS, T_DISRUPTION_SHIELD, T_ESSENCE_OF_SPEED, T_KEEN_SENSES, T_PREMONITION` |
| shader_auras | none |
| particles | 4 native particle emitters (the purple glow in the screenshot; not a shader) |
| engine log | `Loading tile npc/humanoid_shalore_archmage_tarelion.png` |

The `=BASE=TILE=` substitution in `resolvers.calc.nice_tile` used `e.image`, which
`mod/class/NPC.lua:33` had already back-filled to
`npc/humanoid_shalore_archmage_tarelion.png` from type/subtype/name.

## Verdict: CONFIRMED

On a real spawned actor the prediction holds exactly: `image = "invis.png"`, exactly
one `add_mos` entry `{ image = "npc/humanoid_shalore_archmage_tarelion.png",
display_h = 2, display_y = -1 }`, and **no actor shader** (`shader`/`shader_args`
both nil; entry carries no shader). Consistent with not yet being in the catalog,
CheckerTokens reports `unknown-unique` (`identify = nil`), leaves
`rendered_token = false` and `replace_display = false`, so the actor keeps its native
tall body. The token system is safe to admit this identity as a native-tall unique.
(Minor note: the visible purple is native sustain-particle emitters, not a shader;
`nativeTallImage` also ignores `_isshaderaura` entries, so an aura would not have
broken the one-body contract anyway.)

## Evidence

- Crop (centred on Tarelion, tokens ON, 64px): `tmp/rotation/R20-scratch/r20-tarelion-64-crop.png`
  (tight: `r20-tarelion-64-crop-tight.png`); full shot `r20-tarelion-64.png`.
- Dumps: `r20_tarelion.json`, `r20_tarelion2.json`.
- Scripts: `probe.lua`, `probe2.lua`, `run_probe.py`, `run_lua.py`, `stop_fixture.py`.
- Session excerpt (launch plan / processes / log lines): `r20-session-evidence.txt`.
- Source PNG compared: `game/modules/tome/data/gfx/shockbolt/npc/humanoid_shalore_archmage_tarelion.png`
  (64×128) matches the rendered sprite.

## Process cleanup

Stopped exactly the PIDs recorded in
`demo/checkerboard-v3/session/processes.json` (`game` 1893788, `xvfb` 1893785,
display `:160`) via `stop_fixture.py`, verifying `/proc/<pid>/cmdline` before each
signal (never `pgrep -f`). Final check: both `/proc/<pid>` entries gone and the
`/tmp/.X11-unix/X160` socket removed. No other processes touch was made.

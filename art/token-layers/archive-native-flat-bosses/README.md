# Archived standees: native 1-cell bosses

These six R36 upright standee masters are archived, not shipped.

The 2026-10-02 redesign makes standee eligibility **native tall only**: an id
gets a standee iff its catalogue image is a 64x128 shockbolt sprite (the native
`nice_tile tall=1` / `display_h=2` body). These six ids are native **1-cell**
bosses (64x64), so they now draw the flat token plus rank badge; their standee
layers were removed from `data/gfx/tokens-layer/` and from the runtime tables.

The masters are kept here for provenance only. Do not move them back under
`art/token-layers/<id>/standee/`: `tools/build_token_layers.py` would then build
a standee layer for a 1-cell id again.

| id | master sha256 (first 16) |
| --- | --- |
| grushnak | `9caf90001f2fc583` |
| phoenix | `720f9d84968ce388` |
| rungof | `a5d85c59ee3a1b17` |
| shardskin | `0a55b66a060714ac` |
| subject-z | `fb1411170339da0a` |
| vor | `ba0f9ab3019354bd` |

Source batch and prompts: `art/production/handoffs/standee-upright-*`; the
per-id screen review is in `evidence/token-standee-upright-20261002/review/`.

# Archived standees: native-tall but flat by height

These two R36 upright standee masters are archived, not shipped.

They *are* natively tall (their catalogue images are 64x128 shockbolt sprites),
but the redesign derives the standee height from the native alpha bbox:
`clamp(native visible height - 0.25, 1.0, 1.75)` cells. Both measure at or below
1.25 native cells, so the derived cap is exactly 1.0 and they keep the flat
token for now. Their standee layers were removed from
`data/gfx/tokens-layer/` and from the runtime tables.

The masters are kept here for a later pass. Do not move them back under
`art/token-layers/<id>/standee/`: `tools/build_token_layers.py` would then build
a standee layer again.

| id | native visible height (cells) | derived cap | master sha256 (first 16) |
| --- | --- | --- | --- |
| gorbat | 1.0625 | 1.0 | `c726ef66a1bcc3f6` |
| bone-giant | 1.1875 | 1.0 | `9396a65ebdca6383` |

Source batch and prompts: `art/production/handoffs/standee-upright-v1` (gorbat)
and `standee-upright-nine-c` (bone-giant).

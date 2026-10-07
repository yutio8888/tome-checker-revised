# Archived standee: kra-tor

This R36 upright standee master is archived, not shipped.

`kra-tor` is natively tall (its catalogue image is a 64x128 shockbolt sprite),
but the R43 body rule counts the BODY only: the native alpha top (y=38) is the
axe blade above the head (head top y=55-56). The body is ~1 cell tall, so the
derived body-only cap is `clamp(<=1.25 - 0.25, 1.0, 1.75) = 1.0` and kra-tor
keeps its flat token.

The standee layer and its R42 POT aura copy were removed from
`data/gfx/tokens-layer/` (and `.../aura/`) and from the runtime tables
(`CheckerTokens.standee_ids`, `data/token-layer-geometry.lua`). The flat 128px
token `data/gfx/tokens/kra-tor.png` is unchanged.

The master is kept here for provenance. Do not move it back under
`art/token-layers/<id>/standee/`: `tools/build_token_layers.py` would then
build a standee layer again.

| file | sha256 (first 16) |
| --- | --- |
| master-v1.png | `3bca69c571c46106` |
| layer-256.png (removed runtime standee layer) | `c00c79b69cda8cae` |
| aura-256.png (removed R42 POT aura copy) | `35fd7cef0cb812a9` |

Source batch and prompts: `art/production/handoffs/standee-upright-*`; the
per-id screen review is in `evidence/token-standee-upright-20261002/review/`.

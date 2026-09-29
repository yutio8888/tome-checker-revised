# F1 flooded Trollmire — dry-run prompt collection

2026-09-28. Preparation only. **No `--execute` call was made; no ImageGen call happened; no runtime art or `data/gfx` file was touched; nothing was committed.** This file exists so the main agent can review every prompt before authorizing any real generation.

## Packages

| Batch | Handoff root | Assets | Kind |
| --- | --- | --- | --- |
| `f1-flooded-trees-v1` | `art/production/handoffs/f1-flooded-v1/trees/` | `bog-tree-a`, `bog-tree-b`, `hardtree` | terrain-prop |
| `f1-flooded-bog-misc-v1` | `art/production/handoffs/f1-flooded-v1/bog-misc/` | `bog-misc-1`, `bog-misc-2`, `bog-misc-3` | terrain-prop |

Both batches passed `tools/art_tasks.py prepare` (schema/source/reference validation) and both packages report `"assets": 3, "ready": 3, "hold": 0"`. All 6 assets were checked with `python3 tools/run_imagegen.py status <pack>` — every one shows `"calls_used": 0, "calls_left": 2`, confirming no call has ever been made against these packages.

All 6 assets were then run through `python3 tools/run_imagegen.py generate <pack> --saved art/terrain-f1-flooded/masters/<id>-v1.png` **without** `--execute`. Every run returned `"mode": "dry-run"` and the note `这是预演，没有发起任何生成，也没有消耗额度。加 --execute 才真的调用。` (this is a rehearsal; nothing was generated and no quota was spent; only `--execute` really calls). No `art/terrain-f1-flooded/masters/` directory was created by these dry-runs — confirmed by directory listing (only the pre-existing `review/` subfolder exists).

No floor asset appears here: the existing `bog*`/`deep*` runtime tiles are being proposed for reuse, not regeneration (see `BRIEF.md` §2 for the evidence).

## Call budget

6 assets x `max_attempts=2` = **12 calls maximum** if every asset needs one repair. Realistic ceiling if everything succeeds on the first try: **6 calls**.

---

## Package 1: `f1-flooded-trees-v1`

### `bog-tree-a` — BOGTREE (willow family, bare-foliage sub-variant)

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: BOGTREE (willow family, bare-foliage sub-variant). Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: One complete small-to-medium willow tree standing directly in shallow bog water, bare winter-look foliage (thin drooping bare branches, no leaf mass), with the visible trunk continuing down into a few inches of surrounding water and faint ripples or mist at the waterline.
Palette/material: Match the accepted willow style anchor's cool grey-green bark and muted bare-branch tone; add a subtly darker wet-bark shade right at the waterline so it reads as standing in water rather than on dry ground.
Distinct from these related pieces: Distinct from the ordinary broadleaf/pine/cypress tree props: willow is exclusive to this flooded identity, per CONTRACT.md willow no longer belongs to the ordinary TREE family. Distinct from bog-tree-b: this is the sparser bare-branch variant, bog-tree-b is the fuller mossy variant. Must not be confused with hardtree, which is a separate, denser, non-willow silhouette on dry ground.
Footprint, height and composition: Full tree including trunk and a visible waterline/root base; the opaque bounding box's bottom edge must reach the lower 25% of the canvas (grounded, matching the accepted tree props) so the trunk visibly meets the water instead of floating. The canopy may lean but must stay inside a transparent margin on all four sides.
Gameplay contract: Blocks movement and line of sight like an ordinary tree, but only actors whose own pass_tree ability is at least 1 can pass through; can be dug down into bog water. Does NOT block perception or ESP -- do not paint it as dense or heavy as hardtree, that visual weight belongs to a different identity. No hazard: standing in this tile is not the deep-water drowning hazard used elsewhere in Trollmire.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Accepted willow-family camera, matte finish and cutout convention for the tree-willow prop master; match this construction style, not the exact silhouette.
Image 2: identity — Native willow-in-water base part; BOGTREE is the only tree identity with a water base, unlike ordinary TREE.
Image 3: identity — Native bare-foliage willow part used by this specific sub-variant (grids.lua:61).
```

### `bog-tree-b` — BOGTREE (willow family, mossy spring-foliage sub-variant)

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: BOGTREE (willow family, mossy spring-foliage sub-variant). Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: One complete small-to-medium moss-draped willow tree standing directly in shallow bog water, fuller spring foliage with soft drooping leaf clusters and visible moss patches on the trunk, with the trunk continuing down into a few inches of surrounding water and faint ripples or mist at the waterline.
Palette/material: Match the accepted willow style anchor's cool grey-green bark; add visible olive-green moss patches on the trunk and slightly richer green foliage than bog-tree-a's bare variant, plus the same subtly darker wet-bark waterline treatment.
Distinct from these related pieces: Distinct from the ordinary broadleaf/pine/cypress tree props for the same reason as bog-tree-a. Distinct from bog-tree-a: this is the fuller, mossier, leafier variant; bog-tree-a is the sparser bare-branch variant. Must not be confused with hardtree.
Footprint, height and composition: Full tree including trunk and visible waterline/root base; opaque bounding box bottom must reach the lower 25% of the canvas (grounded). Canopy may be fuller and slightly wider than bog-tree-a's but must stay inside a transparent margin on all four sides.
Gameplay contract: Identical gameplay contract to bog-tree-a: blocks movement and sight with a pass_tree>=1 exemption, can be dug to bog water, does not block perception or ESP, no hazard. Only the visual style (moss, fuller spring foliage) differs from bog-tree-a.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Accepted willow-family camera, matte finish and cutout convention; match construction style, not exact silhouette.
Image 2: identity — Native mossy spring-foliage willow part used by this specific sub-variant (grids.lua:66).
Image 3: identity — Native willow-in-water base part shared by all BOGTREE sub-variants.
```

### `hardtree` — HARDTREE

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: HARDTREE. Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: One complete, unmistakably ancient and massively thick tree on dry forest ground: a single gnarled, oversized trunk noticeably thicker and more twisted than a normal oak, topped with a dense, heavy dark canopy with no visible gaps of light through the foliage mass.
Palette/material: Darker, more saturated bark than the accepted oak style anchor (deep umber-grey rather than light bark) and a denser near-black-green canopy shadow tone, while staying within the same tabletop material family as the accepted oak/pine/cypress props.
Distinct from these related pieces: Must read as visibly denser and heavier than the ordinary broadleaf, pine and cypress tree props at 48px in grayscale (differ in both silhouette bulk and value). Do not use a willow shape (reserved for bog-tree) and do not add any water element -- HARDTREE stands on dry grass, never on water.
Footprint, height and composition: Full tree including trunk base; opaque bounding box bottom must reach the lower 25% of the canvas (grounded), planted on implied dry ground. Canopy may be wider or denser than the oak style anchor but must stay inside a transparent margin on all four sides.
Gameplay contract: Blocks movement with no exemption for any can_pass value, and blocks line of sight, perception and ESP alike. Cannot be dug. No hazard or damage. Do not paint any exit, door or hazard marking.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Accepted oak-family camera, matte finish and cutout convention; hardtree must read as visibly denser/heavier than this, not a recolor.
Image 2: identity — Native art for TREE and HARDTREE is literally identical (both use the same treesdef, forest.lua:44-59/76/94); this file documents there is no distinct native HARDTREE asset to copy -- CONTRACT.md Section 1.1's finding that has to be resolved by inventing a new, denser silhouette.
```

---

## Package 2: `f1-flooded-bog-misc-v1`

### `bog-misc-1` — BOGWATER_MISC1 (paired with MISC2, reed-cluster group)

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: BOGWATER_MISC1 (paired with MISC2, reed-cluster group). Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: A small cluster of two to three thin pale sedge-green reed or grass tufts emerging just above the waterline, sparse and delicate, no thick stems.
Palette/material: Muted pale sedge-green and straw tones, restrained tabletop-material palette, no bright saturated color.
Distinct from these related pieces: Purely decorative -- must read as harmless floating or emergent vegetation, never as a wall, fence, raised obstacle or speed-boosting pad. Distinct in shape from the moss-clump (bog-misc-2) and driftwood (bog-misc-3) variants so the three read as different decorations, not recolors of one shape.
Footprint, height and composition: Low, flat silhouette hugging the waterline; the whole motif must stay inside a transparent margin on all four sides and must not read as tall enough to block sight. It sits at the water surface, so it is not required to fill the canvas's lower 25% the way an upright tree trunk is.
Gameplay contract: Zero rule difference from plain bog water: does not block movement, sight, sense or ESP; no hazard. Do not paint anything implying blocking, bonus movement or hazard -- no glow, no bubbles, no spikes, no poison tint.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Composition reference only for a low, flat, transparent overlay construct on a floor tile; do not copy its exit iconography or identity.
Image 2: identity — Native reed-tuft decoration this master stands in for.
Image 3: identity — Second native reed-tuft decoration covered by this same master (CONTRACT 9.4 grouping).
```

### `bog-misc-2` — BOGWATER_MISC3 (paired with MISC4, moss-clump group)

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: BOGWATER_MISC3 (paired with MISC4, moss-clump group). Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: A single low, rounded clump of dense olive-green moss or marsh grass sitting at the waterline, bushier and denser than a reed tuft but still clearly low and flat.
Palette/material: Muted olive-green and damp brown-green tones, restrained tabletop-material palette.
Distinct from these related pieces: Purely decorative, must read as harmless emergent vegetation, never a wall, mound obstacle or speed-boosting pad. Distinct in shape from the sparse reed cluster (bog-misc-1) and the driftwood log (bog-misc-3).
Footprint, height and composition: Low, flat, rounded silhouette hugging the waterline, inside a transparent margin on all four sides, not tall enough to imply blocked sight.
Gameplay contract: Zero rule difference from plain bog water: no movement, sight, sense or ESP block; no hazard. Do not paint anything implying blocking, bonus movement or hazard.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Composition reference only for a low, flat, transparent overlay construct; do not copy its identity.
Image 2: identity — Native moss/grass-clump decoration this master stands in for.
Image 3: identity — Second native moss/grass-clump decoration covered by this same master.
```

### `bog-misc-3` — BOGWATER_MISC5 (paired with MISC6, driftwood group)

```
Use case: stylized-concept. Deliver ONE transparent PNG terrain construction for a tabletop game board: BOGWATER_MISC5 (paired with MISC6, driftwood group). Request square 1024 x 1024; preserve native alpha and actual dimensions.

Subject: A single short, weathered, partially submerged driftwood branch or broken log fragment lying diagonally across part of the water surface, dark textured bark, no leaves, clearly broken and irregular rather than a straight milled plank.
Palette/material: Dark weathered brown-grey wood tones, matching a restrained tabletop-material palette.
Distinct from these related pieces: Purely decorative, must read as harmless flotsam, never as a wall or raised obstacle. Distinct in shape from the reed cluster (bog-misc-1) and moss clump (bog-misc-2).
Footprint, height and composition: The log must be short relative to the tile and clearly broken/irregular in outline, angled diagonally rather than spanning the full tile edge-to-edge; do not draw a continuous straight plank that reaches two opposite tile edges, which would visually invent a bridge or crossing that this grid does not provide. Stay inside a transparent margin on all four sides.
Gameplay contract: Zero rule difference from plain bog water: does not block movement, sight, sense or ESP, and grants no special crossing or speed bonus -- swimming/wading through this tile is exactly as easy or hard as through plain bog water. No hazard.

Match accepted tabletop material, camera and soft upper-left illumination. Show a complete physical construction, including its structural supports where specified; not a detached crown or floating fragment. Return an RGBA PNG whose alpha channel is genuinely transparent outside the construction; do not paint a white, grey or checkerboard backdrop for someone to key out later, and do not return a flat opaque RGB image. No creature disc, square grass tile or baked underlying floor. Shadows must stay within the agreed footprint and preserve the neighbouring cell's actor space. No text, arrows, rarity, faction colors, health or shield rings. Do not add a door, hazard or blocking structure that is absent from the gameplay contract. Exporter supplies grid alignment and any separate rule overlay. One construction only, no contact sheet.

Reference roles:
Image 1: style — Composition reference only for a low, flat, transparent overlay construct; do not copy its identity.
Image 2: identity — Native driftwood/log decoration this master stands in for.
Image 3: identity — Second native driftwood/log decoration covered by this same master.
```

## Points the main agent should scrutinise before `--execute`

1. **`hardtree` bulk vs. willow leaning** — the prompt asks for a denser silhouette than oak/pine/cypress; ImageGen sometimes over-corrects toward a cartoonish "monster tree." If the return looks like a face/creature in the bark, reject and repair with an explicit "no anthropomorphic features" line.
2. **`bog-misc-3` bridge risk** — flagged explicitly in the batch JSON's `gate_reason`. A log spanning edge-to-edge would misrepresent a grid that grants no special crossing. Check the returned image against this specifically.
3. **Willow water base bleed** — both `bog-tree-a/b` prompts ask for "faint ripples or mist at the waterline" baked into the *transparent* prop master. Since the exporter composites the prop over the bog-water floor+bank tile (not grass), any opaque water disc painted into the prop master would double up with the exporter's own water tile and could look wrong at the edges — check that the returned alpha only covers the tree/trunk/immediate ripple accent, not a full water rectangle.
4. **Reused floor decision (`bog-water`/`deep-water`)** — no generation is proposed for this identity; see `BRIEF.md` §2 and `review/bog-vs-deep-vs-poison-96.png`. Confirm the numeric proxy is enough, or ask for an actual B1/B6 in-context 64px look before finalizing.

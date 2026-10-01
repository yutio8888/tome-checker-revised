# Monster batch AF final selection after coordinator rework (2026-10-01)

**Nine accepted tokens; dreaming horror remains native because of its actor shader. Catalog 410.**
The source contracts and same-body summon policies below are unchanged. Blood lich is now a flat 64x64 exact identity mapping; six other tall mappings remain unchanged.

Radiant horror v2 has four separated diagonal arms and a physical sunburst ray crown; masked-body luminance **112.24**. It is structurally distinct from the shipped crouching luminous horror at 48/64/96px and in grayscale. Blood lich v3 is an unrobed flayed scarlet skeletal mage with pale ribs/skull/limbs and a blood orb; luminance **66.40**, passing the unchanged **65** gate. It differs from the red-robed lich, sanguine horror mass and faceless animated blood sac. The descriptive floor baseline remains **45**. No gate threshold/test floor changed and no waiver was applied.

Four additional serial wrapper calls: blood retry infrastructure failure (no image/path), blood v2 recorded but body value 63.83 rejected, radiant v2 recorded and accepted, blood v3 recorded and accepted. **16 total AF calls: 14 recorded masters, two infrastructure provenance failures.** Each pinned task pack retains its original two-call budget; user-authorized additional packets retain their review/retry evidence. Defaults remain gpt-6.1-sol and ephemeral. Blood v2 and radiant v1 join superseded drafts; original prompts, receipts, masters and initial sheets are retained. The former PENDING request is withdrawn and marked SUPERSEDED in review/blood-lich-waiver-request-SUPERSEDED.json.

Current sheets: review/horrors-{color,grayscale}-48-64-96.png, review/liches-blood-{color,grayscale}-48-64-96.png, review/rework-focus-{color,grayscale}-48-64-96.png (luminous horror, lich, sanguine horror and animated blood siblings), and review/floor-readability-48*.png. Rework gates and provenance: evidence/monster-batch-af-rework-20261001. Live validation is a separate task; no game was launched.

Final rework gates: 20 non-live Lua scripts passed (33,948 token-mapping checks), all 438 production tests passed, dead-assets --check and explicit scoped staged diff --check passed. Tested runtime, manifest, mapping tests and all AF sprite bytes match the staged AF source. Gate copy: addons/.af-rework-gate-tmp, HEAD archive + explicit AF paths with staged removals; initial overlay-rename cleanup retained in gate-production-first-copy-failure.txt.

---

## Historical initial iteration (superseded admission/call/gate results)

The following records the initial eight-token selection. Its blood-lich hold and radiant selection are superseded by the final selection above; it is retained as history, not current policy.

# Monster batch AF selection (2026-10-01)

Third off-list dungeon-pool batch from survey final.tsv class a. **Eight tokens
accepted for static production admission; two identities stay native.**
No game launch. Live checking is a separate task. No AF change to version,
CHANGELOG, README or PROGRESS, no release packaging and no terrain work.

## Exact identity and final admission

| Identity | Official Chinese name | Name source line | Final decision |
|---|---|---|---|
| nightmare horror | 梦魇恐魔 | horror.lua:145 | Accepted: flat single body 64x64; body luminance 71.56 |
| radiant horror | 光芒恐魔 | horror.lua:444 | Accepted: flat single body 64x64; body luminance 98.91 |
| dreaming horror | 梦境恐魔 | horror.lua:658 | Native: shadow_simulacrum actor shader and sleep shield particles; no generation |
| maelstrom | 灵能漩涡 | horror.lua:831 | Accepted: single-body tall 64x128, native_tall=true; body luminance 107.31 |
| parasitic horror | 寄生恐魔 | horror.lua:880 | Accepted: single-body tall 64x128, native_tall=true; body luminance 79.54 |
| lich | 巫妖 | lich.lua:76 | Accepted: single-body tall 64x128, native_tall=true; body luminance 78.3 |
| ancient lich | 远古巫妖 | lich.lua:110 | Accepted: single-body tall 64x128, native_tall=true; body luminance 79.76 |
| archlich | 高阶巫妖 | lich.lua:144 | Accepted: single-body tall 64x128, native_tall=true; body luminance 74.79 |
| blood lich | 血巫妖 | lich.lua:181 | Native: v1 body luminance 51.30 < 65; v2 provenance failed, budget exhausted; PENDING unapproved waiver request |
| animated blood | 活化血液 | horror-undead.lua:194 | Accepted: single-body tall 64x128, native_tall=true; body luminance 81.01 |

All ten pool leaves are non-unique and have no define_as. No occupied catalog
name/id conflicts. Exact names, types/subtypes, image hashes/dimensions,
nice_tile/add_mos, default filenames, leaf/base source lines and display hits
are frozen in source-contracts.json. READY there means supported native body,
not final art admission; final-admission.json is authoritative for selection.

Animated blood has a real one-body tall image behind invis.png; it is not an
invisible actor without artwork. Its leaf overrides undead/horror to
undead/blood, while nice_tile explicitly names undead_horror_animated_blood.png.
The default-name undead_blood_animated_blood.png does not exist: nicer_tiles-off
keeps that native fallback, and no invented filename alias is added.
The same-body **Blood-Edge (BLOODEDGE)** artifact summon uses the real PNG at
1x/0 instead of 2x/-1. Its exact summoned dexmage constructor and one unaltered
body are admitted, including localized names; arbitrary altered dimensions or
extra composites remain native. The preliminary source-contract artifact
nickname “Bloodcaller” was wrong and is explicitly corrected in
source-contracts-review.md and blood-edge-contract.json without rewriting the
bytes pinned by generation.

Maelstrom's body_of_ice/spikes shader aura and snowfall particles are separate
from its body. Stone Skin on three liches uses the same engine shader_auras /
_isshaderaura mechanism. Native effects are preserved; no actor.shader bypass.
The 129 leaf/inherited talents and artifact summon talents are separately
resolved and pinned. Dreaming horror's actual actor shader remains unsupported.

Radiant escorts the already mapped luminous horror. Parasitic severed flesh
spawns HORROR_PARASITIC_LEECHES, a different body that stays native. Dream seeds
and lich Call Shadows likewise have their own bodies. Unchanged same-body
copies wear their token. **temporalClone is unchanged and generic; no AF clone
code.** Vault pool lookups reuse exact leaves; greater-crypt random tall lich
and Neverdead archlich orb bosses remain native under captureRandomOrigin.
Survey pool imports span relevant early dungeon layouts; this is not full-game
or fully verified spawn-location coverage.

## References, silhouette and floor review

Opened the native identity sheet, both shipped-family sheets and Prox-v2 style
reference before generation. Every call pins its inspected native image,
approved disc/camera reference and focused shipped sibling contact sheet.
Official Chinese names come only from the specified mod-tome.lua; no locale
settings or other user-facing runtime text changed.

Opened final horror and lich/blood colour **and grayscale 48/64/96 sheets**,
plus both enlarged 48px floor sheets. Horror siblings include luminous, oozing,
abyssal, umbral, bone and sanguine horror, dread/dreadmaster, worm that walks
and headless horror. Nightmare has a radial hooked-tendril maw rather than
abyssal's eye-covered tangle or umbral's humanoid. Radiant has an upright narrow
four-arm silhouette with curled upper hands rather than luminous's broad
crouching stance. Maelstrom is an angular tapering ice vortex with claws;
parasitic is a single thick lamprey tube and concentric suction mouth.

Lich's narrow hood/wand, ancient lich's stooped broad torn mantle/two casting
hands, and archlich's upright spired physical regalia/angular shoulders/blue
bell cape separate the three admitted tiers by structure, not only colour.
Blood lich's native unrobed blood humanoid and rejected candidate appear on
the same sheet, explicitly labelled NATIVE/PENDING, not as an accepted token.
Animated blood is a faceless domed hanging blood sac with short drip lobes,
not the humanoid lich or the shipped sanguine horror. Archlich's headdress is
native physical regalia, not a floating tactical rank mark.

All eight selected masked-body means exceed the unchanged **65** floor.
Descriptive real-floor baseline remains **45**. All eight have visible body
masses and complete disc rims at 48px on ten real refined floor composites.
Yellow frames indicate representative survey pool floors, not live spawn
claims. Exact floor bytes used are pinned in review/floor-source-pins.json;
no terrain file was edited. Fine teeth/fingers and headdress points resolve
better at 64/96px; broad shapes carry identity at 48px.

## Calls, superseded drafts and hold

**12 serial run_imagegen.py calls**, defaults gpt-6.1-sol and ephemeral: nine
initial calls, then three second-call repairs. Eleven recorded masters and one
provenance rejection (blood lich repair returned no path/image). Eight selected
masters: six v1 plus lich v2 and animated blood v2. First lich (54.14), blood
lich (51.30) and animated blood (57.98) passed plate/style but failed the
unchanged masked-body floor; all three v1 masters, original receipts/prompts
and 48/64/96 failure sheets are retained. Lich v2 is 78.30; animated blood v2
is 81.01. Their targeted repair briefs preserve already-passed style gates.
No threshold or test floor changed; no waiver is approved/applied.

Blood lich's two-call budget is exhausted. The PENDING waiver request is in
review/blood-lich-PENDING-waiver-request.json, and the failed v1 stays in
superseded/. No blood-lich runtime PNG or mapping is shipped. A later redesign
needs its own pinned refinement/design brief; this batch does not silently
spend a third call or admit the rejected draft.

Catalog 401 -> **409**. Six native_tall entries and two flat entries.
The production manifest preserves all 401 earlier entries and adds only eight.
Gates and exact isolated-copy baseline are recorded in the AF evidence folder.

## Isolated gates and scope

HEAD archive `96243418` plus only explicit AF files, under addons/.af-gate-tmp:
all **20** non-live Lua scripts passed, including **33,869** token-mapping
checks; **437** production tests passed; dead-assets check passed. The scoped
staged diff check passed. The runtime/source files in the tested copy matched
the staged AF bytes. No game launch, version bump or release packaging.

# Monster batch AG selection — 2026-10-01

Last off-list dungeon-pool batch: seven reviewed special-case identities; seven
accepted tokens. The exact
scope is pinned in `evidence/monster-batch-ag-20261001/survey-selection.json`.
Static source audit and token-art review are separate from live rendering.
No game launch, version bump, packaging or release-document update is part of
this iteration. See `source-contracts-review.md` for the shader and composite
identity decisions and the native fallback limits.

| Token id | Native English identity | Official simplified / traditional Chinese |
|---|---|---|
| multi-hued-drake-hatchling | multi-hued drake hatchling | 七彩龙幼仔 / 七彩龍幼仔 |
| multi-hued-drake | multi-hued drake | 七彩龙 / 七彩龍 |
| greater-multi-hued-wyrm | greater multi-hued wyrm | 强化七彩巨龙 / 強化七彩巨龍 |
| shadow-claw | shadow claw, SHADOW_CLAW | 阴影之爪 / 陰影之爪 |
| shadow-caster | shadow claw, SHADOW_CASTER | 阴影之爪 / 陰影之爪 |
| multi-hued-crystal | multi-hued crystal | 彩虹水晶体 / 彩虹水晶體 |
| shimmering-crystal | shimmering crystal | 闪光水晶体 / 閃光水晶體 |

The Chinese names are source-pinned navigation labels, not new UI translations
or runtime keys. Caster is a token id; its actual native name is also shadow
claw. Different art is justified by different native images, stats, resources
and talents, not by renaming it.

The five multihued/crystal entries accept only their verified native body with
quad_hue and nil shader_args, or a disabled shader. The token body paints
static iridescence. The original actor shader is preserved for native fallback
and is not copied onto either the fresh token Entity or its tactical overlay.
Drakes with nicer_tiles on carry shader=false; off they carry quad_hue.
Crystals retain quad_hue in both native tile modes. Greater wyrm uses the
existing exact one-body tall contract when nicer_tiles is on.

The name index allows duplicate names only when both entries explicitly use
shared_name and bind distinct nonempty define_as. The composite definition is
also used for same-body English and localized temporal clones. Planning output can
list both ids for the single name and distinguishes identity/name counts;
refinement briefs must select one exact shared identity. Unknown uniques,
other definitions, reused art, altered bodies, body-layer shaders, other actor
shaders and any non-nil shader_args keep native art. Shadowy assassin and
dreaming horror remain native and have explicit negative tests.

An inherited abandoned hatchling call directory with no result/receipt is
preserved, with RETRY classification in `handover-call-audit.json`; successful
call-2 has full provenance. Caster's first image failed frozen base lightness
(+8.61 outside ±8), is preserved in `superseded/`, and received a targeted
second-call repair that also failed (-18.88). Both rejected masters remain
in superseded/. Coordinator-authorized structural refinement AG-4/call-1 admits
SHADOW_CASTER with a compact hood, raised hands and violet chest glyph; its
plate drift -4.78 and body mean 67.38 pass the unchanged gates. One of up to
four explicitly authorized additional calls was used, with full provenance.
No style limits, body-value floor or test floors changed; no waiver applies.

Visual acceptance and final generation/gate totals are recorded in REVIEW.md,
final-admission.json and the evidence directory after the complete review.

# Retry packs are appended here (never edited in place).

# Pack 5: uruivellas call-1 (pack 1) returned no image at all (codex ended the turn with image_path "" and image_generation_tool_used false, nothing stored). Same brief re-run once.
retry('uruivellas', 5)

# Pack 6: uruivellas v1 (pack 5 call) failed only the base_drift gate (median -8.45, tolerance +-8): the flames and body shadow darkened the plate around the demon. Same design, figure smaller, flames lifting no shadow onto the plate, disc at reference lightness.
UR_FIT = " Calibration from the previous generation of this exact token: the design, the ash-grey clay demon, the ivory horns and the tight flame aura were right, but the plate around the demon came out DARKER than the style reference (the body and flames cast a dark shadow onto the disc). This time keep the same demon, but draw it a little SMALLER (the whole figure, horns and flames included, inside a circle of about 0.62 of the disc radius, centred, with a wide bare ring of plate on every side) with NO cast shadow, NO contact shadow and NO dark halo or ambient darkening under or around the feet and flames. Render the WHOLE disc, its outer ring band and the plate under and around the figure, at exactly the reference lightness or a hair lighter, evenly all round."
retry('uruivellas', 6, comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS + UR_FIT)

# Pack 7: luminous-horror call-1 (pack 3) returned no image (codex ended the turn with image_path "" and no ImageGen tool use, nothing stored). Same brief re-run once.
retry('luminous-horror', 7)

# Pack 8: grizzly-bear call-1 (pack 4) returned no image (codex ended the turn with image_path "" and no ImageGen tool use, nothing stored). Same brief re-run once.
retry('grizzly-bear', 8)

# Pack 9: weaver-patriarch call-1 (pack 4) returned no image (codex ended the turn with image_path "" and no ImageGen tool use, nothing stored). Same brief re-run once.
retry('weaver-patriarch', 9)

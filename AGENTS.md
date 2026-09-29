# Board visual prototype working rules

## Resume and scope

- Read `PROGRESS.md` first; it separates validated delivery from planned scope and records current versions, packages and unfinished work. Consult `README.md` and the relevant evidence/plan before proceeding. Keep changing inventory counts and hashes in those records rather than this file.
- This addon and `../tome-board-hud` have separate Git repositories. The user requests a commit after each completed, validated iteration; preserve earlier commits without amending or rewriting them. Commit affected repositories separately and preserve unrelated work.
- Creature tokens, board terrain and HUD style are independent settings. Keep runtime token code independent of a particular uiset. Minimalist compatibility means the token package works with the native HUD, not that a complete Minimalist theme must be built.
- Judge the art by coherent tabletop language, tactical legibility and artistic interest. Reduced naturalistic forest atmosphere or a tabletop-map appearance is not itself a defect. Equipment/paper-doll variants and a Blender pipeline are outside the current approved production route.

## Art production and coverage

- Read `art/production/README.md` and the current completion/variant plan before a generation batch. Reuse the prompt templates and pre-generation identity/appearance checks; avoid duplicate assets and unsupported runtime candidates. Include both layouts of early dungeons and their different monsters, bosses, summons and room content in coverage audits.
- Use the imagegen skill and built-in image_gen for creature artwork. Inspect references first, preserve native alpha, and keep complete prompts, generated masters, provenance, selected exports and review evidence under `art/`. Do not substitute procedural drawings for requested creature illustrations.
- Keep faction, rarity, health, shields, text and selection out of creature art. Identity and tactical state remain separate layers. Validate new silhouettes at 48/64/96px; same-family variants need more than a color-only distinction, and dark subjects must remain readable against their bases.
- Use verified identities and supported appearance contracts, never an entire subtype mapped to one drawing. Uncovered creatures, unsupported appearances and unknown unique actors retain native art. Follow the established provenance path for renamed known creatures rather than guessing from their new names.
- A fixed demonstration player token is fixture-only; it is not a completed production player mapping. Do not silently use it for every race/class or describe monster coverage as full-game replacement.
- Terrain art must distinguish movement blocking, line-of-sight blocking and hazards without changing gameplay. Ground decoration must not suggest an obstacle or movement bonus absent from native rules. Include doors, stairs, exits, visible/remembered/unexplored cells and both relevant layouts in terrain validation.
- Switching terrain modes must refresh supported grids in the current level and restore native presentation on fallback. Preserve level, turn, position, passability and visibility rules; unsupported regions remain native.

## Tactical presentation and motion

- Default relations follow the agreed native semantics: friendly green, neutral blue, hostile red; the player retains cyan plus a white inner line. User-configurable faction/rank colors must persist and retain non-color distinctions.
- Health fills counterclockwise from 12 o'clock. Shields use a separate pearl-white outer arc. Normal and elite creatures have no rank mark; preserve the current configurable higher-rank scheme unless the user changes it.
- Body and state layers move together, while the overlay must render at most once per frame even when native body blur creates afterimages. Preserve native movement timing, interruption, game turns and smooth/twitch settings. Fixed facing is the current default; native facing remains selectable.
- Special-movement single-token trails, melee lunges and teleport effects remain separate work packages until implemented and validated. Do not claim native body afterimages are removed by the overlay-only blur fix.
- Visibility-sensitive additions must respect actor visibility/perception as well as tile visibility. `map.seens` is current FOV, not exploration memory; traces or markers must not expose hidden creatures or unseen paths.

## Language, validation and packaging

- Add user-facing settings/dialog text through native `_t` / `:tformat` with matching simplified/traditional locale files and English fallback. Preserve exact keys, placeholders, newlines and color codes; do not translate runtime identifiers or saved configuration keys. Keep locale files in the production payload.
- For HUD/character-panel work, follow the sibling HUD AGENTS.md, including language-selected fonts, compact resource rows, optional minimap folding and Game Options-only preference entries.
- Runtime experiments use only the isolated offline fixture under `<workspace>/demo/checkerboard-v3` (this host: `<workspace>/demo/checkerboard-v3`), via `tools/launch_fixture.py`. Preserve normal user saves and game rules; never send online chat as a test. Keep the local SDL_FRAMEBUFFER_ACCELERATION workaround in the launcher, separate from gameplay code.
- Validate relevant native actors and terrain in-game with shaders enabled, appropriate tile sizes and resolutions. Text changes require simplified/traditional Chinese and English checks. Independent-HUD claims require independent cold starts; saved-setting claims require a new process. Distinguish staged/paused scenes from real continuous combat and object serialization from full-save loading.
- Use `tools/package_runtime.py` for production TEAA and `tools/package_external_test.py` for the external ZIP. PNG entries must remain ZIP_STORED because deflated images failed in the tested engine; Lua/JSON may remain compressed. Verify archive/source bytes and installed TEAA behavior, not only loose development files.
- Never ship `.git`, AGENTS.md, source art, docs, tests, tools, fixture superloads or debug command bridges. The external ZIP contains stable-name TEAAs, installation instructions and checksums; users extract the outer ZIP, not the TEAA files.
- Record results, screenshots, package checksums, limitations and remaining work in `PROGRESS.md` and evidence. Stop only the isolated processes you started. Documentation-only changes need document/diff review and a commit, not a version bump, rebuild or game launch.

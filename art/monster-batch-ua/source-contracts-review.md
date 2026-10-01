# UA source review

The 13 survey class b leaves and both Heart Gloom variants are in
survey-selection.json. General pool uniques have no define_as; Phoenix and the
five zone bosses bind their actual symbols. Actor/base extracts are retained;
all native image byte hashes and dimensions match the source files. All leaves
are unique, rank 3.5 except Ukruk/Shade rank 4 and the three Pride leaders rank 5.
Their physical regalia is separate from CheckerTokenStyle.rankBadge, which maps
3.5 to unique, 4 to boss and 5 to elite_boss independently of image identity.
No tactical state, faction, health or UI marks appear in the art prompts.

## Unsupported and transient appearances

Shade has actor.shader=unique_glow. The UA contract leaves this native even if
shaders are disabled; there is no shader opt-in or generation. No other requested
leaf/base declares actor.shader, moddable_tile, add_displays or animation.
Equipment resolvers/auto_classes do not create a paper doll on those fixed
portraits. All tall bodies are one 64x128 image at 2x/-1. No secondary weapon,
hair or equipment add_mos is admitted. Shorthand tall=1 on Grgglck/Ak'Gishil
expands through the existing native nice_tile resolver; explicit nice_tile on
Kra'Tor/Khulmanar/Queen Ant/Ninandra/Gorbat names the real PNG.

Khulmanar's NPC default-name filename (including Khulmanar) does not exist;
only the explicit General of Urh'Rok nice_tile body does. With nicer_tiles off,
he stays native; no fictitious alias is made. The other default-name body paths
or explicit native image paths exist. Phoenix's PHOENIX_EGG effect explicitly
replaces image with object/egg_dragons_egg_06_64.png and removes MOs, then
restores old_image on deactivation. Only the living bird body is mapped; the
real revival egg, shield particles and firetrail remain native.

## Talents, summons and rename provenance

All 161 leaf/base talent references resolve in talent-contracts.json. The
static appearance-writer scan records Body of Fire and Burning Wake on Phoenix,
Master Summoner on Gorbat, Burning Wake on Vor: addShaderAura bookkeeping,
not actor.shader. Existing _isshaderaura handling keeps these native effects.
Ak'Gishil has Kinetic Aura/shields with particle effects; no body write in the
resolved direct talent callbacks. Temporary invisibility, frozen composites or
other class-acquired display changes remain subject to existing guards.
Dynamic auto_classes do not establish universal coverage of future appearances.

Grgglck on_act calls Invoke Tentacle. Its source clones GRGGLCK_TENTACLE,
an independent actor; it never replaces Grgglck's body. Ak'Gishil on_act calls
Animate Blade: ANIMATED_BLADE or DISTORTED_BLADE are separate actors outside UA.
Khulmanar summons/escorts demon pool actors; Queen Ant summons/escorts ant
pool actors; Ninandra summons weaver young and escorts patriarchs. Rungof
escorts six wargs. Gorbat's rimebark/ritch summons have their own bodies.
No separate summon receives its parent's boss artwork.

Heart Gloom alter callbacks operate after engine Entity construction: Entity:init
has already converted unique=true into the original base name. They alter
name, rarity and one talent only, preserving unique's original string, explicit
canine_rungof.png and all fixed body fields. This gives a stronger constructor
contract than stripping an arbitrary prefix from any unique. English and
translated six-prefix names will be recognized only with Rungof's original
unique marker, no define_as, known life_rating/size/level-range and unchanged
body. Prefixes are _t strings and base getName uses entity-name localization.
A bare renamed unique, forged marker, different canine, changed dimensions or
shader keeps native art. Other uniques remain excluded from generic Heart
Gloom prefixes. This is reuse of the verified original body, not new artwork.

Existing createRandomBoss capture/record provenance is retained: exact flat
and unique tall sources can record a same-body random identity; arbitrary
names or stale origin records cannot. Unique temporal clones remain native
under existing non-unique clone policy. No UA aliases admit a new identity
outside the 13 requested leaves. Both Kor'Pul layouts were audited: SHADE stays
native; THE_POSSESSED is already shipped and unchanged. Survey pool imports
are not proof of live spawn probabilities or full-game replacement.

All review evidence here is static; no game launch, full-save test, live shader
claim, natural continuous combat claim or installable package was produced.

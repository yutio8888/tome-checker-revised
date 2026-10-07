# Standee body-height review (R43/R44/R46, 2026-10-04)

Full native-tall table. `derived` is `clamp(native alpha-bbox height / 64 - 0.25, 1.0, 1.75)`
from `tools/build_standee_heights.py`; `final` is `M.standee_height_override` when present.
Body rule (user decision): head, horns, helmets, hats, hair, raised arms, wings and fins count;
raised weapons, staves, floating orbs, debris, particles, flames, lightning and glow do not.
Sparse or semi-transparent fringes (bristles, specks, mist, shroud, warm glow) are not body.
R46 reproducible measure: the body top is the **solid top**, the FIRST ROW with at least
6 pixels above alpha 128 (`tools/build_standee_heights.py:solid_top`). Energy/cloud beings
whose glow IS their body keep their derived cap (decision 3). The original
three: greater-telugoroth and ultimate-telugoroth, desc "blurred form"; daelach,
desc "cloud of fiery darkness". R48 extends the exemption to fyrk and
ultimate-faeros, desc "fire elementals"; ultimate-teluvorta, desc "time
elemental"; maelstrom, desc "vortex of ice and lightning"; ultimate-gwelgoroth,
desc "air elementals"; and glacial-legion, desc "shifting, ethereal form".
Every value is `clamp((bottom - head_top + 1) / 64 - 0.25, 1.0, 1.75)` for the head/horn top row.

Native-tall ids: **151**; reviewed overrides: **49**;
flat (final 1.0): **53**. The generated table alone has 31 flat ids;
53 includes the reviewed runtime overrides.

| id | derived | final | reason |
| --- | --- | --- | --- |
| `abyssal-horror` | 1.578125 | 1.578125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ak-gishil` | 1.65625 | 1.34375 | floating swords above the head; head/arms are body |
| `ancient-dragon-turtle` | 1.703125 | 1.703125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ancient-lich` | 1 | 1 | flat: native body <= 1.25 cells |
| `animated-blood` | 1 | 1 | flat: native body <= 1.25 cells |
| `arch-zephyr` | 1.46875 | 1.21875 | lightning arcs above the hood; hood top is body |
| `archlich` | 1.5 | 1.5 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `archmage-tarelion` | 1.09375 | 1 | warm glow rows 41-46 excluded; solid top y=49 -> 0.96875 clamped to 1.0 (flat) |
| `argoniel` | 1.25 | 1 | raised sword and staff above the head; body ~1 cell |
| `atamathon` | 1.671875 | 1.671875 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `barrow-wight` | 1 | 1 | flat: native body <= 1.25 cells |
| `bill` | 1.015625 | 1.015625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `blade-horror` | 1.390625 | 1 | blades above the body |
| `blinkwyrm` | 1.3125 | 1.3125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `boiling-horror` | 1.453125 | 1 | steam column is a particle; the frothing ball top is the body (flat) |
| `bone-giant` | 1 | 1 | flat: native body <= 1.25 cells |
| `bone-horror` | 1.140625 | 1.140625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `briagh` | 1.734375 | 1.734375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `brotoq` | 1 | 1 | flat: native body <= 1.25 cells |
| `burb-snow-giant-champion` | 1.65625 | 1.53125 | lightning above the dark horns (horn top y=13) |
| `caldizar` | 1.6875 | 1.25 | staff and motes above the raised hand/head |
| `celia` | 1.6875 | 1.390625 | staff above the head; the head top (y=23) is body |
| `champion-of-urh-rok` | 1.40625 | 1.40625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `chronolith-clone` | 1.015625 | 1.015625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `chronolith-twin` | 1.015625 | 1.015625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `corrupted-daelach` | 1.75 | 1.75 | top is the wings/horns (body); reviewed, no override |
| `corrupted-sand-wyrm` | 1.703125 | 1.703125 | top is the curled tail (body), not a crest; R41 override dropped |
| `cryomancer` | 1.078125 | 1 | staff and orb above the hood; body ~1 cell |
| `daelach` | 1.71875 | 1.71875 | glow is the body (desc: cloud of fiery darkness); derived cap kept (decision 3) |
| `degenerated-ogric-mass` | 1.140625 | 1.140625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `dolleg` | 1.328125 | 1.328125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `dremling` | 1.375 | 1.375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `duathedlen` | 1.40625 | 1.265625 | darkness shroud excluded; solid head top y=31 |
| `elandar` | 1.4375 | 1 | staff and orb above the head; body ~1 cell |
| `emperor-wight` | 1.21875 | 1 | raised sword above the crown; body ~1 cell |
| `entrenched-horror` | 1.546875 | 1.546875 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `eternal-bone-giant` | 1.25 | 1.25 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `fallen-sun-paladin-aeryn` | 1.171875 | 1 | raised long sword above the head |
| `fillarel-aldaren` | 1.125 | 1 | staff and orb held above the head; body ~1 cell |
| `fire-wyrm` | 1.625 | 1.625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `forest-troll-hedge-wizard` | 1 | 1 | flat: native body <= 1.25 cells |
| `forge-giant` | 1.59375 | 1.328125 | head flame is not body (head top y=27) |
| `fyrk` | 1.59375 | 1.59375 | glow is the body (desc: fire elementals); derived cap kept (decision 3) |
| `geomancer` | 1.046875 | 1 | staff and orb held above the hat; body ~1 cell |
| `gigantic-corrosive-tunneler` | 1.4375 | 1.4375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `gigantic-gravity-worm` | 1.703125 | 1.40625 | lightning above the head (head top y=21) |
| `gigantic-sandworm-tunneler` | 1.671875 | 1.40625 | lightning above the head (head top y=21) |
| `glacial-legion` | 1.671875 | 1.671875 | glow is the body (desc: shifting, ethereal form); derived cap kept (decision 3) |
| `golbug` | 1 | 1 | flat: native body <= 1.25 cells |
| `gorbat` | 1 | 1 | flat: native body <= 1.25 cells |
| `greater-gwelgoroth` | 1 | 1 | flat: native body <= 1.25 cells |
| `greater-multi-hued-wyrm` | 1.625 | 1.625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `greater-shivgoroth` | 1 | 1 | flat: native body <= 1.25 cells |
| `greater-telugoroth` | 1.1875 | 1.1875 | glow is the body (desc: blurred form); derived cap kept (decision 3) |
| `greater-teluvorta` | 1.078125 | 1 | floating spell orb above the body |
| `grgglck` | 1.625 | 1.625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `grizzly-bear` | 1 | 1 | flat: native body <= 1.25 cells |
| `half-finished-bone-giant` | 1.265625 | 1.21875 | purple halo rows 31-33 (max alpha 18/62/115, none >128) is not body; skull/head solid top y=34 |
| `harkor-zun` | 1.53125 | 1.53125 | top is the horned head (body); R41 override dropped |
| `harkor-zun-fragment` | 1 | 1 | flat: native body <= 1.25 cells |
| `healer-astelrid` | 1.3125 | 1.3125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `heavy-bone-giant` | 1.75 | 1.75 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `heavy-sentinel` | 1.609375 | 1.546875 | orange glow above the skull (skull top y=13) |
| `high-sun-paladin-aeryn` | 1.140625 | 1 | raised long sword above the head |
| `horned-horror` | 1.25 | 1.25 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ice-wyrm` | 1.625 | 1.625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `khulmanar` | 1.59375 | 1.09375 | club slung above the shoulder |
| `kra-tor` | 1.140625 | 1 | axe blade above the head; the body is ~1 cell (flat) |
| `krogar` | 1 | 1 | flat: native body <= 1.25 cells |
| `kryl-feijan` | 1.703125 | 1.0 | scattered darkness cloud rows 3-55 is not body; first non-darkness body row (blue claw-like limbs) y=58 -> 0.84375 clamped to 1.0 (flat) |
| `kyless` | 1.109375 | 1 | staff and orb held above the head; body ~1 cell |
| `lady-nashva` | 1.671875 | 1.234375 | trident above the head |
| `lady-zoisla` | 1.734375 | 1.3125 | trident and staff above the head |
| `lich` | 1 | 1 | flat: native body <= 1.25 cells |
| `maelstrom` | 1.71875 | 1.71875 | glow is the body (desc: vortex of ice and lightning); derived cap kept (decision 3) |
| `massok` | 1 | 1 | flat: native body <= 1.25 cells |
| `master-vampire` | 1 | 1 | flat: native body <= 1.25 cells |
| `maulotaur` | 1 | 1 | flat: native body <= 1.25 cells |
| `minotaur` | 1 | 1 | flat: native body <= 1.25 cells |
| `minotaur-maze` | 1.453125 | 1.453125 | top is the horns (body); R41 review kept the derived cap |
| `naga-nereid` | 1.046875 | 1 | trident above the head; body ~1 cell |
| `naga-tidecaller` | 1.234375 | 1.078125 | trident above the head; the head top is the body |
| `naga-tidewarden` | 1.09375 | 1 | trident above the head; body ~1 cell |
| `necrotic-abomination` | 1 | 1 | flat: native body <= 1.25 cells |
| `necrotic-mass` | 1 | 1 | flat: native body <= 1.25 cells |
| `ninandra` | 1.265625 | 1.140625 | shipped standee; cool white/cyan (207,251,255) glow rows 30-37 above the head; alpha>128 top y=38; solid top y=39 is 1/64 lower (kept) |
| `norgos-frozen` | 1.671875 | 1.359375 | ice mist above the bear ears |
| `norgos-guardian` | 1.34375 | 1.34375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ogre-guard` | 1.421875 | 1.078125 | hammer and a floating speck above the head (head top y=43) |
| `ogre-mauler` | 1.234375 | 1.234375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ogre-pounder` | 1 | 1 | flat: native body <= 1.25 cells |
| `ogre-rune-spinner` | 1.703125 | 1.296875 | raised arms are body; the vortex is excluded |
| `ogre-warmaster` | 1.390625 | 1.390625 | helmet is the alpha top; the derived cap is kept |
| `ogric-abomination` | 1.5 | 1.140625 | club raised above the head |
| `onilug` | 1.125 | 1.015625 | shadow above the head spikes excluded; solid head top y=47 |
| `pale-drake` | 1.1875 | 1 | staff above the head; body ~1 cell |
| `parasitic-horror` | 1.125 | 1.125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `patchwork-troll` | 1 | 1 | flat: native body <= 1.25 cells |
| `prox` | 1.0625 | 1.0625 | top is the head (a troll, no orb); R41 override dropped |
| `pyromancer` | 1 | 1 | flat: native body <= 1.25 cells |
| `queen-ant` | 1.359375 | 1.359375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `rantha` | 1.75 | 1.75 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `rantha-abomination` | 1.75 | 1.75 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ravenous-horror` | 1.25 | 1.25 | fins are body (desc: spined fins) |
| `rotting-titan` | 1.625 | 1.625 | top is the raised arms (body); R41 override dropped |
| `runed-bone-giant` | 1.75 | 1.75 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `sandworm-queen` | 1.640625 | 1.640625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `sanguine-horror` | 1 | 1 | flat: native body <= 1.25 cells |
| `shax` | 1.03125 | 1.03125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `shiaak-venomblade` | 1.03125 | 1 | raised blades above the body |
| `shivgoroth` | 1 | 1 | flat: native body <= 1.25 cells |
| `slasul` | 1.03125 | 1.03125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `snaproot` | 1.71875 | 1.71875 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `snow-cat` | 1.015625 | 1.015625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `snow-giant` | 1.40625 | 1.40625 | shipped standee; keeps the R40 cap, art body_top=18 (bald head) |
| `snow-giant-boulder-thrower` | 1.625 | 1.484375 | boulder above the raised arms (arm top y=15) |
| `snow-giant-chieftain` | 1.484375 | 1.484375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `snow-giant-thunderer` | 1.578125 | 1.40625 | lightning above the head (head top y=20) |
| `spellblaze-simulacrum` | 1.5625 | 1.5625 | top is the horned head (body); R41 override dropped |
| `spire-dragon` | 1.328125 | 1.328125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `storm-wyrm` | 1.625 | 1.625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `supreme-archmage-linaniil` | 1.015625 | 1.015625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `swarm-hive` | 1.359375 | 1.359375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `swarming-horror` | 1 | 1 | flat: native body <= 1.25 cells |
| `tempest` | 1.125 | 1 | staff and orb held above the head; body ~1 cell |
| `temporal-defiler` | 1.234375 | 1.234375 | top is the raised arms (body); R41 override dropped |
| `temporal-stalker` | 1 | 1 | flat: native body <= 1.25 cells |
| `thalore-wilder` | 1 | 1 | flat: native body <= 1.25 cells |
| `thaurhereg` | 1.53125 | 1.53125 | top is the horns (body); R41 override dropped |
| `the-abomination` | 1.65625 | 1.65625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `the-mouth` | 1.265625 | 1.265625 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `the-possessed` | 1 | 1 | flat: native body <= 1.25 cells |
| `treant` | 1.484375 | 1.484375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ultimate-faeros` | 1.34375 | 1.34375 | glow is the body (desc: fire elementals); derived cap kept (decision 3) |
| `ultimate-gwelgoroth` | 1.375 | 1.375 | glow is the body (desc: air elementals); derived cap kept (decision 3) |
| `ultimate-shivgoroth` | 1.609375 | 1.609375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `ultimate-telugoroth` | 1.609375 | 1.609375 | glow is the body (desc: blurred form); derived cap kept (decision 3) |
| `ultimate-teluvorta` | 1.640625 | 1.640625 | glow is the body (desc: time elemental); derived cap kept (decision 3) |
| `umbral-horror` | 1 | 1 | flat: native body <= 1.25 cells |
| `ungole` | 1.03125 | 1.03125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `urkis` | 1.09375 | 1 | lightning above the head; body ~1 cell |
| `uruivellas` | 1.40625 | 1.296875 | fiery aura above the horns (horn top y=29) |
| `varsha` | 1.75 | 1.75 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `venom-wyrm` | 1.734375 | 1.734375 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `void-spectre` | 1.3125 | 1.125 | trailing wisp above the body |
| `walrog` | 1.609375 | 1.609375 | top is the head water-horns (body); no trident |
| `weaver-matriarch` | 1 | 1 | flat: native body <= 1.25 cells |
| `weaver-queen` | 1.59375 | 1.234375 | sparse bristles/specks excluded; solid body top y=33 |
| `wrathroot` | 1.703125 | 1.703125 | top is the body (head/horns/helmet/hair/arms/wings/fins) |
| `xhaiak-arachnomancer` | 1.515625 | 1.4375 | smoke above the raised legs/arms (limb top y=20) |
| `yeek-mindslayer` | 1.046875 | 1 | raised psi-blade above the body |

"""AE second off-list pool batch: pinned source contracts and AD-style task packs.
No generation or runtime writes; historical prompts remain immutable.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDON = HERE.parents[1]
WS = ADDON.parents[2]
D = 'game/modules/tome/data/'
NPC = D + 'gfx/shockbolt/npc/'
TOK = 'game/addons/tome-checker-revised/data/gfx/tokens/'
STYLE = 'game/addons/tome-checker-revised/art/monsters-v2/masters/prox-v2.png'


def sha(rel):
    return hashlib.sha256((WS / rel).read_bytes()).hexdigest()


def src(path, anchor, after=None, root=D):
    lines = (WS / (root + path)).read_text().splitlines()
    start = 0
    if after:
        start = next(i for i, l in enumerate(lines) if after in l)
    cands = [i + 1 for i, l in enumerate(lines) if i >= start and anchor in l]
    assert cands, (path, anchor)
    return {'path': root + path, 'sha256': sha(root + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at reference lightness, a hair lighter, never darker (the style reference's own brightness). No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
FIT = " The ENTIRE creature, every limb, tail, wing, drip, staff and effect included, fits inside a circle of about three quarters of the disc radius around the disc centre, leaving a wide bare charcoal ring of base plate on every side, yet the creature is large and bold inside that circle."
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value', 'hue'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')


def IDN(png, note):
    return ('identity', NPC + png, note)


# AD's calibrated composition strings, verbatim: no gate or floor change.
_ad = (HERE.parent / 'monster-batch-ad/make_batches.py').read_text()
for _key in ('COMPACT', 'BRIGHT', 'DARKFIX', 'DISCCAL', 'CHEAT'):
    exec(next(l for l in _ad.splitlines() if l.startswith(_key + ' = ')))
COMP = COMP + FIT + COMPACT + BRIGHT + DISCCAL
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ae/'
EVDIR = 'evidence/monster-batch-ae-20261001/source-contracts.json'


def family(name, ids):
    from PIL import Image
    REFS.mkdir(exist_ok=True)
    canvas = Image.new('RGBA', (384, ((len(ids)+2)//3)*128))
    for n, i in enumerate(ids):
        canvas.alpha_composite(Image.open(ADDON / 'data/gfx/tokens' / (i+'.png')).convert('RGBA'), ((n%3)*128, (n//3)*128))
    out = REFS / (name+'.png')
    canvas.save(out)
    return ('family', ART_REL+'refs/'+out.name, 'Shipped siblings in row order: '+', '.join(ids)+'. Match tabletop language; do not copy their body or silhouette.')


STY = ('style', STYLE, 'Approved physical disc, camera and miniature lighting; do not copy the creature.')
FAMILIES = {
    'demons': ['dolleg','uruivellas','thaurhereg','duathedlen','daelach','harkor-zun'],
    'dragons': ['storm-drake','cold-drake','fire-wyrm','venom-wyrm','ice-wyrm','rantha'],
    'giants': ['forest-troll','stone-troll','mountain-troll','minotaur','minotaur-maze','horned-horror'],
    'insects': ['hornet-swarm','giant-spider','weaver-young','weaver-queen','ritch-hunter','ritch-hive-mother-pool'],
    'horrors-wights': ['forest-wight','grave-wight','barrow-wight','dread','dreadmaster','degenerated-ogric-mass'],
}
# Identity inputs were inspected in native-source contact sheet before generation.
ROWS = [
('champion-of-urh-rok', "champion of Urh'Rok", 'major-demon.lua', 'demon', 'major', 'demon_major_champion_of_urh_rok.png', True, 'demons',
 "A massive compact armoured demonic humanoid, enclosed pale silver-steel felsteel plate, two broad swept horns, red visor and chest seams, enormous angular shoulder plates, a two-handed greatsword held vertically close against its chest. A heavy knight silhouette, no wings, no smoke, no bull head. Upper plate surfaces are bright ash-silver.",
 "Champion is an enclosed silver armoured GREAT-SWORD KNIGHT; forge-giant is a burning smith with TWO HAMMERS; shipped demons are thorned brutes, a horned bull, lean shadow demon or smoke-flame warrior. Different body construction, posture and equipment, not a recolour."),
('forge-giant','forge-giant','major-demon.lua','demon','major','demon_major_forge_giant.png',True,'demons',
 "A broad heavy burning demon giant smith with an exposed massive ochre-orange muscular torso, pale hot orange fissures, a short white-hot swept flame mane and small horns, iron-grey bracers and apron, a blocky forge HAMMER in EACH hand pulled close across its thighs. Compact hunched smith stance, two square hammer heads, no sword, no wings, no bull face. Fire stays on the figure; no floor flames or base glow.",
 "A broad exposed smith with TWO SQUARE HAMMERS and forge apron, versus the champion's enclosed plate knight and one greatsword, and versus shipped thorned demon brutes, Uruivellas's bull, lean Duathedlen and smoke-cloud Daelach. Anatomy, equipment and silhouette must separate it."),
('hummerhorn','hummerhorn','swarm.lua','insect','swarms','hummerhorn.png',False,'insects',
 "ONE giant buzzing WASP, golden yellow and mid-brown banded long abdomen curled beneath its thorax, pointed venom stinger kept inside the disc, slender waist, six tucked legs, four pale ivory translucent-looking but opaque-painted folded insect wings, large amber compound eyes and short curved antennae. Side-diagonal hovering insect pose, a single wasp, not a swarm; pale upper planes.",
 "One big long-abdomen flying wasp with thin waist and folded wings; shipped hornet swarm is several insects, ritch hunter stands upright with scythe forelegs, and spiders are wingless eight-legged radial bodies."),
('weaver-matriarch','weaver matriarch','spider.lua','spiderkin','spider','spiderkin_spider_weaver_matriarch.png',True,'insects',
 "A large female arachnid, low broad eight-legged spider with a bulbous oval abdomen, a smaller thorax prominently patterned in YELLOW and WHITE, mid-light cobalt and cornflower blue chitin, pale blue-white highlight planes. Legs folded inward into a compact radial basket with every tip inside the disc. No humanoid torso, no wings, no web effect, no eggs or babies. Fully opaque painted miniature.",
 "Broad low eight-legged blue matriarch with conspicuous yellow-white thorax pattern and bulbous oval abdomen; weaver young is smaller/slender, weaver queen has a different shape, giant spider lacks the matriarch's bold pattern. Different proportions and marking layout."),
('patchwork-troll','patchwork troll','troll.lua','giant','troll','giant_troll_patchwork_troll.png',True,'giants',
 "A hulking asymmetrical troll CONSTRUCT stitched from mismatched troll parts, one swollen pale moss-green arm and one bulky lavender-grey arm, broad pale scarred belly with thick visible stitch seams, small piggy tusked head sunk between uneven shoulders, shattered sword and spear pieces embedded in its back and shoulders kept short, squat bent-knee pose with huge fists close in. Not an undead skeleton; mismatched skin patches are mid-light and bright upper-facing planes.",
 "Patchwork has uneven anatomy, stitch seams, mismatched arms and embedded broken weapon pieces; shipped forest, stone and mountain trolls are coherent natural bodies, not stitched constructs."),
('maulotaur','maulotaur','minotaur.lua','giant','minotaur','giant_minotaur_maulotaur.png',True,'giants',
 "A belligerent bull-headed minotaur with massive swept ivory horns, pale slate-blue fur, broad barrel chest, copper and silver segmented shoulder guards and belt, gripping a large square-headed two-handed GREATMAUL diagonally across the torso. One compact muscular upright bull fighter; no axe, no fire aura, pale silver-blue facing planes and bright ivory muzzle.",
 "A blue-grey hammer-wielding bull, distinctive square greatmaul and angled guarded stance; shipped minotaur carries an axe, labyrinth boss has its own equipment and horned horror is not a bull. Weapon geometry and pose, not colour alone."),
('worm-that-walks','worm that walks','horror.lua','horror','eldritch','horror_eldritch_worm_that_walks.png',False,'horrors-wights',
 "A compact hooded humanoid mass of fat ivory and pale yellow-green MAGGOTS bursting from a torn mid-light sage-brown rotten robe, no solid human skin, face an empty hood filled with worms, two arm-shaped bundles of overlapping plump worms gripping two small bile-stained WARAXES pulled tight at the waist. Worms and ragged robe stay on the figure, no loose spill on the disc, fully opaque, large cream upper highlights.",
 "Worm-that-walks is a ragged hood and worm-bundle arms with TWO AXES, headless horror is a bare headless long-limbed belly creature. Shipped wights are spectral humanoids, flesh golem has solid stitched flesh. Visible worms and robe silhouette, not a colour swap."),
('headless-horror','headless horror','horror.lua','horror','eldritch','horror_eldritch_headless_horror.png',False,'horrors-wights',
 "A HEADLESS gangly humanoid horror, absolutely NO head, face, eyes, skull or horns above its shoulders. Huge distended round pale tan stomach below a visibly empty neck stump, long thin sinewy bent arms pulled inward on either side of its belly and short folded legs, pale ochre-tan flesh with ivory upper planes and mid-slate shadows. Bare skin, no robe, no weapons, no summoned eyes depicted, one compact crouched figure.",
 "Bare headless humanoid with empty neck stump, distended belly and bent gangly arms versus worm-that-walks hood, worms and paired axes; no spectral robe or golem stitches. The Arena HEADLESSHORROR identity keeps native art despite the same name and sprite."),
('storm-wyrm','storm wyrm','storm-drake.lua','dragon','storm','dragon_storm_storm_wyrm.png',True,'dragons',
 "An old powerful lightning dragon, thick serpentine body curled into a tight horseshoe around a raised angular horned head, white-silver and mid-light electric blue scales, jagged forked lightning-shaped dorsal crest, TWO compact bat wings folded into triangular shoulder fins. Broad pearl-white upper planes; small lightning markings confined to the body, no electrical aura, no glow on disc.",
 "Storm WYRM has a thick horseshoe coil, tall horned neck and forked zigzag crest versus the shipped low crouching storm DRAKE; ice wyrm is a spiral with ice crystal spines, fire/venom wyrms have other head and crest structures. Spire dragon is a heavy wingless blade-armoured coil, blinkwyrm is a slender sinuous snake. Do not merely recolour an existing wyrm."),
('spire-dragon','spire dragon','wild-drake.lua','dragon','wild','dragon_wild_spire_dragon.png',True,'dragons',
 "A monstrous patient heavily armoured WINGLESS coiled wyrm, stocky circular coil, broad wedge dragon head held low over the coil, hide covered in large pale stone-grey blade plates and stacked jagged SPIRES and crests, bone-ivory blade ridges and pale slate steel scales, short heavy claws tucked beside its coil. A dense jagged fortress-like silhouette; no wings, no lightning, no ice crystals, fully opaque.",
 "A heavy low wingless armoured blade-and-spire coil, unlike storm wyrm's raised neck and two folded wings, blinkwyrm's lean high S curve, and ice wyrm's pointed crystal crest. Big blade armour and head proportions distinguish the body beyond colour."),
('blinkwyrm','blinkwyrm','wild-drake.lua','dragon','wild','dragon_wild_blinkwyrm.png',True,'dragons',
 "A slender shifting snake-like dragon, elegant compact S-shaped body curled upright in two overlapping bends, small narrow dragon head raised and turned sideways, smooth pale golden-cream and lavender pearl scales with broad light upper planes, two small swept ivory horns, delicate short fins rather than large wings, thin tail curled inward. Fully SOLID opaque miniature: no fading, duplicates, afterimages, portal or teleport effect.",
 "Lean smooth snake-like high S curve with small head and short fins, versus spire dragon's squat broad jagged blade-armour coil, storm wyrm's thick horseshoe and wing triangles, and shipped fire/venom/ice wyrm coils. Different anatomy, pose, scale texture, not colour alone."),
('emperor-wight','emperor wight','wight.lua','undead','wight','emperor_wight.png',True,'horrors-wights',
 "A powerful unearthly humanoid wight, a compact upright undead warrior with pale ivory skull-like face and red eyes, antique GOLD funerary plate and broad gold shoulder guards over a ragged pale ochre-brown mantle, one raised short curved silver SWORD kept tight above its shoulder, other claw hand drawn inward, torn robe hem fully inside the disc. Fully opaque material, no transparency, no crown, no rank emblem, no aura. Broad cream-gold highlight planes along shoulders and armour, bright ivory face and hands.",
 "Emperor is a gold-armoured ragged undead sword warrior with pale skull face and a raised curved sword, not forest wight's green apparition, grave wight's slim spectre, barrow wight's blue-grey armour and front-held weapon, a black dread, or a hood full of maggots. Gold shoulder armour, raised curved sword, ragged mantle and head shape distinguish the identity without a crown or UI badge."),
]


def leaf_block(file, name):
    lines = (WS / (D+'general/npcs/'+file)).read_text().splitlines()
    n = next(i for i,l in enumerate(lines) if 'name = "'+name+'"' in l)
    start = max(i for i in range(n+1) if lines[i].startswith('newEntity{'))
    end = next((i for i in range(n+1,len(lines)) if lines[i].startswith('newEntity{')), len(lines))
    return '\n'.join(lines[start:end]), start+1, end


def build():
    import re
    from PIL import Image, ImageDraw
    identities=[]
    for id_, name, file, typ, sub, png, tall, group, subject, contrast in ROWS:
        block, start, end = leaf_block(file,name)
        base = re.search(r'base = "([^"]+)"',block)[1]
        basepin=src('general/npcs/'+file, 'define_as = "'+base+'"')
        single='explicit image= on the leaf' if re.search(r'(?<!_)\bimage="npc/',block.split('resolvers.nice_tile')[0]) else 'NPC.lua:33 default-name image'
        structure=single+'; no shader, moddable_tile, anim or add_displays on leaf/base; no auto_classes. '
        structure+=('nice_tile{tall=1} expands to invis.png plus one body {image=e.image,display_h=2,display_y=-1}; ' if id_=='patchwork-troll' else 'nice_tile{image="invis.png",add_mos={{image="npc/'+png+'",display_h=2,display_y=-1}}}; ') if tall else 'no nice_tile or add_mos; '
        structure+='nicer_tiles off uses the same single native image; native_tall=true for non-unique tall entry.' if tall else 'flat single native image.'
        s=src('general/npcs/'+file, 'name = "'+name+'"')
        extra=[src('general/npcs/'+file,'resolvers.nice_tile',after='name = "'+name+'"')] if tall else []
        native=NPC+png
        with Image.open(WS/native) as im: size=list(im.size)
        assert size==([64,128] if tall else [64,64]), (id_,size)
        identities.append(dict(id=id_,native_name=name,source=s,base_source=basepin,extra_sources=extra,define_as=None,type=typ,subtype=sub,unique=False,native_tall=tall,image_source=single,structure=structure,native_image='npc/'+png,native_image_path=native,native_image_sha256=sha(native),native_image_size=size,shader=None,moddable_tile=None,anim=None,add_displays=None,nice_tile=('tall=1' if id_=='patchwork-troll' else 'explicit single-body tall') if tall else None,add_mos=[dict(image='npc/'+png,display_h=2,display_y=-1)] if tall else None,leaf_source_lines=[start,end],talents=re.findall(r'Talents\.(T_[A-Z0-9_]+)',block),verdict='READY exact pool identity; Arena HEADLESSHORROR rejected by define_as' if id_=='headless-horror' else 'READY exact pool identity'))
        if tall: identities[-1]['tall_body']=dict(image='invis.png',add_mos=[dict(image='npc/'+png,display_h=2,display_y=-1)],catalog_flag='native_tall=true')
    findings=[
      'All twelve pool leaves are non-unique with no define_as. Eleven names have only one actor leaf; headless horror also has an Arena leaf at zones/arena/npcs.lua:289 bound to HEADLESSHORROR. No current catalog name or id is occupied. Pool headless-horror matches only define_as=nil; Arena stays native by the existing define_as equality guard. No broad subtype mapping.',
      'Same-body copies wear the exact token: hummerhorn can_multiply=4 uses engine NPC reproduction from the same leaf; generic clones with unchanged identity and supported appearance also match. No dedicated talent or effect builds a renamed AE same-body summon, so no name_aliases/image_aliases/variants are required.',
      'Worm that walks on_takehit and Worm Rot spawn CARRION_WORM_MASS (talents/corruptions/rot.lua), a different worm body already mapped. It is not the worm-that-walks token. Headless horror on_added_to_level creates three is_eldritch_eye leaves: other eldritch horrors stay native this batch; eyes are separate actors, not an add_mos composite.',
      'Weaver matriarch escorts are weaver young (already mapped); storm wyrm escorts are storm drakes (already mapped); emperor wight escorts choose undead/wight leaves, each wearing its own exact token, including emperor if drawn. No escort is painted into these masters.',
      'Vaults worms and acidic-vault take worm that walks by exact pool name; horror-chamber takes headless horror by pool name; lightning-vault and sleeping-dragons take storm wyrm. Both relevant early-dungeon layouts may include the shared all.lua pool and these room lookups; source imports do not establish natural spawn probabilities or complete zone coverage.',
      'renegade-wyrmics creates #rng# the Storm Terror from the tall storm wyrm; sludgenest/slime-tunnels destruction orb creates #rng# the Crusher from tall forge-giant and a Corruptor class. Existing captureRandomOrigin policy rejects non-unique tall-body random bosses, preserving native art; no new opt-in to Flame of Urh\'Rok. Maulotaur antimagic quest lookup uses the same leaf.',
      'No per-identity variants, image_aliases or name_aliases are added. Unknown uniques, altered shaders, invisible single images, extra composites, moddable tiles and animations retain native art through existing guards.'
    ]
    ev=dict(schema=1,task='monster-batch-ae: second off-list dungeon-pool batch; static source re-verification only, no game launch; twelve exact identities.',identities=identities,new_ids_not_in_catalog_before_this_batch=[i['id'] for i in identities],summons_and_same_body_copies=dict(method='Source scan of all NPC definitions, talents, timed_effects, maps/vaults, zones, quests and engine reproduction; name/PNG hits and spawn/copy sites inspected.',findings=findings),name_collisions_checked=[dict(name=i['native_name'],other_definitions=['zones/arena/npcs.lua:289 HEADLESSHORROR'] if i['id']=='headless-horror' else [],outcome='exact pool identity; unexpected define_as rejected') for i in identities],kept_native=[dict(name='Arena headless horror',reason='same name/PNG but define_as HEADLESSHORROR; no pool entry may accept it'),dict(name='The Crusher / the Storm Terror random bosses',reason='renamed non-unique tall bodies: existing captureRandomOrigin rejects them')],neighbours_kept_native=[dict(name='multi-hued drakes/wyrms, shadow claws, crystals, liches and other eldritch horrors',reason='later batches; no changes')],runtime_mutation_scan=dict(method='Read each leaf/base resolver and talent lists; scan talents/timed_effects for actor image, type/subtype, shader, add_mos, moddable_tile, add_displays and replace_display writes. Birth sustains and copy/spawn sites inspected.',hits_in_batch=[],auto_classes_review=[dict(identity='all twelve pool leaves',**{'class':'none'},finding='No leaf or base has auto_classes; no urh_rok_form opt-in')],sustains_at_birth_review=[dict(identity='forge-giant',sustained=['Wildfire','Burning Wake'],note='Burning Wake adds _isshaderaura bookkeeping via addShaderAura; supported ignored aura, not actor.shader. Wildfire adds shader_wings particles, not a body write'),dict(identity='patchwork troll',sustained=['Fast Metabolism'],note='life regeneration; Juggernaut and Blinding Speed are activated timed effects'),dict(identity='worm that walks',sustained=['Ruin'],note='temporary values and particles only; Bloodlust is passive timed buff'),dict(identity='spire dragon',sustained=['Kinetic Aura','Kinetic Shield'],note='particles and absorption/temporary values only'),dict(identity='blinkwyrm',sustained=['Disruption Shield','Arcane Power','Essence of Speed'],note='shield particles and stats only'),dict(identity='weaver matriarch, emperor wight',sustained=[],note='base sustains_at_birth; their listed talents are activated/passive, not actor body writes'),dict(identity='champion, hummerhorn, maulotaur, headless horror, storm wyrm',sustained=[],note='no sustains_at_birth; maulotaur Arcane Combat activates later and only changes temporary values')],timed_effects_review='Invisibility shaders, frozen/pinned add_displays and body replacement effects are temporary; existing matcher rejects changed appearance and restores tokens when effects end. No threshold or guard changed.',visibility_review='All token drawing follows actor visibility; no paths, trails or markers added. Native blinkwyrm shifting description does not set shader or animation.',other_hits_reviewed=['Lightning Speed, teleports/Swap and Blinding Speed preserve body image; no motion package implemented here.','Kinetic Aura, Kinetic Shield and Disruption Shield have shader particle effects, not actor.shader.','Corrupted Strength, weapon equip and auto_equip_filters do not create a paper doll on these non-moddable leaves.','Worm Rot builds carrion worm mass, not a copy of caster; thought forms/simulacra generic copies remain governed by existing appearance guards.']))
    # Pin auxiliary source sites as well as each leaf/base and native PNG.
    ev['auxiliary_sources']=[src('zones/arena/npcs.lua','newEntity{ name = "headless horror"'),src('zones/sludgenest/grids.lua','name="forge-giant"'),src('zones/slime-tunnels/grids.lua','name="forge-giant"'),src('maps/vaults/renegade-wyrmics.lua','name = "storm wyrm"'),src('maps/vaults/auto/greater/sleeping-dragons.lua','storm={'),src('maps/vaults/auto/greater/lightning-vault.lua','name="storm wyrm"'),src('maps/vaults/auto/greater/horror-chamber.lua','name="headless horror"'),src('maps/vaults/auto/greater/acidic-vault.lua','name = "worm that walks"'),src('maps/vaults/auto/lesser/worms.lua','name = "worm that walks"'),src('quests/antimagic.lua','name="maulotaur"')]
    out=ADDON/EVDIR; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n')
    families={k:family(k,v) for k,v in FAMILIES.items()}
    packs={}
    for row,i in zip(ROWS,identities):
        id_,name,file,typ,sub,png,tall,group,subject,contrast=row
        refs=[STY,('identity',NPC+png,'Native identity, '+str(i['native_image_size'])+': '+subject),families[group]]
        entry=dict(asset_id=id_,native_name=name,scope='class a dungeon pool; '+i['source']['path']+':'+str(i['source']['line']),sources=[i['source'],i['base_source']]+i['extra_sources'],references=[dict(path=p,sha256=sha(p),role=r,note=n) for r,p,n in refs],contrast_dimensions=['silhouette','value','hue'],prompt_fields=dict(subject=subject+CHEAT,contrast=contrast,composition=COMP+DARKFIX,palette='Mid-light creature masses and broad pale upper-left highlights, with a thin bright rim. '+DISC+' Keep the whole disc at reference lightness; no cast shadow or colour spill.'),kind='creature',max_attempts=1,gate='ready',gate_reason=i['structure']+' Exact static source contract, no game launch; see '+EVDIR,render_evidence=[dict(path='game/addons/tome-checker-revised/'+EVDIR,sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
        packs.setdefault((ROWS.index(row)//3+1),[]).append(entry)
    if (HERE / 'retries.py').exists():
        namespace = {}
        exec((HERE / 'retries.py').read_text(), namespace)
        namespace.get('add_retries', lambda packs: None)(packs)
    for n,entries in packs.items():
        p=ADDON/f'art/production/batches/monster-batch-ae-{n}.json'
        if not p.exists(): p.write_text(json.dumps(dict(schema=1,batch_id=f'monster-batch-ae-{n}',assets=entries),ensure_ascii=False,indent=2)+'\n')
    # Contact sheet is a viewing aid only; source pixels unaltered except nearest scaling.
    canvas=Image.new('RGBA',(6*190,2*340),(48,48,48,255)); draw=ImageDraw.Draw(canvas)
    for n,i in enumerate(identities):
        im=Image.open(WS/i['native_image_path']).convert('RGBA'); im=im.resize((128,256 if i['native_tall'] else 128),Image.Resampling.NEAREST)
        x=(n%6)*190; y=(n//6)*340
        draw.text((x+3,y+3),i['id'],fill='white'); canvas.alpha_composite(im,(x+20,y+30))
    canvas.save(REFS/'native-identities.png')

if __name__=='__main__': build()

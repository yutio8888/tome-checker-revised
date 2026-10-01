"""AF exact source contracts and task packs; AD/AE composition and gates unchanged."""
import hashlib, importlib.util, json, re
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
ADDON=HERE.parents[1]
WS=ADDON.parents[2]
D='game/modules/tome/data/'
NPC=D+'gfx/shockbolt/npc/'
ART_REL='game/addons/tome-checker-revised/art/monster-batch-af/'
EVDIR='evidence/monster-batch-af-20261001/source-contracts.json'
spec=importlib.util.spec_from_file_location('ae',HERE.parent/'monster-batch-ae/make_batches.py'); ae=importlib.util.module_from_spec(spec);spec.loader.exec_module(ae)
sha=ae.sha
src=ae.src
ROWS=[
('nightmare-horror','nightmare horror','horror.lua','horror','eldritch','horror_eldritch_nightmare_horror.png',False,'horrors',
 'A compact black nightmare made flesh: central huge round tooth-lined maw, small deep-set pale eyes, eight thick curled hooked tendrils radiating inward around it. Charcoal-violet skin with broad MID-LIGHT slate-grey raised folds and ivory teeth, thin pale cool rim on every hooked limb. Tangled predatory radial silhouette, no robe, no humanoid skull, no weapon. Dark local creases only; the broad body planes must remain legible.',
 'Radial hooked tendril monster with enormous central maw; not umbral hooded humanoid, dread ghost, luminous four-armed humanoid, ooze mound or aquatic abyssal horror.'),
('radiant-horror','radiant horror','horror.lua','horror','eldritch','horror_eldritch_radiant_horror.png',False,'horrors',
 'A lanky tall golden-light humanoid with EXACTLY FOUR long arms: upper pair raised outward and bent inward, lower pair bent down beside narrow waist. Small faceless smooth oval head, two long legs, opaque sculpted bright warm ivory-gold body with amber creases. Compact symmetrical open four-arm silhouette. Light belongs only to body, no halo, no base glow, no floor effects.',
 'Lanky narrow four-arm humanoid with four visibly separate hands and two long legs, versus luminous horror compact broad body, nightmare radial maw, maelstrom spiral vortex and parasitic lamprey.'),
('dreaming-horror','dreaming horror','horror.lua','horror','eldritch','horror_eldritch_dreaming_horror.png',True,'horrors',None,None),
('maelstrom','maelstrom','horror.lua','horror','eldritch','horror_eldritch_maelstrom.png',True,'horrors',
 'A compact upright hungry VORTEX of solid sculptural blue-white ICE and LIGHTNING: twisting tapering spiral column with a wide swirling upper jaw, jagged ice teeth, two short hooked ice claws pulled inward, layered spiral ridges. Opaque sapphire-grey ice masses with broad pale frosty raised surfaces and restrained bright yellow-white crackle ON THE BODY ONLY. No humanoid, no wings, no snake head or dragon, no floor snow or aura.',
 'Upright tapering angular spiral vortex, versus hooked radial nightmare, smooth four-armed radiant humanoid, lamprey tube and all existing ooze, bone, blood or tentacle horrors.'),
('parasitic-horror','parasitic horror','horror.lua','horror','eldritch','horror_eldritch_parasitic_horror.png',True,'horrors',
 'One gigantic thick lamprey-like parasite, squat upright curved grub tube with its short tail tucked under, oversized upward-facing circular suction mouth containing concentric cream hooked teeth. Writhing lumpy olive-green flesh with broad pale yellow-green dorsal folds and individual under-skin swellings. Mouth is the unmistakable top focal point. No eyes, arms, legs, weapons or armour; fully contained compact C-shaped body.',
 'Single upright thick lamprey tube and concentric suction mouth, not a many-worm mass, ooze puddle, radial nightmare maw, humanoid horror or winged serpent.'),
('lich','lich','lich.lua','undead','lich','undead_lich_lich.png',True,'liches',
 'A gaunt skeleton necromancer wearing a simple narrow burgundy robe with restrained gold piping and a low plain hood framing a bright ivory skull. One bent bony arm raises a small plain wand beside its face, other hand low. Lean forward spellcaster stance with narrow shoulders and visibly skeletal feet. Mid-light wine-red cloth on broad lit folds. No crown, no rank mark, no halo.',
 'Narrow plain hooded robe and ONE small raised wand; ancient lich is broad ragged mantle with TWO extended skeletal casting hands; archlich is monumental armoured spiked regalia and blue cape; blood lich is unrobed blood anatomy.'),
('ancient-lich','ancient lich','lich.lua','undead','lich','undead_lich_ancient_lich.png',True,'liches',
 'An ancient skeletal sorcerer in a broad weathered moss-olive funerary mantle: low cowl around pale lavender-ivory bare skull, asymmetrical layered shredded cape panels sweeping inward, two long skeletal forearms extended forward with BOTH open casting hands. Heavy curved shawl collar, worn parchment cloth highlights and ivory finger masses. Stooped broad triangular mantle silhouette, no wand, no crown, no rank graphic.',
 'Broad shredded asymmetrical shawl mantle and paired outstretched casting hands, versus lich narrow intact robe with raised wand, archlich upright spiked armour/blue cape and blood lich naked fluid humanoid.'),
('archlich','archlich','lich.lua','undead','lich','undead_lich_archlich.png',True,'liches',
 'A monumental upright undead sorcerer in ornate ivory-silver spiked funerary shoulder regalia over a broad DARK BLUE heavy cape and layered ash-grey long robe. Bare desiccated reddish skull under tall narrow bone-spired ceremonial headdress, two hands held low; imposing broad angular shoulders and symmetrical heavy bell-shaped cape. Broad mid-light blue-grey cloth folds, bright ivory shoulder plates and headdress. Headdress is physical native regalia, no floating crown or tactical rank mark.',
 'Upright towering bone-spired headdress and broad angular shoulder armour with symmetrical blue bell cape; unlike simple hooded wand lich, stooped torn-shawl ancient lich or naked blood lich.'),
('blood-lich','blood lich','lich.lua','undead','lich','undead_lich_blood_lich.png',False,'liches',
 'The seething disembodied BLOOD of a powerful necromancer forms a compact wiry humanoid: distinct fluid skull-shaped face, narrow rib-like torso, two sharply bent long arms, two widely planted bent legs and short blood-vein tendrils curled inward around shoulders. NO skeleton material, robe, armour, staff or crown. Opaque lacquer-like crimson blood sculpture with broad pale salmon-red upper highlights, fine dark channels and contained drips; no ground spill.',
 'Lean unrobed angular blood humanoid with clear head, two arms and two legs, versus animated blood round faceless suspended dripping sac, sanguine horror heavy monstrous blood mass and all robed lich tiers.'),
('animated-blood','animated blood','horror-undead.lua','undead','blood','undead_horror_animated_blood.png',True,'liches',
 'One rounded faceless suspended sac of animated crimson blood, a squat domed asymmetrical blob with a scalloped hanging underside, three thick suspended drip lobes and a few attached drop buds kept close under the sac. Opaque glossy crimson liquid with broad pale salmon raised surfaces and dark red creases. No humanoid face, eyes, skull, limbs, tentacles, armour or weapons. No floor puddle or splash.',
 'Round domed faceless blood sac with hanging short drip lobes, versus blood lich articulated humanoid, sanguine horror monstrous anatomy, bone horror skeleton and ordinary ground-hugging oozes.'),
]
IDS=[r[0] for r in ROWS if r[8]]
FAMILIES={'horrors':['luminous-horror','oozing-horror','abyssal-horror','umbral-horror','bone-horror','sanguine-horror','dread','worm-that-walks','headless-horror'], 'liches':['skeleton-magus','skeleton-mage','emperor-wight','barrow-wight','bone-horror','sanguine-horror','dread']}

def build():
 identities=[]
 for id_,name,file,typ,sub,png,tall,group,subject,contrast in ROWS:
  block,start,end=ae.leaf_block(file,name)
  base=re.search(r'base\s*=\s*"([^"]+)"',block)[1]
  source=src('general/npcs/'+file,'name = "'+name+'"')
  basepin=src('general/npcs/'+file,'define_as = "'+base+'"')
  native=NPC+png
  shorthand='tall=1' in block
  shader='shadow_simulacrum' if id_=='dreaming-horror' else None
  default='npc/'+typ+'_'+sub+'_'+name.replace(' ','_')+'.png'
  structure=('NPC default-name image; '+('nice_tile single body 64x128, display_h=2, display_y=-1; ' if tall else 'flat single image 64x64; '))
  if id_=='animated-blood': structure+='Explicit nice_tile body is undead_horror_animated_blood.png, NOT the missing default undead_blood_animated_blood.png. Nicer_tiles-off stays native; no invented image alias. Artifact Bloodcaller copies same PNG at display_h=1/display_y=0; separately pinned exact summon contract.'
  if shader: structure+='Actor shader shadow_simulacrum and sleep shield particles: unsupported; leave native, no artwork.'
  with Image.open(WS/native) as im:size=list(im.size)
  extras=[src('general/npcs/'+file,'resolvers.nice_tile',after='name = "'+name+'"')] if tall else []
  identities.append(dict(id=id_,native_name=name,source=source,base_source=basepin,extra_sources=extras,define_as=None,type=typ,subtype=sub,unique=False,native_tall=tall,native_image='npc/'+png,native_image_path=native,native_image_sha256=sha(native),native_image_size=size,default_image=default,default_image_exists=(WS/(D+'gfx/shockbolt/'+default)).exists(),image_source='NPC.lua:33 default-name image; nice_tile explicit body overrides if configured',structure=structure,shader=shader,moddable_tile=None,anim=None,add_displays=None,nice_tile=('tall=1' if shorthand else 'explicit single-body tall') if tall else None,add_mos=[dict(image='npc/'+png,display_h=2,display_y=-1)] if tall else None,leaf_source_lines=[start,end],talents=re.findall(r'Talents\.(T_[A-Z0-9_]+)',block),direct_display_hits=[l.strip() for l in block.splitlines() if re.search(r'shader|addParticles|addShaderAura|sleep_particle|summon|make_escort|HORROR_PARASITIC_LEECHES',l)],verdict='READY' if subject else 'NATIVE unsupported actor shader'))
  if tall:identities[-1]['tall_body']=dict(image='invis.png',add_mos=[dict(image='npc/'+png,display_h=2,display_y=-1)],catalog_flag='native_tall=true' if subject else 'none; unmapped')
 auxiliary=[src('resolvers.lua','function resolvers.calc.nice_tile',root='game/modules/tome/'),src('class/NPC.lua','-- Grab default image name',root='game/modules/tome/'),src('general/objects/world-artifacts-far-east.lua','name = _t"animated blood"'),src('zones/sludgenest/grids.lua','name="archlich"'),src('zones/slime-tunnels/grids.lua','name="archlich"'),src('maps/vaults/renegade-undead.lua','name = "lich"'),src('maps/vaults/greater-crypt.lua','name="lich"'),src('maps/vaults/auto/greater/horror-chamber.lua','name="radiant horror"')]
 ev=dict(schema=1,task='AF third off-list pool batch; static source verification only; no game launch',identities=identities,auxiliary_sources=auxiliary,name_collisions_checked=['No occupied catalog name/id among ten candidates. Animated blood also has Bloodcaller inline summon with same type/subtype and PNG but 1x body; pinned constructor required. Psionic Maelstrom talent terrain effect has different type/subtype/name and is not this creature.'],summons_and_same_body_copies=['Unchanged same-body copies use exact pool entry; temporalClone already generic, no AF clone code.','Radiant horror escorts luminous horror (already mapped). Parasitic horror on_takehit spawns HORROR_PARASITIC_LEECHES, a different body left native. Dreaming horror summons dream seeds, separate unsupported bodies.','All liches Call Shadows create shadow actors (own body), not lich copies.','Bloodcaller animated blood is same PNG at 1x dimensions: exact summoned dexmage/negative_status_effect_immune/max_vim=200 contract is supported; arbitrary 1x composites stay native.','Vault radiant horror and lich filters use pool leaves. Greater-crypt randomized tall lich and orb pedestal Neverdead archlich remain native under captureRandomOrigin policy.'],runtime_mutation_scan='Read base/leaf, callbacks, resolve inherited talent modes and display writers in talent-contracts.json. Nightmare Stealth/Gloom/Abyssal Shroud, lich Hymn/Stone Skin/Call Shadows and maelstrom Thunderstorm are native particles/aura bookkeeping; any actual actor shader/animation/display replacement remains rejected. Maelstrom directly adds body_of_ice _isshaderaura and snowfall particles, not actor.shader.',excluded=['dreaming horror shader; no generation or mapping','multi-hued drakes/wyrms','shadow claws','crystals'])
 out=ADDON/EVDIR;out.write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n')
 families={}
 for group,ids in FAMILIES.items():
  c=Image.new('RGBA',(384,((len(ids)+2)//3)*128))
  for n,i in enumerate(ids):c.alpha_composite(Image.open(ADDON/'data/gfx/tokens'/f'{i}.png').convert('RGBA'),(n%3*128,n//3*128))
  p=HERE/'refs'/f'{group}.png';c.save(p)
  families[group]=dict(path=ART_REL+'refs/'+p.name,sha256=sha(ART_REL+'refs/'+p.name),role='family',note='Shipped siblings row order: '+', '.join(ids)+'. Compare shape; do not copy anatomy.')
 packs={}
 for row,i in zip(ROWS,identities):
  id_,name,file,typ,sub,png,tall,group,subject,contrast=row
  if not subject:continue
  refs=[dict(path=ae.STYLE,sha256=sha(ae.STYLE),role='style',note='Approved tabletop disc, camera, lighting only; do not copy creature.'),dict(path=NPC+png,sha256=sha(NPC+png),role='identity',note='Inspected native identity and anatomy, '+str(i['native_image_size'])),families[group]]
  a=dict(asset_id=id_,native_name=name,scope='class a off-list pool; '+i['source']['path']+':'+str(i['source']['line']),sources=[i['source'],i['base_source']]+i['extra_sources']+auxiliary[:2],references=refs,contrast_dimensions=['silhouette','value','hue'],prompt_fields=dict(subject=subject+ae.CHEAT,contrast=contrast,composition=ae.COMP+ae.DARKFIX,palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. '+ae.DISC+' Keep whole disc at reference lightness; no cast shadow or colour spill.'),kind='creature',max_attempts=2,gate='ready',gate_reason=i['structure']+' Static evidence only; live separate.',render_evidence=[dict(path='game/addons/tome-checker-revised/'+EVDIR,sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
  packs.setdefault(IDS.index(id_)//3+1,[]).append(a)
 for n,assets in packs.items():
  p=ADDON/f'art/production/batches/monster-batch-af-{n}.json'
  if not p.exists():p.write_text(json.dumps(dict(schema=1,batch_id=f'monster-batch-af-{n}',assets=assets),ensure_ascii=False,indent=2)+'\n')
 # Source READY means supported appearance; final art admission is separate.
 admitted=json.loads((HERE/'final-admission.json').read_text())['accepted_ids'] if (HERE/'final-admission.json').exists() else IDS
 (HERE/'catalog.json').write_text(json.dumps([dict(id=i) for i in admitted],indent=2)+'\n')
 (HERE/'catalog.js').write_text('window.monsterCatalog = '+(HERE/'catalog.json').read_text().strip()+';\n')

if __name__=='__main__':build()

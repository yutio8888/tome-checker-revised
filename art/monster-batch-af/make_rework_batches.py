"""Coordinator-authorized AF redesign/retry; preserve original packs and all gates."""
import copy, hashlib, json
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WS=ROOT.parents[2]
EV=ROOT/'evidence/monster-batch-af-rework-20261001'
REL='game/addons/tome-checker-revised/'
def pin(path):
 return dict(path=REL+path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
def build():
 EV.mkdir(exist_ok=True)
 request=dict(authority='Explicit user/coordinator review in this same task',accepted_previous=['nightmare-horror','maelstrom','parasitic-horror','lich','ancient-lich','archlich','animated-blood'],native_accepted={'dreaming-horror':'shader'},rework={'blood-lich':'No waiver. The missing image/path repair was an infrastructure failure, explicitly authorized for retry with more serial calls. Redesign as flayed blood-red skeletal lich-mage, no robe, crimson-scarlet highlights and pale bone accents; unchanged body floor 65.','radiant-horror':'Prior 48/64 silhouette was too similar to luminous horror. Structural redesign: exactly four arms widely spread in a clear X, white-hot sunburst ray crown behind body, white-gold rather than yellow. Keep native identity, disc/style gates unchanged.'},no_game_launch=True,body_floor=65.0,disc_and_style_gates='unchanged',supersedes='Blood-lich PENDING request is withdrawn by user direction; do not request or apply a waiver.')
 r=EV/'review-request.json'
 if not r.exists():r.write_text(json.dumps(request,indent=2)+'\n')
 blood=next(a for a in json.loads((ROOT/'art/production/batches/monster-batch-af-3.json').read_text())['assets'] if a['asset_id']=='blood-lich')
 radiant=next(a for a in json.loads((ROOT/'art/production/batches/monster-batch-af-1.json').read_text())['assets'] if a['asset_id']=='radiant-horror')
 out=[]
 for original in [blood,radiant]:
  a=copy.deepcopy(original);id_=a['asset_id']
  a['scope']+='; coordinator-requested AF rework; source identity unchanged'
  a['references'][2]=dict(**pin('art/monster-batch-af/refs/rework-siblings.png'),role='family',note='Opened shipped siblings in row order: luminous horror, previous radiant horror, red-robed lich, sanguine horror, animated blood, bone horror. Do not copy the rejected radiant pose; compare silhouette and value at 48/64px.')
  a['render_evidence'].append(pin('evidence/monster-batch-af-rework-20261001/review-request.json'))
  if id_=='blood-lich':
   a['prompt_fields']['subject']='A flayed BLOOD-RED SKELETAL LICH-MAGE, a wiry upright humanoid undead sorcerer with a clearly exposed rib cage, stern ivory-bone skull face washed in bright scarlet, articulated pale bone shoulder and forearm ridges partly sheathed in blood, long bent arms and two planted skeletal legs. NO ROBE, CLOTH, CLOAK OR ARMOUR. One open claw hand holds a small bright crimson blood-orb close beside the ribcage; the other reaches inward in a casting gesture. A small low physical bone-and-blood circlet hugs the skull, no floating rank mark. Bold broad MID-LIGHT CRIMSON-SCARLET surfaces over torso and limbs, large pale ivory bone accents on skull, ribs and limbs, pink-scarlet highlight planes covering most body surfaces, deep red only in narrow creases. All blood tendrils short and tucked in, no blood puddle or floor aura. Complete compact flayed lich sorcerer, not a robed wizard, giant blood mass or faceless blob. Body must be strongly light enough at 48px: broad pale bone and scarlet masses, not tiny white specular dots. Aim masked-body luminance comfortably ABOVE 65, around 85-100, while keeping the neutral disc unchanged.'
   a['prompt_fields']['contrast']='Structural identity: exposed skeletal rib cage, recognizable skull, long thin casting arms, planted bony legs, small blood-orb and close physical circlet. Red-robed lich is a narrow hooded cloth caster with a wand; NEVER copy its robe. Sanguine horror is a heavy amorphous monstrous blood mass, animated blood is a round faceless dripping sac. This is a lean naked skeletal lich-mage, with conspicuous pale bone planes and scarlet wet anatomy; not a recolour of any sibling.'
   a['gate_reason']+=' Explicit user-authorized retry/redesign after infrastructure provenance failure, NOT a waiver or lowered gate.'
   a['retry_authorization']=dict(previous_batch='monster-batch-af-3',reason='User explicitly authorizes additional serial calls after infrastructure failure; new flayed skeletal lich-mage direction and broad pale bone/scarlet value structure.',evidence=[pin('art/production/handoffs/monster-batch-af-3/blood-lich/imagegen-calls/call-2/call.json'),pin('evidence/monster-batch-af-rework-20261001/review-request.json')])
  else:
   a['prompt_fields']['subject']='A lanky radiant horror, a faceless narrow humanoid made of WHITE-HOT GOLDEN LIGHT, with EXACTLY FOUR long arms spread very clearly into a broad X: two upper arms stretch diagonally up-left/up-right, two lower arms diagonally down-left/down-right; four separated hands at four unmistakable diagonal tips. Two thin legs descend close together beneath the waist. Behind head and shoulders is a compact opaque sculptural WHITE-HOT SUNBURST of thick pointed rays, eight broad angular ivory-white rays with short warm-gold recesses, framing upper torso; NO solid circular halo ring. This sunburst belongs to the creature body and stays fully within the safe central plate area; no glow/bounce light whatsoever on the disc. Smooth small faceless head; large broad ivory-white body planes, hot pale white-gold limbs, restrained amber grooves only. Bold front-facing upright four-arm X pose, no fists curled inward, no crouching stance, no wings or weapons, no robe. Render opaque physical miniature sculpture, with clearly separated ray geometry and four limbs at 48px, not blurred luminous particles. Keep entire figure and sunburst compact inside inner three quarters of disc radius, wide visible bare base ring on all sides.'
   a['prompt_fields']['contrast']='Shipped luminous horror is a yellow-gold broad crouching humanoid with drooping curved arms and no ray crown. New radiant horror must be a white-hot narrow upright four-armed X with a thick spiked sunburst framing head/upper torso: the silhouette changes at 48px and in grayscale, not just the hue. All FOUR arms extend straight diagonally into open negative spaces, never two faint extra inward-curled arms. Sunburst is creature anatomy/light sculpture, not faction/health/selection/rank UI.'
   a['refinement']=dict(supersedes='radiant-horror',previous_batch='monster-batch-af-1',design_change_reason=request['rework']['radiant-horror']+' This is a separately reviewed change in pose and thick sculptural ray geometry, not a colour-only correction.',evidence=[pin('art/production/handoffs/monster-batch-af-1/radiant-horror/receipts/attempt-1.json'),pin('art/production/handoffs/monster-batch-af-1/radiant-horror/imagegen-calls/call-1/call.json'),pin('evidence/monster-batch-af-rework-20261001/review-request.json')])
  a['max_attempts']=2
  out.append(a)
 p=ROOT/'art/production/batches/monster-batch-af-4.json'
 if not p.exists():p.write_text(json.dumps(dict(schema=1,batch_id='monster-batch-af-4',assets=out),indent=2)+'\n')
if __name__=='__main__':build()

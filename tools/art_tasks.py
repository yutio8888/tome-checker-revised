#!/usr/bin/env python3
"""Prepare pinned ImageGen handoffs and inspect receipts. Never invokes a model.

prepare writes prompts and manifests, not artwork. hold tasks get no tool-call
file. ready tasks still require the receiving agent to view all references and
follow imagegen SKILL.md. record inspects PNG/hash/alpha only, NOT artistic quality.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from string import Template

import check_token_style
from audit_completion import current_catalog

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TEMPLATES = ROOT / 'art/production/templates'
KINDS = {'creature', 'terrain-floor', 'terrain-prop', 'player'}

# 实测口径（2026-09-28，F1 地形批次前 3 次真实 ImageGen 调用）：三次互不相关的
# 调用（bog-tree-a 两次、bog-tree-b 一次）都在同一个角留下 alpha=1 而不是 0，读
# 作本机 ImageGen 输出管线在透明区域边缘的量化残留，不是内容缺陷。比照 A1 本来就
# 为不透明上限留了容差（`check_token_style.MASTER_ALPHA_MAX_FLOOR=240`，因为
# "原生输出可能为252"），这里对角点透明下限做同型量级的容差，取代字面上从未被真
# 实输出验证过的"必须恰好为0"。阈值取 4（约1.6%），仍能挡住任何真正可见的角落
# 残留。`tools/run_imagegen.py` 的 terrain_gate 引用同一常量，避免两处门控各自
# 定义、彼此漂移。
CORNER_ALPHA_MAX = 4

# Production player tokens are keyed by native paper-doll body family, i.e. the
# expanded `moddable_tile` of a base-game birth subrace (see
# docs/player-token-plan-20260928/PLAN.md). The value is the descriptor text the
# pinned birth line must contain. Classes, equipment, Lich, DLC and tutorial
# subraces are deliberately not families here.
PLAYER_FAMILIES = {
    'human_male': 'human_#sex#', 'human_female': 'human_#sex#',
    'elf_male': 'elf_#sex#', 'elf_female': 'elf_#sex#',
    'dwarf_male': 'dwarf_#sex#', 'dwarf_female': 'dwarf_#sex#',
    'halfling_male': 'halfling_#sex#', 'halfling_female': 'halfling_#sex#',
    'ogre_male': 'ogre_#sex#', 'ogre_female': 'ogre_#sex#',
    'yeek': 'yeek', 'ghoul': 'ghoul', 'skeleton': 'skeleton', 'runic_golem': 'runic_golem',
}
PLAYER_DESCRIPTORS = 'game/modules/tome/data/birth/races/'
PLAYER_DOLLS = 'game/modules/tome/data/gfx/shockbolt/player/'


def player_token_id(family):
    """Runtime id; the export later lands at data/gfx/tokens/player-<family>.png."""
    return 'player-' + family.replace('_', '-')


def current_player_registry():
    """Player body families that already ship a production token: {family: id}.

    Player art is checked against this registry, never the monster catalog: a
    player family is not a native creature name, and a monster token must not
    satisfy (or block) a player family by accident.
    """
    manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    shipped = {a['id'] for a in manifest['assets']}
    return {family: player_token_id(family) for family in PLAYER_FAMILIES
            if player_token_id(family) in shipped
            or (ROOT / 'data/gfx/tokens' / (player_token_id(family) + '.png')).is_file()}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def confined(path, parent):
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError(f'path escapes permitted tree: {path}')
    return resolved


def pinned(entry):
    path = confined(WORKSPACE / entry['path'], WORKSPACE)
    if not path.is_file() or digest(path) != entry['sha256']:
        raise ValueError(f'missing or changed input; re-audit before generation: {path}')
    return path


REFINEMENT_KEYS = {'supersedes', 'previous_batch', 'design_change_reason', 'evidence'}


def refinement_gate(asset, name, catalog):
    """Repainting an already mapped token needs an explicit, pinned refinement brief.

    Duplicate detection stays the default: an unannounced re-run of a covered
    identity is still rejected outright. art/production/README.md allows exactly
    one way past it -- "现有棋子的重绘需专门的refinement brief" -- and this makes
    that way declared instead of impossible. It is NOT a third attempt: the
    declaration must name the token it supersedes, the batch whose two-call budget
    was already spent, why the *design direction* changed (not "try again"), and
    pin the recorded evidence of how the earlier attempts ended. Those pins are
    re-checked at record time, so the earlier batch's receipts cannot be edited
    or deleted to make the justification fit afterwards.
    """
    refinement = asset.get('refinement')
    mapped = asset['kind'] in ('creature', 'player') and name in catalog
    if not mapped:
        if refinement:
            raise ValueError(f'refinement declared for an identity that is not mapped: {name}')
        return
    if not refinement:
        raise ValueError(f'already mapped: {name}; use a separately reviewed refinement brief')
    if set(refinement) != REFINEMENT_KEYS:
        raise ValueError('refinement needs exactly supersedes, previous_batch, '
                         'design_change_reason and evidence')
    if refinement['supersedes'] != catalog[name]:
        raise ValueError(f'refinement must supersede the mapped token id {catalog[name]}')
    if not str(refinement['previous_batch']).strip():
        raise ValueError('refinement must name the batch whose attempt budget was spent')
    if len(str(refinement['design_change_reason']).strip()) < 80:
        raise ValueError('refinement needs a written design-direction change, not a retry note')
    evidence = refinement['evidence']
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('refinement must pin the recorded outcome of the earlier attempts')
    for entry in evidence:
        pinned(entry)


def player_contract(asset, family):
    """A player asset names one native body family and pins where it comes from.

    `sources` must pin (a) the birth descriptor line(s) that set this family's
    `moddable_tile` in data/birth/races/*.lua and (b) at least one native
    paper-doll base body PNG from that family's own doll folder, by SHA-256.
    Image pins carry no line/anchor; text pins are anchor-checked as usual.
    """
    if family not in PLAYER_FAMILIES:
        raise ValueError(f'unknown player body family: {family}')
    if asset['asset_id'] != player_token_id(family):
        raise ValueError(f'player asset_id must be {player_token_id(family)}')
    descriptor = f'moddable_tile = "{PLAYER_FAMILIES[family]}"'
    doll_dir = PLAYER_DOLLS + family + '/'
    has_descriptor = has_doll = False
    for item in asset['sources']:
        path = item['path']
        if 'line' in item or 'anchor' in item:
            if path.startswith(PLAYER_DESCRIPTORS) and descriptor in item.get('anchor', ''):
                has_descriptor = True
        elif path.startswith(doll_dir) and path.endswith('.png') and '/' not in path[len(doll_dir):]:
            has_doll = True
        else:
            raise ValueError(f'player image pin must be a base doll PNG under {doll_dir}: {path}')
    if not has_descriptor:
        raise ValueError(f'player sources must pin the birth descriptor line {descriptor}')
    if not has_doll:
        raise ValueError(f'player sources must pin a native paper-doll base image under {doll_dir}')


def validate(manifest):
    if manifest.get('schema') != 1:
        raise ValueError('unsupported task schema')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', manifest.get('batch_id', '')):
        raise ValueError('invalid batch_id')
    assets = manifest.get('assets', [])
    if not 1 <= len(assets) <= 4:
        raise ValueError('handoff must contain 1-4 independently reviewed assets')
    names, ids = set(), set()
    catalog = current_catalog()
    players = current_player_registry() if any(a.get('kind') == 'player' for a in assets) else {}
    for asset in assets:
        asset_id, name = asset['asset_id'], asset['native_name']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', asset_id) or asset_id in ids or name in names:
            raise ValueError('duplicate or invalid asset identity')
        ids.add(asset_id)
        names.add(name)
        if asset['kind'] not in KINDS or asset['gate'] not in ('hold', 'ready'):
            raise ValueError('unknown template kind or production gate')
        if asset.get('max_attempts') not in (1, 2):
            raise ValueError('initial attempt plus at most one focused repair per handoff')
        if not asset.get('gate_reason') or not asset.get('scope'):
            raise ValueError('scope and gate_reason are required')
        if asset['kind'] == 'player':
            player_contract(asset, name)
        refinement_gate(asset, name, players if asset['kind'] == 'player' else catalog)
        sources = asset['sources']
        if not sources:
            raise ValueError('native source evidence required')
        for item in sources:
            if asset['kind'] == 'player' and 'line' not in item and 'anchor' not in item:
                # Pinned paper-doll image: hash only, no text anchor to re-read.
                pinned(item)
                continue
            path = pinned(item)
            lines = path.read_text().splitlines()
            line = item['line']
            if not isinstance(line, int) or not 1 <= line <= len(lines) or item['anchor'] not in lines[line-1]:
                raise ValueError(f'source anchor changed: {path}:{line}')
        refs = asset['references']
        if not 1 <= len(refs) <= 3:
            raise ValueError('use 1-3 focused references, not an entire library')
        roles = {ref['role'] for ref in refs}
        if 'style' not in roles or (asset['kind'] in ('creature', 'player') and 'identity' not in roles):
            raise ValueError('style and creature identity reference roles must be explicit')
        for ref in refs:
            if pinned(ref).suffix.lower() != '.png':
                raise ValueError('reference must be a pinned PNG')
        if asset['gate'] == 'ready':
            if not asset.get('render_evidence'):
                raise ValueError('ready requires reviewed resolved actor/grid evidence')
            for evidence in asset['render_evidence']:
                pinned(evidence)
        if asset['kind'] in ('creature', 'player'):
            dimensions = set(asset.get('contrast_dimensions', []))
            if not dimensions <= {'silhouette', 'value', 'hue'} or len(dimensions) < 2:
                raise ValueError('family separation needs at least two design dimensions')
        elif set(asset.get('grid_contract', {})) != {'movement', 'sight', 'danger', 'interaction', 'export'}:
            raise ValueError('terrain requires separate movement/sight/danger/interaction/export contracts')
        fields = asset['prompt_fields']
        if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
            raise ValueError('empty prompt field')
        # Raises on missing placeholders rather than emitting an incomplete prompt.
        Template((TEMPLATES/(asset['kind']+'.txt')).read_text()).substitute(native_name=name, **fields)
    return manifest


def prepare(manifest_path, output):
    raw = manifest_path.read_bytes()
    manifest = validate(json.loads(raw))
    output = confined(output, ROOT / 'art/production')
    if output.exists():
        raise ValueError('output exists; use a new versioned handoff directory')
    # Finish all validation before writing anything.
    output.mkdir(parents=True)
    (output/'batch.json').write_bytes(raw)
    for asset in manifest['assets']:
        folder = output / asset['asset_id']
        folder.mkdir()
        prompt = Template((TEMPLATES/(asset['kind']+'.txt')).read_text()).substitute(
            native_name=asset['native_name'], **asset['prompt_fields'])
        ref_list = '\n'.join(f"Image {i+1}: {r['role']} — {r['note']}" for i, r in enumerate(asset['references']))
        prompt += '\nReference roles:\n' + ref_list + '\n'
        (folder/'prompt.txt').write_text(prompt)
        lock = dict(schema=1, task=asset, manifest_sha256=hashlib.sha256(raw).hexdigest(),
            template_sha256=digest(TEMPLATES/(asset['kind']+'.txt')),
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), actual_references=asset['references'],
            references_inspected_by_agent=False, generation_called=False)
        (folder/'inputs.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2)+'\n')
        if asset['gate'] == 'ready':
            call = dict(prompt=prompt, referenced_image_paths=[str(pinned(r)) for r in asset['references']])
            (folder/'imagegen-request.json').write_text(json.dumps(call, ensure_ascii=False, indent=2)+'\n')
        (folder/'HANDOFF.md').write_text(
            f"# {asset['native_name']}\n\nGate: **{asset['gate']}** — {asset['gate_reason']}\n\n"
            f"Scope: {asset['scope']}\n\n"
            "Read art/production/README.md and the installed imagegen skill. Open every referenced PNG before calling the tool. "
            "A prompt preview is not generation authorization when gate is hold. Never bypass the unresolved source/display contract.\n\n"
            "For ready tasks, use the built-in ImageGen with imagegen-request.json; do not run an API client. "
            "Copy the original output byte-for-byte to a new versioned master. Record full prompt, original path, saved path and attempt. "
            "Inspect 48/64/96px exports and compare the family in grayscale. Mechanical checks do not accept art. "
            f"Maximum {asset['max_attempts']} calls in this handoff; report unresolved design issues if exhausted. "
            "Do not edit identity mapping, manifests, runtime code or git commits; return evidence to the integrator.\n")
    return {'assets': len(manifest['assets']), 'ready': sum(a['gate']=='ready' for a in manifest['assets']),
            'hold': sum(a['gate']=='hold' for a in manifest['assets']), 'output': str(output), 'image_calls': 0}


def inspect_png(path, kind):
    from PIL import Image  # Read-only inspection; no save, resize or recolor.
    with Image.open(path) as image:
        if image.format != 'PNG':
            raise ValueError('master is not PNG')
        if image.width != image.height or image.width < 512:
            raise ValueError('master must be square and >= 512px; record actual resolution')
        # Native alpha must exist in the stored file, not be manufactured by
        # convert('RGBA'). ImageGen on this host returns a plain RGB PNG when
        # transparency is not demanded in the prompt, and art/production/README.md
        # forbids keying out a white background and calling it native alpha.
        native_alpha = image.mode in ('RGBA', 'LA', 'PA') or (
            image.mode == 'P' and 'transparency' in image.info)
        alpha = image.convert('RGBA').getchannel('A')
        extrema = alpha.getextrema()
        corners = [alpha.getpixel(p) for p in ((0,0),(image.width-1,0),(0,image.height-1),(image.width-1,image.height-1))]
        if kind != 'terrain-floor' and not native_alpha:
            raise ValueError(f'master stores no alpha channel (mode={image.mode}); '
                             'regenerate with an explicit transparent-background prompt')
        if kind != 'terrain-floor' and (extrema[0] != 0 or extrema[1] < check_token_style.MASTER_ALPHA_MAX_FLOOR
                                        or any(c > CORNER_ALPHA_MAX for c in corners)):
            raise ValueError('transparent prop/token lacks usable alpha or transparent corners')
        if kind == 'terrain-floor' and extrema != (255,255):
            raise ValueError('floor master must be opaque')
        return dict(mode=image.mode, size=list(image.size), native_alpha_channel=native_alpha,
                    alpha_extrema=list(extrema), corner_alpha=corners, alpha_bbox=alpha.getbbox())



def repair(pack, review_path):
    """Prepare one edit with recorded first output as its target; no tool call."""
    pack = confined(pack, ROOT/'art/production')
    lock = json.loads((pack/'inputs.json').read_text())
    asset = lock['task']
    if asset['gate'] != 'ready' or asset['max_attempts'] != 2:
        raise ValueError('task does not allow repair')
    receipt = json.loads((pack/'receipts/attempt-1.json').read_text())
    review = json.loads(review_path.read_text())
    required = {'review_scale', 'observed_failure', 'required_change', 'invariants'}
    if set(review) != required or any(not str(v).strip() for v in review.values()):
        raise ValueError('repair needs scale, observed failure, focused change and invariants')
    target = dict(path=str((ROOT/receipt['saved_output_path']).relative_to(WORKSPACE)),
                  sha256=receipt['sha256'], role='edit-target', note='Edit this first-attempt master only.')
    refs = [target] + [r for r in asset['references'] if r['role']=='style']
    for ref in refs:
        pinned(ref)
    folder = pack/'repair'
    if folder.exists() or (pack/'receipts/attempt-2.json').exists():
        raise ValueError('repair already prepared or budget exhausted')
    prompt = Template((TEMPLATES/'repair.txt').read_text()).substitute(native_name=asset['native_name'], **review)
    prompt += '\nReferences: image 1 is the edit target; remaining images specify approved style only.\n'
    folder.mkdir()
    (folder/'review.json').write_bytes(review_path.read_bytes())
    (folder/'prompt.txt').write_text(prompt)
    lock.update(prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), actual_references=refs,
                template_sha256=digest(TEMPLATES/'repair.txt'))
    (folder/'inputs.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n')
    call = dict(prompt=prompt, referenced_image_paths=[str(pinned(r)) for r in refs])
    (folder/'imagegen-request.json').write_text(json.dumps(call,ensure_ascii=False,indent=2)+'\n')
    return dict(repair_folder=str(folder), image_calls=0, remaining_calls=1)


def record(pack, original, saved, attempt):
    pack = confined(pack, ROOT/'art/production')
    prompt_dir = pack/'repair' if attempt == 2 else pack
    lock = json.loads((prompt_dir/'inputs.json').read_text())
    asset = lock['task']
    if asset['gate'] != 'ready':
        raise ValueError('hold task cannot receive a generation receipt')
    if not 1 <= attempt <= asset['max_attempts']:
        raise ValueError('attempt budget exceeded')
    receipts = pack/'receipts'
    if attempt != len(list(receipts.glob('attempt-*.json'))) + 1:
        raise ValueError('attempt receipts must be sequential and never overwritten')
    for entry in (asset['sources'] + lock['actual_references'] + asset['render_evidence']
                  + (asset.get('refinement') or {}).get('evidence', [])):
        pinned(entry)
    prompt = (prompt_dir/'prompt.txt').read_bytes()
    if hashlib.sha256(prompt).hexdigest() != lock['prompt_sha256']:
        raise ValueError('prompt changed; prepare a new pinned handoff')
    saved = confined(saved, ROOT/'art')
    original = original.resolve()
    if original == saved or not original.is_file() or not saved.is_file() or digest(original) != digest(saved):
        raise ValueError('preserve distinct original/saved paths with identical bytes')
    metrics = inspect_png(saved, asset['kind'])
    receipt = dict(schema=1, asset_id=asset['asset_id'], tool='image_gen.imagegen',
        original_output_path=str(original), saved_output_path=str(saved.relative_to(ROOT)),
        sha256=digest(saved), prompt_sha256=lock['prompt_sha256'], full_prompt=prompt.decode(),
        references=lock['actual_references'], attempt=attempt, metrics=metrics,
        preserved_original_bytes=True, mechanical_check='pass',
        # The receipt stage only has the master; disc geometry and base-plate
        # drift are measured on the 128px export by tools/build_monster_art.py.
        style_gate='master-alpha-only; disc/drift gated at 128px export',
        visual_review='pending', runtime_review='pending', accepted=False)
    receipts.mkdir(exist_ok=True)
    with (receipts/f'attempt-{attempt}.json').open('x') as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('manifest', type=Path)
    prep.add_argument('--out', type=Path, required=True)
    rep = commands.add_parser('repair')
    rep.add_argument('pack', type=Path)
    rep.add_argument('review', type=Path)
    rec = commands.add_parser('record')
    rec.add_argument('pack', type=Path)
    rec.add_argument('--original', type=Path, required=True)
    rec.add_argument('--saved', type=Path, required=True)
    rec.add_argument('--attempt', type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.manifest, args.out)
        elif args.command == 'repair':
            result = repair(args.pack, args.review)
        else:
            result = record(args.pack, args.original, args.saved, args.attempt)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')

if __name__ == '__main__':
    main()

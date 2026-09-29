"""Record the reviewed DEFAULT/alternate pairs; does not execute Lua or launch ToME.

Line selections are deliberately curated from this checkout, not a Lua branch
parser. The identity table is a source inventory, not an encounter probability
or a claim that the listed actors pass runtime generation/display filters.
"""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import json
import re

from audit_repaint_sources import ROOT, WORKSPACE, OUT, EARLY, LOAD, relative, visible_lines

ZONES = {
    'trollmire': ('FLOODED', 'is_flooded', [21,22,23,24,25,26,27,28,30], [32,33,34,35,36,37,39,41], 'TROLL_PROX', 'TROLL_SHAX', 'P2'),
    'ruins-kor-pul': ('HIDEOUT', 'is_hideout', [21,22,23,24,25,27], [29,30,31,32,33,35], 'SHADE', 'THE_POSSESSED', 'P1'),
    'norgos-lair': ('INVADED', 'is_invaded', [23,24,25,26,27,29], [31,32,33,34,35,46], 'NORGOS', 'FROZEN_NORGOS', 'P3'),
    'heart-gloom': ('PURIFIED', 'is_purified', [52,53,54,55], [52,53,54,55], 'WITHERING_THING', 'DREAMING_ONE', 'P4'),
    'scintillating-caves': ('TWISTED', 'layout', [20,21,22,23,24,26], [20,21,22,23,24,26], 'SPELLBLAZE_CRYSTAL', 'SPELLBLAZE_CRYSTAL', 'P5'),
    'rhaloren-camp': ('OVERGROUND', 'layout', [20,21,22,23,24,26], [20,21,22,23,24,26], 'INQUISITOR', 'INQUISITOR', 'P6'),
    'old-forest': ('CRYSTALINE', 'is_crystaline', [21,22,23,24,25,26,27,29], [31,32,33,34,35,36,38], 'WRATHROOT', 'SHARDSKIN', 'P7'),
    'maze': ('COLLAPSED', 'is_collapsed', [21,22,23,24,25,26,27,28,29,31], [33,34,35,36,37,38,39,41], 'MINOTAUR_MAZE', 'HORNED_HORROR', 'P8'),
    'sandworm-lair': ('BIGWORM', 'layout', [21,22,23,24], [21,22,23,24], 'SANDWORM_QUEEN', 'SANDWORM_QUEEN', 'P10'),
    'daikara': ('VOLCANO', 'is_volcano', [20,21,23,24,30], [20,21,26,27,30], 'RANTHA_THE_WORM', 'VARSHA_THE_WRITHING', 'P9'),
}

NOTES = {
    'trollmire': ('森林／池塘；Prox；Bill支线共用', '水生导入过滤squid；补electric eel与Shax，复用giant eel和dragon turtle；BOGWATER／BOGTREE'),
    'ruins-kor-pul': ('骷髅系与The Shade；石质房间／门', '盗贼系替换直接导入的骷髅系；The Possessed及thief护卫；静态末层不同'),
    'norgos-lair': ('熊犬蛇植物与Norgos；雪林', '植物直接导入改为shivgoroth；三档最低等级10/12/15减9为1/3/6；Frozen Norgos；雪粒子增强'),
    'heart-gloom': ('gloomy/deformed/sick前缀＋随机阴郁技能；Withering Thing及技能召唤影子', 'dreaming/slumbering/dozing前缀＋随机梦境技能；Dreaming One；梦境地面与全屏效果'),
    'scintillating-caves': ('晶体洞穴；同一普通怪物表与Spellblaze Crystal', '同一普通表／首领，但新增亡灵密室、法师密会、晶体密会和snake-pit房间候选；须另核对房间怪群'),
    'rhaloren-camp': ('室内营地；精灵表与Inquisitor；房间列表包含rat-nest', '地表营地；普通表／首领共用；房间列表以collapsed-tower替换rat-nest，新增构装体／炮塔等条件敌人'),
    'old-forest': ('熊犬蛇虫植物蚂蚁；Wrathroot；暗草森林', '直接导入的犬蛇改为晶体；Shardskin；春叶森林材质和明暗变化，不能凭名字添加新阻挡'),
    'maze': ('盗贼／牛头人／软泥等；Minotaur of the Labyrinth；楼梯', '腐化和时空恐魔替换直接导入的鼠虫蚁／牛头人；Horned Horror；裂隙交互下层，不是普通楼梯'),
    'sandworm-lair': ('普通掘洞虫引路；Sandworm Queen与召唤沙虫', '首层巨大掘洞虫2×2显示及特殊路径；后续层仍有普通掘洞虫；女王和普通导入表共用'),
    'daikara': ('共享xorn／雪巨人，犬类／冰龙；Rantha', '共享xorn／雪巨人，火龙／faeros；Varsha；火山末层、岩浆地面；读取已移除on_stand的本区Grid'),
}

# Only new/changed families and their shared counterparts are expanded here.
# Other direct families remain in zone-variants.csv and the original backlog.
FAMILY_SCOPES = {
    'aquatic_critter': ('trollmire:FLOODED', 'P2', '鳗鱼姿态与龟壳剪影；电鳗不能只靠电光区分；高阶龟保留高图验证'),
    'thieve': ('ruins-kor-pul:HIDEOUT;maze:DEFAULT;maze:COLLAPSED', 'P1/P8', '姿态／武器布局区分，保留真实潜行；固定职业造型，不实施换装'),
    'shivgoroth': ('norgos-lair:INVADED', 'P3', '三档冰体的臂长／晶冠／躯干比例不同；不用敌我蓝环或护盾白环承担身份'),
    'crystal': ('scintillating-caves:DEFAULT;scintillating-caves:TWISTED;old-forest:CRYSTALINE', 'P5/P7', '主晶柱构型和宽面明度区分；高阶quad_hue及wisp召唤另层验收'),
    'horror-corrupted': ('maze:COLLAPSED', 'P8', '小型人形／巨臂／领队、翼形与长蛞蝓分组；暗体保留大面轮廓光'),
    'horror_temporal': ('maze:COLLAPSED', 'P8', '幼体／成体／队长与爬行／虚空轮廓分开；高阶先确认实际生成条件'),
    'fire-drake': ('daikara:VOLCANO', 'P9', '火幼龙／成年／古龙与冰系有姿态和翼角差异；不只换红色'),
    'faeros': ('daikara:VOLCANO', 'P9', '三档火元素的核心与外形不同；发光不侵占阵营和生命环'),
    'cold-drake': ('daikara:DEFAULT', 'P9', '与火龙成对设计；幼体不等于成年缩小'),
    'xorn': ('daikara:DEFAULT;daikara:VOLCANO', 'P9', '两版共用；多肢／甲壳与地面岩石区分；特殊合体事件另验收'),
}

# Exact zone.lua declarations for DEFAULT and alternate layouts respectively.
ROOM_LINES = {
    'trollmire': (194, 66), 'ruins-kor-pul': (45, 45),
    'norgos-lair': (None, None), 'heart-gloom': (None, None),
    'scintillating-caves': (None, 44), 'rhaloren-camp': (43, 129),
    'old-forest': (49, 49), 'maze': (None, None),
    'sandworm-lair': (None, None), 'daikara': (46, 46),
}
ROOM_FOCUS = {
    'honey_glade': 'honey tree及蜂群召唤、grizzly bear；低级地城房间有add_levels，不按基础区域上限排除',
    'forest-ruined-building1': 'mob/moblet分支：盗贼、骷髅、尸鬼及其护卫；复用身份不复用不同物种的画',
    'forest-ruined-building2': 'honey tree、venus flytrap、brown bear的gloomy/wet等房间改名；water imp；需独立可信来源记录',
    'forest-ruined-building3': '原生mobs随机池、密室残缺骷髅；实际生成前展开选择表，未知身份保留原生',
    'mage-hideout': '原生mobs随机池含多类施法者；等级<=20房间条件；不能把全池画成同一法师',
    'troll-hideout': 'forest troll群，复用现有棋子；等级变化和密集摆位',
    'thief-hideout': 'thieve家族的mobs与boss分支；潜行、随机装备不产生新的换装需求',
    'plantlife': 'poison ivy、treant；圆盘演员与TREE地形构件必须区别',
    'mold-path': 'molds／oozes过滤群；POISON_DEEP_WATER、矮障碍和复制行为',
    'loot-vault': '条件forest wight或空房；不把每次抽到空房当作怪物验证通过',
    'worms': 'carrion worm mass、worm that walks；怪物组合与繁殖验证',
    'bandit-fortress': '盗贼池、bandit lord和随机改名Guard；嵌套区域另记覆盖，保留createRandomBoss来源',
    'amon-sul-crypt': 'skeleton warrior／armoured skeleton warrior；mage／magus；archer／master archer；ghoul／ghast四分支',
    'skeleton-mage-cabal': 'skeleton mage、skeleton warrior、skeleton archer、thief、bloated horror随机选一；并非只有法师',
    'crystal-cabal': '晶体subtype过滤与add_levels=4；含高阶quad_hue的生成需核对',
    'snake-pit': 'rattlesnake、green worm mass、giant brown ant、snow cat、green mold、giant grey rat、giant spider、ritch flamespitter、sandworm随机池；并非只有蛇',
    'rat-nest': 'giant white／brown／grey rat与molds；等级<=6且rodent已加载才允许',
    'circle': '使用当前怪物表并add_levels=17/20的无名过滤；实际解析清单单列，不猜固定物种',
    'collapsed-tower': 'broken golem、poison ivy、venus flytrap、skeleton mage、black bear、程序构造elemental crystal炮塔；嵌套盗贼区域',
    'perilous-cliffs': 'snow giant thunderer、boulder thrower；高等级偏移与CLIFFSIDE地形',
    'snow-giant-camp': 'snow giant三类及chieftain、随机unique营地首领；仅符合roomCheck条件时生成',
}


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def declarations(path):
    """Extract literal top-level identity declarations as source references only."""
    source = '\n'.join(visible_lines(path))
    starts = list(re.finditer(r'(?m)^[ \t]*newEntity\s*{', source))
    found = []
    for i, start in enumerate(starts):
        stop = starts[i + 1].start() if i + 1 < len(starts) else len(source)
        block = source[start.start():stop]
        name = re.search(r'(?m)^[ \t]*(?:newEntity\s*{\s*)?name\s*=\s*"([^"]+)"', block)
        if not name:
            continue
        define = re.search(r'\bdefine_as\s*=\s*"([^"]+)"', block)
        level = re.search(r'\blevel_range\s*=\s*{\s*(\d+)', block)
        found.append(dict(native_name=name[1], define_as=define[1] if define else '',
                          source=relative(path), source_line=source[:start.start()+name.start()].count('\n')+1,
                          declared_min_level=int(level[1]) if level else '',
                          native_tall='yes' if 'display_h=2' in block or 'display_h = 2' in block else 'no',
                          shader='quad_hue' if '"quad_hue"' in block else 'unique_glow' if '"unique_glow"' in block else ''))
    return found


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = set()
    with (OUT / 'monster-backlog.csv').open() as f:
        baseline = {row['native_name']:row['batch'] for row in csv.DictReader(f)}
    catalog = ROOT / 'overload/mod/class/CheckerTokens.lua'
    sources.add(catalog)
    covered = set(re.findall(r'\{id="[^"]+", name="([^"]+)"', catalog.read_text()))
    assert len(covered) == 25 and len(baseline) == 40
    matrix, identities, rooms = [], {}, {}

    def add_identity(actor, layouts, phase, role, brief):
        name = actor['native_name']
        if name in identities:
            old = identities[name]
            old['zone_layouts'] = ';'.join(sorted(set(old['zone_layouts'].split(';') + layouts.split(';'))))
            return
        state = 'existing-25' if name in covered else 'already-planned-' + baseline[name] if name in baseline else 'new-proposed'
        rule = '原生解析后确定生成／显示资格；不按导入或最低等级推算遭遇概率'
        priority = 'paired-scene'
        if name in ('squid', 'ink squid'):
            priority, rule = 'excluded-local-import', 'Trollmire水生导入明确清除squid的rarity；不计本变体新增目标；all.lua高等级补充不在本断言内'
        elif name in ("The Fragmented Essence of Harkor'Zun", "Harkor'Zun"):
            priority, rule = 'conditional-event', '两版共享的低频／合体事件，独立于主线两种首领；实机确认触发与合体来源'
        elif name in ('ancient dragon turtle', 'dredge captain', 'temporal stalker', 'void horror', 'fire wyrm', 'ice wyrm', 'faeros', 'greater faeros', 'ultimate faeros'):
            priority = 'conditional-generation'
        if name in ('shivgoroth', 'greater shivgoroth', 'ultimate shivgoroth'):
            rule = f'Norgos INVADED回调：level_range[1]与start_level减9；声明下限{actor["declared_min_level"]}→{actor["declared_min_level"]-9}；普通高图接入前置'
        if name == 'wisp':
            priority, rule = 'summoned-actor', 'rarity=false；shimmering crystal通过rarity_summoned_crystal召唤，不能因非随机掉表漏掉'
        if name == 'shadow':
            priority, rule = 'summoned-actor', 'Withering Thing的Call Shadows动态NPC；记录技能来源和召唤者，保留消失／重生／死亡行为'
        identities[name] = dict(**actor, zone_layouts=layouts, paired_phase=phase, role=role,
                                baseline_state=state, priority=priority, generation_note=rule, design=brief)

    for zone in EARLY:
        alt, flag, normal_lines, alt_lines, boss, alt_boss, phase = ZONES[zone]
        base = WORKSPACE / 'game/modules/tome/data/zones' / zone
        zpath, npath = base/'zone.lua', base/'npcs.lua'
        sources.update((zpath, npath, base/'grids.lua'))
        text = zpath.read_text()
        assert re.search(r'alternateZone(?:Tier1)?\(short_name,\s*{"' + alt + r'"', text)
        npcs = visible_lines(npath)
        actors = {actor['define_as']:actor for actor in declarations(npath) if actor['define_as']}
        lists = []
        for numbers in (normal_lines, alt_lines):
            loads = []
            for number in numbers:
                match = LOAD.match(npcs[number - 1])
                assert match and match[1] == 'npcs', (zone, number)
                loads.append(match[2])
                sources.add(WORKSPACE / f'game/modules/tome/data/general/npcs/{match[2]}.lua')
            lists.append(loads)
        for index, (layout, numbers, guardian) in enumerate((('DEFAULT', normal_lines, boss), (alt, alt_lines, alt_boss))):
            a = actors[guardian]
            room_line = ROOM_LINES[zone][index]
            room_names = []
            if room_line:
                declaration = text.splitlines()[room_line-1]
                assert 'lesser_vaults_list' in declaration
                room_names = re.findall(r'"([^"]+)"', declaration)
                for name in room_names:
                    paths = list((WORKSPACE/'game/modules/tome/data/maps/vaults').rglob(name+'.lua'))
                    assert len(paths) == 1, (name, paths)
                    path = paths[0]
                    sources.add(path)
                    record = rooms.setdefault(name, dict(room=name, zone_layouts=set(), source=relative(path),
                                                        requirements=ROOM_FOCUS[name],
                                                        status='conditional-room-resolve-before-art'))
                    record['zone_layouts'].add(f'{zone}:{layout}')
            matrix.append(dict(zone=zone, layout=layout, state_flag=flag, paired_phase=phase,
                               direct_families=';'.join(lists[index]),
                               npc_import_refs=';'.join(f'{relative(npath)}:{n}' for n in numbers),
                               room_templates=';'.join(room_names),
                               room_source_ref=f'{relative(zpath)}:{room_line}' if room_line else '',
                               families_added_vs_other=';'.join(sorted(set(lists[index])-set(lists[1-index]))),
                               guardian_id=guardian, guardian_name=a['native_name'],
                               guardian_definition=f'{a["source"]}:{a["source_line"]}',
                               layout_source=f'{relative(zpath)}:20', requirements=NOTES[zone][index],
                               validation_status='planned-not-runtime-verified'))
            add_identity(a, f'{zone}:{layout}', phase, 'main-guardian', '独特身份单独画；与另一变体首领至少两项形状差异；沿用运行时等级角标')
        if zone == 'trollmire':
            add_identity(actors['TROLL_BILL'], 'trollmire:DEFAULT;trollmire:FLOODED', phase, 'shared-optional-guardian', '复用现有Bill，宝藏支线单独验收')
        if zone == 'sandworm-lair':
            add_identity(actors['SANDWORM_TUNNELER'], 'sandworm-lair:DEFAULT;sandworm-lair:BIGWORM', phase, 'navigation-actor', '复用原M5计划；普通引路掘洞虫与坍塌时序')
            add_identity(actors['SANDWORM_TUNNELER_HUGE'], 'sandworm-lair:BIGWORM', phase, 'navigation-actor', '复用原M5计划；首层巨大掘洞虫2×2显示不等于四格碰撞')
    for family, (layouts, phase, brief) in FAMILY_SCOPES.items():
        path = WORKSPACE / f'game/modules/tome/data/general/npcs/{family}.lua'
        sources.add(path)
        for actor in declarations(path):
            add_identity(actor, layouts, phase, 'family-member', brief)

    shadow_path = WORKSPACE/'game/modules/tome/data/talents/cursed/shadows.lua'
    sources.add(shadow_path)
    shadow_line = next(i for i,l in enumerate(shadow_path.read_text().splitlines(),1) if 'name = "shadow"' in l)
    add_identity(dict(native_name='shadow', define_as='', source=relative(shadow_path), source_line=shadow_line,
                      declared_min_level='dynamic', native_tall='no', shader=''),
                 'heart-gloom:DEFAULT', 'P4', 'skill-summon', '虚影保留通透及外形，不画成被动阴影；消失、重生与受击需要实机验证')

    for stem in ('ruins-kor-pul-last', 'ruins-kor-pul-invaded-last', 'rhaloren-camp-last', 'trollmire-treasure'):
        sources.add(WORKSPACE / f'game/modules/tome/data/maps/zones/{stem}.lua')
    for stem in ('underground', 'underground_gloomy', 'underground_dreamy', 'mountain', 'lava', 'sand'):
        sources.add(WORKSPACE / f'game/modules/tome/data/general/grids/{stem}.lua')
    sources.add(WORKSPACE / 'game/modules/tome/class/GameState.lua')
    rows = sorted(identities.values(), key=lambda row: (int(row['paired_phase'].split('/')[0][1:]), row['role'], row['native_name']))
    assert len(matrix) == 20 and len({(r['zone'], r['layout']) for r in matrix}) == 20
    for row in rows:
        line = (WORKSPACE / row['source']).read_text().splitlines()[row['source_line']-1]
        assert f'"{row["native_name"]}"' in line, row
    write_csv('zone-variants.csv', matrix)
    write_csv('variant-monster-backlog.csv', rows)
    room_rows = [dict(r, zone_layouts=';'.join(sorted(r['zone_layouts']))) for _,r in sorted(rooms.items())]
    write_csv('variant-room-backlog.csv', room_rows)
    summary = dict(scope='Curated ten base-game T1/T2 layout pairs, selected changed/shared families, main guardians and known summons; static declarations, not resolved spawn lists. Explicit lesser-vault lists are tracked separately; all.lua, nested zones and event/room selectors are not exhaustively expanded into identities.',
                   layout_rows=len(matrix), identity_rows=len(rows),
                   room_templates=len(room_rows),
                   baseline_states=dict(Counter(r['baseline_state'] for r in rows)),
                   priority_counts=dict(Counter(r['priority'] for r in rows)),
                   new_targets_excluding_filtered_and_events=sum(r['baseline_state']=='new-proposed' and r['priority'] not in ('excluded-local-import','conditional-event') for r in rows),
                   new_target_priorities=dict(Counter(r['priority'] for r in rows if r['baseline_state']=='new-proposed' and r['priority'] not in ('excluded-local-import','conditional-event'))),
                   source_sha256={relative(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})
    (OUT/'variant-source-audit.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

# P1 Kor'Pul 双布局原生身份审计底稿

范围：本地 ToME 1.7.6 源码与 checker-revised 0.5.2。此页及 [inventory.csv](inventory.csv) 是**声明与接入风险**，不是实机生成率、最终 `image` 或完整候选解析。实机结果由 `tests/live_korpul_inventory.lua` 在独立离线夹具按布局另存；未触发房间、护卫或首领一律为未验证。

## 布局与来源

`data/zones/ruins-kor-pul/zone.lua:20-21` 用 `alternateZone(short_name, {"HIDEOUT", 2})` 选布局，`is_hideout` 见 :39。两版均为 3 层；普通层使用 Roomer，直接 NPC 生成器为 OnSpots、20–30 个和 `max_ood=2`（:25-29、:40-58）。末层 :76-80 分别加载 `data/maps/zones/ruins-kor-pul-last.lua:24`（`SHADE`）与 `ruins-kor-pul-invaded-last.lua:24-29`（`THE_POSSESSED`，位置二选一）。

| 布局 | 直接导入；源码 `data/zones/ruins-kor-pul/npcs.lua` | 固定首领 |
| --- | --- | --- |
| DEFAULT | rodent :21、vermin :22、molds :23、skeleton :24、snake :25、all :27 | `SHADE` :41-91；`The Shade`；固定地图 `ruins-kor-pul-last.lua:24` |
| HIDEOUT | rodent :29、vermin :30、molds :31、thieve :32、snake :33、all :35 | `THE_POSSESSED` :93-136；`The Possessed`；固定地图 `ruins-kor-pul-invaded-last.lua:24-29` |

直接表替换不能解释成对侧家族不存在。`data/general/npcs/all.lua:54,69,78,97` 还会以 `rarity(4, 35)` 方式加载 molds、skeleton、thieve 中未加载的文件；导入、等级和稀有度过滤并不等于遭遇。需用当前 `zone.npc_list` 和实际生成样本复核。

## 首组四身份的声明与显示风险

三类骨架均继承 `data/general/npcs/skeleton.lua:22-56` 的 `BASE_NPC_SKELETON`：`undead/skeleton`、`display="s"`、`rank=2`、装备栏含主副手、躯干和箭袋；基础免疫、材质与状态由原生演员保留。degenerated skeleton warrior（:58-66）显式 `image="npc/degenerated_skeleton_warrior.png"`，等级 1–18、稀有度 1，描述只有一臂，装备 resolver 为 greatsword；不能凭名称添加盾。degenerated skeleton archer（:68-80）等级 3–20、稀有度 3，声明无显式 `image`；缺手腕仍用 longbow 与 arrow，最终图路径需原生解析。skeleton mage（:82-100）显式 `npc/skeleton_mage.png`，等级 5–25、稀有度 3，staff 装备及火焰/魔法箭技能；技能视觉效果不能烘入静态棋子。

grey mold 继承 `data/general/npcs/molds.lua:22-44` 的 `BASE_NPC_MOLD`：`immovable/molds`、`display="m"`、`rank=1`、`never_move=1`、无装备栏位；它是可攻击的 Actor。个体 :46-57 等级 1–15、稀有度 1、无显式 `image`，最终图路径需原生解析。霉菌状态环和地板装饰应分别验收。

四盗贼来自 `data/general/npcs/thieve.lua:22-60` 的 `BASE_NPC_THIEF`，继承 `humanoid/human`、`display="p"`、`rank=2`、双 dagger＋light armor resolver、出生维持技能 resolver；个体均无显式 `image`。cutpurse :62（1+）、rogue :72（2+）、thief :82（3+）、bandit :98（5+）的稀有度依次为 1/1/1/2；bandit 有 `THIEF_BANDIT`。rogue、thief、bandit 的潜行和其他状态可能触发保护性显示回退，需记录实际层叠和棋子原因。

`The Shade` 声明为 `undead/skeleton`、`rank=4`，`data/zones/ruins-kor-pul/npcs.lua:41-66` 有 `shader="unique_glow"`、staff/轻甲装备而无显式 `image`；当前 `overload/mod/class/CheckerTokens.lua:83` 对 shader 回退。`The Possessed` 从 `BASE_NPC_THIEF` 继承身份，:93-109 的 `nice_tile` 是 `image="invis.png"` 加一层 `npc/humanoid_human_the_possessed.png`，`display_h=2`、`display_y=-1`，并装备 dagger/轻甲。当前棋子表无这两个首领，因此即便 nice_tile 结构未来可支持，也不能把现在的回退称为缺陷。:114-116 另生一名 `thief` 护卫；须在实际生成后单独验身份、等级、阵营与复制/显示。`KOR_FURY`（:137 起）为后期 backup guardian，不是 HIDEOUT 第二首领。

## 条件房间

两版共用 `zone.lua:44-45` 的 `lesser_vault` 房间池：`circle`、`amon-sul-crypt`、`rat-nest`、`skeleton-mage-cabal`、`crystal-cabal`、`snake-pit`。每次未必生成房间，生成房间亦未必抽中其中某身份。

| 房间 | 条件与候选源码 | 必须单独核对 |
| --- | --- | --- |
| circle | `data/maps/vaults/auto/lesser/circle.lua:27-29` | 无名 actor 过滤 `add_levels=20/17`；不能按房名猜物种。 |
| amon-sul-crypt | `data/maps/vaults/amon-sul-crypt.lua:22-24,38-42,56-59,73-76,90-93` | 四支：warrior/armoured warrior、mage/magus、ghoul/ghast、archer/master archer；有等级偏移。 |
| rat-nest | `data/maps/vaults/auto/lesser/rat-nest.lua:21-35` | 当前等级 ≤6 且 rodent 已导入；鼠与 `molds` 过滤，后者 `add_levels=4`。 |
| skeleton-mage-cabal | `data/maps/vaults/auto/lesser/skeleton-mage-cabal.lua:21-27,32-39,64` | 当前等级 5–25；五选一包含 skeleton mage/warrior/archer、thief、bloated horror；`add_levels=8`。 |
| crystal-cabal | `data/maps/vaults/auto/lesser/crystal-cabal.lua:21-34` | 当前等级 5–25；晶体 subtype 过滤且 `add_levels=4`。 |
| snake-pit | `data/maps/vaults/snake-pit.lua:24-55` | 九名随机池含 green mold、sandworm、ritch flamespitter 等；不是固定蛇。 |

原生解析需要保存 `name/type/subtype/define_as/image/add_mos/add_displays/shader/anim/textures/shader_auras/replace_display/rank` 与棋子命中或回退原因。无显式 `image` 的身份不能用源码命名规则补出“最终路径”。审计脚本对现有活动区 NPC 原型做**脱离地图的 `finishEntity`**，可能消耗 RNG/UID，但不摆放演员、不推进世界回合；它标记的是本布局活动候选的解析，房间是否实际生成仍靠未摆位种子与现场记录。

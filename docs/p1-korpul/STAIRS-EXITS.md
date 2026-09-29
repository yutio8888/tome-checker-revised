# 楼梯、地表通路与世界出口审计

续接状态：下文是0.6.1时的历史审计。0.6.2已完成Kor’Pul三种出口，见[接入与两变体验证](../../evidence/runtime-v062/README.md)；森林平面通路与世界标记仍待处理。

2026-09-27；核对本地 ToME 1.7.6 源码与 checker-revised 0.6.0→0.6.1。**Kor'Pul 的上楼、下楼和世界出口目前都保留原生图；Trollmire DEFAULT 的草地出口已被旧选择器合并为同款 `exit` 图，丢失方向和目的地的视觉区别。** 本轮只分析，不增加楼梯资产、不修改地形接入或任何换层规则。

## 实际定义与当前显示

下表的文件路径相对原生 `game/modules/tome/`。`change_level` 的正负是区域内层号变化；屏幕上箭头的东/西方向是另一个维度。所有这些普通出口都有 `notice=true`、`always_remember=true`；原生图是地面 `image` 加标志 `add_mos`，不能仅比较地面 PNG。

| 区域／出现位置 | 原生定义及来源 | 原生图层、方向 | 实际换层规则 | 当前插件结果 |
| --- | --- | --- | --- | --- |
| Trollmire DEFAULT，第1层入口 | `GRASS_UP_WILDERNESS`，`data/general/grids/forest.lua:151`；`data/zones/trollmire/zone.lua:219` | `grass.png` + `worldmap.png`；世界地图标记，非上楼梯 | `change_zone="wilderness"`、`change_level=1`，目的地为世界地图第1层 | blockout/refined 均归到同一个 `exit{parity}`；世界地图标记被整格替代 |
| Trollmire DEFAULT，第2/3层回程、第4层返回 | `GRASS_UP4`，`forest.lua:183`；zone默认up、`data/maps/zones/trollmire-treasure.lua:23` | `grass.png` + `way_next_4.png`；朝西/左的平面通路 | 无change_zone，层号 −1 | 同一套 exit；回程朝向无法从图分辨 |
| Trollmire DEFAULT，第1/2层前进 | `GRASS_DOWN6`，`forest.lua:234`；zone默认down | `grass.png` + `way_next_6.png`；朝东/右的平面通路 | 无change_zone，层号 +1 | 同一套 exit；不是独立下楼梯图 |
| Trollmire，第3层尚未开启宝藏 | `zone.lua` 第3层覆写 `down="GRASS"`，保留 `default_down` 点 | 普通草地，不是隐藏楼梯的公开标志 | 没有出口行为 | DEFAULT仍按普通草地；不能提前画出通路 |
| Trollmire，任务开启第3→4层 | `data/quests/trollmire-treasure.lua:45` 克隆 `GRASS_DOWN6`、改名为隐藏宝藏通路 | 原生仍朝东；增加 `desc="Beware!"`，不是另一种楼梯方向 | 自带 `change_level_check` 警告确认，再调用 `game:changeLevel(4)` | DEFAULT旧草地选择器仍把它画作普通exit，没有表达特殊危险；原生确认回调仍在 |
| Trollmire FLOODED，以上对应出口 | 同一区域脚本 FLOODED 分支使用相同 grass up/down/world出口，含第3层和第4层安排 | 地图主体为沼泽，但出口定义仍是草地底与通路图层 | 对应规则相同 | `zone.is_flooded` 排除整个森林替换；所有地形/出口原生 |
| Kor'Pul DEFAULT / HIDEOUT，第1层入口 | `UP_WILDERNESS`，`data/general/grids/basic.lua:24`；`data/zones/ruins-kor-pul/zone.lua:73` | `marble_floor.png` + `stair_up_wild.png`；上行至地表的世界出口 | `change_zone="wilderness"`、`change_level=1`；不是再下到本区域第2层 | 原生完整图层；无Kor'Pul替换，无森林替换 |
| Kor'Pul DEFAULT / HIDEOUT，第2/3层回程 | `UP`，`basic.lua:36`；zone默认up；两份末层静态图的Roomer子生成器up | `marble_floor.png` + `stair_up.png`；真正上楼梯 | 无change_zone，层号 −1 | 原生完整图层 |
| Kor'Pul DEFAULT / HIDEOUT，第1/2层前进 | `DOWN`，`basic.lua:47`；zone默认down | `marble_floor.png` + `stair_down.png`；真正下楼梯 | 无change_zone，层号 +1 | 原生完整图层 |
| Kor'Pul DEFAULT / HIDEOUT，第3层末端 | `data/maps/zones/ruins-kor-pul-last.lua` / `ruins-kor-pul-invaded-last.lua` | 子生成器只指定 `UP`，没有常规第4层出口；门洞和boss房入口仍是门/地面 | zone.max_level=3；不能因房间入口造出换层标志 | 门按已验证门合同处理；不能把门当楼梯 |
| 已加载但非这些主线生成器选用的出口 | `FLAT_UP/DOWN{8,2,4,6}`、`FLAT_UP_WILDERNESS`（basic.lua）；`GRASS_UP/DOWN{8,2,4,6}`其他方向（forest.lua） | flat为石地上的平面方向标，grass为草地上的方向标；数字8/2/4/6对应北/南/西/东；flat world为 `worldmap.png` | UP −1、DOWN +1；WORLD另含change_zone | 不因文件已导入就声称会自然出现；Kor'Pul均不在白名单。Trollmire旧选择器对任何符合草地出口条件者过宽 |

`WORLD_EXIT` 不是这两个区域上述源码里的 `define_as`，是审阅中的语义称呼；这里必须落实到 `UP_WILDERNESS` 或 `GRASS_UP_WILDERNESS`，不能拿统一名称掩盖其不同原生形状。条件vault/事件若另加有回调、特殊目的地、外部显示的出口，应单独采集来源，默认保留原生；本表不宣称穷尽所有全局事件。

原生 `class/Game.lua:2276` 的 `CHANGE_LEVEL` 先检查可行动能量、禁移动状态、出世界地图的负面状态限制，再调用 `change_level_check`。有 `change_zone` 或 `change_level_abs` 时，`change_level` 是目标层；否则使用当前层号加上该值。换图时还传递 keep_old_lev / force_down / 自动楼梯 / 临时区域返回参数。本插件的 Game superload仅管理显示和设置，没有重写此逻辑。

## 现有证据能说明哪一格

[0.6.0 HIDEOUT第1层原生字段实机记录](../../evidence/runtime-v061/stairs-prechange-hideout-060.tsv)是在本轮替换前，对当时运行地图直接只读枚举所得：

| 当时地图坐标（0起始） | 实际对象 | 原生显示与结果 |
| --- | --- | --- |
| `(28,40)` | `DOWN` / next level | `marble_floor.png` + `stair_down.png`；+1、无change_zone；Kor'Pul分类返回nil，forest_override=none |
| `(36,26)` | `UP_WILDERNESS` / exit to the worldmap | `marble_floor.png` + `stair_up_wild.png`；目标wilderness第1层；同样原生 |

因此当这两格被实机画面展示时，台阶图标是原生楼梯/世界出口，并非漏导出一款已绘制的棋盘地形。坐标只适用于这次地图实例，不能套在另一次生成或旧摆位截图上。

已检查旧 [HIDEOUT 64px refined截图](../../evidence/runtime-v060/screenshots/korpul-hideout-refined-64.png)：人物左下方蓝色长杖及更下方的卷曲腰带样图，是地面物品展示，不能凭它们与棋盘地面的风格差异判断为楼梯。旧图中的物品外形不构成出口规则证据；精确出口身份应读该次地图的 `define_as/change_*`，不要根据战斗日志里历史“worldmap here”消息推断当前英雄所在格仍是出口。

## 为什么Kor'Pul尚未替换、森林已经替换

`CheckerTerrain.classify` 的P1白名单只收录 basic.lua 的普通 FLOOR、WALL/HARDWALL及门；显式拒绝 `change_level`、`change_zone`、不受支持的add_mos和特殊回调。楼梯本身就带 `change_level` 与 `add_mos`，也没有白名单来源印章，所以原生显示保留。Kor'Pul记忆合同仍适用：未观察格不透露内容；记忆格沿用已知地形，不借出口新图泄露未知区域。

旧森林 `terrain(g)` 则先对 `subtype=='grass'` 且有 `change_level or change_zone` 返回 `exit`，未区分层方向、世界目的地或特殊回调。`terrainImage`只加坐标奇偶，因此 DEFAULT 所有出口使用 `checker-revised+exit0/1.png` 或 `checker-revised+refined/exit0/1.png`。它以自己的 `replace_display`替代整个地形显示，保留Grid规则字段；外部replace_display仍优先。该视觉归并是已存在的问题，本轮没有扩大它。

## 建议的最小下一步

建议重绘，但先做三种明确的石质图：**上楼梯、下楼梯、世界出口**。同一石地底板、同一灯光和留白，上楼以抬起的阶面/向上收束轮廓，下楼以暗井口和下沉阶面，世界出口以通向明亮地表的门洞加小型地图符号区分；不要只靠颜色，也不要复用棋子的红色敌对环。48px应能辨别三种语义，64/96px再看台阶材质。

森林另用东西向平面通路及世界标记，不能把“前进层号+1”画成固定向上箭头。隐藏宝藏入口在原生任务揭示前仍是草地；揭示后若设计特殊通路图，必须单独验收带警告回调的身份，并保留原生确认行为。

接入建议只扩展现有P1观察/记忆合同，逐个登记准确的 `UP`、`DOWN`、`UP_WILDERNESS` 来源、规则与图层签名，保留其地面和目的地差异；不要放开全部 `change_level` 或全部 `add_mos`。没有审阅过的来源、动态目的地、特殊回调、外部显示、shader及其他区域继续原生。森林方向修正另做明确白名单，避免把当前宽泛exit选择器复制到地城。

接入验收至少包含两版Kor'Pul第1层世界出口、第2层UP/DOWN、第3层只有回程；Trollmire左右向通路、未揭示与已揭示宝藏、FLOODED回退；并验证可见→记忆→未知、设置切换、原生换层目标与确认回调。没有这些资产和实机证据前，当前保留原生比宣称“楼梯已统一重绘”准确。

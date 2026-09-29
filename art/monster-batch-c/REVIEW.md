# Monster batch C — 离线美术复核

批次清单 `art/production/batches/monster-batch-c-1.json`，任务包 `art/production/handoffs/monster-batch-c-1/`。ImageGen 前台单图共 4/8 次（经 `tools/run_imagegen.py`，产物溯源到 `~/.codex/generated_images/`）；没有启动游戏，没有使用夹具。skeleton archer 与 Horned Horror 为已接入身份的重绘，任务包内写有 `refinement` 声明（钉住 batch B 回执与实机审图记录）。

| 身份 | 调用 | 选中母版 | 128px 静态门控 | 结论 |
| --- | ---: | --- | --- | --- |
| skeleton master archer | 2 | `masters/skeleton-master-archer-v2.png` | 通过：底盘 +3.54，半径 0.860，侵入 +2.81 | 新接入 |
| skeleton archer | 1 | `masters/skeleton-archer-v1.png` | 通过：底盘 −1.67，半径 0.860，侵入 +4.97 | 取代 batch B |
| Horned Horror | 1 | `masters/horned-horror-v1.png` | 通过：底盘 −2.21，半径 0.859，侵入 +6.36 | 取代 batch B |

master archer v1（底盘 −0.07，门控通过）的黑甲在 48px 灰度下与暗底盘粘连；v2 为人工看图返修（`manual-review.json`），加亮黑甲左上受光面、加粗金边，身份与姿态不变，选 v2。三款均无门控失败，**无豁免申请**。

## 视觉评审

并排图：[弓手家族彩图](review/archers-color-48-64-96.png)／[灰度](review/archers-grayscale-48-64-96.png)；[Horned Horror 与迷宫 Minotaur 彩图](review/horror-color-48-64-96.png)／[灰度](review/horror-grayscale-48-64-96.png)。由 `make_review_sheets.py` 用实际 48/64/96 导出拼合（Minotaur 只存了 128px，脚本用同一 `export_token` 对其母版现导）。

- **原生对照与取舍**：原生 skeleton archer 直立、双腿宽 A 字、金色弓；degenerated archer 佝偻、骨色发霉。既有 degenerated 棋子的蹲伏侧身姿态与其原生一致，而 batch B 的 skeleton archer 以 degenerated 母版为风格参考、照搬了蹲伏姿态，与原生不符。故保留 degenerated，重绘 skeleton archer。
- **skeleton archer**：正面直立、脊柱竖直、双臂一线拉满金弓、双腿宽 A 字；48px 呈“X/十字”细骨架，与 degenerated 的团状蹲伏剪影明显不同；洁白骨色＋金弓为辅助线索。
- **skeleton master archer**：黑色漆甲、宽金边、带冠头盔、宽肩甲、外张甲裙；48px 为宽厚暗色人形，与白骨弓手在明度（暗 vs 亮）和轮廓（厚甲 vs 细骨）两维区分。与新 skeleton archer 同为正面拉弓姿态（两者原生本即同姿），区分不靠色相。残余：灰度 48px 下主体仍属偏暗，靠金边、骷髅脸与轮廓辨认；需实机 64px 复看。
- **Horned Horror**：浅灰紫躯体、象牙角、背后五六条洋红触手呈新月冠、无武器、双拳钢甲缠青白闪电（原生 Storm Bringer Gauntlets）；亮度明显高于 batch B，暗底盘上可读。48px 剪影为“顶部触手冠＋两侧亮拳”，不同于 Minotaur 的直立持斧牛人；色调冷紫对暖棕为辅助。触手冠顶部接近右上等级标记区，实机需确认王冠标记不遮挡主要识别特征。
- 未绘等级、阵营、血量、护盾或光环；闪电紧贴拳部，未照亮底盘。

## 接入

`CheckerTokens.lua` 新增精确条目 `skeleton-master-archer`（name/image/type/subtype 同原生 `general/npcs/skeleton.lua:176`）；`tests/token_mapping.lua` 增加三种弓骷髅互不借图的断言。`prepare_runtime_art.py` 批次顺序末尾加入 `monster-batch-c`，同 id 取代 batch B 的 skeleton-archer 与 horned-horror。batch B 的 `horned-horror` 豁免条目按字节绑定旧图，现已不被任何运行贴图命中。

## 未完成

- 未实机：需在隔离夹具复看 Dreadfell／Unremarkable Cave 的 master archer 自然生成、家族排 48/64/96、Maze COLLAPSED L4 的 Horned Horror（含 boss 王冠标记位置）。
- `tests/live_v9_scene.lua` 与 `tools/run_monster_live_validation.py` 仍把 skeleton master archer 当“保持原生”的对照，实机前需改指向另一未覆盖身份。

# Monster batch G 评审（2026-09-29，离线，未实机、未提交、未打包）

ImageGen 总调用 **22 / 26**（按 `call-*` 目录计，含被中断而无 `call.json` 的 Massok 首次调用）。每款不超过 3 次。所有母版为 ImageGen 原生 RGBA，逐字节保存于 `masters/`；没有 Python 补画。

## 逐项结果

| 款 | 合同 | 调用 | 选用母版 | 门控 | 结论 |
| --- | --- | --- | --- | --- | --- |
| xhaiak arachnomancer | native_tall（`evidence/monster-live-f-20260929/` 探针） | 1 | v1 | 偏移 -6.07 / 半径 0.860 | 上线 |
| shiaak venomblade | native_tall（同上） | 2 | v2 | 偏移 +0.01 / 0.860 | 上线；v1（-7.29）体色近黑橄榄，48px 成黑团，自行淘汰 |
| dremling | native_tall，贴图 `horror_corrupted_drem.png`（与 drem 文件名对调，负例测试保留） | 3（g-2、g-2b、g-2c） | v2 | +3.37 / 0.860 | 上线；前两次仅底盘偏移 -11.04／-8.19 |
| Massok the Dragonslayer | native_tall 唯一 | 3（首次被中断、次次骨剑越盘 1.204、第三次偏移 -10.32） | v1 | 仅 base_drift -10.32 | **PENDING**，不接线 |
| Pale Drake | native_tall 唯一 | 1 | v1 | -4.86 / 0.858 | 上线 |
| The Master | 单图唯一 | 2 | v2 | -2.58 / 0.859 | 上线；v1（-7.81）袍近黑，灰度下成黑柱，淘汰 |
| Spellblaze Crystal | 单图唯一 | 2 | v2 | +0.68 / 0.859 | 上线；v1 仅偏移 -10.45，用「不压暗底盘」措辞重新生成 |
| Rhaloren Inquisitor | 单图唯一（公式图名） | 2 | v2 | -6.01 / 0.860 | 上线；v1 大剑越盘 1.077，经一次定向返修收回 |
| Krogar | native_tall 唯一 | 2 | v1（重生包 3c） | -2.87 / 0.860 | 上线；首次长杖越盘 0.984 且 -9.44 |
| Fillarel Aldaren | native_tall 唯一 | 1 | v1 | -7.17 / 0.859 | 上线 |
| Harno, Herald of Last Hope | 单图唯一 | 1 | v1 | -7.63 / 0.859 | 上线 |
| Lithfengel | 单图唯一 | 2 | v2 | -5.28 / 0.858 | 上线；v1 仅偏移 -9.12 |

「不压暗底盘」措辞：此前 4 单位压暗指令在本机常落在 -5 到 -11；重生提示改为「底盘与参考同亮度、宁可略亮、绝不更暗」后，水晶 +0.68、dremling +3.37、Krogar -2.87、Lithfengel -5.28、shiaak +0.01。没有做亮度修补（不走 brighten-repair）。

## dremling 亮度（不是只看门控）

按 Kryl-Feijan 同口径（128px 导出，alpha>=180 且 d<=0.55 的像素平均亮度，见 `review/luminance.json`）：批 F 被拒黑曜石旧稿 **39.84**，新稿 **90.55**（+127%）。真实地板 48px（`review/floor-readability-48-x2.png`）中旧稿是黑团，新稿是明显的浅灰石像。

## 同族与可读性（自评）

- 蜘蛛族（`review/spiderkin-*`）：Ungolë 圆身黑蜘蛛；xhaiak 细长多肢、浅色布带；shiaak 矮壮鼠尾草绿、双弯刀。轮廓可分，不靠颜色单维。xhaiak 仍偏暗（亮度 51.6），靠浅布和细肢轮廓保持可读，列为较弱项。
- 亡灵（`review/undead-*`）：Pale Drake 为兜帽骷髅法师、紫黑袍配金饰与骷髅杖；The Master 为直立猩红/象牙长袍、高领、红宝珠杖（杖在画面左）；与既有 7 款骷髅轮廓不同。二者同为「长袍持杖」，灰度下仍有相似处，主要靠色相与领／兜帽轮廓区分，列为需实机复核项。
- 兽人（`review/orc-*`）：golbug 金饰锤盾、brotoq 双斧黑甲、Krogar 绿皮链甲持短杖、Massok（未上线）骨盔与单剑。
- Harno 灰蓝斗篷偏暗（亮度 45.7），48px 仍可见兜帽轮廓与褐色皮饰，为最弱的一款，列为已知限制。
- 所有 48/64/96 彩色与灰度家族图、真实地板 48px 合成图见 `review/`；脚本 `make_review_sheets.py` 可重现。

## Massok 待评审

见 `art/production/waivers/monster-batch-g-PENDING-REQUEST.json`。仅 base_drift -10.32（超 2.32），其余全过；已达单款 3 次上限，未再调用。未批准前保持原生，`tests/token_mapping.lua` 与 `test_monster_batch_g.py` 锁定其未接线。

## Reviewer decision (2026-09-29)

- Accepted all 11 shipped tokens. Dremling v2 (masked body luminance 90.6 vs 39.8) and shiaak venomblade v2 fix the dark-on-dark failures.
- Massok base-drift waiver (-10.32): **approved** (strong art, only base drift misses); wiring pending.
- Needs in-game confirmation: Harno and xhaiak arachnomancer (dark subjects) at 48px; Pale Drake vs The Master (both robed staff figures, separated by hue and head shape) in Dreadfell.

## 2026-10-04 dremling 平面 token 重绘（v3，用户决定）

- 用户决定：dremling 的 `desc`（`game/modules/tome/data/general/npcs/horror-corrupted.lua:83`，"A giant black-skinned humanoid covered in spikey scabrous deposits ... featureless ... eyesockets, empty and hollow"）与已选用的黑色立绘一致；现行平面 token v2 是 pale-stone 且持斧，与 desc 矛盾。保留立绘，只重绘平面 token。
- 重绘包 `art/production/handoffs/dremling-token-repaint-v1/`（`dremling-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`，**1** 次调用，attempt 1 即过门控；manifest `art/production/batches/dremling-token-repaint-v1.json` 带 refinement 声明，supersedes `monster-batch-g-2c`）。
- 新母版 `art/monster-batch-g/masters/dremling-v3.png`（sha256 `7bf8e12d…`）；门控 base_drift **-3.64**、最大不透明半径 0.8585、占格 0.8594、无警告。旧母版与旧运行 token 归档于 `art/monster-batch-g/superseded/dremling-v2.png` 与 `.../dremling-v2-runtime-128.png`。
- 外观：黑皮 + 浅骨色 scabrous 尖刺沉积、无五官面具脸与空洞眼窝、空爪无武器；与已接受立绘 `art/token-layers/dremling/standee/master-v1.png` 一致。
- 三尺寸（48/64/96 真实尺寸、mid-brown 地板）对照图见 `art/token-layers/review-batch1/dremling-token.png`（native／v2／v3／立绘）。
- 本目录 `review/` 下 2026-09-29 的家族图与 `luminance.json` 是 v2 的历史记录，未重跑；v3 的对照以 `dremling-token.png` 为准。

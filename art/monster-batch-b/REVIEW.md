# Monster batch B — 离线美术复核

原生源码合同见 `evidence/monster-batch-b-20260929/source-contracts.json` 及 `source-contracts-detail.json`。ImageGen 前台单图 10/24 次，六款候选入源码；没有启动游戏。首次及二次全候选彩图／灰度图在 `review/first-pass-*` 与 `review/second-pass-*`；最终与既有家族锚点并排见 [彩图](review/selected-color-48-64-96.png) 和 [灰度图](review/selected-grayscale-48-64-96.png)。

| 身份 | 调用 | 选中母版 | 静态门控 |
| --- | ---: | --- | --- |
| Shax the Slimy | 2 | `masters/shax-v1.png` | 底盘 −9.99，精确豁免待批准 |
| Horned Horror | 2 | `masters/horned-horror-v1.png` | 底盘 −10.01，精确豁免待批准 |
| Norgos, the Guardian | 2 | `masters/norgos-guardian-v2.png` | 底盘 −12.09，精确豁免待批准 |
| skeleton archer | 1 | `masters/skeleton-archer-v1.png` | 通过 |
| skeleton magus | 0 | 原生 | 未生图，保持原生 |
| armoured skeleton warrior | 1 | `masters/armoured-skeleton-warrior-v1.png` | 通过 |
| skeleton master archer | 2 | `masters/skeleton-master-archer-v1.png` | 通过；v2 圆盘越界 0.881 |
| skeleton assassin | 0 | 原生 | 未生图，保持原生 |
| ghoul | 0 | 原生 | 未生图，保持原生 |
| ghast | 0 | 原生 | 未生图，保持原生 |
| ghoulking | 0 | 原生 | 未生图，保持原生 |

## 视觉评审

Shax 以蹼足、低垂头和湿发区别 Prox；Horned Horror 的双角、拳和肩后触手区别迷宫 Minotaur；Guardian Norgos 是低伏圆背的暖色活熊，Frozen Norgos 是角状冰壳与直立肩。三款的 48/64/96px 灰度剪影可辨；暗底偏移均仍需逐资产审批。

三个骷髅使用不同武器与装备：普通弓箭手是轻装横弓；大师弓箭手有肩甲、背箭束和更宽的弓；重甲战士手持盾与单手剑，区别既有双手巨剑战士。大师与普通弓手在 48px 仍较近，实机 64px 必须复看；v2 竖弓稿虽然更易区分，但圆盘半径 0.881 超过 0.867，不接入。未画出等级、阵营、血量、护盾。

## 单资产豁免请求

全局 ±8 明度、0.867 圆盘半径及其他门限未变。以下只请求 `base_drift`，并由母版和 128px 导出双哈希及实测值绑定；审阅者可逐项拒绝。

| 身份 | 128px 底盘偏移 | 母版 SHA256 | 128px SHA256 |
| --- | ---: | --- | --- |
| shax | -9.99 | `bb33c4615a77c3ee130e2922fdd6b66370e80c291e2d4d6def9a6ea621b1f098` | `e7eea887ab9eabe238c11bb2e593bd734b13ebcb8ecaeb5da16c1fedbc122f2f` |
| horned-horror | -10.01 | `fe50ca67244e207bfbb1e64daea4ffd6122b12c464aade439651dcb01f9e2516` | `c9bb09b63789d44ebb7b23ddec02eb940c6047e15b8da7f6e0187265acfa5af0` |
| norgos-guardian | -12.09 | `b9bf1dcc5e60cfe076ac294ebf81997362b0f58c00e171fc42855cf100b7151c` | `dc260cae3635bbecb483a480dafd1aa9254539938f5188eb0553c90b16bdc5f8` |

二次亮度返修 Shax +22.20、Horned +30.17 均过亮，选用较接近门限的首稿；Guardian 首稿 +15.89，二稿 −12.09。未对越界的弓手 v2 申请几何豁免。

## 剩余合同与实机

skeleton magus、skeleton assassin、ghoul、ghast、ghoulking 的原生定义均无显式 `image=`；不推断 type/subtype 通用图，也不把玩家 ghoul 棋子当怪物。需在夹具里先核实实例的 image、moddable_tile、add_mos、shader、装备显示；其中 ghoul 还须与玩家 ghoul 分离。仅在合同确认后另立美术批次。

本轮没有 shader、FOV、连续战斗、跨进程存档或 TEAA 安装结论。

## Reviewer decision (2026-09-29)

- Approved the exact-byte base-drift waivers for shax, horned-horror and norgos-guardian.
- Rejected skeleton-master-archer v1: at 48/64/96px it is nearly identical to skeleton-archer, while the native sprite is distinguished by black-and-gold armour. Mapping, manifest entry and runtime token withdrawn; the creature stays native until a redraw carries that armour distinction. Masters and sprite exports remain here as rejected drafts.

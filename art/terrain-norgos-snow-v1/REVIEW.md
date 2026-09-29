# Norgos 雪岩地形美术复核（2026-09-28）

本批经 `tools/run_imagegen.py --execute` 发起 **7 次**内置 ImageGen 单图调用：雪岩地板 1、雪松 1、冬榆 1、上楼梯 1、初版下楼梯 1、世界出口 1、下楼梯重设计 1；未超过任务 8 次硬上限。各调用完整提示词、参考图哈希、原始输出路径和门控记录在 `art/production/handoffs/norgos-snow-*/.../imagegen-calls/call-1/`，母版在 `masters/`，选中件在 `selected/` 与 `selected-masters.json`。初版下楼梯保留作对照，不用于运行。

| 选中构件 | 母版 | 结果 |
| --- | --- | --- |
| 雪岩地板 | `snow-ground-v1.png` | 1254px RGB，全不透明；ACCEPTANCE A2 通过。首次调用暴露 `run_imagegen.py` 在地板专用门控前误套角色原生 alpha 门控；修正工具后对同一 ImageGen 原始输出重新运行地板门控并逐字节登记，无第二次生成。 |
| 雪松 | `snow-tree-pine-v1.png` | 原生 RGBA、四角透明、接地与边距通过。48px 仍有深绿锥形轮廓。 |
| 冬榆 | `snow-tree-elm-v1.png` | 原生 RGBA、四角透明、接地通过；A8.1 左边距实测 24px，要求 25.08px，短缺 1.08px。按 `(asset_id, sha256)` 精确匹配的 `art/production/waivers/a8-edge-margin.json` 单件豁免通过，其余门控未放宽。48px 的宽枝与雪松锥形在形状上可分。 |
| 上楼梯 | `snow-exit-up-v1.png` | 亮的凸起石阶，向远处升高。 |
| 下楼梯 | `snow-exit-down-cave-v1.png` | 初版 `snow-exit-down-v1.png` 在 64px 过于接近上楼梯；重设计为中央深色凹入通道，64px 明暗与几何均可区分。 |
| 世界出口 | `snow-exit-world-v1.png` | 开放的石拱与通往山外的小路，和室内石阶有不同轮廓；它只是可通行的地图出口，不改原生通行规则。 |

`tools/export_forest_terrain.c --snow` 使用森林管线的面积采样、地板与原生 alpha 构件叠合、网格线和最终 parity 乘法，导出 `exports/128/` 的 **12 张** 128px RGBA 完整格。48/64/96px 复核缩放件在 `exports/review/`，64px 两种 parity 的拼版见 `exports/review-sheet-64.png`。`data/gfx/refined/snow/` 的 12 张运行件与对应 `exports/128/` 源文件逐字节相同；SHA-256 清单见 `export-manifest.json`。奇偶与两种树形通过独立的 x 奇偶选择，死资产审计显示零死件。

实机 48/64/96px 截图及六次冷启动的规则验证见 `evidence/norgos-20260928/README.md`。树、石阶、地板在三档尺寸下都保持分层；64px 的下楼梯重设计后不再与上楼梯同形。局限：这套雪岩地板用于 Norgos；Daikara 尚未启用，也未验证无雪岩地与本套素材并置的视觉过渡。Blockout 仍沿用通用绿/棕占位图，雪岩风格只用于 Refined。

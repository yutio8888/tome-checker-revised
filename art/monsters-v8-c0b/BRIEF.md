# C0b：鼠类补全、三款霉菌与骷髅战士（出图 9 款，接入 8 款）

原生身份：giant white mouse、giant brown mouse、giant grey mouse、giant rabbit、
giant crystal rat、brown mold、green mold、shining mold、skeleton warrior。
任务包分三批：`art/production/batches/c0b-rodent-mice-v1.json`、
`c0b-rodent-extra-v1.json`、`c0b-molds-skeleton-v1.json`（脚本限制每包 1–4 项）。
主代理已在 `evidence/c0b-art-gate/` 用隔离夹具解析九个脱离地图的原生副本，
确认全部为可复用的 single-image 合同，九项一并由 hold 转 ready。
每款首轮各调用一次内置 ImageGen（经 `tools/run_imagegen.py`），
小尺寸有具体缺陷时各最多一次定向返修。原图逐字节保留。
**结果：全批 11 次调用，8 款入库接入；`skeleton warrior` 两次都圆盘越界，
配额用尽后按规范剔除并交回设计，运行时保留原生贴图。**
详见 `REVIEW.md`。

共同画面沿用既有规范：俯视三分之四视角、左上柔光、哑光雕刻体块、
中性深灰褐薄圆盘与低调铜灰斜边，机械导出目标占格约 86%，主体全部留在盘内，
外环第六留白，右上等级角与左上交互角留空。盘外是原生透明 alpha，
不画阵营、生命、护盾、等级、文字、光效或场景。

## 差异方案

- **三款 mouse**：已映射的三种 rat 都是低伏横长的四足侧身加一条粗长裸尾。
  三款 mouse 改为**竖立/端坐的紧凑团块**，头顶两只明显放大的圆盘状耳朵破开轮廓，
  身体短圆、尾细。与同色 rat 至少在**剪影**与**明暗分布**两维不同，不靠"小一点"。
  三款之间再以姿态分开：白鼠端坐侧头、棕鼠前倾低头嗅地、灰鼠直立仰头抬前爪。
- **giant rabbit**：低伏团状身躯加一对细长竖耳与巨大后腿，**没有长裸尾**，
  不能读成大老鼠，也不能与端坐圆耳的 mouse 混。
- **giant crystal rat**：仍是鼠的四足体型，但脊背长出硬边晶簇把背线打断成锯齿，
  深灰紫毛配浅玫瑰石英亮面，形成其他鼠都没有的"暗底＋硬边亮片"高频明暗。
  原生没有 shader，因此晶体画成哑光矿物，不发光。
- **三款 mold**：已映射的 grey mold 是层叠波浪褶的莲座。新三款各占一种形态：
  brown mold＝扁平同心生长环的硬壳；green mold＝鼓胀圆瘤堆成的团块；
  shining mold＝一簇分开的细长柱体组成的放射状开放轮廓。
  "shining" 只是名字与描述，原生无 shader、无光源，因此不画自发光与光晕，
  只用最亮的蜡质柱头做明度身份。三款都必须读成占满棋子的立体生物，不是地面装饰。
- **skeleton warrior**：与已映射的 degenerated skeleton warrior 区分——后者是
  亮骨、断臂、低伏散架的宽剪影；本款是直立紧凑的着甲剪影，锈铁胸甲与头盔构成
  大块中暗调，只有颅骨/前臂/胫骨留亮骨，双手持一把斜举的双手巨剑。
  解析出的原生装备确实是 `iron greatsword` 且**无盾**（带盾的是本批之外的
  armoured skeleton warrior）。也要与已映射的 skeleton mage（长袍＋法杖）区分。

## 验收

母版：RGBA 原生 alpha、alpha 跨 0–255、四角透明、方形且 ≥512px。
128px 导出：`tools/check_token_style.py` 的圆盘越界（≤0.867）、底盘偏移（±8）、
扇区上偏（≤+20）、四角 alpha、占格 0.83–0.91，**新资产不吃 GRANDFATHERED 豁免**。
这些由 `tools/run_imagegen.py` 在调用当场判定，并由 `export.py` 在批次导出时复测。
机械判据不等于验收：48/64/96px 的实际看图与同族灰度对照结论见 `REVIEW.md`。
运行映射、打包与实机核验由主代理负责。

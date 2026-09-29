# 第六批：Kor'Pul 盗贼四款

按本轮范围仅生成 cutpurse、rogue、thief、bandit。实际阅读 AGENTS.md、imagegen SKILL.md 和原生 `game/modules/tome/data/general/npcs/thieve.lua`；使用内置 image_gen，每款单独调用，共四次成功调用，首版通过静态自审。未使用 CLI/API 后备，未程序绘制、抠底或修改生成像素。装备替换、boss、楼梯均不属于本次美术任务。

四款继承原生 BASE_NPC_THIEF 的双 dagger 与 light armor。Cutpurse 是初学者；rogue 增加 stealth 与换位；thief 强调 stealth、disarm 和 poison；bandit 描述强调蛮力，同时仍为双匕首轻甲盗贼。通过身份衣装与姿态表达，未绘制技能生效、透明身体或状态颜色。

沿用 v5 哑光上色微缩件、陡俯视三分之四镜头、左上柔光、中性暗灰褐薄圆盘及低调铜灰物理盘沿。角色与刀刃全部在盘内，顶部与右上外圈留空。没有阵营环、血条、护盾、等级、稀有度、选中或文字。

| 角色 | 剪影 | 明度与低饱和色相 |
| --- | --- | --- |
| cutpurse / 扒手 | 裸头短发、窄身、三角叉腿、短刃下持 | 浅麻衣与赭褐裤，浅色肩胸清楚 |
| rogue / 游荡者 | 尖兜帽、角形短披肩、横伸短刃 | 冷灰靛蓝上身、暗灰裤，肩背面非黑 |
| thief / 窃贼 | 左侧低蹲、弯曲长斗篷、双刀平行前伸 | 烟褐大块长披布，较暗但保留亮褶 |
| bandit / 强盗 | 秃头裸臂、宽肩方形蹲姿、粗短双刀 | 肤色亮头肩、深褐轻皮背心、暗锈褐腰布 |

实际查看四张原生盗贼、v5 退化骷髅战士、cave-troll-v3、v4 48/64/96 参考页和运行玩家 hero.png。玩家参考仅用于区分身份，不把其蓝色选中环纳入新画。四原生参考和风格检查图已保存在 references/，其来源与 SHA-256 见 manifest.json。

masters/ 为未经修改的生成母版；prompts/ 保留逐字完整提示词、工具、输入角色、原始输出路径、保存路径、哈希与原生 alpha 量测。selected-masters.json 与 catalog.json 采用 v5 格式。机械导出由集成代理使用既有 C exporter 完成，详细记录见 export-report.json。此文不宣称任何实机验证。

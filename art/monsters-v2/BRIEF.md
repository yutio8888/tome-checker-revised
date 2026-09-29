# 怪物棋子第二批：扩展 12 种

沿用 ../monsters-v1/BRIEF.md 的视觉规则。本批继续使用内置 ImageGen 直出，不进行 Blender 对照或建模实验。每个实体单独生成一张透明 PNG，使用第一批实际通过审核的母版作材质／角度／中性圆盘参考。

画面中的圆盘与第一批保持同样大小；主体尽量占盘内可用范围，但全部留在盘沿以内。不要为满足“盘内”把生物缩成很小的摆件。识别点靠大轮廓、头部和姿态；不单纯给旧棋子换色。阵营、rank 和状态一律留给程序层。

| ID | 精确实体 | 原版身份参考（shockbolt/npc/） | 优先识别点 |
| --- | --- | --- | --- |
| stone-troll | stone troll | troll_s.png | 灰石色皮肤与粗硬块面，姿态区别于森林巨魔 |
| cave-troll | cave troll | troll_c.png | 原图的长矛和洞穴巨魔轮廓；武器也收在盘内 |
| prox | Prox the Mighty | giant_troll_prox_the_mighty.png | 独特脸型、体格和原图装备；不只是森林巨魔放大 |
| bill | Bill the Stone Troll | troll_bill.png | 石巨魔和树干巨棒的显著组合，不挤进邻格 |
| great-wolf | great wolf | canine_gw.png | 更厚实的颈肩／竖毛，姿态区别于普通狼 |
| fox | fox | canine_fox.png | 尖脸、大蓬尾、暖狐色、轻巧的四足比例 |
| black-bear | black bear | black_bear.png | 深毛色、较长口鼻，保留浅灰棕高光防止糊进盘面 |
| brown-rat | giant brown rat | vermin_rodent_giant_brown_rat.png | 圆耳、长裸尾和尖鼻，不画成小号狼 |
| king-cobra | king cobra | green-snake.png | 展开的颈罩与竖起前身；区别于棕蛇的低盘曲 |
| bee-swarm | bee swarm | bee_swarm.png | 3–5 个清楚的蜂形组成一个群体棋子，区别于单体昆虫 |
| giant-eel | giant eel | aquatic_critter_giant_eel.png | 鳗鱼头、细长鳍边、流线弯身；不做成另一条盘蛇 |
| dragon-turtle | dragon turtle | aquatic_critter_dragon_turtle.png | 甲壳、四肢、尾和龙形头部的大轮廓 |

以上识别点须以实际看过的原图与实体说明为依据；原图缺乏清晰信息时保守处理，不凭名称添加未经支持的身份配饰。独特角色原图为 64×128，新的单格构图需要重新安排姿态，不能直接压扁。

生成代理按 giants（4）、beasts（4）、shapes（4）分工。每个物种独立调用；保存 masters/<id>-v1.png 与 prompts/<id>-v1.json。必要的定向返修保留版本，prompt记录关联上一张图及改变的唯一目标。每张查看原生 alpha 与实际画面；留白可由统一尺寸导出处理，不能自行程序抠底／补画。源图只作为身份与风格参考，不直接作为完成的棋子交付。

母版建议来自第一批：forest-troll-v1.png、wolf-v2.png、brown-bear-v2.png、brown-snake-v1.png、venus-flytrap-v1.png。每次只用最相关的一两张风格图，避免混淆身份。验收以 64px 为主、48px 压力、96px 放大；这是静态素材样板，不代表全图库覆盖或实战验收完成。

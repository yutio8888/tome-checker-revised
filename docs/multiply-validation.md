# 白色蠕虫原生 Multiply 验证

0.5.2 已接入 `white-worm-mass` 并通过实机验证，记录及原始截图在 `evidence/runtime-v052/`。`tools/package_runtime.py --runtime --fixture` 或 `tools/launch_fixture.py` 会把本测试装到独立 fixture 命名空间，再通过 fixture 调试入口执行：

```lua
multiply_audit = dofile('/data-checker-fixture/monster-live_multiply.lua')
multiply_audit.run()
-- 此时三个冻结个体留在原生生成的位置，可截图。
multiply_audit.cleanup()
```

`run(false)` 在验证后立即清理。结果写入 `/multiply-validation.txt`，同时输出 `[MultiplyLive] PASS/FAIL`。记录包含技能源码位置、前后回合、父子关系、坐标、rank、level、生命、繁殖次数、经验、能量、技能保留状态，每个棋子／叠加层的 Entity uid、actor／display／overlay 的 map object 标识，以及各演员实际收到的 body／overlay 回调次数。保留个体也可从 `multiply_audit.actors` 获取。开始下一次或离开当前关卡前先 cleanup；错误会自动清理本次已登记实体。

护栏要求真实 `CheckerFixture.enabled()`、`checker_fixture=true`、无登录、禁用连接、cheat、staged Trollmire、原 hero 控制、暂停和棋子启用。脚本从原生 vermin 定义创建一个普通白色蠕虫，不改 spawn pool、不腾挪已有实体、不改地形。若没有连续两代均安全可见的空邻格，会失败并清理，可换较空的 staged 场景再跑。

脚本直接调用游戏已注册的真实 `T_MULTIPLY.action` 两次。后代由原生 `cloneActor` 和 `zone:addEntity` 产生，无 mock 或测试自制复制体。父体先渲染，再繁殖，显式断言三代的 `actor._mo`、`state.display._mo`、`state.overlay._mo` 互不共享。最后短暂包装各实例的绘制方法进行计数，调用真实 forceRedraw，要求三个实例各自收到 body／overlay 回调且自身 map object 不变；包装始终恢复。这会捕捉父体 callback 被后代覆盖的问题。为了检验生命继承，测试明确把父体设为原生存活生命区间的 55%；未改变 rank、max_life、level、攻击或繁殖预算。原生两代次数为 `4 → 父3/子2 → 父3/子1/孙0`，后代经验 `0.1`、初始能量 `0`、无掉落，最后一代不再学到 Multiply。断言同时覆盖 rank／生命／max_life／level／combat 继承，渲染前后规则字段不变，以及既有实体、玩家能量和世界回合不变。

原生依据：`game/modules/tome/data/general/npcs/vermin.lua:22–54` 定义 white worm mass（rank 1、can_multiply 4、Multiply 1）；`data/talents/misc/npcs.lua:38–69` 扣除预算、克隆、重学技能并入图；`engine/Actor.lua:90–104` 执行 cloneActor；`mod/class/Actor.lua:105–109` 设置克隆能量 0 等默认项，`:3080–3086` 设置 immune_possession，`:7884` 只在首次入关卡时重置生命。

范围：这是实际技能 action 的复制与渲染审计；不经过 `useTalent` 的通用冷却／施法能量包装，不推进整局回合，不验证完整战斗 AI。原生生成消耗 fixture RNG／UID 并临时加入三个实体；只用于可丢弃离线环境，不写玩家存档。

主代理已在 shader 开启的实际游戏中验证两代繁殖、三实体的真实绘制回调和安全清理，并拍摄1920×1080的64／96px截图。初次测试因岸边可用空格太少而安全拒绝，随后只扩大测试位置搜索范围，未挪动已有演员或改动地形；首次拒绝也保留在证据目录。96px补拍等待原生镜头滚动完成，避免最上一代尚未进入画面。

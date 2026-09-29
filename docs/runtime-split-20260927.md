# 正式运行包与离线夹具拆分 — 2026-09-27

本轮将棋子渲染、地形偏好与专用演示环境分开。正式代码不再要求 cheat、`checker_demo`、Trollmire 或某个 HUD 才能识别已覆盖生物，也不再强制出生、固定区域布局或读取可执行测试命令。身份与外观保护仍由 `CheckerTokens` 决定；未知生物保留原图。

## 正式选项与接口

| 设置 / 接口 | 当前行为 |
| --- | --- |
| `config.settings.tome.checker_tokens_enabled` | 缺省 `true`；只控制生物棋子 |
| `config.settings.tome.checker_terrain_mode` | 缺省 `vanilla`；接受 `vanilla`、`blockout`、`refined` |
| `game:checkerTokensEnabled()` | 读取棋子启用状态 |
| `game:checkerSetTokensEnabled(boolean)` | 保存棋子选项，立即恢复或重新识别当前层生物 |
| `game:checkerSetMode(mode)` | 保留历史公开入口，但现在**只切换地形**，同时保存偏好 |
| `game:checkerToggle()` | 在 refined / vanilla 地形之间切换 |
| `game:checkerRefreshActor(actor)` | 刷新一个生物，包括不在 `level.entities` 内的测试实例 |
| `game:checkerApplySettings()` | 按当前设置应用地形并刷新地图；进入新层、读取游戏后调用 |

Game Options 的 `Board colors` 已改为 `Token colors`。同页新增 `Creature tokens` 和 `Trollmire terrain`，颜色对话框本身不变。选项由独立 `mod.class.CheckerOptions` 保存到 `tome.checker_*`，无需 Board 或任一 `uiset`。即使在没有当前地图的菜单环境中，也能保存偏好。

地形默认保持原生；仅非 flooded 的 Trollmire 使用已检查的草地、花草、树木、道路、出口和普通水面。未知宝库地面、门、炖锅和特殊地形保留原图；其他地区完全保留原生地形。`checker_mode` 表示当前区域实际采用的地形模式；在其他区域为 `vanilla`，已保存的 refined 偏好仍可在回到支持区域时生效。

已安装的地形外观由每个格子的 `_checker_terrain` 记录 ownership，避免重新进入地图时把旧替换误认作原图。切换只改显示，不调用移动、FOV 重算、出生或区域生成规则。外部替换显示仍归原所有者处理。生物渲染与保存引用策略继续由原有 Actor / identity 代码负责。

## 历史测试语义迁移

旧测试使用 `checkerSetMode('vanilla')` 关闭棋子、再用 `refined` 打开。现在应分别调用 `checkerSetTokensEnabled(false)` 和 `checkerSetTokensEnabled(true)`；地形 vanilla 与已启用棋子可以同时存在，任何地形切换都不会重新打开已关闭棋子。

需要迁移的现有调用集中在 `tests/token_mapping.lua`、`tests/live_scene.lua` 和 `tests/lifecycle.lua`。仅用于比较原生生物图的 `game.checker_native_actors` 兼容开关留在专用 fixture 中，正式包不读取它。

正常玩家不会因持有旧 `checker_hero` 字段而被换成固定 Berserker 图。专用 fixture 可以记录 `checker_hero` 供旧场景断言使用，但只有明确传入 `checker_hero=true`（启动器 `--hero-token`）才使用该演示图。

## 专用 fixture

源码目录为 `tests/fixture/tome-checker-fixture/`，独立短名 `checker-fixture`，不声明对棋子或 Board HUD 的依赖。它独自持有：

- 固定 Cornac Berserker 出生、随机种子和 Trollmire DEFAULT 布局、固定池塘数量。
- `game:checkerStage()`、`checker-command.txt` 命令读取与截图入口。
- `board-test-command.txt` 的 Lua 执行桥，以及原地形 audit。
- 可选固定英雄图和历史 `checker_native_actors` 测试兼容逻辑。

所有这些行为同时要求安装 fixture、`checker_fixture=true`、cheat 与 offline 设置；仅安装正式包不会提供这些入口。未安装棋子包时仍能出生、摆位和截图，地形 audit 跳过不存在的棋子地形 API。

fixture 继续设置 `checker_demo=true`，以兼容既有 live 测试护栏。数据路径统一为：

```lua
dofile('/data-checker-fixture/audit.lua')
scene = dofile('/data-checker-fixture/monster-live_scene.lua')
```

`package_runtime.py` 将顶层 `tests/*.lua` 复制为 fixture 的 `data/monster-*.lua`；正式 `data/` 不再注入测试文件。外部 `demo/board-hud/tools/debug.py` 只需检查 fixture 已安装、写命令并触发 audit，不再覆盖运行包的 audit 文件。`demo/checkerboard-v3/tools/command.py` 的命令/截图文件位置保持不变，可使用 `tokens on/off` 和 `zoom 48/64/96`。

## 打包、安装与冷启动

下列命令从 `/workspace/t-engine4` 执行。停止现有离线 fixture 后再启动；本次拆分子代理未执行任何真实启动、停止或当前 session 安装操作。

```bash
# 正式 .teaa：只打包运行源码与资源，排除整个 fixture、tests、tools、art、.git 和旧 audit。
python3 game/addons/tome-checker-revised/tools/package_runtime.py

# 明确安装正式包及专用fixture（只作用于既有 checkerboard-v3 runtime）。
python3 game/addons/tome-checker-revised/tools/package_runtime.py --runtime --fixture

# 查看所选组合，无写入、无启动。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Minimalist --without-board --shaders --terrain vanilla --dry-run

# 仅棋子 + 原生 Minimalist：原生玩家、原生地形、默认3秒日志淡出。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Minimalist --without-board --shaders --terrain vanilla

# 仅 Board + 原生生物/地形。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Board --without-tokens --shaders

# 双插件演示；明确允许固定演示英雄图。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Board --shaders --hero-token

# 可选：原生 Classic，完全不加载 Board。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Classic --without-board --shaders --terrain vanilla

# 可选：只有正式棋子包，正常出生、cheat=false、无命令桥。
python3 game/addons/tome-checker-revised/tools/launch_fixture.py --hud Minimalist --without-board --without-fixture --terrain vanilla --shaders
```

启动器会精确安装所选插件，因此运行 launch 前无需另行执行 package 安装命令。`--prepare-only` 完成相同安装和配置准备，但不启动进程。`--without-board` 缺省选择 Minimalist；明确指定 `--hud Board --without-board` 会报参数错误。没有棋子包时只能选择 vanilla 地形，也不能请求英雄棋子图。

每次真实准备都将 `session/home` 原目录完整移至 `session/previous-homes/<UTC时间戳>`，再生成干净 home；不会读取历史 Minimalist 坐标、旧 shader override 或普通用户 home。相同插件的旧 `.teaa` 归档到 `session/previous-addon-packages/`，避免旧压缩包与新目录重复发现。所有运行安装、配置、日志与归档均位于 `demo/checkerboard-v3`。窗口沿用软件渲染环境，明确设置 `SDL_FRAMEBUFFER_ACCELERATION=0`、禁用网络与 Steam。

## 已完成验证与边界

- `lua5.1 tests/runtime_modes.lua` 与 `luajit tests/runtime_modes.lua`：各 **85** 项通过，涵盖所有当前 catalog 身份无 cheat/区域门槛、原生玩家保护、独立保存与即时刷新、未知地形、地形 owner 恢复、菜单设置和无棋子依赖的 fixture 装载。
- 13 个本轮 Lua 文件通过 `luac5.1 -p`；两个 Python 工具通过 AST 语法检查。
- launcher 7 种有效组合、4 种非法组合、显式 hero opt-in 与 offline/fixture 参数通过纯检查。
- 在 `demo/checkerboard-v3` 内创建并清理临时测试目录，验证精确安装会移除陈旧 debug 文件、不会通过硬链接改写源文件。
- 正式 ZIP 在内存中生成，1748 个条目通过 CRC 与 fixture 排除检查；没有用该检查安装或替换当前 session。

这些是纯测试与打包检查，未代替主代理负责的三个组合冷启动、当前引擎截图、原生跨进程恢复和 shader 实机验证。Board 专有小地图调色与地面物品标记仍是 HUD 的可选差异，不在本次 Minimalist 范围中重做。

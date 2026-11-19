# 马里奥动画速度与试玩方式

## 直接使用

双击 Ubuntu 桌面 **Week16-Mario-Fast**。先点击游戏窗口，然后按 **I** 开始，**WASD** 控制方向，**J/K** 控制动作，关闭游戏窗口退出。

这是同一份固定版本 LiteNES 的 Ubuntu 原生构建，供流畅试玩。它不经过 RV32 NEMU 或 RTL，不能代替课程中的 CPU、设备或游戏验收。课程入口 **Week16-Mario-NEMU** 与 **Week16-Mario-Characters** 保留。

## 2026-11-19 实测与原因

原 NEMU 图形版的 120 个 NES 模拟帧耗时 23.79 秒，仅 **5.04 模拟帧/秒**，复现了动画很慢的问题。

- 关闭逐帧哈希与日志：23.48 秒，5.11 模拟帧/秒，改善很小。
- 将 GPU 裁剪从逐像素检查改为一次裁剪、逐行复制：无哈希版本 19.25 秒，6.23 模拟帧/秒；保留校验的版本约 6 帧/秒。仍达不到流畅试玩的目标。
- 实际 NEMU 配置已经使用 `-O2`，并关闭 trace/debug。配置文件中的无效符号 `CONFIG_CC_OPT_O2` 修正为真正的 `CONFIG_CC_O2`；原先默认值也是 O2，因此这项更正没有被算作提速。
- 同一份 LiteNES 改用 AM 的 native 平台：120 帧含启动耗时 2.37 秒，50.59 模拟帧/秒；持续进入关卡的 7 秒测试中，每秒计数均为 63。上游按整数毫秒限速，`1000 / 60 = 16`，因此接近 62.5 模拟帧/秒。

主要限制是 LiteNES 的 NES 模拟工作又被编译成 RV32 指令，再由教学 NEMU 逐条解释执行。单纯删日志或调整显存复制不足以补偿这层开销。原生版移除 RV32 解释执行这一层，但保留同一份 NES CPU、PPU 和游戏源数据。

上游 `FRAME_SKIP=1`，每两个 NES 模拟帧绘制一幅画面；因此约 63 模拟帧/秒对应约 31.5 次游戏绘图/秒，不宣称 63 幅独立画面/秒。基准包含启动时间，NEMU 使用 SDL dummy，native 使用真实桌面窗口；这是本机的体验测量，不是严格跨平台性能排名。

## 验证范围

- 优化前 NEMU、优化后 NEMU、native 的前 120 帧共 60 个画面哈希完全一致。
- 图形版普通启动不计算哈希、不打印逐帧验收日志；有界测试仍保留哈希。
- 显存裁剪测试覆盖四个边缘、跨行源步长、极端坐标、空或负尺寸；键盘、串口和时钟回归通过。
- 真实 native 启动脚本接受定时 SDL 开始、移动、跳跃和退出事件。人工检查实际截图，确认已进入 1-1 关卡；正常退出码为 0。
- 学校 OJ 未验收，原生试玩结果不计入 RTL/NEMU 的通过项。

完整测量值与哈希：[性能证据](evidence/game-performance.json)。

## 复现

在已有第 16 周环境的 Ubuntu 桌面终端执行：

```bash
cd ~/course-week8-work
source pa2/env.sh
python3 pa2/install_io.py
python3 pa2/prepare_litenes.py --mode graphics
make -C build/litenes-graphics ARCH=riscv32-nemu image
make -C build/litenes-graphics ARCH=native image
bash tools/install-week16-launchers.sh
bash tools/run-week16.sh fast
```

有界一致性与速度测试：

```bash
python3 pa2/prepare_litenes.py --mode graphics --frames 120
make -C build/litenes-graphics-test ARCH=riscv32-nemu image
make -C build/litenes-graphics-test ARCH=native image
python3 pa2/benchmark_game.py --label nemu --min-fps 0
python3 pa2/benchmark_game.py --native --label native --min-fps 45 \
  --compare build/performance/nemu.json
python3 pa2/test_native.py
python3 pa2/test_io.py
```

`--min-fps 0` 只用于采集仍然缓慢的 NEMU 数据；去掉它，默认 30 模拟帧/秒门槛仍会失败，不能将采集成功当作 NEMU 流畅性测试通过。native 测试需要可用的桌面显示环境，测试注入只作用于被测试进程，不修改正常游戏的输入处理。

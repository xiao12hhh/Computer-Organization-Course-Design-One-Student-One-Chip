# 第 15–16 周：RTL minirv 与输入输出

本地实现与验证已完成。代码和本参考说明由 AI 按学习者要求编写；需补学后独立讲解，学校 OJ 和个人报告不在本次验收声明内。

## 第 15 周实现

`npc/minirv/` 是新的 RTL NPC，原来的 sCPU 工程保留在 `npc/`。新处理器严格限制为 16 个 32 位寄存器，以及 add、addi、lui、lw、lbu、sw、sb、jalr 八条指令；另有 ebreak 作为仿真退出约定。没有把 C 解释器当作 RTL 执行器，也没有通过添加乘除法 RTL 来绕过 minirv 转译。

`regfile.sv` 保存寄存器并保护 x0；`decode.sv` 产生执行、访存和写回控制；`top.sv` 负责取指、加载数据选择和时钟提交。C++ 仅提供 RAM、设备、文件加载、运行控制和验证。加载/取指经 DPI-C 读取对齐 32 位字；lbu 在 RTL 选择字节。sw/sb 根据字节掩码写入，写入只发生在上升沿；ebreak 也只通知一次。非法指令、高编号寄存器和未对齐字访问会停止并报错。

默认 PC/RAM 起点为 0x80000000，与 AM 一致。`--base 0` 可运行前期 Logisim 的原始镜像。RAM 为 128 MiB，所有访问检查边界。返回 a0=0 为 GOOD TRAP，否则 BAD TRAP；达到指令上限返回状态 2，不能视为通过。

AM 的 minirv 工具链将常用算术/分支转换成八条指令和查表操作，因此能运行复杂 C 程序。设置 `NPC_BIN` 后，官方 `make ARCH=minirv-npc ALL=dummy run` 也已经可用。编译流程中的 `python` 改成 `python3`，无须安装旧命令别名。

## 第 16 周实现

NPC 串口位于 0x10000000，写一个字节就在终端输出字符。时钟位于 0xa0000048/0xa000004c，先读高 32 位触发快照，再读低位；AM 使用它提供启动后的微秒数。时钟源为宿主单调时钟，不会因调整系统日期倒退。日历时间仍沿用课程的占位值，不能把它当成真实日期。

NEMU 增加 AM 时钟、键盘和显存驱动，启用框架中的设备模型，并补齐显存刷新标记的处理。驱动支持带裁剪的矩形绘制；键盘按下/松开经 SDL、NEMU 队列、MMIO、AM 接口到达客户程序。音频与磁盘不在这次必做范围内。

马里奥来自已经固定版本的官方 `am-kernels/kernels/litenes`。NES 的 CPU、PPU 和游戏数据沿用上游；本项目只在被忽略的 build 目录生成派生版本，增加字符渲染和有界测试退出。字符画从真实 PPU 256×240 画面采样成 64×30，并输出画面哈希；不是预先写好的标题图。ROM 未复制进本仓库。

## 直接打开

Ubuntu 桌面入口：

- **Week15-NPC-Tests**：运行 RTL 核心检查。
- **Week16-Mario-Characters**：在 RTL minirv 中持续运行字符版。八指令转译开销很大，本机标题画面需等待数分钟；Ctrl+C 退出。按课程当前阶段要求，此版没有键盘控制。
- **Week16-Mario-NEMU**：NEMU 图形版；I 开始，WASD 方向，J/K 动作。请先点击游戏窗口使其获得焦点，关闭窗口退出。
- **Week16-RTC-Test**：运行官方时钟测试，确认 1、2、3 秒输出后自动停止其无限循环。

命令行入口：

```bash
cd ~/course-week8-work
bash tools/run-week16.sh char
# 或：graphics / rtc / test
```

## 验证结果

- 核心定向/随机测试覆盖寄存器、立即数、各字节通道、JALR 源目的重合、x0、错误指令、越界和指令上限。
- 原 Logisim mem/sum 镜像只在 halt 处加入 ebreak，在 RTL 分别执行 5,763 / 5,883 条指令，a0=0；逐指令 PC、全部寄存器、每个写入字节与独立 C 模型一致。
- 官方 cpu-tests 全部 36 个通过：35 个 GOOD TRAP，wrong 是预期 BAD TRAP。全程开启逐指令对照。
- 官方 `riscv-tests-am` 的 38 个 RV32I 测试转译到 minirv 后全部通过。沿用上游对 fence_i、ma_data 的排除；M 扩展汇编不在该 minirv 转译器支持范围，未伪称其通过。C 乘除法由软件例程处理，已由 cpu-tests 覆盖。
- 串口、微秒时钟、显存边缘裁剪和读回通过；SDL 注入 A 按下/松开后，AM 得到正确键码和状态。
- 官方 `am-tests` 的 rtc_test 原函数输出 1、2、3 秒，随后测试工具主动终止无限循环；没有将其描述成 GOOD TRAP。
- 字符 LiteNES：40 个 NES 模拟帧，跳帧后输出 20 幅字符画，5 个不同画面哈希。RTL 执行 1,844,371,963 条指令、输出 44,118 个串口字节，最后 a0=0/GOOD TRAP。一次验证约 4 分 19 秒，耗时受宿主负载影响。
- NEMU LiteNES：120 个 NES 模拟帧，刷新 60 幅画面、7 个不同哈希，GOOD TRAP；一次运行约 33 秒。
- 第 13 周调试器和监视点回归通过。新增可复现的 PA2 编译链接实验，独立副本运行，没有污染工作 NEMU。

记录：[字符版第 40 帧](evidence/week16-npc-frame.txt)、[NEMU 实际截图](evidence/week16-nemu.png)、[链接实验结果](evidence/week16-linkage.json)。这些是本地验证，不是平台评分或官方架构认证。

## 复现

在第 14 周环境已就绪的基础上执行 `bash pa2/setup_week16.sh`。脚本校验固定版本与已安装补丁，保留未知用户改动。RISC-V 测试新增固定提交 `676cbc7a4e520fca1c3d4dd1b586b2550769e02e`；NEMU/AM/am-kernels 版本沿用 [第 13–14 周记录](weeks13-14.md)。

```bash
cd ~/course-week8-work
source pa2/env.sh
export NPC_BIN="$PWD/build/minirv-npc/npc"
make test-week15
make test-week16            # 包含真实游戏执行，需数分钟
python3 pa2/test_games.py --verify-only  # 只重查已有游戏日志
python3 pa2/linkage_experiments.py
```

可选波形：`build/minirv-npc/npc --trace build/minirv.vcd --diff 程序.bin`。无限运行请显式 `--max 0`；做测试时保留有限指令预算。

补学见 [第 15–16 周学习路线](study-weeks15-16.md)，必答题见 [PA2 参考解答](pa2-answers.md)。对应官方 [D4](https://ysyx.oscc.cc/docs/2407/d/4.html)、[D5](https://ysyx.oscc.cc/docs/2407/d/5.html)、[PA2 输入输出](https://ysyx.oscc.cc/docs/ics-pa/2.5.html)。

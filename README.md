# 计算机组成原理课程设计 · 一生一芯

记录课程学习、实验代码和阶段进展。

## 当前进度

截至 2026-11-18：

- 已安装 VMware 和 Ubuntu 22.04.5 LTS。
- 已安装 Logisim-evolution，并完成第一个简单电路（学习者反馈；电路文件尚未归档）。
- 已初始化 ysyx-workbench 的 NPC 和 NVBoard 环境。
- Verilator 5.054 官方 Hello World、波形示例编译运行通过。
- NVBoard 官方示例已运行，LED 流水灯、数码管和 VGA 图片显示正常。
- GTKWave 已打开生成的 VCD 并显示信号。

已追加前八周的本地参考实验包：Logisim 基础电路、求和状态机、完整 sCPU、两指令 minirv、HDLBits 本地练习与 NVBoard 演示。代码由 AI 根据学习者要求编写并验证，尚未取得学校 OJ 或 HDLBits 的在线通过记录，不代表学习者已独立掌握。

## 文档

- [环境配置和使用说明](docs/environment.md)
- [学习进度日志](docs/progress.md)
- [前八周实验内容、运行方法与验收范围](docs/weeks01-08.md)
- [第 9–12 周实验、启动方式与验证范围](docs/weeks09-12.md)
- [第 9–12 周补学路线](docs/study-weeks09-12.md)
- [第 13–14 周：监视点、RV32IM 与 AM](docs/weeks13-14.md)
- [第 13–14 周补学清单](docs/study-weeks13-14.md)
- [PA1 必答题参考与源码统计](docs/pa1-answers.md)
- [第 15–16 周：RTL minirv、设备与马里奥](docs/weeks15-16.md)
- [第 15–16 周补学路线](docs/study-weeks15-16.md)
- [PA2 必答题参考与链接实验](docs/pa2-answers.md)
- [后续补学顺序](docs/study-next.md)
- [本地验证结果](docs/test-results.md)

第 9–12 周本地实现已追加：可切换进制的七段显示、移位器/LFSR/键盘实验、完整八指令 minirv、带输出的 RTL sCPU，以及实际 NEMU 框架中的简易调试器与表达式求值。官方 mem/sum 程序、RTL 差分测试和 NEMU 集成测试通过。学校 OJ 未验收。

第 13–14 周已追加：32 槽监视点、RV32 整数与 M 扩展执行核心、AM 运行环境、字符串和格式化库、PA1 必答题参考。35 个正常 cpu-tests 均 GOOD TRAP，故意错误的 wrong 程序正确 BAD TRAP；AM 求和示例输出 5050。执行 `make test-week13 test-week14` 复测。详见上述说明中的范围与限制。

第 15–16 周已追加：严格八指令/16 寄存器 RTL minirv NPC、DPI-C 内存与退出、串口/时钟、NEMU 键盘/显存驱动。36 个 AM CPU 测试及 38 个 RV32I 转译测试通过。字符版马里奥在 RTL 上完成 40 帧并 GOOD TRAP；NEMU 图形版完成 120 帧。Ubuntu 桌面新增 Week15-NPC-Tests、Week16-Mario-Characters、Week16-Mario-NEMU、Week16-RTC-Test。

电路位于 `logisim/`，硬件代码位于 `rtl/`，平台题目本地版本位于 `hdlbits/`，测试位于 `tests/`，虚拟板入口位于 `nvboard/` 和 `nvboard-labs/`，独立 NPC 工程位于 `npc/`，NEMU 补丁和测试位于 `pa1/`。

Ubuntu 在仓库目录执行 `make test`；Windows 按前八周说明生成测试向量，再运行 `python tools/test_logisim.py`。新实验已部署到 Ubuntu 的 `~/course-week8-work`。

## 提交约定

按学习者要求，每完成一个有意义的小步骤，将相关文件和进度记录提交并推送到本仓库。

1. 开始工作前检查远端更新，保留已有修改。
2. 记录本次改动、实际验证结果、未解决问题和下一步。
3. 检查待提交文件，只提交本次相关内容。
4. 提交说明使用清楚的中文，例如：`docs: 记录开发环境验证结果`。
5. 推送完成后提供提交链接；失败时明确说明，不把本地提交当作已同步。

这是按步骤执行的提交约定，不是后台自动同步。虚拟机、安装包、密钥和编译产物不纳入仓库。

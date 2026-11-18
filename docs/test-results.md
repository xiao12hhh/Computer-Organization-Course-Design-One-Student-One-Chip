# 本地验证结果

执行日期：2026-11-13。

## Logisim-evolution 4.0.0

实际通过已安装 Logisim 的测试向量模式和命令行时钟仿真运行。测试入口：`tools/test_logisim.py`，不是仅对 XML 格式进行检查。

```
PASS decoder24: 4 vectors
PASS encoder164: 17 vectors
PASS full_adder: 8 vectors
PASS mux4x3: 16384 vectors
PASS sum10: every state from 0 to 10; final sum 55
PASS scpu: all 35 architectural states, sum 55
PASS minirv2: all 6 call/return states, a0=30, ra=12, PC=12
PASS minirv2_edges: negative immediates, wraparound, x0, JALR bit zero and rd==rs1
ALL LOGISIM CHECKS PASSED
```

普通编码器的 17 个向量覆盖全零和 16 个独热输入；它没有声明多位同时有效时具有优先选择功能。sCPU 的轨迹由独立 Python 解释器按照指令语义计算，并逐行对照 Logisim 输出。

## Verilator 5.054 / Ubuntu 22.04.5

运行 `make test`，启用断言和定时语义。

```
PASS: exhaustive decoder, encoder, priority, adder, mux and ALU
PASS: sum10, complete sCPU, ADDI/JALR, x0, signed immediates, alignment and reset
PASS: 7 HDLBits local exercises (not online judge submissions)
```

组合逻辑覆盖译码器 4 组、编码器 65,536 组、带使能的优先编码器 512 组、全加器 8 组、四选一 16,384 组、ALU 2,048 组输入。时序检查覆盖求和、分支成立/不成立、调用返回、复位、立即数边界、x0、跳转位 0 清除、rd=rs1、非法指令及未对齐跳转。

测试程序使用显式整型参考值与小位宽信号比较，因此测试编译关闭 WIDTHEXPAND 的提示；并未全局忽略所有警告或关闭断言。

## NVBoard

DEMO=0、1、2、3 分别构建为独立程序，并在 Ubuntu 桌面会话中各执行 100,000 次仿真周期，退出状态均为 0。其核心电路由上述 RTL 测试覆盖。

这个检查证明四个程序可以编译、链接、初始化虚拟板并运行；不等于学校 OJ 评分，也不宣称穷举了 GUI 鼠标交互。

## 平台与范围

未登录或提交到 HDLBits/学校 OJ，没有在线 AC 记录。minirv 本次仅为第八周的 addi/jalr 子集；不是完整 RV32I 或完整八指令 minirv。实际学习掌握情况仍需通过解释、修改和答辩检验。
# 2026-11-18：第 9–12 周追加验证

- Logisim 进制显示：全部 256 个数 × 4 种进制，共 1024 组向量通过；计数器 256 个状态通过。
- 完整 minirv：自编程序 65 状态、官方 mem 和 sum 各 6001 状态，PC/全部 16 个 GPR/fault 逐周期对照独立 ISA 模型通过。mem 最终 PC=0x121c，sum 最终 PC=0x224，均 a0=0。
- Verilator：8192 个桶形移位组合、4096 个寄存器移位组合、LFSR 全 255 非零状态、256 条 FSM 输入流通过。
- PS/2：通码、重复码、断码、数字、错误奇校验、扩展码忽略、半帧超时恢复通过。
- RTL sCPU/NPC：求和 55；20000 周期独立模型比较，覆盖 reset、enable、out、非法指令、回绕。
- C 表达式：优先级、左结合、无符号回绕、寄存器/解引用、短路、非法输入和深度限制；2000 组固定种子随机 AST 对照。使用 -Wall -Wextra -Werror 及 ASan/UBSan。
- 实际 NEMU：si/info r/x/p/c/q、寄存器别名、非法参数、内存边界和客户内存更新检查通过，内置客户程序 HIT GOOD TRAP。
- NVBoard：实验六、七、十一各 100000 周期启动检查；SDL 事件注入验证 LFSR 按钮一步、A 键按下/重复/松开及数码管、SW0 启动 CPU 后十进制 55。
- 之前全部 RTL/C 回归仍通过。未重新声称学校 OJ 或 HDLBits 在线验收通过。

复现命令与限制见 [第 9–12 周说明](weeks09-12.md)。详细运行日志位于本地 build/，编译产物不提交到仓库。

# 2026-11-18：第 13–14 周追加验证

- 真实 NEMU 监视点：寄存器/内存/PC、多点触发、32 槽池、删除复用、求值异常及终止状态保护通过。
- 独立 Python 整数参考：38,602 例 RV32 运算和边界通过；UBSan 无报错。
- klib 对照宿主 libc：9,080 例通过，包含内存重叠、字符串、格式化截断；UBSan 无报错。
- 固定版本 AM cpu-tests：35 个正常用例 GOOD TRAP；wrong 必须 BAD TRAP 且非零退出，负例检查通过。
- AM 示例实际交叉编译并运行，输出 `Week14 AM: sum=5050; strings/format PASS`，以 GOOD TRAP 结束。
- PA1 原有表达式测试和 2,000 组随机 AST 对照仍通过。
- 可复现配置脚本 `bash pa2/setup.sh` 在现有环境重新执行成功。

复测命令：`make test-week13 test-week14`、`make -C pa1 test count`。详见 [第 13–14 周说明](weeks13-14.md)。本轮未改动早期 RTL/Logisim，也未重新声明其在线验收。

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

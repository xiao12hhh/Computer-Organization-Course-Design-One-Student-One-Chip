# 第 9–12 周本地参考实验

依据《26 秋组成原理课程设计·一生一芯指南》v26.01，第 9–12 周安排；实现与验证日期：2026-11-18。

这份代码由 AI 按学习者要求编写，供运行、阅读、修改和补学使用。实际功能测试已执行，不代表学习者独立掌握，也不代替学校 OJ 验收。学校题面尚未提供，仍沿用“先做本地版本”的约定。

## 第 9 周：显示、移位、状态机与键盘

### Logisim 可切换进制的七段显示

打开 `logisim/radix_display.circ`。`Value` 是 8 位无符号数，`Base` 为 0、1、2、3 时分别显示二、八、十、十六进制；`Digit0` 是最低位，`Digit7` 是最高位。为便于对照，保留前导零。

另提供 `logisim/radix_counter.circ`：`Reset` 清零，`Load` 将 `Value` 装入计数器，`Run` 使计数器在时钟上升沿加一，255 后回到 0。`Load` 优先于 `Run`；改变 `Base` 只改变显示，不改变保存的数值。单击时钟可手动推进，也可启用 Logisim 自动时钟。

进制转换使用 1024×32 ROM 查表，其输出拆成 8 个四位数码，连接真正的七段显示组件。这里没有把“计数制切换”误当作改变数值；另附计数器以便演示时序变化。若老师规定只能使用门电路或限定显示位数，需要按后续题面调整。

### NVBoard 实验六

Ubuntu 桌面打开 `Week09-Shift-LFSR`，或在仓库运行：

```bash
bash tools/run-lab.sh 6
```

- 默认显示 LFSR 伪随机序列，初始值 1。点击中间 C 按钮推进一步，L 按钮复位。低两位数码管显示十六进制值。
- SW15:14=01 时显示通用移位寄存器，SW7:0 为装入值，SW10:8 为操作号，SW11 为串行输入。每按一次 C 执行一次操作。
- 操作号 0–7 依次为：清零、装入、逻辑右移、逻辑左移、算术右移、串入右移、循环右移、循环左移。
- SW15:14=10 或 11 时显示桶形移位器；SW7:0 为输入，SW10:8 为移动位数，SW11=1 左移、0 右移，SW12=1 算术、0 逻辑。
- LFSR 反馈为 `q[4]^q[3]^q[2]^q[0]`，右移，非零序列周期为 255；零状态自动恢复为 1。

### NVBoard 实验七

打开 `Week09-Keyboard-FSM`，或运行：

```bash
bash tools/run-lab.sh 7
```

让 NVBoard 窗口获得焦点后，用电脑键盘输入字母或数字。低两位显示 PS/2 扫描码，中间两位显示小写 ASCII，高两位显示累计按键次数（十六进制，256 次回绕）。例如按 A 显示 `01 61 1C`；长按重复通码只计一次；松开后低四位熄灭。L 按钮清零。

仅实现顺序按下/松开的单键必做内容，不实现 Shift 组合键、小键盘、多键同时按下。扩展扫描码被忽略；接收器检查起始位、奇校验、停止位，并在半帧超时后重新同步。接收字节后立即消费，因此无需队列。

同一演示还包含连续四个相同位检测的 Moore 状态机：SW1 给出输入，C 按钮推进，LD0 是输出，LD7:4 是状态编号；四个连续 0 或 1 后输出为 1，重叠序列继续有效。复位使用 L 按钮，以适配 NVBoard 的按钮布局。

## 第 10 周：完整 minirv

打开 `logisim/minirv_full.circ`。这是实际由寄存器、选择器、加法器、ROM 和 RAM 构成的数据通路，支持全部八条指令：`add/addi/lui/lw/lbu/sw/sb/jalr`。

- PC 初始为 0，16 个 32 位寄存器，x0 恒为 0。
- ISA 按字节寻址，ROM/RAM 各 1 MiB，数据小端存放。
- `lbu` 从指定字节通道读出并零扩展；`sb` 只写对应通道，其他字节保持不变。
- `lw/sw` 需要四字节对齐；JALR 清除目标最低位，然后检查四字节对齐。
- 不支持的指令、x16–x31、超出内存范围的访存或跳转会置 `fault`，禁止该次状态写入；没有实现完整异常处理。
- 预装测试覆盖全部指令、四个字节通道、负立即数、x0、JALR 的 `rd==rs1`。最终 x8 为 `0x90abcdef`、a0 为 143；这个自编程序与官方验收程序的结束值不同。

官方 `mem/sum` 镜像按讲义同时装入指令 ROM 和数据 RAM。下载包固定 SHA256 为 `b31639d38b8a1b6e866894d40947d928cf626dfd3bd50ec26402819bd0df4938`，脚本会检查。

Windows 在仓库目录执行：

```powershell
python tools/fetch_minirv_programs.py
python tools/test_minirv_logisim.py
```

脚本生成 `build/minirv-logisim/minirv_mem.circ` 和 `minirv_sum.circ`，通过真实 Logisim 执行，并将每个周期的 PC、全部寄存器和故障状态与独立 Python ISA 模型比较。官方程序各运行 6000 周期：mem 的 PC=`0x121c`，sum 的 PC=`0x224`，均 a0=0。要在图形界面重新执行，应右键数据 RAM 加载相应 `build/official-minirv/*.hex`；ROM 已由生成器预装。复位寄存器不会恢复被改写的 RAM，重复验收前需重新加载 RAM。

图形显示/VGA 属于本指南不要求的 minirv 扩展，未包含。

## 第 11 周：RTL sCPU / NPC

`rtl/scpu_io.sv` 实现 4 位 PC、4 个 8 位寄存器，以及 add、li、bner0。R0 是普通可写寄存器，与 RISC-V 的 x0 不同。增加本地输出指令 `01_0000_rs`，把指定寄存器锁存到显示端口；程序的第 8 条指令 `0x42` 输出 R2。

```bash
make -C npc sim
bash tools/run-lab.sh 11
```

前一条命令运行本仓库的 NPC 仿真工程，打印状态轨迹并生成 `build/scpu-npc/scpu.vcd`，可用 GTKWave 打开。后一条启动虚拟板：打开 SW0 自动运行；低两位显示十进制 **55**，中间两位为十六进制 **37**，最高已绑定位显示 PC=8。也可关闭 SW0 后按 C 单步，按 L 复位。

本仓库 `npc/` 是可独立构建的 Verilator 工程，保留原 `~/ysyx-workbench/npc` 目录。主功能已完成，不把它表述为完整 RV32 处理器、SoC 集成或已完成综合/时序签核。

## 第 12 周：真实 PA/NEMU 调试器

基于课程 `init.sh` 指定的 NEMU `ics2024`，固定上游提交 `8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0`，部署于 `~/course-nemu`。仓库保存我们实现的源文件和可重复安装脚本，不复制整个上游历史。

桌面打开 `Week12-NEMU-Debugger`，或：

```bash
~/course-nemu/build/riscv32-nemu-interpreter
```

可直接尝试：

```text
info r
p $pc
x 4 $pc
si
p $t0
p 1 + 2 * 3
p *0x80000000
c
q
```

- `si [N]`：单步执行，默认一条；`info r`：PC 和 32 个 RV32 寄存器。
- `x N EXPR`：从表达式得到的地址读 N 个 32 位字，N 限制为 1–1024，并检查整个范围。
- `p EXPR`：支持十/十六进制、寄存器、括号、`+ - * / == != &&`，以及一元正负号和解引用 `*`。
- 数值采用 32 位无符号语义，溢出回绕；`&&` 短路。除零、未知寄存器、错误括号、越界访存会报告无效，不使调试器崩溃。
- 词法扫描与递归下降解析按优先级分层；表达式长度最多 4096，递归深度最多 128。
- 内存查询限定为 NEMU 的物理 RAM，不触发 MMIO 设备副作用。当前 PA1 还没有地址翻译。

内置客户程序执行完得到 `HIT GOOD TRAP`。这是 PA1 框架自带的小程序；未提前宣称完成第 14 周 RV32IM 指令集。监视点和 PA1 必答题按课程表属于第 13 周，未列为本次完成项。

复现安装与测试：

```bash
bash pa1/setup.sh
make -C pa1 test
python3 pa1/test_nemu.py
```

安装脚本检查固定上游版本；如果目标文件已被你修改，会停止并保留你的内容。仅移除框架 `welcome()` 中课程明确要求移除的启动练习断言，未关闭运行时断言。配置使用 RV32、native ELF，未开启设备和指令反汇编 trace。

## 总体验证与学习

Ubuntu 执行 `make test` 可运行所有已归档 RTL/C 测试；真实 NEMU 另运行上面的集成测试。Windows 的 Logisim 测试：

```powershell
python tools/generate_radix_display.py
python tools/test_radix_display.py
python tools/fetch_minirv_programs.py
python tools/test_minirv_logisim.py
```

NVBoard 不仅经过启动测试，还向实际 SDL 事件队列注入开关/按钮/键盘事件，经过 NVBoard 引脚绑定、PS/2 序列、RTL 后检查显示输出。可复现：

```bash
export NVBOARD_HOME=$HOME/ysyx-workbench/nvboard
for n in 6 7 11; do
  make -C nvboard-labs DEMO=$n
  ./build/lab-$n/demo --check $n
done
```

后续补学见 [第 9–12 周补学路线](study-weeks09-12.md)。不需要先读完整仓库；先运行一个例子，再沿数据变化追踪对应模块。

## 依据

- [NJU 实验六：移位寄存器及桶形移位器](https://nju-projectn.github.io/dlco-lecture-note/exp/06.html)
- [NJU 实验七：状态机及键盘输入](https://nju-projectn.github.io/dlco-lecture-note/exp/07.html)
- [F6：完整 minirv](https://ysyx.oscc.cc/docs/2407/f/6.html)
- [E5：RTL sCPU](https://ysyx.oscc.cc/docs/2407/e/5.html)
- [PA1：简易调试器](https://ysyx.oscc.cc/docs/ics-pa/1.4.html)、[表达式求值](https://ysyx.oscc.cc/docs/ics-pa/1.5.html)
- [NEMU ics2024](https://github.com/NJU-ProjectN/nemu/tree/ics2024)

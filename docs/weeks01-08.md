# 前八周本地实验包

更新：2026-11-13。依据《26秋组成原理课程设计_一生一芯指南》v26.01，第 9–10 页周计划（PDF 文件第 10–11 页）。

本包由 AI 根据学习者要求编写并执行本地验证，供运行、检查和后续补学。它不是学习者独立完成过程的证明。在线题库、学校 OJ 的通过记录，以及个人理解程度，均不能由本地运行代替。

## 第 1 周：环境、工具和提问方法

环境见 [environment.md](environment.md)。现在具备 Logisim、Verilator、NVBoard、GTKWave 和 Git。

F1 的核心方法：先检索问题（STFW），再查手册（RTFM），必要时读源码（RTFSC）。求助时提供操作系统、版本、最小复现、实际命令、完整错误、预期结果，以及已经尝试过的办法。例如：说明缺少哪个头文件、编译命令里的 include 路径，而不是只说“运行不了”。

F1 官方页面还列有通识问卷、报名和学习情况记录等个人平台事项；这些尚未代办，也没有记录为通过。是否属于本校必须完成的项目，应以老师要求为准。仓库进度日志记录真实发生的实现和验证，不编造学习时长或个人心得。

## 第 2 周：门电路与译码器

- `logisim/decoder24.circ`：由反相器和与门组成的 2–4 译码器。输入 A1:A0，输出 Y3:Y0 独热，高有效。
- `rtl/logic_blocks.sv` 中的 `decoder24`：同样的逻辑行为。
- `hdlbits/step_one.v`、`zero.v`、`gates4.v`：Getting Started 和四输入门的本地版本。
- 验证：译码器 4 组输入全部通过；四输入门 16 组组合全部检查。

## 第 3 周：编码器与优先编码器

- `logisim/encoder164.circ`：16–4 普通编码器，合法输入为独热或全零；全零输出 0，多位同时有效不属于普通编码器契约。
- `rtl/logic_blocks.sv` 的 `encoder164` 另提供 valid 和 multi 标志；`priority83` 为高位优先，含使能。
- `hdlbits/always_case2.v` 按该题题面使用**低位优先**，不能与高位优先版本混用。
- NVBoard `DEMO=1` 同时演示译码和高位优先编码。
- 验证：Logisim 17 组合法输入；RTL 编码器 65,536 组输入和优先编码器 512 组输入。

## 第 4 周：全加器、加减法和 ALU

- `logisim/full_adder.circ`：异或、与、或门构成的全加器，8 组组合全部通过。
- `hdlbits/module_add.v` 与 `module_addsub.v`：按题目结构串联两个 add16。在线平台提供 add16；本地等价模块仅位于测试文件中。
- `rtl/logic_blocks.sv` 的 `alu4` 与 NVBoard `DEMO=2`：4 位 ALU。

本地 ALU 操作编码为：0 加，1 减，2 按位取反 A，3 与，4 或，5 异或，6 有符号小于，7 相等。结果取 4 位；另输出 carry、overflow、zero。减法的 carry=1 表示**没有借位**。比较的结果为 0000 或 0001。

学校 OJ 的操作编码、位宽和端口尚未取得，这一契约不能直接视为 OJ 接口。ALU 对全部 16×16×8 组输入进行了检查，覆盖正负溢出、零结果和进/借位。

## 第 5 周：多路选择器

- `logisim/mux4x3.circ`：3 位四选一。S1:S0 为选择，D0_0 是第 0 路的最低位；其余命名类推。
- RTL `mux4x3` 和 NVBoard `DEMO=0` 对应此电路。
- `hdlbits/mux9to1v.v`：16 位九选一，选择值 9–15 时输出全 1，遵循题面。
- 验证：Logisim 与 RTL 四选一均覆盖 16,384 组输入；九选一检查 1,024 组数据、每组全部 16 个选择值。

## 第 6 周：状态机与数列求和

`logisim/sum10.circ` 内含两个寄存器和加法器。初态 index=0、sum=0；每次有效时钟先计算 next_index=index+1，再把它加入 sum。到 index=10 时保持结果。

实际轨迹 `(index,sum)`：

```
(0,0) (1,1) (2,3) (3,6) (4,10) (5,15)
(6,21) (7,28) (8,36) (9,45) (10,55)
```

RTL `sum10` 则用 index 表示**下一次要加的数**，复位为 1；两种 index 的含义相差一步，sum 的逐周期结果相同。测试分别按各自状态定义核对。

## 第 7 周：完整 sCPU

`logisim/scpu.circ` 是可执行的寄存器、ROM、选择器、加法器和译码电路；`rtl/sequential.sv` 另提供等价 sCPU 参考模块。

- PC 为 4 位，按指令计数；4 个通用寄存器，每个 8 位，R0 可写。
- add：操作码 00；目标、源 1、源 2 各占 2 位。
- li：操作码 10；4 位立即数零扩展后写入目标寄存器。
- bner0：操作码 11；当 R0 与指定源寄存器不等时跳到 4 位地址。
- ROM 已装入求和程序。R0=11 表示循环边界，R1 从 1 增到 11，R2 累加，R3=1。
- Logisim 的 35 个可见状态与独立 Python 指令解释器逐一比对，最终 R2=55、R1=11、PC=7。

GUI 下 PC=7 的程序会自循环，保持结果。命令行验证利用名为 halt 的输出停止仿真；halt 是测试观察信号，不是 sISA 新增指令。

## 第 8 周：两指令 minirv

`logisim/minirv2.circ` 支持 addi 和 jalr；`minirv2_edges.circ` 为同一电路装入边界测试程序。对应 RTL 为 `minirv2`。

- PC 和寄存器为 32 位，16 个通用寄存器，x0 固定为 0。
- addi 的 12 位立即数按符号扩展；运算按 32 位回绕。
- jalr 用旧源寄存器值计算目标，清除目标最低位，并将旧 PC+4 写入目标寄存器。
- 不支持的指令、超出 x0–x15 的寄存器及未按 4 字节对齐的跳转保持状态并报告错误。
- Logisim 演示 ROM 为 64 个指令字，只用于本包的小程序，不能当作完整地址空间实现。
- 调用返回测试的 a0=30、ra=12、PC=12。边界程序验证 −1、−2048、2047、回绕、x0、目标位 0 清除与 rd=rs1。

第 8 周的两个基础指令按官方 F6 的阶段划分选取。完整八指令 minirv（add、addi、lui、lw、lbu、sw、sb、jalr）在指南第 10 周安排实现，本包没有将两指令版本标成完整八指令处理器。

## 运行与复现

Windows：用 Logisim 打开 `logisim` 下的 `.circ`。时序电路可以在 Simulate 菜单开启时钟；Reset 输入置 1 再置 0 可复位。

Windows 自动检查：

```powershell
python tools/generate_logisim.py
python tools/generate_processors.py
python tools/test_logisim.py --exe D:\Logisim\logisim-evolution.exe
```

Ubuntu：

```bash
cd ~/course-week8-work
make test
bash tools/run-nvboard.sh 0  # 选择器
bash tools/run-nvboard.sh 1  # 译码/编码
bash tools/run-nvboard.sh 2  # ALU
bash tools/run-nvboard.sh 3  # 流水灯
```

NVBoard 开关：模式 0 用 SW0–2、3–5、6–8、9–11 分别输入四路数据，SW12–13 选择；模式 1 用 SW0–7 输入优先编码器、SW8 使能，SW9–10 输入译码器，LD0–2 为编码、LD3 为有效、LD8–11 为译码；模式 2 用 SW0–3 输入 A、SW4–7 输入 B、SW8–10 输入操作码，LD0–3 为结果、LD4 carry、LD5 overflow、LD6 zero。SEG0 显示结果数字。

测试日志和生成波形位于 `build/`，不提交大体积生成物。

## 尚待本人或平台完成

- HDLBits 和学校 OJ 的线上提交、评分结果尚未取得。当前仅声明本地测试通过。
- F1 个人问卷、注册/学习记录等事项没有代办。
- 老师口头或另行发布的改错题、简答题若未包含在现有指南中，仍需取得题目后核对。
- 补学后独立解释和修改电路；本地实验包不等于已经掌握知识。

## 对照资料

- [官方 F1](https://ysyx.oscc.cc/docs/2407/f/1.html)
- [官方 F3 数字逻辑基础](https://ysyx.oscc.cc/docs/2407/f/3.html)
- [官方 F4 状态机](https://ysyx.oscc.cc/docs/2407/f/4.html)
- [官方 F5 sCPU](https://ysyx.oscc.cc/docs/2407/f/5.html)
- [官方 F6 minirv](https://ysyx.oscc.cc/docs/2407/f/6.html)
- [HDLBits 题目索引](https://hdlbits.01xz.net/wiki/Problem_sets)

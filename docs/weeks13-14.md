# 第 13–14 周本地参考实验

依据课程指南 v26.01 第 13–14 周安排；实现与验证日期：2026-11-18。代码与参考解答由 AI 按学习者要求编写，供运行、阅读和修改。学习者尚需补学、独立解释；未提交学校 OJ，未代填个人问卷或冒充个人实验报告。

## 已实现的内容

第 13 周：真实 NEMU 中的 32 槽监视点池，活动链表与空闲链表；`w EXPR` 创建、`info w` 查看、`d N` 删除。每执行一条指令后重新计算表达式，变化时显示旧值、新值、PC 并暂停；表达式失效也暂停。多个监视点同时触发时全部报告；池满或删除不存在的编号不会崩溃。GOOD/BAD TRAP、ABORT 的终止状态不会被监视点覆盖。正常 `q`/EOF 返回成功，但不把已有失败伪装成成功。

第 14 周：在真实 NEMU 的 `isa_exec_once` 中接入 `pa2/rv32.c`：整数算术、逻辑、移位、比较、跳转、分支、字节/半字/字访存及符号扩展、全部八条 M 扩展指令。x0 恒为零，JALR 清最低位；乘法高位使用 64 位中间值；有符号除法按向零截断，处理除零与 INT_MIN/-1。

AM 环境包括交叉编译器、启动代码、链接脚本、klib 和 NEMU 批处理运行。实现 strlen/strcpy/strncpy/strcat/strcmp/strncmp/memset/memcpy/memmove/memcmp/strchr/strrchr，以及 printf/vprintf/sprintf/vsprintf/snprintf/vsnprintf。串口采用 NEMU 自带设备，把 `putch` 输出送到终端。示例计算 1 到 100 的和，检查字符串、格式化和缓冲区截断，最后输出 `sum=5050; strings/format PASS` 并 GOOD TRAP。

## 现在怎样打开

Ubuntu 桌面可用 `Week13-Watchpoints` 打开调试器，`Week14-AM-Demo` 运行示例。也可在终端执行：

```bash
cd ~/course-week8-work
source pa2/env.sh
~/course-nemu/build/riscv32-nemu-interpreter
```

然后逐行尝试：

```text
w $t0
w *0x80000010
info w
c
p $pc
c
d 0
d 1
c
q
```

`w` 后面是表达式，`d` 后面是 `info w` 显示的编号。`si N` 也会受监视点影响：某一条指令触发时立即停下，不保证执行满 N 条。

运行 AM 示例与测试：

```bash
cd ~/course-week8-work
source pa2/env.sh
python3 pa2/test_demo.py
make test-week13 test-week14
make -C pa1 test count
```

## 如何复现环境

现有虚拟机已配置完成，无需重复下载。新 Ubuntu 22.04 环境先安装课程基础编译依赖（git、make、GCC、readline、SDL2 等），再运行 `bash pa2/setup.sh`。脚本会下载缺少的依赖仓库、检查固定提交、安装补丁并编译 NEMU；未知用户改动会保留并报错。

- NEMU ics2024：`8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0`。
- Abstract Machine ics2026：`9bc0a93c52c928a6de970f39a507be94cfb63a9f`。
- am-kernels ics2026：`9c433f7cf4b4e05d09543bf7e269b23502d1b2b6`。
- 交叉 GCC：Ubuntu 11.4.0，binutils 2.38；安装在 `~/course-tools/riscv`，没有覆盖系统 GCC。

本地工具链从 Ubuntu 软件包解包，不需 root。`pa2/env.sh` 设置 PATH 和动态库搜索路径；GCC 包装器使用 `-ffreestanding -nostdinc`，仅包含编译器内建头文件及项目的整数 limits.h，避免把 x86 宿主 libc 的头文件用于 RV32 裸机。这里的 libc 由 AM klib 提供。AM 的编译参数含 `rv32im_zicsr`，但本阶段链接掉未使用的异常/CSR 代码，实际被测程序无需 CSR 指令。

## 验证与范围

- 监视点：寄存器、内存、PC 条件、多点同时触发、32 槽耗尽、删除复用、非法表达式、运行期间求值失败和结束状态保护通过。
- RV32 独立 Python 大整数参考：38,602 例通过，包含全部 M 指令、除零、符号边界、溢出、移位、立即数、访存及 JALR；C 核心启用 UBSan。
- AM 官方 cpu-tests：36 个程序实际编译并执行。35 个 GOOD TRAP；`wrong` 是故意出错的负例，必须 BAD TRAP 且非零退出才算测试通过。没有把上游包装 Makefile 的成功退出当成程序通过。
- klib：9,080 例与宿主 libc 对照，覆盖重叠内存、字节符号、字符串和格式化截断；启用 UBSan。
- 真实 RV32 AM 示例完成 printf 串口输出、字符串与 sprintf/snprintf 检查、5050 求和、GOOD TRAP。
- 之前的表达式单元测试及 2,000 组随机表达式回归通过。

这是课程当前阶段的整数执行环境，不是完整特权架构实现：ECALL、CSR、异常处理、分页未实现；EBREAK 用作 NEMU 退出约定。FENCE 在顺序单核模型中无操作，FENCE.I 不在本次范围。未声明 RISC-V 官方架构认证通过。

格式化支持 `%s %c %d %i %u %x %X %p %%`、字段宽度、左对齐和零填充；不支持浮点、精度和长度修饰符，遇到不支持的格式返回 -1。`memcpy` 与标准语义一致，不允许重叠；重叠用 `memmove`。AM 上游的动态分配等后续占位函数没有被宣称完成。第 15–16 周的 RTL NPC、MMIO 图形程序不属于本次完成范围。

## 补学与参考

先读 [补学清单](study-weeks13-14.md)，再按 [PA1 必答题参考](pa1-answers.md) 自己解释和修改。官方资料：[监视点](https://ysyx.oscc.cc/docs/ics-pa/1.6.html)、[D1](https://ysyx.oscc.cc/docs/2407/d/1.html)、[D3](https://ysyx.oscc.cc/docs/2407/d/3.html)。

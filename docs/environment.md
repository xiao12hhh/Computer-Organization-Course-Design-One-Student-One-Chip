# 环境配置记录

验证日期：2026-11-11。此记录来自实际安装和运行结果。

## 主机与虚拟机

- 主机：Windows，VMware Workstation。
- 虚拟机：Ubuntu 22.04.5 LTS，64 位。
- 虚拟机分配：4 个 CPU 核心、6 GB 内存、80 GB 虚拟磁盘、NAT 网络。
- Logisim-evolution 在 Windows 使用；已由学习者完成第一个简单电路。

## 开发工具

- Verilator：5.054，输出为 `Verilator 5.054 2026-11-01 rev v5.054-62-ge4c94116f`。
- GTKWave：3.3.104。
- Git：2.34.1。
- SDL2：2.0.20；SDL2_image：2.0.5；SDL2_ttf：2.0.18。
- GCC/G++、Make、GDB、Python3、pkg-config 以及 Verilator 构建依赖已安装。
- VMware Tools 服务及桌面集成进程运行正常。

## 目录与环境变量

Ubuntu 中：

- 课程工作目录：`~/ysyx-workbench`。
- NPC：`~/ysyx-workbench/npc`。
- NVBoard：`~/ysyx-workbench/nvboard`。
- Verilator 源码：`~/verilator`。
- Verilator 安装入口：`/usr/local/bin/verilator`。
- 官方验证示例、波形及日志：`~/course-environment-checks`。

`NPC_HOME` 与 `NVBOARD_HOME` 已写入 Ubuntu 用户的 `~/.bashrc`，新终端自动加载。可以检查：

```bash
echo "$NPC_HOME"
echo "$NVBOARD_HOME"
verilator --version
```

此 GitHub 仓库用于归档课程成果；它与现有的 `ysyx-workbench` 工作目录是两个独立仓库。当前没有更改课程框架的 Git 远端，也没有将其现有源码复制到本仓库。

## 已解决的问题

1. APT 提示上次软件安装被中断：完成 `dpkg --configure -a`，随后安装依赖；最终 `dpkg --audit` 无问题输出。
2. NVBoard 构建缺少 `SDL_image.h`：安装 `libsdl2-image-dev` 和 `libsdl2-ttf-dev`，构建通过。
3. 为官方演示建立桌面启动入口，减少重复输入命令。

## 实际验证

- Verilator 官方 `make_hello_c` 编译成功，运行输出 `Hello World!`。
- Verilator 官方 `make_tracing_c` 编译运行成功，生成 `logs/vlt_dump.vcd`。
- GTKWave 加载该 VCD，并显示时钟、复位、计数等信号。
- NVBoard 官方 `example` 编译成功，图形窗口正常启动。
- 不同时刻的运行画面中，LED 位置和数码管数字发生变化；VGA 图片正常显示。
- 新 Bash 终端能读取正确的 `NPC_HOME` 和 `NVBOARD_HOME`。

## 日常启动

Ubuntu 桌面：

- **NVBoard Official Example**：运行官方虚拟板示例。
- **GTKWave Official Example**：查看已生成的官方示例波形。
- **ysyx-workbench**：打开课程工作目录。
- **课程环境使用说明.txt**：本机使用说明。

也可以在 Ubuntu 终端运行：

```bash
cd "$NVBOARD_HOME/example"
make run
```

退出时先保存文件，再在 Ubuntu 中正常关机。若提示 APT 正在安装软件，等待安装完成后再关机。

## 验证范围

以上证明开发环境和官方示例可以工作，不代表已经独立完成课程流水灯设计或其他实验。自己的电路、源码与报告将在实际完成后分别归档。

本次配置的临时 SSH 授权已移除；密钥、主机登录信息、虚拟机镜像和安装包不上传。

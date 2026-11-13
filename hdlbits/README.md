# HDLBits 本地练习

每个 `.v` 文件独立定义 `top_module`，不能把所有文件直接一起交给平台编译。测试脚本只在 build 目录中重命名模块，以便本地统一验证。

题面对应：

- [step_one](https://hdlbits.01xz.net/wiki/Step_one)
- [zero](https://hdlbits.01xz.net/wiki/Zero)
- [gates4](https://hdlbits.01xz.net/wiki/Gates4)
- [always_case2](https://hdlbits.01xz.net/wiki/Always_case2)：低位优先。
- [module_add](https://hdlbits.01xz.net/wiki/Module_add)：课程表里的 Adder 1。
- [module_addsub](https://hdlbits.01xz.net/wiki/Module_addsub)
- [mux9to1v](https://hdlbits.01xz.net/wiki/Mux9to1v)：非法选择值输出全 1。

`add16` 由在线平台提供；`tests/tb_hdlbits.sv` 中的版本仅供本地仿真。当前文件已经通过本地测试，尚无在线平台评分记录。

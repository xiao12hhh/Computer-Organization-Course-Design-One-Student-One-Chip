VERILATOR ?= verilator
.PHONY: test test-logic test-sequential test-hdlbits
.PHONY: test-week13 test-week14
test-week13:
	python3 pa1/test_nemu.py
	python3 pa1/test_watchpoints.py
test-week14:
	bash -c 'source pa2/env.sh; python3 pa2/test_rv32.py && python3 pa2/test_klib.py && python3 pa2/test_cpu.py && python3 pa2/test_demo.py'
test: test-logic test-sequential test-hdlbits test-week09 test-week11 test-pa1

.PHONY: test-week11 test-pa1
test-week11:
	$(MAKE) -C npc test
test-pa1:
	$(MAKE) -C pa1 test

.PHONY: test-week09
test-week09:
	mkdir -p build
	$(VERILATOR) --binary --timing --assert -Wno-DECLFILENAME --top-module tb_week09 --Mdir build/week09 rtl/week09.sv tests/tb_week09.sv
	./build/week09/Vtb_week09
test-logic:
	mkdir -p build
	$(VERILATOR) --binary --timing --assert -Wno-DECLFILENAME -Wno-WIDTHEXPAND --top-module tb_logic --Mdir build/logic rtl/logic_blocks.sv tests/tb_logic.sv
	./build/logic/Vtb_logic
test-sequential:
	mkdir -p build
	$(VERILATOR) --binary --timing --assert --trace -Wno-DECLFILENAME -Wno-WIDTHEXPAND --top-module tb_sequential --Mdir build/sequential rtl/sequential.sv tests/tb_sequential.sv
	./build/sequential/Vtb_sequential
test-hdlbits:
	python3 tools/prepare_hdlbits.py
	$(VERILATOR) --binary --timing --assert -Wno-DECLFILENAME -Wno-WIDTHEXPAND --top-module tb_hdlbits --Mdir build/hdlbits build/hdlbits-src/*.v tests/tb_hdlbits.sv
	./build/hdlbits/Vtb_hdlbits

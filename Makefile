VERILATOR ?= verilator
.PHONY: test test-logic test-sequential test-hdlbits
test: test-logic test-sequential test-hdlbits
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

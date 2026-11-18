.DEFAULT_GOAL := sim
BUILD := $(abspath ../build/scpu-npc)
$(BUILD)/scpu: ../rtl/scpu_io.sv main.cpp
	mkdir -p $(BUILD)
	verilator --cc --exe --build --trace --top-module scpu_io -Wno-DECLFILENAME --Mdir $(BUILD)/obj $(abspath ../rtl/scpu_io.sv main.cpp) -o $@
.PHONY: sim test
sim test: $(BUILD)/scpu
	cd .. && ./build/scpu-npc/scpu

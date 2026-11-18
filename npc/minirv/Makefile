.DEFAULT_GOAL := build
ROOT := $(abspath ../..)
BUILD := $(ROOT)/build/minirv-npc
SOURCES := top.sv decode.sv regfile.sv main.cpp
.PHONY: build run
build: $(BUILD)/npc
$(BUILD)/reference.o: $(ROOT)/pa2/rv32.c $(ROOT)/pa2/rv32.h
	mkdir -p $(BUILD)
	cc -O2 -c $(ROOT)/pa2/rv32.c -o $@
$(BUILD)/npc: $(SOURCES) $(BUILD)/reference.o
	verilator --cc --exe --build --trace --top-module minirv_top --Mdir $(BUILD)/obj -Wno-DECLFILENAME -CFLAGS '-O2 -std=c++17' $(abspath $(SOURCES)) $(BUILD)/reference.o -o $@
run: build
	$(BUILD)/npc $(ARGS) $(IMG)

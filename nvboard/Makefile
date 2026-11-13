NVBOARD_HOME ?= $(HOME)/ysyx-workbench/nvboard
export NVBOARD_HOME
DEMO ?= 0
BUILD_DIR := $(abspath ../build/nvboard-$(DEMO))
VERILATOR ?= verilator
.DEFAULT_GOAL := all
include $(NVBOARD_HOME)/scripts/nvboard.mk
$(BUILD_DIR)/auto_bind.cpp: top.nxdc
	mkdir -p $(BUILD_DIR)
	python3 $(NVBOARD_HOME)/scripts/auto_pin_bind.py $< $@
$(BUILD_DIR)/demo: board_top.sv main.cpp ../rtl/logic_blocks.sv ../rtl/sequential.sv $(BUILD_DIR)/auto_bind.cpp $(NVBOARD_ARCHIVE)
	$(VERILATOR) --cc --exe --build --top-module board_top -GDEMO=$(DEMO) -Wno-DECLFILENAME --Mdir $(BUILD_DIR)/obj_dir $(abspath board_top.sv main.cpp ../rtl/logic_blocks.sv ../rtl/sequential.sv) $(BUILD_DIR)/auto_bind.cpp $(NVBOARD_ARCHIVE) -CFLAGS "-I$(NVBOARD_HOME)/usr/include" -LDFLAGS "$(LDFLAGS)" -o $(BUILD_DIR)/demo
.PHONY: all run
all: $(BUILD_DIR)/demo
run: all
	$(BUILD_DIR)/demo

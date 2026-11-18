NVBOARD_HOME ?= $(HOME)/ysyx-workbench/nvboard
export NVBOARD_HOME
DEMO ?= 6
BUILD_DIR := $(abspath ../build/lab-$(DEMO))
.DEFAULT_GOAL := all
include $(NVBOARD_HOME)/scripts/nvboard.mk
$(BUILD_DIR)/auto_bind.cpp: top.nxdc
	mkdir -p $(BUILD_DIR)
	python3 $(NVBOARD_HOME)/scripts/auto_pin_bind.py $< $@
$(BUILD_DIR)/demo: lab_top.sv main.cpp ../rtl/week09.sv ../rtl/scpu_io.sv $(BUILD_DIR)/auto_bind.cpp $(NVBOARD_ARCHIVE)
	verilator --cc --exe --build --top-module lab_top -GDEMO=$(DEMO) -Wno-DECLFILENAME --Mdir $(BUILD_DIR)/obj_dir $(abspath lab_top.sv main.cpp ../rtl/week09.sv ../rtl/scpu_io.sv) $(BUILD_DIR)/auto_bind.cpp $(NVBOARD_ARCHIVE) -CFLAGS "-I$(NVBOARD_HOME)/usr/include $(shell sdl2-config --cflags)" -LDFLAGS "$(LDFLAGS)" -o $(BUILD_DIR)/demo
.PHONY: all run
all: $(BUILD_DIR)/demo
run: all
	$(BUILD_DIR)/demo

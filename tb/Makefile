SIM ?= verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/../rtl/alu.sv
COCOTB_TOPLEVEL = alu
COCOTB_TEST_MODULES = test_alu
EXTRA_ARGS += --trace --trace-structs
WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim
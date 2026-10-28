SIM ?= verilator
TOPLEVEL_LANG = verilog
EXTRA_ARGS += --trace --trace-structs
WAVES = 1

# list of modules to test; each needs rtl/<name>.sv and tb/test_<name>.py
MODULES = alu regfile imm_gen decoder mem

ifneq ($(MOD),)

VERILOG_SOURCES = $(CURDIR)/../rtl/$(MOD).sv
COCOTB_TOPLEVEL = $(MOD)
COCOTB_TEST_MODULES = test_$(MOD)
SIM_BUILD = sim_build_$(MOD)
include $(shell cocotb-config --makefiles)/Makefile.sim

else

.PHONY: test clean_all
test:
	@for m in $(MODULES); do \
		echo "=== $$m ==="; \
		$(MAKE) MOD=$$m || exit 1; \
	done
	@echo "ALL TESTS PASSED"

clean_all:
	rm -rf sim_build_* sim_build results.xml dump.vcd dump.fst __pycache__

endif
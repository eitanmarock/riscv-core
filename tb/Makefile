SIM ?= verilator
TOPLEVEL_LANG = verilog
EXTRA_ARGS += --trace --trace-structs
WAVES = 1

# list of modules to test; each needs tb/test_<name>.py
MODULES = alu regfile imm_gen decoder mem branch_cmp core

# modules that need more RTL files than their own
SRCS_core = core mem decoder imm_gen regfile alu branch_cmp

ifneq ($(MOD),)

SRCS = $(if $(SRCS_$(MOD)),$(SRCS_$(MOD)),$(MOD))
VERILOG_SOURCES = $(foreach s,$(SRCS),$(CURDIR)/../rtl/$(s).sv)
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
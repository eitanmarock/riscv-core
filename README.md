# RV32I Core in SystemVerilog, verified with cocotb

A single-cycle RISC-V (RV32I subset) processor core written in SystemVerilog,
with a self-checking Python verification environment built on
[cocotb](https://www.cocotb.org/) and [Verilator](https://www.veripool.org/verilator/).

No FPGA board is needed: everything is built and verified in simulation on Linux.

## Status

Work in progress. Currently implemented and tested:

| Area | Instructions |
|---|---|
| Arithmetic / logic (R-type) | ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND |
| Arithmetic / logic (I-type) | ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI |
| Memory | LW, SW |
| Control flow | BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL |

Not implemented yet: LUI, AUIPC, JALR, byte/halfword loads and stores,
CSRs, interrupts.

## Architecture

```
            +-----------------------------------------+
  pc -----> | instruction memory --> decoder          |
            |        |                 | control      |
            |        v                 v              |
            |   register file --> ALU --> data memory |
            |        ^   imm_gen --^         |        |
            |        +-----------------------+        |
            +-----------------------------------------+
```

| Module | File | Role |
|---|---|---|
| `alu` | `rtl/alu.sv` | Arithmetic, logic, shifts, comparisons |
| `regfile` | `rtl/regfile.sv` | 32 registers, 2 read ports, 1 write port, x0 hardwired to 0 |
| `imm_gen` | `rtl/imm_gen.sv` | Extracts and sign-extends the immediate (I, S, B, U, J formats) |
| `decoder` | `rtl/decoder.sv` | Turns an instruction into control signals |
| `branch_cmp` | `rtl/branch_cmp.sv` | Evaluates branch conditions |
| `mem` | `rtl/mem.sv` | Word memory, used for both instructions and data |
| `core` | `rtl/core.sv` | Top level: program counter and wiring |

## Verification approach

Every module has a cocotb testbench in `tb/`. The testbenches drive thousands
of random inputs (plus corner values such as `0`, `0x7FFFFFFF`, `0x80000000`,
`0xFFFFFFFF`) and compare every output against an independent
reference model written in Python.

- Combinational modules (`alu`, `imm_gen`, `decoder`, `branch_cmp`): random
  stimulus checked against a Python model.
- Sequential modules (`regfile`, `mem`): clocked random reads and writes
  checked against a Python copy of the state.
- `core`: small assembled programs (arithmetic, load/store, a loop summing
  1..5, JAL) executed on the core, with final register and memory contents
  checked.

## Running the tests

Requirements: Linux, Python 3, Verilator 5.x, cocotb 2.x.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install cocotb pytest

cd tb
make test          # runs every module's tests
make MOD=alu       # runs a single module
make clean_all     # removes build output
```

Waveforms are written as `.vcd` / `.fst` files and can be opened with GTKWave.

## Repository layout

```
rtl/   SystemVerilog source
tb/    cocotb testbenches, Makefile, test programs
docs/  documentation
```

## Roadmap

- [ ] LUI, AUIPC, JALR
- [ ] Byte and halfword loads and stores
- [ ] Cross-check against Spike (official RISC-V ISA simulator) instruction by instruction
- [ ] Run the official riscv-arch-test suite
- [ ] 5-stage pipeline with hazard detection and forwarding
- [ ] Functional coverage and SystemVerilog assertions
- [ ] GitHub Actions CI running `make test` on every commit
- [ ] Synthesis results (area / frequency) with Yosys

## Author

Eitan Marock, B.Sc. Electrical and Electronics Engineering, Ariel University.
[LinkedIn](https://www.linkedin.com/in/eitan-marock/)
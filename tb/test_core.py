import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


def r_type(f7, rs2, rs1, f3, rd):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0b0110011


def addi(rd, rs1, imm):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (0b000 << 12) | (rd << 7) | 0b0010011


def lw(rd, rs1, imm):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (0b010 << 12) | (rd << 7) | 0b0000011


def sw(rs2, rs1, imm):
    imm &= 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (0b010 << 12) | ((imm & 0x1F) << 7) | 0b0100011


def add(rd, rs1, rs2):
    return r_type(0b0000000, rs2, rs1, 0b000, rd)


def sub(rd, rs1, rs2):
    return r_type(0b0100000, rs2, rs1, 0b000, rd)


def beq(rs1, rs2, offset):
    o = offset & 0x1FFF
    return (((o >> 12) & 1) << 31) | (((o >> 5) & 0x3F) << 25) | (rs2 << 20) | \
           (rs1 << 15) | (0b000 << 12) | (((o >> 1) & 0xF) << 8) | \
           (((o >> 11) & 1) << 7) | 0b1100011


def bne(rs1, rs2, offset):
    return (beq(rs1, rs2, offset) & ~(0b111 << 12)) | (0b001 << 12)


def jal(rd, offset):
    o = offset & 0x1FFFFF
    return (((o >> 20) & 1) << 31) | (((o >> 1) & 0x3FF) << 21) | \
           (((o >> 11) & 1) << 20) | (((o >> 12) & 0xFF) << 12) | (rd << 7) | 0b1101111


async def run_program(dut, program, cycles=8):
    # clear instruction memory, then load the program
    for i in range(256):
        dut.imem.words[i].value = 0
    for i in range(32):
        dut.rf.regs[i].value = 0
    for i in range(256):
        dut.dmem.words[i].value = 0    
    for i, word in enumerate(program):
        dut.imem.words[i].value = word

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


def reg(dut, n):
    return int(dut.rf.regs[n].value)


@cocotb.test()
async def core_arith(dut):
    await run_program(dut, [
        addi(1, 0, 5),      # x1 = 5
        addi(2, 0, 10),     # x2 = 10
        add(3, 1, 2),       # x3 = 15
        sub(4, 1, 2),       # x4 = -5
    ])
    assert reg(dut, 1) == 5
    assert reg(dut, 2) == 10
    assert reg(dut, 3) == 15
    assert reg(dut, 4) == 0xFFFFFFFB, f"x4 = {reg(dut, 4):#x}"


@cocotb.test()
async def core_load_store(dut):
    await run_program(dut, [
        addi(1, 0, 5),      # x1 = 5
        addi(2, 0, 10),     # x2 = 10
        sw(2, 0, 8),        # mem[8] = x2  (word number 2)
        lw(3, 0, 8),        # x3 = mem[8]  -> 10
        add(4, 3, 1),       # x4 = 10 + 5  -> 15
        sw(4, 0, 12),       # mem[12] = x4 (word number 3)
    ])
    assert int(dut.dmem.words[2].value) == 10
    assert int(dut.dmem.words[3].value) == 15
    assert reg(dut, 3) == 10, f"x3 = {reg(dut, 3)}"
    assert reg(dut, 4) == 15, f"x4 = {reg(dut, 4)}"



@cocotb.test()
async def core_loop(dut):
    # sum = 5 + 4 + 3 + 2 + 1 using a loop
    await run_program(dut, [
        addi(1, 0, 5),      # 0:  x1 = 5 (counter)
        addi(2, 0, 0),      # 4:  x2 = 0 (sum)
        add(2, 2, 1),       # 8:  loop: x2 += x1
        addi(1, 1, -1),     # 12: x1 -= 1
        bne(1, 0, -8),      # 16: if x1 != 0 jump back to 8
        addi(3, 0, 99),     # 20: x3 = 99 (after the loop)
    ], cycles=20)
    assert reg(dut, 2) == 15, f"sum = {reg(dut, 2)}"
    assert reg(dut, 1) == 0
    assert reg(dut, 3) == 99


@cocotb.test()
async def core_jal(dut):
    await run_program(dut, [
        jal(1, 8),          # 0: x1 = 4 (return address), jump to 8
        addi(2, 0, 111),    # 4: skipped
        addi(3, 0, 7),      # 8: x3 = 7
    ], cycles=6)
    assert reg(dut, 1) == 4, f"x1 = {reg(dut, 1)}"
    assert reg(dut, 2) == 0, "skipped instruction executed"
    assert reg(dut, 3) == 7    
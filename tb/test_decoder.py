import random
import cocotb
from cocotb.triggers import Timer

# (name, funct3, funct7, expected alu_op)
R_OPS = [
    ("ADD", 0b000, 0b0000000, 0), ("SUB", 0b000, 0b0100000, 1),
    ("SLL", 0b001, 0b0000000, 2), ("SLT", 0b010, 0b0000000, 3),
    ("SLTU", 0b011, 0b0000000, 4), ("XOR", 0b100, 0b0000000, 5),
    ("SRL", 0b101, 0b0000000, 6), ("SRA", 0b101, 0b0100000, 7),
    ("OR", 0b110, 0b0000000, 8), ("AND", 0b111, 0b0000000, 9),
]

I_OPS = [
    ("ADDI", 0b000, None, 0), ("SLLI", 0b001, 0b0000000, 2),
    ("SLTI", 0b010, None, 3), ("SLTIU", 0b011, None, 4),
    ("XORI", 0b100, None, 5), ("SRLI", 0b101, 0b0000000, 6),
    ("SRAI", 0b101, 0b0100000, 7), ("ORI", 0b110, None, 8),
    ("ANDI", 0b111, None, 9),
]


def r_type(funct7, rs2, rs1, funct3, rd):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0b0110011


def i_type(imm12, rs1, funct3, rd):
    return ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0b0010011


async def check(dut, instr, reg_write, alu_src, alu_op, valid, what,
                mem_write=0, mem_to_reg=0):
    dut.instr.value = instr
    await Timer(1, unit="ns")
    got = (int(dut.reg_write.value), int(dut.alu_src.value),
           int(dut.alu_op.value), int(dut.valid.value),
           int(dut.mem_write.value), int(dut.mem_to_reg.value))
    exp = (reg_write, alu_src, alu_op, valid, mem_write, mem_to_reg)
    assert got == exp, f"{what} instr={instr:#010x}: got {got}, expected {exp}"


@cocotb.test()
async def decoder_supported(dut):
    for _ in range(2000):
        rd, rs1, rs2 = (random.randint(0, 31) for _ in range(3))
        name, f3, f7, op = random.choice(R_OPS)
        await check(dut, r_type(f7, rs2, rs1, f3, rd), 1, 0, op, 1, name)

        name, f3, f7, op = random.choice(I_OPS)
        if f7 is None:
            imm = random.getrandbits(12)
        else:                       # shifts: shamt in low 5 bits, funct7 on top
            imm = (f7 << 5) | random.getrandbits(5)
        await check(dut, i_type(imm, rs1, f3, rd), 1, 1, op, 1, name)


@cocotb.test()
async def decoder_memory(dut):
    for _ in range(500):
        rd, rs1, rs2 = (random.randint(0, 31) for _ in range(3))
        imm = random.getrandbits(12)
        lw = ((imm << 20) | (rs1 << 15) | (0b010 << 12) | (rd << 7) | 0b0000011)
        sw = (((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) |
              (0b010 << 12) | ((imm & 0x1F) << 7) | 0b0100011)
        await check(dut, lw, 1, 1, 0, 1, "LW", mem_write=0, mem_to_reg=1)
        await check(dut, sw, 0, 1, 0, 1, "SW", mem_write=1, mem_to_reg=0)

        # other widths (LB, LH, SB, SH...) are not supported yet
        bad_f3 = random.choice([0b000, 0b001, 0b100, 0b101])
        await check(dut, (lw & ~(0b111 << 12)) | (bad_f3 << 12),
                    0, 0, 0, 0, "LOAD bad funct3")
        bad_f3 = random.choice([0b000, 0b001])
        await check(dut, (sw & ~(0b111 << 12)) | (bad_f3 << 12),
                    0, 0, 0, 0, "STORE bad funct3")


@cocotb.test()
async def decoder_unsupported(dut):
    # BRANCH, JAL, JALR are not implemented yet
    for opcode in (0b1100011, 0b1101111, 0b1100111):
        for _ in range(100):
            instr = (random.getrandbits(25) << 7) | opcode
            await check(dut, instr, 0, 0, 0, 0, f"opcode={opcode:#09b}")
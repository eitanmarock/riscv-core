import random
import cocotb
from cocotb.triggers import Timer


def sext(value, bits):
    value &= (1 << bits) - 1
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value & 0xFFFFFFFF


def bits(x, hi, lo):
    return (x >> lo) & ((1 << (hi - lo + 1)) - 1)


def model(instr):
    opcode = instr & 0x7F
    if opcode in (0b0010011, 0b0000011, 0b1100111):
        return sext(bits(instr, 31, 20), 12)
    if opcode == 0b0100011:
        return sext((bits(instr, 31, 25) << 5) | bits(instr, 11, 7), 12)
    if opcode == 0b1100011:
        v = (bits(instr, 31, 31) << 12) | (bits(instr, 7, 7) << 11) | \
            (bits(instr, 30, 25) << 5) | (bits(instr, 11, 8) << 1)
        return sext(v, 13)
    if opcode in (0b0110111, 0b0010111):
        return (instr & 0xFFFFF000)
    if opcode == 0b1101111:
        v = (bits(instr, 31, 31) << 20) | (bits(instr, 19, 12) << 12) | \
            (bits(instr, 20, 20) << 11) | (bits(instr, 30, 21) << 1)
        return sext(v, 21)
    return 0


@cocotb.test()
async def imm_random(dut):
    opcodes = [0b0010011, 0b0000011, 0b1100111, 0b0100011,
               0b1100011, 0b0110111, 0b0010111, 0b1101111, 0b0110011]
    for _ in range(5000):
        instr = (random.getrandbits(25) << 7) | random.choice(opcodes)
        dut.instr.value = instr
        await Timer(1, unit="ns")
        got = int(dut.imm.value)
        exp = model(instr)
        assert got == exp, f"instr={instr:#010x}: got {got:#x}, expected {exp:#x}"
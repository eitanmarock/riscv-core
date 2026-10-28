import random
import cocotb
from cocotb.triggers import Timer


def signed(x):
    return x - (1 << 32) if x & 0x80000000 else x


def model(f3, a, b):
    if f3 == 0b000: return int(a == b)
    if f3 == 0b001: return int(a != b)
    if f3 == 0b100: return int(signed(a) < signed(b))
    if f3 == 0b101: return int(signed(a) >= signed(b))
    if f3 == 0b110: return int(a < b)
    if f3 == 0b111: return int(a >= b)
    return 0


@cocotb.test()
async def branch_random(dut):
    corners = [0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]
    for _ in range(5000):
        f3 = random.choice([0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111])
        a = random.choice(corners + [random.getrandbits(32)])
        # make equal operands common, otherwise BEQ is almost never taken
        b = a if random.random() < 0.2 else random.choice(corners + [random.getrandbits(32)])
        dut.a.value = a
        dut.b.value = b
        dut.funct3.value = f3
        await Timer(1, unit="ns")
        got = int(dut.taken.value)
        exp = model(f3, a, b)
        assert got == exp, f"f3={f3:03b} a={a:#x} b={b:#x}: got {got}, expected {exp}"
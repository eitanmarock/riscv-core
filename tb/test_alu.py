import random
import cocotb
from cocotb.triggers import Timer

MASK = 0xFFFFFFFF

def signed(x):
    return x - (1 << 32) if x & 0x80000000 else x

def model(op, a, b):
    sh = b & 0x1F
    if op == 0: return (a + b) & MASK
    if op == 1: return (a - b) & MASK
    if op == 2: return (a << sh) & MASK
    if op == 3: return int(signed(a) < signed(b))
    if op == 4: return int(a < b)
    if op == 5: return a ^ b
    if op == 6: return a >> sh
    if op == 7: return (signed(a) >> sh) & MASK
    if op == 8: return a | b
    if op == 9: return a & b

@cocotb.test()
async def alu_random(dut):
    corners = [0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]
    for _ in range(5000):
        op = random.randint(0, 9)
        a = random.choice(corners + [random.getrandbits(32)])
        b = random.choice(corners + [random.getrandbits(32)])
        dut.a.value = a
        dut.b.value = b
        dut.op.value = op
        await Timer(1, unit="ns")
        got = int(dut.y.value)
        exp = model(op, a, b)
        assert got == exp, f"op={op} a={a:#x} b={b:#x}: got {got:#x}, expected {exp:#x}"
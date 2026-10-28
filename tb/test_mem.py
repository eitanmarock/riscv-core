import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

DEPTH = 256


@cocotb.test()
async def mem_starts_zero(dut):
    dut.we.value = 0
    dut.wdata.value = 0
    for w in range(DEPTH):
        dut.addr.value = w * 4
        await Timer(1, unit="ns")
        assert int(dut.rdata.value) == 0, f"word {w} not zero at start"


@cocotb.test()
async def mem_random(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    ref = [0] * DEPTH       # reference model in Python
    dut.we.value = 0
    dut.addr.value = 0
    dut.wdata.value = 0
    await RisingEdge(dut.clk)

    for _ in range(3000):
        we = random.randint(0, 1)
        addr = random.getrandbits(10)    # byte address, 0..1023
        wdata = random.getrandbits(32)

        dut.we.value = we
        dut.addr.value = addr
        dut.wdata.value = wdata

        await RisingEdge(dut.clk)        # write happens here
        if we:
            ref[addr >> 2] = wdata       # low 2 bits ignored

        await Timer(1, unit="ns")
        got = int(dut.rdata.value)
        assert got == ref[addr >> 2], \
            f"addr={addr:#x}: got {got:#x}, expected {ref[addr >> 2]:#x}"
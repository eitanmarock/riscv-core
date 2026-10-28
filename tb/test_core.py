import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def core_prog1(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    for _ in range(4):               # one instruction per cycle
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    regs = dut.rf.regs
    assert int(regs[1].value) == 5, f"x1 = {int(regs[1].value)}"
    assert int(regs[2].value) == 10, f"x2 = {int(regs[2].value)}"
    assert int(regs[3].value) == 15, f"x3 = {int(regs[3].value)}"
    assert int(regs[4].value) == 0xFFFFFFFB, f"x4 = {int(regs[4].value):#x}"
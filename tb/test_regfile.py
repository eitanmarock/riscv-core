import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def regfile_random(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    ref = [0] * 32          # reference model in Python
    dut.we.value = 0
    dut.rs1.value = 0
    dut.rs2.value = 0
    dut.rd.value = 0
    dut.wdata.value = 0
    await RisingEdge(dut.clk)

    for _ in range(3000):
        we = random.randint(0, 1)
        rd = random.randint(0, 31)
        wdata = random.getrandbits(32)
        rs1 = random.randint(0, 31)
        rs2 = random.randint(0, 31)

        dut.we.value = we
        dut.rd.value = rd
        dut.wdata.value = wdata
        dut.rs1.value = rs1
        dut.rs2.value = rs2

        await RisingEdge(dut.clk)      # write happens here
        if we and rd != 0:
            ref[rd] = wdata

        await Timer(1, unit="ns")      # let outputs settle after the edge
        assert int(dut.rdata1.value) == ref[rs1], \
            f"rs1={rs1}: got {int(dut.rdata1.value):#x}, expected {ref[rs1]:#x}"
        assert int(dut.rdata2.value) == ref[rs2], \
            f"rs2={rs2}: got {int(dut.rdata2.value):#x}, expected {ref[rs2]:#x}"
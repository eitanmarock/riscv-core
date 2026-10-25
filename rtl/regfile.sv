module regfile (
    input  logic        clk,
    input  logic        we,
    input  logic [4:0]  rs1,
    input  logic [4:0]  rs2,
    input  logic [4:0]  rd,
    input  logic [31:0] wdata,
    output logic [31:0] rdata1,
    output logic [31:0] rdata2
);
    logic [31:0] regs [31:0];

    // initial value so simulation never reads unknown values
    initial begin
        for (int i = 0; i < 32; i++) regs[i] = 32'd0;
    end

    // write: on rising clock edge, never to x0
    always_ff @(posedge clk) begin
        if (we && rd != 5'd0) regs[rd] <= wdata;
    end

    // read: combinational, x0 always zero
    assign rdata1 = (rs1 == 5'd0) ? 32'd0 : regs[rs1];
    assign rdata2 = (rs2 == 5'd0) ? 32'd0 : regs[rs2];
endmodule
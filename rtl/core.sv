module core #(
    parameter string PROG_FILE = "progs/prog1.hex"
) (
    input  logic clk,
    input  logic rst
);
    logic [31:0] pc;
    logic [31:0] instr;
    logic [31:0] imm;
    logic [31:0] rdata1, rdata2;
    logic [31:0] alu_b, alu_y;
    logic [31:0] dmem_rdata, rd_data;
    logic        reg_write, alu_src, mem_write, mem_to_reg, valid;
    logic [3:0]  alu_op;

    // program counter
    always_ff @(posedge clk) begin
        if (rst) pc <= 32'd0;
        else     pc <= pc + 32'd4;
    end

    // instruction memory (read only)
    mem #(.DEPTH(256), .INIT_FILE(PROG_FILE)) imem (
        .clk(clk), .we(1'b0), .addr(pc), .wdata(32'd0), .rdata(instr)
    );

    decoder dec (
        .instr(instr), .reg_write(reg_write), .alu_src(alu_src),
        .alu_op(alu_op), .mem_write(mem_write), .mem_to_reg(mem_to_reg),
        .valid(valid)
    );

    imm_gen ig (.instr(instr), .imm(imm));

    regfile rf (
        .clk(clk), .we(reg_write), .rs1(instr[19:15]), .rs2(instr[24:20]),
        .rd(instr[11:7]), .wdata(rd_data), .rdata1(rdata1), .rdata2(rdata2)
    );

    assign alu_b = alu_src ? imm : rdata2;

    alu al (.a(rdata1), .b(alu_b), .op(alu_op), .y(alu_y));

    // data memory: address comes from the ALU, store data from rs2
    mem #(.DEPTH(256)) dmem (
        .clk(clk), .we(mem_write), .addr(alu_y), .wdata(rdata2), .rdata(dmem_rdata)
    );

    assign rd_data = mem_to_reg ? dmem_rdata : alu_y;
endmodule
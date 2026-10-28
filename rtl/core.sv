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
    logic        reg_write, alu_src, valid;
    logic [3:0]  alu_op;

    // program counter
    always_ff @(posedge clk) begin
        if (rst) pc <= 32'd0;
        else     pc <= pc + 32'd4;
    end

    // instruction memory (read only: we is tied to 0)
    mem #(.DEPTH(256), .INIT_FILE(PROG_FILE)) imem (
        .clk(clk), .we(1'b0), .addr(pc), .wdata(32'd0), .rdata(instr)
    );

    decoder dec (
        .instr(instr), .reg_write(reg_write), .alu_src(alu_src),
        .alu_op(alu_op), .valid(valid)
    );

    imm_gen ig (.instr(instr), .imm(imm));

    regfile rf (
        .clk(clk), .we(reg_write), .rs1(instr[19:15]), .rs2(instr[24:20]),
        .rd(instr[11:7]), .wdata(alu_y), .rdata1(rdata1), .rdata2(rdata2)
    );

    assign alu_b = alu_src ? imm : rdata2;

    alu al (.a(rdata1), .b(alu_b), .op(alu_op), .y(alu_y));
endmodule
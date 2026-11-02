module core #(
    parameter string PROG_FILE = "progs/prog1.hex"
) (
    input  logic clk,
    input  logic rst
);
    logic [31:0] pc, pc_next, pc_plus4;
    logic [31:0] instr;
    logic [31:0] imm;
    logic [31:0] rdata1, rdata2;
    logic [31:0] alu_b, alu_y;
    logic [31:0] dmem_rdata, rd_data;
    logic        reg_write, alu_src, mem_write, mem_to_reg;
    logic        branch, jal, jalr, lui, auipc, valid;
    logic        taken;
    logic [3:0]  alu_op;

    assign pc_plus4 = pc + 32'd4;

    // next pc: JALR target, or pc+imm for JAL / taken branch, or pc+4
    always_comb begin
        if (jalr)                       pc_next = alu_y & 32'hFFFFFFFE;
        else if (jal || (branch && taken)) pc_next = pc + imm;
        else                            pc_next = pc_plus4;
    end

    always_ff @(posedge clk) begin
        if (rst) pc <= 32'd0;
        else     pc <= pc_next;
    end

    mem #(.DEPTH(256), .INIT_FILE(PROG_FILE)) imem (
        .clk(clk), .we(1'b0), .addr(pc), .wdata(32'd0), .rdata(instr)
    );

    decoder dec (
        .instr(instr), .reg_write(reg_write), .alu_src(alu_src),
        .alu_op(alu_op), .mem_write(mem_write), .mem_to_reg(mem_to_reg),
        .branch(branch), .jal(jal), .jalr(jalr), .lui(lui),
        .auipc(auipc), .valid(valid)
    );

    imm_gen ig (.instr(instr), .imm(imm));

    regfile rf (
        .clk(clk), .rst(rst), .we(reg_write), .rs1(instr[19:15]), .rs2(instr[24:20]),
        .rd(instr[11:7]), .wdata(rd_data), .rdata1(rdata1), .rdata2(rdata2)
    );

    branch_cmp bc (.a(rdata1), .b(rdata2), .funct3(instr[14:12]), .taken(taken));

    assign alu_b = alu_src ? imm : rdata2;

    alu al (.a(rdata1), .b(alu_b), .op(alu_op), .y(alu_y));

    mem #(.DEPTH(256)) dmem (
        .clk(clk), .we(mem_write), .addr(alu_y), .wdata(rdata2), .rdata(dmem_rdata)
    );

    // value written to rd
    always_comb begin
        if (jal || jalr)   rd_data = pc_plus4;       // return address
        else if (lui)      rd_data = imm;
        else if (auipc)    rd_data = pc + imm;
        else if (mem_to_reg) rd_data = dmem_rdata;
        else               rd_data = alu_y;
    end
endmodule
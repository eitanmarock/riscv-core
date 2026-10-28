module decoder (
    input  logic [31:0] instr,
    output logic        reg_write,
    output logic        alu_src,     // 0 = register, 1 = immediate
    output logic [3:0]  alu_op,
    output logic        mem_write,   // 1 = store to data memory
    output logic        mem_to_reg,  // 1 = register gets memory data
    output logic        valid        // 1 = instruction is supported
);
    logic [6:0] opcode;
    logic [2:0] funct3;
    logic [6:0] funct7;

    assign opcode = instr[6:0];
    assign funct3 = instr[14:12];
    assign funct7 = instr[31:25];

    always_comb begin
        reg_write  = 1'b0;
        alu_src    = 1'b0;
        alu_op     = 4'd0;
        mem_write  = 1'b0;
        mem_to_reg = 1'b0;
        valid      = 1'b0;

        case (opcode)
            7'b0110011: begin  // R-type
                reg_write = 1'b1;
                valid     = 1'b1;
                case (funct3)
                    3'b000: alu_op = funct7[5] ? 4'd1 : 4'd0;  // SUB / ADD
                    3'b001: alu_op = 4'd2;                     // SLL
                    3'b010: alu_op = 4'd3;                     // SLT
                    3'b011: alu_op = 4'd4;                     // SLTU
                    3'b100: alu_op = 4'd5;                     // XOR
                    3'b101: alu_op = funct7[5] ? 4'd7 : 4'd6;  // SRA / SRL
                    3'b110: alu_op = 4'd8;                     // OR
                    3'b111: alu_op = 4'd9;                     // AND
                endcase
            end
            7'b0010011: begin  // I-type ALU
                reg_write = 1'b1;
                alu_src   = 1'b1;
                valid     = 1'b1;
                case (funct3)
                    3'b000: alu_op = 4'd0;                     // ADDI
                    3'b001: alu_op = 4'd2;                     // SLLI
                    3'b010: alu_op = 4'd3;                     // SLTI
                    3'b011: alu_op = 4'd4;                     // SLTIU
                    3'b100: alu_op = 4'd5;                     // XORI
                    3'b101: alu_op = funct7[5] ? 4'd7 : 4'd6;  // SRAI / SRLI
                    3'b110: alu_op = 4'd8;                     // ORI
                    3'b111: alu_op = 4'd9;                     // ANDI
                endcase
            end
            7'b0000011: begin  // LOAD: only LW (funct3 = 010)
                if (funct3 == 3'b010) begin
                    reg_write  = 1'b1;
                    alu_src    = 1'b1;   // address = rs1 + imm
                    alu_op     = 4'd0;
                    mem_to_reg = 1'b1;
                    valid      = 1'b1;
                end
            end
            7'b0100011: begin  // STORE: only SW (funct3 = 010)
                if (funct3 == 3'b010) begin
                    alu_src   = 1'b1;    // address = rs1 + imm
                    alu_op    = 4'd0;
                    mem_write = 1'b1;
                    valid     = 1'b1;
                end
            end
            default: ;
        endcase
    end
endmodule
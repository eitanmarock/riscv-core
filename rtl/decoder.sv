module decoder (
    input  logic [31:0] instr,
    output logic        reg_write,
    output logic        alu_src,
    output logic [3:0]  alu_op,
    output logic        mem_write,
    output logic        mem_to_reg,
    output logic        branch,      // 1 = conditional branch
    output logic        jal,         // 1 = JAL
    output logic        valid
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
        branch     = 1'b0;
        jal        = 1'b0;
        valid      = 1'b0;

        case (opcode)
            7'b0110011: begin  // R-type
                reg_write = 1'b1;
                valid     = 1'b1;
                case (funct3)
                    3'b000: alu_op = funct7[5] ? 4'd1 : 4'd0;
                    3'b001: alu_op = 4'd2;
                    3'b010: alu_op = 4'd3;
                    3'b011: alu_op = 4'd4;
                    3'b100: alu_op = 4'd5;
                    3'b101: alu_op = funct7[5] ? 4'd7 : 4'd6;
                    3'b110: alu_op = 4'd8;
                    3'b111: alu_op = 4'd9;
                endcase
            end
            7'b0010011: begin  // I-type ALU
                reg_write = 1'b1;
                alu_src   = 1'b1;
                valid     = 1'b1;
                case (funct3)
                    3'b000: alu_op = 4'd0;
                    3'b001: alu_op = 4'd2;
                    3'b010: alu_op = 4'd3;
                    3'b011: alu_op = 4'd4;
                    3'b100: alu_op = 4'd5;
                    3'b101: alu_op = funct7[5] ? 4'd7 : 4'd6;
                    3'b110: alu_op = 4'd8;
                    3'b111: alu_op = 4'd9;
                endcase
            end
            7'b0000011: begin  // LW
                if (funct3 == 3'b010) begin
                    reg_write  = 1'b1;
                    alu_src    = 1'b1;
                    mem_to_reg = 1'b1;
                    valid      = 1'b1;
                end
            end
            7'b0100011: begin  // SW
                if (funct3 == 3'b010) begin
                    alu_src   = 1'b1;
                    mem_write = 1'b1;
                    valid     = 1'b1;
                end
            end
            7'b1100011: begin  // BRANCH (funct3 010 and 011 do not exist)
                if (funct3 != 3'b010 && funct3 != 3'b011) begin
                    branch = 1'b1;
                    valid  = 1'b1;
                end
            end
            7'b1101111: begin  // JAL
                reg_write = 1'b1;
                jal       = 1'b1;
                valid     = 1'b1;
            end
            default: ;
        endcase
    end
endmodule
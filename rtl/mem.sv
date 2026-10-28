module mem #(
    parameter int    DEPTH     = 256,
    parameter string INIT_FILE = ""
) (
    input  logic        clk,
    input  logic        we,
    input  logic [31:0] addr,
    input  logic [31:0] wdata,
    output logic [31:0] rdata
);
    localparam int AW = $clog2(DEPTH);

    logic [31:0] words [DEPTH];

    initial begin
        for (int i = 0; i < DEPTH; i++) words[i] = 32'd0;
        if (INIT_FILE != "") $readmemh(INIT_FILE, words);
    end

    // write: on rising clock edge
    always_ff @(posedge clk) begin
        if (we) words[addr[AW+1:2]] <= wdata;
    end

    // read: combinational
    assign rdata = words[addr[AW+1:2]];
endmodule
module course_regfile(
  input logic clk, rst, wen,
  input logic [3:0] rd, rs1, rs2,
  input logic [31:0] wdata,
  output logic [31:0] a, b,
  output logic [31:0] regs [0:15]
);
  assign a = rs1 == 0 ? 32'b0 : regs[rs1];
  assign b = rs2 == 0 ? 32'b0 : regs[rs2];
  always_ff @(posedge clk) begin
    if (rst) begin
      for (int j=0;j<16;j++) regs[j]<=0;
    end else begin
      if (wen && rd!=0) regs[rd]<=wdata;
      regs[0]<=0;
    end
  end
endmodule

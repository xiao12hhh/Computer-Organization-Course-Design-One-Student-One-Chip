module top_module(input [31:0] a,b,input sub,output [31:0] sum);
  wire [31:0] operand=b^{32{sub}};
  wire carry,unused_carry;
  add16 lo(a[15:0],operand[15:0],sub,sum[15:0],carry);
  add16 hi(a[31:16],operand[31:16],carry,sum[31:16],unused_carry);
endmodule

module top_module(input [31:0] a,b,output [31:0] sum);
  wire carry,unused_carry;
  add16 lo(a[15:0],b[15:0],1'b0,sum[15:0],carry);
  add16 hi(a[31:16],b[31:16],carry,sum[31:16],unused_carry);
endmodule

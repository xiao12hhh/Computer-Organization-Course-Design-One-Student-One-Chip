// sISA plus local extension 01_0000_rs: latch R[rs] to the display port.
module scpu_io(input logic clk,rst,en,input logic [7:0] instruction,
  output logic [3:0] pc,output logic [7:0] r0,r1,r2,r3,out_value,
  output logic out_valid,illegal);
  logic [7:0] regs[4];
  wire [1:0] op=instruction[7:6],rd=instruction[5:4],rs1=instruction[3:2],rs2=instruction[1:0];
  assign r0=regs[0];assign r1=regs[1];assign r2=regs[2];assign r3=regs[3];
  assign illegal=op==1 && instruction[5:2]!=0;
  always_ff @(posedge clk) begin
    if(rst) begin pc<=0;out_value<=0;out_valid<=0;for(int i=0;i<4;i++)regs[i]<=0;end
    else if(en && !illegal) begin
      pc<=pc+1'b1;
      case(op)
        0:regs[rd]<=regs[rs1]+regs[rs2];
        1:begin out_value<=regs[rs2];out_valid<=1;end
        2:regs[rd]<={4'b0,instruction[3:0]};
        3:if(regs[0]!=regs[rs2])pc<=instruction[5:2];
      endcase
    end
  end
endmodule

module scpu_system(input logic clk,rst,en,
  output logic [3:0] pc,output logic [7:0] r0,r1,r2,r3,out_value,
  output logic out_valid,illegal);
  logic [7:0] instruction;
  always_comb case(pc)
    0:instruction=8'h8b;1:instruction=8'h91;2:instruction=8'ha0;3:instruction=8'hb1;
    4:instruction=8'h29;5:instruction=8'h17;6:instruction=8'hd1;
    7:instruction=8'h42;8:instruction=8'he3;
    default:instruction=8'h7f;
  endcase
  scpu_io cpu(clk,rst,en,instruction,pc,r0,r1,r2,r3,out_value,out_valid,illegal);
endmodule

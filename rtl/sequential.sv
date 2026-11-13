module sum10(input logic clk,rst, output logic [7:0] sum,
             output logic [3:0] index, output logic done);
  always_ff @(posedge clk) begin
    if(rst) begin sum<=0; index<=1; done<=0; end
    else if(!done) begin
      sum<=sum+{4'b0,index};
      if(index==10) done<=1; else index<=index+1'b1;
    end
  end
endmodule

module scpu(input logic clk,rst, input logic [7:0] instruction,
            output logic [3:0] pc, output logic [7:0] r0,r1,r2,r3,
            output logic illegal);
  logic [7:0] regs[4];
  assign r0=regs[0]; assign r1=regs[1]; assign r2=regs[2]; assign r3=regs[3];
  assign illegal=instruction[7:6]==2'b01;
  always_ff @(posedge clk) begin
    if(rst) begin pc<=0; for(int i=0;i<4;i++) regs[i]<=0; end
    else if(!illegal) begin
      pc<=pc+1'b1;
      case(instruction[7:6])
        2'b00: regs[instruction[5:4]]<=regs[instruction[3:2]]+regs[instruction[1:0]];
        2'b10: regs[instruction[5:4]]<={4'b0,instruction[3:0]};
        2'b11: if(regs[0]!=regs[instruction[1:0]]) pc<=instruction[5:2];
        default: ;
      endcase
    end
  end
endmodule

// Week 8 subset: RV32E register count; only ADDI and JALR are accepted.
module minirv2(input logic clk,rst,input logic [31:0] instruction,
               input logic [3:0] debug_index,
               output logic [31:0] pc,debug_value, output logic illegal,misaligned);
  logic [31:0] regs[16];
  logic [4:0] rd,rs1;
  logic [31:0] imm,result,target;
  logic is_addi,is_jalr;
  assign rd=instruction[11:7]; assign rs1=instruction[19:15];
  assign imm={{20{instruction[31]}},instruction[31:20]};
  assign is_addi=instruction[6:0]==7'h13 && instruction[14:12]==0;
  assign is_jalr=instruction[6:0]==7'h67 && instruction[14:12]==0;
  assign result=regs[rs1[3:0]]+imm;
  assign target=result & 32'hfffffffe;
  assign illegal=(!is_addi && !is_jalr)||rd[4]||rs1[4];
  assign misaligned=is_jalr && (target[1:0]!=0);
  assign debug_value=regs[debug_index];
  always_ff @(posedge clk) begin
    if(rst) begin pc<=0; for(int i=0;i<16;i++) regs[i]<=0; end
    else if(!illegal && !misaligned) begin
      pc<=is_jalr ? target : pc+32'd4;
      if(rd!=0) regs[rd[3:0]]<=is_jalr ? pc+32'd4 : result;
      regs[0]<=0;
    end
  end
endmodule

module running_light #(parameter integer PERIOD=100000)(input logic clk,rst,
                                                       output logic [7:0] led);
  localparam integer WIDTH=(PERIOD<=1)?1:$clog2(PERIOD);
  logic [WIDTH-1:0] count;
  always_ff @(posedge clk) begin
    if(rst) begin count<=0; led<=1; end
    else if(count==WIDTH'(PERIOD-1)) begin count<=0; led<={led[6:0],led[7]}; end
    else count<=count+1'b1;
  end
endmodule

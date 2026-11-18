module minirv_top(
  input logic clk, rst, en,
  input logic [31:0] reset_pc,
  output logic [31:0] pc,
  output logic [31:0] regs [0:15],
  output logic halted, fault
);
  import "DPI-C" function int pmem_read(input int address);
  import "DPI-C" function void pmem_write(input int address, input int data, input byte mask);
  import "DPI-C" function void npc_trap(input int code, input int trap_pc, input int invalid);
  logic [31:0] inst,a,b,next_pc,result,address,rdata,wdata;
  logic write_reg,lw,lbu,sw,sb,trap,illegal,commit;
  // Fetch and loads are combinational; the timer device provides a high/low snapshot.
  always_comb inst=(!rst && !halted && en)?pmem_read(pc):0;
  always_comb rdata=(!rst && !halted && en && !illegal && (lw||lbu))?pmem_read(address):0;
  assign wdata=lw?rdata:lbu?((rdata>>(8*address[1:0]))&32'hff):result;
  assign commit=en && !rst && !halted && !illegal && !trap;
  course_decode idu(inst,pc,a,b,next_pc,result,address,write_reg,lw,lbu,sw,sb,trap,illegal);
  course_regfile rf(clk,rst,commit&&write_reg,inst[10:7],inst[18:15],inst[23:20],wdata,a,b,regs);
  // Stores and trap notifications happen once, at the architectural commit edge.
  always_ff @(posedge clk) begin
    if (rst) begin pc<=reset_pc;halted<=0;fault<=0;end
    else if (en && !halted) begin
      if (illegal) begin halted<=1;fault<=1;npc_trap(-1,pc,1);end
      else if (trap) begin halted<=1;pc<=next_pc;npc_trap(regs[10],pc,0);end
      else begin
        if (sw) pmem_write(address,b,8'h0f);
        if (sb) pmem_write(address,b<<(8*address[1:0]),8'(1<<address[1:0]));
        pc<=next_pc;
      end
    end
  end
endmodule

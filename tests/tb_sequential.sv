module tb_sequential;
  logic clk=0,rst=1;
  always #5 clk=~clk;
  logic [7:0] total,sinst,r0,r1,r2,r3,led;
  logic [3:0] index,spc,di;
  logic done,si,mi,ma;
  logic [31:0] rpc,inst,dv;
  logic [7:0] srom[16];
  logic [31:0] rom[64];
  assign sinst=srom[spc];
  assign inst=rom[rpc[7:2]];
  sum10 summation(clk,rst,total,index,done);
  scpu smallcpu(clk,rst,sinst,spc,r0,r1,r2,r3,si);
  minirv2 riscv(clk,rst,inst,di,rpc,dv,mi,ma);
  running_light #(.PERIOD(2)) light(clk,rst,led);
  function automatic [31:0] addi(int rd,int rs,int imm);
    return (32'(imm)&32'hfff)<<20 | 32'(rs)<<15 | 32'(rd)<<7 | 32'h13;
  endfunction
  function automatic [31:0] jalr(int rd,int rs,int imm);
    return (32'(imm)&32'hfff)<<20 | 32'(rs)<<15 | 32'(rd)<<7 | 32'h67;
  endfunction
  task automatic step;
    @(posedge clk); #1;
  endtask
  task automatic reset_all;
    @(negedge clk); rst=1; step(); @(negedge clk); rst=0;
  endtask
  initial begin
    $dumpfile("build/sequential.vcd"); $dumpvars(0,tb_sequential);
    for(int i=0;i<16;i++) srom[i]=8'h80;
    // r0=limit, r1=index, r2=sum, r3=1. End loop increments to 11.
    srom[0]=8'h8b; srom[1]=8'h91; srom[2]=8'ha0; srom[3]=8'hb1;
    srom[4]=8'h29; srom[5]=8'h17; srom[6]=8'hd1; srom[7]=8'hdf;
    for(int i=0;i<64;i++) rom[i]=jalr(0,0,12);
    rom[0]=addi(10,0,20); rom[1]=jalr(1,0,16); rom[2]=jalr(1,0,12);
    rom[3]=jalr(0,0,12); rom[4]=addi(10,10,10); rom[5]=jalr(0,1,0);
    di=10; reset_all();
    for(int cycle=1;cycle<=40;cycle++) begin
      step();
      assert(!si && !mi && !ma) else $fatal;
      assert(led==(8'b1 << ((cycle/2)%8))) else $fatal(1,"running light");
      if(cycle<=10) assert(total==cycle*(cycle+1)/2) else $fatal(1,"sum trace");
      if(cycle==10) assert(done && total==55) else $fatal;
    end
    assert(total==55 && done && r2==55 && r1==11 && spc==7) else $fatal(1,"sCPU sum");
    assert(dv==30 && rpc==12) else $fatal(1,"minirv call and return");
    // Immediate limits, wraparound, x0 protection and rd==rs1 JALR ordering.
    rom[0]=addi(2,0,-1); rom[1]=addi(3,2,1); rom[2]=addi(4,0,-2048);
    rom[3]=addi(5,0,2047); rom[4]=addi(0,0,99); rom[5]=addi(6,0,29);
    rom[6]=jalr(6,6,0); rom[7]=jalr(0,0,28);
    reset_all(); repeat(8) step();
    di=2; #1; assert(dv==32'hffffffff) else $fatal;
    di=3; #1; assert(dv==0) else $fatal;
    di=4; #1; assert(dv==32'hfffff800) else $fatal;
    di=5; #1; assert(dv==2047) else $fatal;
    di=0; #1; assert(dv==0) else $fatal;
    di=6; #1; assert(dv==28 && rpc==28) else $fatal;
    rom[0]=jalr(0,0,2); reset_all(); #1; assert(ma) else $fatal;
    step(); assert(rpc==0) else $fatal;
    rom[0]=addi(16,0,1); reset_all(); #1; assert(mi) else $fatal;
    step(); assert(rpc==0) else $fatal;
    rom[0]=32'hffffffff; reset_all(); #1; assert(mi) else $fatal;
    $display("PASS: sum10, complete sCPU, ADDI/JALR, x0, signed immediates, alignment and reset");
    $finish;
  end
endmodule

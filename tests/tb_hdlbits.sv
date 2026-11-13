// add16 is provided by HDLBits; this equivalent is ONLY for local simulation.
module add16(input [15:0] a,b,input cin,output [15:0] sum,output cout);
  assign {cout,sum}={1'b0,a}+{1'b0,b}+{16'b0,cin};
endmodule
module tb_hdlbits;
  logic one,zero,oa,oo,ox,sub;
  logic [3:0] v,sel;
  logic [1:0] pos;
  logic [31:0] a,b,sum,sumsub;
  logic [15:0] words[9],out;
  integer expectpos;
  dut_step_one u0(one); dut_zero u1(zero);
  dut_gates4 u2(v,oa,oo,ox); dut_always_case2 u3(v,pos);
  dut_module_add u4(a,b,sum); dut_module_addsub u5(a,b,sub,sumsub);
  dut_mux9to1v u6(words[0],words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],sel,out);
  initial begin
    #1; assert(one && !zero) else $fatal;
    for(int k=0;k<16;k++) begin
      v=4'(k); expectpos=0;
      for(int j=3;j>=0;j--) if((k&(1<<j))!=0) expectpos=j;
      #1; assert(oa==(k==15) && oo==(k!=0) && ox==($countones(v)%2) && pos==expectpos) else $fatal;
    end
    for(int k=0;k<1024;k++) begin
      a=$urandom; b=$urandom;
      if(k==0) begin a=32'hffffffff; b=1; end
      if(k==1) begin a=32'h0000ffff; b=1; end
      if(k==2) begin a=0; b=32'hffffffff; end
      for(int s=0;s<2;s++) begin sub=1'(s); #1;
        assert(sum==a+b && sumsub==(sub?a-b:a+b)) else $fatal;
      end
      for(int j=0;j<9;j++) words[j]=16'($urandom);
      for(int s=0;s<16;s++) begin sel=4'(s); #1;
        if(s<9) assert(out==words[s]) else $fatal;
        else assert(out==16'hffff) else $fatal;
      end
    end
    $display("PASS: 7 HDLBits local exercises (not online judge submissions)"); $finish;
  end
endmodule

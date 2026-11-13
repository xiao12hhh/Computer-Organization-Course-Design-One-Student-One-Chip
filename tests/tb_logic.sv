module tb_logic;
  logic [1:0] a2,sel;
  logic [3:0] dec,enc,aa,bb,result;
  logic [15:0] onehot;
  logic ev,em,en,pv;
  logic [7:0] priority_input;
  logic [2:0] py,ma,mb,mc,md,my,op;
  logic fa,fb,fc,fs,fo,carry,ov,z;
  integer expected, signed_a,signed_b, math_result;
  decoder24 d0(a2,dec);
  encoder164 e0(onehot,enc,ev,em);
  priority83 p0(priority_input,en,py,pv);
  full_adder f0(fa,fb,fc,fs,fo);
  mux4x3 m0(ma,mb,mc,md,sel,my);
  alu4 u0(aa,bb,op,result,carry,ov,z);
  initial begin
    for(int i=0;i<4;i++) begin a2=2'(i); #1; assert(dec==(1<<i)) else $fatal; end
    for(int i=0;i<65536;i++) begin
      onehot=16'(i); expected=0;
      for(int j=0;j<16;j++) if((i & (1<<j))!=0) expected |= j;
      #1;
      assert(enc==expected && ev==(i!=0) && em==((i!=0)&&((i&(i-1))!=0))) else $fatal;
    end
    for(int enable=0;enable<2;enable++) for(int i=0;i<256;i++) begin
      en=1'(enable); priority_input=8'(i); expected=0;
      if(enable!=0) for(int j=0;j<8;j++) if((i & (1<<j))!=0) expected=j;
      #1; assert(py==expected && pv==((enable!=0)&&(i!=0))) else $fatal;
    end
    for(int i=0;i<8;i++) begin
      {fa,fb,fc}=3'(i); #1;
      assert({fo,fs}==2'(int'(fa)+int'(fb)+int'(fc))) else $fatal;
    end
    for(int i=0;i<16384;i++) begin
      {sel,ma,mb,mc,md}=14'(i); #1;
      case(sel) 0: expected=int'(ma); 1: expected=int'(mb); 2: expected=int'(mc); 3: expected=int'(md); endcase
      assert(my==expected) else $fatal;
    end
    for(int i=0;i<16;i++) for(int j=0;j<16;j++) for(int k=0;k<8;k++) begin
      aa=4'(i); bb=4'(j); op=3'(k);
      signed_a=(i<8)?i:i-16; signed_b=(j<8)?j:j-16;
      math_result=0;
      case(k)
        0: begin expected=(i+j)&15; math_result=signed_a+signed_b; end
        1: begin expected=(i-j)&15; math_result=signed_a-signed_b; end
        2: expected=(~i)&15;
        3: expected=i&j; 4: expected=i|j; 5: expected=i^j;
        6: expected=int'(signed_a<signed_b); 7: expected=int'(i==j);
      endcase
      #1;
      assert(result==expected && z==(expected==0)) else $fatal(1,"ALU %d %d %d",i,j,k);
      assert(ov==((k<2)&&((math_result< -8)||(math_result>7)))) else $fatal;
      assert(carry==((k==0)?(i+j>15):((k==1)?(i>=j):0))) else $fatal;
    end
    $display("PASS: exhaustive decoder, encoder, priority, adder, mux and ALU");
    $finish;
  end
endmodule

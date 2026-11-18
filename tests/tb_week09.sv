module tb_week09;
  logic clk=0,rst=1,en=1,serial_in=0,w=0;
  logic [2:0] op=0,amount=0; logic [7:0] data=0,q,result,random_q;
  logic left=0,arith=0,z; logic [3:0] state;
  shift8 sh(clk,rst,en,serial_in,op,data,q);
  barrel8 b(data,amount,left,arith,result);
  lfsr8 l(clk,rst,en,random_q);
  repeat4 f(clk,rst,en,w,z,state);
  logic psclk=1,psdata=1,valid,error,pressed;
  logic [7:0] received,scan,ascii,press_count;
  ps2_receiver #(.TIMEOUT(100)) rx(clk,rst,psclk,psdata,valid,error,received);
  key_display kd(clk,rst,valid,error,received,pressed,scan,ascii,press_count);
  always #5 clk=~clk;
  task automatic tick; @(posedge clk); #1; @(negedge clk); endtask
  task automatic sendbit(input bit v);
    psdata=v; repeat(6) tick(); psclk=0; repeat(6) tick(); psclk=1; repeat(6) tick();
  endtask
  task automatic sendcode(input logic [7:0] code,input bit corrupt=0);
    sendbit(0); for(int k=0;k<8;k++) sendbit(code[k]);
    sendbit((~^code)^corrupt); sendbit(1); repeat(6) tick();
  endtask
  bit seen[256]; integer expect_value,run_length,previous;
  initial begin
    repeat(2) tick(); rst=0;
    for(int a=0;a<256;a++) for(int m=0;m<8;m++) for(int mode=0;mode<4;mode++) begin
      data=8'(a); amount=3'(m); left=1'(mode&1); arith=1'(mode>>1); #1;
      expect_value=left ? (a<<m)&255 : (arith && a>=128 ? ((a-256)>>>m)&255 : a>>m);
      assert(result==8'(expect_value)) else $fatal(1,"barrel %d %d %d",a,m,mode);
    end
    @(negedge clk);
    for(int a=0;a<256;a++) for(int m=0;m<8;m++) for(int si=0;si<2;si++) begin
      op=1; data=8'(a); tick(); op=3'(m);serial_in=1'(si);tick();
      case(m)
        0:expect_value=0;1:expect_value=a;2:expect_value=a>>1;3:expect_value=(a<<1)&255;
        4:expect_value=(a>>1)|(a&128);5:expect_value=(a>>1)|(si<<7);
        6:expect_value=(a>>1)|((a&1)<<7);7:expect_value=((a<<1)&255)|(a>>7);
      endcase
      assert(q==8'(expect_value)) else $fatal(1,"shift");
    end
    rst=1;tick();rst=0;
    for(int k=0;k<255;k++) begin
      assert(random_q!=0 && !seen[random_q]) else $fatal(1,"LFSR repeated early");
      seen[random_q]=1; tick();
    end
    assert(random_q==1) else $fatal(1,"LFSR period");
    for(int bits=0;bits<256;bits++) begin
      rst=1;tick();rst=0;run_length=0;previous=-1;
      for(int j=0;j<8;j++) begin
        w=1'(bits>>j);run_length=(int'(w)==previous)?run_length+1:1;previous=int'(w);tick();
        assert(z==(run_length>=4)) else $fatal(1,"FSM overlap");
      end
    end
    rst=1;tick();rst=0;
    sendcode(8'h1c); assert(pressed && scan==8'h1c && ascii=="a" && press_count==1) else $fatal(1,"A make");
    sendcode(8'h1c); assert(press_count==1) else $fatal(1,"typematic");
    sendcode(8'hf0);sendcode(8'h1c); assert(!pressed && ascii==0 && scan==0) else $fatal(1,"A break");
    sendcode(8'h16); assert(ascii=="1" && press_count==2) else $fatal(1,"digit");
    sendcode(8'hf0);sendcode(8'h16);
    sendcode(8'h1b,1); assert(!pressed && press_count==2) else $fatal(1,"bad parity");
    sendcode(8'he0);sendcode(8'h75); assert(!pressed) else $fatal(1,"extended key");
    sendbit(0);sendbit(1);repeat(110) tick();
    sendcode(8'h1b);assert(ascii=="s" && press_count==3) else $fatal(1,"timeout recovery");
    $display("PASS week09: 8192 barrel / 4096 shift cases; LFSR 255; 256 FSM streams; PS2 make/repeat/break/parity/timeout");
    $finish;
  end
endmodule

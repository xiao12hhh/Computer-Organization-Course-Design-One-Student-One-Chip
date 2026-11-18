// NJU experiments 6/7, local reference implementation.
module shift8(input logic clk,rst,en,serial_in,input logic [2:0] op,
  input logic [7:0] data,output logic [7:0] q);
  always_ff @(posedge clk) begin
    if(rst) q<=0;
    else if(en) case(op)
      0:q<=0; 1:q<=data; 2:q<={1'b0,q[7:1]}; 3:q<={q[6:0],1'b0};
      4:q<={q[7],q[7:1]}; 5:q<={serial_in,q[7:1]};
      6:q<={q[0],q[7:1]}; 7:q<={q[6:0],q[7]};
    endcase
  end
endmodule

// Three explicit mux stages, not a sequential multi-cycle shifter.
module barrel8(input logic [7:0] data,input logic [2:0] amount,
  input logic left,arith,output logic [7:0] result);
  wire [7:0] stage[4];
  assign stage[0]=data;
  for(genvar k=0;k<3;k++) begin: level
    localparam integer N=1<<k;
    wire fill=arith && data[7];
    assign stage[k+1]=!amount[k] ? stage[k] : left ?
      {stage[k][7-N:0],{N{1'b0}}} : {{N{fill}},stage[k][7:N]};
  end
  assign result=stage[3];
endmodule

module lfsr8(input logic clk,rst,en,output logic [7:0] q);
  always_ff @(posedge clk)
    if(rst || q==0) q<=1;
    else if(en) q<={q[4]^q[3]^q[2]^q[0],q[7:1]};
endmodule

module repeat4(input logic clk,rst,en,w,output logic z,output logic [3:0] state);
  always_ff @(posedge clk)
    if(rst) state<=0;
    else if(en) begin
      if(w) state<=(state>=5 && state<8)?state+1'b1:(state==8?4'd8:4'd5);
      else state<=(state>=1 && state<4)?state+1'b1:(state==4?4'd4:4'd1);
    end
  assign z=state==4 || state==8;
endmodule

// Synchronize both wires; consume one complete frame immediately. The decoder
// accepts a byte every system cycle, so no FIFO/backpressure is needed here.
module ps2_receiver #(parameter integer TIMEOUT=100000)(
  input logic clk,rst,ps2_clk,ps2_data,output logic valid,error,
  output logic [7:0] data);
  logic [2:0] cs,ds;
  logic [3:0] count;
  logic [9:0] frame;
  integer idle;
  wire falling=cs[2]&&!cs[1];
  always_ff @(posedge clk) begin
    if(rst) begin cs<=7; ds<=7; count<=0; frame<=0; idle<=0; valid<=0; error<=0; data<=0; end
    else begin
      cs<={cs[1:0],ps2_clk}; ds<={ds[1:0],ps2_data}; valid<=0; error<=0;
      if(falling) begin
        idle<=0;
        if(count==0) begin if(!ds[2]) begin frame[0]<=0; count<=1; end end
        else if(count==10) begin
          count<=0;
          if(ds[2] && (^frame[9:1])) begin data<=frame[8:1]; valid<=1; end
          else error<=1;
        end else begin frame[count]<=ds[2]; count<=count+1'b1; end
      end else if(count!=0) begin
        if(idle>=TIMEOUT-1) begin count<=0; idle<=0; error<=1; end
        else idle<=idle+1;
      end
    end
  end
endmodule

module key_display(input logic clk,rst,valid,error,input logic [7:0] data,
  output logic pressed,output logic [7:0] scan,ascii,press_count);
  logic released,extended;
  function automatic [7:0] translate(input logic [7:0] code);
    case(code)
      8'h1c:translate="a";8'h32:translate="b";8'h21:translate="c";8'h23:translate="d";
      8'h24:translate="e";8'h2b:translate="f";8'h34:translate="g";8'h33:translate="h";
      8'h43:translate="i";8'h3b:translate="j";8'h42:translate="k";8'h4b:translate="l";
      8'h3a:translate="m";8'h31:translate="n";8'h44:translate="o";8'h4d:translate="p";
      8'h15:translate="q";8'h2d:translate="r";8'h1b:translate="s";8'h2c:translate="t";
      8'h3c:translate="u";8'h2a:translate="v";8'h1d:translate="w";8'h22:translate="x";
      8'h35:translate="y";8'h1a:translate="z";
      8'h45:translate="0";8'h16:translate="1";8'h1e:translate="2";8'h26:translate="3";
      8'h25:translate="4";8'h2e:translate="5";8'h36:translate="6";8'h3d:translate="7";
      8'h3e:translate="8";8'h46:translate="9";8'h29:translate=" ";
      default:translate=0;
    endcase
  endfunction
  always_ff @(posedge clk) begin
    if(rst) begin pressed<=0; scan<=0; ascii<=0; press_count<=0; released<=0; extended<=0; end
    else if(error) begin released<=0; extended<=0; end
    else if(valid) begin
      if(data==8'he0) extended<=1;
      else if(data==8'hf0) released<=1;
      else begin
        released<=0; extended<=0;
        if(!extended && released && data==scan) begin pressed<=0; ascii<=0; scan<=0; end
        else if(!extended && !released && translate(data)!=0) begin
          if(!pressed) press_count<=press_count+1'b1;
          pressed<=1; scan<=data; ascii<=translate(data);
        end
      end
    end
  end
endmodule

module hex7(input logic [3:0] digit,input logic blank,output logic [7:0] segments);
  logic [7:0] bits;
  always_comb case(digit)
    0:bits=8'h03;1:bits=8'h9f;2:bits=8'h25;3:bits=8'h0d;
    4:bits=8'h99;5:bits=8'h49;6:bits=8'h41;7:bits=8'h1f;
    8:bits=8'h01;9:bits=8'h09;10:bits=8'h11;11:bits=8'hc1;
    12:bits=8'h63;13:bits=8'h85;14:bits=8'h61;15:bits=8'h71;
  endcase
  assign segments=blank?8'hff:bits;
endmodule

module lab_top #(parameter integer DEMO=6)(input logic clk,rst,
  input logic [15:0] sw,input logic [4:0] btn,input logic ps2_clk,ps2_data,
  output logic [15:0] ledr,
  output logic [7:0] seg0,seg1,seg2,seg3,seg4,seg5,seg6,seg7);
  assign seg6=8'hff;
  assign seg7=8'hff;
  logic [4:0] buttons,previous,metastable;
  always_ff @(posedge clk) begin
    if(rst)begin buttons<=0;previous<=0;metastable<=0;end
    else begin metastable<=btn;buttons<=metastable;previous<=buttons;end
  end
  wire step=buttons[2]&&!previous[2];
  wire reset=rst|buttons[4]; // BTNL
  logic [23:0] digits;
  logic [5:0] blank;
  if(DEMO==6) begin: shifts
    logic [7:0] q,lfsr,barrel;
    shift8 a(clk,reset,step,sw[11],sw[10:8],sw[7:0],q);
    lfsr8 b(clk,reset,step,lfsr);
    barrel8 c(sw[7:0],sw[10:8],sw[11],sw[12],barrel);
    wire [7:0] selected=sw[15:14]==0?lfsr:sw[15:14]==1?q:barrel;
    assign ledr={8'b0,selected};assign digits={16'b0,selected};assign blank=6'b111100;
  end else if(DEMO==7) begin: keyboard
    logic valid,error,pressed,z;logic [7:0] data,scan,ascii,count;logic [3:0] state;
    ps2_receiver r(clk,reset,ps2_clk,ps2_data,valid,error,data);
    key_display d(clk,reset,valid,error,data,pressed,scan,ascii,count);
    repeat4 f(clk,reset,step,sw[1],z,state);
    assign digits={count,ascii,scan};assign blank={2'b0,{4{!pressed}}};
    assign ledr={6'b0,error,pressed,state,3'b0,z};
  end else begin: processor
    logic [3:0] pc;logic [7:0] r0,r1,r2,r3,result;logic valid,illegal;
    scpu_system cpu(clk,reset,sw[0]|step,pc,r0,r1,r2,r3,result,valid,illegal);
    // Decimal 55 on low two digits; PC and result hex on the upper digits.
    assign digits={pc,4'b0,result,4'(result/10),4'(result%10)};
    assign blank=valid?6'b000000:6'b000011;
    assign ledr={2'b0,illegal,valid,pc,r2};
  end
  hex7 d0(digits[3:0],blank[0],seg0);hex7 d1(digits[7:4],blank[1],seg1);
  hex7 d2(digits[11:8],blank[2],seg2);hex7 d3(digits[15:12],blank[3],seg3);
  hex7 d4(digits[19:16],blank[4],seg4);hex7 d5(digits[23:20],blank[5],seg5);
endmodule

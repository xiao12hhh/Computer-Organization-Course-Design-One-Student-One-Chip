// Local reference interfaces; school OJ port names must be checked separately.
module decoder24(input logic [1:0] a, output logic [3:0] y);
  assign y = 4'b0001 << a;
endmodule

// Single-hot encoder: valid says at least one input is set; multi flags invalid use.
module encoder164(input logic [15:0] a, output logic [3:0] y,
                  output logic valid, multi);
  always_comb begin
    y = 0;
    for (int i=0; i<16; i++) if (a[i]) y |= 4'(i);
  end
  assign valid = |a;
  assign multi = (a != 0) && ((a & (a-16'd1)) != 0);
endmodule

// Highest numbered asserted input wins.
module priority83(input logic [7:0] a, input logic en,
                  output logic [2:0] y, output logic valid);
  always_comb begin
    y = 0;
    valid = en && (|a);
    if (en) for (int i=0; i<8; i++) if (a[i]) y = 3'(i);
  end
endmodule

module full_adder(input logic a,b,cin, output logic sum,cout);
  assign sum = a ^ b ^ cin;
  assign cout = (a & b) | (a & cin) | (b & cin);
endmodule

module mux4x3(input logic [2:0] a,b,c,d, input logic [1:0] sel,
             output logic [2:0] y);
  always_comb case(sel)
    0: y=a; 1: y=b; 2: y=c; 3: y=d;
  endcase
endmodule

// Local ALU contract: 000 add, 001 subtract, 010 NOT A, 011 AND,
// 100 OR, 101 XOR, 110 signed less-than, 111 equality.
module alu4(input logic [3:0] a,b, input logic [2:0] op,
            output logic [3:0] y, output logic carry,overflow,zero);
  logic [4:0] wide;
  always_comb begin
    y=0; carry=0; overflow=0; wide=0;
    case(op)
      0: begin
        wide={1'b0,a}+{1'b0,b}; y=wide[3:0]; carry=wide[4];
        overflow=~(a[3]^b[3]) & (y[3]^a[3]);
      end
      1: begin
        wide={1'b0,a}+{1'b0,~b}+5'd1; y=wide[3:0]; carry=wide[4];
        overflow=(a[3]^b[3]) & (y[3]^a[3]);
      end
      2: y=~a;
      3: y=a&b;
      4: y=a|b;
      5: y=a^b;
      6: y={3'b0,($signed(a)<$signed(b))};
      7: y={3'b0,(a==b)};
    endcase
  end
  assign zero=(y==0);
endmodule

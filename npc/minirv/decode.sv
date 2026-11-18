module course_decode(
  input logic [31:0] inst, pc, a, b,
  output logic [31:0] next_pc, result, address,
  output logic write_reg, load_word, load_byte, store_word, store_byte,
  output logic trap, illegal
);
  logic [31:0] imm_i, imm_s;
  assign imm_i={{20{inst[31]}},inst[31:20]};
  assign imm_s={{20{inst[31]}},inst[31:25],inst[11:7]};
  always_comb begin
    next_pc=pc+4;result=0;address=0;write_reg=0;
    load_word=0;load_byte=0;store_word=0;store_byte=0;trap=0;illegal=0;
    case(inst[6:0])
      7'h33:begin
        illegal=inst[31:25]!=0 || inst[14:12]!=0 || inst[11] || inst[19] || inst[24];
        result=a+b;write_reg=1;
      end
      7'h13:begin
        illegal=inst[14:12]!=0 || inst[11] || inst[19];result=a+imm_i;write_reg=1;
      end
      7'h37:begin illegal=inst[11];result={inst[31:12],12'b0};write_reg=1;end
      7'h67:begin
        illegal=inst[14:12]!=0 || inst[11] || inst[19];
        result=pc+4;next_pc=(a+imm_i)&32'hfffffffe;write_reg=1;
      end
      7'h03:begin
        address=a+imm_i;write_reg=1;
        load_word=inst[14:12]==2;load_byte=inst[14:12]==4;
        illegal=(!load_word && !load_byte) || inst[11] || inst[19] || (load_word && address[1:0]!=0);
      end
      7'h23:begin
        address=a+imm_s;store_word=inst[14:12]==2;store_byte=inst[14:12]==0;
        illegal=(!store_word && !store_byte) || inst[19] || inst[24] || (store_word && address[1:0]!=0);
      end
      7'h73:begin trap=inst==32'h00100073;illegal=!trap;end
      default:illegal=1;
    endcase
    illegal=illegal || next_pc[1:0]!=0;
  end
endmodule

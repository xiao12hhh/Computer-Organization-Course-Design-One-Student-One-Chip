from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'build'/'hdlbits-src'
out.mkdir(parents=True,exist_ok=True)
for src in (root/'hdlbits').glob('*.v'):
    (out/src.name).write_text(src.read_text().replace('module top_module','module dut_'+src.stem))

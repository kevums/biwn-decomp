"""Render the same qualified eight-root read-only monitor for fixtures and gameplay."""
from pathlib import Path
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import json
ROOT=Path(__file__).resolve().parents[1]
def render(build):
 path=ROOT/'scripts/native_gpu_family_observer_v2.inc.c';text=path.read_text();roots=build['mailbox_roots'];entries=list(roots);symbols=build['mailbox_symbols']
 assert [int(a,16)for a in entries]==[0xe0a6,0xe0f2,0xe148,0xe19e,0xe202,0xe220,0xe26c,0xe2b8]
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
 original_polls=[i.address for a in entries for i in md.disasm(image[int(a,16)-0x4000:roots[a]['end']-0x4000],int(a,16))if i.mnemonic=='cmpi.l'and'$f03204.l'in i.op_str]
 gate=json.loads(Path(build['final_component_gate']).read_text());code=Path(gate['GPU_binary']);native_polls=[i.address for i in md.disasm(code.read_bytes(),build['mailbox_start'])if i.mnemonic in['move.l','movea.l']and i.op_str.startswith('$f03204.l,')];assert len(original_polls)==len(native_polls)==8
 assert all(i.mnemonic=='movea.l'and i.op_str.split(',')[-1].strip()=='a0'for i in md.disasm(code.read_bytes(),build['mailbox_start'])if i.address in native_polls),'Actual native operand capture requires the verified MOVEA.L-to-A0 loads'
 values={'__ORIGINAL__':[int(a,16)for a in entries],'__ENDS__':[roots[a]['end']for a in entries],'__NATIVE__':[roots[a]['native_entry']for a in entries],'__RETURNS__':[symbols[roots[a]['symbol']+'_return']for a in entries],'__COMMANDS__':[roots[a]['command']for a in entries],'__ARGS__':[roots[a]['argument_count']for a in entries],'__POLLS__':original_polls+native_polls}
 for key,items in values.items():assert key in text;text=text.replace(key,','.join(hex(v)+'u'for v in items))
 for key,value in {'__MB_START__':build['mailbox_start'],'__MB_END__':build['mailbox_end'],'__MB_BODY__':symbols['biwn_native_gpu_mailbox_body']}.items():assert key in text;text=text.replace(key,hex(value)+'u')
 return text,path

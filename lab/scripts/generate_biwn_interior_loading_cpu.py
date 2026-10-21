"""FullCPU scene parsers/loaders, texture setup/cache and indoor position.
Source-specific fixed C; source exception/undefined DIVS overflow not emulated.
"""
import hashlib,json,re
from pathlib import Path
import generate_biwn_display_list_cpu as framed
resource=framed.resource;base=resource.base;ROOT=base.ROOT
RANGES={0x20aa0:0x20b2a,0x20b2a:0x20c16,0x20c16:0x20cc4,0x20cf8:0x20d7c,0x20d7c:0x20e40,0x20f78:0x21242,0x1aa40:0x1aade,0x1ac3c:0x1ac68,0x1ac68:0x1ae56,0x10520:0x105da,0x105da:0x10652}
def rename(s):
 return s.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_interior_loading_cpu.py').replace('biwn_input_dispatch_cpu','biwn_interior_loading_cpu').replace('biwn_dispatch_cpu_status','biwn_interior_loading_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_INTERIOR_LOADING_CPU').replace('BIWN_RESOURCE_CPU','BIWN_INTERIOR_LOADING_CPU').replace('BIWN_DISPLAY_LIST_CPU','BIWN_INTERIOR_LOADING_CPU')
def emit(row):
 pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=base.split(tail);code=None;terminal=False
 if op=='jsr'and parts[0].startswith('('):
  target=framed.address(parts[0]);code=[f'u={target};CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc=u;',f'CHECK(invoke(&s,s.cpu.pc,{hex(nxt)}u));break;'];terminal=True
 elif op=='lsr.l':
  assert parts[0]=='#$6';r=base.register(parts[1]);code=[f'v=s.cpu.registers[{r}];u=(v>>5)&1u;v>>=6;put(&s,{r},4,v);nz(&s,v,32);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));']
 elif op=='divs.w':
  r=base.register(parts[1]);assert r is not None and r<8
  code=[resource.load(parts[0],2),f'{{int64_t dividend=(int64_t)(int32_t)s.cpu.registers[{r}],divisor=(int64_t)(int32_t)sx16((uint16_t)v),quotient,remainder;if(!divisor)return BIWN_INTERIOR_LOADING_CPU_DIVISION_BY_ZERO;quotient=dividend/divisor;if(quotient< -32768||quotient>32767)return BIWN_INTERIOR_LOADING_CPU_DIVISION_OVERFLOW;remainder=dividend%divisor;s.cpu.registers[{r}]=((uint32_t)(uint16_t)remainder<<16)|(uint16_t)quotient;nz(&s,(uint16_t)quotient,16);}}']
 if code is None:return rename(framed.emit(row))
 if not terminal:code.append(f's.cpu.pc={hex(nxt)}u;break;')
 return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';rows=[]
 for a,b in RANGES.items():
  assert image[a-0x4000:b-0x4000]==snapshot[a:b];rows +=base.binary_tools.m68k_instructions(snapshot[a:b],a)[0]
 prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
 header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_INTERIOR_LOADING_CPU_H');header=header.replace('BIWN_INTERIOR_LOADING_CPU_BAD_PC=7','BIWN_INTERIOR_LOADING_CPU_BAD_PC=7,BIWN_INTERIOR_LOADING_CPU_DIVISION_BY_ZERO=8,BIWN_INTERIOR_LOADING_CPU_DIVISION_OVERFLOW=9');a=header.index('/* Static');b=header.index('enum biwn_interior_loading_cpu_status biwn_interior_loading_cpu_body',a);header=header[:a]+'''/* FullCPU/source private frames for six scene loader/parser bodies,
 * 1AA40texture setup,1AC3Clookup,1AC68acquire and10520/105DAindoor position.
 * Bothstackbanks; fixed build-time decoded blocks, no runtimeCPUdecode or
 * originalCPU/GPUexecution. Nestedbody providers execute up to theirRTS;
 * outercall consumesRTS. Existing sourceDF60yield propagation retained.
 * Finite valid buffers are caller requirements. DIVS normal signed16bit
 * quotient domain; host statuses8/9 for zero/overflow leave callerCPU
 * unchanged with priorRAMeffects retained, not sourceexception/trap or
 * undefinedflag emulation. Disc/BIOS/scheduler/actor helpers are providers.
 * This group alone proves no fullscene loading, boot or playablegame. */
'''+header[b:]
 source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_interior_loading_cpu.c','biwn_interior_loading_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(base.SUFFIX));(source/names[1]).write_text(header);manifest=dict(status='generated_unverified',instructions=len(rows),ranges={hex(a):hex(b)for a,b in RANGES.items()},instructions_decoded=rows,stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},new_published_components=0,whole_game_complete=False);(session/'interior-loading-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()

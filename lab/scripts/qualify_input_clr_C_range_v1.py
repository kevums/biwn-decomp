"""Qualify the changed shared C-code floor using exact extracted watcher.
Host synthetic states only; no game state is modified.
"""
import ctypes as c,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
def main():
 bp=V/'native-Deck-input-clr-disc-build-v1-current.json';b=read(bp);gp=V/'input-clr-geometry-observer-qualified-v1-current.json';g=read(gp);text=Path(g['observer']).read_text();lo=text.index('static const uint32_t shared_root[5]');hi=text.index('static void native_deck_watch(',lo);body=text[lo:hi]
 elf=Path(b['directory'])/'five-build/native-shared.elf';table=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-readelf'),'-sW',str(elf)],text=True);functions=[(int(x.split()[1],16),x.split()[7])for x in table.splitlines()if len(x.split())>=8 and x.split()[3]=='FUNC'and x.split()[6]=='1'];floor=min(a for a,_ in functions);assert floor==b['shared_Deck_symbols']['midpoint']<b['shared_Deck_symbols']['native_input_bit']
 out=V/'input-clr-C-range-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'ELF-symbols.txt').write_text(table)
 stub='''#include <stdint.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],deck_used[101];\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}\nstatic void read_cpu(struct cpu *out){*out=current;}\n'''
 hook='''\nvoid clear(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(shared_pending,0,sizeof(shared_pending));memset(shared_incoming,0,sizeof(shared_incoming));memset(shared_C_observations,0,sizeof(shared_C_observations));shared_errors=shared_C_outside=0;}\nvoid put(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}\nvoid stack(uint32_t sp){current.r[15]=sp;}\nvoid pc(uint32_t a){shared_watch(a);}\nuint64_t stat(unsigned n){if(n==0)return shared_errors;if(n==1)return shared_C_outside;if(n==7)return shared_pending_total();return shared_C_observations[n-2];}\n'''
 source=out/'fixture.c';source.write_text(stub+body+hook);lib=out/'fixture.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 f=c.CDLL(str(lib));f.put.argtypes=[c.c_uint32,c.c_uint32];f.stack.argtypes=[c.c_uint32];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64
 names=['coordinate','input','face','scan','geometry'];bounds=[(832,1008),(608,816),(608,816),(416,592),(832,1008)];base=b['deck_arena_address']+6*1024;rows=[]
 for k,name in enumerate(names):
  low,top=bounds[k]
  for pc,symbol in functions:
   for offset,want in [(low,True),(top,True),(low-2,False),(top+2,False)]:
    f.clear();f.put(0xc0920,0xc0928+6*1024);f.stack(0xc0928+6*1024+768);f.pc(b['shared_Deck_symbols']['biwn_v4_'+name]);f.stack(base+offset);f.pc(pc);errors,outside,observations=[f.stat(i)for i in [0,1,k+2]];assert f.stat(7)==1 and errors==0 and outside==int(not want)and observations==int(want),(name,symbol,offset,errors,outside,observations);rows.append(dict(root=name,symbol=symbol,PC=hex(pc),SP_offset=offset,accepted=want))
  f.clear();f.put(0xc0920,0xc0928+6*1024);f.stack(0xc0928+6*1024+768);f.pc(b['shared_Deck_symbols']['biwn_v4_'+name]);f.stack(base+low-2);f.pc(floor-2);assert f.stat(1)==f.stat(k+2)==0
 save(out/'cases.json',rows);proof=dict(status='terminal_ELF_C_floor_all_functions_stack_boundary_controls_pass',directory=str(out),ELF_C_functions=len(functions),C_floor=hex(floor),first_C_function='midpoint',removed_old_symbol='bit',late_symbol_not_used_as_floor='native_input_bit',legal_controls=sum(x['accepted']for x in rows),rejected_outside_stack_controls=sum(not x['accepted']for x in rows),assembly_boundary_controls=5,new_predictions=0,new_training=False,guest_state_writes=False,scope=__doc__+'Each actual ELF FUNC start for all5roots,both inclusive stack endpoints and2outside values. Checks observer counters,not real CPU execution/IRQ fidelity.',source_sha256={str(x):sha(x)for x in [Path(__file__),bp,gp,elf,Path(g['observer']),source,lib,out/'cases.json',out/'ELF-symbols.txt']});save(out/'review.json',proof);save(V/'input-clr-C-range-qualified-v1-current.json',proof);print(proof['status'],proof['ELF_C_functions'],proof['legal_controls'],proof['rejected_outside_stack_controls'])
if __name__=='__main__':main()

"""Synthetic controls for exact six-root admission, C-stack and scene commit observer.
Host memory/CPU fixtures only;no guest execution or runtime repair.
"""
import ctypes as c,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 bp=V/'native-scene17-direct-dispatch-disc-build-v1-current.json';b=read(bp);gp=V/'scene17-direct-dispatch-geometry-observer-qualified-v1-current.json';g=read(gp);text=Path(g['observer']).read_text();start=text.index('static const uint32_t shared_root[6]');end=text.index('static void native_deck_watch(',start);body=text[start:end]
 out=V/'scene17-direct-dispatch-shared-observer-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory,deck_used[101];\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *o){*o=current;}\n'''
 arrays=['shared_public','shared_attempts','shared_entries','shared_returns','shared_original','shared_fallbacks','shared_calls','shared_helper_returns','shared_C_observations','shared_pending','shared_busy','shared_rejected','shared_incoming','shared_busy_CPU','shared_rejected_CPU','shared_rejected_task','shared_busy_frame','shared_busy_stack','deck_used']
 hooks='\nvoid clear(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));shared_errors=shared_C_outside=0;'+''.join('memset('+a+',0,sizeof('+a+'));'for a in arrays)+'for(unsigned k=0;k<6;k++)shared_min[k]=shared_top[k];}\n'
 hooks+='''void put(uint32_t a,uint32_t v){ram[a]=v>>24;ram[a+1]=v>>16;ram[a+2]=v>>8;ram[a+3]=v;}\nvoid word(uint32_t a,uint16_t v){ram[a]=v>>8;ram[a+1]=v;}\nvoid reg(unsigned k,uint32_t v){current.r[k]=v;}\nvoid sr(uint16_t v){current.sr=v;}\nvoid pc(uint32_t a){current.pc=a;shared_watch(a);}\nvoid snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}\nuint64_t stat(unsigned n,unsigned k){if(n==0)return shared_errors;if(n==1)return shared_C_outside;if(n==2)return shared_pending_total();if(n==3)return shared_entries[k];if(n==4)return shared_returns[k];if(n==5)return shared_fallbacks[k];if(n==6)return shared_attempts[k];return shared_C_observations[k];}\n'''
 source=out/'fixture.c';source.write_text(stub+body+hooks);lib=out/'fixture.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 f=c.CDLL(str(lib));f.put.argtypes=[c.c_uint32,c.c_uint32];f.word.argtypes=[c.c_uint32,c.c_uint16];f.reg.argtypes=[c.c_uint,c.c_uint32];f.sr.argtypes=[c.c_uint16];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint,c.c_uint];f.stat.restype=c.c_uint64
 names=['coordinate','input','face','scan','geometry','scene'];layout=[(16,832,1008),(144,608,816),(144,608,816),(272,416,592),(16,832,1008),(144,608,816)];syms=b['shared_Deck_symbols'];rows=[];task=0xc0928+6*1024;slot=b['deck_arena_address']+6*1024;sp=task+768
 elf=Path(b['directory'])/'five-build/native-shared.elf';table=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-readelf'),'-sW',str(elf)],text=True);(out/'ELF-symbols.txt').write_text(table);functions=[(int(x.split()[1],16),x.split()[7])for x in table.splitlines()if len(x.split())>=8 and x.split()[3]=='FUNC'and x.split()[6]=='1'];floor=min(a for a,_ in functions);assert floor==syms['midpoint']==syms['biwn_v4_scene_capture_end']+8
 def init(task_value=task,flags=0):
  f.clear();f.put(0xc0920,task_value);f.reg(15,sp);f.reg(0,0x12345678);f.reg(8,0xabcdef01);f.sr(flags)
 for k,name in enumerate(names):
  entry=syms['biwn_v4_'+name];fallback=syms['biwn_v4_'+name+'_original_fallback'];offset,low,top=layout[k];frame=slot+offset
  for address,symbol in functions:
   for depth,want in [(low,True),(top,True),(low-2,False),(top+2,False)]:
    init();f.pc(entry);f.reg(15,slot+depth);f.pc(address);assert f.stat(0,k)==0 and f.stat(1,k)==int(not want)and f.stat(2,k)==1 and f.stat(7,k)==int(want),(name,symbol,depth);rows.append(dict(group='C_floor',root=name,symbol=symbol,SP=depth,legal=want))
  for fault,task_value in [('zero',0),('unaligned',task+1),('bit8',task+256),('bit9',task+512),('end',0xc0928+101*1024)]:
   for flags in range(64):
    init(task_value,(0x2000 if flags>=32 else 0)|(flags%32));f.pc(entry);assert f.stat(2,k)==1;f.pc(fallback);assert f.stat(0,k)==f.stat(1,k)==f.stat(2,k)==0 and f.stat(3,k)==0 and f.stat(5,k)==f.stat(6,k)==1
   rows.append(dict(group='invalid_admission',root=name,fault=fault,legal=True,CCR_bank_cases=64))
  for fault in ['none','D0','A0','SP','SR','frame','stack','duplicate','missing']:
   init();f.put(frame+114,1)
   if fault!='missing':f.pc(entry)
   if fault=='D0':f.reg(0,0)
   if fault=='A0':f.reg(8,0)
   if fault=='SP':f.reg(15,sp+2)
   if fault=='SR':f.sr(1)
   if fault=='frame':f.put(frame,1)
   if fault=='stack':f.put(slot+low,1)
   if fault=='duplicate':f.pc(entry)
   f.pc(fallback);assert bool(f.stat(0,k))==(fault!='none'),(name,fault);assert f.stat(2,k)==0
   rows.append(dict(group='busy_fallback',root=name,fault=fault,legal=fault=='none'))
  for fault in ['D0','A0','SP','SR','task','missing','duplicate']:
   init(0)
   if fault!='missing':f.pc(entry)
   if fault=='D0':f.reg(0,0)
   if fault=='A0':f.reg(8,0)
   if fault=='SP':f.reg(15,sp+2)
   if fault=='SR':f.sr(1)
   if fault=='task':f.put(0xc0920,1)
   if fault=='duplicate':f.pc(entry)
   f.pc(fallback);assert f.stat(0,k)>0
   rows.append(dict(group='invalid_corruption',root=name,fault=fault,legal=False))
  init();f.pc(entry);f.reg(15,slot+low-2);f.pc(floor-2);assert f.stat(1,k)==0
 # The sixth root must commit the exact frame CPU/SR/PC and active logical bank.
 for fault in ['none','D0','D2','A0','A2','SP','SR','logical_PC','bank','active','error']:
  for flags in range(64):
   k=5;frame=slot+144;init(flags=(0x2000 if flags>=32 else 0)|(flags%32));f.pc(syms['biwn_v4_scene'])
   for i in range(16):f.put(frame+4+i*4,{0:0x12345678,8:0xabcdef01,15:sp}.get(i,0))
   f.word(frame+80,(0x2000 if flags>=32 else 0)|(flags%32));f.put(frame+68,0x17f12);f.put(frame+(76 if flags>=32 else 72),sp)
   if fault in ['D0','D2','A0','A2','SP']:f.reg({'D0':0,'D2':2,'A0':8,'A2':10,'SP':15}[fault],99)
   if fault=='SR':f.sr(0xffff)
   if fault=='logical_PC':f.put(frame+68,0)
   if fault=='bank':f.put(frame+(76 if flags>=32 else 72),0)
   if fault=='active':f.put(frame+114,1)
   if fault=='error':f.put(frame+94,1)
   f.pc(syms['biwn_v4_scene_return']);assert bool(f.stat(0,5))==(fault!='none')and f.stat(2,5)==0,(fault,flags)
  rows.append(dict(group='scene_commit',fault=fault,legal=fault=='none',CCR_bank_cases=64))
 save(out/'cases.json',rows);proof=dict(status='terminal_six_root_admission_C_floor_and_scene_commit_controls_pass',directory=str(out),fixture=str(source),fixture_library=str(lib),observer=g['observer'],ELF_C_functions=len(functions),C_floor=hex(floor),C_floor_legal_controls=len(functions)*6*2,C_floor_rejected_controls=len(functions)*6*2,invalid_admission_legal_cases=6*5*64,busy_fallback_controls=6*9,invalid_admission_corruption_controls=6*7,scene_commit_controls=11*64,new_predictions=0,new_training=False,host_guest_RAM_writes=0,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,gp,Path(g['observer']),source,lib,elf,out/'ELF-symbols.txt',out/'cases.json']},scope=__doc__+'Nativeentriescountacceptedbodyadmissions;attemptsandvalidatedfallbacksseparate.Invalidtaskfallbackmustpreserveall16registersandSR.Busyaliasfallbackalsopreserves118byteframeanddeclaredCstack.NativeCmustbelongtoexactlyonependingframe.Scenecommitchecksallregisters,SR,logicalPC,activebankandclearedactive/error.');save(out/'review.json',proof);save(V/'scene17-direct-dispatch-shared-observer-qualified-v1-current.json',proof);print(proof['status'],proof['ELF_C_functions'],proof['invalid_admission_legal_cases'])
if __name__=='__main__':main()

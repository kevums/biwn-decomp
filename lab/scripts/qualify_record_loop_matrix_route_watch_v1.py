"""Host-only call-site witness fault controls; zero guest execution or repair."""
import ctypes as c,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 bp=V/'native-record-loop-image-disc-build-v1-current.json';b=read(bp);helper=b['shared_Deck_symbols']['biwn_v4_scene_helper_return'];arena=b['deck_arena_address'];src=ROOT/'scripts/record_matrix_route_watch_v1.inc.c';watch=src.read_text().replace('MR_HELPER_RETURN',str(helper)+'u').replace('MR_ARENA',str(arena)+'u')
 out=V/'record-loop-matrix-route-watch-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 stub='#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000];\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}\nstatic void read_cpu(struct cpu *o){*o=current;}\n'
 hooks='''\nvoid clear(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(mr_pending,0,sizeof(mr_pending));memset(mr_entries,0,sizeof(mr_entries));memset(mr_returns,0,sizeof(mr_returns));mr_errors=mr_ignored=0;}\nvoid put(uint32_t a,uint32_t v){memory[a]=v>>24;memory[a+1]=v>>16;memory[a+2]=v>>8;memory[a+3]=v;}\nvoid sp(uint32_t a){current.r[15]=a;}\nvoid sr(uint16_t v){current.sr=v;}\nvoid pc(uint32_t a){mr_watch(a);}\nuint64_t stat(unsigned i){if(i<2)return mr_entries[i];if(i<4)return mr_returns[i-2];if(i==4)return mr_errors;if(i==5)return mr_pending_total();return mr_ignored;}\n'''
 source=out/'fixture.c';source.write_text(stub+watch+hooks);lib=out/'fixture.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 f=c.CDLL(str(lib));f.put.argtypes=[c.c_uint32,c.c_uint32];f.sp.argtypes=[c.c_uint32];f.sr.argtypes=[c.c_uint16];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64;rows=[]
 for native in [False,True]:
  for flags in range(64):
   for fault in ['none','duplicate','return_SP','return_SR','missing_entry','pending']+(['active','error','logical_PC','guest_SP','frame_link']if native else['invalid_task']):
    f.clear();task=0xc0928+6*1024;frame=arena+6*1024+144;sp=task+768;f.put(0xc0920,task);f.sp(sp);f.sr((0x2000 if flags>=32 else 0)|(flags%32));f.put(sp,helper if native else 0x172c4)
    if native:
     for a,v in [(frame+110,0x172c4),(frame+68,0xe220),(frame+114,1),(frame+106,sp),(frame+102,frame+4)]:f.put(a,v)
    mapping={'active':(frame+114,0),'error':(frame+94,1),'logical_PC':(frame+68,0),'guest_SP':(frame+106,sp+4),'frame_link':(frame+102,0),'invalid_task':(0xc0920,0)}
    if fault in mapping:f.put(*mapping[fault])
    if fault!='missing_entry':f.pc(0xe220)
    if fault=='duplicate':f.pc(0xe220)
    if fault=='pending':assert f.stat(5)==1 and f.stat(4)==0
    else:
     f.sp(sp+(8 if fault=='return_SP'else 4))
     if fault=='return_SR':f.sr(0xffff)
     f.pc(helper if native else 0x172c4)
     assert bool(f.stat(4))==(fault!='none'),(native,flags,fault,f.stat(4))
     if fault=='none':assert f.stat(0+int(native))==f.stat(2+int(native))==1 and f.stat(5)==0
    rows.append(dict(native=native,flags=flags,fault=fault,legal=fault=='none'))
 f.clear();f.put(0xc0920,0xc0928);f.sp(0xc0928+768);f.put(0xc0928+768,0x123456);f.pc(0xe220);assert f.stat(4)==f.stat(5)==0 and f.stat(6)==1
 save(out/'cases.json',rows);proof=dict(status='terminal_record_matrix_original_native_callsite_fault_controls_pass',directory=str(out),controls=len(rows),legal_controls=sum(x['legal']for x in rows),negative_controls=sum(not x['legal']for x in rows),all32CCR_both_banks=True,ignored_world_call_control=True,guest_execution=False,guest_RAM_writes=0,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,src,source,lib,out/'cases.json']});save(out/'review.json',proof);save(V/'record-loop-matrix-route-watch-qualified-v1-current.json',proof);print(proof['status'],len(rows),flush=True)
if __name__=='__main__':main()

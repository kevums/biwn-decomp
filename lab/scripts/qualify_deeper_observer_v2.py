"""Exact new geometry observer fault fixtures, not actual game execution."""
import ctypes as c,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import shared_deck_deeper_observer_v2 as monitor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-Deck-deeper-disc-build-v2-current.json';build=read(bp);parent=read(v/'native-Deck-coordinate-disc-build-current.json');text,old=monitor.observer_source(build,parent)
 out=v/'deeper-observer-qualification-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=out/'observer.c';source.write_text(text)
 direction=old.with_name('direction-shadow-model.c');library=out/'observer.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),str(direction),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 start=text.index('static unsigned g4_pending[101]');stop=text.index('static int32_t o6_retained_observe',start);dump_start=text.index('int geometry_dump(',stop);dump_end=text.index('static const uint32_t o6_inner_returns',dump_start)
 stub=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;static uint8_t memory[0x200000];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *o){*o=current;}
'''
 hooks=r'''
void reset(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));
memset(g4_pending,0,sizeof(g4_pending));memset(g4_helper_pending,0,sizeof(g4_helper_pending));memset(g4_native,0,sizeof(g4_native));memset(g4_marker_seen,0,sizeof(g4_marker_seen));memset(g4_order,0,sizeof(g4_order));memset(g4_transform_pending,0,sizeof(g4_transform_pending));
memset(g4_helpers,0,sizeof(g4_helpers));memset(g4_helper_returns,0,sizeof(g4_helper_returns));memset(g4_compiled,0,sizeof(g4_compiled));memset(g4_markers,0,sizeof(g4_markers));
g4_entries=g4_returns=g4_body_steps=g4_errors=g4_parent_returns=g4_transform_entries=g4_transform_returns=0;}
void reg(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void put(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}
void word(uint32_t a,uint16_t v){memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;}
void pc(uint32_t a){g4_watch(a);}
'''
 fixture=out/'fixture.c';fixture.write_text(stub+text[start:stop]+text[dump_start:dump_end]+hooks);lib=out/'fixture.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(fixture),'-o',str(lib)],capture_output=True,text=True);(out/'fixture-compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 f=c.CDLL(str(lib));f.reg.argtypes=[c.c_uint,c.c_uint32];f.put.argtypes=[c.c_uint32,c.c_uint32];f.word.argtypes=[c.c_uint32,c.c_uint16];f.pc.argtypes=[c.c_uint32];f.geometry_dump.argtypes=[c.c_char_p]
 variants=['legal_native','legal_original','bad_task','duplicate_public','wrong_argument','wrong_order','missing_marker','duplicate_marker','wrong_marker_target','wrong_frame_pointer','wrong_CPU_pointer','wrong_active','C_stack_outside','C_return_outside','wrong_virtual_SP','wrong_virtual_PC','wrong_C_return_SP','C_error','missing_C_return','missing_transform_return','wrong_transform_return_word','wrong_transform_return_SP','missing_helper','wrong_original_return_SP','wrong_outer_SP','wrong_outer_word','wrong_preserved_D2','wrong_saved_outer_PC','missing_geometry_return']
 s=build['shared_Deck_symbols'];rows=[]
 for name in variants:
  f.reset();native=name!='legal_original';slot=6;delta=slot*1024;base=build['deck_arena_address']+delta;frame=base+16;sp=0xc0928+delta+768;hsp=sp-16;csp=base+900;cret=s['biwn_v4_geometry_body'];outer=build['outer_arena_address']+slot*576+16
  put=f.put;reg=f.reg;pc=f.pc;put(0xc0920,1 if name=='bad_task'else 0xc0928+delta);reg(15,sp);reg(2,0xdead0012);reg(3,0xa55a1234);put(sp,build['outer_symbols']['biwn_outer_helper_return']);put(outer+106,sp);put(outer+110,0x11ee6 if name=='wrong_saved_outer_PC'else 0x11ee4);pc(0x11ad4)
  if name=='duplicate_public':pc(0x11ad4)
  if native:pc(s['biwn_v4_geometry'])
  targets=[0x10968,0x11384,0x10ba4,0x1142e,0x10734];logical=[0x11ae6,0x11b32,0x11b38,0x11b3e,0x11b44]
  if name=='wrong_order':targets[0],targets[2]=targets[2],targets[0]
  for h,target in enumerate(targets):
   if name=='missing_helper'and h==2:continue
   f.word(hsp+4,2 if name=='wrong_argument'and h==2 else 1);f.word(hsp+6,7)
   if native and h<3:
    reg(15,csp);put(csp,2 if name=='C_return_outside'and h==2 else cret);put(csp+4,frame+2 if name=='wrong_frame_pointer'and h==2 else frame);put(csp+12,frame+6 if name=='wrong_CPU_pointer'and h==2 else frame+4);put(csp+16,target)
    put(frame+114,0 if name=='wrong_active'and h==2 else 1);put(frame+64,hsp+2 if name=='wrong_virtual_SP'and h==2 else hsp);put(frame+68,target+2 if name=='wrong_virtual_PC'and h==2 else target);put(hsp,logical[h]);reg(15,base+820 if name=='C_stack_outside'and h==2 else csp);pc(s['service_geometry'])
    reg(15,csp-16);put(csp-12,frame);put(csp-8,target+2 if name=='wrong_marker_target'and h==2 else target)
    if not(name=='missing_marker'and h==2):pc(s['biwn_v5_deeper_helper_marker'])
    if name=='duplicate_marker'and h==2:pc(s['biwn_v5_deeper_helper_marker'])
    if h==1:
     reg(15,hsp-12);put(hsp-12,2 if name=='wrong_transform_return_word'else s['biwn_v4_geometry_helper_return']);put(frame+106,hsp-12);put(frame+110,0x113fe);pc(0x110d4);reg(15,hsp-6 if name=='wrong_transform_return_SP'else hsp-8)
     if name!='missing_transform_return':pc(s['biwn_v4_geometry_helper_return'])
    put(frame+94,3 if name=='C_error'and h==2 else 0);reg(15,csp+6 if name=='wrong_C_return_SP'and h==2 else csp+4)
    if not(name=='missing_C_return'and h==2):pc(cret)
   else:
    reg(15,hsp);put(hsp,s['biwn_v4_geometry_helper_return']if native else logical[h]);pc(target);reg(15,hsp+6 if name=='wrong_original_return_SP'and h==4 else hsp+4);pc(s['biwn_v4_geometry_helper_return']if native else logical[h])
  reg(15,sp+2 if name=='wrong_outer_SP'else sp)
  if name=='wrong_outer_word':put(sp,0x11ee6)
  if name=='wrong_preserved_D2':reg(2,0xdead0013)
  if name!='missing_geometry_return':pc(s['biwn_v4_geometry_return']if native else 0x11b4a)
  path=out/(name+'.json');assert f.geometry_dump(str(path).encode())==0;actual=read(path)
  accepted=actual['errors']==actual['pending']==0 and actual['entries']==actual['returns']==actual['matched_outer_parent_returns']==1 and actual['helper_entries']==actual['helper_returns']==[1]*5 and actual['compiled_helper_services']==actual['compiled_helper_markers']==([1,1,1,0,0]if native else[0]*5)and actual['transform_entries']==actual['transform_returns']==int(native)
  assert accepted==name.startswith('legal_'),(name,actual);rows.append(dict(case=name,accepted=accepted,counters=actual))
 save(out/'cases.json',rows);proof=dict(status='terminal_deeper_observer_two_legal_fault_controls_pass',directory=str(out),observer=str(source),observer_sha256=sha(source),legal_controls=2,rejected_fault_controls=len(rows)-2,actual_game_execution=False,source_sha256={str(p):sha(p)for p in[Path(__file__),Path(monitor.__file__),Path(monitor.__file__).with_name('deeper_geometry_observer_v2.inc.c'),source,library,fixture,lib,out/'cases.json']},scope=__doc__+' Read-only exact extracted geometry code; two legal modes and faults test order, arguments, logical context, real C returns, transform capture, parent state. Other retained monitors are separately qualified. No emulator/game fidelity claim.')
 save(out/'review.json',proof);save(v/'deeper-observer-qualified-v2-current.json',proof);print(proof['status'],len(rows)-2,flush=True)
if __name__=='__main__':main()

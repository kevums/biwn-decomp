"""Exact new geometry observer fault fixtures, not actual game execution."""
import ctypes as c,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import shared_deck_outer_compact_full_observer_v1 as monitor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-outer-compact-disc-build-v1-current.json';build=read(bp);parent=read(v/'native-Deck-coordinate-disc-build-current.json');text,old=monitor.observer_source(build,parent)
 out=v/'outer-compact-geometry-observer-qualification-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=out/'observer.c';source.write_text(text)
 direction=old.with_name('direction-shadow-model.c');library=out/'observer.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),str(direction),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 start=text.index('static unsigned g6_pending[101]');stop=text.index('static int32_t o6_retained_observe',start);dump_start=text.index('int geometry_dump(',stop);dump_end=text.index('static const uint32_t o6_inner_returns',dump_start)
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
memset(g6_pending,0,sizeof(g6_pending));memset(g6_calls,0,sizeof(g6_calls));memset(g6_active,0,sizeof(g6_active));g6_native_calls=g6_native_returns=g6_original_calls=g6_original_returns=g6_original_body_steps=g6_active_entries=g6_inactive_entries=0;
memset(g5_gpu_pending,0,sizeof(g5_gpu_pending));memset(g5_gpu_sp,0,sizeof(g5_gpu_sp));g5_native_gpu_entries=g5_native_gpu_returns=g5_original_gpu_entries=g5_original_gpu_returns=g5_original_faces_steps=0;
memset(g4_pending,0,sizeof(g4_pending));memset(g4_helper_pending,0,sizeof(g4_helper_pending));memset(g4_native,0,sizeof(g4_native));memset(g4_marker_seen,0,sizeof(g4_marker_seen));memset(g4_order,0,sizeof(g4_order));memset(g4_transform_pending,0,sizeof(g4_transform_pending));
memset(g4_helpers,0,sizeof(g4_helpers));memset(g4_helper_returns,0,sizeof(g4_helper_returns));memset(g4_compiled,0,sizeof(g4_compiled));memset(g4_markers,0,sizeof(g4_markers));
g4_entries=g4_returns=g4_body_steps=g4_errors=g4_parent_returns=g4_transform_entries=g4_transform_returns=g4_original_plane_entries=g4_original_plane_returns=g4_original_plane_steps=0;}
void reg(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void put(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}
void word(uint32_t a,uint16_t v){memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;}
void pc(uint32_t a){g4_watch(a);}
'''
 fixture=out/'fixture.c';fixture.write_text(stub+text[start:stop]+text[dump_start:dump_end]+hooks);lib=out/'fixture.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(fixture),'-o',str(lib)],capture_output=True,text=True);(out/'fixture-compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 f=c.CDLL(str(lib));f.reg.argtypes=[c.c_uint,c.c_uint32];f.put.argtypes=[c.c_uint32,c.c_uint32];f.word.argtypes=[c.c_uint32,c.c_uint16];f.pc.argtypes=[c.c_uint32];f.geometry_dump.argtypes=[c.c_char_p]
 variants=['legal_native','legal_original','legal_native_noGPU','legal_original_noGPU','wrong_faces_frame','wrong_faces_CPU','wrong_faces_target','wrong_faces_logical_PC','wrong_faces_logical_SP','wrong_faces_RTS_PC','wrong_GPU_SP','wrong_GPU_return_word','wrong_GPU_saved_return','wrong_GPU_active_CPU','wrong_GPU_C_stack','wrong_GPU_zero_argument','wrong_GPU_return_SP','duplicate_GPU_entry','missing_GPU_entry','missing_GPU_return','bad_task','duplicate_public','wrong_argument','wrong_order','missing_marker','duplicate_marker','wrong_marker_target','wrong_frame_pointer','wrong_CPU_pointer','wrong_active','C_stack_outside','C_return_outside','wrong_virtual_SP','wrong_virtual_PC','wrong_C_return_SP','C_error','missing_C_return','missing_transform_return','wrong_transform_return_word','wrong_transform_return_SP','missing_helper','wrong_original_return_SP','wrong_outer_SP','wrong_outer_word','wrong_preserved_D2','wrong_saved_outer_PC','missing_geometry_return','wrong_plane_frame','wrong_plane_CPU','wrong_plane_target','wrong_plane_logical_PC','wrong_plane_logical_SP','wrong_plane_RTS_PC','wrong_parent_RTS_PC']
 variants += ['legal_native_active','legal_original_active','legal_native_active_noGPU','legal_original_active_noGPU']
 variants += ['debug_'+x for x in ['frame','CPU','target','logical_PC','logical_SP','RTS_PC','budget_entry','service_entry','opaque_entry','active_entry','missing_C_return','wrong_C_return_SP','budget_restore','service_restore','opaque_restore','missing_dependency','duplicate_dependency','dependency_order','dependency_SP','dependency_word','saved_SP','saved_return','saved_CPU','C_stack','budget_capture','service_capture','opaque_capture','active_capture','logical_capture_PC','logical_capture_SP','return_SP','missing_dependency_return','unexpected_inactive_call']]
 variants += ['original_debug_'+x for x in ['dependency_word','dependency_SP','dependency_order','return_SP','missing_dependency_return','missing_dependency']]
 s=build['shared_Deck_symbols'];rows=[]
 for name in variants:
  f.reset();native=not name.startswith(('legal_original','original_debug_'))and name!='wrong_original_return_SP';slot=6;delta=slot*1024;base=build['deck_arena_address']+delta;frame=base+16;sp=0xc0928+delta+768;hsp=sp-16;csp=base+900;cret=s['biwn_v4_geometry_body'];outer=build['outer_arena_address']+slot*384+16
  put=f.put;reg=f.reg;pc=f.pc;put(0xc0920,1 if name=='bad_task'else 0xc0928+delta);reg(15,sp);reg(2,0xdead0012);reg(3,0xa55a1234);put(sp,build['outer_symbols']['biwn_outer_helper_return']);put(outer+106,sp);put(outer+110,0x11ee6 if name=='wrong_saved_outer_PC'else 0x11ee4);pc(0x11ad4)
  if name=='duplicate_public':pc(0x11ad4)
  if native:pc(s['biwn_v4_geometry'])
  active=('active'in name and name!='debug_unexpected_inactive_call')or name.startswith(('debug_','original_debug_'));f.word(0x403cc,0 if name=='debug_unexpected_inactive_call'else int(active))
  targets=[0x10968,0x11384,0x10ba4,0x1142e,0x10734];logical=[0x11ae6,0x11b32,0x11b38,0x11b3e,0x11b44]
  if name=='wrong_order':targets[0],targets[2]=targets[2],targets[0]
  def dependencies():
   if not active and name!='debug_unexpected_inactive_call':return
   logical_returns=[0x107aa,0x107d2,0x107e6,0x10808,0x1081c,0x1083e,0x10852,0x10874,0x10888,0x108aa,0x108be,0x108e0,0x108f6,0x10918,0x10938,0x1095a]
   for j,logical_return in enumerate(logical_returns):
    if j==0 and name.endswith('missing_dependency'):continue
    depSP=hsp-(108 if j%2 else 84);depPC=0x149ae if j%2 else 0x1b45a
    corrupt=j==0
    if native:
     put(frame+90,14-j if corrupt and name=='debug_budget_capture'else 15-j);put(frame+82,0 if corrupt and name=='debug_service_capture'else s['service_geometry_debug_helpers']);put(frame+86,0 if corrupt and name=='debug_opaque_capture'else frame);put(frame+114,0 if corrupt and name=='debug_active_capture'else 1)
     put(frame+98,base+820 if corrupt and name=='debug_C_stack'else base+850);put(frame+102,frame+6 if corrupt and name=='debug_saved_CPU'else frame+4);put(frame+106,depSP+2 if corrupt and name=='debug_saved_SP'else depSP);put(frame+110,logical_return+2 if corrupt and name=='debug_saved_return'else logical_return)
     put(frame+64,depSP+2 if corrupt and name=='debug_logical_capture_SP'else depSP);put(frame+68,depPC+2 if corrupt and name=='debug_logical_capture_PC'else depPC)
    put(depSP,2 if corrupt and name.endswith('dependency_word')else s['biwn_v4_geometry_helper_return']if native else logical_return)
    reg(15,depSP+2 if corrupt and name.endswith('dependency_SP')else depSP);pc((0x149ae if depPC==0x1b45a else 0x1b45a)if corrupt and name.endswith('dependency_order')else depPC)
    if corrupt and name=='debug_duplicate_dependency':pc(depPC)
    reg(15,depSP+6 if corrupt and name.endswith('return_SP')else depSP+4)
    if not(corrupt and name.endswith('missing_dependency_return')):pc(s['biwn_v4_geometry_helper_return']if native else logical_return)
   if native:
    put(frame+90,3 if name=='debug_budget_restore'else 2);put(frame+82,0 if name=='debug_service_restore'else s['service_geometry']);put(frame+86,0 if name=='debug_opaque_restore'else frame);put(frame+114,1)
  for h,target in enumerate(targets):
   if name=='missing_helper'and h==2:continue
   f.word(hsp+4,2 if name=='wrong_argument'and h==2 else 1);f.word(hsp+6,7)
   if native and h<5:
    reg(15,csp);put(csp,2 if name=='C_return_outside'and h==2 else cret);put(csp+4,frame+2 if name=='wrong_frame_pointer'and h==2 else frame);put(csp+12,frame+6 if name=='wrong_CPU_pointer'and h==2 else frame+4);put(csp+16,target)
    put(frame+114,0 if name=='wrong_active'and h==2 else 1);put(frame+64,hsp+2 if name=='wrong_virtual_SP'and h==2 else hsp);put(frame+68,target+2 if name=='wrong_virtual_PC'and h==2 else target);put(hsp,logical[h]);reg(15,base+820 if name=='C_stack_outside'and h==2 else csp)
    if h==3:
     put(csp+4,frame+2 if name=='wrong_faces_frame'else frame);put(csp+12,frame+6 if name=='wrong_faces_CPU'else frame+4);put(csp+16,0x11430 if name=='wrong_faces_target'else target)
     put(frame+68,0x11430 if name=='wrong_faces_logical_PC'else target);put(frame+64,hsp+2 if name=='wrong_faces_logical_SP'else hsp)
    if h==4:
     put(csp+4,frame+2 if name=='debug_frame'else frame);put(csp+12,frame+6 if name=='debug_CPU'else frame+4);put(csp+16,target+2 if name=='debug_target'else target)
     put(frame+68,target+2 if name=='debug_logical_PC'else target);put(frame+64,hsp+2 if name=='debug_logical_SP'else hsp);put(frame+90,3 if name=='debug_budget_entry'else 2);put(frame+82,0 if name=='debug_service_entry'else s['service_geometry']);put(frame+86,0 if name=='debug_opaque_entry'else frame);put(frame+114,0 if name=='debug_active_entry'else 1)
    pc(s['service_geometry_debug']if h==4 else s['service_geometry_faces']if h==3 else s['service_geometry'])
    if h<3:
     reg(15,csp-16);put(csp-12,frame);put(csp-8,target+2 if name=='wrong_marker_target'and h==2 else target)
     if not(name=='missing_marker'and h==2):pc(s['biwn_v5_deeper_helper_marker'])
     if name=='duplicate_marker'and h==2:pc(s['biwn_v5_deeper_helper_marker'])
    if h==1:
     nested=csp-40;plane_ret=s['biwn_v4_coordinate_body'];put(nested,plane_ret);put(nested+4,frame+2 if name=='wrong_plane_frame'else frame);put(nested+12,frame+6 if name=='wrong_plane_CPU'else frame+4);put(nested+16,0x110d6 if name=='wrong_plane_target'else 0x110d4)
     put(frame+68,0x110d6 if name=='wrong_plane_logical_PC'else 0x110d4);put(frame+64,hsp-16 if name=='wrong_plane_logical_SP'else hsp-18);put(hsp-18,2 if name=='wrong_transform_return_word'else 0x113fe);reg(15,nested);pc(s['service_geometry_original'])
     put(frame+68,0x1117a if name=='wrong_plane_RTS_PC'else 0x11382);reg(15,nested+6 if name=='wrong_transform_return_SP'else nested+4)
     if name!='missing_transform_return':pc(plane_ret)
    if h==3 and not name.endswith('noGPU'):
     gpu=hsp-58;put(frame+64,gpu);put(frame+68,0xe26c);put(frame+106,gpu);put(frame+110,0x11686 if name=='wrong_GPU_saved_return'else 0x11684);put(frame+102,frame+6 if name=='wrong_GPU_active_CPU'else frame+4);put(frame+98,base+820 if name=='wrong_GPU_C_stack'else base+850)
     put(gpu,2 if name=='wrong_GPU_return_word'else s['biwn_v4_geometry_helper_return']);f.word(gpu+20,1 if name=='wrong_GPU_zero_argument'else 0);reg(15,gpu+2 if name=='wrong_GPU_SP'else gpu)
     if name!='missing_GPU_entry':pc(0xe26c)
     if name=='duplicate_GPU_entry':pc(0xe26c)
     reg(15,gpu+6 if name=='wrong_GPU_return_SP'else gpu+4)
     if name!='missing_GPU_return':pc(s['biwn_v4_geometry_helper_return'])
    if h==4:dependencies()
    put(frame+64,hsp);put(frame+68,0x1098e if h==0 else 0x1142c if h==1 else 0x10c16 if h==2 else 0x1175e if name=='wrong_faces_RTS_PC'else 0x11760 if h==3 else 0x10964 if name=='debug_RTS_PC'else 0x10966)
    if name=='wrong_parent_RTS_PC'and h==2:put(frame+68,0x10c14)
    put(frame+94,3 if name=='C_error'and h==2 else 0);reg(15,csp+6 if (name=='wrong_C_return_SP'and h==2)or(name=='debug_wrong_C_return_SP'and h==4)else csp+4)
    if not(name=='missing_C_return'and h==2 or name=='debug_missing_C_return'and h==4):pc(cret)
   else:
    reg(15,hsp);put(hsp,s['biwn_v4_geometry_helper_return']if native else logical[h]);pc(target)
    if not native and h==1:
     reg(15,hsp-18);put(hsp-18,0x113fe);pc(0x110d4);pc(0x11382);reg(15,hsp-14);pc(0x113fe)
    if h==3 and not name.endswith('noGPU'):
     gpu=hsp-58;put(gpu,0x11684);f.word(gpu+20,0);reg(15,gpu);pc(0xe26c);reg(15,gpu+4);pc(0x11684)
    if h==4:dependencies()
    reg(15,hsp+6 if name=='wrong_original_return_SP'and h==4 else hsp+4);pc(s['biwn_v4_geometry_helper_return']if native else logical[h])
  reg(15,sp+2 if name=='wrong_outer_SP'else sp)
  if name=='wrong_outer_word':put(sp,0x11ee6)
  if name=='wrong_preserved_D2':reg(2,0xdead0013)
  if name!='missing_geometry_return':pc(s['biwn_v4_geometry_return']if native else 0x11b4a)
  path=out/(name+'.json');assert f.geometry_dump(str(path).encode())==0;actual=read(path)
  accepted=actual['errors']==actual['pending']==0 and actual['entries']==actual['returns']==actual['matched_outer_parent_returns']==1 and actual['helper_entries']==actual['helper_returns']==[1]*5 and actual['compiled_helper_services']==actual['compiled_helper_markers']==([1]*5 if native else[0]*5)and actual['transform_entries']==actual['transform_returns']==int(native)and actual['original_transform_entries']==actual['original_transform_returns']==int(not native)
  want_GPU=0 if name.endswith('noGPU')else 1
  accepted=accepted and actual['native_GPU_entries']==actual['native_GPU_returns']==(want_GPU if native else 0)and actual['original_GPU_entries']==actual['original_GPU_returns']==(0 if native else want_GPU)
  want_debug=16 if active else 0
  accepted=accepted and actual['native_debug_dependency_entries']==actual['native_debug_dependency_returns']==(want_debug if native else 0)and actual['original_debug_dependency_entries']==actual['original_debug_dependency_returns']==(0 if native else want_debug)
  assert accepted==name.startswith('legal_'),(name,actual);rows.append(dict(case=name,accepted=accepted,counters=actual))
 save(out/'cases.json',rows);proof=dict(status='terminal_six_helper_observer_legal_and_fault_controls_pass',directory=str(out),observer=str(source),observer_sha256=sha(source),legal_controls=8,rejected_fault_controls=len(rows)-8,actual_game_execution=False,source_sha256={str(p):sha(p)for p in[Path(__file__),Path(monitor.__file__),Path(monitor.__file__).with_name('outer_compact_debug_geometry_observer_v1.inc.c'),source,library,fixture,lib,out/'cases.json']},scope=__doc__+' Read-only exact extracted geometry code; eight legal modes and faults test order, arguments, logical context, real C returns, transform capture, parent state. Other retained monitors are separately qualified. No emulator/game fidelity claim.')
 save(out/'review.json',proof);save(v/'outer-compact-geometry-observer-qualified-v1-current.json',proof);print(proof['status'],len(rows)-8,flush=True)
if __name__=='__main__':main()

"""Read-only exact geometry monitor over combined original/native CPU execution.
RAM and register snapshots are copied into a separate host observer fixture.
Original outer/caller/helper bodies execute; GPU/formatter/text effects remain
explicit component fixtures. This is not fresh gameplay or an IRQ test.
"""
import ctypes as c,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import check_native_deck_outer_connected_debug_v1 as connected
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 proof=read(V/'debug-observer-qualified-v1-current.json')
 for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 out=V/'debug-observer-actual-CPU-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 fixture=Path(proof['directory'])/'fixture.c';text=fixture.read_text();start=text.index(' unsigned relevant=',text.index('static void g4_watch('));end=text.index(' if(!relevant)return;',start)
 extras='\nvoid snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}\nint wants(uint32_t pc){'+text[start:end]+'return relevant!=0;}\n'
 source=out/'fixture.c';source.write_text(text+extras);lib=out/'fixture.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.wants.argtypes=[c.c_uint32];f.wants.restype=c.c_int;f.pc.argtypes=[c.c_uint32];f.geometry_dump.argtypes=[c.c_char_p]
 rows=[]
 class Observed(connected.Engine):
  observing=False
  def cpu(self):
   state=super().cpu()
   if self.observing and f.wants(state.pc):
    raw=self.native.device.ram();f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
   return state
  def run(self,*args):
   native=args[-1];f.reset();self.observing=True
   try:result=super().run(*args)
   finally:self.observing=False
   path=out/('lane-'+str(len(rows))+'.json');assert f.geometry_dump(str(path).encode())==0;x=read(path);n=x['entries']
   assert x['errors']==x['pending']==0 and x['returns']==x['matched_outer_parent_returns']==n,x
   assert x['helper_entries']==x['helper_returns']==[n]*5,x
   assert x['compiled_helper_services']==x['compiled_helper_markers']==([n]*5 if native else[0]*5),x
   assert x['transform_entries']==x['transform_returns']==(n if native else 0),x
   assert x['original_transform_entries']==x['original_transform_returns']==(0 if native else n),x
   want=x['debug_active_entries']*16
   assert x['native_debug_dependency_entries']==x['native_debug_dependency_returns']==(want if native else 0),x
   assert x['original_debug_dependency_entries']==x['original_debug_dependency_returns']==(0 if native else want),x
   rows.append(dict(native=native,**x));return result
 connected.Engine=Observed;sys.argv=[sys.argv[0],'--limit','32'];connected.main()
 assert len(rows)==64 and sum(x['debug_active_entries']for x in rows)==6 and sum(x['debug_inactive_entries']for x in rows)==2
 save(out/'cases.json',rows);paths=[Path(__file__),Path(connected.__file__),V/'debug-observer-qualified-v1-current.json',fixture,source,lib,out/'cases.json']
 result=dict(status='terminal_exact_debug_observer_actual_combined_CPU_contracts_match',directory=str(out),CPU_lanes=len(rows),geometry_calls=sum(x['entries']for x in rows),active_debug_calls=sum(x['debug_active_entries']for x in rows),original_and_native_dependency_calls=sum(x['native_debug_dependency_entries']+x['original_debug_dependency_entries']for x in rows),host_guest_RAM_writes=0,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__)
 save(out/'review.json',result);save(V/'debug-observer-actual-CPU-v1-current.json',result);print(result['status'],flush=True)
if __name__=='__main__':main()

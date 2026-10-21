"""Wire accepted local wait C ahead of a separate native-image static provider."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 pp=ROOT/'verification/native-formatter-C-runtime-preparation-current.json';prep=json.loads(pp.read_text());candidatep=Path(prep['candidate']);candidate=json.loads(candidatep.read_text());assert sha(candidate['library'])
 checkp=ROOT/'verification/GPU-wait-local-C-check-current.json';check=json.loads(checkp.read_text());assert check['accepted']and check['cases']==8192 and check['failed_cases']==0
 authorp=Path(check['author_proof']);author=json.loads(authorp.read_text());source=Path(check['source']);assert sha(source)==check['source_text_sha256']==author['source_text_sha256']
 out=ROOT/'verification/native-formatter-C-bridge'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 wrapper=out/'wait-dispatch.c';wrapper.write_text('''#include "biwn_input_dispatch_cpu.h"
extern int biwn_GPU_wait_repair_step(struct biwn_world_bus*,struct biwn_task_cpu*);
extern int biwn_native_formatter_translated_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);
int biwn_native_formatter_wait_C_step(struct biwn_world_bus*b,struct biwn_task_cpu*s,biwn_input_write8 w,biwn_world_cpu_service service,void*context){
 if(!s)return 1;
 switch(s->pc){case 0xe098:case 0x162708:case 0x162712:case 0x162714:case 0x16271e:case 0x162720:return biwn_GPU_wait_repair_step(b,s);default:return biwn_native_formatter_translated_step(b,s,w,service,context);}
}
''');library=out/'libnative-formatter-wait-C.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(wrapper),str(source),candidate['library'],'-o',str(library)];built=subprocess.run(cmd,capture_output=True,text=True);(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
 cp=out/'CPU-candidate.json';cdata={**candidate,'library':str(library),'function':'biwn_native_formatter_wait_C_step','status':'compiled_native_formatter_with_guided_local_wait_C_pending_runtime','directory':str(out),'translated_provider':candidate['library'],'local_wait_C':str(source),'local_wait_C_sha256':sha(source),'local_wait_gate':str(checkp),'local_wait_gate_sha256':sha(checkp),'source_origin':'Local Code Author guided revision for six fixed wait entries; coordinator static compilation of other native-image instructions; older original-game C providers inherited. Not new originalgame instructioncoverage.'}
 for pc in [0xe098,0x162708,0x162712,0x162714,0x16271e,0x162720]:cdata['selected_case_sources'][hex(pc)]='local_guided_GPU_wait_repair.c'
 save(cp,cdata)
 bridgep=out/'native-CPU-candidate.json';builder=ROOT/'scripts/build_biwn_fast_CPU_bridge.py';private=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source';cost=ROOT/'verification/main-static-cycle-cost-experimental-candidate.json';cmd=[str(ROOT/'.venv/bin/python'),'-u',str(builder),'--CPU-candidate',str(cp),'--candidate-output',str(bridgep),'--CPU-private-source',str(private),'--cost-candidate',str(cost)]
 built=subprocess.run(cmd,capture_output=True,text=True);(out/'bridge-build.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stdout+built.stderr;bridge=json.loads(bridgep.read_text());assert bridge['required_core_sha256']==sha(private/'virtualjaguar_libretro.dylib')
 paths=[Path(__file__),pp,candidatep,Path(candidate['library']),Path(candidate['directory'])/'biwn_route_CPU.c',ROOT/'scripts/native_formatter_C_semantics.py',ROOT/'verification/native-formatter-C-runtime-preparation/20261018T230147.967195Z/build-native-provider.py',checkp,authorp,source,wrapper,library,cp,bridgep,builder,cost,Path(bridge['library']),Path(bridge['directory'])/'fast_CPU_bridge.c']
 state=dict(status='terminal_native_formatter_C_bridge_compiled_pending_runtime',directory=str(out),CPU_candidate=str(cp),native_CPU_candidate=str(bridgep),instruction_atlas=candidate['instruction_RAM_source'],atlas_is_not_a_checkpoint=True,selected_static_cases=len(cdata['selected_case_sources']),local_guided_wait_entries=6,local_wait_C_native_cases=8192,all_additional_original_game_coverage_claims=False,full_game_complete=False,new_training=False,default_promoted=False,source_sha256={str(p):sha(p)for p in paths})
 save(out/'build.json',state);save(ROOT/'verification/native-formatter-C-bridge-current.json',state)
 # Original compile-failed preparation receipt stays historical; this receipt
 # binds the separately completed extension and its actual generated C.
 print(json.dumps({k:state[k]for k in ['status','CPU_candidate','native_CPU_candidate','selected_static_cases']}),flush=True)
if __name__=='__main__':main()

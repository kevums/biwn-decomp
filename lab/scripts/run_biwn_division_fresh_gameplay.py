"""Fresh gameplay of the checked division provider; reuse an immutable native control.

The only added wrapper observes division-provider calls. It changes no guest
state, instruction result or cost. The active long route keeps its own backend.
"""
import ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from check_biwn_division_CPU import inventory

def read(path):return json.loads(Path(path).read_text())

def main():
    publicationp=ROOT/'verification/CPU-division-exception-publication-current.json';publication=read(publicationp)
    assert publication['status']=='terminal_division_exception_component_and_local_C_verified'
    buildp=ROOT/'verification/CPU-division-provider-build-current.json';build=read(buildp);cp=Path(build['CPU_candidate']);candidate=read(cp);atlas,entries=inventory(candidate)
    priorp=ROOT/'verification/native-formatter-C-processors/20261018T233023.397005Z/protocol.json';prior=read(priorp)
    assert prior['status']=='terminal_fresh_C_processors_equal' and prior['frames']==1600 and prior['sprint']
    oldprobe=Path(prior['directory'])/'probe.py';assert sha(oldprobe)==prior['source_sha256'][str(oldprobe)]
    reference=Path(prior['directory'])/'reference';assert sha(reference/'report.json')==prior['report_sha256']['reference']
    out=ROOT/'verification/CPU-division-fresh-gameplay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    wrapper=out/'division-observer.c'
    text='''#include <stdint.h>
#include "biwn_input_dispatch_cpu.h"
extern int biwn_division_checked_CPU_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);
struct counts {uint64_t total,unsigned_steps,signed_steps,zero_exceptions,normal_returns,errors;};
static struct counts counters;
int biwn_counted_division_CPU_step(struct biwn_world_bus*b,struct biwn_task_cpu*s,biwn_input_write8 w,biwn_world_cpu_service service,void*context){
 unsigned kind=0;int status;if(s)switch(s->pc){
'''
    for row in entries:text+='case '+hex(row['pc'])+'u:kind='+str(2 if row['signed'] else 1)+';break;\n'
    text+='''default:break;}
 status=biwn_division_checked_CPU_step(b,s,w,service,context);
 if(kind){counters.total++;if(kind==1)counters.unsigned_steps++;else counters.signed_steps++;if(status==11)counters.zero_exceptions++;else if(status==0)counters.normal_returns++;else counters.errors++;}
 return status;
}
const struct counts*biwn_division_observer_counts(void){return &counters;}
'''
    wrapper.write_text(text);library=out/'libdivision-observer.dylib';rest=ROOT/'projects/black-ice-white-noise/restoration'
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(rest),str(wrapper),candidate['library'],'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    counted={**candidate,'function':'biwn_counted_division_CPU_step','library':str(library),'directory':str(out),'status':'compiled_observation_wrapper_pending_gameplay'}
    countedp=out/'CPU-candidate.json';save(countedp,counted);nativep=out/'native-CPU-candidate.json'
    core_source=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source'
    command=[str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/build_biwn_fast_CPU_bridge.py'),'--CPU-candidate',str(countedp),'--candidate-output',str(nativep),'--CPU-private-source',str(core_source),'--cost-candidate',build['cost_candidate']]
    result=subprocess.run(command,capture_output=True,text=True);(out/'bridge-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr;native=read(nativep)
    source=oldprobe.read_text();old_native=read(ROOT/'verification/native-formatter-C-bridge-current.json')['native_CPU_candidate']
    assert source.count(repr(old_native))==1;source=source.replace(repr(old_native),repr(str(nativep)))
    marker="        report['C_processor_backends']=finish_processors()";assert source.count(marker)==1
    observe=f'''
        division_observer=c.CDLL({str(library)!r})
        class DivisionCounts(c.Structure):
            _fields_=[(name,c.c_uint64) for name in ['total','unsigned_steps','signed_steps','zero_exceptions','normal_returns','errors']]
        division_observer.biwn_division_observer_counts.restype=c.POINTER(DivisionCounts)
        dcounts=division_observer.biwn_division_observer_counts().contents
        report['division_provider_counts']={{name:getattr(dcounts,name) for name,_ in DivisionCounts._fields_}}
'''
    source=source.replace(marker,observe+marker);probe=out/'probe.py';compile(source,str(probe),'exec');probe.write_text(source)
    cmd=list(next(row['command']for row in prior['commands']if row['lane']=='C'));cmd[2]=str(probe);cmd[cmd.index('--output')+1]=str(out/'C')
    control=read(reference/'report.json')
    assert sha(Path(cmd[cmd.index('--core')+1]))==control['core_sha256']
    assert sha(Path(cmd[cmd.index('--disc')+1]))==control['disc_sha256']
    inputp=Path(cmd[cmd.index('--frame-controller-script')+1]);assert sha(inputp)==prior['source_sha256'][str(inputp)]
    deps=[out/'runner-as-run.py',publicationp,buildp,cp,Path(candidate['library']),priorp,oldprobe,reference/'report.json',reference/'frontend-PCM.s16le',inputp,wrapper,library,countedp,nativep,Path(native['library']),Path(native['directory'])/'fast_CPU_bridge.c',Path(native['cost_library']),probe]
    state=dict(status='running_fresh_division_C_gameplay',pid=os.getpid(),directory=str(out),frames=1600,command=cmd,
        reference=str(reference),reference_reused=True,reference_scope='Exact prior fresh native run, same core/disc/input bytes; reference not rerun in this experiment.',
        source_sha256={str(p):sha(p)for p in deps},new_training=False,default_promoted=False,checkpoint_restores=0,host_guest_RAM_writes=0,
        separate_long_merchant_job_unchanged=True,scope='Fresh C CPU/GPU/DSP/IRQ run of the repaired disc, using the checked division provider plus read-only call counters. Compare every recorded frame and PCM with immutable native control. No new zero fault is assumed in ordinary gameplay.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/CPU-division-fresh-gameplay-active.json',state)
    mark()
    try:
        with (out/'C.log').open('w')as log:
            child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();exit_code=child.wait()
        state['exit_code']=exit_code
        if exit_code:
            state.update(status='terminal_fresh_division_gameplay_child_rejected');mark();return
        game=read(out/'C/report.json');assert game['core_sha256']==control['core_sha256'] and game['disc_sha256']==control['disc_sha256']
        assert len(game['frames'])==len(control['frames'])==1600
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
        comparisons={name:sum(a[name]!=b[name]for a,b in zip(game['frames'],control['frames']))for name in fields}
        counts=game['division_provider_counts'];assert counts['total']>0 and counts['errors']==0 and counts['total']==counts['unsigned_steps']+counts['signed_steps']==counts['zero_exceptions']+counts['normal_returns']
        CPU=game['C_CPU_backend'];backends=game['C_processor_backends']
        assert CPU['stats']['errors']==CPU['counts']['Original']==CPU['counts']['Rejected']==0
        assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
        assert backends['DSP']['core_counts']['Original']==backends['DSP']['core_counts']['Rejected']==backends['DSP']['errors']==0
        assert all(backends['IRQ'][kind][name]==0 for kind in ['core','selection']for name in ['Original','Rejected'])
        PCM_equal=sha(out/'C/frontend-PCM.s16le')==sha(reference/'frontend-PCM.s16le')
        state.update(status='terminal_fresh_division_gameplay_equal'if not any(comparisons.values())and PCM_equal else'terminal_fresh_division_gameplay_diverged',
            comparisons=comparisons,audio_PCM_equal=PCM_equal,division_provider_counts=counts,C_CPU_backend=CPU,C_processor_backends=backends,
            report_sha256=sha(out/'C/report.json'),ordinary_gameplay_zero_exception_verified=bool(counts['zero_exceptions']))
        mark();save(ROOT/'verification/CPU-division-fresh-gameplay-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','comparisons','audio_PCM_equal','division_provider_counts','ordinary_gameplay_zero_exception_verified']}),flush=True)
    except BaseException as error:state.update(status='terminal_fresh_division_gameplay_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()

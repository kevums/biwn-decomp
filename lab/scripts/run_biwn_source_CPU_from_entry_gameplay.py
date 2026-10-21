"""Fresh 1600-frame sprint gameplay from HLE-prepared initial CPU entry with source GPU/DSP/IRQ."""
import json,subprocess,os
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())

def main():
    bp=ROOT/'verification/bootstrap-CPU-build-current.json';build=read(bp);assert build['status']=='terminal_bootstrap_CPU_compiled_pending_execution'
    dp=ROOT/'verification/CPU-division-fresh-gameplay-current.json';division=read(dp);assert division['status']=='terminal_fresh_division_gameplay_equal'
    template=Path(division['directory'])/'probe.py';assert sha(template)==division['source_sha256'][str(template)]
    ip=ROOT/'verification/pre-mainstage-CPU-inventory-current.json';inventory=read(ip);assert inventory['status']=='terminal_read_only_bootstrap_inventory_equal'
    reference=Path(division['reference']);control=read(reference/'report.json');assert sha(reference/'report.json')==division['source_sha256'][str(reference/'report.json')]
    out=ROOT/'verification/source-CPU-from-entry-gameplay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    text=template.read_text();old_native=str(Path(division['directory'])/'native-CPU-candidate.json');assert text.count(repr(old_native))==1;text=text.replace(repr(old_native),repr(build['native_CPU_candidate']))
    marker='        owner,retired,CPU_library,CPU_host,finish_CPU=CPU_bridge.install('
    assert text.count(marker)==1
    text=text.replace(marker,"        core.BIWNCPUOriginalInstructionCount.restype=c.c_uint64\n        original_before_owner_install=core.BIWNCPUOriginalInstructionCount()\n"+marker)
    start=text.index("        entry_gate={'armed':False");stop=text.index('        core.BIWNSetCPUExecOwner(gate,0)',start)+len('        core.BIWNSetCPUExecOwner(gate,0)')
    text=text[:start]+"        entry_gate=dict(armed=True,bootstrap_native_callbacks=0,source_from_initial_entry=True,original_before_owner_install=original_before_owner_install)"+text[stop:]
    marker="        report['source_C_execution']=args.CPU_mode=='C'";assert text.count(marker)==1
    text=text.replace(marker,marker+"\n        report['C_CPU_backend']['scope']='SourceCPUfromHLEpreparedinitialPC,not gatedat4000; no originalCPUopcodefallback duringthe testedframes. SourceGPU/DSP/IRQ selection+entry; platformHLE,devices,blitter/OP,IRQlines+ACK/commit/prefetch/emulatorcostservices retained.'")
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(division['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'C');command[command.index('--frames')+1]='1600';input_path=Path(command[command.index('--frame-controller-script')+1]);assert sha(input_path)==division['source_sha256'][str(input_path)]
    assert sha(Path(command[command.index('--core')+1]))==control['core_sha256'] and sha(Path(command[command.index('--disc')+1]))==control['disc_sha256']
    state=dict(status='running_source_CPU_from_initial_entry',pid=os.getpid(),directory=str(out),command=command,reference=str(reference),reference_reused=True,frames=1600,new_training=False,default_promoted=False,host_guest_RAM_writes=0,checkpoint_restores=0,
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',bp,dp,ip,template,probe,Path(build['CPU_candidate']),Path(build['native_CPU_candidate']),reference/'report.json',reference/'frontend-PCM.s16le',input_path]},
        scope='Fresh HLE-prepared image entry with strictC CPU from frame1 plus sourceGPU/DSP/IRQ. Reuses exact same-core/disc 1600frame sprint native control. HLE preparation,device/clock/IRQhost services remain; not authenticatedfirmware/standalonehardwareproof.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/source-CPU-from-entry-gameplay-active.json',state)
    mark()
    try:
        with(out/'C.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();exit_code=child.wait()
        state['exit_code']=exit_code
        if exit_code:state['status']='terminal_source_CPU_entry_child_rejected';mark();print((out/'C.log').read_text()[-1800:],flush=True);return
        game=read(out/'C/report.json');assert len(game['frames'])==len(control['frames'])==1600
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];comparisons={name:sum(a[name]!=b[name]for a,b in zip(game['frames'],control['frames']))for name in fields}
        CPU=game['C_CPU_backend'];backends=game['C_processor_backends']
        assert CPU['entry_gate']['original_before_owner_install']==0 and CPU['counts']['Original']==CPU['counts']['Rejected']==CPU['stats']['errors']==0 and CPU['stats']['steps']>0
        assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
        assert backends['DSP']['core_counts']['Original']==backends['DSP']['core_counts']['Rejected']==backends['DSP']['errors']==0
        assert all(backends['IRQ'][kind][name]==0 for kind in ['core','selection']for name in ['Original','Rejected'])
        PCM_equal=sha(out/'C/frontend-PCM.s16le')==sha(reference/'frontend-PCM.s16le')
        state.update(status='terminal_source_CPU_from_entry_gameplay_equal'if not any(comparisons.values())and PCM_equal else'terminal_source_CPU_entry_diverged',comparisons=comparisons,PCM_equal=PCM_equal,C_CPU_backend=CPU,C_processor_backends=backends,division_provider_counts=game['division_provider_counts'],report_sha256=sha(out/'C/report.json'),original_CPU_instructions_before_or_during_window=0)
        mark();save(ROOT/'verification/source-CPU-from-entry-gameplay-current.json',state);print(json.dumps({k:state[k]for k in ['status','comparisons','PCM_equal','C_CPU_backend','division_provider_counts']}),flush=True)
    except BaseException as error:state.update(status='terminal_source_CPU_entry_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()

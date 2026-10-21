"""Fresh initial-entry C CPU/GPU/DSP/IRQ merchant route with the repaired DSP catalogue."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    window_path=ROOT/'verification/external-DSP-live-window-current.json';window=read(window_path)
    assert window['status']=='terminal_external_DSP_live_window_equal' and window['external_instructions']==460 and window['PCM_prefix_byte_equal']
    cp=Path(window['candidate']);candidate=read(cp);assert sha(cp)==window['source_sha256'][str(cp)]
    initial_path=ROOT/'verification/source-CPU-from-entry-gameplay-current.json';initial=read(initial_path);assert initial['status']=='terminal_source_CPU_from_entry_gameplay_equal'
    failed_path=ROOT/'verification/native-formatter-C-processors/20261018T233557.255349Z/protocol.json';failed=read(failed_path);reference=Path(failed['directory'])/'reference';control=read(reference/'report.json')
    assert len(control['frames'])==24975
    template=Path(initial['directory'])/'probe.py';assert sha(template)==initial['source_sha256'][str(template)]
    out=ROOT/'verification/external-DSP-combined-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    long_template=Path(failed['directory'])/'probe.py';assert sha(long_template)==failed['source_sha256'][str(long_template)]
    text=long_template.read_text();initial_text=template.read_text()
    start=text.index('        import biwn_fast_CPU_bridge as CPU_bridge');stop=text.index('        GPU_source = DSP_source = IRQ_source = None',start)
    source_start=initial_text.index('        import biwn_fast_CPU_bridge as CPU_bridge');source_stop=initial_text.index('        GPU_source = DSP_source = IRQ_source = None',source_start)
    text=text[:start]+initial_text[source_start:source_stop]+text[stop:]
    start=initial_text.index('        division_observer=');stop=initial_text.index("        report['C_processor_backends']=finish_processors()",start)
    at=text.rindex("        report['C_processor_backends']=finish_processors()");text=text[:at]+initial_text[start:stop]+text[at:]
    scope_line=next(line for line in initial_text.splitlines()if "report['C_CPU_backend']['scope']"in line)
    marker="        report['source_C_execution']=args.CPU_mode=='C'";assert text.count(marker)==1;text=text.replace(marker,marker+'\n'+scope_line)
    old=str(ROOT/'verification/CPU-IRQ-selection-DSP-experimental-candidate.json');assert text.count(repr(old))==1;text=text.replace(repr(old),repr(str(cp)))
    line='            import biwn_fast_GPU_bridge, biwn_DSP_program_router, biwn_CPU_IRQ_select_owner';assert text.count(line)==1
    text=text.replace(line,'            import biwn_fast_GPU_bridge, biwn_CPU_IRQ_select_owner\n            import biwn_DSP_external_router as biwn_DSP_program_router')
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(failed['commands'][1]['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'C')
    state=dict(status='running_fresh_initial_entry_combined_merchant_with_external_DSP',pid=os.getpid(),directory=str(out),command=command,candidate=str(cp),native_reference_reused=True,reference=str(reference),
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',probe,cp,Path(candidate['library']),Path(candidate['external_library']),Path(window['directory'])/'protocol.json',Path(initial['directory'])/'protocol.json',template,long_template,ROOT/'scripts/biwn_DSP_external_router.py',reference/'report.json',reference/'frontend-PCM.s16le']},
        scope='Fresh repaired-disc HLE entry with C CPU from initial preparedPC, C GPU/DSP plus source IRQ selection/entry. Includes repaired externalDSPcatalogue and checked division backend. HLE/devices/IRQline+ACK/vector/hostcommit/prefetch/cost/clock/blitter/OP retained. No checkpointrestore, guestRAMpatch or physical-console proof.',
        checkpoint_restores=0,host_guest_RAM_writes=0,new_training=False,default_promoted=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/external-DSP-combined-route-current.json',state)
    mark()
    try:
        with(out/'C.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code
        if code:
            state['status']='terminal_external_DSP_combined_route_rejected';state['child_status']=read(out/'C/status.json') if(out/'C/status.json').exists()else None;mark();return
        report=read(out/'C/report.json');assert len(report['frames'])==len(control['frames'])
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
        differences={k:sum(a[k]!=b[k]for a,b in zip(report['frames'],control['frames']))for k in fields}
        CPU=report['C_CPU_backend'];backends=report['C_processor_backends'];DSP=backends['DSP']
        assert CPU['entry_gate']['original_before_owner_install']==0 and CPU['counts']['Original']==CPU['counts']['Rejected']==CPU['stats']['errors']==0
        assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
        assert DSP['errors']==DSP['uncovered']==DSP['core_counts']['Original']==DSP['core_counts']['Rejected']==0 and DSP['external_program']['owned']>=460
        assert all(backends['IRQ'][k][v]==0 for k in ['core','selection']for v in ['Original','Rejected'])
        PCM_equal=sha(out/'C/frontend-PCM.s16le')==sha(reference/'frontend-PCM.s16le')
        assert report['audio']['nonzero_samples']>0
        final=report['frames'][-1];assert final['player_mode_word']==1 and final['floor_word']==0 and final['navigation']['outdoor_hold']>=120
        state.update(status='terminal_initial_entry_external_DSP_combined_merchant_equal'if not any(differences.values())and PCM_equal else'terminal_initial_entry_external_DSP_combined_merchant_diverged',frames=len(report['frames']),comparisons=differences,PCM_equal=PCM_equal,C_CPU_backend=CPU,C_processor_backends=backends,nonzero_audio_samples=report['audio']['nonzero_samples'],division_provider_counts=report['division_provider_counts'],report_sha256=sha(out/'C/report.json'))
        mark();print(json.dumps({k:state[k]for k in ['status','frames','comparisons','PCM_equal','nonzero_audio_samples']}),flush=True)
    except BaseException as error:state.update(status='terminal_external_DSP_combined_route_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()

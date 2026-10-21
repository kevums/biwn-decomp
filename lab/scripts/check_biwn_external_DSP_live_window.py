"""Fresh-route DSP-only ownership across the actual failure and first nonzero audio."""
import json,os,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    candidate=read(ROOT/'verification/external-DSP-experimental-candidate-current.json');cp=Path(candidate['directory'])/'candidate.json'
    gate=read(ROOT/'verification/external-DSP-native-check-current.json');guards=read(ROOT/'verification/external-DSP-guards-current.json')
    assert gate['status']=='terminal_external_DSP_native_pass'and gate['failed_cases']==0 and gate['cases']==5580
    assert gate['candidate_sha256']==sha(cp)and guards['status']=='terminal_external_DSP_guards_pass'
    failed_path=ROOT/'verification/native-formatter-C-processors/20261018T233557.255349Z/protocol.json';failed=read(failed_path);original=Path(failed['directory'])
    reference=original/'reference';control=read(reference/'report.json')
    out=ROOT/'verification/external-DSP-live-window'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    template=original/'probe.py';assert sha(template)==failed['source_sha256'][str(template)];text=template.read_text();marker="        report['source_C_execution']=args.CPU_mode=='C'";assert text.count(marker)==1
    text=text.replace(marker,"        report['source_C_execution']=args.CPU_mode=='C' or bool(args.own_DSP_window)")
    old="scope='OnlyHLE bootstrap before mainstage4000 uses original68000opcodes in C lane; C GPU/DSP/IRQ selection+entry providers installed; original device/IRQ line+ACK/commit/cost/HLE services retained. No guestRAMpatch or checkpointrestore.'"
    assert old in text;text=text.replace(old,"scope='This probe uses originalCPU/GPU/IRQ; only the requestedDSPwindow is source-owned. HLE/devices/clock retained; no checkpointrestore or guestRAMpatch.'")
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(failed['commands'][0]['command']);command[2]=str(probe);command[command.index('--frames')+1]='15920';command[command.index('--output')+1]=str(out/'C-DSP-window')
    command+=['--own-DSP-window','15845','15920','--DSP-owner-kind','router','--DSP-router-candidate',str(cp),'--require-owned-DSP']
    state=dict(status='running_fresh_external_DSP_live_window',pid=os.getpid(),directory=str(out),command=command,candidate=str(cp),frames=15920,DSP_owned_frames=[15845,15920],native_reference_reused=True,
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',probe,cp,Path(candidate['library']),Path(candidate['external_library']),Path(gate['directory'])/'protocol.json',Path(guards['directory'])/'protocol.json',reference/'report.json']},
        scope='Fresh HLE normal controller route; source DSP only for75frames around the real merchant transition. OriginalCPU/GPU/IRQ and firmware/device/clock providers remain. Reuses the exact immutable native control, not a new full combined C route.',new_training=False,default_promoted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/external-DSP-live-window-current.json',state)
    mark()
    try:
        with(out/'C-DSP-window.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code
        if code:state['status']='terminal_external_DSP_live_window_rejected';mark();return
        report=read(out/'C-DSP-window/report.json');DSP=read(out/'C-DSP-window/DSP-owner-report.json');assert len(report['frames'])==15920
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
        differences={k:sum(a[k]!=b[k]for a,b in zip(report['frames'],control['frames']))for k in fields}
        PCM=(out/'C-DSP-window/frontend-PCM.s16le').read_bytes()
        with(reference/'frontend-PCM.s16le').open('rb')as f:PCM_equal=f.read(len(PCM))==PCM
        assert DSP['errors']==DSP['uncovered']==DSP['core_counts']['Original']==DSP['core_counts']['Rejected']==0
        external=DSP['owned']-DSP['profiles']['music']-DSP['profiles']['media'];assert external==460
        assert report['audio']['nonzero_samples']>0
        state.update(status='terminal_external_DSP_live_window_equal'if not any(differences.values())and PCM_equal else'terminal_external_DSP_live_window_diverged',comparisons=differences,PCM_prefix_byte_equal=PCM_equal,PCM_bytes=len(PCM),nonzero_audio_samples=report['audio']['nonzero_samples'],DSP=DSP,external_instructions=external,report_sha256=sha(out/'C-DSP-window/report.json'))
        mark();print(json.dumps({k:state[k]for k in ['status','comparisons','PCM_prefix_byte_equal','nonzero_audio_samples','external_instructions']}),flush=True)
    except BaseException as error:state.update(status='terminal_external_DSP_live_window_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()

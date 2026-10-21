"""Explicit old->API-only-core state import, checked by one original frame.

The original report is never relabeled or edited. A saved derivative probe
allows only the pinned old/new core pair, records that compatibility exception,
and still requires exact full-machine/RAM round-trip before any execution.
"""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    core=json.loads((ROOT/'verification/GPU-register-state-experimental-candidate.json').read_text())
    check=json.loads((ROOT/'verification/GPU-register-state-current.json').read_text())
    assert check['core_sha256']==core['core_sha256']
    base=ROOT/'runs/world-controls-20261017T084146.540377Z'
    parent=json.loads((base/'protocol.json').read_text())
    command=next(row['command']for row in parent['commands']if row['phase']=='reference')[:]
    checkpoint=base/'reference/report.json'
    original_report=checkpoint.read_bytes();old=json.loads(original_report);assert old['core_sha256']==core['parent_core_sha256']
    out=ROOT/'verification/GPU-register-checkpoint'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    probe=ROOT/'scripts/probe_biwn_frame_CPU_owner.py';source=probe.read_text()
    root_line='ROOT = Path(__file__).resolve().parents[1]';assert source.count(root_line)==1
    derivative='import sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+source.replace(root_line,'ROOT = Path('+repr(str(ROOT))+')')
    guard="assert previous['core_sha256']==sha(core_path.read_bytes())";assert derivative.count(guard)==1
    qualifier="assert previous['core_sha256']=="+repr(core['parent_core_sha256'])+" and sha(core_path.read_bytes())=="+repr(core['core_sha256'])
    derivative=derivative.replace(guard,qualifier)
    marker="restored_checkpoint=dict(report=str(args.restore_original_report),state_sha256=sha(blob),";assert derivative.count(marker)==1
    derivative=derivative.replace(marker,marker+"source_core_sha256=previous['core_sha256'],target_core_sha256=sha(core_path.read_bytes()),explicit_core_compatibility_import=True,")
    target=out/'compatible_checkpoint_probe.py';target.write_text(derivative)
    for flag in ['--capture-frame','--frame-controller-script']:
        while flag in command:
            i=command.index(flag);del command[i:i+2]
    command[command.index('--restore-original-report')+1]=str(checkpoint)
    command[command.index('--frames')+1]='1';command+=['--capture-frame','1']
    commands={}
    for phase in ['old_original','new_original']:
        cmd=command[:];cmd[cmd.index('--output')+1]=str(out/phase)
        if phase=='new_original':
            cmd[1]=str(target);cmd[cmd.index('--core')+1]=core['core_path']
            cmd[cmd.index('--native-CPU-candidate')+1]=str(ROOT/'verification/GPU-register-native-CPU-experimental-candidate.json')
        commands[phase]=cmd
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),commands=commands,source_checkpoint=str(checkpoint),
               old_core_sha256=core['parent_core_sha256'],new_core_sha256=core['core_sha256'],
               parent_probe_sha256=hashlib.sha256(source.encode()).hexdigest(),derivative_probe_sha256=hashlib.sha256(derivative.encode()).hexdigest(),
               scope='Explicit complete-state transfer between pinned old and API-only cores; no source-report relabeling. Saved derivative changes only workspace/import path, the qualified old/new core check and provenance fields. Exact machine/RAM round-trip still mandatory before execution. One actual original-CPU/GPU/DSP frame must match all bytes/traces. New source-GPU bridge and startup performance not verified here.')
    def save():(out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n')
    save()
    try:
        for phase,cmd in commands.items():
            state['status']='running_'+phase
            with(out/(phase+'.log')).open('w')as log:
                child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();print(phase,'PID',child.pid,flush=True);code=child.wait()
            assert code==0,(phase,code)
        before=json.loads((out/'old_original/report.json').read_text());after=json.loads((out/'new_original/report.json').read_text())
        assert before['mode']==after['mode']=='reference' and not before['errors']and not after['errors']
        assert before['owned_CPU_instructions']==after['owned_CPU_instructions']==0
        assert before['original_CPU_instructions']==after['original_CPU_instructions']>0
        assert before['frames']==after['frames'] and after['restored_original_checkpoint']['explicit_core_compatibility_import']
        names=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']
        for name in names:assert (out/'old_original'/name).read_bytes()==(out/'new_original'/name).read_bytes(),name
        assert checkpoint.read_bytes()==original_report
        state.update(status='one_original_frame_cross_core_state_import_matches',checked_files=names,
                     new_original_checkpoint=str(out/'new_original/report.json'),original_CPU_instructions=after['original_CPU_instructions'],
                     original_report_unchanged=True,metadata_GPU_bridge_verified=False,default_promoted=False)
        save();(ROOT/'verification/GPU-register-checkpoint-current.json').write_text(json.dumps(state,indent=2)+'\n');print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise

if __name__=='__main__':main()

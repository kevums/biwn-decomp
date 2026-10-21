"""Whole-frame continuation from explicit newly C-loaded outdoor RAM.

The original serialized machine is restored exactly, then a byte-checked data
overlay supplies the verified C-loaded scene. No actor task is blocked here.
Native and reconstructed CPU/GPU/DSP use the same declared starting overlay.
This is a controlled state transplant, not natural scene-entry/boot proof.
"""
import argparse,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,default=60);ap.add_argument('--scene',type=int,default=0);ap.add_argument('--CPU-candidate',type=Path);ap.add_argument('--native-CPU-candidate',type=Path);ap.add_argument('--input-script',type=Path);ap.add_argument('--scene-setup-proof',type=Path);ap.add_argument('--capture-frame',type=int,action='append');ap.add_argument('--reuse-reference',type=Path);args=ap.parse_args();assert 1<=args.frames<=1200
    out=ROOT/'runs'/('loaded-scene-frames-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    recipe=json.loads((ROOT/'verification/interactive-preview-recipe.json').read_text());candidate=recipe['candidate']
    overrides={k:v.resolve()for k,v in [('--CPU-candidate',args.CPU_candidate),('--native-CPU-candidate',args.native_CPU_candidate)]if v}
    value=lambda flag:overrides.get(flag,Path(candidate[candidate.index(flag)+1]))
    checkpoint=value('--restore-original-report');before=(checkpoint.parent/'final-RAM.bin').read_bytes()
    proof_path=(args.scene_setup_proof or ROOT/'verification/nearby-actor-scene-current.json').resolve()
    source_proof=json.loads(proof_path.read_text());folder=Path(source_proof['directory']);source=folder/f'scene-{args.scene}-loaded-C-RAM.bin';target=bytearray(source.read_bytes());assert len(target)==len(before)==0x200000
    if args.scene_setup_proof:assert sha(target)==source_proof['scene_RAM_sha256']
    else:
        cases=json.loads((folder/'cases.json').read_text());load=next(row['actor']['load']for row in cases if row['actor']['scene']==args.scene);assert sha(target)==load['RAM_sha256']
    code_changes=[]
    # Offline setup used relocated native queue operands. No queue remains
    # pending; restore these four operands to the frame runtime's source code.
    for address in [0x20ba2,0x20c26,0x20d3e,0x20d8c]:
        assert int.from_bytes(target[address:address+4],'big')==0x1f0000
        target[address:address+4]=(0x15ec7c).to_bytes(4,'big');code_changes.append(dict(address=hex(address),from_value='0x1f0000',to_value='0x15ec7c'))
    overlay=json.loads(value('--experimental-code-overlay').read_text())
    for patch in overlay['patches']:
        address=int(patch['address'],16);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement']);assert len(old)==len(new)
        assert target[address:address+len(old)]in [old,new],patch['address']
        target[address:address+len(old)]=new
    cpu=json.loads(value('--CPU-candidate').read_text());atlas=Path(cpu['instruction_RAM_source']).read_bytes();decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);differences=[]
    for key in cpu['selected_case_sources']:
        pc=int(key,16)
        if pc in [0x303c,0x3042,0x304e,0x4088]:continue
        row=next(decoder.disasm(atlas[pc:pc+24],pc,count=1),None);assert row is not None,key
        if target[pc:pc+row.size]!=atlas[pc:pc+row.size]:differences.append(dict(PC=key,expected=atlas[pc:pc+row.size].hex(),actual=target[pc:pc+row.size].hex()))
    save(out/'instruction-byte-differences.json',differences)
    # The bootstrap at180000 was executed before the recorded checkpoint;
    # that address range is now resource data. Do not overwrite loaded assets
    # with an obsolete bootstrap image. Reached-site byte guards remain on.
    boot_reuse=[row for row in differences if 0x180000<=int(row['PC'],16)<0x180188]
    resident_differences=[row for row in differences if row not in boot_reuse]
    assert not resident_differences,'Scene data changed resident source instructions'
    from check_biwn_loaded_actor_runtime import ring,get
    old_tasks=ring(before);new_tasks=ring(target);created=[task for task in new_tasks if task not in old_tasks]
    assert created and all(get(target,task+26)==0 for task in created)
    # Do not rewrite task readiness or saved context state. Record all tasks.
    tasks=[dict(task=hex(task),entry=hex(get(target,task+8)),saved_PC=hex(get(target,task+16)),blocked=get(target,task+26),parameter=get(target,task+30),new=task in created)for task in new_tasks]
    patches=[];position=0
    while position<len(before):
        if before[position]==target[position]:position+=1;continue
        start=position;position+=1;last=position
        while position<len(before)and position-start<65536:
            if before[position]!=target[position]:last=position+1
            elif position-last>=16:break
            position+=1
        end=last;patches.append(dict(address=hex(start),original=before[start:end].hex(),replacement=target[start:end].hex()))
    state_overlay=out/'starting-scene-overlay.json';save(state_overlay,dict(status='explicit_controlled_scene_state_transplant',patches=patches,scope='Original serialized CPU/GPU/DSP/devices checkpoint plus verified C-loaded mainRAM scene and existing experimental code recipe. Readiness/context fields not changed beyond the real source loader output. Four offline queue-base operands restored. This is neither natural entry nor an unmodified-game run.'))
    reconstructed=bytearray(before)
    for patch in patches:
        a=int(patch['address'],16);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement']);assert reconstructed[a:a+len(old)]==old;reconstructed[a:a+len(old)]=new
    assert reconstructed==target
    reused=None
    if args.reuse_reference:
        reused=args.reuse_reference.resolve();saved=json.loads((reused/'report.json').read_text());old_overlay=Path(saved['experimental_code_overlay']['manifest'])
        assert saved['mode']=='reference'and not saved['errors']and len(saved['frames'])==args.frames
        assert saved['core_sha256']==sha(value('--core').read_bytes())
        assert sha(state_overlay.read_bytes())==sha(old_overlay.read_bytes())==saved['experimental_code_overlay']['sha256']
        assert sha((reused/'warm-RAM.bin').read_bytes())==sha(target)
        assert saved['restored_original_checkpoint']['report']==str(checkpoint)
        state_overlay=old_overlay
    (out/'starting-scene-RAM.bin').write_bytes(target);save(out/'tasks.json',tasks)
    windows=[dict(start_frame=1,stop_frame=min(4,args.frames+1),buttons=['C'])]
    if args.frames>=40:windows.append(dict(start_frame=20,stop_frame=40,buttons=['U']))
    if args.input_script:windows=json.loads(args.input_script.read_text())['windows']
    for window in windows:assert 1<=window['start_frame']<window['stop_frame']<=args.frames+1
    schedule=out/'input.json';save(schedule,dict(windows=windows))
    if reused:assert saved['frame_controller_script_sha256']==sha(schedule.read_bytes())
    common=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),'--warm-frames','0','--frames',str(args.frames),'--core',str(value('--core')),'--restore-original-report',str(checkpoint),'--experimental-code-overlay',str(state_overlay),'--frame-controller-script',str(schedule),'--capture-audio','--native-CPU-bridge','--extended-CPU','--CPU-candidate',str(value('--CPU-candidate')),'--native-CPU-candidate',str(value('--native-CPU-candidate'))]
    captures=sorted(set(args.capture_frame or [1,min(10,args.frames),min(30,args.frames),min(50,args.frames),min(70,args.frames),min(90,args.frames),min(110,args.frames),args.frames]));assert len(captures)<=8 and all(1<=frame<=args.frames for frame in captures)
    for frame in captures:common+=['--capture-frame',str(frame)]
    gpu=['--regular-GPU-mode','C','--renderer-bundles','--renderer-overlays','--material-bundles','--control-bundles','--setup-bundles','--native-GPU-bridge','--GPU-frame-only','--native-GPU-candidate',str(value('--native-GPU-candidate')),'--stop-on-GPU-original']
    dsp=['--native-DSP-owner','--DSP-owner-kind','router','--require-owned-DSP','--DSP-router-candidate',str(ROOT/'verification/fast-DSP-router-experimental-candidate.json')]
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=args.frames,source_scene_proof=str(proof_path),source_scene_RAM=str(source),source_scene_RAM_sha256=sha(source.read_bytes()),initial_RAM_sha256=sha(target),base_checkpoint=str(checkpoint),restored_queue_operands=code_changes,loaded_task_contexts=len(tasks),new_task_contexts=len(created),new_tasks_blocked=0,bootstrap_sites_now_resource_data=len(boot_reuse),script_sha256=sha(Path(__file__).read_bytes()),CPU_candidate=str(value('--CPU-candidate')),native_CPU_candidate=str(value('--native-CPU-candidate')),GPU_candidate=str(value('--native-GPU-candidate')),commands=[],scope='Controlled original machine + C-loaded scene RAM transplant. Source whole-frame scheduling/interrupts/controllers/devices run; no actor blocking or per-frame processor reset. Original reference and C compare traces/RAM/video/PCM/final machine. Original IRQ/HLE/device providers and supplied start remain; not natural scene entry, standalone or full-game proof.')
    def publish():save(out/'protocol.json',state);save(ROOT/'verification/loaded-scene-frames-active.json',state)
    def run(phase,command,allow_failure=False):
        state.update(status='running_'+phase);state['commands'].append(dict(phase=phase,command=command))
        with(out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;publish();print(phase,'PID',child.pid,flush=True);code=child.wait()
        state['last_exit_code']=code;publish()
        if code and not(allow_failure and code==1):raise RuntimeError(f'{phase} exited {code}; see {out/(phase+".log")}')
    publish()
    try:
        if reused:
            (out/'reference').symlink_to(reused,target_is_directory=True);state['reused_reference']=str(reused);publish()
        else:run('reference',common+['--mode','reference','--output',str(out/'reference')])
        run('C',common+['--mode','C',*gpu,*dsp,'--output',str(out/'C')])
        run('compare',[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),'--C-run',str(out/'C'),'--reference',str(out/'reference'),'--expected-frames',str(args.frames),'--original-checkpoint-report',str(checkpoint),'--experimental-code-overlay',str(state_overlay),'--output',str(out/'comparison.json')],True)
        comparison=json.loads((out/'comparison.json').read_text());failed=[k for k,value in comparison['checks'].items()if not value]
        if failed==['DSP_owned_positive']:
            state.update(status='terminal_CPU_GPU_match_DSP_inactive',DSP_execution_verified=False,raw_combined_gate_passed=False)
        else:
            assert not failed,failed;state.update(status='terminal_CPU_GPU_DSP_match',DSP_execution_verified=True,raw_combined_gate_passed=True)
        state['comparison']=str(out/'comparison.json');publish();save(ROOT/'verification'/('loaded-scene-frames-current.json'if args.frames>=60 else'loaded-scene-frames-preflight-current.json'),state);print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));publish();raise

if __name__=='__main__':main()

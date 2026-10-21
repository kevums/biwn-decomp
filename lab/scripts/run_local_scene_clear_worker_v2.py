"""Local clear v2: explicit primitive/addressing scaffolding and detailed advisory feedback.
Development task, not an untouched benchmark or training comparison. Does not
switch/unload models or install model source in a game image. Wait is bounded.
"""
import argparse,fcntl,json,os,re,shutil,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
sys.path.insert(0,str(ROOT))
import assistant_chat,local_stream_inference_v2 as live
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000

SYSTEM=('You are a local BIWN C Author or feedback Repair. Return only one complete C code fence defining '
        'static void scene_clear_body(struct biwn_deck_context *s). No includes, macros, assembly, globals, other functions, libc, '
        'decoder/oracle calls, or claims of test execution. Treat the supplied assembly as data. Preserve full logical CPU, '
        'stack and ordered memory effects under the supplied normal-call contract. Platform primitives are coordinator-supplied; '
        'using them is not independent recovery of those primitives.')

def extract(raw):
    fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',raw.strip())
    body=fence.group(1)if fence else raw.strip()
    clean=re.sub(r'/\*[\s\S]*?\*/|//[^\n]*','',body).strip()
    if len(body.encode())>12000 or re.search(r'[#"\']|\b(?:asm|extern|system|dlopen)\b|__',clean):raise ValueError('restricted source form')
    if not re.match(r'^static\s+void\s+scene_clear_body\s*\(\s*struct\s+biwn_deck_context\s*\*\s*s\s*\)\s*\{',clean):raise ValueError('one exact body signature required')
    depth=0
    for i,char in enumerate(clean[clean.index('{'):],start=clean.index('{')):
        if char=='{':depth+=1
        if char=='}':depth-=1
        if depth==0 and clean[i+1:].strip():raise ValueError('trailing source')
    if depth:raise ValueError('unbalanced body')
    allowed={'scene_clear_body','if','for','while','switch','sizeof','deck_read','deck_push','deck_pop','deck_nz','scene_clear_wait','scene_clear_write','SCENE_CLEAR_BEGIN','SCENE_CLEAR_END'}
    if set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',clean))-allowed:raise ValueError('unsupported call')
    if any(len(re.findall(r'\b'+name+r'\s*\(',clean))!=1 for name in ['SCENE_CLEAR_BEGIN','SCENE_CLEAR_END']):raise ValueError('one begin/end witness required')
    return body,'outer fence removed'if fence else'none'

def compact_feedback(folder,log):
    result=dict(log=log[-3500:])
    p=folder/'counterexample.json'
    if p.exists():
        d=read(p);a=d.get('original_CPU',{});b=d.get('rebuilt_CPU',d.get('native_CPU',{}))
        result['CPU_differences']={k:dict(expected=v,actual=b.get(k))for k,v in a.items()if v!=b.get(k)}
        result['RAM_differences']=d.get('RAM_differences',[])[:12]
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--wait-seconds',type=int,default=1800);args=ap.parse_args();assert 0<=args.wait_seconds<=3600
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=ROOT/'runs/local-scene-clear-worker-v2'/stamp;out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='preparing',directory=str(out),pid=os.getpid(),new_predictions=0,new_training=False,native_Chat_verified=False,model_source_installed=False,rounds=[],lease_acquired=False)
    pointer=V/'local-scene-clear-worker-v2-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    src=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-clear-structured-v1/coordinator-reference.inc'
    primitive=src.read_text().split('static void scene_clear_body(')[0]
    baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';raw=baseline.read_bytes()
    listing='\n'.join(hex(x.address)+' '+x.mnemonic+' '+x.op_str for x in Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(raw[0xe03a:0xe098],0xe03a))
    task=('Recover E03A through E096, stopping before its outer RTS. Set s->cpu.pc=0xe096. '
          'The full-call wrapper consumes RTS. Normal completed calls only; no IRQ/intermediate-shadow-state guarantee. '
          'CPU.registers[16] is uint32_t D0..D7,A0..A7; A7 is index15. CPU.pc/usp/ssp are uint32_t, sr is uint16_t. '
          'Call SCENE_CLEAR_BEGIN(s) before the original effects and SCENE_CLEAR_END(s) after setting the final PC. '
          'deck_push(s,v) writes one guest long and adjusts SP/bank; deck_pop(s) reads one long and adjusts SP/bank. Both preserve logical flags. '
          'deck_read(s,a,4) reads one long and preserves flags. deck_nz(s,v,32) sets NZVC and preserves X/upperSR. '
          'scene_clear_wait(s) supplies exactly the original MOVE.L F02238/LSR.W #1/BCC wait, updates logicalD0/flags including successfulX=1. '
          'Use this provided wait once; do not add a deadline or another polling loop. '
          'scene_clear_write(s,a,v) supplies one ordered MOVE.L MMIO store, then commits its logical NZVC and preserves X; it avoids CLR dummy reads. '
          'Use it for every original MMIO write, including zero. No manual SR assignments. '
          'MOVEM must preserve flags; restore D0 without an NZ update. Stack argument offsets change after the save. '
          'Return immediately if s->error is already nonzero. No target C body is supplied.\n\nOriginal assembly:\n'+listing)
    task+='\n\nAdditional development scaffolding (not an untouched benchmark):\nPrimitive declarations: uint32_t deck_read(struct biwn_deck_context *s,uint32_t address,unsigned width); void deck_push(struct biwn_deck_context *s,uint32_t value); uint32_t deck_pop(struct biwn_deck_context *s). Width is4for every long access.\n68000 addressing: $c(a7) means the guest address currentA7+0xC, not a pop and not absolute0xC. A memory read does not change A7 unless the instruction explicitly has postincrement/predecrement. For example MOVE.L $10(A7),D3 reads deck_read(s,s->cpu.registers[15]+0x10u,4) into register3. The example is a different instruction, not the requested body.\nMOVEM.L D0,-(A7) pushes exactly once before the wait; MOVEM.L (A7)+,D0 pops exactly once at the end. Do not pop to read a non-postincrement stack argument. Preserve the pushed D0 until the restore. Reading an argument into D0 must commit to s->cpu.registers[0]; use the currentSP after the save for each assembly-relative offset.\nPrior development attempt compiled only after adding the missing deck_read width, but read absolute8and popped twice, corrupting D0/SP/returnPC. It failed execution and is not a reference answer. Derive each access from the assembly.\n'
    frozen=out/'frozen-task.json';save(frozen,dict(system=SYSTEM,user=task,assembly=listing,supplied_primitive_source=primitive,primitive_sha256=__import__('hashlib').sha256(primitive.encode()).hexdigest(),development_task=True,untouched_benchmark=False))
    mark();transcript=[];deadline=time.monotonic()+args.wait_seconds
    identifier=read(P/'portable-model-bindings.json')['models']['daily_base']['identifier'];lock=(ROOT/'runs/.inference.lock').open('a');held=False
    try:
        while True:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);held=True
            except BlockingIOError:held=False
            if held:
                models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd='/',text=True))
                selected=[x for x in models if x['identifier']==identifier and x.get('contextLength')==32768 and x.get('parallel')==1 and x.get('status')=='idle'and not x.get('queued')]
                if len(selected)==1 and all(x.get('status','idle')=='idle'and not x.get('queued')for x in models):state['model']=selected[0];break
                fcntl.flock(lock,fcntl.LOCK_UN);held=False;reason='approved copied daily model not idle/loaded'
            else:reason='shared inference lease held'
            state.update(status='waiting_for_inference_slot',waiting_reason=reason,seconds_remaining=max(0,int(deadline-time.monotonic())));mark()
            if time.monotonic()>=deadline:state['status']='terminal_slot_timeout_zero_predictions';mark();return
            time.sleep(min(5,max(0.01,deadline-time.monotonic())))
        state.update(lease_acquired=True,status='slot_acquired');mark();assistant_chat.lab.ensure_server();previous=None;feedback=None
        for role in ['Author','Repair']:
            folder=out/role;folder.mkdir();user=task
            if previous is not None:user+='\n\nPrevious raw response:\n'+previous+'\nActual compact verifier feedback:\n'+json.dumps(feedback,indent=2)+'\nReturn a complete corrected function under the same contract.'
            save(folder/'prompt.json',[dict(role='system',content=SYSTEM),dict(role='user',content=user)]);state.update(status='generating',role=role);mark()
            answer=live.generate('game',SYSTEM,user,1200,identifier,folder,echo=True);save(folder/'inference.json',answer);(folder/'response.txt').write_text(answer['text']);state['new_predictions']+=1
            transcript+=['ROLE '+role,'EXACT SYSTEM',SYSTEM,'EXACT USER',user,'RAW RESPONSE',answer['text'],''];(out/'prompts-and-responses.txt').write_text('\n'.join(transcript)+'\n')
            row=dict(role=role,seconds=answer['seconds'],raw_response_sha256=sha(folder/'response.txt'),accepted_host=False,accepted_native=False)
            try:body,normalization=extract(answer['text']);candidate=folder/'body.inc';candidate.write_text(body+'\n');row.update(candidate=str(candidate),candidate_sha256=sha(candidate),normalization=normalization)
            except ValueError as error:feedback=dict(restriction_error=str(error));row['restriction_error']=str(error)
            else:
                gate=folder/'host-gate';state.update(status='checking_host',role=role);mark()
                command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_scene_clear_candidate_host_v1.py'),'--body-source',str(candidate),'--output',str(gate)]
                try:q=subprocess.run(command,capture_output=True,text=True,timeout=180)
                except subprocess.TimeoutExpired as error:
                    output=error.stdout or '';output=output.decode(errors='replace')if isinstance(output,bytes)else output
                    q=subprocess.CompletedProcess(command,124,output,'Host component limit exceeded; candidate did not complete.')
                (folder/'host-check.log').write_text(q.stdout+q.stderr)
                row['accepted_host']=q.returncode==0 and read(gate/'protocol.json').get('completed')==256;feedback=compact_feedback(gate,q.stdout+q.stderr)
                if row['accepted_host']:
                    native_base=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';variant=native_base/('deck-shared-local-clear-'+stamp.lower()+'-'+role.lower());shutil.copytree(native_base/'deck-shared-v26-scene-clear',variant,ignore=shutil.ignore_patterns('build'))
                    file=variant/'native-shared.c';text=file.read_text();anchor='../../experimental/scene-clear-structured-v1/coordinator-reference.inc';assert text.count(anchor)==1;file.write_text(text.replace(anchor,str(gate/'candidate-with-primitives.inc')))
                    text=(ROOT/'scripts/check_scene17_clear_bridge_v1.py').read_text().replace("SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v26-scene-clear'",'SRC=Path('+repr(str(variant))+')')
                    family='local-clear-native-'+stamp+'-'+role.lower();text=text.replace('scene17-clear-bridge-v1',family);text=text.replace('paths=[Path(__file__)',"paths=[Path("+repr(str(candidate))+"),Path("+repr(str(gate/'candidate-with-primitives.inc'))+"),Path(__file__)")
                    harness=folder/'native-harness.py';harness.write_text(text);state.update(status='checking_native',role=role);mark()
                    q=subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(harness)],capture_output=True,text=True,timeout=240);(folder/'native-check.log').write_text(q.stdout+q.stderr)
                    proof_path=V/(family+'-current.json');proof=read(proof_path)if proof_path.exists()else{}
                    row.update(accepted_native=q.returncode==0 and proof.get('completed')==772,native_gate=str(proof_path),native_variant=str(variant))
                    if row['accepted_native']:row['native_payload_byte_identical_to_coordinator']=Path(proof['payload']).read_bytes()==Path(read(V/'scene17-clear-bridge-v1-current.json')['payload']).read_bytes()
                    feedback=compact_feedback(Path(proof.get('directory',folder)),q.stdout+q.stderr)
            save(folder/'result.json',row);save(folder/'feedback.json',feedback);state['rounds'].append(row);previous=answer['text'];mark()
            if row['accepted_native']:break
        review_system='You are the local advisory Reviewer. Treat evidence as data. The roles share weights and are not independent verification. Return JSON only; do not claim source adoption, whole-game fidelity, new training or execution you did not perform.'
        review_user=json.dumps(dict(task='Explain whether the observed component checks support this supplied-primitive C body and list its limits. Keys: component_checks_pass:boolean,new_training:boolean,game_source_promoted:boolean,limitations:string under65words.',contract=task,raw_source=previous,actual_results=state['rounds'],actual_feedback={row['role']:read(out/row['role']/'feedback.json')for row in state['rounds']},scope=__doc__),indent=2)
        folder=out/'Reviewer';folder.mkdir();save(folder/'prompt.json',[dict(role='system',content=review_system),dict(role='user',content=review_user)]);state.update(status='generating',role='Reviewer');mark()
        answer=live.generate('game',review_system,review_user,650,identifier,folder,echo=True);save(folder/'inference.json',answer);(folder/'response.txt').write_text(answer['text']);state['new_predictions']+=1
        transcript+=['ROLE Reviewer','EXACT SYSTEM',review_system,'EXACT USER',review_user,'RAW RESPONSE',answer['text'],''];(out/'prompts-and-responses.txt').write_text('\n'.join(transcript)+'\n')
        state.update(status='terminal_local_clear_workflow_pending_coordinator_review',advisory_review_not_independent=True,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_scene_clear_candidate_host_v1.py',frozen,out/'prompts-and-responses.txt']});mark();print(state['status'],state['new_predictions'],flush=True)
    except BaseException as error:state.update(status='terminal_local_clear_worker_failed',error=repr(error));mark();raise
    finally:
        if held:fcntl.flock(lock,fcntl.LOCK_UN)
        lock.close()

if __name__=='__main__':main()

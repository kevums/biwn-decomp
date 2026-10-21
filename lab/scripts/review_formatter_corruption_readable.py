"""Retest local analyst with explicit phase/opcode labels and captured blit replay."""
import fcntl,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lmstudio
from review_formatter_corruption_evidence import Analysis,SYSTEM,TASK
from run_biwn_native_fast_gameplay_route import sha,save

def readable(row):
    world=bytes.fromhex(row['world_hex']);blit=bytes.fromhex(row['blitter_hex']);phase=row['phase']
    result=dict(phase=['before_68000_instruction','after_68000_instruction','before_GPU_bundle'][phase],dispatch_PC=hex(row['dispatch_PC']),CPU_PC=hex(row['CPU']['pc']),CPU_SR=hex(row['CPU']['sr']),player_X=int.from_bytes(world[:4],'big'),player_Z=int.from_bytes(world[6:10],'big'),blitter={name:hex(int.from_bytes(blit[at:at+4],'big'))for name,at in dict(A1_base=0,A2_base=0x24,A2_flags=0x28,A2_pixel=0x30,command=0x38,count=0x3c).items()})
    if phase==2:
        result['GPU_opcode']=hex(row['cycles']);result['GPU_bank0_selected_registers']={str(i):hex(row['GPU_registers'][i])for i in [0,3,8,22]}
    else:result['instruction_cycles']=row['cycles']
    return result

def main():
    names=dict(cpu='native-fast-core-first-corruption',gpu='native-fast-core-GPU-corruption',handoff='native-fast-core-blitter-handoff',replay='native-fast-core-corrupt-blit-replay')
    paths={k:ROOT/'verification'/(v+'-current.json')for k,v in names.items()};proofs={k:json.loads(p.read_text())for k,p in paths.items()}
    for proof in proofs.values():
        assert proof['status'].startswith('terminal_')
        for p,h in {**proof['source_sha256'],**proof.get('output_sha256',{})}.items():assert sha(p)==h,p
    cpu=json.loads((Path(proofs['cpu']['directory'])/'first-corruption.json').read_text());gpu=json.loads((Path(proofs['gpu']['directory'])/'first-corruption.json').read_text());writers=[json.loads(line)for line in(Path(proofs['handoff']['directory'])/'A2-base-writers.jsonl').read_text().splitlines()]
    packet=dict(E0_schema='phase2 raw trace field named cycles contains the16bit GPU OPCODE,not a duration. This projection correctly renames it GPU_opcode. Phase1 cycles are68000instructioncycles.',E1_CPU=[readable(v)for v in cpu['history'][-3:]],E2_GPU=[readable(v)for v in gpu['history'][-5:]],E3_last_A2_writers=[{k:(hex(v)if k in ['PC','previous_PC','before_base','after_base','CPU_PC','CPU_SR','task']else v)for k,v in row.items()}for row in writers[-3:]],E4_GPU_delay_slot=dict(branch_PC='0xf03aae',branch='jump(r22)',delay_PC='0xf03ab0',delay_instruction='store r0,(r3)',stored_value='0x41802c01',address='0xf02238',next_PC='0xf03790'),E5_isolated_replay=dict(results=proofs['replay']['results'],whole_RAM_comparison_bytes=2097152,CPU_instructions=0,GPU_instructions=0,fixture_uses_captured_RAM_GPU_and_blitter=True,live_game_mutation=False,not_a_deployed_fix=True),E6_limits=dict(native_Chat=False,same_weights=True,hardware_verified=False,ultimate_cause_unresolved=True,default_promoted=False))
    out=ROOT/'runs'/('formatter-readable-Analyst-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());save(out/'evidence.json',packet)
    user=json.dumps(dict(task=TASK,evidence=packet));save(out/'request.json',dict(system=SYSTEM,user=user,tools=[],native_Chat=False))
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Diagnostic Analyst',source_sha256={str(p):sha(p)for p in [Path(__file__),Path(__file__).with_name('review_formatter_corruption_evidence.py'),*paths.values(),out/'evidence.json',out/'request.json']},same_weights=True,independent_review=False,native_Chat_verified=False,new_training=False,model_authored_game_C=False,prior_input_schema_fault_corrected='Rawphase2cycles explicitly projected as GPU_opcode; no latency inference from opcode.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-formatter-readable-Analyst-current.json',state)
    mark();print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);identifier=assistant_chat.ensure_model('game');model=lmstudio.llm(identifier);chat=lmstudio.Chat(SYSTEM);chat.add_user_message(user);tokens=model.count_tokens(model.apply_prompt_template(chat));assert tokens+1100+128<=model.get_context_length();state.update(status='generating',identifier=identifier,input_tokens=tokens);mark();start=time.monotonic();response=model.respond(chat,response_format=Analysis,config={'temperature':0,'maxTokens':1100,'contextOverflowPolicy':'stopAtLimit'});elapsed=time.monotonic()-start
        parsed=Analysis.model_validate_json(response.content).model_dump();save(out/'response.json',dict(text=response.content,stats=response.stats.to_dict(),seconds=elapsed));save(out/'analysis.json',parsed)
        state.update(status='terminal_local_readable_corruption_analysis_pending_coordinator',analysis=parsed,seconds=elapsed,output_words=len(' '.join([*parsed['observations'],*parsed['unproven'],parsed['next_experiment']]).split()),actual_tools=0,coordinator_review_pending=True);mark();print(json.dumps(parsed,indent=2),flush=True);print('seconds',elapsed,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:(out/'prompts-and-responses.txt').write_text('LOCAL DIAGNOSTIC ANALYST; READABLE INPUT REVISION; ADVISORY; SAMEWEIGHTS\nSYSTEM\n'+SYSTEM+'\nUSER\n'+user+'\nRESPONSE\n'+json.dumps(state.get('analysis'),indent=2))

if __name__=='__main__':main()

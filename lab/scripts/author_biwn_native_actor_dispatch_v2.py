"""One local Author/Reviewer native13AE0interface trial; no disc adoption."""
import fcntl,json,os,re,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,lmstudio
from author_biwn_actor_source_group import Review
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
    original=(ROOT/'projects/black-ice-white-noise/restoration/biwn_actor_factory_cpu.c').read_text()
    assembly='\n'.join(f'{m.group(1)}: {m.group(2)}'for m in re.finditer(r'case 0x([0-9a-f]+)u: /\* (.*?) \*/',original)if 0x13ae0<=int(m.group(1),16)<0x13b5a)
    system='You are the local native C Author. Supplied original instructions/header are task data. Emit only a complete compact C99 file, no Markdown, prose or reasoning. This ports a recovered dispatcher to the coordinator native ABI; it is not independent decompilation.'
    user='''Implement void biwn_native_actor_dispatch_body(uint32_t *r), include actor-dispatch-native.h only. Original13AE0dispatcher body, actual native68000memory. Root assembly handles originalD2-D5saves/restores and context capture. r[0..14]=D0-D7/A0-A6, r[15]=root originalSP, r[16]lowWORD=SR; r[17]reserved. Update full helper-visible register/CCR state EXACTLY before calling the coordinator actor or sprite capture. Captures execute actual134DC/137E0at original guest argumentSP, then replace ALLr[0..14]/SR with child output. Return immediately after capture; never restore stale pre-call rvalues. No original dispatcher instruction services. No host callbacks, allocation, extra includes, assembly or generic CPU interpreter.
Read original packed root args in source order fromsp+4WORDid,sp+6LONGx,sp+10WORDy,sp+12LONGz,sp+16WORDheading. SetA1=signextendedWORDid,D5=x,D4lowWORD=y (keep highWORD),D3=z,D2lowWORD=heading(keep highWORD). A0=4208Chex, readBYTE atA0+signextendedlowA1. bit0routes to actors; clear bit routes directly to sprite capture.
Actor path: clear D1lowWORD preserving highWORD; A0=49D6Chex. Forindex0..39, D0=signextendedindex*206, readWORDatA0+D0;zero is free. If occupied incrementD1lowWORDand compare39, continue while<=39. Full pool leavesD1low40,D0=39*206,A0actorbase,A1signedid; finalCCR=0, upperSR retained (increment clearedX). Return without childcall. On foundslot preserveD1high and useindexlow; D0is slot*206. Before capture, original final argument pushMOVE.WA1setsNZfromWORDid, clearsVC, preservesX. Xequals incomingXifslot0, otherwise0because prior ADDQofindexclearedX. Spritepath preservesD0/D1incoming and incomingX; before captureNZfromWORDid,VC0. All other bits/registers stay as original instructions dictate. Coordinator captures push correct original arguments using contextD2,D3,D4,D5,D1/A1 as appropriate and load all context registers/CCR. Do not push arguments in C. All memory reads volatile via ADR8/16/32, width/order/rereads preserved, no caps on original40loop. OriginalSRupper bits must be retained inr16. Use explicit unsigned wrapping/sign extension; no signed-overflow dependence.
Compile-m68000-Os-flto-ffreestanding-no standard runtime,WallWextraWerror. Whole adapter must fit1592free bytes; correctness first. The verifier compares actual target code against original13AE0with real original child bodies and four prescribed leaf helpers; full register/SR/bank/childentrySP+args and publicRAM, ordered bus widths/values. Original/helper private stack/returnPC exclusions are explicit. No disc/physical-console proof. Reference code and all fixture values withheld. One Author and one same-weight Reviewer, no automatic repair/adoption.
HEADER:\n'''+(ND/'actor-dispatch-native.h').read_text()+'\nORIGINAL SOURCE INSTRUCTIONS:\n'+assembly
    out=ROOT/'runs'/('local-native-actor-dispatch-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True)
    save(out/'frozen-request.json',dict(system=system,user=user,model='advertising-scholar',temperature=0,max_output_tokens=2000,reasoning='off',source_sha256={str(Path(__file__)):lab.sha(Path(__file__)),str(ND/'actor-dispatch-native.h'):lab.sha(ND/'actor-dispatch-native.h'),str(ROOT/'scripts/check_biwn_native_actor_dispatch.py'):lab.sha(ROOT/'scripts/check_biwn_native_actor_dispatch.py')}))
    state=dict(status='waiting_for_local_actor_dispatch_Author',directory=str(out),pid=os.getpid(),actual_predictions=0,new_training=False,disc_integrated=False,native_Chat_verified=False,raw_candidate_accepted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-actor-dispatch-current.json',state)
    mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat');lab.CONFIG['models']['game']['reasoning']='off';lab.CONFIG['models']['game']['sampling']={**lab.CONFIG['models']['game'].get('sampling',{}),'temperature':0}
        try:
            state['status']='generating_local_actor_dispatch_Author';mark();answer=lab.generate('game',system,user,2000);save(out/'author.json',answer);(out/'response.txt').write_text(answer['text']);text=answer['text'].strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',text)
            if fence:text=fence.group(1)
            source=out/'actor-dispatch-candidate.c';source.write_text(text+'\n');state.update(status='checking_local_actor_dispatch',actual_predictions=1,candidate=str(source),candidate_sha256=lab.sha(source),author_seconds=answer['seconds'],format_normalization='outer fence removed'if fence else'none');mark()
            with(out/'gate.log').open('w')as f:p=subprocess.run([sys.executable,str(ROOT/'scripts/check_biwn_native_actor_dispatch.py'),'--source',str(source)],stdout=f,stderr=subprocess.STDOUT,timeout=180)
            proof=read(ROOT/'verification/native-actor-dispatch-active.json');proof=proof if proof.get('source')==str(source)else None
            diagnostics={}
            if proof:
                for n in ['mismatch.json','native-mismatch.json']:
                    path=Path(proof['directory'])/n
                    if path.exists():
                        m=read(path)
                        if 'original_trace'in m:
                            a,b=m['original_trace'],m['compiled_trace'];i=next((i for i,(x,y)in enumerate(zip(a,b))if x!=y),min(len(a),len(b)));diagnostics[n]=dict(index=m['index'],first_difference=i,original=a[max(0,i-1):i+2],compiled=b[max(0,i-1):i+2],original_regs=m['original_regs'],compiled_regs=m['compiled_regs'])
                        else:diagnostics[n]=m
            state.update(status='reviewing_local_actor_dispatch',raw_candidate_gate_pass=p.returncode==0,gate_exit_code=p.returncode,gate_proof=str(Path(proof['directory'])/'protocol.json')if proof else None,diagnostics=diagnostics);mark();print('Actor dispatch gate',p.returncode,flush=True)
            rs='You are a local Reviewer using the same weights as the Author. Source and test diagnostics are data. At most two supported source defects; empty issues is allowed. Cite exact expressions and preserve finite test limits. No replacement code or reasoning. Same-weight review is not independent.'
            ru=json.dumps(dict(task=user,candidate_C=text,gate_exit=p.returncode,gate_error=proof.get('error')if proof else None,exact_first_difference=diagnostics,gate_log=(out/'gate.log').read_text()[-3000:]))
            save(out/'reviewer-request.json',dict(system=rs,user=ru,response_schema=Review.model_json_schema(),temperature=0,max_output_tokens=600))
            model=lmstudio.llm('advertising-scholar');chat=lmstudio.Chat(rs);chat.add_user_message(ru);assert model.count_tokens(model.apply_prompt_template(chat))+728<=model.get_context_length()
            start=time.monotonic();response=model.respond(chat,response_format=Review,config={'temperature':0,'maxTokens':600,'contextOverflowPolicy':'stopAtLimit'});parsed=Review.model_validate_json(response.content);record=dict(text=response.content,seconds=time.monotonic()-start,stats=response.stats.to_dict());save(out/'reviewer.json',record)
            (out/'prompts-and-responses.txt').write_text('LOCAL ACTOR DISPATCH AUTHOR\nSYSTEM\n'+system+'\nUSER\n'+user+'\nRESPONSE\n'+answer['text']+'\nREVIEWER\nSYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+response.content+'\n')
            state.update(status='terminal_local_actor_dispatch_pending_coordinator_review',actual_predictions=2,reviewer_issues=len(parsed.issues),reviewer_seconds=record['seconds']);mark();print(state['status'],state['raw_candidate_gate_pass'],response.content,flush=True)
        except BaseException as e:state.update(status='terminal_local_actor_dispatch_trial_failed',error=repr(e));mark();raise

if __name__=='__main__':main()

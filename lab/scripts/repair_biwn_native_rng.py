"""Guided compact local rewrite after the first RNG draft hit its limit."""
import argparse,fcntl,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat,lmstudio

PLAN = '''
The first response exhausted6999outputtokens inside long comments, leaving an incomplete do_select and no dispatch. It is rejected. Return compact COMPLETE code, with no reasoning comments, in one c fence. Aim under3000tokens. Do not repeat assembly or re-trace instructions in comments. Coordinator now supplies this full implementation plan; this is guided authoring, not autonomous derivation.
Use nz32(v)=(v?0:4)|(v&0x80000000?8:0), upper=frame->sr&0xffe0. Helpers may call the accepted result functions on initialized local math_result storage; only numeric d0/d1 matter there. Frame registers D2-D7/A2-A6 and return/args must remain unchanged.
CURRENT/INDEXED: read selector (current from113080; indexed from arg), sign-extend word and form table address113082+4*sx(selector). Read seed. Read Q, call remainder(seed,Q), base=returnedD0*48271u. Read Q AGAIN, call division(seed,Q), read R, call multiply(quotient,R). product=mul.d0; finalD1=mul.d1 (NOT the product). A0=base, A1=seed, because original multiply copies its incoming D2/D3 to A0/A1. state=base-product with wrapping. Initial X=(base<product). Write state. If state is zero or negative, read that table slot again, add7fffffff, write it, set X to unsigned carry of that actual addition. Then read the returned table value. CURRENT must first reread selector and use that selector for the final read; its last ASL also sets X to signbit of the reread selector. INDEXED keeps X from subtraction/normalization. Set D0=final read, SR=upper|X*16|nz32(D0).
FILL: loop i=1..255. Read table[i-1], Q at462f0, remainder; temp2=rem*3275u, base=rem*22925u. Read Q AGAIN, division; read R at462f4; multiply. Preserve final math D1=mul.d1. A0=temp2,A1=base (the original incoming D2/D3 at multiply). Compute state=base-mul.d0, store table[i], and if nonpositive reread slot/add7fffffff/write. Final D0=1020, SR=upper with all five CCR bits zero (ADDQ255to256 has no carry; final CMP256-255=1). Preserve final D1/A0/A1 from last iteration.
SEED: map seed7fffffff to zero, write table[0], run FILL. INIT: run SELECT with explicit selector0 (do not alter frame->arg), then SEED with explicit123456789. Final results come from FILL; preserve the SELECT temporary store side effect.
SELECT: read old word at113080. If old<=255, leave D0/D1 unchanged and preserve incoming X. Otherwise let s=sx16(old), t=((s<<8)-s)<<7 using uint32 wrap, h=(s-t)>>16; let k be low16(old+h) arithmetic-shift-right7, then subtract arithmetic-shift-right15(old), wrapping16. D0=low16((k<<8)-k). D1=(t&ffff0000)|k. Temporary normalized selector is low16(old-D0); set X=(old<(uint16_t)D0). Write temporary word. Always write raw new selector. Final original restore MOVE.L D3 sets NZVC, so SR=upper|X*16|nz32(original saved D3). A0/A1 unchanged. Implement arithmetic shifts through unsigned bit formulas, avoiding implementation-dependent signed shifts.
GET: read selector, A0=113082, D0=read32(table+4*sx(selector)), preserve D1/A1. X=selector sign bit. SR=upper|X*16|nz32(D0).
SET: A1=value, A0=value-1 wrapping. First CMPA against7ffffffd: preserve incoming X; calculate normal32-bit subtraction NZVC. If A0>7ffffffd unsigned, return with those A0/A1/flags and unchanged D0/D1. Otherwise read selector, D0=4*sx(selector), A0=113082, write value to slot. Final X=selector sign bit and NZVC=nz32(value). D1 unchanged.
Use volatile reads/writes in the stated order, including RMW rereads and the final table read. Do not replace Q/R with fixed constants. Nonzero-Q component scope remains; no zero-exception or hardware claim. Export only the required dispatch (static helpers allowed).
'''

REVIEW = '''
The guided rewrite is rejected: compiler fatal error includes nonexistent "biwn_native_rng.h". The supplied filename is "rng-native.h"; include exactly that. Coordinator static review also found these concrete contract violations; these are static findings, NOT executed CPU-test results:
1. do_init overwrites frame->arg twice. This modifies the original caller's argument memory and is prohibited. Change do_select to take an explicit selector, do_seed to take an explicit seed; dispatch passes the supplied argument and init passes0/123456789. Never write frame->arg or return_pc.
2. do_get omits A0. Set frame->r[8]=0x113082; preserve r[1],r[9] and all other non-output registers.
3. do_set corrupts r[10] (A2) and swaps output registers. NEVER write r[10]. At entry A1=r[9]=value and A0=r[8]=value-1. Invalid values leave D0/D1 unchanged and flags are32bit CMPA(value-1,0x7ffffffd), preserving X: result=u-v; N/Z from result; C=u<v; V=((u^v)&(u^result)&0x80000000)!=0. Valid path returns D0=sx16(selector)<<2, A0=0x113082,A1=value, D1 preserved. Write value to the selected slot; NZ from value, X=selector sign. See original assembly.
4. do_current fails to replace X after the final selector reread/ASL. After s=*sel, X=(s>>15)&1 regardless of prior subtraction/normalization. Indexed keeps the subtraction/normalization X.
5. do_indexed declares unused sel pointer, which will fail -Wall -Wextra -Werror. Remove it. Initialize every local math_result mr={0}; the external division helper reads original_d2 even when only numeric results are subsequently used, so uninitialized storage is not permitted.
6. For raw negative selectors, compute the wrapped byte address in uint32_t before casting to a volatile uint32_t pointer. Do not index tbl by a uint32_t 0xffffffff etc, which expresses out-of-array pointer arithmetic in C. A static read_slot(uint16_t s) can return *(volatile uint32_t*)(uintptr_t)(0x113082u+(sx16(s)<<2)); matching write_slot is allowed. Keep each volatile read/write and all rereads in original order. Ordinary fill indices1..255 are fine.
Other supplied plan details still apply. Return one complete compact C file, no explanations or reasoning comments. Preserve untouched fields and existing functions' correct behavior. Same-model review is not independent verification. Original/native execution gates have not accepted any candidate.
'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--review',action='store_true');args=parser.parse_args()
    parent_path=ROOT/('verification/local-native-rng-rewrite-current.json'if args.review else'verification/local-native-rng-current.json');parent=json.loads(parent_path.read_text())
    if args.review:assert parent['status']=='terminal_compile_rejected'
    else:assert parent['status']=='terminal_failed' and parent['result']['stats']['stopReason']=='maxPredictedTokensReached'
    out=ROOT/'runs'/(('local-native-rng-review-'if args.review else'local-native-rng-guided-rewrite-')+lab.stamp());out.mkdir()
    system=parent['system']+'\nReturn compact compilable code only. No explanatory or reasoning comments.'
    if args.review:
        system=lab.COMMON+'\n'+lab.ROLES['game']['reviewer']+'\nYou are the local Reviewer, using the same weights as the Restorer. Return complete corrected C99 in one c fence, no commentary. You have not executed tools or verified success.'
        prompt=parent['prompt']+'\nREJECTED RESTORER CANDIDATE\n'+Path(parent['candidate']).read_text()+'\nCOORDINATOR STATIC REVIEW\n'+REVIEW
    else:prompt=parent['prompt']+'\nCOORDINATOR REWRITE DIAGNOSIS AND PLAN\n'+PLAN
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),system=system,prompt=prompt,
               parent=str(Path(parent['directory'])/'protocol.json'),role='Local Reviewer guided correction'if args.review else'Local Restorer guided rewrite',
               source_accepted=False,coordinator_edited_model_source=False,coordinator_supplied_full_algorithm_plan=True,
               new_training=False,native_Chat=False)
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/('verification/local-native-rng-review-current.json'if args.review else'verification/local-native-rng-rewrite-current.json')).write_text(text)
    save();(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nLOCAL RESTORER\n');print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('advertising');model=lmstudio.llm('advertising-scholar');chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            rendered=model.apply_prompt_template(chat);tokens=model.count_tokens(rendered);assert tokens+4500+128<=model.get_context_length();(out/'formatted-prompt.txt').write_text(rendered);state.update(status='generating',input_tokens=tokens);save();started=time.monotonic()
            def fragment(part):
                with(out/'partial-answer.txt').open('a')as stream:stream.write(part.content)
            result=model.respond(chat,config={'temperature':0.1,'maxTokens':4500},on_prediction_fragment=fragment)
        state['result']=dict(text=result.content,seconds=round(time.monotonic()-started,3),stats=result.stats.to_dict());(out/'raw-response.txt').write_text(result.content)
        with(out/'prompts-and-responses.txt').open('a')as stream:stream.write(result.content+'\n')
        assert result.stats.to_dict()['stopReason']=='eosFound','Generation did not finish'
        blocks=re.findall(r'```(?:c|C)?\s*\n(.*?)```',result.content,re.S);assert len(blocks)==1
        candidate=out/'rng-native.c';candidate.write_text(blocks[0].rstrip()+'\n')
        native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
        command=[str(ROOT/'tools/m68k-elf/bin/m68k-elf-gcc'),'-m68000','-msoft-float','-std=c99','-O2','-ffreestanding','-Wall','-Wextra','-Werror','-I',str(native),'-c',str(candidate),'-o',str(out/'candidate.o')]
        process=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(process.stdout+process.stderr)
        state.update(status='terminal_compiled_pending_native_semantics'if process.returncode==0 else'terminal_compile_rejected',candidate=str(candidate),candidate_sha256=lab.sha(candidate),compile_exit_code=process.returncode,compile_command=command);save();print(state['status'],state['result']['seconds'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()

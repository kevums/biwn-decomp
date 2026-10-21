"""Local Restorer C proposal from original assembly and recovered logical C.

Coordinator supplies the ABI frame/shims and test harness. Streaming tokens
are saved as they arrive. Compilation is not semantic acceptance.
"""
import fcntl,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,binary_tools,assistant_chat,lmstudio


def main():
    out=ROOT/'runs'/('local-native-rng-'+lab.stamp());out.mkdir()
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    decoded,_=binary_tools.m68k_instructions(image[0x1a6e0:0x1a91e],0x1a6e0)
    listing='\n'.join(f'{i["address"]:06x} {i["bytes"]:16s} {i["assembly"]}'for i in decoded)
    (out/'original-disassembly.txt').write_text(listing+'\n')
    system=lab.COMMON+'\n'+lab.ROLES['game']['restorer']+'\nYou are the local Restorer authoring one complete C99 native RNG module. Output one c code fence only. You have not compiled, executed, or verified this code.'
    prompt='''Implement all eight original RNG routines in one high-level C99 dispatch function with the EXACT rng-native.h ABI below. Coordinator supplies that frame and the assembly shims. Preserve all return D0,D1,A0,A1 and SR low five bits, and leave other saved registers unchanged. Use the original assembly as authority for flags/register side effects; the supplied portable C preserves logical effects but excludes those register/flag outputs. Original restore MOVEs and MOVEMs differ in flag effects. Native frame r[0..7]=D0..D7,r[8..14]=A0..A6. Its sr is incoming full SR; replace only the CCR bits as needed. Original stack argument is frame->arg.word_value or long_value. Never touch frame->return_pc.
Use direct volatile uint16_t/uint32_t access at the original addresses, with raw sign-extended word selectors, wrapped uint32_t arithmetic and exact order/rereads. Preserve selector alias effects and the temporary normalization store before selecting a new raw index. The fill loops 1..255. Use logical expressions and loops, not a switch for every original PC, a decoder or an interpreter. The single dispatch switch selects only the eight original entry addresses. You may call the already accepted C math_result helpers declared in the header (initialize original_d2/d3 if needed). Those helpers compute exact multiply/quotient/remainder/D1; their native zero-divisor processor-exception adaptation is NOT part of this C interface. Q divisors are nonzero in this phase; do not invent a zero-divisor or hardware proof. No libc, original game calls, mutable globals, int64, signed-overflow or signed-left-shift UB. Static local helper functions are allowed. Compile -m68000 -msoft-float -std=c99 -O2 -ffreestanding -Wall -Wextra -Werror. Do not emit assembly or another file.
HEADER\n'''+(native/'rng-native.h').read_text()+'\nRECOVERED LOGICAL C (coordinator-authored, already compared with original external RAM/value/call order; adapt it rather than returning its callback API)\n'+(native.parent/'biwn_rng.c').read_text()+'\nORIGINAL COMPLETE EIGHT-ROUTINE ASSEMBLY\n'+listing+'\nACCEPTED MATH C FOR INTERFACE/RETURN DETAILS\n'+(native/'math-results-optimized.c').read_text()
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Local Restorer',model='advertising-scholar',system=system,prompt=prompt,assembly_instructions=len(decoded),native_Chat=False,new_training=False,source_accepted=False,coordinator_supplied_recovered_algorithms_and_ABI=True,coordinator_edited_model_source=False)
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/'verification/local-native-rng-current.json').write_text(text)
    save();(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nRESTORER RESPONSE\n');print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('advertising');model=lmstudio.llm('advertising-scholar');chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            rendered=model.apply_prompt_template(chat);tokens=model.count_tokens(rendered);assert tokens+7000+128<=model.get_context_length();(out/'formatted-prompt.txt').write_text(rendered)
            state.update(status='generating',input_tokens=tokens);save();started=time.monotonic()
            def fragment(part):
                with(out/'partial-answer.txt').open('a')as stream:stream.write(part.content)
            result=model.respond(chat,config={'temperature':0.1,'maxTokens':7000},on_prediction_fragment=fragment)
        state['result']=dict(text=result.content,seconds=round(time.monotonic()-started,3),stats=result.stats.to_dict());(out/'raw-response.txt').write_text(result.content)
        with(out/'prompts-and-responses.txt').open('a')as stream:stream.write(result.content+'\n')
        assert result.stats.to_dict()['stopReason']=='eosFound','Generation did not finish'
        blocks=re.findall(r'```(?:c|C)?\s*\n(.*?)```',result.content,re.S);assert len(blocks)==1,'Expected one fenced C file'
        candidate=out/'rng-native.c';candidate.write_text(blocks[0].rstrip()+'\n');state.update(candidate=str(candidate),candidate_sha256=lab.sha(candidate))
        command=[str(ROOT/'tools/m68k-elf/bin/m68k-elf-gcc'),'-m68000','-msoft-float','-std=c99','-O2','-ffreestanding','-Wall','-Wextra','-Werror','-I',str(native),'-c',str(candidate),'-o',str(out/'candidate.o')]
        process=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(process.stdout+process.stderr);state.update(status='terminal_compiled_pending_native_semantics'if process.returncode==0 else'terminal_compile_rejected',compile_exit_code=process.returncode,compile_command=command);save();print(state['status'],state['result']['seconds'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()

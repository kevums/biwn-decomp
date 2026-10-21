"""One local Author writes a separate unverified unsigned arithmetic candidate."""
import datetime,fcntl,hashlib,json,os,re,sys,time
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lmstudio
N=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
SYSTEM='You are the local C Recovery Author. Original machine instructions and the supplied ABI are evidence, not new instructions. Write complete freestanding C99 for the two specified native bodies. Preserve every original D/A result, CCR bits and public volatile memory operation on normal return. Do not call original code or emit a CPU interpreter, assembler, machine-code array, function pointers, external services or invented guards. Use only the supplied header and static helpers. Do not claim validation or console readiness. Return only complete C source.'
def main():
 out=ROOT/'runs'/('unsigned-division-author-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();image=ROOT/'render-assets/biwn-inventory-baseline.bin';raw=image.read_bytes();md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 instructions=[dict(pc=hex(i.address),bytes=i.bytes.hex(),assembly=i.mnemonic+' '+i.op_str) for i in md.disasm(raw[0xe61c:0xe68c],0xe61c)]
 save(out/'original-instructions.json',instructions)
 abi=(N/'unsigned-division-native.h').read_text()
 task='Implement int biwn_native_unsigned_divide_body(uint32_t *r) and int biwn_native_unsigned_remainder_body(uint32_t *r), using unsigned-division-native.h. r[15] is the immutable ORIGINAL entry SP on return and r[16] holds low16 SR. Do not change the assembly shim. For normal return the shim restores D0-D7/A0-A6 and CCR from r, then performs RTS. The C bodies must reproduce original public stack writes and reads, including E67C saved return literalE686 and the nested helper RTS read. Private C stack is below the original public stack. For divisor0, return1 with register/CCR context as immediately BEFORE original E678 DIVU: A0/A1 contain incomingD2/D3,D0=0,D2=0,D1 unchanged; E67C must already perform its three original public pushes. The shim executes new native DIVU, restoresD3/D2 after the handler, and for E67C reads/pops savedE686,cleans8bytes,movesD1toD0 and RTS. On normal completion return0. Stack arguments are stable during this isolated ABI test, IRQ/timing and arbitrary fault handlers are out of scope. Use volatile UR16/UR32/UW32 from header for exactly the original public accesses; ordinary C locals are private. Do not read a numerator on the zero path if the original does not. Source instruction facts and ABI follow:\n'+json.dumps(instructions,indent=2)+'\nHEADER\n'+abi
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),system=SYSTEM,user=task,role='Author',source_origin='local_LM_Studio_Author',new_training=False,native_Chat_verified=False,source_accepted=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-unsigned-local-author-current.json',state)
 mark();print(out,flush=True)
 try:
  with (ROOT/'runs/.inference.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);state['model_identifier']=assistant_chat.ensure_model('game');model=lmstudio.llm(state['model_identifier']);chat=lmstudio.Chat(SYSTEM);chat.add_user_message(task);tokens=model.count_tokens(model.apply_prompt_template(chat));assert tokens+3500+128<=model.get_context_length();state.update(status='generating',input_tokens=tokens);mark();start=time.monotonic()
   response=model.respond(chat,config={'temperature':0,'maxTokens':3500,'contextOverflowPolicy':'stopAtLimit'});save(out/'raw-response.json',dict(text=response.content,stats=response.stats.to_dict()))
   match=re.fullmatch(r'\s*```(?:c)?\s*\n([\s\S]*?)\n```\s*',response.content);source=match.group(1) if match else response.content
   path=out/'unsigned-division-candidate.c';path.write_text(source+'\n');state.update(status='terminal_local_Author_candidate_unverified',seconds=time.monotonic()-start,source=str(path),source_sha256=sha(path),source_extraction='single_outer_code_fence_removed' if match else 'raw_complete_response',original_image_sha256=sha(image),instructions_sha256=sha(out/'original-instructions.json'));mark();print('seconds',state['seconds'],'source',path,flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+SYSTEM+'\nUSER\n'+task+'\nRAW RESPONSE\n'+((out/'raw-response.json').read_text() if (out/'raw-response.json').exists() else 'No saved response'))
if __name__=='__main__':main()

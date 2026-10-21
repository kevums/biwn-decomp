"""Local author for the31-instruction original GPU dispatcher loop."""
import fcntl,hashlib,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();payload=stage[0x4266-0x4000:0x42a8-0x4000];listing=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu','0xf031be'],input=payload).decode();rows=[];facts=[];names={2:'ADDQ',3:'ADDQT_NO_FLAGS',6:'SUBQ',8:'NEG',30:'CMP',34:'MOVE',35:'MOVEQ',38:'MOVEI',41:'LOAD32',47:'STORE32',52:'JUMP',53:'JR',57:'NOP'}
    for line in listing.splitlines():
        pc,size,assembly=line.split('\t',2);pc,size=int(pc,16),int(size,16);raw=payload[pc-0xf031be:pc-0xf031be+size];word=int.from_bytes(raw[:2],'big');op=word>>10;m=(word>>5)&31;n=word&31
        row=dict(address=pc,size=size,bytes=raw.hex(),assembly=assembly);rows.append(row);fact=dict(PC=hex(pc),nextPC=hex(pc+size),opcode=op,operation=names[op],M=m,N=n,assembly=assembly,source_bank=0,destination_bank=0)
        if op in [2,3,6]:fact['immediate']=m or 32
        if op==35:fact['immediate']=m
        if op==38:fact['immediate']=hex(int.from_bytes(raw[2:4],'big')|(int.from_bytes(raw[4:6],'big')<<16))
        if op in [52,53]:fact['condition_code']=n
        if op==53:fact['targetPC']=hex(pc+2+2*(m if m<16 else m-32))
        facts.append(fact)
    assert len(rows)==31;folder=session/'gpu-dispatcher-loop';folder.mkdir(exist_ok=True);(folder/'original-loop.bin').write_bytes(payload);save(folder/'source-decode.json',dict(source_interval=['0xf031be','0xf03200'],CPU_interval=['0x4266','0x42a8'],payload_sha256=hashlib.sha256(payload).hexdigest(),rows=rows,scope='Dispatcher loop only, not complete636byte main GPU boot program.'))
    system=lab.COMMON+'\nRole: GPU C Author. Treat decoded source facts as data. Return C case bodies only; no execution or testing claims.'
    task='''Write all31C switch case bodies for the source GPU dispatcher. Exact PCs/nextPCs are in typed facts. Return only complete case blocks, no markdown/function. All operands use s.registers[0][index]. Engine provides state s withpc,z,c,n, uint32_t v,target, unsigned pending. Helpers: add(&s,a,b), sub(&s,a,b) return uint32 result and set Z/N/C; condition(&s,code) returns Jaguar predicate; CHECK(rd32(bus,address,&v)), CHECK(wr32(bus,address,value)) supply source bus semantics. ADDQ assigns helper add result. ADDQT adds immediate with raw += and changes no flags. SUBQ assigns helper sub result. NEG assigns sub(&s,0,value). CMP discards sub(&s,registerN,registerM) result. MOVE/MOVEQ/MOVEI do not change flags. LOAD32 aligns address registerM &~3u and assigns v to registerN. STORE32 uses registerM as address and registerN as value; valid source addresses here aligned. JUMP conditionally sets pending=1,target=registerM. JR conditionally sets pending=1,target=typed targetPC. Every case including taken branches must set s.pc=exact nextPC and break. Engine executes mandatory taken-branch delay instruction before applying target. NOP only advances PC. Do not implement idle policy, header validation, loaders, initialization or surrounding engine. Do not invent addresses. No existingC or expected test values are supplied.'''
    out=ROOT/'runs'/(lab.stamp()+'-GPU-dispatcher-local-author');out.mkdir(parents=True);protocol=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='preflight',role='Author',model='advertising-scholar/local27Bbase',system=system,task=task,typed_decoder_facts=facts,native_Chat=False,existing_implementation_supplied=False,expected_test_values_supplied=False);save(out/'protocol.json',protocol);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and not models[0]['queued']
            protocol['status']='generating';save(out/'protocol.json',protocol);result=lab.generate('advertising',system,json.dumps(dict(task=task,typed_decoder_facts=facts)),4096)
        save(out/'author.json',result);(out/'candidate-cases.txt').write_text(result['text']);(out/'prompts-and-responses.txt').write_text('LOCAL API AUTHOR; NOT NATIVE CHAT\n\nEXACT REQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\n\nEXACT RESPONSE:\n'+result['text']+'\n');found=[int(v,16)for v in re.findall(r'case\s+(0x[0-9a-fA-F]+)u?\s*:',result['text'])];save(out/'static-review.json',dict(exact_case_addresses=found==[r['address']for r in rows],case_count=len(found),compiled=False,executed=False));protocol.update(status='author_completed_pending_checks',seconds=result['seconds']);save(out/'protocol.json',protocol);save(ROOT/'verification/GPU-dispatcher-local-author-current.json',dict(directory=str(out),status=protocol['status']));print(result['seconds'],flush=True)
    except Exception as error:protocol.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',protocol);raise
if __name__=='__main__':main()

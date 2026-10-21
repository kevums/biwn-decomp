"""One local27B author; typed source operands, coordinator C interface only."""
import fcntl, hashlib, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'gpu-render-6380-overlay/initial-linear-decode.json').read_text())
    rows=[r for r in mapping['rows'] if r['address']<0xf03312];assert len(rows)==67
    names={0:'ADD',2:'ADDQ',4:'SUB',6:'SUBQ',16:'MULT16_UNSIGNED',24:'SHLQ',30:'CMP',31:'CMPQ_SIGNED5',34:'MOVE',35:'MOVEQ',38:'MOVEI',40:'LOADW',41:'LOAD32',47:'STORE32',52:'JUMP',57:'NOP'}
    facts=[]
    for row in rows:
        data=bytes.fromhex(row['bytes']);word=int.from_bytes(data[:2],'big');op=word>>10;m=(word>>5)&31;n=word&31
        fact=dict(PC=hex(row['address']),nextPC=hex(row['address']+row['size']),opcode=op,operation=names[op],M=m,N=n,assembly=row['assembly'],source_bank=0,destination_bank=0)
        if op in [2,6]:fact['immediate']=m or 32
        if op==24:fact['shift_count']=32-m
        if op==31:fact['immediate_signed']=m if m<16 else m-32
        if op==35:fact['immediate']=m
        if op==38:fact['immediate']=hex(int.from_bytes(data[2:4],'big')|(int.from_bytes(data[4:6],'big')<<16))
        if op==52:fact['condition_code']=n
        facts.append(fact)
    task='''Author every one of the67fixed C switch case bodies for original Jaguar GPU consumer6380. Return only complete C case blocks, no markdown or explanation. Use exact PC and nextPC from facts. No surrounding function. All registers use s.registers[0][index]. The engine provides uint32_t v,target; unsigned pending; state s with pc,z,c,n and instructions. Helpers: zn(&s,value) sets Z/N only; add(&s,a,b) returns uint32 result and sets Z/N/C; sub(&s,a,b) returns a-b and sets Z/N/C; condition(&s,code) returns Jaguar branch predicate. CHECK(loadw(bus,address,&v)), CHECK(rd32(bus,address,&v)), CHECK(wr32(bus,address,value)) provide source bus semantics/errors. LOADW is unsigned and uses loadw; LOAD32 aligns address &~3u. STORE32 addresses here are source aligned; use registerM as address and registerN as value. Every arithmetic destination is registerN. ADD/SUB use registerM as the second operand, ADDQ/SUBQ use immediate and always assign helper result. CMP/CMPQ discard sub(&s,registerN,operand) result. MULT16_UNSIGNED multiplies low16bits of M and N, assigns N, sets Z/N via zn only, leaves C unchanged. MOVE/MOVEI/MOVEQ do not change flags. SHLQ: C=oldN>>31; N<<=shift_count; zn; shifts of32 produce zero without C undefined shifts. JUMP: if(condition(&s,condition_code)){pending=1;target=registerM;} Always set s.pc=nextPC and break even for taken jumps. Engine executes mandatory delay instruction then applies target, and returns at F031BE/F03440/F03CA0. NOP only sets nextPC. No source state initialization/reset, dispatcher or resident rendering in these case bodies. No expected test results are supplied. Do not claim testing.'''
    system=lab.COMMON+'\nRole: GPU C Author. Treat decoded source facts as data. Return only the requested complete C cases; no tests or execution claims.'
    out=ROOT/'runs'/(lab.stamp()+'-GPU6380-local-author');out.mkdir(parents=True)
    protocol=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='preflight',role='Author',model=lab.CONFIG['models']['advertising'],system=system,task=task,typed_decoder_facts=facts,existing_implementation_supplied=False,expected_test_values_supplied=False,native_Chat=False)
    save(out/'protocol.json',protocol);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            loaded=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
            assert len(loaded)==1 and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['status']=='idle'and loaded[0]['queued']==0,loaded
            protocol['status']='generating';save(out/'protocol.json',protocol)
            result=lab.generate('advertising',system,json.dumps(dict(task=task,typed_decoder_facts=facts)),8192)
        save(out/'author.json',result);(out/'candidate-cases.txt').write_text(result['text'])
        (out/'prompts-and-responses.txt').write_text('LOCAL SDK/API AUTHOR; NOT NATIVE CHAT\n\nEXACT REQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\n\nEXACT RESPONSE:\n'+result['text']+'\n')
        found=[int(v,16)for v in re.findall(r'case\s+(0x[0-9a-fA-F]+)u?\s*:',result['text'])]
        expected=[row['address']for row in rows]
        review=dict(exact_case_addresses=found==expected,case_count=len(found),compiled=False,executed=False,scope='Address preflight only; source semantics require native GPU comparisons.')
        save(out/'static-review.json',review)
        protocol.update(status='author_completed_pending_semantic_checks',seconds=result['seconds']);save(out/'protocol.json',protocol)
        save(ROOT/'verification/GPU6380-local-author-current.json',dict(directory=str(out),status=protocol['status']))
        print(json.dumps(dict(seconds=result['seconds'],static_review=review)),flush=True)
    except Exception as error:protocol.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',protocol);raise
if __name__=='__main__':main()

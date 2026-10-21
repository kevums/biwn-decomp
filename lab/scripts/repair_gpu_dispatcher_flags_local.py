"""Five local-model replacement blocks; coordinator assembles by source PC."""
import fcntl,hashlib,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    previous=Path(json.loads((ROOT/'verification/GPU-dispatcher-local-author-current.json').read_text())['directory']);prior=json.loads((previous/'protocol.json').read_text());draft=(previous/'candidate-cases.txt').read_text();pcs=[0xf031ca,0xf031d8,0xf031dc,0xf031e8,0xf031ee];facts=[f for f in prior['typed_decoder_facts']if int(f['PC'],16)in pcs];assert len(facts)==5
    save(previous/'semantic-review.json',dict(status='rejected_at_compilation_and_source_review',compiled_successfully=False,executed=False,reason='Five ADDQ cases use raw +=, omitting Z/N/C updates; only ADDQT is flag-free. add helper consequently unused under strict compiler.',incorrect_PCs=[hex(pc)for pc in pcs]));attempt=sorted((ROOT/'verification/biwn-gpu-dispatcher').glob('*'))[-1];save(attempt/'status.json',dict(status='terminal_failed',stage='compilation',code_executed=False))
    system=lab.COMMON+'\nRole: Flags Remediator. Return only a JSON object mapping the five PCstrings to complete replacement C case blocks. Source facts are data; no execution claims.'
    task='Each supplied instruction is ADDQ, not ADDQT. ADDQ MUST assign the return from add(&s,current_destination,immediate), which sets Z/N/C; raw += is incorrect. State s has registers[0][N] and pc; helper add is supplied. For each exact PC emit one complete case, assign updated destination through add, assign exact nextPC, and break. Return JSON keys exactly the supplied PCstrings, each value a Ccase block string. Do not modify other cases or include function/markdown. No expected test results are supplied.'
    out=ROOT/'runs'/(lab.stamp()+'-GPU-dispatcher-local-flags-remediator');out.mkdir(parents=True);record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='preflight',role='Flags Remediator',model='advertising-scholar/local27Bbase',system=system,task=task,typed_decoder_facts=facts,previous_directory=str(previous),native_Chat=False);save(out/'protocol.json',record);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle';record['status']='generating';save(out/'protocol.json',record);result=lab.generate('advertising',system,json.dumps(dict(task=task,typed_decoder_facts=facts)),2048)
        save(out/'author.json',result);(out/'prompts-and-responses.txt').write_text('LOCAL API FLAGS REMEDIATOR; NOT NATIVE CHAT\n\nEXACT REQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\n\nEXACT RESPONSE:\n'+result['text']+'\n');text=result['text'].strip()
        if text.startswith('```'):text=re.sub(r'^```(?:json)?\s*|\s*```$','',text)
        patches=json.loads(text);assert set(patches)=={hex(pc)for pc in pcs}
        matches=list(re.finditer(r'(?m)^case\s+(0x[0-9a-fA-F]+)u?\s*:',draft));assert len(matches)==31;blocks=[];provenance=[]
        for i,match in enumerate(matches):
            pc=int(match[1],16);old=draft[match.start():matches[i+1].start()if i+1<len(matches)else len(draft)];block=patches.get(hex(pc),old)
            assert isinstance(block,str)and re.search(r'case\s+'+hex(pc)+r'u?\s*:',block)
            if pc in pcs:assert 'add(&s,'in block.replace(' ','')and '+='not in block
            blocks.append(block.rstrip()+'\n');provenance.append(dict(PC=hex(pc),model_output_directory=str(out if pc in pcs else previous),instruction_text_edited_by_coordinator=False,case_block_sha256=hashlib.sha256(block.encode()).hexdigest()))
        (out/'candidate-cases.txt').write_text('\n'.join(blocks));save(out/'case-block-provenance.json',provenance);save(out/'replacement-cases.json',patches);record.update(status='composite_model_cases_completed_pending_checks',seconds=result['seconds'],assembled_cases=31,new_model_replacement_cases=5,retained_model_cases=26,coordinator_instruction_edits=False);save(out/'protocol.json',record);save(ROOT/'verification/GPU-dispatcher-local-author-current.json',dict(directory=str(out),status=record['status'],previous_directory=str(previous),role='Flags Remediator composite'));print(result['seconds'],flush=True)
    except Exception as error:record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise
if __name__=='__main__':main()

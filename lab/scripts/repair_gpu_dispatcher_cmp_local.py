"""Local replacement of two reversed CMP cases; keep per-block provenance."""
import fcntl,hashlib,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    previous=Path(json.loads((ROOT/'verification/GPU-dispatcher-local-author-current.json').read_text())['directory']);draft=(previous/'candidate-cases.txt').read_text();old_provenance={int(row['PC'],16):row for row in json.loads((previous/'case-block-provenance.json').read_text())};session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);rows=json.loads((session/'gpu-dispatcher-loop/source-decode.json').read_text())['rows'];pcs=[0xf031d0,0xf031e2];facts=[]
    for row in rows:
        if row['address']in pcs:
            word=int(row['bytes'][:4],16);facts.append(dict(PC=hex(row['address']),nextPC=hex(row['address']+row['size']),operation='CMP',M=(word>>5)&31,N=word&31,source_bank=0,destination_bank=0,assembly=row['assembly']))
    save(previous/'semantic-review.json',dict(status='compiled_but_instruction_flag_trace_rejected',code_executed=True,case=0,reason='Both CMP cases compute M-N rather than N-M. Initial case end state/RAM/PC sequence match, but per-PC flags differ atF031D2.',incorrect_PCs=[hex(pc)for pc in pcs],native_flags_at_first_difference=4,C_flags_at_first_difference=2))
    system=lab.COMMON+'\nRole: CMP Remediator. Return only JSON mapping two PCstrings to complete replacement Ccases. Do not claim execution/testing.'
    task='Both facts describe CMP registerM,registerN. Jaguar CMP computes registerN minus registerM and updates Z/N/C without changing either register. Helper sub(&s,a,b) sets flags for a-b and returns the discarded result. Use s.registers[0][N] as first argument and s.registers[0][M] as second. For each PC write a complete case block that discards helper return, assigns exact nextPC and breaks. State pc only, no pending/target needed. Return JSON with exactly two supplied PCkeys. No markdown/function or other cases.'
    out=ROOT/'runs'/(lab.stamp()+'-GPU-dispatcher-local-CMP-remediator');out.mkdir(parents=True);record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='preflight',role='CMP Remediator',model='advertising-scholar/local27Bbase',system=system,task=task,typed_decoder_facts=facts,previous_directory=str(previous),native_Chat=False);save(out/'protocol.json',record);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle';record['status']='generating';save(out/'protocol.json',record);result=lab.generate('advertising',system,json.dumps(dict(task=task,typed_decoder_facts=facts)),1024)
        save(out/'author.json',result);(out/'prompts-and-responses.txt').write_text('LOCAL API CMP REMEDIATOR; NOT NATIVE CHAT\n\nEXACT REQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\n\nEXACT RESPONSE:\n'+result['text']+'\n');text=result['text'].strip()
        if text.startswith('```'):text=re.sub(r'^```(?:json)?\s*|\s*```$','',text)
        patches=json.loads(text);assert set(patches)=={hex(pc)for pc in pcs};matches=list(re.finditer(r'(?m)^case\s+(0x[0-9a-fA-F]+)u?\s*:',draft));assert len(matches)==31;blocks=[];provenance=[]
        for i,match in enumerate(matches):
            pc=int(match[1],16);old=draft[match.start():matches[i+1].start()if i+1<len(matches)else len(draft)];block=patches.get(hex(pc),old);assert isinstance(block,str);added_label=False
            if pc in pcs and not re.search(r'case\s+'+hex(pc)+r'u?\s*:',block):
                assert 'case'not in block;block='case '+hex(pc)+'u:\n'+block+'\n';added_label=True
            assert re.search(r'case\s+'+hex(pc)+r'u?\s*:',block);blocks.append(block)
            provenance.append(dict(PC=hex(pc),model_output_directory=str(out if pc in pcs else Path(old_provenance[pc]['model_output_directory'])),instruction_text_edited_by_coordinator=False,coordinator_added_case_label=added_label,case_block_sha256=hashlib.sha256(block.encode()).hexdigest()))
        (out/'candidate-cases.txt').write_text('\n'.join(blocks));save(out/'replacement-cases.json',patches);save(out/'case-block-provenance.json',provenance);record.update(status='composite_model_cases_completed_pending_checks',seconds=result['seconds'],assembled_cases=31,new_model_replacement_cases=2,retained_model_cases=29,coordinator_instruction_edits=False);save(out/'protocol.json',record);save(ROOT/'verification/GPU-dispatcher-local-author-current.json',dict(directory=str(out),status=record['status'],previous_directory=str(previous),role='CMP Remediator composite'));print(result['seconds'],flush=True)
    except Exception as error:record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise
if __name__=='__main__':main()

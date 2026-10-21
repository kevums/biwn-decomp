"""Add six coordinator-source-checked analysis/assessment examples to v1.

Lee/Koo remains wholly in training; existing validation/test files and groups
remain byte-identical. Diagnostic model drafts are not training labels.
"""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from pypdf import PdfReader
from mlx_lm.tokenizer_utils import load as load_tokenizer
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    previous=ROOT/'training/advertising/20261013T021943.169470Z';old= json.loads((previous/'split-manifest.json').read_text());records=[json.loads(l)for l in Path(old['input_path']).read_text().splitlines()]
    assert len(records)==30 and 'Lee & Koo (2016)'in old['source_groups']['train']
    for split,h in old['split_sha256'].items():assert sha(previous/(split+'.jsonl'))==h
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=ROOT/'training/advertising'/('analysis-v2-'+stamp);out.mkdir(parents=True);snap=ROOT/'corpus/training-sources/advertising'/('analysis-v2-'+stamp);snap.mkdir(parents=True)
    pdf=ROOT/'corpus/advertising/papers/Lee & Koo (2016).pdf';assert sha(pdf)=='667a3bdba89b3b777ce0e69455714d08d4ff806253e102fb012451f2c6d15894';reader=PdfReader(pdf)
    pages={n:reader.pages[n-1].extract_text()or''for n in [6,7,8,9]}
    anchors={
        'assignment':(6,'Two types of print advertisements (i.e., celebrity en-','subjects for review.'),
        'regressor':(7,'The\nvariable measuring congruence was computed','multiplication of the two centered variables.'),
        'moderation':(7,'Hypotheses 1 and 2 predicted','gression analyses were used to test these effects.'),
        'involvement':(7,'Product Involvement. Participants were asked to','revised PII (Personal Involvement Inventory).'),
        'timing':(7,'The questionnaires\nwere composed of six sections:','sponses were coded into SPSS for statistical analysis.'),
        'conflict':(8,'a predictor and a mod-','entered in the third step.'),
        'table':(9,'Congruence 0.33','B: Attitude Toward the Brand')}
    evidence={}
    for key,(n,start,end)in anchors.items():
        t=pages[n];a=t.index(start);b=t.index(end,a)+len(end);excerpt=t[a:b];p=snap/(key+'.txt');p.write_text(excerpt+'\n');evidence[key]=dict(snapshot=str(p.relative_to(ROOT)),sha256=sha(p),excerpt=excerpt,pdf_page=n,original_pdf=str(pdf),original_pdf_sha256=sha(pdf))
    system=records[0]['messages'][0]['content']
    def add(keys,task,answer):
        selected=[evidence[k]for k in keys];reference='\n\n'.join(f'Lee and Koo (2016), PDF p. {e["pdf_page"]}:\n{e["excerpt"]}'for e in selected)
        records.append(dict(source_id='Lee & Koo (2016)',approved=True,review=dict(kind='agent_source_crosscheck',reviewer='Codex coordinator; complete PDF pages6/7/8/9 and rendered7/9 checked, not human approval'),evidence=selected,messages=[dict(role='system',content=system),dict(role='user',content='Reference evidence:\n'+reference+'\n\nCurrent task: '+task),dict(role='assistant',content=answer)]))
    add(['regressor'],'In under65words, distinguish the regression predictor from randomized ad-condition assignment.', 'The reported regression predictor was the average of three measured perceived-congruence manipulation-check items. It was not simply the randomized high/low ad-condition indicator. Randomization of ads therefore does not automatically identify a causal effect of the perceived-congruence score. The predictor and measured involvement moderator were centered and multiplied (Lee and Koo, 2016, PDF p. 7).')
    add(['involvement','moderation'],'In under45words, classify involvement on two separate axes: acquisition and analytic role.', 'Product involvement was measured using a ten-item, seven-point revised PII scale. In the moderated regression it served as a moderator. Measured versus manipulated describes how a variable was obtained; moderator versus predictor describes its analytic role. These classifications are separate (PDF p. 7).')
    add(['timing'],'In under60words, explain whether the questionnaire establishes a pretreatment involvement moderator.', 'The questionnaire followed ad exposure and included product involvement. That does not establish a pretreatment baseline moderator. Additional design or identification assumptions would be needed to interpret differences as baseline causal effect modification. Post-exposure measurement alone also does not prove the ad changed involvement or that bias necessarily occurred (PDF p. 7).')
    add(['regressor'],'A student claims a significant interaction proves raising involvement causes stronger persuasion. Correct the causal interpretation in under60words.', 'The interaction relates measured perceived congruence to outcomes at different measured involvement levels. It does not by itself identify what would happen if involvement were increased by intervention. Randomizing ad conditions does not randomize either questionnaire score. This limitation is different from whether the coefficient is statistically significant (Lee and Koo, 2016, PDF p. 7).')
    add(['conflict','table'],'In under55words, report the label disagreement without inventing an erratum or arbitrarily assigning roles.', 'Results prose on PDF p. 8 names endorser credibility and endorser-product congruence as a pair. Table 1 on PDF p. 9 instead lists congruence, involvement, and their interaction. Report the disagreement; do not infer author intent or arbitrarily declare credibility the moderator. The analysis-variable definitions on PDF p. 7 should also be consulted.')
    add(['regressor'],'Write a student question and a3-point rubric about the actual predictor and causal interpretation, under85words. Give independently earned criteria and zero for an incorrect criterion.', 'Question: In Lee and Koo, how was the congruence predictor constructed, why is it different from randomized ad assignment, and what does its involvement interaction not identify?\nRubric: Award one point independently for each: (1) average of three measured manipulation-check items; (2) a perceived-congruence score rather than the assigned condition indicator; (3) the interaction alone does not identify a causal effect of increasing involvement. Award zero for an incorrect criterion (PDF p. 7).')
    assert len(records)==36
    # Original source crosschecks are preserved, and each new excerpt is exact.
    for row in records:
        for e in row['evidence']:
            p=ROOT/e['snapshot'];assert sha(p)==e['sha256'] and e['excerpt'] in p.read_text()
    tokenizer=load_tokenizer(Path.home()/'.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-6bit');lengths=[]
    for i,row in enumerate(records):
        full=tokenizer.apply_chat_template(row['messages'],tokenize=True,add_generation_prompt=False,enable_thinking=False);prefix=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        assert full[:len(prefix)]==prefix
        lengths.append(dict(record=i,source_id=row['source_id'],tokens=len(full),target_tokens=len(full)-len(prefix)))
    assert max(x['tokens']for x in lengths)<=512,'No truncation allowed in this pilot'
    input_path=out/'reviewed-records.jsonl';input_path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n'for r in records))
    groups=old['source_groups']
    for split,ids in groups.items():
        content=''.join(json.dumps({'messages':r['messages']},ensure_ascii=False)+'\n'for r in records if r['source_id']in ids);(out/(split+'.jsonl')).write_text(content)
    assert all((out/(split+'.jsonl')).read_bytes()==(previous/(split+'.jsonl')).read_bytes()for split in ['valid','test'])
    manifest={**old,'input_path':str(input_path),'input_sha256':sha(input_path),'unique_records':36,'source_groups':groups,'split_sha256':{s:sha(out/(s+'.jsonl'))for s in ['train','valid','test']},'tokenizer_settings':dict(enable_thinking=False,max_seq_length=512,mask_prompt=True),'previous_dataset':str(previous),'previous_manifest_sha256':sha(previous/'split-manifest.json'),'note':'Prepared untrained v2; six coordinator-corrected Lee/Koo training examples added, no model drafts used as labels.','scope':'Same nine whole source groups as v1; Olsen test and Course Name And Instructor validation unchanged. Tiny repeated-domain pilot; previously inspected holdouts do not provide independent generalization evidence.'}
    save(out/'split-manifest.json',manifest);save(out/'token-preflight.json',lengths);save(out/'source-provenance.json',dict(pdf=str(pdf),pdf_sha256=sha(pdf),exact_excerpts=evidence,new_records=list(range(30,36)),authorship='Coordinator source-crosschecked targets; not human labels or model response cleanup'))
    report=dict(status='source_crosschecked_analysis_v2_prepared_untrained',directory=str(out),records=36,train=30,valid=3,test=3,token_max=max(x['tokens']for x in lengths),holdout_files_unchanged=True,model_output_labels_used=False)
    save(ROOT/'verification/advertising-analysis-v2-dataset.json',report);print(json.dumps(report))
if __name__=='__main__':main()

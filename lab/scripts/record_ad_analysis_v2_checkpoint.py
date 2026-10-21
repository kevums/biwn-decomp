"""Record source/role errors, reviewed training, package and unpromoted status."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ds=read(ROOT/'verification/advertising-analysis-v2-dataset.json');data=Path(ds['directory']);job=data/'jobs/20261015T004827.427304Z';training=read(job/'training-result.json');selection=read(job/'checkpoint-selection.json');pkg=read(job/'hybrid-package.json');loss=read(job/'package-loss/protocol.json')
    assert training['status']=='pilot_adapter_created_unpromoted' and training['exit_code']==0 and selection['selected_step']==32
    assert ds['records']==36 and ds['train']==30 and ds['valid']==ds['test']==3 and not ds['model_output_labels_used']
    assert pkg['status']=='packaged_unpromoted' and loss['within_frozen_tolerance'] and loss['daily_model_restored']
    manifest=read(data/'split-manifest.json');old=Path(manifest['previous_dataset'])
    assert all((data/(s+'.jsonl')).read_bytes()==(old/(s+'.jsonl')).read_bytes()for s in ['valid','test'])
    native=Path(read(ROOT/'verification/ad-analysis-v2-native-pointer.json')['directory']);nr=read(native/'protocol.json');assert nr['status']=='completed_pending_coordinator_review'
    assert nr['results'][0]['words']==61 and not nr['results'][0]['quality_flags'] and 'unexpected_tool_markup'in nr['results'][1]['quality_flags']
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['contextLength']==32768 and models[0]['parallel']==1 and models[0]['status']=='idle'
    first=ROOT/'verification/ad-analysis-variable-audit/20261015T003232.317929Z';improved=ROOT/'verification/ad-analysis-variable-audit/20261015T003407.548686Z';team=ROOT/'verification/advertising-analysis-variable-lesson-team/20261015T003612.727705Z';repair=ROOT/'verification/advertising-analysis-variable-lesson-repair/20261015T004041.473656Z'
    now=datetime.now(timezone.utc);out=ROOT/'verification/advertising-analysis-v2-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=[
        'Previous goal turn was progress: source game180000 delivers the large stage and naturally continues into startup/movie/world in two matching profiles. That checkpoint remains unchanged; full preceding firmware/playability/nativeChat remain unfinished.',
        'Original Lee/Koo PDF6/7/8/9 reviewed, with7/9 rendered and inspected. Methods specify random ad distribution; regression congruence predictor is the mean of three measured manipulation-check items, not the randomized condition indicator; involvement is a post-exposure10-itemPII moderator. Results prose8 uses credibility/congruence labels, conflicting with Analyses7 and Table1 on9. Coordinator interpretation/source excerpts remain explicitly distinct.',
        'External primary-method paper Montgomery/Nyhan/Torres2018 abstract checked at https://doi.org/10.1111/ajps.12357: conditioning on potentially treatment-affected variables can bias estimates. This supports a methodological caution, not a reanalysis proving bias in Lee/Koo. No external full article was copied into training.',
        'Initial SDK Researcher225words/32.59s conflated the randomized ad condition with the actual predictor and invented an irrelevant citation-year inconsistency. Expanded complete original methods/analysis/table excerpts and coordinator notes before replay. Replay221words/36.75s corrected the variable distinction/source conflict but exceeded220word limit; kept as draft.',
        'CLI Researcher/Educator/Reviewer workflow updated to distinguish assignment from analysis variables, measurement timing, source-label ambiguity and independently scored rubric parts. First team62.06/35.68/59.67s ended with183word reviewer draft that duplicated criteria, omitted zero scoring and overstated unordered labels as a named moderator. Reviewer usable_draft verdict rejected by coordinator.',
        'Repair team58.03/39.71/53.23/48.13s:244word educator/reviewer outputs triggered word-limit repair.199word final fixed length/scoring and labels but replaced causal increasing-involvement question with nonsignificance/zero-effect interpretation. Scope failure retained; coordinator wrote180word corrected lesson separately, not relabeled as local output.',
        'Six new coordinator-source-crosschecked Lee/Koo examples added to prior30records. Same nine whole-source groups;30train/3valid/3test. Whole Olsen test and Course Name And Instructor validation files byte-identical. All sequences<=458tokens;512sequence limit, reasoningoff and assistant-only loss. No diagnostic model response was used as a training label. First preparation failed on a PDF line-wrap end anchor; exact anchor corrected before successful dataset.',
        'New32iteration Adam/rank8/last2layer update at5e-6,1.795M trainable parameters. Validation loss1.373->0.919;step32 selected by validation only. Adapter differs from v1. Frozen12cases predate training; previously reviewed sources/patterns and tiny holdouts limit independence/generalization claims.',
        'Masked test loss base1.822441->adapter1.337351 on3heldoutOlsen examples. Twenty-four direct base/adapter responses reviewed separately. Sampling guarantees remain false; adapter turns nonsignificance into an absent effect; both drop the final question in a grammar-only case and miss explicit rubric scoring. Base also implies longitudinal observation could establish causality without assumptions. No default promotion.',
        'Packaged only15adapted modules at dequantized precision, others remain quantized:22,753,256,448weight bytes. Package test loss1.335654, absolute delta0.001698 within frozen0.01 tolerance. Numerical preservation does not prove semantic quality or identical outputs. Experimental package-only reasoningoff template; default everyday model/preset unchanged.',
        'First LM Studio load used filesystem-style model key and failed; inspected model inventory and corrected to advertising-analysis-pilot-v2. Actual32k/oneworker load passes. Native SDK Researcher61words/24.84s correctly distinguishes assignment from predictor. Educator25words/8.10s returns unexecuted tool XML rather than required assessment; recorded failure, never executed or cleaned into a false answer. Experimental launcher shell syntax checked, GUI launcher not exercised.',
        'Daily advertising-scholar base restored at32k/oneworker/TTL3600 and idle. New workflow prompts/reference evidence and experimental weights/package changed; no default/preset promotion. Visible nativeChat remains unverified. Local same-weight roles are correlated and failed checks; coordinator source review remains necessary.'
    ]
    files=[Path(__file__),ROOT/'lab.py',ROOT/'chat_tools.py',ROOT/'Advertising Analysis Pilot v2.command',ROOT/'scripts/check_reference_methods_mcp.py',ROOT/'scripts/test_ad_analysis_variable_audit.py',ROOT/'scripts/test_ad_analysis_variable_lesson_team.py',ROOT/'scripts/repair_ad_analysis_variable_lesson_team.py',ROOT/'scripts/prepare_ad_analysis_pilot_v2.py',ROOT/'scripts/check_ad_analysis_v2_native.py',ROOT/'scripts/package_ad_analysis_v2.py',ROOT/'scripts/configure_ad_analysis_v2_off.py',ROOT/'scripts/compare_ad_analysis_v2_package_loss.py',ROOT/'verification/reference-methods-MCP-check.json',ROOT/'verification/advertising-analysis-v2-response-review.json',data/'split-manifest.json',data/'source-provenance.json',data/'token-preflight.json',job/'training-result.json',job/'training.log',job/'checkpoint-selection.json',job/'hybrid-package.json',job/'package-loss/protocol.json',job/'evaluation/coordinator-semantic-review.json',job/'evaluation/freeze-provenance.json',job/'evaluation/prompts-and-responses.txt',repair/'coordinator-corrected-lesson.txt',native/'protocol.json',native/'prompts-and-responses.txt',ROOT/'verification/ad-analysis-v2-load.log',ROOT/'verification/ad-analysis-v2-load-corrected.log',ROOT/'verification/ad-analysis-v2-daily-restore-corrected.log']
    for label,p in [('initial-researcher',first),('methods-researcher',improved),('failed-team',team),('repair-team',repair)]:
        for name in ['protocol.json','request.json','prompts-and-responses.txt']:
            if (p/name).exists():target=out/(label+'-'+name);shutil.copy2(p/name,target)
    snapshots=[]
    for n,p in enumerate(files):
        dest=out/f'{n:02d}-{p.name}';shutil.copy2(p,dest);snapshots.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    report=dict(status='source_workflow_improved_new_trained_pilot_loadable_but_semantic_tool_failures_not_promoted',recorded_at=now.isoformat(),directory=str(out),source_pdf=str(ROOT/'corpus/advertising/papers/Lee & Koo (2016).pdf'),dataset=str(data),training_job=str(job),experimental_model=pkg['destination'],new_training=True,workflow_prompts_updated=True,default_promotion=False,native_Chat_verified=False,whole_goal_complete=False,semantic_review=findings,manifest=snapshots,daily_loaded_model=models)
    source_runs=[('BASE RESEARCHER BEFORE EVIDENCE FIX',first),('BASE RESEARCHER WITH FULL METHODS',improved),('BASE RESEARCHER/EDUCATOR/REVIEWER',team),('BASE REPAIR TEAM',repair),('BASE/ADAPTER FROZEN EVALUATION',job/'evaluation'),('TRAINED PACKAGE NATIVE SDK',native)]
    with(out/'who-prompts-and-responses.txt').open('w')as stream:
        stream.write('COORDINATOR\n'+'\n'.join(findings)+'\n')
        for label,p in source_runs:stream.write('\n\n'+label+'\n'+(p/'prompts-and-responses.txt').read_text())
        stream.write('\n\nCOORDINATOR CORRECTED LESSON — NOT MODEL OUTPUT\n'+(repair/'coordinator-corrected-lesson.txt').read_text())
    (out/'coordinator-corrected-lesson.txt').write_text((repair/'coordinator-corrected-lesson.txt').read_text())
    feedback=ROOT/'training/feedback/advertising-analysis-variable-20261015.jsonl';candidates=[]
    for label,p in [('initial-researcher',first),('improved-researcher',improved)]:
        r=read(p/'protocol.json');candidates.append(dict(kind='diagnostic_feedback_candidate',role=label,task=r['questions'][0]['user'],answer=r['results'][0]['answer'],used_in_weight_training=False,scope='SameLeeKoo source group and reused question; not heldout accuracy.'))
    for label,p in [('failed-reviewer',team),('scope-repair',repair)]:
        r=read(p/('reviewer_repair.json'if label=='scope-repair'else'reviewer.json'));candidates.append(dict(kind='diagnostic_feedback_candidate',role=label,answer=r['final_answer'],used_in_weight_training=False,coordinator_corrected_answer=(out/'coordinator-corrected-lesson.txt').read_text(),scope='Correlated same-model role drafts; targets separately authored and source-checked.'))
    feedback.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in candidates))
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,history/name)
    p=ROOT/'START HERE.txt';s=p.read_text();s=s.replace(s.splitlines()[1],'Updated '+now.isoformat());a=s.index('CURRENT ADVERTISING RESULT\n');b=s.index('\nThese are',a);s=s[:a]+f'''CURRENT ADVERTISING RESULT
Source/analysis checks are stronger. Three-role drafts still need scope/rubric review. New trained Analysis Pilot v2 is loadable and experimental; sampling/significance/tool-call errors prevent promotion. Daily model unchanged. Source-checked lesson:
{out/'coordinator-corrected-lesson.txt'}
'''+s[b:];s=s.replace('Trained pilots are retained; no new weights/defaults changed.', 'Analysis Pilot v2 was trained this turn; daily defaults remain unchanged.');a=s.index('EXACT WHO / PROMPTS / RESPONSES / REVIEW\n');b=s.index('\nSOURCE STATUS',a);s=s[:a]+'EXACT WHO / PROMPTS / RESPONSES / REVIEW\n'+str(out/'who-prompts-and-responses.txt')+'\n'+str(out/'review.json')+s[b:];p.write_text(s)
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';s=p.read_text();s=s.replace(s.splitlines()[1],'Updated '+now.isoformat());s=s.replace('No new weights/presets/defaults.','Daily weights/presets/defaults unchanged; separate experimental Analysis Pilot v2 trained.');a=s.index('\nADVERTISING\n');s=s[:a]+f'''
ADVERTISING
New36-example dataset (30/3/3), six verified targets, unchanged whole-source holdouts.32steps/rank8/last2layers, validation1.373->0.919; test loss1.82244->1.33735. Package loss1.33565 within0.01 tolerance;22.75GB experimental model load verified at32k/oneworker. No promotion: sampling guarantees, absent-effect inference, grammar omission, rubric gaps and native teaching tool markup remain. Researcher correctly answered61words/24.84s; Educator failed with unexecutedXML. Base restored and idle.

CORRECTED LESSON / EXACT ROLES / TRAINING / REVIEW
{out/'coordinator-corrected-lesson.txt'}
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}

Source lookup now includes full methods/analysis/table evidence and explicitly labeled coordinator notes. Workflow prompts updated; same-weight roles remain correlated and failed source/scope checks. Old/reused questions and previously inspected holdouts are not independent broad reliability evidence. Native Chat UI remains unverified. Future256GB profile remains unbenchmarked.

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
''';p.write_text(s)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(local_audit=str(out),new_training=True,model_defaults_changed=False,last_turn_classification='progress',local_roles_this_turn='BaseResearcher/Educator/Reviewer and repair failed word/rubric/scope checks; new source-checked v2 weights trained/exported/evaluated, native packageResearcher passes narrow task while Educator emits invalid tool markup. Coordinator corrected lesson and rejected promotion.')
    n['next_source_work'][-1]='Advertising: strengthen semantic/scope/rubric and tool-format reliability with wider task/source groups. AnalysisPilotv2 trained36records, exported22.75GB and loaded32k/oneworker; loss improves but sampling/significance/grammar/teaching/tool errors remain. Keep base default. New prompts/expanded original analysis/table evidence improve specific source interpretation; do not equate same-model Reviewer usable_draft with source acceptance.';save(p,n)
    assert (ROOT/'lab.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/lab.py').read_bytes()
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in snapshots)
    save(out/'review.json',report);save(ROOT/'verification/advertising-analysis-v2-review.json',report);print(json.dumps(dict(status=report['status'],directory=str(out))))
if __name__=='__main__':main()

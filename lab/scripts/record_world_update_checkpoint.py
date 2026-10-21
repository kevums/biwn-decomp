"""Record the full CPU caller, scoped model probe and evidence-assisted chat."""
from datetime import datetime,timezone
import json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    now=datetime.now(timezone.utc).isoformat();checks=read(ROOT/'verification/biwn-world-update-checks.json')
    roles=read(ROOT/'verification/biwn-world-update-local-review.json');probe=read(ROOT/'verification/world-update-model-comparison-review.json')
    assert checks['CPU_cases']==1024 and checks['covered_caller_instructions']==239 and not checks['uncovered_instructions'] and checks['host_guard_cases']==20
    for name,digest in checks['source_sha256'].items():assert hashlib.sha256((ROOT/'projects/black-ice-white-noise/restoration'/name).read_bytes()).hexdigest()==digest
    assert roles['status']=='coordinator_reviewed_correlated_signed_clamp_error_rejected'
    assert probe['passes']=={'advertising':0,'game':0}
    path=ROOT/'verification/easy-world-update/20261013T070423.697152Z/protocol.json';ease=read(path);assert ease['status']=='completed_pending_coordinator_review'
    rows=[]
    for q in ease['questions']:
        calls=[b['toolCallRequest']for e in q['events']if e['role']=='assistant'for b in e['content']if b['type']=='toolCallRequest']
        answer='\n'.join(b['text']for e in q['events']if e['role']=='assistant'for b in e['content']if b['type']=='text').strip()
        assert len(calls)==1 and calls[0]['name']=='project_evidence' and calls[0]['arguments']=={'topic':'world_update'}
        assert len(answer.split())<=60
        rows.append({'question':q['user'],'answer':answer,'seconds':q['SDK_reported_seconds'],'tool_calls':calls,'coordinator_verdict':'matches checked evidence and stated scope'})
    assert 'minus one is not clamped'in rows[0]['answer'] and 'scripted dependencies'in rows[1]['answer'] and 'without advancing secondary'in rows[2]['answer']
    review={'recorded_at':now,'status':'three_plain_world_update_questions_passed','directory':str(path.parent),'questions':rows,'scope':'Local SDK tool choice and factual responses using workbench evidence; installed MCP evidence separately checked. Native Chat display/adoption remains unverified while locked.'}
    save(path.parent/'coordinator-review.json',review);save(ROOT/'verification/easy-world-update-review.json',review)
    s=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(s/'boot-slice-validation.json');assert validation['portable_C_component_count']==22
    validation.update(latest_aggregate_update=now,world_update_CPU_caller=checks)
    validation['component_count_scope']='21 CPU components and one GPU component. Complete1A188 caller now subsumes the previously counted selection block, so count remains22. Caller helper boundaries scripted; this is not full-game integration.'
    save(s/'boot-slice-validation.json',validation)
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['contextLength']==32768 and models[0]['status']=='idle'
    game=('The complete956byte CPU update caller1A188..1A544 is translated to C and matches1,024 original-CPU fixtures with20 host guards; all239 caller instructions executed across those fixtures. '
          'Memory read/write order, helper arguments/order, signed clock clamp,14bit fractional movement,16/32bit position wrap, boundary branching and helper-result restore/retain rules match. '
          'Nine dependency targets are scripted RTS stubs in this test; actual digit helper executes. Ten extra caller examples and four selection examples freeze answers for model evaluation. '
          'Existing inventory C input/render integration still passes600 steps and earlier330 panel comparisons. Component count remains22 because the broader caller subsumes the earlier selection block. '
          'GPU movement, collision/terrain helpers, scene/entity updates, full main-loop integration, audio, complete game and physical hardware validation remain unfinished.')
    frontend=('Installed world_update evidence topic and Game Assistant routing. Three ordinary local questions each made one evidence call and answered correctly in4.9–7.9seconds. '
              'Native LM Studio Chat adoption remains unverified while locked; API exchanges are logged outside native history. Bounded inventory PNG/action tool remains installed.')
    quality=('Small new source-reading probe: both27B everyday base and30B coding model answered0of4 frozen questions exactly; all eight responses retained. These are narrow fresh-context samples, not a general ranking. '
             'Local Analyst/Reviewer also both misread the negative signed clamp; coordinator rejected that field against original execution. No default promotion, accepted model code or weight training this turn.')
    pending=('Implement/connect the update caller dependencies, especially GPU movement and collision helpers, then compare real scene state. Continue source-grounded model evaluation and verify native Chat when accessible. '
             'Advertising Source Pilot v1 remains loadable/experimental; everyday base default. Future256GB hardware unbenchmarked. Full goal active incomplete.')
    evidence=['verification/biwn-world-update-checks.json','verification/world-update-contract-examples.json','verification/biwn-world-update-local-review.json','verification/world-update-model-comparison-review.json','verification/world-update-MCP-check.json','verification/easy-world-update-review.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        p=ROOT/'verification'/name;d=read(p)
        if name=='setup-status.json':d.update(updated_at_utc=now,game_work=game,frontend=frontend,pending=pending,latest_world_model_quality=quality)
        elif name=='current-runtime-state.json':d.update(recorded_at=now,models=models,model_state_refreshed_at=now,decomp_progress=game,visible_chat=frontend,MCP_updated_evidence=frontend,
            local_inference_jobs='Two local review roles, eight source-reading responses and three evidence-assisted chat requests terminal. Usual27B restored and idle. No background training/inference claimed.',
            emulator_jobs='Unicorn caller1024cases/20guards and14contract examples terminal. Three early Unicorn crashes retained; explicit initialSR0x2000 fixed the harness. No whole-game replay or pinned emulator core changes.',latest_API_ease_review=str(ROOT/evidence[-1]),latest_source_probe=str(ROOT/evidence[3]))
        elif name=='everyday-inference.json':d.update(updated_at=now,model=models,model_state_refreshed_at=now,frontend=frontend,latest_API_ease_review=str(ROOT/evidence[-1]),latest_local_game_roles=str(ROOT/evidence[2]),latest_source_probe=str(ROOT/evidence[3]))
        else:
            d.update(recorded_at_utc=now,previous_goal_turn_classification=d['this_goal_turn_classification'],this_goal_turn_classification='progress: completeCPU caller C matches1024cases/239instructions/20guards;14original-derived contract examples;two-model source probe rejects eight answers;three ordinary evidence-assisted questions pass',next_safe_work=pending)
            for item in d['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=game;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend'in item['requirement']:item['state']=frontend;item['evidence']=list(dict.fromkeys(item['evidence']+evidence[-2:]))
                elif 'Multiagent game'in item['requirement']:item['state']+=' Latest correlated role drafts both misread signed clamp; rejected. New two-model four-question source probe scored0of4each; no model code promoted.';item['evidence']=list(dict.fromkeys(item['evidence']+evidence[2:4]))
            d['post_review_evidence'].update({Path(e).name:str(ROOT/e)for e in evidence})
        save(p,d)
    config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+' '+frontend;config['models']['game']['latest_source_probe']=quality;save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game,latest_world_update_check=str(ROOT/evidence[0]));save(ROOT/'corpus/game/project-intake.json',intake)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+game+'\n\nMAIN CPU CALLER SOURCE\n'+str(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.c')+'\nCHECKS\n'+str(ROOT/evidence[0])+'\n\nMODEL QUALITY\n'+quality+'\n'+str(ROOT/evidence[3])+'\n\nEASY CHAT\n'+frontend+'\n\nLATEST APPROXIMATE CPU EXPORT\n18,306 decoded CPU instructions and206 entry candidates. Automatic C remains approximate. World/primary/secondary/axis names are analyst labels, not recovered original symbols.\n\n'+pending+'\n')
    p=ROOT/'START HERE.txt';text=p.read_text();start=text.index('CURRENT GAME RESULT\n');end=text.index('\nTRY IN ADVERTISING ASSISTANT',start)
    text=text[:start]+'CURRENT GAME RESULT\n'+game+'\n\n'+frontend+'\n'+text[end:]
    text=text.replace('TRY IN GAME ASSISTANT\n','TRY IN GAME ASSISTANT\nIn the reconstructed CPU update caller, does a clock difference of minus one get clamped to30?\nIs movement fully rebuilt now, or are helper implementations still missing?\n')
    text+='\nSOURCE-READING QUALITY — '+now+'\n'+quality+'\n';p.write_text(text)
    p=ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt';p.write_text(p.read_text()+'\nCOMPLETE CPU UPDATE CALLER — '+now+'\n'+game+'\nSource:biwn_world_update.c/.h; depends on biwn_inventory_select.c. Reproduce: .venv/bin/python scripts/check_biwn_world_update.py. Caller and digit-helper bytes untouched; RTS stubs at nine dependency targets. Private stack/caller-saved CCR excluded. Analyst position/view labels are hypotheses. Host limits/errors preserve prior effects.\n')
    p=ROOT/'POST REVIEW.txt';p.write_text(p.read_text()+'\nCOMPLETE CPU UPDATE CALLER AND LOCAL MODEL QUALITY — '+now+'\n'+game+'\nWHO DID WHAT: Codex decoded all956callerbytes/239instructions, wrote the high-level C caller with explicit bus/call dependencies, preserved rereads, signed comparisons, stored widths and ordering, and compared originalCPUcaller/actual digit helper against C. Nine other helpers use identical scripted boundary effects and RTS return stubs. Initial32case preflight and final1024case/20guard run pass; all239callerinstructions covered. Three early runs aborted inside Unicorn helper_flush_flags at initialBTST; diagnostic PC log and macOS crash report retained. Explicitly initializingSR0x2000 fixed the harness; no caller bytes or emulator core changed. C passed without source repair.\nOriginalCPU10callerexamples plus4selectionexamples froze model answers before comparison. Local27BAnalyst9.76seconds/Reviewer8.53seconds both wrongly clamped-1to30; other six typed fields matched. Reject negativeclamp and overbroad not-original-execution wording: caller/digit instructions execute, dependencies are scripted.\nRole prompts/responses:\n'+str(Path(roles['directory'])/'prompts-and-responses.txt')+'\n'+quality+'\nTwo-model probe prompts/responses:\n'+str(Path(probe['directory'])/'prompts-and-responses.txt')+'\nOnly one model loaded at a time,32kcontext/oneworker; uniformrequesttemp0.2/top_p0.9/top_k40/repeatpenalty1. No expected answers in inference requests. Everyday model restored afterward. Advertisingsourceanswers6.0–7.1seconds, coder0.9–1.2seconds; both0of4exact. All failures are semantic, not JSON parse failures. No general ranking inferred.\nThree normal questions selectedworld_update evidence once each and answered negativeclamp, remaininghelpers andcollisionresult2 correctly under requested lengths. SDK uses workbenchtool code; freshinstalledMCP evidence checked separately. NativeChat remainedlocked on freshUIcheck; no unlock requested.\nPlain question prompts/responses:\n'+str(path.parent/'prompts-and-responses.txt')+'\nCoordinator audit:\n'+str(ROOT/evidence[-1])+'\n'+pending+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
    save(ROOT/'verification/world-update-checkpoint.json',{'recorded_at':now,'backup':read(ROOT/'verification/world-update-checkpoint-backup.json')['directory'],'components':22,'CPU_caller_cases':1024,'caller_instruction_coverage':[239,239],'host_guards':20,'extra_original_contract_examples':14,'source_probe_passes':probe['passes'],'plain_chat_questions_passed':3,'known_compute_jobs':'terminal','models':models,'full_goal_status':'active incomplete','evidence':evidence,'native_Chat_adoption':'unverified while locked','next_work':pending})
    print(json.dumps({'caller_cases':1024,'caller_instructions':239,'components':22,'source_probe':probe['passes'],'plain_chat_questions':3,'installed':True}))

if __name__=='__main__':main()

"""Finalize dispatcher proofs and exact reviewed local-chat exchanges."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();checkpoint=read(ROOT/'verification/disc-dispatch-checkpoint.json');linked=read(ROOT/'verification/biwn-disc-world-dispatch-checks.json');mcp=read(ROOT/'verification/disc-dispatch-MCP-check.json');assert mcp['status']=='fresh_installed_dispatcher_static_yield_and_disc_scope_passed'
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name in ['biwn-input-dispatch-cpu-checks.json','biwn-input-dispatch-yield-checks.json','biwn-disc-world-dispatch-checks.json']:
        proof=read(ROOT/'verification'/name);assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
    protocol_path=ROOT/'verification/easy-disc-dispatch/20261013T202555.417724Z/protocol.json';protocol=read(protocol_path);assert protocol['status']=='completed_pending_coordinator_review';reviewed=samples(protocol)
    assert len(reviewed)==2 and all(s['word_count']<160 and len(s['tool_calls'])==1 for s in reviewed)
    reviewed[0].update(verdict='bounded_current_scope_correct',reason='Actual no-button dispatcher code distinguished from standaloneCPU and syntheticyield proofs; three unreachedtop scripts/15unsupportednestedservices/world-stackyield/render/fullgame limits correct.')
    reviewed[1].update(verdict='bounded_same_model_role_review_correct',reason='1890CPUcases/816instructions/19scriptedhelpers and25yieldcases/75suspensions/225handoffs/18scriptedhelpers copied correctly. No discworldinner-yieldclaim;15unsupportedservices explicit. Sameweights roles not independent.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768
    audit=ROOT/'verification/disc-dispatch-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True);shutil.copy2(protocol_path,audit/'SDK-protocol.json')
    who=('Codex authored the source-specific static C generator, fullCPU dispatcher interface and comparison/suspension/integration tests. Original native CPU and independent Unicorn observer decide CPU acceptance; actual scheduler/idles compare separately. '
         'The generated C has no runtime instruction decode or original CPU calls. It is static recompilation, not recovered original source; the readable logical C remains. '
         'The local27Bbase answered one ordinary prompt and one Analyst/Reviewer prompt via LM Studio SDK, each with one evidence call. Both answers are correct within current evidence; two samples do not prove general reliability. Roles share weights and are not independent verification. '
         'No local-model-authored code, training, model switch or default promotion. Everyday base stays32k/oneworker/idle. Native Chat/provider adoption remains unverified after prior tooltimeout; no conversation injection or unlock request.')
    corrections=['Generated all816dispatcher instructionblocks from pinned stage/workmap, retaining exact partial/fullregister writes, arithmetic flags, rawjumptable/addressing, save/argument/JSRframes and internalPCcontinuations. All1890cases/38guards passed against twoCPUoracles.',
                 'First yieldrun all25chosenexistingfixtures matchedCPU/RAM/handoffs, but harness incorrectly required32. There are16eligiblefixtures for firstsite and9forsecond. Correctedcountto25; final75inner suspensions/225handoffs cover both sites. No generatedCbehavior change.',
                 'No-button discscene now runs actualdispatcher512times across16cases; complete CPU/RAM/privateframes and2576handoffs match. Three top-levelscriptsconfigured,zero reached. Fifteen nestedservicebodies explicitlyunsupported; no nestedservices orinner yields reached, so worldcaller suspensionunverified.',
                 'Synthetic3context yield proof uses18other scripts includingmutableanimation/poll/resourceeffects. It does not prove actualscene animationcompletion, loading task switches, worldstackyieldcontinuation, targetacquisition, render/scanout or completegame.',
                 'Ordinarylocalanswer usedstatus evidence in11.58SDKseconds; rolereview usedlargerscheduler evidence in30.11SDKseconds. Differentpayloads/lengths/cache meanthisisnotgeneral speedbenchmark. Exactevents retained; nativeChatgeneration unverified.']
    review={'recorded_at':now,'status':'dispatcher_code_and_two_bounded_local_answers_passed_world_yields_unverified','who_did_what':who,'samples':reviewed,'corrections':corrections,'native_new_response_verified':False,'disc_world_dispatcher_yields_verified':False,'general_model_reliability_proved':False,'new_training':False,'default_promoted':False,'model_idle':True,'directory':str(audit),'payload_bytes_by_topic':mcp['payload_bytes_by_topic']}
    save(audit/'review.json',review);save(ROOT/'verification/disc-dispatch-review.json',review)
    transcript='STATIC DISPATCHER / SEPARATE REAL YIELDS / NO-BUTTON SCENE\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(corrections)+'\n\nEXACT SYSTEM / USER / TOOLS / RESPONSES\n'+json.dumps(protocol,ensure_ascii=False,indent=2)+'\n\nCOORDINATOR VERDICTS\n'+json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n\nCURRENT CODE SCOPE\n'+read(ROOT/'config.json')['disc_world_actor_progress']+'\nFull goal active and incomplete.\n';(audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now,status=review['status'],local_answers_bounded_correct=2,SDK_reported_seconds=[s['SDK_reported_seconds']for s in reviewed],known_compute_jobs='terminal',model_idle=True,new_training=False,default_promoted=False,native_new_response_verified=False,review=str(ROOT/'verification/disc-dispatch-review.json'),transcript=str(audit/'prompts-and-responses.txt'))
    checkpoint['evidence']+=['verification/disc-dispatch-MCP-check.json','verification/disc-dispatch-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))];save(ROOT/'verification/disc-dispatch-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(disc_dispatch_checkpoint=checkpoint,disc_dispatch_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: two bounded dispatcher/yield scope answers correct. Native Chat/provider unverified; everydaybaseidle.',latest_API_ease_review=str(ROOT/'verification/disc-dispatch-review.json'))
        if name=='requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+checkpoint['evidence']))
        save(path,value)
    note='\nDISPATCHER LOCAL INFERENCE REVIEW — '+now+'\n\n'+who+'\n\nRESULT\nBoth boundedanswers correctly distinguish staticCPUproof, separate syntheticrealyieldring and no-buttondiscscene. SDKreportedseconds: '+', '.join(str(round(s['SDK_reported_seconds'],2))for s in reviewed)+'. No general reliability/speedclaim.\n\nEXACT PROMPTS / TOOLS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','CURRENT DECOMPILATION.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    text=text[:a]+('LOCAL INFERENCE RESULT\nTwo SDK fallback answers correctly explain current dispatcher limits, one evidence call each, about12/30SDKseconds. The no-button discscene reaches no helperscripts, but three remain configured,15nestedservices remain unsupported and realworldcaller dispatcher yields are unverified. Separate syntheticring yield proof retains18scriptedhelpers. Native Chat/provider adoption remains unverified; exact SDK logs are separate. No new training/default promotion; everydaybaseidle.\n\nTry: Have we finished the input controls, and are all scripts gone now? Can I play the game?\n\nExact prompts, tools, answers and reviews:\n'+str(audit/'prompts-and-responses.txt')+'\n\n')+text[b:];path.write_text(text)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
    print(json.dumps({'components':106,'dispatcher_CPU_cases':1890,'instructions':816,'yield_cases':25,'inner_yields':75,'yield_handoffs':225,'disc_cases':16,'world_scripts_configured':3,'world_scripts_reached':0,'unsupported_nested_services':15,'local_answers_bounded_correct':2,'native_verified':False,'model_idle':True,'audit':str(audit)}))
if __name__=='__main__':main()

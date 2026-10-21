"""Save long original-game exploration, export and ease-of-inference checkpoint."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc).isoformat()
    backup=read(ROOT/'verification/long-exploration-checkpoint-backup.json')['directory']
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    review=read(ROOT/'verification/biwn-long-audio-review.json');local=read(ROOT/'verification/biwn-long-audio-local-review.json')
    assert review['static_expansion']['instructions_total']==18306 and review['checked_portable_C_components']==14
    for role in local['roles']:
        obj=json.loads(role['text'])
        assert (obj['frames_each_long_run'],obj['framebuffer_difference_frames'],obj['stream_changes'],obj['new_nonzero_audio'],obj['new_static_instruction_starts'],obj['checked_C_components'])==(9000,8224,0,False,81,14)
        assert role['word_count']<160
    local.update(recorded_at=now,status='coordinator_reviewed_bounded_summary_pass_correlated_copy',
                 review=['Both structured summaries preserve supplied observed counts and scoped limits.',
                         'Reviewer exactly copies analyst, including empty errors. No independent review or general quality/autonomy proof.',
                         'Codex coordinator wrote streaming observer, verified baseline/hashes, ran Ghidra extension/data reclassification and checked artifacts. Local roles summarized supplied evidence.'],
                 source_review=str(ROOT/'verification/biwn-long-audio-review.json'))
    save(ROOT/'verification/biwn-long-audio-local-review.json',local);save(Path(local['directory'])/'coordinator-review.json',local)
    easy_pointer=read(ROOT/'verification/easy-long-exploration-current.json');easy_dir=Path(easy_pointer['directory']);easy=read(easy_dir/'protocol.json')
    assert easy['status']=='completed_pending_coordinator_review' and easy['rounds']==2
    calls=[c['toolCallRequest']for e in easy['events']for c in e['content']if c['type']=='toolCallRequest']
    answer='\n'.join(c['text']for e in easy['events']if e['role']=='assistant'for c in e['content']if c['type']=='text'and c['text'])
    assert len(calls)==1 and calls[0]['name']=='project_evidence' and len(answer.split())<90
    assert '81' in answer and '14' in answer and 'no complete reconstructed game' in answer
    ease={'recorded_at':now,'status':'coordinator_reviewed_ordinary_question_bounded_pass','directory':str(easy_dir),
          'system':easy['system'],'prompt':easy['user'],'answer':answer,'words':len(answer.split()),'tool_calls':calls,
          'SDK_reported_seconds':easy['seconds'],'rounds':easy['rounds'],
          'review':'Accurately distinguishes81new static starts, zero observed game audio,14isolated checked components and unfinished full reconstruction.',
          'scope':'One fresh ordinary question through localhost SDK using saved Game Assistant system prompt. API max2prediction-round guard; not a native Chat message, native latency benchmark or general autonomy proof.'}
    save(ROOT/'verification/easy-long-exploration-review.json',ease);save(easy_dir/'coordinator-review.json',ease)
    game=('Original-game assisted-BIOS exploration extended to two9000frame runs after exact900frame streaming-observer preflight. Supplied inputs change8224framebuffer samples,5470CPU-PC samples and8131GPU-PC samples; DSP-PC, watched command state and audio totals do not differ. Both long runs have zero new nonsilent pairs, zero nonzero output-ring samples and no watched game-phase mailbox/stream writes in frames622..9000. Scene/inventory changes visually confirmed; not proof every button acted or sound assets are absent. Streaming trace consumed~26million events per long run with zero unreadable records.')
    decomp=('Latest separate Ghidra project adds81stable sampled originalCPU instruction starts:18306decoded instructions,206entry candidates, no new function entries. Three starts in14bytes formerly classified as data were reviewed/reclassified; existing instruction rows and prior projects unchanged. All matching stable long-run sampledPCs now present; incomplete execution coverage and approximateC remain. Fourteen isolated portableC components checked; no complete reconstructed build or hardware validation.')
    next_work='Inspect newly observed UI/game-state paths and stream references; reconstruct further original routines against CPU/DSP fixtures. Broaden advertising evidence/semantic evaluation before promoting another trained model. Full goal active and incomplete.'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
    assert len(models)==1 and models[0]['modelKey']=='local/advertising-qwen38' and models[0]['status']=='idle'
    evidence=['verification/biwn-long-audio-review.json','verification/biwn-long-audio-local-review.json','verification/easy-long-exploration-review.json',str(session/'long-observed-disassembly-summary.json'),str(session/'long-observed-data-repair-summary.json')]
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path)
        if name=='setup-status.json':value.update(updated_at_utc=now,game_work=game+' '+decomp,pending=next_work)
        elif name=='current-runtime-state.json':
            value.update(recorded_at=now,models=models,model_state_refreshed_at=now,decomp_progress=game+' '+decomp,
                         local_inference_jobs='All known jobs terminal: two local long-run summaries and ordinary-question API test completed; no background training/inference job claimed.',
                         emulator_jobs='900frame streaming preflight and two9000frame original-game runs completed normally; core/CDI/BIOS unchanged.',
                         ghidra_jobs='Three logged headless jobs terminal;81new stable instruction starts and three data conflicts resolved. ApproximateC remains unverified as whole game.',
                         MCP_updated_evidence='Fourteen checkedCcomponents, extended9000frame exploration and latest18306instruction export refreshed.')
        elif name=='everyday-inference.json':value.update(updated_at=now,model=models,model_state_refreshed_at=now,latest_API_ease_review=str(ROOT/evidence[2]),latest_game_exploration_review=str(ROOT/evidence[0]))
        else:
            value.update(recorded_at_utc=now,previous_goal_turn_classification=value['this_goal_turn_classification'],
                         this_goal_turn_classification='progress: exact streaming preflight, two9000frame game runs,81stable CPU boundaries added/data conflicts resolved, two local scope reviews and ordinary-question tool test',next_safe_work=next_work)
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:item['state']=game+' '+decomp;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend' in item['requirement']:item['state']+=' One saved-preset ordinary progress question through localhost SDK completed in16.84seconds with one evidence call and correct'+str(len(answer.split()))+'word answer; not nativeUI timing.';item['evidence']=list(dict.fromkeys(item['evidence']+[evidence[2]]))
                elif 'Multiagent game' in item['requirement']:item['state']+=' Latest long-run analyst/reviewer give accurate bounded53word JSON summaries; reviewer verbatim copy, no independent verification.';item['evidence']=list(dict.fromkeys(item['evidence']+[evidence[1]]))
            value['post_review_evidence'].update({Path(e).name:str(ROOT/e)if not Path(e).is_absolute()else e for e in evidence})
        save(path,value)
    config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+' '+decomp;save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game+' '+decomp,latest_long_exploration_review=str(ROOT/evidence[0]),latest_static_export=review['static_expansion']);save(ROOT/'corpus/game/project-intake.json',intake)
    source=Path(review['static_expansion']['final_export'])
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT DECOMPILATION\n\nApproximate full CPU export, NOT a complete working reconstructed game:\n'+str(source/'decompiled.c')+'\n\nAssembly listing:\n'+str(source/'listing.asm')+'\n\nChecked isolated portableC components (14):\n'+str(ROOT/'projects/black-ice-white-noise/restoration')+'\n\n'+decomp+'\n\nLong original-game emulator test/captures:\n'+review['directory']+'\n\n'+game+'\n\nExact roles/prompts/answers and limitations: POST REVIEW.txt. Everyday interface: LM Studio → Game Assistant — Quick Start.\n')
    path=ROOT/'START HERE.txt';path.write_text(path.read_text()+'\nLATEST EXTENDED ORIGINAL-GAME TEST — '+now+'\n'+game+'\n'+decomp+'\nLatest files are linked in CURRENT DECOMPILATION.txt. One ordinary localAPI question using saved Game Assistant prompt returned a correct'+str(len(answer.split()))+'word answer with one tool call in'+str(round(easy['seconds'],2))+'SDK-reported seconds; this is not nativeUI timing.\n')
    path=ROOT/'POST REVIEW.txt';path.write_text(path.read_text()+'\nLONG ORIGINAL-GAME EXPLORATION / DECOMPILER EXPANSION — '+now+'\n'+game+'\n'+decomp+'\nWHO DID WHAT: Codex wrote a separate streaming observer, verified all900baseline frame/command/DSP/watch records exactly, ran9000frame baseline/input scripts, inspected captures and validated unchanged inputs/core. Codex imported stable matchingCPU starts into copied Ghidra projects, preserved earlier volatile annotations, reviewed three data conflicts and reclassified only14bytes. Actual local analyst→reviewer returned accurate bounded JSON; reviewer copied analyst exactly. Codex reviewed the counts/scope and tested one normal progress question with saved Game Assistant prompt and automatic tools. No Codex subagents, no independent verification, no new weights or core changes.\nExact local roles/prompts/responses: '+str(Path(local['directory'])/'prompts-and-responses.txt')+'\nExact ordinary question/system/tool/result/answer: '+str(easy_dir/'prompts-and-responses.txt')+'\nOrdinary answer ('+str(len(answer.split()))+'words, '+str(round(easy['seconds'],2))+'SDK-reported seconds): '+answer+'\nSource exploration/captures: '+review['directory']+'\nFinal approximate export: '+str(source)+'\nLatest files: '+str(ROOT/'CURRENT DECOMPILATION.txt')+'\n'+next_work+'\nAll known jobs terminal at this checkpoint; usual27B idle32k/oneworker. Locked-screen API outputs are separate from native Chat messages.\n')
    save(ROOT/'verification/long-exploration-checkpoint.json',{'recorded_at':now,'backup':backup,'models':models,'full_goal_status':'active incomplete','known_compute_jobs':'terminal','evidence':evidence,'static_export':review['static_expansion'],'ordinary_question':ease,'next_work':next_work})
    print(json.dumps({'recorded_at':now,'instructions':18306,'checked_C_components':14,'ordinary_question_words':len(answer.split()),'ordinary_question_seconds':easy['seconds'],'model_status':models[0]['status']}))


if __name__=='__main__':main()

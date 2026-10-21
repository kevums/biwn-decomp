"""Bind actual native Chat trials, source review and current delivery receipts."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
RUNS=Path.home()/'.lmstudio/local-ai-lab/runs/native-chat-teams'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    out=V/'visible-five-caller-Chat-review-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    results=[]
    for index,name in enumerate(['2026-10-20T09-14-02.253Z-3e2d8793-9a10-4d61-a9e9-a8bfc140fa8e','2026-10-20T09-21-29.550Z-458af7d9-6a1b-430b-aefe-3e72be4b530a']):
        folder=RUNS/name;session=read(folder/'session.json')
        assert session['status']=='terminal_research_team_generation_complete_semantic_review_required'
        assert len(session['roles'])==3 and all(x['status']=='terminal'for x in session['roles'])
        assert session['same_local_weights'] and not session['independent_verification']
        target=out/('trial-'+str(index+1));target.mkdir();shutil.copyfile(folder/'session.json',target/'session-as-generated.json')
        text=['ACTUAL LM STUDIO NATIVE CHAT TEAM','Source: '+str(folder),'Same local27Bweights; sequential roles, not independent verification.','']
        files=[folder/'session.json'];words=[]
        for i,role in enumerate(['Analyst','Restorer','Reviewer'],1):
            prompt=folder/f'{i}-{role}-prompt.txt';response=folder/f'{i}-{role}-response.txt'
            text.extend(['EXACT '+role+' PROMPT',prompt.read_text(),'RAW '+role+' RESPONSE',response.read_text(),''])
            words.append(len(response.read_text().split()));files.extend([prompt,response])
        (target/'prompts-and-responses.txt').write_text('\n'.join(text)+'\n')
        final=(folder/'3-Reviewer-response.txt').read_text()
        if index==0:
            assert words==[129,49,129]
            verdict='terminal_native_Chat_current_disc_facts_received_word_limit_failed'
            review='Current five-caller disc and then-older three-caller GUI were correctly distinguished at generation time. Analyst and Reviewer exceeded110words and reused hosted-pipeline counts; not adopted as the concise current answer. GUI was promoted after this request began.'
        else:
            assert words==[82,34,75]
            assert all(x in final for x in ['current five-caller native disc','checkpoint restored','19 video frames differed','11E6C','13 vs 16','No new training'])
            assert session['evidence']['evidence']['separate_test_preview']['uses_current_five_caller_disc']
            verdict='terminal_native_Chat_five_caller_GUI_status_source_and_length_review_pass'
            review='Final75-word raw answer accepted for this current-status question without editing. It preserves the current checkpoint GUI, fresh trial scope, differing video, remaining outer task, fidelity/full-source limits and changed restoration. This single checked answer does not establish general model reliability.'
        proof=dict(status=verdict,directory=str(target),source_directory=str(folder),new_predictions=3,words_by_role=words,
                   native_UI_verified=True,UI_observation='CUA observed the actual LM Studio Chat role prompts and completed replies. Current trial final answer appeared in AX text elements1984and1985 after Scroll to bottom; raw response matches the observed wording.',
                   same_local_weights=True,independent_verification=False,new_training=False,coordinator_review=review,
                   model=session['modelInfo'],role_metrics=[{k:x[k]for k in ['role','input_tokens','stats']}for x in session['roles']],
                   source_sha256={str(p):sha(p)for p in files},whole_goal_complete=False)
        save(target/'review.json',proof);save(V/f'visible-five-caller-Chat-trial-{index+1}-current.json',proof);results.append(proof)
    accepted=results[1]
    save(V/'visible-five-caller-Chat-reviewed-current.json',accepted)
    report=ROOT/'reports/Five Caller GUI and Local Inference Review.txt'
    report.write_text('FIVE-CALLER GUI AND LOCAL INFERENCE\n\nThe existing Desktop BIWN Test Preview app now uses the reviewed five-caller disc at its saved street checkpoint. '
        'The actual487-frame GUI check observed launch, start, movement, pause and close; all five native callers returned and memory guards passed. '
        'Expected Deck appearance was not confirmed, and run-chord, revision-specific fidelity and audible audio remain unverified. '
        'A separate2400-frame headless replay matched full CPU, RAM, video, GPU, DSP and final serialized state with and without counters.\n\n'
        'LM Studio Chat ran two visible three-role trials on the same locally loaded27Bmodel. Analyst analyzes current evidence; Restorer selects the next source step; Reviewer checks the answer. '
        'They share weights and are not independent verification. The first final answer used129words against a110-word limit. '
        'After selecting compact current evidence, the second final answer used75words against a90-word limit and passed source review. '
        'Input tokens per role changed from18341–18444 to5465–5735; first-token times changed from22.663–23.077seconds to4.068–4.610seconds. '
        'Questions, evidence and cache conditions differed, so these are observed timings, not a controlled speed comparison.\n\n'
        'The one-click current Reader is a separate local stream. V18failed length/instruction echo andV19overgeneralized return correctness and cycle wording. '
        'V20returned77words in6.63seconds and passed source review. Its prompt strongly constrains the current status; this is not evidence of general instruction following. '
        'All raw failures and exact prompts are preserved. No optimizer update or new game algorithm was produced in these frontend checks.\n\n'
        'Current exact native Chat prompts/responses: '+str(Path(accepted['directory'])/'prompts-and-responses.txt')+'\n'
        'Current one-click Reader: '+str(Path(read(V/'Deck-status-live-v20-current.json')['directory'])/'prompts-and-responses.txt')+'\n\n'
        'Next game source step: integrate outer Deck task0x11E6C while preserving the five native callers and suspended contexts. '
        'The whole-game rebuild and visual/timing/audio/physical fidelity remain unfinished. AdvertisingV12remains rejected; the base model is retained pending broader accepted research/education validation.\n')
    sources=ROOT/'config/current-model-work-sources.json';items=read(sources);shutil.copyfile(sources,out/'source-list-before-native-trials.json')
    for item in [['visible-five-caller-Chat-trial-1-current.json','Actual native Chat: current disc received, concise answer failed'],['visible-five-caller-Chat-trial-2-current.json','Actual native Chat: current five-caller GUI and75-word final answer reviewed']]:
        assert not any(x[0]==item[0]for x in items);items.insert(0,item)
    save(sources,items)
    pointer=V/'native-Deck-current-status-v1-current.json';pub=read(pointer);shutil.copyfile(pointer,out/'status-publication-before-Chat.json')
    packet=read(pub['packet']);packet.update(native_Chat_verified=True,native_Chat_scope='One actual visible current disc/GUI status question:3sequentialsame-weightroles;75-wordfinal answer source reviewed. No general reliability or model-training acceptance claim.',native_Chat_review=str(V/'visible-five-caller-Chat-reviewed-current.json'))
    save(out/'current-status.json',packet);pub['packet']=str(out/'current-status.json');pub['dependencies_sha256'].update({str(out/'current-status.json'):sha(out/'current-status.json'),str(Path(accepted['directory'])/'review.json'):sha(Path(accepted['directory'])/'review.json')});save(pointer,pub)
    goal_path=V/'goal-continuation-current.json';goal=read(goal_path);shutil.copyfile(goal_path,out/'goal-before-Chat.json')
    goal.update(current_turn_predictions=9,saved_native_Chat_trial_pending_review=False,latest_native_Chat_review=str(V/'visible-five-caller-Chat-reviewed-current.json'),
                ongoing_finite_workers=[],reserved_arena_data_bytes=129536,non_code_reservation_bytes=129712,alignment_padding_bytes=176)
    goal['current_turn_classification']+=' Actual native Chat source and length review passed for the second trial; compact selected evidence reduced input tokens.'
    goal['remaining_requirements']['local_frontend']='Current five-caller GUI launch/movement/pause/close and native returns reviewed. Latest visible native Chat answer passes source/length review. Expected Deck appearance, run chord, broad model reliability, audio/visual fidelity and current portable migration remain incomplete.'
    save(goal_path,goal)
    # Refresh mutable current frontend hashes after the final source-list and
    # status publication changes; preserve the preceding receipt as an archive.
    delivery_path=V/'five-caller-frontend-delivery-v1-current.json';delivery=read(delivery_path);shutil.copyfile(delivery_path,out/'delivery-before-Chat.json')
    delivery['source_sha256'].update({name:sha(name)for name in delivery['source_sha256']})
    delivery['source_sha256'].update({str(V/'visible-five-caller-Chat-reviewed-current.json'):sha(V/'visible-five-caller-Chat-reviewed-current.json'),str(report):sha(report)})
    delivery.update(native_Chat_current_GUI_trial_pending_review=False,native_Chat_current_GUI_reviewed=True,new_predictions_this_goal_continuation=9,native_Chat_report=str(report))
    save(delivery_path,delivery);save(out/'delivery-final.json',delivery)
    print(json.dumps(dict(directory=str(out),native_Chat_final_words=75,Reader_words=77,new_predictions=9,optimizer_updates=0),indent=2))


if __name__=='__main__':main()

"""Publish actual native Chat and one-click Reader trials, retaining rejected drafts."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];V=R/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    chat=read(V/'visible-six-caller-Chat-reviewed-current.json');out=Path(chat['directory'])
    s=read(V/'Deck-status-live-v22-current.json')
    s.update(status='terminal_raw_Reader_rejected_scope_wording',accepted=False,coordinator_review='Says deeper original helpers missing although they still execute from disc; readable/native recovery is unfinished. Outer bridge coordinates is ambiguous. No promotion.')
    save(V/'Deck-status-live-v22-reviewed-current.json',s)
    accepted=[]
    for tag,p in [('first',R/'runs/Deck-status-live-20261020T152838.866100Z/protocol.json'),('launcher',V/'Deck-status-live-v23-current.json')]:
        s=read(p);folder=Path(s['directory']);answer=read(folder/'response.txt')
        assert set(answer)=={'completed','limits'}and all(len(v.split())<=35 for v in answer.values())
        assert s['new_predictions']==1 and s['format_pass']
        for name,h in s['source_sha256'].items():assert sha(name)==h,name
        assert 'Six-caller' in answer['completed']and 'Shift+Up' in answer['completed']and 'incomplete' in answer['limits']
        s.update(status='terminal_current_six_caller_Reader_source_review_pass',accepted=True,answer=answer,words=len(' '.join(answer.values()).split()),actual_launcher_executed=(tag=='launcher'),
                 coordinator_review='Raw concise strings correctly describe installed subsystem/checkpoint GUI and tested key mapping; explicitly retain incomplete whole-game rebuilding and fidelity. Deterministic prelude supplies fresh/control scope and Deck appearance caveat. No general quality/completion claim.')
        save(V/('Deck-status-live-v23-reviewed-current.json'if tag=='launcher'else'Deck-status-live-v23-first-reviewed-current.json'),s)
        save(out/(tag+'-Reader-review.json'),s);accepted.append(s)
    sp=V/'native-Deck-current-status-v1-current.json';state=read(sp);pp=Path(state['packet']);packet=read(pp)
    shutil.copyfile(sp,out/'publication-before-Chat-review.json');shutil.copyfile(pp,out/'packet-before-Chat-review.json')
    packet.update(native_Chat_verified=True,native_Chat_review=str(V/'visible-six-caller-Chat-reviewed-current.json'),
                  native_Chat_scope='One actual visible six-caller preview question;3sequentialroles on same base weights,89word final reviewed. Initial8Kcontext rejection made zero predictions;32Kserial retry completed. Reviewer copies Analyst content; not independent verification or broad training acceptance.')
    save(pp,packet);state['dependencies_sha256'][str(pp)]=sha(pp)
    state['dependencies_sha256'][str(V/'visible-six-caller-Chat-reviewed-current.json')]=sha(V/'visible-six-caller-Chat-reviewed-current.json');save(sp,state)
    report=R/'reports/Six Caller GUI and Local Inference Review.txt'
    report.write_text('BIWN — GUI AND LOCAL INFERENCE DELIVERY\n\n'
        'Desktop BIWN Test Preview.app uses six-caller runtime v4. Double-click, click game window, press P. Hold C+Up or Shift+Up for run input; arrows move/turn; P pauses; Esc closes. Hold1 about a second, release, then holdD for Deck selection/activation. No LM Studio model is required for the game window.\n\n'
        'Actual GUI sessions:367frames verifies77 C+Up input frames;415frames verifies58 C+Up frames and native returns coordinate50,input50,face2,scan25,geometry24,outer1. All guards,immutable code and invalid-task checks pass. Expected Deck appearance and audible audio remain unverified; speed ratio was not measured.\n\n'
        'Fresh disc evidence:24,965frames per lane, not the earlier five-caller25,007figure. Control restores only the outer entry; inner five stay native in both.40video frames differ; final video matches. Whole-game source rebuilding and fidelity remain incomplete.\n\n'
        'LM Studio Chat: BIWN — Local game team. First attempt had8192context and zero predictions because input+6000output reserve did not fit. Native load settings now32768context,parallel1. Three actual same-weight passes completed:90wordAnalyst,37wordRestorerJSON,89wordReviewer. Final launch/run/source-status answer passed source review. Reviewer repeats Analyst; Restorer reason overstates finite subsystem coverage. No independent review or broad reliability proof. Exact prompts and raw responses preserved.\n\n'
        'One-click Reader:v21rejected at117words;v22rejected for missing-runtime-helper wording/ambiguous authorship. V23returns24words in two strings; direct run2.71sec,actual current-status launcher2.39sec. Both launchers now use six-caller evidence. API inference reuses matching32Kserial instance so native Chat stays selected.\n\n'
        'This continuation ran7actual local predictions (3Chatroles+4Readercalls),zero optimizer updates. AdvertisingV12remains rejected/unpromoted; daily base retained. Whole-game recovery,broad accepted game/Advertising training and current portable migration remain open.\n\n'
        'Exact Chat prompts/responses: '+str(out/'prompts-and-responses.txt')+'\nReader prompts/responses: '+str(Path(accepted[-1]['directory'])/'prompts-and-responses.txt')+'\n')
    ip=R/'config/current-model-work-sources.json';shutil.copyfile(ip,out/'model-work-sources-before-six-frontend.json');items=read(ip)
    new=[['visible-six-caller-Chat-reviewed-current.json','Actual native Chat:six-caller preview launch/run/current status,89word final reviewed;32Kserial context'],['Deck-status-live-v21-reviewed-current.json','Six-caller Reader:117word raw response rejected'],['Deck-status-live-v22-reviewed-current.json','Six-caller Reader:runtime-helper wording rejected'],['Deck-status-live-v23-first-reviewed-current.json','Six-caller Reader:short raw answer source reviewed'],['Deck-status-live-v23-reviewed-current.json','Actual one-click current status:six-caller evidence and short local answer reviewed']]
    for item in reversed(new):
        assert not any(x[0]==item[0]for x in items);items.insert(0,item)
    save(ip,items)
    gp=V/'goal-continuation-current.json';g=read(gp);shutil.copyfile(gp,out/'goal-before-frontend-review.json')
    g.update(recorded_at=datetime.now(timezone.utc).isoformat(),current_turn_predictions=7,current_turn_actual_local_predictions=7,current_turn_optimizer_updates=0,
        current_turn_classification='Progress:actual367/415frame six-caller GUI verifies Shift run mapping and all six returns;currentMCP/nativeChat updated and observed3roles;2Readerfailures retained;v23direct+actuallauncher pass.Seven predictions,zero updates.',
        latest_native_Chat_review=str(V/'visible-six-caller-Chat-reviewed-current.json'),latest_native_Chat_words=89,latest_Reader_words=accepted[-1]['words'],loaded_local_model='local/advertising-qwen38:27B6bit,32768context,parallel1',
        one_click_launcher_version='v23current six-caller brief;actuallauncher executed',native_Deck_context_version='v13',native_chat_current_context='Source-bound six-caller fresh/control+actualGUI evidence;actualvisibleChat reviewed',
        candidate_control_frames=[24965,24965],latest_usability_report=str(report),full_objective_complete=False,blocked=False,ongoing_finite_workers=[])
    save(gp,g)
    receipt=dict(status='terminal_six_caller_GUI_Chat_and_one_click_delivery_reviewed',directory=str(out),report=str(report),actual_local_predictions=7,optimizer_updates=0,
        native_Chat_review=str(V/'visible-six-caller-Chat-reviewed-current.json'),Reader_review=str(V/'Deck-status-live-v23-reviewed-current.json'),fresh_game_review=str(V/'native-Deck-six-reviewed-v1-current.json'),GUI_review=str(V/'native-keyboard-live-v4-reviewed-current.json'),
        same_weight_review_independent=False,full_objective_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),report,R/'native_deck_source_context_v13.py',R/'native_deck_status_evidence_v1.py',R/'scripts/native_chat_team_context.py',R/'scripts/run_deck_status_live_v23.py',R/'scripts/show_native_six_status_v1.py',R/'BIWN Current Status.command',R/'Live Local BIWN Briefing.command',ip]})
    save(out/'delivery.json',receipt);save(V/'six-caller-frontend-delivery-v1-current.json',receipt)
    print(out,'7predictions;whole goal incomplete')

if __name__=='__main__':main()

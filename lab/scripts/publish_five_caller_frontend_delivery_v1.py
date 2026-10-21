"""Publish current GUI/status delivery and preserve all failed local outputs."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    out=V/'five-caller-frontend-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    reader_path=V/'Deck-status-live-v20-current.json';reader=read(reader_path)
    assert reader['status']=='terminal_streamed_local_briefing_pending_source_review' and reader['format_pass']
    for name,expected in reader['source_sha256'].items():assert sha(name)==expected,name
    answer=reader['answer'];count=len(' '.join(answer.values()).split());assert count<=100
    assert all(x in answer['completed']for x in ['Five native Deck callers','18 native geometry returns versus 18 original-control returns','Coordinator','five-caller checkpoint GUI','487'])
    assert all(x in answer['limits']for x in ['0x11E6C','Full-game rebuilding is incomplete','19 video frames differ','Cycle identity is unverified','13-frame','original 16-frame','Deck appearance','audio/physical','training'])
    accepted=dict(reader,status='terminal_v20_constrained_reader_source_review_accepted',words=count,
                  coordinator_review='Raw response accepted without editing. This constrained status prompt and source review do not establish broad instruction-following reliability.',
                  full_MCP_evidence_sha256=sha(Path(reader['directory'])/'full-MCP-evidence.json'))
    save(V/'Deck-status-live-v20-reviewed-current.json',accepted);save(out/'reader-review.json',accepted)
    shutil.copyfile(ROOT/'scripts/run_deck_status_live_v20.py',out/'reader-as-run.py')
    backups=[]
    for name in ['Live Local BIWN Briefing.command','BIWN Current Status.command']:
        p=ROOT/name;shutil.copyfile(p,out/('before-'+name));text=p.read_text();assert 'run_deck_status_live_v17.py'in text
        p.write_text(text.replace('run_deck_status_live_v17.py','run_deck_status_live_v20.py'));backups.append(str(out/('before-'+name)))
    sources=ROOT/'config/current-model-work-sources.json';shutil.copyfile(sources,out/'before-model-work-sources.json');items=read(sources)
    for item in [
        ['Deck-status-live-v18-reviewed-current.json','Current GUI Reader trial: rejected overlength and copied instructions'],
        ['Deck-status-live-v19-reviewed-current.json','Compact Reader trial: rejected generalized correctness and cycle wording'],
        ['Deck-status-live-v20-reviewed-current.json','Current five-caller disc and GUI briefing: accepted constrained raw response']]:
        assert not any(x[0]==item[0]for x in items);items.insert(0,item)
    save(sources,items)
    old_goal=V/'goal-continuation-current.json';shutil.copyfile(old_goal,out/'previous-goal.json');goal=read(old_goal)
    goal.update(status='active_five_caller_fresh_disc_and_current_GUI_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),
                previous_goal_turn_classification='No recovery progress: answered the launch question by checking existing saved launchers. This continuation revalidated those artifacts and took the next available publication and GUI actions.',
                current_turn_classification='Progress:137 saved game-source dependencies revalidated; five-caller status published through actual configured MCP; five-caller Python preview installed and observed;2400-frame observer comparison and487-frame actual GUI reviewed; constrained local Reader accepted after two recorded failures.',
                publication=str(V/'five-caller-frontend-delivery-v1-current.json'),review=str(ROOT/'reports/Five Native Deck Callers Review.txt'),
                full_objective_complete=False,blocked=False,foreground_UI_preview_changed=True,ongoing_finite_workers=[],
                resident_code_bytes=66320,reserved_arena_data_bytes=129712,total_reservation_bytes=196032,initial_heap_bytes=201856,
                candidate_control_frames=[25007,25007],model_frontend_version='v19',tool_count=18,
                current_GUI_native_callers=5,actual_GUI_frames=487,headless_observer_comparison_frames=2400,
                geometry_native_returns=18,geometry_original_control_returns=18,current_turn_predictions=6,current_turn_optimizer_updates=0,
                saved_native_Chat_trial_pending_review=True)
    # Arena reservation equals total reservation minus semantic code bytes.
    goal['reserved_arena_data_bytes']=196032-66320
    goal['remaining_requirements']=dict(full_objective_complete=False,
        game='Five recovered Deck callers are now native and reviewed on fresh disc. Outer task11E6C remains hosted-only. Whole-game readable source rebuild, arbitrary suspension/IRQ, timing and physical fidelity remain incomplete.',
        local_frontend='Current five-caller GUI launch/movement/pause/close and native returns reviewed. Expected Deck appearance, run chord and audio/visual fidelity remain unverified. Current source routes updated; visible local team trial review and current migration pending.',
        Advertising='V12:128auditedupdates and48matchedpredictions show regression; adapter remains unpromoted. Base27B retained. Broad research/teaching reliability and accepted trained-model validation remain incomplete.',
        future_hardware='Current new files are not yet added to the portable migration package. Actual future-machine acceptance remains unverified.')
    goal['next_actions']=[
        'Integrate outer Deck task11E6C with proper per-task suspension and continuations, preserving the five native callers; qualify original helpers, fallback and fresh-disc controls.',
        'Review the visible local team trial, preserve failures and improve actual current-evidence answers without claiming broad training gains.',
        'Verify expected Deck appearance and documented run chord; retain revision-specific visual/audio/timing limitations.',
        'Improve source-backed Advertising research/education reliability from the rejected adapter evidence; complete remaining full-game source recovery and portable configuration acceptance.']
    save(old_goal,goal)
    paths=[reader_path,V/'Deck-status-live-v20-reviewed-current.json',V/'Deck-status-live-v18-reviewed-current.json',V/'Deck-status-live-v19-reviewed-current.json',
           V/'native-Deck-shared-reviewed-v4-current.json',V/'native-keyboard-live-v3-reviewed-current.json',V/'preview-v3-nonintrusion-current.json',
           V/'native-Deck-context-v11-current.json',V/'native-Deck-current-status-v1-current.json',V/'current-frontend-v19-install-current.json',
           ROOT/'native_deck_status_evidence_v1.py',ROOT/'native_format_evidence.py',ROOT/'native_deck_source_context_v11.py',ROOT/'scripts/native_chat_team_context.py',
           ROOT/'scripts/run_biwn_native_keyboard_v3.py',ROOT/'scripts/native_preview_observer_v3.c',ROOT/'scripts/run_deck_status_live_v20.py',
           ROOT/'Live Local BIWN Briefing.command',ROOT/'BIWN Current Status.command',ROOT/'Show BIWN Native Disc.command',sources]
    state=dict(status='terminal_five_caller_frontend_and_GUI_delivery_reviewed',directory=str(out),report=str(ROOT/'reports/Five Native Deck Callers Review.txt'),
               source_sha256={str(p):sha(p)for p in paths},backups=backups,Reader_words=count,Reader_seconds=reader['stream']['seconds'],
               current_GUI_Deck_callers=5,actual_GUI_frames=487,headless_observer_comparison_frames=2400,
               native_Chat_current_GUI_trial_pending_review=True,new_optimizer_updates=0,whole_goal_complete=False)
    save(out/'protocol.json',state);save(V/'five-caller-frontend-delivery-v1-current.json',state)
    print(json.dumps(dict(directory=str(out),Reader_words=count,Reader_seconds=reader['stream']['seconds'],dependencies=len(paths)),indent=2))


if __name__=='__main__':main()

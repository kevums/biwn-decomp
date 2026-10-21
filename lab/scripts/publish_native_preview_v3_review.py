"""Record the actually observed GUI session and preserve its narrower limits."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v3'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    install_path=ROOT/'verification/native-preview-v3-install-current.json';install=read(install_path)
    for name,expected in read(install['runtime_inventory']).items():assert sha(RT/name)==expected,name
    assert sha(Path(install['app'])/'Contents/MacOS/BIWNTestPreview')==install['launcher_sha256']
    live=read(RT/'verification/native-keyboard-v3-current.json')
    assert live['status']=='terminal_native_keyboard_frontend_stopped_pending_review' and not live['headless']
    assert live['frames']==487 and live['keyboard_events']==29
    assert live['native_returns']==dict(coordinate=8,input=8,face=2,scan=4,geometry=3)
    assert live['all_GPU_Deck_guards_pass'] and live['immutable_native_code_unchanged']
    assert not any(live['original_Deck_body_steps'].values()) and live['invalid_task_identities']==0
    for name,expected in live['source_sha256'].items():assert sha(name)==expected,name
    out=ROOT/'verification/native-keyboard-live-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'live-session.json',live)
    shutil.copyfile(ROOT/'scripts/native_chat_team_context.py',out/'native-chat-context-before-v11.py')
    guide=ROOT/'BIWN Test Preview - Start Here.txt';shutil.copyfile(guide,out/'guide-before-v3.txt')
    guide.write_text('BIWN TEST PREVIEW — START HERE\n\nDouble-click BIWN Test Preview.app on the Desktop, click inside the game window and press P. LM Studio is not required.\n\nArrows: move and turn. Hold C + Up: run (documented control). Z: attack/read.\n1 then D: send Deck activation. 2 then D: equip Beretta. 0: Deck exit. P: pause/resume. Esc: close.\n\nThis is now the reviewed five-caller experimental disc, resumed from its saved street checkpoint. It is a mixed original/compiled game, not a complete decompilation or fresh boot. The previous three-caller runtime is preserved.\n\nThe updated app was observed launching, starting, moving, pausing and closing. Its 487-frame keyboard session recorded returns from all five native callers and passed memory guards. The expected Deck visual transition was not confirmed in this session; native calls alone do not prove that appearance. Revision 23 visual fidelity and audible game audio remain unverified. The C + Up chord was not exercised by the computer-use check.\n\nA separate 2,400-frame headless ordinary-input replay matched full CPU, RAM, video, GPU, DSP and final serialized state with and without the preview counters. This checks the finite observer effect, not general game equivalence.\n\nDirect Python:\n/Users/kevin/.lmstudio/local-ai-lab/.venv/bin/python3.12 /Users/kevin/.lmstudio/local-ai-lab/native-preview-v3/scripts/run_biwn_native_keyboard_v3.py --play-audio\n\nReview: '+str(out/'review.json')+'\n')
    proof=dict(status='terminal_five_caller_GUI_launch_movement_and_counters_reviewed',directory=str(out),
               app=install['app'],runtime=str(RT),disc=live['disc'],disc_sha256=live['disc_sha256'],
               checkpoint_restored=True,fresh_boot=False,frames=487,keyboard_events=29,native_returns=live['native_returns'],
               GPU_returns=live['GPU_returns'],actual_GUI_observed=True,keyboard_movement_verified=True,start_pause_verified=True,close_verified=True,
               all_GPU_Deck_guards_pass=True,immutable_native_code_unchanged=True,
               Deck_shortcut_ordinary_pad_events_recorded=True,Deck_expected_visual_transition_verified=False,
               run_chord_verified=False,audible_game_audio_verified=False,revision23_visual_fidelity_verified=False,
               old_three_caller_runtime_preserved=True,headless_nonintrusion_frames=2400,
               headless_proof=install['proof'],headless_proof_sha256=install['proof_sha256'],
               source_sha256={str(p):sha(p)for p in [Path(__file__),install_path,Path(install['runtime_inventory']),out/'live-session.json',guide]},
               new_training=False,whole_game_complete=False,
               scope='CUA observed the actual app title, initial paused street, P start, held Up street movement, later pause and Esc close. 1,D and0 events reached the frontend; native callbacks ran, but screenshots stayed on a street view. Do not claim a confirmed Deck visual transition or renderer defect. Terminal runtime receipt independently checks native returns and memory integrity. GUI FPS includes deliberate pauses and is not a benchmark.')
    save(out/'review.json',proof);save(ROOT/'verification/native-keyboard-live-v3-reviewed-current.json',proof)
    print(out,flush=True)


if __name__=='__main__':main()

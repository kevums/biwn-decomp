"""Advance current status after the actual five-caller desktop preview review."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
    pointer=V/'native-Deck-current-status-v1-current.json';previous=read(pointer)
    gui_path=V/'native-keyboard-live-v3-reviewed-current.json';gui=read(gui_path)
    assert gui['status']=='terminal_five_caller_GUI_launch_movement_and_counters_reviewed'
    for name,expected in gui['source_sha256'].items():assert sha(name)==expected,name
    for name,expected in previous['dependencies_sha256'].items():assert sha(name)==expected,name
    out=V/'native-Deck-current-status-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    shutil.copyfile(pointer,out/'previous-publication.json');shutil.copyfile(gui_path,out/'GUI-review.json')
    packet=read(previous['packet'])
    packet['checked_current_summary']=packet['checked_current_summary'].replace('The desktop preview still uses the older three-caller checkpoint.','The desktop preview now uses this five-caller disc at a restored checkpoint. Its launch, movement, pause and close were observed; all five native callers returned in487frames. The expected Deck visual transition was not confirmed.')
    packet['checked_answer']=packet['checked_current_summary']
    packet.update(preview_native_Deck_callers=5,latest_image_GUI_verified=True,GUI_review=str(out/'GUI-review.json'),
                  GUI_checkpoint_restored=True,GUI_fresh_boot=False,GUI_frames=487,GUI_native_returns=gui['native_returns'],
                  GUI_Deck_expected_visual_transition_verified=False,GUI_audio_verified=False,headless_observer_nonintrusion_frames=2400)
    packet['remaining']=[x for x in packet['remaining']if x!='Latest-image GUI validation']
    packet['remaining'].append('Expected Deck appearance and run chord validation in the five-caller GUI')
    save(out/'current-status.json',packet)
    # This readable report is current; its earlier frozen review remains intact.
    report=ROOT/'reports/Five Native Deck Callers Review.txt';shutil.copyfile(report,out/'report-before-GUI.txt')
    report.write_text(report.read_text().replace('Desktop BIWN Test Preview remains the earlier three-caller checkpoint build. The five-caller GUI has not been observed.',
       'Desktop BIWN Test Preview now uses the reviewed five-caller disc at its restored street checkpoint. CUA observed launch, start, movement, pause and close over487frames; all five native callers returned with intact guards. Deck shortcut inputs were recorded, but the expected Deck visual transition was not confirmed. A2400-frame headless replay matched full CPU/RAM/video/GPU/DSP and final serialized state with and without counters. This is a finite observer check, not general game equivalence.'))
    shutil.copyfile(report,out/'review.txt')
    dependencies={str(out/'current-status.json'):sha(out/'current-status.json'),str(out/'GUI-review.json'):sha(out/'GUI-review.json'),str(out/'review.txt'):sha(out/'review.txt')}
    dependencies.update(previous['dependencies_sha256'])
    state=dict(previous,directory=str(out),packet=str(out/'current-status.json'),dependencies_sha256=dependencies,latest_GUI_review=str(gui_path))
    save(pointer,state)
    for name in ['BIWN Latest Work.txt','BIWN Latest Result.txt']:
        p=ROOT/name;shutil.copyfile(p,out/('before-'+name));p.write_text('BIWN CURRENT REVIEWED RESULT\n\n'+packet['checked_current_summary']+'\n\nReview: '+str(report)+'\n')
    print(out,flush=True)
if __name__=='__main__':main()

"""Stage a separate five-caller GUI bundle; do not switch the desktop app."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
TARGET=RUNTIME/'native-preview-v3'


def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2)+'\n')
def copy(src,dst):
    src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(['/bin/cp','-c',str(src),str(dst)],capture_output=True,text=True)
    if p.returncode:shutil.copyfile(src,dst)
    assert sha(src)==sha(dst)


def main():
    assert not TARGET.exists(),'Preserve an existing bundle; inspect it before continuing'
    proof_path=ROOT/'verification/native-Deck-shared-reviewed-v4-current.json'
    proof=read(proof_path)
    assert proof['status']=='terminal_fresh_five_native_Deck_callers_reviewed'
    assert sha(proof['build'])==proof['build_sha256'] and sha(proof['disc'])==proof['disc_sha256']
    build=read(proof['build']);parent=read(build['parent_build'])
    run=read(ROOT/'verification/native-Deck-five-caller-geometry-v1-candidate-current.json')
    folder=Path(run['directory'])/'candidate';report=read(folder/'report.json')
    assert sha(folder/'state-final.bin')==report['final_serialized_state_sha256']
    assert sha(folder/'RAM-final.bin')==report['final_RAM_sha256']
    assert sha(folder/'video-final.xrgb8888')==report['frames'][-1]['video_sha256']
    TARGET.mkdir();(TARGET/'runs').mkdir()
    for name in ['run_biwn_native_keyboard_v3.py','native_preview_observer_v3.c','biwn_live_window.py','biwn_audio_output.py','biwn_controller.py','probe_biwn_fresh_CD_boot.py']:
        copy(ROOT/'scripts'/name,TARGET/'scripts'/name)
    for src,name in [(build['derived_disc'],'native.cdi'),(build['component'],'component.bin'),(parent['component'],'GPU-parent-component.bin'),(report['core'],'core.dylib')]:copy(src,TARGET/'artifacts'/name)
    for name in ['state-final.bin','RAM-final.bin','video-final.xrgb8888']:copy(folder/name,TARGET/'candidate'/name)
    copy(ROOT/'verification/preview-three-caller-input-v1.json',TARGET/'artifacts/pad-input-fixture.json')
    new_parent=dict(parent,component=str(TARGET/'artifacts/GPU-parent-component.bin'));pp=TARGET/'verification/parent.json';save(pp,new_parent)
    new_build=dict(build,derived_disc=str(TARGET/'artifacts/native.cdi'),component=str(TARGET/'artifacts/component.bin'),parent_build=str(pp),parent_build_sha256=sha(pp));bp=TARGET/'verification/build.json';save(bp,new_build)
    save(TARGET/'verification/native-Deck-shared-reviewed-v4-current.json',dict(proof,build=str(bp),build_sha256=sha(bp),disc=str(TARGET/'artifacts/native.cdi'),source_provenance=str(proof_path),source_provenance_sha256=sha(proof_path)))
    keep=['requested_options','video','core_sha256','staged_cart_ROM_sha256','final_serialized_state_sha256','final_RAM_sha256']
    new_report={k:report[k]for k in keep};new_report.update(core=str(TARGET/'artifacts/core.dylib'),checkpoint_video_sha256=report['frames'][-1]['video_sha256'])
    save(TARGET/'candidate/report.json',new_report)
    save(TARGET/'verification/native-Deck-five-caller-geometry-v1-candidate-current.json',dict(directory=str(TARGET)))
    link=TARGET/'.venv/bin/python3.12';link.parent.mkdir(parents=True);link.symlink_to(RUNTIME/'.venv/bin/python3.12')
    state=dict(status='terminal_five_caller_preview_bundle_staged_not_desktop_default',directory=str(TARGET),source_provenance=str(proof_path),source_provenance_sha256=sha(proof_path),
               files={str(p.relative_to(TARGET)):sha(p)for p in TARGET.rglob('*')if p.is_file()and not {'runs','__pycache__'}&set(p.relative_to(TARGET).parts)},
               keyboard_window_verified=False,headless_checks_pending=True,new_training=False,whole_game_complete=False)
    save(TARGET/'manifest.json',state);save(ROOT/'verification/native-keyboard-runtime-bundle-v3-current.json',state)
    print(TARGET,flush=True)


if __name__=='__main__':main()

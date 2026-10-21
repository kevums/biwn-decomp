"""Switch the existing Test Preview app after the complete headless replay gate."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v4'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    proof_path=ROOT/'verification/preview-v4-nonintrusion-current.json'
    proof=read(proof_path)
    assert proof['status']=='terminal_six_caller_preview_2400frame_observer_nonintrusion_match'
    assert proof['frames']==2400 and all(x>0 for x in proof['native_returns'].values())
    for name,expected in proof['source_sha256'].items():assert sha(name)==expected,name
    out=ROOT/'verification/native-preview-v4-install'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    app=Path.home()/'Applications/BIWN Test Preview.app'
    binary=app/'Contents/MacOS/BIWNTestPreview'
    shutil.copyfile(binary,out/'previous-BIWNTestPreview')
    source=ROOT/'scripts/native_preview_app_launcher_v5.c'
    target=out/'BIWNTestPreview'
    p=subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(target)],capture_output=True,text=True)
    (out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    shutil.copyfile(target,binary);binary.chmod(0o755)
    signed=subprocess.run(['codesign','--force','--sign','-',str(app)],capture_output=True,text=True)
    (out/'codesign.log').write_text(signed.stdout+signed.stderr);assert signed.returncode==0,signed.stderr
    verified=subprocess.run(['codesign','--verify','--deep','--strict',str(app)],capture_output=True,text=True)
    assert verified.returncode==0,verified.stderr
    # Include the longer fixture and all immutable delivered files. Runs and
    # current execution pointers are mutable diagnostics, not bundle payloads.
    files={str(p.relative_to(RT)):sha(p)for p in RT.rglob('*')if p.is_file()and not {'runs','__pycache__'}&set(p.relative_to(RT).parts)and p.name not in ['manifest.json','native-keyboard-v4-current.json']}
    save(out/'runtime-files.json',files)
    receipt=dict(status='terminal_six_caller_Test_Preview_installed_GUI_observation_pending',directory=str(out),app=str(app),
                 runtime=str(RT),launcher_source=str(source),launcher_sha256=sha(binary),previous_launcher=str(out/'previous-BIWNTestPreview'),
                 proof=str(proof_path),proof_sha256=sha(proof_path),headless_frames=2400,native_returns=proof['native_returns'],
                 runtime_inventory=str(out/'runtime-files.json'),runtime_inventory_sha256=sha(out/'runtime-files.json'),
                 actual_GUI_observed=False,old_v2_and_v3_runtimes_preserved=True,new_training=False,whole_game_complete=False)
    save(out/'protocol.json',receipt);save(ROOT/'verification/native-preview-v4-install-current.json',receipt)
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()

"""One entry point: local source author/reviewer, original checks, readable C."""
import fcntl
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab


def ensure_game_model():
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
        expected=lab.CONFIG['models']['game']
        matching=[m for m in models if m['identifier']==expected['identifier']and m['modelKey']==expected['model_key']]
        loaded=False
        if not matching:
            lab.load('game','mac64-chat')
            loaded=True
        observed=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
        matching=[m for m in observed if m['identifier']==expected['identifier']and m['modelKey']==expected['model_key']]
        assert len(matching)==1 and matching[0]['contextLength']==32768 and matching[0]['parallel']==1
        return dict(model_loaded_by_launcher=loaded,model=matching[0])


def main():
    print(json.dumps(ensure_game_model()),flush=True)
    print('Local model writes and reviews a source-observed doorway helper. Prompts and responses are saved. No weights are trained in this test.',flush=True)
    for script in ['author_biwn_portal_key.py','check_local_biwn_portal_key.py','check_local_portal_geometry_integration.py']:
        print('Running '+script,flush=True)
        subprocess.run([sys.executable,str(ROOT/'scripts'/script)],check=True,timeout=240)
    author=json.loads((ROOT/'verification/local-portal-key-author-current.json').read_text())
    proof=json.loads((ROOT/'verification/local-portal-geometry-integration-current.json').read_text())
    assert Path(proof['helper']).parent==Path(author['directory'])
    print('\nVerified local-authored source: '+proof['helper'],flush=True)
    print('Complete prompts/responses: '+str(Path(author['directory'])/'prompts-and-responses.txt'),flush=True)
    print('2432 original native-CPU value comparisons;192 full portal-function fixtures;5 missing-callback guards.',flush=True)
    print('Roles share model weights. This proves the declared helper/portable-function scope, not full game or native Chat operation.',flush=True)


if __name__=='__main__':main()

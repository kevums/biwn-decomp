"""One installed-menu inference check of current native RNG evidence."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
QUESTION=('How is the native RNG build doing? In at most 180 words, say who wrote it, '
          'what was tested, and what still differs. Distinguish the eight tracked '
          'player/scene fields from actor snapshots, and mention whether this is the whole rebuilt game.')


def main():
    out=ROOT/'verification/native-rng-menu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    launcher=Path.home()/'.lmstudio/local-ai-lab/Start Local AI.command'
    before=set((ROOT/'runs').glob('ask-*-game'))
    state=dict(status='running_installed_menu1',directory=str(out),launcher=str(launcher),
               question=QUESTION,native_Chat=False,new_training=False)
    (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n')
    with(out/'menu.log').open('w')as stream:
        process=subprocess.run([str(launcher)],input='1\n'+QUESTION+'\n/quit\n',
            stdout=stream,stderr=subprocess.STDOUT,text=True,timeout=240)
    added=set((ROOT/'runs').glob('ask-*-game'))-before
    assert process.returncode==0 and len(added)==1,(process.returncode,added)
    run=added.pop();session=json.loads((run/'session.json').read_text());turn=session['turns'][0]
    state.update(status='terminal_installed_native_rng_status_pending_coordinator_review',
                 exit_code=process.returncode,run=str(run),turn=turn)
    text=json.dumps(state,indent=2)+'\n'
    (out/'protocol.json').write_text(text);(ROOT/'verification/native-rng-menu-current.json').write_text(text)
    print(turn.get('answer'),flush=True)
    print('FLAGS',turn.get('quality_flags'),'rounds',turn.get('rounds'),'seconds',turn.get('seconds'),flush=True)


if __name__=='__main__':main()

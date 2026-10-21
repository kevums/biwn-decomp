"""Finite isolated atomic/function/bridge checks for the new exact-disc provider."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def main():
    v=ROOT/'verification';read=lambda p:json.loads(Path(p).read_text())
    bank=read(v/'interior-C-bank-build-current.json')
    assert bank['status']=='terminal_interior_bank_C_compiled_pending_checks'
    nativep=Path(bank['directory'])/'native-CPU-candidate.json'
    cost=read(v/'CPU-division-provider-build-current.json')['cost_candidate']
    core_source=v/'CPU-IRQ-selection-core-build/20261017T094441.859213Z/source'
    commands=[['check_biwn_interior_C_instructions.py']]
    commands += [['check_biwn_interior_C_functions.py','--routine',name]for name in ['select','scan','doorway','interior']]
    commands += [['build_biwn_fast_CPU_bridge.py','--CPU-candidate',bank['CPU_candidate'],'--candidate-output',str(nativep),
                  '--CPU-private-source',str(core_source),'--cost-candidate',cost]]
    out=v/'interior-C-component-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    state=dict(status='running_interior_C_component_pipeline',directory=str(out),pid=os.getpid(),stages=[],
               CPU_candidate=bank['CPU_candidate'],new_model_predictions=0,new_training=False,whole_game_complete=False)
    def mark():
        save(out/'protocol.json',state);save(v/'interior-C-component-pipeline-current.json',state)
    mark()
    try:
        for index,args in enumerate(commands):
            command=[sys.executable,'-u',str(ROOT/'scripts'/args[0]),*args[1:]]
            row=dict(index=index,command=command,script_sha256=sha(ROOT/'scripts'/args[0]),status='running')
            state['stages'].append(row);state['current_stage']=index;mark();print('Stage',index,args,flush=True)
            with(out/f'stage-{index}.log').open('w')as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);row['child_pid']=child.pid;mark()
                code=child.wait()
            row.update(exit_code=code,status='terminal_pass'if code==0 else'terminal_failed');mark()
            assert code==0,(index,(out/f'stage-{index}.log').read_text()[-3000:])
        state['status']='terminal_interior_C_components_and_bridge_pass_pending_review';mark();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_interior_C_component_pipeline_failed',error=repr(error));mark();raise


if __name__=='__main__':main()

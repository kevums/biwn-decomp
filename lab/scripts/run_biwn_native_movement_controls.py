"""Reuse immutable control images/observer with identical movement input."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from run_biwn_native_gameplay_route import ROOT,save,sha


def main():
    prior_path=ROOT/'verification/native-cadence-controls-current.json'
    prior=json.loads(prior_path.read_text())
    assert prior['status']=='terminal_four_arm_cadence_prefix_pending_write_analysis'
    for path,digest in prior['source_sha256'].items():assert sha(path)==digest,path
    for control in prior['controls'].values():assert sha(control['disc'])==control['sha256']
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-movement-controls'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    prefix=ROOT/'verification/whole-merchant-global-fixed-input.json'
    inputs=out/'movement-input.json';windows=json.loads(prefix.read_text())['windows']
    save(inputs,dict(windows=[dict(row,stop_frame=min(row['stop_frame'],661))for row in windows if row['start_frame']<=660]))
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),frames=660,lanes=prior['lanes'],commands=[],
        source_control_proof=str(prior_path),source_control_proof_sha256=sha(prior_path),pad_input='Same recorded L600-620,R621-623,U624onward in all four lanes',
        source_sha256={**prior['source_sha256'],str(inputs):sha(inputs),str(prefix):sha(prefix),str(Path(__file__)):sha(Path(__file__))},
        restored_checkpoints=0,host_guest_RAM_writes=0,whole_game_complete=False)
    def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-movement-controls-active.json',state)
    checkpoint();children=[]
    try:
        for row in prior['commands']:
            lane=row['lane'];command=list(row['command']);command[command.index('--output')+1]=str(out/lane)
            command+=['--frame-controller-script',str(inputs)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_four_arm_movement_prefix';checkpoint();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane in state['lanes']};assert all(not v['errors']for v in observations.values())
        state.update(status='terminal_four_arm_movement_prefix_pending_write_analysis',observations=observations);checkpoint();save(ROOT/'verification/native-movement-controls-current.json',state);print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()

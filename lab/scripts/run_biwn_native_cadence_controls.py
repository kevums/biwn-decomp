"""Four-arm deterministic control of native layout and routine substitution.

No existing image changes. Two new on-disc controls are constructed by
restoring declared patch bytes in copies. Frame observations remain read-only.
"""
import argparse
from datetime import datetime,timezone
import ctypes as c
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import native_rng_evidence
from extract_biwn_stage import swap16
from run_biwn_native_gameplay_route import make_probe,save,sha

FUNCTIONS={0xe540,0xe588,0xe60a,0x1b718,0x1a6e0,0x1a6f8,0x1a77c,0x1a7f4,0x1a87a,0x1a8c6,0x1a8e2,0x1a8f8}
HEAP={0x1521c,0x1526c,0x1557c,0x1558c,0x15592,0x15598,0x1559e}


def make_control(build,out,keep_heap_only):
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset']
    patches=json.loads(Path(build['patch_manifest']).read_text())['patches']
    selected=[row for row in patches if (int(row['address'],16)not in HEAP if keep_heap_only else int(row['address'],16)in FUNCTIONS)]
    if not keep_heap_only:assert {int(row['address'],16)for row in selected}==FUNCTIONS
    control=out/('BIWN-23-heap-only-control.cdi'if keep_heap_only else'BIWN-23-startup-layout-control.cdi')
    shutil.copyfile(build['derived_disc'],control)
    intervals=[]
    with control.open('r+b')as stream:
        for row in selected:
            a=offset+int(row['address'],16)-0x4000;original=bytes.fromhex(row['original']);replacement=bytes.fromhex(row['replacement'])
            stream.seek(a);assert stream.read(len(replacement))==swap16(replacement)
            stream.seek(a);stream.write(swap16(original));intervals.append((a,a+len(original)))
        stream.flush();os.fsync(stream.fileno())
    changed=0;position=0
    with Path(build['derived_disc']).open('rb')as old,control.open('rb')as new:
        while True:
            a=old.read(1048576);b=new.read(1048576);assert len(a)==len(b)
            if not a:break
            if a!=b:
                for index,(x,y)in enumerate(zip(a,b)):
                    if x!=y:assert any(lo<=position+index<hi for lo,hi in intervals);changed+=1
            position+=len(a)
    assert sha(build['derived_disc'])==build['derived_disc_sha256']
    return dict(disc=str(control),sha256=sha(control),restored_patch_addresses=[row['address']for row in selected],
        changed_bytes_from_native=changed,all_other_native_disc_bytes_preserved=True,
        control_kind='Original routines and entry/staging, only3520byte heap reservation retained'if keep_heap_only else'Native startup/copy/cleanup/payload and3520byte heap reservation retained; twelve function redirects restored to original code')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=660);args=parser.parse_args();assert 360<=args.frames<=1500
    summary=native_rng_evidence.load(ROOT);cold=json.loads(Path(summary['proof']).read_text());build=json.loads(Path(cold['build_proof']).read_text())
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-cadence-controls'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    layout=make_control(build,out,False);heap=make_control(build,out,True)
    save(out/'controls.json',dict(layout=layout,heap=heap))
    source=ROOT/'scripts/native_cadence_observer.c';library=out/'libcadence-observer.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    # Validate the serialized counter schema before starting game runs.
    lib=c.CDLL(str(library));lib.finish_observe.argtypes=[c.c_char_p];assert lib.finish_observe(str(out/'empty-check.json').encode())==0
    assert json.loads((out/'empty-check.json').read_text())['event_record_bytes']==224
    original_probe=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';probe=out/'cadence-probe.py'
    text=make_probe(original_probe,library,build['original_disc'],build['component'])
    text=text.replace("Read-only original/native instruction boundary snapshots; no guest execution ownership or writes.","Read-only observed RAM changes with previous CPU PC as a writer candidate; attribution needs opcode/source checking.")
    probe.write_text(text)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    lanes={'reference':build['original_disc'],'heap_only':heap['disc'],'startup_layout':layout['disc'],'native':build['derived_disc']}
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),frames=args.frames,lanes=lanes,controls=dict(heap=heap,layout=layout),commands=[],
        source_sha256={str(path):sha(path)for path in [Path(__file__),ROOT/'scripts/run_biwn_native_gameplay_route.py',source,library,probe,original_probe,core]},
        restored_checkpoints=0,host_guest_RAM_writes=0,pad_input='none',whole_game_complete=False,
        scope='Fresh read-only four-arm prefix. Heap-only isolates seven heap pointer changes; startup-layout adds identical native staging/copy/finalizer; native adds twelve routine redirects. Derived controls are not promoted. No controller buttons, guest-state writes, cycle manipulation or state restoration.')
    def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-cadence-controls-active.json',state)
    checkpoint();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(args.frames),'--core',str(core),'--disc',disc,'--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_four_arm_actor_player_cadence_prefix';checkpoint();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane in lanes}
        assert all(not row['errors']for row in observations.values()),observations
        assert observations['heap_only']['resident_steps']==0
        assert observations['startup_layout']['old_rng_steps']>0 and observations['startup_layout']['old_math_steps']>0
        assert observations['native']['old_rng_steps']==observations['native']['old_math_steps']==0
        state.update(status='terminal_four_arm_cadence_prefix_pending_write_analysis',observations=observations,finished_at=datetime.now(timezone.utc).isoformat());checkpoint();save(ROOT/'verification/native-cadence-controls-current.json',state);print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()

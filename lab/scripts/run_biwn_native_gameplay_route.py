"""Fresh original/native-disc route replay with read-only boundary tracing.

Starts from ordinary load_game/HLE. Existing controller windows are evidence,
not executable instructions. No checkpoint restore or guest RAM/code writes.
The raw original word-scan bug is deliberately retained in this first pair.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_rng_evidence


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def make_probe(source,observer,original,component):
    text=source.read_text()
    text='import sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+text
    replacements={
        'ROOT = Path(__file__).resolve().parents[1]':'ROOT = Path('+repr(str(ROOT))+')',
        '    args = parser.parse_args()':"    parser.add_argument('--disc',type=Path,required=True)\n    args = parser.parse_args()",
        "    disc = ROOT / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'":"    disc = args.disc.resolve()",
        "    button_ids = {'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 8,\n                  'B': 0, 'C': 1, 'OPTION': 3, 'PAUSE': 2}":"    from biwn_controller import JOYPAD_BUTTONS\n    button_ids=JOYPAD_BUTTONS",
    }
    for marker,replacement in replacements.items():
        assert text.count(marker)==1,marker;text=text.replace(marker,replacement)
    marker='    assert 1 <= args.frames <= (24000 if args.post_scene_navigate_actor is not None or args.frame_controller_script or args.navigate_waypoints else 14400)'
    assert text.count(marker)==1
    text=text.replace(marker,'    assert 1 <= args.frames <= 30000  # Explicit bounded gameplay continuation.')
    install=f'''
        observer=c.CDLL({str(observer)!r})
        observer_payload=c.create_string_buffer(Path({str(component)!r}).read_bytes())
        observer.begin_observe.argtypes=[c.c_void_p,c.c_void_p,c.c_int,c.c_void_p,c.c_uint32,c.c_char_p]
        observer.begin_observe.restype=c.c_int
        assert observer.begin_observe(ram_pointer,c.cast(core.BIWNReadCPUState,c.c_void_p),
            int(disc!=Path({str(original)!r})),observer_payload,len(observer_payload.raw)-1,
            str(out/'gameplay-events.bin').encode())==0
        observer.set_frame.argtypes=[c.c_uint32]
        OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32)
        native_observer=OWNER(('observe',observer))
        core.BIWNSetCPUExecOwner.argtypes=[OWNER,c.c_int]
        core.BIWNSetCPUExecOwner(native_observer,0)
'''
    marker='        assert ram_pointer';assert text.count(marker)==1;text=text.replace(marker,marker+install)
    marker='            current_frame = i+1';assert text.count(marker)==1;text=text.replace(marker,marker+'\n            observer.set_frame(current_frame)')
    marker="                       stage_sha256=hashlib.sha256(ram[0x4000:0x100000]).hexdigest())"
    assert text.count(marker)==1
    text=text.replace(marker,"                       floor_word=int.from_bytes(ram[0x49c62:0x49c64],'big'),\n                       raw_word_49c5c=int.from_bytes(ram[0x49c5c:0x49c5e],'big'),\n                       video_sha256=hashlib.sha256(video.get('raw',b'')).hexdigest(),\n"+marker)
    finish='''
        observer.finish_observe.argtypes=[c.c_char_p];observer.finish_observe.restype=c.c_int
        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0
        report['gameplay_observer']='Read-only original/native instruction boundary snapshots; no guest execution ownership or writes.'
'''
    marker="        report.update(status='terminal_fresh_libretro_CD_probe', frames=rows,";assert text.count(marker)==1;text=text.replace(marker,finish+marker)
    return text


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=24738)
    args=parser.parse_args()
    summary=native_rng_evidence.load(ROOT);assert summary and summary['entries']==12
    cold=json.loads(Path(summary['proof']).read_text());build=json.loads(Path(cold['build_proof']).read_text())
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-gameplay-route'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    print(out,flush=True)
    prefix_path=ROOT/'verification/whole-merchant-global-fixed-input.json'
    route_path=ROOT/'verification/merchant-outdoor-controller-input.json'
    prefix=json.loads(prefix_path.read_text())['windows'];route=json.loads(route_path.read_text())['windows']
    windows=prefix+[dict(start_frame=row['start_frame']+23538,stop_frame=row['stop_frame']+23538,buttons=row['buttons'])for row in route]
    windows=[row for row in windows if row['start_frame']<=args.frames]
    inputs=out/'controller-input.json';save(inputs,dict(windows=windows))
    source=ROOT/'scripts/native_gameplay_observer.c';library=out/'libgameplay-observer.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'observer-compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    original_probe=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';probe=out/'fresh-gameplay-probe.py'
    probe.write_text(make_probe(original_probe,library,build['original_disc'],build['component']))
    subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),frames=args.frames,recorded_at=now.isoformat(),
        harness_preflight_fix='Copied probe frame limit extended from24000to30000 for the24738frame route; first failed pair exited before emulation.',
        current_native_proof=summary['proof'],current_native_proof_sha256=sha(summary['proof']),
        build_proof=cold['build_proof'],build_proof_sha256=sha(cold['build_proof']),commands=[],
        checkpoint_restores=0,host_guest_RAM_writes=0,host_CPU_seeds=0,marker_scan_repair_applied=False,
        original_disc=build['original_disc'],candidate_disc=build['derived_disc'],whole_game_complete=False,
        source_sha256={str(path):sha(path)for path in [Path(__file__),source,library,probe,original_probe,inputs,prefix_path,route_path,core]},
        scope='Two fresh ordinary original/native CDI loads with identical recorded pad inputs. Read-only trace. No marker repair, checkpoint restore, scene transplant, position injection or source CPU owner. The existing outdoor route may encounter the known unmodified-game marker bug or diverge earlier; completion is not assumed.')
    def checkpoint():
        save(out/'protocol.json',state);save(ROOT/'verification/native-gameplay-route-active.json',state)
    checkpoint()
    children=[]
    try:
        for lane,disc in [('reference',build['original_disc']),('candidate',build['derived_disc'])]:
            run=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(args.frames),'--core',str(core),
                 '--disc',disc,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
            captures=[frame for frame in [23538,args.frames]if frame<=args.frames]
            run+=['--save-frame-checkpoints',*map(str,sorted(set(captures)))]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT)
            children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=run))
        state['status']='running_fresh_controller_route_pair';checkpoint();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane,_,_ in children}
        assert not any(row['errors']or row['copy_errors']for row in observations.values()),observations
        assert observations['candidate']['old_rng_steps']==observations['candidate']['old_math_steps']==observations['candidate']['old_keypad_steps']==0
        state.update(status='terminal_fresh_controller_route_pair_pending_semantic_analysis',observations=observations,
                     finished_at=datetime.now(timezone.utc).isoformat())
        checkpoint();save(ROOT/'verification/native-gameplay-route-current.json',state)
        print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()

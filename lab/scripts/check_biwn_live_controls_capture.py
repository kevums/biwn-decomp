"""Compare readable controls with calls captured in real instruction-timed play.

No fixtures supply RAM reads, helper results, actor/clock values or RNG results.
Only D0/public CPU bus effects are compared; CPU ABI and timing stay separate.
"""
import argparse
import ctypes as c
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import struct
import check_biwn_game_controls as controls

ROOT=controls.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-receipt',type=Path,required=True)
    parser.add_argument('--replay',type=Path,required=True)
    parser.add_argument('--routine',choices=['controls','scene_cleanup'],default='controls')
    args=parser.parse_args()
    capture=json.loads(args.capture_receipt.read_text());directory=Path(capture['captures'])
    assert capture.get('routine','controls')==args.routine
    assert sha((Path(capture['directory'])/'fast_CPU_bridge.c').read_bytes())==capture['source_sha256']
    component_path=ROOT/'verification/game-controls-current.json'
    component=json.loads(component_path.read_text())
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    for name,expected in component['source_sha256'].items():assert sha((restore/name).read_bytes())==expected,name
    library=component['compiler'][-1];lib=c.CDLL(library)
    if args.routine=='controls':
        raw_fn=lib.biwn_game_controls_with_scratch
        raw_fn.argtypes=[c.POINTER(controls.world.Bus),controls.dispatch.W8,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)]
    else:
        raw_fn=lib.biwn_cleanup_reset_region
        raw_fn.argtypes=[c.POINTER(controls.world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)]
    raw_fn.restype=c.c_int
    name='live-readable-controls'if args.routine=='controls'else'live-readable-scene-cleanup'
    out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    results=[];aborted=[]
    for receipt in sorted(directory.glob('*-result.json')):
        info=json.loads(receipt.read_text());prefix=receipt.name.split('-')[0]
        if not info['complete']:aborted.append(dict(capture=prefix,reason=info));continue
        def read(suffix):return(directory/(prefix+'-'+suffix)).read_bytes()
        before=struct.unpack('>19IH',read('before-CPU.bin'));after=struct.unpack('>19IH',read('after-CPU.bin'))
        initial=read('before-RAM.bin');final=read('after-RAM.bin');raw=read('bus.bin');assert len(raw)%10==0
        actual=[]
        for offset in range(0,len(raw),10):
            op,address,width,value=struct.unpack('>BIBI',raw[offset:offset+10]);assert op in[0,1]and width in[1,2,4]
            actual.append(['w'if op else'r',address,width,value])
        case=dict(kind='live_'+args.routine+'_'+prefix,state=int.from_bytes(initial[0x49cb8:0x49cba],'big'),incoming=list(before[:16]),initial=[],helper_returns={},default_helper_return=0)
        script=controls.Script(initial,case)
        def fn(bus,write8,budget,incoming,result):
            if args.routine=='controls':return raw_fn(bus,write8,before[15]-46,budget,incoming,result)
            return raw_fn(bus,incoming,20000,result)
        status,value=controls.dispatch.translated(fn,script,case,budget=1024)
        written={address+i for op,address,width,_ in actual if op=='w'for i in range(width)}
        ram_mismatch=[hex(a)for a in sorted(written)if a>=len(script.memory)or script.memory[a]!=final[a]]
        row=dict(capture=prefix,status=status,original_D0=after[0],readable_C_D0=value,bus_events=len(actual),written_bytes=len(written),public_write_footprint_matches=not ram_mismatch,ordered_bus_matches=script.trace==actual,errors=script.errors,
                 initial_RAM_sha256=sha(initial),final_RAM_sha256=sha(final),bus_sha256=sha(raw),
                 actor=int.from_bytes(initial[0x49c4c:0x49c4e],'big'),delta=int.from_bytes(initial[0x4c24e:0x4c250],'big'),weapon=int.from_bytes(initial[0x49d5a:0x49d5c],'big'),
                 damage_writes=[event for event in actual if event[0]=='w'and 0x49e34<=event[1]<0x4be64 and(event[1]-0x49e34)%206==0])
        row['passed']=status==0 and not script.errors and value==after[0]and row['ordered_bus_matches']and not ram_mismatch
        if args.routine=='scene_cleanup':
            value_at=lambda data,a,w:int.from_bytes(data[a:a+w],'big')
            handles={value_at(initial,0x4bdb0+i*30,4)for i in range(40)if value_at(initial,0x4bd9c+i*30,2)}-{0}
            caller_return=value_at(initial,before[15],4)
            row['cleanup_observations']=dict(
                floor_before_cleanup=value_at(initial,0x49c62,2),scene_index_before_cleanup=value_at(initial,0x49c64,2),
                caller_return_PC=hex(caller_return),caller_action={0x1a134:'up',0x1a16e:'down'}.get(caller_return,'other'),
                actor_mark_writes=sum(op=='w'and width==2 and address>=0x49d6e and address<=0x49d6e+39*206 and(address-0x49d6e)%206==0 for op,address,width,_ in actual),
                actor_resource_flag_clears=sum(op=='w'and width==2 and value==0 and address>=0x4bd9c and address<=0x4bd9c+39*30 and(address-0x4bd9c)%30==0 for op,address,width,value in actual),
                texture_refcount_writes=sum(op=='w'and width==2 and 0x15b4a2<=address<0x15b532 and(address-0x15b4a2)%4==0 for op,address,width,_ in actual),
                actor_handles_before=[hex(a)for a in sorted(handles)],
                actor_handles_zero_after=[hex(a)for a in sorted(handles)if value_at(final,a,4)==0],
                total_free_before=value_at(initial,0x112d64,4),total_free_after=value_at(final,0x112d64,4))
        if not row['passed']:
            (out/(prefix+'-mismatch.json')).write_text(json.dumps(dict(result=row,actual_bus=actual,readable_C_bus=script.trace,write_footprint_mismatch=ram_mismatch),indent=2)+'\n')
        results.append(row)
    replay=json.loads((args.replay/'comparison.json').read_text())
    checks=replay['checks']
    required=['all_frame_CPU_RAM_pixels_audio','CPU-before-instructions.bin','retired-instruction-costs.bin','final-serialized-state.bin','same_controller_script','C_exact_restore']
    replay_matches=all(checks.get(key)is True for key in required)and all(value for key,value in checks.items()if key!='DSP_owned_positive')
    native=json.loads((args.replay/'C/native-CPU-bridge-report.json').read_text())
    assert native['library']==capture['library']
    passed=bool(replay_matches and results and all(row['passed']for row in results))
    report=dict(status=('live_readable_'+args.routine+('_match'if passed else'_failed')),routine=args.routine,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),captures=len(results),passes=sum(row['passed']for row in results),aborted=aborted,results=results,component_proof=str(component_path),component_source_sha256=component['source_sha256'],capture_receipt=str(args.capture_receipt.resolve()),replay=str(args.replay.resolve()),replay_comparison=str(args.replay/'comparison.json'),replay_checks=checks,replay_CPU_GPU_equivalence_verified=replay_matches,combined_CPU_GPU_DSP_gate_passed=all(checks.values()),damage_call_captures=sum(bool(row['damage_writes'])for row in results),supplied_RAM_reads=False,supplied_helper_results=False,actor_or_clock_overrides=False,new_training=False,default_runtime_promoted=False,
                scope='Readable controls run off-line from exact entry RAM/CPU of natural state2 calls captured during the unmodified ordinary-input300frame attack replay. Full D0 and every ordered public CPU bus read/write match, plus final RAM bytes in CPU write footprint. No external helper result or read override. Private stack, other registers/CCR, concurrent device writes outside that footprint, standalone execution and high-level runtime substitution are not proved. Original instruction-timed provider still runs the game.')
    if args.routine=='scene_cleanup':report['scope']='Readable20F0Ccleanup runs off-line from exact entry RAM/CPU captured in an ordinary-input experimental scene-transition replay. FullD0 and every ordered public CPU bus read/write plus final bytes in CPU write footprint match. No read/texture/heap/helper overrides. Private stack/otherCPUregisters/CCR, concurrent device writes outside footprint and high-level frame-runtime substitution excluded; actual game still uses instruction-timed source provider.'
    report['verifier_sha256']=sha(Path(__file__).read_bytes())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification'/(name+'-current.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key]for key in ['status','captures','passes','damage_call_captures','directory']}),flush=True)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()

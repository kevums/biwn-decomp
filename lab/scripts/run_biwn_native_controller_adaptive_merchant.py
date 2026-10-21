"""Fresh feedback-pad route: building, two elevator ascents and merchant audio.
Different input timing is deliberate and reported, not a fixed-input match.
"""
from datetime import datetime,timezone
import json,os,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,make_probe,save,sha


def main():
    bp=ROOT/'verification/native-controller-disc-build-current.json';build=json.loads(bp.read_text())
    for path,digest in build['source_sha256'].items():assert sha(path)==digest,path
    route_path=ROOT/'verification/normal-route-312-plan.json';assert json.loads(route_path.read_text())['points']==[[9408,41216],[11296,41216],[11296,41376]]
    out=ROOT/'verification/native-controller-adaptive-merchant'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    observer_source=ROOT/'scripts/native_controller_gameplay_observer.c';library=out/'libgameplay-observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer_source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    source=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';text=make_probe(source,library,build['original_disc'],build['component'])
    marker='    post_waypoint_index=0';assert text.count(marker)==1;text=text.replace(marker,marker+'\n    elevator_stable_key=None\n    elevator_stable_frames=0')
    marker='                navigation_inputs = {button_ids[name] for name in buttons}';assert text.count(marker)==1
    policy='''                # Feedback policy: wait300frames in a stable indoor floor,
                # hold ordinary Up until loading begins, release while loading.
                # Only RAM reads; neither guest state nor clocks are changed.
                if scene_change_frame is not None:
                    mode=int.from_bytes(before[0x49c60:0x49c62],'big')
                    floor=int.from_bytes(before[0x49c62:0x49c64],'big')
                    key=(mode,floor)
                    elevator_stable_frames=elevator_stable_frames+1 if key==elevator_stable_key else 0
                    elevator_stable_key=key
                    if mode!=2 or floor<2:
                        buttons=['U'] if mode==2 and floor<2 and elevator_stable_frames>=300 else []
                    # Onfloor2, retain existing corridor/live actor2 navigation.
'''
    text=text.replace(marker,policy+marker)
    post_path=out/'post-scene-waypoints.json'
    save(post_path,dict(points=[[11488,41568],[11680,41568],[12832,41568]],provenance='Same recovered corridor points as earlier checked normal merchant route; ordinary pad navigation only.'))
    probe=out/'adaptive-merchant-probe.py';probe.write_text(text)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),whole_game_complete=False,host_guest_RAM_writes=0,checkpoint_restores=0,marker_repair=False,input_policy='Same three source-derived waypoints fromframe600 using existing live position/yaw steering. After first scene change, hold Up once indoor floor<2 is stable300frames; release onloading/floorchange. Onfloor2 follow recovered corridor points then live actor2 from entry+1101. Stop10000frames after firstentry or20000total. Contact/dialogue outcome is not assumed. Input frames differ by live state; not fixed-input equivalence.',source_sha256={str(p):sha(p)for p in [post_path,Path(__file__),ROOT/'scripts/run_biwn_native_fast_gameplay_route.py',source,probe,route_path,library,observer_source,core]})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-controller-adaptive-merchant-active.json',state)
    mark();children=[]
    try:
        for lane,disc in [('reference',build['original_disc']),('candidate',build['derived_disc'])]:
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','20000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route_path),'--stop-after-scene-change','10000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post_path),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_fresh_adaptive_pad_pair';mark();print('PIDs',[c.pid for _,c,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors'])
            results[lane]=dict(scene_change_frame=report['scene_change_frame'],executed_frames=report['executed_frames'],final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},reached_indoor_floor2=any(row['player_mode_word']==2 and row['floor_word']==2 and row['scene_word']==314 for row in rows),observation=obs,nonzero_audio_samples=report['audio']['nonzero_samples'],report_sha256=sha(out/lane/'report.json'))
        assert results['candidate']['observation']['old_rng_steps']==results['candidate']['observation']['old_keypad_steps']==results['candidate']['observation']['old_controller_steps']==0
        assert results['candidate']['observation']['controller_entries']>0
        state.update(status='terminal_native_controller_adaptive_merchant_pair_classified',results=results,both_reached_indoor_floor2=all(v['reached_indoor_floor2']for v in results.values()),both_captured_nonzero_audio=all(v['nonzero_audio_samples']>0 for v in results.values()),finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-controller-adaptive-merchant-current.json',state);print(json.dumps(results,indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise


if __name__=='__main__':main()

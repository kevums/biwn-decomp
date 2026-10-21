"""Fresh repaired-pair route with an outdoor clearance point.

Original/native13 x unmodified/on-disc assembled18byte scan repair. The
ordinary controller policy is identical; button frames follow live state.
No checkpoint restore, guest-memory patch, clock control or CPU owner.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,make_probe,save,sha


def main():
    bp=ROOT/'verification/native-word-scan-build-current.json';build=json.loads(bp.read_text());gate_path=ROOT/'verification/native-word-scan-current.json';gate=json.loads(gate_path.read_text())
    assert gate['build_proof_sha256']==sha(bp) and gate['native_cases']==512
    for p,digest in build['source_dependencies_sha256'].items():assert sha(p)==digest,p
    baseline=json.loads(Path(build['baseline_proof']).read_text());assert sha(build['baseline_proof'])==build['baseline_proof_sha256']
    for p,digest in baseline['source_sha256'].items():assert sha(p)==digest,p
    all_lanes=dict(original=baseline['original_disc'],original_repaired=build['images']['original_repaired']['disc'],native=baseline['derived_disc'],native_repaired=build['images']['native_repaired']['disc'])
    lanes={key:all_lanes[key]for key in ['original_repaired','native_repaired']}
    assert sha(all_lanes['original'])==baseline['original_disc_sha256'] and sha(all_lanes['native'])==baseline['derived_disc_sha256']
    for lane in ['original_repaired','native_repaired']:assert sha(lanes[lane])==build['images'][lane]['sha256']
    out=ROOT/'verification/native-word-scan-clearance-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source_observer=ROOT/'scripts/native_controller_gameplay_observer.c';host=source_observer.read_text()
    declarations='\n/* Host-only code signatures: checked, never copied into guest RAM. */\n'
    for name,key in [('original_fragment','original_fragment'),('repaired_fragment','repaired_fragment')]:declarations+='static const unsigned char '+name+'[18]={'+','.join('0x'+build[key][i:i+2]for i in range(0,36,2))+'};\n'
    host=host.replace('static uint32_t heap_base;', 'static uint32_t heap_base;\nstatic unsigned repaired,repair_code_errors;\nstatic uint64_t repair_code_checks;'+declarations)
    host=host.replace('candidate=(unsigned)selected;', 'candidate=(unsigned)selected&1u;repaired=((unsigned)selected&2u)!=0;')
    marker='    if(pc==0x400a){';assert host.count(marker)==1
    host=host.replace(marker,'    if(pc==0x400a||pc==0x1b0ee){repair_code_checks++;if(memcmp(ram+0x1b0ee,repaired?repaired_fragment:original_fragment,18))repair_code_errors++;}\n'+marker)
    marker='    array(file,"rng_entries",rng_entries,8);';assert host.count(marker)==1
    host=host.replace(marker,'    fprintf(file,",\\"word_scan_repaired\\":%u,\\"repair_code_checks\\":%llu,\\"repair_code_errors\\":%u",repaired,(unsigned long long)repair_code_checks,repair_code_errors);\n'+marker)
    observer_source=out/'word-scan-observer.c';observer_source.write_text(host);library=out/'libword-scan-observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer_source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    source=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';text=make_probe(source,library,baseline['original_disc'],baseline['component'])
    selected=f"int(disc!=Path({baseline['original_disc']!r}))";assert text.count(selected)==1
    mask=f"(int(disc in [Path({all_lanes['native']!r}),Path({lanes['native_repaired']!r})])|2*int(disc in [Path({lanes['original_repaired']!r}),Path({lanes['native_repaired']!r})]))"
    text=text.replace(selected,mask)
    marker='    post_waypoint_index=0';assert text.count(marker)==1
    text=text.replace(marker,marker+'''\n    elevator_stable_key=None
    elevator_stable_frames=0
    return_started=False
    return_started_frame=None
    floor_zero_frame=None
    exit_pulse_frame=None
    exit_waypoint_index=0
    outdoor_hold=0
    restoration_phase='approach'
''')
    old='    assert 0 <= args.stop_after_scene_change <= (15000 if args.post_scene_navigate_actor is not None else 1200)';assert text.count(old)==1;text=text.replace(old,'    assert 0 <= args.stop_after_scene_change <= (23000 if args.post_scene_navigate_actor is not None else 1200)')
    marker='                navigation_inputs = {button_ids[name] for name in buttons}';assert text.count(marker)==1
    policy='''                if scene_change_frame is not None:
                    mode=int.from_bytes(before[0x49c60:0x49c62],'big')
                    floor=int.from_bytes(before[0x49c62:0x49c64],'big')
                    key=(mode,floor)
                    elevator_stable_frames=elevator_stable_frames+1 if key==elevator_stable_key else 0
                    elevator_stable_key=key
                    media_idle=(int.from_bytes(before[0x47b82:0x47b84],'big')==0 and int.from_bytes(before[0xbd85c:0xbd85e],'big')==65535)
                    if not return_started and current_frame-scene_change_frame>=15001 and mode==2 and floor==2 and media_idle:
                        return_started=True;return_started_frame=current_frame
                    if not return_started:
                        restoration_phase='merchant_approach_or_wait'
                        if mode!=2 or floor<2:
                            restoration_phase='ascend_or_load'
                            buttons=['U'] if mode==2 and floor<2 and elevator_stable_frames>=300 else []
                    elif mode==2 and floor>0:
                        restoration_phase='descend_or_wait'
                        buttons=['D'] if elevator_stable_frames>=300 else []
                    elif mode==2 and floor==0:
                        if floor_zero_frame is None:floor_zero_frame=current_frame
                        if current_frame-floor_zero_frame<220:
                            restoration_phase='floor0_wait';buttons=[]
                        else:
                            if exit_pulse_frame is None:exit_pulse_frame=current_frame
                            if current_frame-exit_pulse_frame<10:
                                restoration_phase='recorded_C_pulse';buttons=['C']
                            else:
                                restoration_phase='exit_waypoints';address=None;active=True
                                points=[[12864,42416],[13024,42416]]
                                tx,tz=points[exit_waypoint_index]
                                if (tx-x)**2+(tz-z)**2<=64 and exit_waypoint_index<len(points)-1:
                                    exit_waypoint_index+=1;tx,tz=points[exit_waypoint_index]
                                dx,dz=tx-x,tz-z
                                target=round(math.atan2(-dx,dz)*128/math.pi)%256
                                error=(target-heading+128)%256-128
                                buttons=[] if dx*dx+dz*dz<=64 else(['L']if error>2 else ['R']if error< -2 else ['U'])
                    elif mode==1:
                        # Move clear of the portal before testing idle stability.
                        address=None;active=True;tx,tz=13056,42400
                        dx,dz=tx-x,tz-z;target=round(math.atan2(-dx,dz)*128/math.pi)%256
                        error=(target-heading+128)%256-128
                        if dx*dx+dz*dz<=64:
                            restoration_phase='outdoor_hold';outdoor_hold+=1;buttons=[]
                        else:
                            restoration_phase='outdoor_clearance';outdoor_hold=0
                            buttons=['L']if error>2 else ['R']if error< -2 else ['U']
                    else:
                        restoration_phase='return_loading';outdoor_hold=0;buttons=[]
'''
    text=text.replace(marker,policy+marker)
    marker='                                  buttons=buttons, no_guest_memory_writes=True)';assert text.count(marker)==1
    text=text.replace(marker,marker+"\n                navigation.update(restoration_phase=restoration_phase,return_started=return_started,return_started_frame=return_started_frame,floor_zero_frame=floor_zero_frame,exit_waypoint_index=exit_waypoint_index,outdoor_hold=outdoor_hold)")
    marker='            if args.stop_after_scene_change and scene_change_frame is not None and current_frame>=scene_change_frame+args.stop_after_scene_change:';assert text.count(marker)==1
    text=text.replace(marker,'            if outdoor_hold>=120 and row[\'player_mode_word\']==1:break\n'+marker)
    probe=out/'fresh-word-scan-route.py';probe.write_text(text)
    subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    route_path=ROOT/'verification/normal-route-312-plan.json';post=out/'merchant-corridor.json';save(post,dict(points=[[11488,41568],[11680,41568],[12832,41568]]))
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),scan_component_proof=str(gate_path),scan_component_proof_sha256=sha(gate_path),maximum_frames=30000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,host_marker_patch=False,repair_delivery='Assembled18bytefragment inCDI before ordinary load; flags/bytes checked at400Aand every scanentry.',whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/run_biwn_native_fast_gameplay_route.py',source,source_observer,observer_source,library,probe,route_path,post,core]},input_policy='Feedback approach/ascend/merchant as prior route. Begin return only at firstentry+15001with floor2and mediaidle; normalDown tofloor0 after300stableframes per floor, then220wait/recordedC10pulse/doorwaypoints12864,42416→13024,42416(tolerance8). Onoutdoorentry continue to source-derived clearancepoint13056,42400(tolerance8), then stop after120stableoutdoorframes or30000total/entry+21000. Two freshrepairedlanes; earlierunmodified controls neverreached thechangedbranch. Pad timings differ. No expected outcome assumed.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-word-scan-clearance-route-active.json',state)
    mark();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','30000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route_path),'--stop-after-scene-change','21000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_two_fresh_repaired_clearance_lanes';mark();print('PIDs',[child.pid for _,child,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
            if lane.startswith('native'):assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==0
            returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
            floors=sorted({x['floor_word']for x in returned})
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=floors,outdoor_after_return=any(x['player_mode_word']==1 for x in returned),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
        for row in results.values():row['continuous_merchant_to_outdoor']=bool(row['merchant_reached']and{0,1}<=set(row['return_floor_values'])and row['completed_outdoor_hold'])
        state.update(status='terminal_two_fresh_repaired_clearance_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-word-scan-clearance-route-current.json',state);print(json.dumps({lane:{k:v for k,v in row.items()if k not in ['observation','last_navigation']}for lane,row in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

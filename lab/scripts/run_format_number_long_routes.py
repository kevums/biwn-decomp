"""Fresh adaptive ordinary-button routes on base/optimized formatter discs.
Reuses the checked navigation/controller policy and read-only resource observer.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    rp=ROOT/'verification/native-load-scan-route-current.json';route=read(rp);directory=Path(route['directory']);template=directory/'fresh-load-route.py';observer=directory/'load-observer.c'
    for p in [template,observer]:assert sha(p)==route['source_sha256'][str(p)]
    parent=read(route['build_proof']);builds={}
    for lane,name in [('parent','native-unsigned-format'),('number','native-number-format')]:
        p=ROOT/'verification'/(name+'-disc-build-current.json');b=read(p);assert sha(b['derived_disc'])==b['derived_disc_sha256']
        e=read(ROOT/'verification'/(name+'-disc-entry-current.json'));assert e['status']=='terminal_native_entry_heap_and_component_pass'and e['build_proof_sha256']==sha(p)
        builds[lane]=b
    symbols=['biwn_native_heap_allocate_body','biwn_native_heap_compact_body','biwn_native_scheduler_dispatch','biwn_native_scheduler_remove','biwn_native_scheduler_select','biwn_native_scheduler_rte','biwn_native_task_create','biwn_native_copy_body','biwn_native_free_body','biwn_native_heap_initialize','biwn_native_resource_release_body','biwn_native_heap_initialize_return','biwn_native_resource_acquire','biwn_native_resource_acquire_body','biwn_native_resource_load','biwn_native_resource_load_body','biwn_native_load_scan']
    assert all(parent['symbols'][s]==builds['parent']['symbols'][s]==builds['number']['symbols'][s]for s in symbols),'Rebuild observer for changed prefix symbols'
    out=ROOT/'verification/native-number-format-long-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=out/'resource-observer.c';source.write_bytes(observer.read_bytes());library=out/'resource-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lines=template.read_text().splitlines(keepends=True);changed=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changed.append('observer library')
        elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(builds['number']['component'])+' if disc==Path('+repr(builds['number']['derived_disc'])+') else '+repr(builds['parent']['component'])+').read_bytes())\n';changed.append('exact per-disc padded signature')
        elif line.startswith('            (511 if disc==Path('):lines[i]='            511,observer_payload,len(observer_payload.raw)-1,\n';changed.append('both profiles have compiled acquire/loader and identical prefix symbols')
    assert len(changed)==3
    probe=out/'fresh-route.py';probe.write_text(''.join(lines));compile(probe.read_text(),str(probe),'exec')
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';waypoints=ROOT/'verification/normal-route-312-plan.json';corridor=ROOT/'verification/native-word-scan-clearance-long-route/20261018T053248.873269Z/merchant-corridor.json'
    for p in [core,waypoints,corridor]:assert sha(p)==route['source_sha256'][str(p)]
    state=dict(status='running_fresh_base_optimized_adaptive_routes',pid=os.getpid(),directory=str(out),commands=[],maximum_frames=35000,
        checkpoint_restores=0,additional_host_guest_RAM_writes=0,host_CPU_seeds=0,adaptive_controller=True,identical_fixed_input_claimed=False,
        selector_Deck_repairs_added=False,LLM_calls=0,training_updates=0,whole_game_complete=False,
        prior_policy=str(rp),prior_policy_sha256=sha(rp),template_changes=changed,common_prefix_symbol_positions_verified=symbols,
        source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer,source,library,probe,core,waypoints,corridor]},
        builds={lane:dict(disc=b['derived_disc'],disc_sha256=b['derived_disc_sha256'],heap_start=b['heap_start'])for lane,b in builds.items()})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-number-format-long-route-active.json',state)
    mark();children=[]
    try:
        for lane,b in builds.items():
            cmd=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',b['derived_disc'],'--navigate-waypoints',str(waypoints),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(corridor),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=cmd));mark()
        print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
        for lane,b in builds.items():
            d=out/lane;report=read(d/'report.json');obs=read(d/'gameplay-observation.json');rows=report['frames'];last=rows[-1]
            assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors'])and obs['repair_code_checks']>0
            assert obs['heap_base']==b['heap_start']and obs['native_C_allocate_calls']>0
            assert obs['native_C_acquire_calls']==obs['acquire_entries']>0 and obs['old_acquire_body_steps']==0 and obs['acquire_task_stack_outside']==0
            assert obs['native_C_loader_calls']==obs['loader_entries']>0 and obs['old_loader_body_steps']==0 and obs['loader_task_stack_outside']==0
            returned=[r for r in rows if(r.get('navigation')or{}).get('return_started')]
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],
                merchant_reached=any(r['player_mode_word']==2 and r['floor_word']==2 and r['scene_word']==314 and abs(r['raw_player_X']-12832)<=16 and abs(r['raw_player_Z']-42385)<=16 for r in rows),
                return_floor_values=sorted({r['floor_word']for r in returned}),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,
                nonzero_audio_samples=report['audio']['nonzero_samples'],final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},
                observation=obs,report_sha256=sha(d/'report.json'),scope='Adaptive normal-button policy; route completion and timing reported, no identical-input or frame-equivalence claim.')
        state.update(status='terminal_fresh_base_optimized_adaptive_routes_classified',results=results);mark();save(ROOT/'verification/native-number-format-long-route-current.json',state)
        print(json.dumps({lane:{k:v for k,v in r.items()if k!='observation'}for lane,r in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

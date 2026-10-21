"""Review terminal stationary/motion lanes and run the actual C integrator.

This evaluates captured original-CPU transitions, not a duplicated Python
implementation of the recovered routine. It does not waive fresh-route gates.
"""
import ctypes as c
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    out = V/'record-loop-equal-state-reviewed-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    deps = {str(Path(__file__)):sha(__file__)}
    cases = {}; summary = {}
    for mode in ['stationary','motion']:
        cases[mode] = {}; summary[mode] = {}
        for origin in ['candidate','control']:
            cases[mode][origin] = {}; summary[mode][origin] = {}
            for lane in ['native','original','replica']:
                name = (f'record-loop-equal-state-{origin}-{lane}-v1-current.json' if mode=='stationary'
                        else f'record-loop-equal-state-motion-{origin}-{lane}-v2-current.json')
                pointer = V/name; job = read(pointer); directory = Path(job['directory'])
                assert job['status']=='terminal_saved_state_equal_origin_diagnostic_pending_review'
                assert job['frames']==180 and job['snapshot_restores']==1 and job['host_pose_or_timer_writes']==0
                assert job['immutable_component_and_arena_fences_unchanged']
                for path,digest in job['source_sha256'].items():assert sha(path)==digest,path
                deps.update(job['source_sha256']);deps[str(pointer)]=sha(pointer)
                rows = read(directory/'frames.json'); assert len(rows)==180
                events = read(directory/'world-events.json') if mode=='motion' else None
                cases[mode][origin][lane] = (job,rows,events)
                save(out/f'{mode}-{origin}-{lane}-job.json',job)
                summary[mode][origin][lane] = dict(counters=job['counters'],code_bytes_changed=job['host_code_bytes_changed'],
                    world_events=len(events) if events else None, nonzero_speed_events=sum(bool(e['speed'])for e in events)if events else None,
                    final_pose=rows[-1]['pose'],final_video_sha256=rows[-1]['video_sha256'])
            a,b=[cases[mode][origin][lane]for lane in ['native','original']]
            assert a[0]['initial_state']==b[0]['initial_state']
            reference='native'if origin=='candidate'else'original'
            ref=cases[mode][origin][reference];rep=cases[mode][origin]['replica']
            assert ref[1:]==rep[1:],'Unchanged replay is not deterministic'
            comparison={key:dict(differing_frames=sum(x[key]!=y[key]for x,y in zip(a[1],b[1])),
                                  first=next((x['frame']for x,y in zip(a[1],b[1])if x[key]!=y[key]),None),
                                  final_equal=a[1][-1][key]==b[1][-1][key])for key in ['pose','video_sha256','CPU','GPU','DSP']}
            summary[mode][origin]['comparison']=comparison
            summary[mode][origin]['unchanged_replica_exact']=True
            assert comparison['DSP']['differing_frames']==0
            if mode=='stationary':
                assert comparison['pose']['differing_frames']==comparison['video_sha256']['differing_frames']==0
                assert a[0]['counters'][1]==119 and a[0]['counters'][2]in [118,119]
                assert a[0]['counters'][1]-a[0]['counters'][2]in [0,1]
                assert a[0]['counters'][3]==a[0]['counters'][4]>0
                assert all(row['pose']==a[0]['initial_state']['pose']for row in a[1]+b[1])
            else:
                assert comparison['pose']['differing_frames']>0 and comparison['video_sha256']['differing_frames']>0
                assert a[0]['ordinary_input_schedule']==b[0]['ordinary_input_schedule']==dict(up_frames=[1,60],release_frames=[61,180])
    assert summary['motion']['candidate']['comparison']['pose']['first']==7
    assert summary['motion']['candidate']['comparison']['video_sha256']['first']==9
    assert summary['motion']['candidate']['native']['nonzero_speed_events']==22
    assert summary['motion']['candidate']['original']['nonzero_speed_events']==23
    assert summary['motion']['control']['native']['nonzero_speed_events']==summary['motion']['control']['original']['nonzero_speed_events']==23
    assert summary['motion']['control']['comparison']['pose']['final_equal']
    restoration=ROOT/'projects/black-ice-white-noise/restoration'
    source=out/'actual-world-integrator.c'
    source.write_text('#include <string.h>\n#include "biwn_world_update.c"\n'+r'''
static uint8_t memory[0x200000];
static int rd8(void*p,uint32_t a,uint8_t*v){(void)p;if(a>=sizeof(memory))return 1;*v=memory[a];return 0;}
static int rd16(void*p,uint32_t a,uint16_t*v){(void)p;if(a>=sizeof(memory)-1)return 1;*v=(uint16_t)(memory[a]*256u+memory[a+1]);return 0;}
static int rd32(void*p,uint32_t a,uint32_t*v){uint16_t hi,lo;if(rd16(p,a,&hi)||rd16(p,a+2,&lo))return 1;*v=(uint32_t)hi*65536u+lo;return 0;}
static int wr16(void*p,uint32_t a,uint16_t v){(void)p;if(a>=sizeof(memory)-1)return 1;memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;return 0;}
static int wr32(void*p,uint32_t a,uint32_t v){return wr16(p,a,(uint16_t)(v>>16))||wr16(p,a+2,(uint16_t)v);}
int replay_step(const uint32_t *in,uint32_t *out){
 struct biwn_world_bus bus={rd8,rd16,rd32,wr16,wr32,0,0,0};
 memset(memory,0,sizeof(memory));wr32(0,0x49c50,in[0]);wr32(0,0x49c56,in[1]);
 for(unsigned i=0;i<3;i++){wr16(0,0x49c5a+i*2,(uint16_t)in[2+i]);wr16(0,0x49b8c+i*2,(uint16_t)in[5+i]);wr16(0,0x49b92+i*2,(uint16_t)in[8+i]);wr16(0,0x49cde+i*2,(uint16_t)in[11+i]);wr16(0,0x49ce6+i*2,(uint16_t)in[14+i]);}
 if(integrate(&bus,0)!=BIWN_WORLD_OK||integrate(&bus,1)!=BIWN_WORLD_OK)return 1;
 rd32(0,0x49c50,&out[0]);rd32(0,0x49c56,&out[1]);
 for(unsigned i=0;i<3;i++){uint16_t v;rd16(0,0x49c5a+i*2,&v);out[2+i]=v;rd16(0,0x49b8c+i*2,&v);out[5+i]=v;rd16(0,0x49b92+i*2,&v);out[8+i]=v;}
 return 0;
}
''')
    library=out/'actual-world-integrator.dylib'
    q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),
                      str(source),str(restoration/'biwn_inventory_select.c'),'-o',str(library)],capture_output=True,text=True)
    (out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    lib=c.CDLL(str(library));lib.replay_step.argtypes=[c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];lib.replay_step.restype=c.c_int
    checks=[]
    for origin in ['candidate','control']:
        for lane in ['native','original']:
            job,rows,events=cases['motion'][origin][lane]
            for i,e in enumerate(events):
                incoming=[e['x'],e['z'],*e['player_fraction'],*e['camera'],*e['camera_fraction'],*e['delta_integer'],*e['delta_fraction']]
                a=(c.c_uint32*17)(*incoming);b=(c.c_uint32*11)();assert lib.replay_step(a,b)==0
                if i+1<len(events):
                    n=events[i+1];expected=[n['x'],n['z'],*n['player_fraction'],*n['camera'],*n['camera_fraction']]
                else:
                    n=rows[-1]['pose'];expected=[*n['integer_XZ'],*n['player_fraction_words'],*n['camera_words'],*n['camera_fraction_words']]
                assert list(b)==expected,(origin,lane,i,list(b),expected)
                checks.append(dict(origin=origin,lane=lane,event_index=i,frame=e['frame'],expected=expected,actual=list(b)))
    assert len(checks)==627
    save(out/'actual-C-transition-checks.json',checks);save(out/'lane-summary.json',summary)
    for file in [source,library,out/'actual-C-transition-checks.json',out/'lane-summary.json',
                 restoration/'biwn_world_update.c',restoration/'biwn_world_update.h',restoration/'biwn_inventory_select.c',
                 restoration/'biwn_inventory_select.h',restoration/'biwn_input_dispatch.c',restoration/'biwn_input_dispatch_cpu.c',
                 restoration/'biwn_world_flow_cpu.c']:
        deps[str(file)]=sha(file)
    report=ROOT/'reports/BIWN Equal State Rendering and Movement Diagnosis.txt'
    report.write_text('BIWN — equal-state rendering and movement diagnosis\n\n'
        'Twelve separate180-frame saved-state lanes:two endpoint origins times native/original/unchanged-replica,each stationary and moving. '
        'Every lane restores an exact serialized machine/RAM snapshot. Only the10scene-entry code bytes may change;player/camera/timers are untouched. '
        'These are diagnostic interventions,not fresh boots. Both stationary and moving unchanged replicas reproduce every recorded CPU/GPU/DSP/RAM/video row and movement event exactly.\n\n'
        'Stationary:at each of the two distinct endpoint poses,native and original scene code produce identical video for all180frames. '
        'Native code enters119scene calls in each origin,completes119/118,and completes238/237record bodies;original entries166/165. CPU/GPU states differ but DSP hashes and all observed poses agree. The fixed180-frame boundary can leave one native scene call active;this is not a quiescence or full observer-guard proof. '
        'Both endpoint images remain distinct across origins. This narrows the failure;it is not broad renderer equivalence or a fresh-matrix pass.\n\n'
        'Motion:both code variants receive the same ordinary Up input for60frames then release120frames. From candidate origin,the player first differs atframe7 and video at9;native consumes22nonzero movement events versus23original. '
        'From control origin,both consume23nonzero movement events and end at exactly the same expanded pose despite7intermediate pose and10video differences. '
        'Cadence differs:world events136/177(candidate origin),137/177(control origin). The recovered world-integrate C function reproduces all627captured next-event/final position,fraction and camera transitions exactly. '
        'This is an executable check of existing source against captured original-CPU transitions,not newly recovered whole functions. '
        'The event field named buttons is the raw word at49BAC,not a verified held-button label.\n\n'
        'A scene-code-only intervention therefore changes world-update/input timing and,in one bounded input trial,the number of consumed movement steps. '
        'No arithmetic mismatch is observed in the627captured integration transitions. The specific cause of the earlier fresh-route final mismatch is still unresolved. '
        'The exact fresh matrix-video failure remains failed;v37 stays unpromoted and v34 remains reviewed baseline. No pose/timer masks,input tuning,training updates or fresh-game reruns were used.\n\n'
        'Next:observe191F4input dt/remainder and held-button values at the source boundaries to attribute the extra movement step,then address scene cadence without changing input/state to force matching images.\n')
    deps[str(report)]=sha(report)
    facts=dict(status='terminal_equal_state_rendering_agrees_motion_cadence_differs_C627_transitions_pass',directory=str(out),report=str(report),
               lanes=12,frames_per_lane=180,unchanged_replica_pairs=4,unchanged_replicas_exact=True,
               stationary_same_origin_native_original_video_differences=[0,0],stationary_same_origin_pose_differences=[0,0],
               motion_candidate_origin_first_pose_difference=7,motion_candidate_origin_first_video_difference=9,
               motion_candidate_origin_nonzero_steps=dict(native=22,original=23),motion_control_origin_nonzero_steps=dict(native=23,original=23),
               actual_recovered_C_integrator_transitions=627,all_C_integrator_transitions_pass=True,
               source_unique_functions_recovered=0,source_game_code_changed=False,snapshot_restores=12,host_pose_or_timer_writes=0,
               fixed_frame_cut_can_leave_scene_active=True,all_monitors_quiescent_claimed=False,
               changed_scene_entry_lanes=4,changed_code_bytes_per_intervention=10,new_fresh_routes=0,new_predictions=0,new_training=False,
               fresh_matrix_gate_waived=False,v37_promoted=False,full_fidelity_verified=False,source_sha256=deps)
    save(out/'review.json',facts);save(V/'record-loop-equal-state-reviewed-v2-current.json',facts)
    print(facts['status'],'12lanes/4replicas/627actual-C transitions',flush=True)


if __name__=='__main__':main()

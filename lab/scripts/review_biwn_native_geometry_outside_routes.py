"""Review the exact geometry disc and its same-layout original-entry control."""
import json
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification'
    bp=v/'native-geometry-outside-disc-build-current.json'
    build=read(bp)
    assert build['status']=='terminal_native_geometry_outside_disc_built_entry_verified_pending_gameplay'
    assert build['parent_resident_prefix_byte_identical'] and build['linked_component_bytes']==17084
    assert build['component_bytes']==20480 and build['appended_bytes']==212
    assert build['linked_native_cases']==1376 and build['linked_changing_coordinate_cases']==256 and build['entry_cases']==96
    deps={}
    def bind(p,expected=None):
        p=Path(p).resolve();digest=sha(p)
        assert expected is None or digest==expected,str(p)
        assert str(p) not in deps or deps[str(p)]==digest,str(p)
        deps[str(p)]=digest
    bind(bp)
    for key in ['derived_disc','derived_stage','patch_manifest']:
        bind(build[key],build[key+'_sha256'])
    for p,h in build['source_sha256'].items():
        bind(p,h)
    for key in ['linked_component','component']:
        bind(build[key])
    component=read(v/'native-geometry-outside-reviewed-current.json')
    bind(v/'native-geometry-outside-reviewed-current.json')
    bind(component['canonical_source'],component['canonical_sha256'])
    bind(component['component_proof'],component['component_proof_sha256'])
    assert not component['raw_attempt_pass'] and not component['raw_repair_pass'] and component['coordinator_C_edits']==1
    lanes=[]
    for name in ['native-geometry-outside-route-current.json','native-geometry-outside-layout-control-current.json']:
        path=v/name;lane=read(path);bind(path)
        assert lane['status']=='terminal_native_frame_acquire_route_pending_review'
        assert lane['exit_code']==0 and lane['live_monitor_pass'] and lane['geometry_monitor_pass'] and lane['returned_outdoors']
        assert lane['build_proof_sha256']==sha(bp)
        for p,h in lane['source_sha256'].items():
            bind(p,h)
        folder=Path(lane['directory'])/'candidate'
        report=read(folder/'report.json');bind(folder/'report.json',lane['report_sha256'])
        observed=read(folder/'gameplay-observation.json')
        assert observed==lane['observations']
        assert observed['geometry_entries']==observed['geometry_returns']>0
        assert observed['geometry_errors']==observed['geometry_pending']==observed['geometry_stack_outside']==0
        for file in ['gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le']:
            bind(folder/file)
        lanes.append((lane,report))
    candidate,control=lanes[0][0],lanes[1][0]
    assert control['control_delta']['restored_entries']==['1028E'] and control['control_delta']['declared_bytes']==8
    assert candidate['observations']['geometry_entries']==candidate['observations']['geometry_native_entries']
    assert candidate['observations']['geometry_old_steps']==0
    assert control['observations']['geometry_native_entries']==0 and control['observations']['geometry_old_steps']>0
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','navigation']
    differences={key:sum(a[key]!=b[key] for a,b in zip(lanes[0][1]['frames'],lanes[1][1]['frames'])) for key in fields}
    equal_PCM=sha(Path(candidate['directory'])/'candidate/frontend-PCM.s16le')==sha(Path(control['directory'])/'candidate/frontend-PCM.s16le')
    now=datetime.now(timezone.utc);out=v/'native-geometry-outside-live-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=ROOT/'reports/native-geometry-outside-live.txt'
    o=candidate['observations'];c=control['observations']
    report.write_text('BIWN — COMPLETE NATIVE BOUNDARY ROUTINE LIVE TEST\n'+now.isoformat()+'\n\n'
        'The complete1028E signed boundary routine is installed in a separate experimental disc. It adds212bytes after the unchanged16872-byte cache-cluster prefix,using17084of20480reservedbytes. Heap floor and the existing startup copy/clear sizes are unchanged. '
        'The only internal absolute relocation is the declared call to the scalar C kernel. Final-address1376stable+256changing-coordinate comparisons and96startup cases passed before the derived disc was tested.\n\n'
        f'Candidate completed{candidate["frames"]}frames;control completed{control["frames"]}. Both returned outdoors after the merchant/media route. Candidate observed{o["geometry_entries"]}complete boundary calls,all entering compiled code,with{o["geometry_early"]}early returns,{o["geometry_inside"]}inside returns and{o["geometry_last_outside"]}final-bound outside returns. '
        f'All observed D/A registers,SR,stack banks,return word andargument checks passed. User-stack observations:{o["geometry_user_observations"]};minimum headroom:{o["geometry_min_headroom"]}bytes;maximum private depth:{o["geometry_max_depth"]}bytes. '
        f'The same-layout control restores only the8-byte original1028Eentry;it observed{c["geometry_entries"]}original calls andzero compiled entries. Other cache routines,payload andlayout remain compiled. '
        f'Compared prefix video differences:{differences["video_sha256"]};PCM byte equality:{equal_PCM}. Fullstate/route differences are retained in the review receipt. Neither adaptive completion nor the live return monitor establishes exact whole-game equivalence or a general speedup.\n\n'
        'Authorship: local base27B Author andone repairAuthor supplied the scalar logic;coordinator removed oneunusedpointer declaration inaseparatecopy. Both raw model drafts failedtheir gates,andthe same-weight Reviewer missed theinitialbyte-offset error. Coordinator supplied ABI,checkers,diagnostic,relocation/integration andlive observer. Three actual local predictions,no newweights,no independentmodel verification.\n\n'
        'This route uses retained emulator CPU/GPU/DSP/IRQ. The separate combined C-processor job is on the preceding16872-byte cache-cluster disc;its eventual result must not be transferred tothis17084-byte disc. The current interactive preview was not restarted. Whole readable game/source rebuild,standalone physical-console boot/audio andnative LMStudio Chat-window demonstration remain incomplete.\n\n'
        'Component and exact prompts: '+component['report']+'\n'+component['transcript']+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_native_geometry_outside_two_live_routes_reviewed',recorded_at=now.isoformat(),directory=str(out),
                report=str(report),build=str(bp),build_sha256=sha(bp),candidate_frames=candidate['frames'],control_frames=control['frames'],
                compared_prefix_frames=min(candidate['frames'],control['frames']),same_layout_differences=differences,PCM_equal=equal_PCM,
                candidate_observations=o,control_observations=c,dependencies_sha256=deps,new_training=False,
                native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-geometry-outside-live-reviewed-current.json',result)
    print(json.dumps({key:result[key] for key in ['status','candidate_frames','control_frames','PCM_equal','same_layout_differences']}),flush=True)


if __name__=='__main__':
    main()

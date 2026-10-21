"""Freeze the newest reviewed native build without changing older publications."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';review_path=v/'native-geometry-outside-live-reviewed-current.json';review=read(review_path)
    assert review['status']=='terminal_native_geometry_outside_two_live_routes_reviewed'
    build=read(review['build']);assert sha(review['build'])==review['build_sha256']
    assert review['candidate_frames']==review['control_frames']==24978
    diffs=review['same_layout_differences']
    assert diffs['CPU_full']==1 and all(diffs[k]==0 for k in ['video_sha256','navigation','full_GPU_state_sha256','full_DSP_state_sha256'])
    assert review['PCM_equal'] and build['linked_native_cases']==1376 and build['linked_changing_coordinate_cases']==256
    assert build['linked_component_bytes']==17084 and build['component_bytes']==20480 and build['entry_cases']==96
    component=read(v/'native-geometry-outside-reviewed-current.json');assert component['coordinator_C_edits']==1
    assert not component['raw_attempt_pass'] and not component['raw_repair_pass']
    now=datetime.now(timezone.utc);out=v/'current-biwn-latest-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    snapshots=out/'snapshots';snapshots.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        path=Path(path).resolve();assert path.is_relative_to(ROOT)
        actual=sha(path);assert expected is None or actual==expected,str(path)
        # Mutable pointer names are historical byte-for-byte snapshots in this publication.
        target=path
        if path.name.endswith(('-current.json','-active.json')):
            target=snapshots/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name)
            shutil.copyfile(path,target);assert sha(target)==actual
            aliases[str(path)]=str(target)
        deps[str(target)]=actual
    for p,h in review['dependencies_sha256'].items():bind(p,h)
    bind(review_path)
    bind(v/'native-geometry-outside-reviewed-current.json')
    for p in [component['report'],component['transcript'],component['raw_author'],component['raw_repair'],component['cleanup']]:bind(p)
    for key in ['raw_author','raw_repair','cleanup']:
        protocol=read(component[key]);folder=Path(protocol['directory'])
        assert folder.is_relative_to(ROOT/'runs')
        for p in folder.iterdir():
            if p.is_file():bind(p)
    for name in ['current_biwn_evidence_v2.py','chat_tools_current_v2.py']:bind(ROOT/name)
    bind(Path(__file__))
    difference_path=Path(review['directory'])/'final-RAM-and-CPU-difference-diagnostic.json';difference=read(difference_path)
    assert difference['different_final_RAM_bytes']==7 and not difference['unclassified_addresses']
    bind(difference_path)
    obs=review['candidate_observations']
    assert obs['geometry_entries']==obs['geometry_native_entries']==obs['geometry_returns']==obs['geometry_early']==1
    assert obs['geometry_inside']==obs['geometry_last_outside']==obs['geometry_errors']==obs['geometry_stack_outside']==0
    summary=(
        'The latest experimental BIWN disc uses 17,084 bytes of compiled game code in a 20,480-byte reservation. '
        'Its complete boundary routine passed 1,376 stable and 256 changing-coordinate comparisons of full CPU state, public RAM and ordered accesses, plus 96 startup cases. '
        'Two fresh 24,978-frame merchant/media/outdoor routes completed. The compiled routine ran once on an early-return path and passed live register/flags/stack checks; its other paths remain component-test coverage. '
        'The same-layout original-entry control matched video, navigation, GPU/DSP state and captured PCM, with one differing CPU frame and differing RAM hashes. '
        'These routes use retained emulator processors and platform services. The separate C-processor test applies to the preceding 16,872-byte cache disc. '
        'Local Author and repair drafts both failed; the coordinator removed one unused declaration from the repair and supplied the ABI, checks and integration. '
        'No whole-game source rebuild, physical-console readiness, whole-game speedup, new weight training or native Chat-window generation is established.')
    facts=dict(project='Black Ice White Noise, Atari Jaguar CD',recorded_at=now.isoformat(),checked_current_summary=summary,
        experimental_build=dict(name='native boundary disc',resident_bytes=17084,reserved_bytes=20480,heap_start=hex(build['heap_start']),
                                derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256']),
        component_verification=dict(original_entry='0x1028E',native_bytes=212,stable_cases=1376,changing_coordinate_cases=256,
                                    original_instruction_coverage=[18,18],startup_cases=96,private_stack_bytes=48,
                                    scope='Full CPU/registers/SR/stack banks/public RAM and ordered accesses; private scratch/code/entry excluded. Controlled RAM only; no arbitrary alias/fault/IRQ/physical timing proof.'),
        gameplay_comparison=dict(candidate_frames=24978,control_frames=24978,compiled_boundary_calls=1,live_early_returns=1,
                                 live_inside_returns=0,live_final_bound_returns=0,inside_and_final_bound_paths_component_only=True,
                                 restored_control_entry_bytes=8,video_equal=True,navigation_equal=True,GPU_DSP_state_equal=True,
                                 PCM_byte_equal=True,CPU_different_frames=1,full_RAM_different_frames=diffs['full_RAM_sha256'],
                                 final_RAM_different_bytes=7,final_RAM_differences_confined_to_declared_entry_or_private_window=True,CPU_different_frame_numbers=[x['frame']for x in difference['CPU_changed_frames']],exact_whole_state_equivalence=False,processors='Retained native emulator CPU/GPU/DSP/IRQ and platform services'),
        local_authorship=dict(actual_model_calls=3,model='local 27B base',roles=['Author','Reviewer','one repair Author'],
                              raw_first_draft_pass=False,raw_repair_pass=False,reviewer_missed_byte_offset_error=True,
                              coordinator_C_edits=1,coordinator_edit='Removed one unused pointer declaration; no access/control-flow expression edits.',
                              ABI_and_verifiers_and_integration='Coordinator',accepted_unchanged_local_output=False,independent_review=False),
        report=review['report'],component_report=component['report'],prompts_and_responses=component['transcript'],
        whole_game_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,
        new_training=False,default_promoted=False,native_Chat_verified=False,
        remaining_work=['Complete readable game and original-console source rebuild','Broader scenes/paths, timing and physical-console/audio checks',
                        'Verify native LM Studio Chat display','Advertising semantic source-review reliability and training evaluation',
                        'Complete migration preparation and test the future 256GB hardware profile'])
    pub=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=now.isoformat(),
             facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,
             scope='Scopedpublication supersedes v2collector attempt whosecleanup pointer was mistakenly treatedasa runfolder. No live configurationusedthatattempt. Completed native boundary-disc evidence only. Live job observation is added separately at read time. Historical source/receipts unchanged.')
    save(out/'publication.json',pub);save(v/'current-biwn-latest-publication-current.json',pub)
    print(json.dumps(dict(status=pub['status'],directory=str(out),bound_files=len(deps),snapshotted_pointers=len(aliases))),flush=True)


if __name__=='__main__':
    main()

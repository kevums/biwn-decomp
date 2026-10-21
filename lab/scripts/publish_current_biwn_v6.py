"""Publish reviewed complete102C4 scanner facts without preview promotion."""
import argparse,hashlib,json,shutil,os
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--review',type=Path,default=ROOT/'verification/native-geometry-scan-live-reviewed-current.json');args=parser.parse_args()
    rp=args.review.resolve();review=read(rp)
    assert rp.is_relative_to(ROOT/'verification')
    assert review['status']=='terminal_native_geometry_scan_two_live_routes_reviewed' and review['live_monitor_pass']
    bp=Path(review['build']);build=read(bp);assert sha(bp)==review['build_sha256']
    gp=Path(build['component_gate']);gate=read(gp);assert sha(gp)==build['component_gate_sha256']
    assert gate['source_accepted'] and gate['status'].endswith('_CPU_RAM_ordered_pass')
    assert gate['source_sha256']==sha(gate['source'])
    assert review['derived_disc_sha256']==build['derived_disc_sha256']
    obs=review['candidate_observations'];control=review['control_observations']
    assert obs['scan_entries']==obs['scan_returns']==obs['scan_native_entries'] and obs['scan_entries']>0
    assert obs['scan_errors']==obs['scan_pending']==obs['scan_stack_outside']==0
    assert control['scan_entries']==control['scan_returns'] and control['scan_errors']==0
    attempts=[read(ROOT/'verification'/n)for n in ['local-native-geometry-scan-author-current.json','local-native-geometry-scan-repair-current.json','local-native-geometry-scan-q3-current.json']]
    assert not attempts[0]['raw_kernel_gate_pass'] and not attempts[1]['raw_repair_gate_pass'] and not attempts[2]['raw_kernel_gate_pass']
    now=datetime.now(timezone.utc);out=ROOT/'verification/current-biwn-latest-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(p,expected=None):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);q=p
        if p.name.endswith(('-current.json','-active.json')):
            q=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:16]+'-'+p.name);shutil.copy2(p,q);aliases[str(p)]=str(q)
        deps[str(q)]=h
    for p,h in review['dependencies_sha256'].items():bind(p,h)
    for p in [rp,bp,gp,Path(__file__),ROOT/'current_biwn_evidence_v2.py',ROOT/'current_biwn_evidence_v4.py',ROOT/'chat_tools_current_v4.py',ROOT/'scripts/ask_biwn_current_status_v8.py',ROOT/'biwn_status_brevity_v5.py']:bind(p)
    for d in attempts:
        folder=Path(d['directory'])
        for p in folder.iterdir():
            if p.is_file():bind(p)
    differences=review['same_layout_differences'];same_length=review['candidate_frames']==review['control_frames'];media_equal=review['PCM_equal'] and differences['video_sha256']==0
    count=build['linked_component_bytes'];stable=gate['native_cases'];changing=gate['changing_coordinate_cases']
    summary=(f'The latest published experimental scanner disc contains {count:,} resident bytes in the unchanged {build["component_bytes"]:,}-byte reservation. '
      f'The complete original102C4 reverse scanner passed {stable:,} stable and {changing:,} changing-read full CPU/public-RAM/ordered-access component cases, final-address checks and {build["entry_cases"]} startup cases. '
      f'Both fresh gameplay runs completed {review["candidate_frames"]:,}/{review["control_frames"]:,} frames and returned outdoors using retained emulator processors and platform services. '
      f'The compiled scanner ran {obs["scan_entries"]} times ({obs["scan_successes"]} success and {obs["scan_failures"]} failure returns) with live register/flags/object-write/task-stack checks passing. Unreached return paths remain component-only. '
      f'Video differences: {differences["video_sha256"]} frames; PCM equal: {review["PCM_equal"]}; CPU differences: {differences["CPU_full"]} frames. Full per-frame equivalence and physical timing are not established. '
      'All three raw local Author candidates failed, and the same-weight reviews were unreliable. The accepted C/ABI/checks/integration are coordinator work; no local generated C was adopted and no weights changed. '
      'Each C-processor job is added separately with its own disc identity; no preceding-disc result proves this scanner disc. Full readable game and original-console source rebuild remain unfinished. No preview promotion, whole-game speedup, physical-console readiness or native Chat-window generation is established.')
    facts=dict(project='Black Ice White Noise, Atari Jaguar CD',recorded_at=now.isoformat(),checked_current_summary=summary,
      experimental_build=dict(name='native complete reverse geometry scanner',resident_bytes=count,reserved_bytes=build['component_bytes'],heap_start=hex(build['heap_start']),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256']),
      component_verification=dict(original_entry='0x102C4',native_bytes=gate['binary_bytes'],stable_cases=stable,changing_read_cases=changing,original_instruction_coverage=gate['original_instruction_coverage'],startup_cases=build['entry_cases'],private_stack_bytes=gate['max_private_stack_bytes'],source=gate['source'],scope='Full native CPU/registers/SR/stack banks/public RAM plus ordered accesses, including tagged object/header/record pointers and changing reads. Original register-save/private scratch/code/entry exclusions apply. No arbitrary alias/fault/IRQ or physical timing proof.'),
      gameplay_comparison=dict(candidate_frames=review['candidate_frames'],control_frames=review['control_frames'],compiled_scanner_calls=obs['scan_entries'],live_success_returns=obs['scan_successes'],live_failure_returns=obs['scan_failures'],unreached_paths_component_only=True,live_monitor_pass=True,video_equal=differences['video_sha256']==0,navigation_equal=differences['navigation']==0,GPU_DSP_state_equal=differences['full_GPU_state_sha256']==differences['full_DSP_state_sha256']==0,PCM_byte_equal=review['PCM_equal'],CPU_different_frames=differences['CPU_full'],full_RAM_different_frames=differences['full_RAM_sha256'],all_field_difference_counts=differences,frame_counts_equal=same_length,exact_whole_state_equivalence=same_length and not any(differences.values())and review['PCM_equal'],timing_disagreement_unresolved=not media_equal,processors='Retained native emulator CPU/GPU/DSP/IRQ and platform services'),
      local_authorship=dict(actual_model_calls=5,model='local27Bbase and Qwen3CoderNext GGUF Q3_K_XL',roles=['Author','Reviewer','one repair Author','Reviewer of repair','fresh coder Author'],raw_first_draft_pass=False,raw_repair_pass=False,raw_fresh_coder_pass=False,raw_candidates_attempted=3,raw_candidates_passed=0,accepted_unchanged_local_output=False,accepted_C='Coordinator implementation',ABI_and_verifiers_and_integration='Coordinator',same_weight_reviews_unreliable=True,independent_review=False,source_history='The27Bfirst draft failed ordered access case0; its one repair failed CPU/RAM case0. A fresh coder response to the exact original task failed ordered access case0. Same-weight reviewers were unreliable, including an empty schema-valid review. Selected search/layout/helper/ABI/checks/integration are coordinator work. Different models/quantizations on one development task do not establish a ranking or training gain.'),
      report=review['report'],component_proof=str(gp),prompts_and_responses=str(ROOT/'reports/native-geometry-scan-prompts-and-responses.txt'),prediction_index=str(ROOT/'reports/native-geometry-scan-prediction-index.json'),
      whole_game_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,new_training=False,default_promoted=False,native_Chat_verified=False,
      remaining_work=['Resolve timing/scene/audio disagreements and broaden coverage','Complete readable game and original-console source rebuild','Verify native LM Studio Chat display','Advertising semantic source-review reliability and training evaluation','Full migration preparation and future256GB hardware verification'])
    publication=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=now.isoformat(),facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,scope='Newest reviewed complete102C4 scanner experiment, including disagreements and coordinator authorship. Publication is a factual status update, not default preview promotion. Named processor-job state is added separately at read time.')
    save(out/'publication.json',publication)
    destination=ROOT/'verification/current-biwn-latest-publication-current.json';temporary=destination.with_name('.current-biwn-publication-v6.tmp.json')
    save(temporary,publication);os.replace(temporary,destination)
    print(json.dumps(dict(status=publication['status'],directory=str(out),bound_files=len(deps),resident_bytes=count)),flush=True)
if __name__=='__main__':main()

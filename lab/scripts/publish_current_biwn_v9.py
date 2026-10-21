"""Publish the reviewed18888byte native routes with inherited limits and attribution."""
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';rp=v/'native-interior-live-reviewed-current.json';review=read(rp)
    assert review['status']=='terminal_native_interior_two_live_routes_reviewed' and review['live_monitor_pass']
    bp=Path(review['build']);build=read(bp);assert sha(bp)==review['build_sha256']
    gp=Path(build['component_gate']);gate=read(gp);assert sha(gp)==build['component_gate_sha256'] and gate['source_accepted']
    assert gate['stable_cases']==1958 and gate['changing_cases']==768
    dp=v/'native-interior-development-reviewed-current.json';dev=read(dp)
    assert not dev['accepted_local_body_edited'] and dev['actual_model_predictions']==4
    pp=v/'native-geometry-scan-corrected-live-reviewed-current.json';parent=read(pp)
    assert not parent['PCM_equal'] and parent['same_layout_differences']['video_sha256']>0
    cp=v/'interior-C-runtime-reviewed-current.json';provider=read(cp)
    assert provider['status']=='terminal_interior_C_provider_components_reviewed' and provider['atomic_cases']==100224
    obs=review['candidate_observations'];original=review['control_observations']
    assert obs['interior_kind_entries']==original['interior_kind_entries']==[14,1]
    assert obs['interior_kind_successes']==[14,0] and obs['interior_kind_failures']==[0,1] and obs['interior_skips']==1
    now=datetime.now(timezone.utc);out=v/'current-biwn-latest-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p)
        target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for data in [review,dev,parent,provider]:
        for p,h in data['dependencies_sha256'].items():bind(p,h)
    for p in [rp,bp,gp,dp,pp,cp,Path(__file__),ROOT/'current_biwn_evidence_v7.py',ROOT/'chat_tools_current_v7.py',
              ROOT/'scripts/ask_biwn_current_status_v12.py',ROOT/'biwn_status_brevity_v5.py']:bind(p)
    differences=review['same_layout_differences']
    coverage=('Actor10520 reached14success returns and0failure returns live. Sprite105DA reached0success returns and1failure return, '
              'which skipped its scan. Actor failure paths, sprite successful selection and sprite non-skipped search failures remain component-test coverage.')
    summary=('The latest published experimental disc contains18888resident bytes in the unchanged20480byte reserve. The shared616byte '
             'native actor/sprite selector passed1958stable+768changing-read originalCPU/publicRAM/ordered cases at its final address and96startup cases. '
             'Two fresh routes each completed24996frames and returned outdoors using retained native emulator processors/platform services. '+coverage+
             ' The read-only monitor has zero reported errors/pending/stack-outside; candidate private depth100bytes/minimum606byte headroom. '
             'Audio matches the control that restores only10520/105DAentries; video, navigation and CPU/GPU/RAM snapshots differ, so timing/full-state '
             'equivalence remains unproved. Prior compiled functions remain in the control, including the scanner with inherited original-entry '
             'video/audio/timing discrepancies. The accepted C body is unchanged local27B output after one guided repair, with coordinator ABI/contract/'
             'layout/verifiers/integration; scalar helpers remain a prompt-compliance limitation. Same-weight Reviewers missed defects; no new weights '
             'or independent review. The new provider passed100224atomic checks and four complete-function suites; its exact18888disc C-processor '
             'route is observed separately. Older four terminal C-route results apply only to their own discs. Full readable game/console rebuild remains unfinished; preview unchanged.')
    facts=dict(project='Black Ice White Noise, Atari Jaguar CD',recorded_at=now.isoformat(),checked_current_summary=summary,
      experimental_build=dict(name='native local-model interior actor/sprite selectors10520/105DA',resident_bytes=18888,
        reserved_bytes=20480,heap_start=hex(build['heap_start']),reservation_free_bytes=1592,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256']),
      component_verification=dict(original_entries=['0x10520','0x105da'],native_bytes=616,stable_cases=1958,changing_read_cases=768,
        original_instruction_coverage=[99,99],startup_cases=96,private_stack_bytes=100,source=gate['source'],
        scope='FullD/A/PC/SR/USP/SSP/publicRAM and logical ordered width/value accesses; native/tracer RAM agreement, dense32768records, flags/tags/overlaps and controlled changing reads. Private8KBstack/code/entry exclusions; no arbitraryfault/IRQ/physicaltiming proof.'),
      live_path_coverage=coverage,
      gameplay_comparison=dict(candidate_frames=24996,control_frames=24996,compiled_interior_calls=15,
        actor_success_returns=14,actor_failure_returns=0,sprite_success_returns=0,sprite_failure_returns=1,sprite_skipped_scans=1,
        live_success_returns=14,live_failure_returns=1,per_kind_unreached_paths_component_only=True,live_monitor_pass=True,
        video_equal=False,navigation_equal=False,PCM_byte_equal=True,CPU_different_frames=differences['CPU_full'],
        full_RAM_different_frames=differences['full_RAM_sha256'],all_field_difference_counts=differences,frame_counts_equal=True,
        exact_whole_state_equivalence=False,timing_disagreement_unresolved=True,
        control_scope='Only10520/105DAentries restored; prior doorway/geometry functions remain compiled in both, not the unmodified game',
        processors='Retained native emulator CPU/GPU/DSP/IRQ/platform services'),
      inherited_parent_limits=dict(build_resident_bytes=17812,original_entry_comparison='Scanner102C4 compiled versus original-scanner entry',
        candidate_frames=parent['candidate_frames'],control_frames=parent['control_frames'],video_equal=False,PCM_byte_equal=False,
        unresolved_timing_state_media_disagreement=True,latest_selector_control_does_not_resolve_parent=True,report=parent['report']),
      local_authorship=dict(actual_model_calls=4,model='local27Bbase advertising-scholar,32K/oneworker',
        roles=['Author','same-weight Reviewer','one guided repair Author','same-weight Reviewer'],raw_candidates_attempted=2,
        raw_candidates_passed=1,raw_first_draft_pass=False,raw_repair_pass=True,accepted_unchanged_local_output=True,
        accepted_function_entries=['0x10520','0x105da'],accepted_C='Unedited repaired local Author native kernel',
        ABI_and_verifiers_and_integration='Coordinator',same_weight_reviews_unreliable=True,independent_review=False,
        format_limit=dev['format_normalization'],prompt_compliance_limit=dev['prompt_compliance_limit'],
        source_history='First draft failed unclosed-fence compilation; coordinator source findings guided the one repair. Body unchanged after fence removal. Reference/fixture values withheld. Supported development task, no model ranking/training gain.'),
      C_provider_components=dict(instruction_locations=provider['instruction_locations'],atomic_cases=100224,function_cases=provider['function_cases'],
        gameplay_verdict_separate=True,report=provider['report']),
      report=review['report'],component_proof=str(gp),prompts_and_responses=dev['transcript'],prediction_index=dev['prediction_index'],
      whole_game_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,new_training=False,
      default_promoted=False,native_Chat_verified=False,
      remaining_work=['Complete new exact18888disc C-processor gameplay comparison and broaden paths',
        'Resolve inherited and current timing/state/media discrepancies','Complete readable game/original-console source rebuild',
        'Verify current native LM Studio Chat interaction; historical local-role display exists',
        'Advertising source-review/teaching reliability and adaptation evaluation','Full workbench migration/future256GB hardware verification'])
    result=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=now.isoformat(),
                facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,
                scope='Latest reviewed18888native selector gameplay and inherited limits. Named processor jobs are added independently at read time. No preview promotion.')
    save(out/'publication.json',result);destination=v/'current-biwn-latest-publication-current.json'
    if destination.exists():shutil.copy2(destination,out/'previous-publication.json')
    temporary=v/'.current-biwn-publication-v9.tmp.json';save(temporary,result);os.replace(temporary,destination)
    print(json.dumps(dict(status=result['status'],resident_bytes=18888,bound_files=len(deps))))


if __name__=='__main__':main()

"""Add pending C-chain and reviewed cold-restore facts without promoting gameplay."""
import copy
import hashlib
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import json


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';pointer=v/'current-biwn-latest-publication-current.json';previous=read(pointer)
    assert previous['facts']['experimental_build']['resident_bytes']==28380
    chain=read(v/'actor-chain-development-reviewed-current.json');cold=read(v/'cold-runtime-model-reviewed-current.json')
    assert chain['status']=='terminal_source_owned_actor_chain_component_startup_pass_gameplay_pending'
    assert cold['copied_model_final_responses']==2 and cold['default_model_restored']
    out=v/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for name,obj in[('previous-publication.json',previous),('chain-development.json',chain),('cold-restore.json',cold)]:save(out/name,obj)
    facts=copy.deepcopy(previous['facts']);facts['recorded_at']=datetime.now(timezone.utc).isoformat()
    facts['checked_current_summary']=facts['checked_current_summary'].replace('The latest experimental disc','The latest gameplay-tested experimental disc',1)+' A newer28,448byte source-owned movement/collision C-chain development build passes7,680prototype and7,680final cases/all301sites,15,360context executions and96startup cases. Its maxprivate564/minfixtureheadroom354 replaces prior894/24; actualgameplay with a newmonitor remains pending. This refactors already-recovered functions,not additional gamefunction recovery. A real cold-moved package passes7of18toolkinds/4origin-integrity controls; bothcopiedmodelweights load and produce finalresponses when thecopiedmodeldefinitions areused. Rawweight-folder profiles returned reasoningonly; configuredoutputs2.61/2.85seconds. TheReviewer missed two-sentenceformat and Researchercausalwordingneedsqualification; noqualitygain. Daily32Kmodelrestored; nativeChat/fullrestore/offmachine/futurehardwareunfinished.'
    facts['next_component_development']=dict(status=chain['status'],latest_built_resident_bytes=28448,latest_gameplay_tested_resident_bytes=28380,gameplay_frames=0,prototype_cases=7680,final_address_cases=7680,original_instruction_sites=301,context_executions=15360,physical_helper_context_checks=8969,virtual_collision_context_checks=1094,max_native_private_depth=564,minimum_fixture_task_headroom=354,prior_max_private_depth=894,prior_minimum_fixture_headroom=24,startup_cases=96,reserved_bytes=28544,free_reserved_bytes=96,heap_floor_unchanged=True,source_owned_C_between=['0x13c9a','0x13b5a','0x13bb0'],remaining_original_physical_helpers=['0x13440','0xe220','0x1039c','0x102c4','0x1028e','0x10652'],additional_functions_recovered=False,source_authorship='Coordinator C ABI/refactor/fixtures/monitors; no newlocalAuthor output or weights',normalized_build=chain['normalized_build'],report=chain['report'],scope='Finite original-facing contract and shared-C-context refactor. Virtual internal collision entry is shadowCPUcomparison,not physical C-ABI equality. OnlyE220effects prescribed in movementfixtures. Fresh realgameplay/newsharedcontextmonitor pending; no currentpreviewpromotion or transfer of oldgameplay/processor receipts.')
    facts['migration_progress']=dict(package=cold['package'],same_host_different_root=True,cold_move_verified=True,registered_tools=18,tested_tool_kinds=7,boundary_controls=4,original_tree_fallback=False,cloned_files=cold['cloned_files'],preserved_symlinks=14,package_logical_bytes=cold['logical_bytes'],model_files_copied=39,model_weight_shards_verified=10,copied_model_loads=2,copied_model_final_responses=2,copied_model_context_length=8192,current_daily_context_length=32768,current_daily_restored=True,raw_directory_profile_final_responses=0,raw_directory_profile_reasoning_only_tokens=399,copied_definition_profile_prediction_seconds=[2.61,2.85],quality_gain_demonstrated=False,Reviewer_format_limit_failed=True,Researcher_causal_wording_needs_qualification=True,SDK_control_client='Originalworkbench,not copied PythonSDK',copied_SDK_or_full_CLI_workflows_verified=False,all_tools_behavior_verified=False,full_workbench_restored=False,training_runtime_restored=False,native_Chat_verified=False,off_machine_restore_verified=False,future_hardware_verified=False,canonical_publication_snapshot_resident_bytes=26220,report=cold['report'],scope='Actual bundledPython/venv/MCP/index pathrepair after relocating package outsideworkbench,7toolkinds/4boundarycontrols. Selecteddailybase+trainedReviewer39resources/10shards fullyhashchecked aftercopy; bothloadedviatemporaryLMStudioaliases resolvingcopiedweights. Configuredcopieddefinitionsenablefinalresponses; rawprofilefailureandtasklimitsretained. Temporarybindingsremoved; dailybase32K/1workerrestored. No fullCLI/toolchain/training/onboarding/sourcebuild or offmachine/futurehardware proof.')
    deps=dict(previous['dependencies_sha256'])
    for obj in[chain,cold]:
        for p,h in obj['dependencies_sha256'].items():
            assert Path(p).resolve().is_relative_to(ROOT)and sha(p)==h,p
            assert p not in deps or deps[p]==h,p
            deps[p]=h
    for p in[Path(__file__),*out.glob('*.json')]:deps[str(p)]=sha(p)
    snapshots=out/'snapshots';snapshots.mkdir();aliases=[]
    for name,h in list(deps.items()):
        p=Path(name)
        if p.name.endswith(('-current.json','-active.json')):
            assert sha(p)==h,name
            target=snapshots/(hashlib.sha256(name.encode()).hexdigest()[:12]+'-'+p.name);target.write_bytes(p.read_bytes());del deps[name];deps[str(target)]=h;aliases.append(dict(original=name,snapshot=str(target),sha256=h))
    for p,h in deps.items():assert sha(p)==h,p
    result=dict(status=previous['status'],schema_version=2,directory=str(out),recorded_at=facts['recorded_at'],facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,scope=__doc__+' Latestgameplaytested28380; new28448Cchainpendinggameplay. Coldcanonicalpublication26220ishistorical. Fullfourpartgoalremainsactive.')
    save(out/'publication.json',result);save(pointer,result)
    print(json.dumps(dict(status=result['status'],published_gameplay_bytes=28380,pending_development_bytes=28448,bound_files=len(deps),goal_complete=False)))


if __name__=='__main__':main()

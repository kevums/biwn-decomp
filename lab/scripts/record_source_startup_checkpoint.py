"""Publish source startup CPU proof, preserving device/scheduler boundaries."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/startup-source-fullCPU-checks.json');raw=Path(proof['directory']);assert read(raw/'status.json')['status']=='terminal_pass'
    assert proof['cases']==8 and proof['source_caller_coverage']==[82,82]and not proof['remaining_caller_scripts']
    assert proof['source_task_creations_per_case']==19 and proof['contexts_after_startup']==21
    assert proof['disc_requests_per_case']==[12]*8 and proof['disc_bytes_per_case']==[758846]*8
    assert not proof['startup_snapshot_removed']and not proof['source_GPU_context_or_scanout_compared']
    assert proof['test_script_sha256']==sha(ROOT/'scripts/check_biwn_startup_display_cpu.py')
    assert proof['imported_checker_sha256']==sha(ROOT/'scripts/check_biwn_startup_rng_cpu.py')
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in proof['source_sha256'].items():assert sha(source/n)==digest
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);now=datetime.now(timezone.utc);out=ROOT/'verification/source-startup-CPU-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[Path(__file__),ROOT/'scripts/check_biwn_startup_display_cpu.py',ROOT/'scripts/check_biwn_startup_rng_cpu.py',ROOT/'scripts/generate_biwn_static_factory_cpu.py',ROOT/'scripts/generate_biwn_startup_HUD_cpu.py',session/'static-factory-fullCPU-generation.json',session/'startup-HUD-fullCPU-generation.json',ROOT/'verification/startup-source-fullCPU-checks.json',raw/'cases.json',raw/'coverage.json',raw/'report.json',raw/'status.json',raw/'compiler.txt',raw/'libstartup-display-cpu.dylib',ROOT/'scripts/biwn_disc_backend.py']
    files.extend(source/n for n in proof['source_sha256'])
    for row in read(raw/'cases.json'):
        p=Path(row['final_RAM_path']);assert sha(p)==row['RAM_sha256'];files.append(p)
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    cp=dict(recorded_at=now.isoformat(),status='standalone_source_startup_CPU_verified',audit=str(out),report=str(raw/'report.json'),cases=8,caller_instruction_coverage=[82,82],source_task_creations_per_case=19,contexts_after_startup=21,disc_requests_per_case=12,disc_bytes_per_case=758846,no_reached_game_helper_ABI_scripts=True,remaining_game_helper_scripts=[],BIOS_and_completion_adapters=['0x303c','0x3042','0xdf60'],full_CPU_SR_USP_SSP_private_RAM_TOM_blitter_and_ordered_bus_match=True,source_helper_coverage=proof['source_helper_coverage'],initial_Frozen_RAM_two_context_ring_freepool_and_CPU_supplied=True,source_modal_11E6C_branch_reached=False,actual_startup_scheduler_switching_verified=False,isolated_sprite_GPU_reset_reseed_provider=True,inherited_GPU_DSP_state_compared=False,earlier_startup_capture_still_supplied_to_connected_game=True,connected_loading_movie_world_changed=False,source_boot_verified=False,playable_rebuilt_game=False,native_Chat_verified=False,new_training=False,model_defaults_changed=False,new_published_components=0,authorship='Coordinator-authored184 static-factory and572 HUD fixed CPU blocks plus integration tests; no local-model code authorship or new training.',
        checked_answer='Separate source-startup proof:8 cases run17C40->17DC2 with all82 caller instructions and every reached game helper as source/C code, including RNG, clear/display, scene/player/static-object initialization and both HUD helpers. No reached game-helper ABI scripts remain.19 actual creations per case form21 contexts;12 file-backed transfers total758846 bytes per case. Original CPU, independent Unicorn and C match allCPU/flags/stack banks, full2MBRAM/privateframes, TOM display/blitter state, ordered CPU bus and disc transfers. Supplied FrozenRAM/two-context/freepool/CPU, emulatedbuttons with modalbit0 clear, BIOS303C/3042 and synchronous completion/RTS atDF60 remain. Isolated sprite GPUreset/reseed and shared synchronous blitter are device fixtures. Actual scheduler switching, inheritedGPU/DSP context, sourceDD40/system/globalboot/firmware/physicalscanout/playability remain unverified. This standalone startup is not linked to the later loading/movie/world run; its earlier startup capture is still supplied.',
        next_step='Use retained full-state sprite GPU/source GPU-DSP initialization, replace startup DF60 completion adapter with source scheduler continuations, and connect source startup into the loading/movie/world run. Implement modal11E6C and sourceDD40/system/globalboot as needed.')
    save(out/'checkpoint.json',cp);save(out/'manifest.json',manifest);save(ROOT/'verification/source-startup-CPU-checkpoint.json',cp)
    summary=session/'emulator-runtime/summary.json';data=read(summary);data['source_startup_CPU_checkpoint']=cp;save(summary,data)
    p=ROOT/'CURRENT DECOMPILATION.txt';p.write_text('LATEST SOURCE STARTUP CPU CHECK\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAUTHORSHIP\n'+cp['authorship']+'\n\nAUDIT\n'+str(out)+'\n\nNEXT\n'+cp['next_step']+'\n\nEARLIER CHECKPOINTS\n'+p.read_text())
    print(json.dumps({k:cp[k]for k in ['status','audit','cases','source_task_creations_per_case','disc_requests_per_case','disc_bytes_per_case','earlier_startup_capture_still_supplied_to_connected_game']}))
if __name__=='__main__':main()

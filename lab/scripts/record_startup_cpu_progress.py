"""Publish standalone startup progress separately from connected game proof."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    caller=read(ROOT/'verification/startup-caller-fullCPU-checks.json');rng=read(ROOT/'verification/startup-RNG-fullCPU-checks.json')
    assert caller['cases']==8 and caller['source_caller_instruction_coverage']==[82,82]and caller['actual_source_task_creations']==128
    assert rng['cases']==56 and rng['source_RNG_instruction_coverage']==[123,144]
    for report in [caller,rng]:
        assert read(Path(report['directory'])/'status.json')['status']=='terminal_pass'
        assert report['full_2MB_RAM_compared_without_masks']and report['all_CPU_registers_SR_USP_SSP_compared']and report['ordered_bus_compared_to_independent_Unicorn']
        assert not report['startup_snapshot_removed']and not report['whole_game_complete']
        assert report['test_script_sha256']==sha(ROOT/'scripts/check_biwn_startup_rng_cpu.py')
        for name,digest in report['source_sha256'].items():assert digest==sha(ROOT/'projects/black-ice-white-noise/restoration'/name)
    now=datetime.now(timezone.utc);out=ROOT/'verification/startup-CPU-progress-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[Path(__file__),ROOT/'scripts/check_biwn_startup_rng_cpu.py',ROOT/'scripts/generate_biwn_startup_cpu.py',ROOT/'verification/startup-caller-fullCPU-checks.json',ROOT/'verification/startup-RNG-fullCPU-checks.json']
    source=ROOT/'projects/black-ice-white-noise/restoration';files.extend(source/n for n in caller['source_sha256'])
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);files.append(session/'startup-fullCPU-generation.json')
    for report in [caller,rng]:
        directory=Path(report['directory']);files.extend(directory/n for n in ['cases.json','coverage.json','report.json','status.json','compiler.txt','libstartup-rng-cpu.dylib'])
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    cp=dict(recorded_at=now.isoformat(),status='standalone_startup_CPU_progress_verified',audit=str(out),authorship='Coordinator-authored static C and tests; no local model code authorship or new training.',caller_report=caller['directory'],RNG_report=rng['directory'],caller_cases=8,caller_instruction_coverage=[82,82],source_task_creations_per_case=16,source_task_creations_total=128,RNG_cases=56,RNG_instruction_coverage=[123,144],RNG_uncovered_instructions=21,full_CPU_SR_USP_SSP_and_2MB_RAM_no_masks=True,ordered_bus_matches_independent_Unicorn=True,original_CPU_or_GPU_execution_on_C_path=False,scripted_caller_helpers=caller['scripted_helper_providers'],earlier_startup_capture_still_supplied=True,connected_loading_movie_world_changed=False,source_boot_verified=False,playable_rebuilt_game=False,native_Chat_verified=False,new_training=False,model_defaults_changed=False,new_published_components=0,
        checked_answer='Separate startup progress: 56 RNG cases match original CPU and independent Unicorn; 123 of144 generated RNG instructions reached. Startup caller17C40->17DC2 matches all82 instructions in8 cases, including16 actual source task creations per case (128 total). All registers/flags/stack banks and full2MBRAM/private frames match without masks, as do ordered bus accesses. Eight caller helpers remain ABI scripts. This is a standalone test with supplied two-context ring/freepool, not continuous boot or removal of the startup capture. The connected loading/movie/world run still uses its earlier startup capture. Full boot/playability and visible native Chat remain unverified.',
        next_step='Replace the eight standalone helper providers with full-CPU source bodies, connect real startup loading/scheduling, then compare continuous startup-to-movie/world before removing the capture.')
    save(out/'checkpoint.json',cp);save(out/'manifest.json',manifest);save(ROOT/'verification/startup-CPU-progress-checkpoint.json',cp)
    summary_path=session/'emulator-runtime/summary.json';summary=read(summary_path);summary['standalone_startup_CPU_checkpoint']=cp;save(summary_path,summary)
    p=ROOT/'CURRENT DECOMPILATION.txt';p.write_text('LATEST SEPARATE STARTUP CPU CHECK\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAUTHORSHIP\n'+cp['authorship']+'\n\nAUDIT\n'+str(out)+'\n\nNEXT\n'+cp['next_step']+'\n\nCONNECTED GAME CHECKPOINT (UNCHANGED)\n'+p.read_text())
    print(json.dumps(cp))
if __name__=='__main__':main()

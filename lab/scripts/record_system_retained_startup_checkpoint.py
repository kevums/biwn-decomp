"""Publish DD40 first handoff -> source startup with retained GPU/DSP."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/system-startup-retained-GPU-checks.json');raw=Path(proof['directory']);system=read(ROOT/'verification/system-source-bootstrap-checks.json');sysraw=Path(system['directory'])
    assert read(raw/'status.json')['status']==read(sysraw/'status.json')['status']=='terminal_pass'
    assert proof['cases']==2 and proof['sprite_requests_per_case']==[5,5]
    assert not proof['initial_context_ring_or_freepool_supplied']and proof['source_initial_freepool_records']==100 and proof['source_freepool_records_remaining']==80
    assert proof['source_system_DD40_DDCC_first_handoff_verified']and not proof['source_startup_scheduler_verified']and not proof['intermediate_GPU_reset_or_reseed']
    assert system['cases']==4 and system['source_instruction_coverage']==[37,38]
    assert proof['test_script_sha256']==sha(ROOT/'scripts/check_biwn_startup_retained_GPU.py')and system['script_sha256']==sha(ROOT/'scripts/check_biwn_system_cpu.py')
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in proof['source_sha256'].items():assert sha(src/n)==digest
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);now=datetime.now(timezone.utc);out=ROOT/'verification/system-retained-startup-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[Path(__file__),ROOT/'scripts/check_biwn_startup_retained_GPU.py',ROOT/'scripts/check_biwn_system_cpu.py',ROOT/'scripts/generate_biwn_system_cpu.py',session/'system-fullCPU-generation.json',ROOT/'verification/system-startup-retained-GPU-checks.json',ROOT/'verification/system-source-bootstrap-checks.json']
    for directory in [raw,sysraw]:files.extend(directory/n for n in ['report.json','status.json','cases.json','compiler.txt']);files.extend(directory.glob('*.dylib'));files.extend(directory.glob('*.bin'))
    files.extend(src/n for n in proof['source_sha256']);files.extend(src/n.replace('.c','.h')for n in proof['source_sha256'])
    files.extend([ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-retained-interior-render-device.dylib',ROOT/'scripts/biwn_disc_backend.py',ROOT/'scripts/check_biwn_continuous_loading_movie_world.py'])
    manifest=[]
    for i,p in enumerate(files):
        assert p.exists(),p;target=out/f'{i:03d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    cp=dict(recorded_at=now.isoformat(),status='system_first_handoff_source_startup_retained_GPU_DSP_verified',audit=str(out),report=str(raw/'report.json'),cases=2,source_system_first_handoff_verified=True,source_system_standalone_cases=4,source_system_instruction_coverage=[37,38],source_freepool_records=100,source_freepool_records_remaining=80,source_render_context_creation_verified=True,source_startup_task_creations=19,source_total_task_creations_including_render=20,contexts_after_startup=21,sprite_requests_per_case=5,disc_requests_per_case=12,disc_bytes_per_case=758846,no_reached_game_helper_ABI_scripts=True,initial_context_ring_freepool_or_startup_capture_supplied=False,initial_Frozen_RAM_CPU_supervisorstack_and_processor_setup_supplied=True,source_startup_scheduler_switching_verified=False,synchronous_DF60_completion_RTS_adapter=True,intermediate_GPU_reset_or_reseed=False,full_CPU_RAM_logical_GPU4396_DSP8496_peripheral_disc_and_GPU_trace_match=True,earlier_startup_capture_still_supplied_to_connected_game=True,connected_loading_movie_world_changed=False,source_boot_verified=False,playable_rebuilt_game=False,native_Chat_verified=False,new_training=False,model_defaults_changed=False,new_published_components=0,authorship='Coordinator-authored source system CPU and integration; existing full-state GPU kernels reused. No local-model code authorship or new training.',
        checked_answer='New standalone startup chain: sourceDD40 creates100free task records/systemcontext, DDF2 createsrender, and actualTRAP0/dispatch/RTE reaches17C40. Startup then creates19 moretasks (20 creations includingrender), forming21contexts with80free records left. Two Native/C runs match fullCPU/private2MBRAM, inheritedlogicalGPU4396/DSP8496,peripherals,disc andGPUtraces. Five source sprite requests percase use resident dispatcher with no intermediateGPUreset/reseed.12 file-backed transfers total758846bytes percase. Initial context ring/freepool/17DC2startupcapture are not supplied here. FrozenRAM/CPU/supervisorstack/sourceprocessor-setup, one externalsystemclocktick/buttons, BIOS303C/3042, synchronous completion/RTS atDF60, shared synchronousblitter/GPUcompletion remain providers. Source system firsthandoff is verified; actualstartupCDscheduler switching is not. This chain is still separate from the loading/movie/world run, which retains its earlierstartupcapture. Source4000/globalboot/firmware/remainingtasks/modalbranch/physicalscanout/playability/nativeChat remain unverified.',
        next_step='Replace the startup DF60 completion adapter with source scheduling/resumption, implement the health timeout wrapper, retain created actor/source helper continuations, and connect the startup chain to loading/movie/world without a captured startup boundary.')
    save(out/'checkpoint.json',cp);save(out/'manifest.json',manifest);save(ROOT/'verification/system-retained-startup-checkpoint.json',cp)
    p=session/'emulator-runtime/summary.json';summary=read(p);summary['system_retained_startup_checkpoint']=cp;save(p,summary)
    p=ROOT/'CURRENT DECOMPILATION.txt';p.write_text('LATEST SYSTEM-FIRST-HANDOFF / RETAINED STARTUP\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAUTHORSHIP\n'+cp['authorship']+'\n\nAUDIT\n'+str(out)+'\n\nNEXT\n'+cp['next_step']+'\n\nEARLIER CHECKPOINTS\n'+p.read_text())
    print(json.dumps({k:cp[k]for k in ['status','audit','source_total_task_creations_including_render','contexts_after_startup','source_freepool_records_remaining','sprite_requests_per_case']}))
if __name__=='__main__':main()

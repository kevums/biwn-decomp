"""Publish user task STOP and supplied resource-lock scheduler handoff proofs."""
import json,hashlib,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-busy-user-movie-caller.json');priv=read(ROOT/'verification/BIWN-user-movie-STOP-C.json');guards=read(ROOT/'verification/BIWN-movie-privilege-guards.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass' and proof['all_six'] and proof['busy_resource_TRAP0_handoff_verified']
    assert (len(proof['messages']),proof['frames'],proof['audio_samples'],priv['cases'],guards['checks'])==(6,763,512,64,44)
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_busy_user_movie_caller.py')==proof['script_sha256']
    for m in proof['messages']:
        a=read(raw/f'message-{m["message_id"]}-native.json');b=read(raw/f'message-{m["message_id"]}-C.json');assert a==b
        stages=b['summary']['busy_handoff'];assert [(x['label'],x['busy'],x['current_task']) for x in stages]==[('movie_before_D414',1,'0x100000'),('resource_selected',1,'0x101000'),('source_resource_released_lock',0,'0x101000'),('movie_resumed_D416',0,'0x100000')]
        assert stages[0]['CPU']['registers'][15]==stages[-1]['CPU']['registers'][15]==0x180fb8 and stages[-1]['CPU']['pc']==0xd416
        assert not m['original_CPU_GPU_DSP_instructions_on_C_path']
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='The movie caller now runs as a user-mode task with the source privilege STOP handler and nested GPU interrupt/return. With a supplied busy CD/resource task ring, source D414 TRAP0 selects a resource completion continuation, source1B13C releases the lock, and source DF60 yield resumes the movie at D416 with its private frame intact. All six caller runs then match the original across763frames/512audioenqueues through natural audio shutdown and resident return. This checks the supplied ring/resource-tail/yield-call context; it does not yet prove live world task creation or actual firmware/physical synchronization.',
        movies=6,video_frames=763,audio_samples_enqueued=512,source_state_dispatches=proof['source_dispatches'],source_disc_requests=proof['disc_requests'],controlled_word_clocks=proof['word_clocks'],source_movie_CPU_coverage=proof['source_CPU_coverage'],
        user_mode_caller_verified=True,source_privilege_STOP_nested_GPU_IRQ_RTE_verified=True,source_privilege_instructions=4,standalone_privilege_cases=64,privilege_event_contract_checks=44,
        busy_resource_TRAP0_handoff_verified=True,source_resource_lock_release_verified=True,source_DF60_yield_resume_D416_verified=True,movie_private_frame_preserved=True,
        busy_flag_semantics='47B80 is the shared CD/resource busy lock, established by source1B082 and cleared by1B13C;47B82 excludes new resource work during movies. Earlier renderer-ready labels were inaccurate.',
        privilege_operand_execution='User STOP22A0E raises vector8/DDfe. Handler STOP waits under supervisor stack, nestedGPUIRQ wakes it; DE02 adds2 to savedPC and DE06 RTE reaches22A10. Its2000operand executesas move.lD0,D0 before22A12. Source behavior retained.',
        C_CPU_GPU_DSP=True,original_CPU_GPU_DSP_instructions_on_C_path=False,
        declared_providers=['Supplied two-task ring/requester frame/resource completion continuation with six saved registers','Declared DF60 caller return after resource-tail RTS; complete resource load/task origin not executed in this scenario','File-backed MSF/CD progress provider and nominal dispatch/SSI/VBI clocks, same as prior normalfullcaller test','BIOS3000 no-op; repeats0/no cancellation'],
        audio_tail_limit='Natural source stop under the nominal schedule leaves each last audio token queued; all512samples enqueued does not mean everybyte played. Earlier reference-matched controlled audio previews retained.',
        every_queued_audio_byte_played=False,live_world_task_creation_linked=False,repeat_or_cancellation_paths_verified=False,BIOS_actual_firmware=False,physical_AV_synchronization_verified=False,in_game_playback_verified=False,native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator authored4privilege/operand source blocks, own exception/IRQ events and user/busy integration. Existing source scheduler/resource/movie/GPU/DSP bodies unchanged. No new localmodelcode/training;139selectedregistry/171localinstructionbodies unchanged.',
        report=str(ROOT/'verification/BIWN-busy-user-movie-caller.json'),privilege_report=str(ROOT/'verification/BIWN-user-movie-STOP-C.json'),guards=str(ROOT/'verification/BIWN-movie-privilege-guards.json'),
        next_work=['Connect actual resource-task creation/load lifetime and actor dialogue calls to the live world scheduler; current ring/tail are supplied.', 'Exercise source repeats/cancellation; reconstruct source GPU timer/global scheduling and inspect nominal audio tails.', 'Validate BIOS/platform replacement, whole source boot/game tasks/scanout and native LM Studio Chat usability.'])
    save(ROOT/'verification/busy-user-movie-checkpoint.json',cp);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';summary=read(p);summary['busy_user_movie_checkpoint']=cp;save(p,summary)
    out=ROOT/'verification/busy-user-movie-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);files=[ROOT/'scripts/generate_biwn_movie_privilege_cpu.py',ROOT/'scripts/check_biwn_user_movie_STOP.py',ROOT/'scripts/check_biwn_user_full_movie_caller.py',ROOT/'scripts/check_biwn_busy_user_movie_caller.py',ROOT/'scripts/check_biwn_movie_privilege_guards.py',Path(__file__),ROOT/'verification/BIWN-busy-user-movie-caller.json',ROOT/'verification/BIWN-user-movie-STOP-C.json',ROOT/'verification/BIWN-movie-privilege-guards.json',ROOT/'verification/busy-user-movie-checkpoint.json',*[src/n for n in proof['source_sha256']],src/'biwn_movie_privilege_cpu.h'];manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest));(out/'who-and-prompts.txt').write_text('Coordinator reconstructed user STOP privilege path and supplied busy-resource scheduler handoff. No local-model implementation prompts/training;171existing localbodies unchanged.\nMovie D414 TRAP0/private44byteMOVEM frame is actual source. Scheduler selects supplied source1B13C resource-tail context; its CLR releases47B80. DF60 is called with a declared4byte caller return, then sourceMOVEM11/TRAP/DE08/RTE resumes movieD416. No movie frame/PC/lock release injected by host. Resource task creation/full earlierCDload remains separate.\nUser STOP uses real privilege6byteframe plus nestedGPU6byteframe. Source savedPC+2 reaches2000operand as an actualMOVE instruction; preserving this was required for sourceexactflags/userstack behavior.\nBusy flag is CD/resource ownership, correcting earlier renderer labels. Allsix user/busy caller runs match original; physicaltiming/firmware/liveworld/repeats/cancel unfinished.\n')
    save(ROOT/'verification/busy-user-movie-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — USER TASK MOVIES AND BUSY RESOURCE HANDOFF\n'+now+'\n\n'+cp['checked_answer']+'\n\n64 standalone privilege cases;44 interface checks. Four source privilege/operand instructions. Actual movie/user stack and nested supervisor IRQ frames preserved. Shared busy flag belongs to CD/resources.\n\nSupplied task ring/resource-tail/DF60call, file/CD/clock providers remain declared; live world task origins, complete firmware/timing/gameplay unfinished. Audio tails remain queued under nominal schedule. No new training/defaults.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),frames=763,privilege_cases=64,guards=44)))
if __name__=='__main__':main()

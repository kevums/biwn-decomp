"""Publish retained ready-task -> merchant choice/movie/state2/facing proof."""
import json,hashlib,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-retained-merchant-dialogue.json');raw=Path(proof['directory']);assert read(raw/'status.json')['status']=='terminal_pass'
    assert (proof['frames'],proof['audio_samples'],proof['intermediate_trigger_capture_or_reset'],proof['post_dialogue_state2_facing_verified'])==(187,125,False,True)
    a=read(raw/'message-60-native.json');b=read(raw/'message-60-C.json');assert a==b and b['summary']['CPU']['pc']==0xeb04
    assert not proof['messages'][0]['original_CPU_GPU_DSP_instructions_on_C_path'];src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_retained_merchant_dialogue.py')==proof['script_sha256']
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='The source-created ready merchant now resumes its warm scheduler frame, chooses message60 from nearby-player/cash0 inputs, runs source207CC/display/fulluser movie caller through187frames/125audioenqueues, returns to its own caller, sets merchantstate2 and executes sourcefacing beforeanimationEB04. One CPU/RAM/GPU/DSP/peripheral context is retained from warm resumption through dialogue and facing; no intermediate message-entry capture or peripheral reset. Native/C state/devices/trace/audio match. Initial ready-world capture, taskquiescence and disc/clock/BIOS providers remain; animation/movement/renderer/globalworld continuation afterEB04 is unverified.',
        source_created_merchant_task=True,merchant_task='0xc1528',actor_slot=4,source_selected_message=60,video_frames=187,audio_samples_enqueued=125,controlled_word_clocks=proof['word_clocks'],source_state_dispatches=proof['source_dispatches'],source_disc_requests=proof['disc_requests'],
        retained_trigger_movie_post_dialogue_context=True,intermediate_trigger_capture_or_peripheral_reset=False,source_warm_scheduler_frame_resumed=True,source_post_dialogue_state2_verified=True,source_post_dialogue_facing_verified=True,source_next_boundary='0xeb04',
        C_CPU_GPU_DSP=True,original_CPU_GPU_DSP_instructions_on_C_path=False,
        initial_boundary='Ready-world capture originates in checked source world/taskcreation/model21/output allocation/firstNPCyield. Peripheral/source GPU/DSP startup fixture is established before warm-task resumption, not between trigger/movie/postdialogue.',
        declared_providers=['Initial ready-world source task/assets capture','Nearbyplayer XY/cash0 and quiescentothercontexts; source selfyield and branch choosemessage60','SourcebootSSP200000, existing sourceGPU/DSP startup beforemerchant continuation','File-backed CD/BIOS3000 no-op/nominal SSI/VBI clocks; no physicalfirmware/timing proof'],
        animation_after_dialogue_verified=False,movement_after_dialogue_verified=False,uninterrupted_world_from_boot_verified=False,renderer_after_dialogue_verified=False,purchases_or_choice_branches_verified=False,BIOS_actual_firmware=False,physical_AV_synchronization_verified=False,every_queued_audio_byte_played=False,in_game_playback_verified=False,native_Chat_verified=False,whole_game_complete=False,
        audio_tail_limit='Natural source stop under nominal schedule leaves final audio token queued; matching output is not proof of everybyte played or physicalsync.',
        implementation_authorship='Coordinator linked existing source NPC/scheduler/math/direction/movie/CPU/GPU/DSP bodies in retained runtime and compared sourcepost-dialogue. No new localmodelcode/training;139selectedregistry/171localbodies unchanged.',
        report=str(ROOT/'verification/BIWN-retained-merchant-dialogue.json'),
        next_work=['Continue sourceEB04 animation and13C9A movement/collision/geometry then sourceNPCyield/renderer while preserving this context.', 'Link world load/task origins without initialreadycapture; choices/purchases/repeats/cancel and sourceglobaltiming/actualboot/scanout/firmware remain.', 'Continue native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/retained-merchant-checkpoint.json',cp);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';s=read(p);s['retained_merchant_dialogue_checkpoint']=cp;save(p,s)
    out=ROOT/'verification/retained-merchant-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);files=[ROOT/'scripts/check_biwn_retained_merchant_dialogue.py',Path(__file__),ROOT/'verification/BIWN-retained-merchant-dialogue.json',ROOT/'verification/retained-merchant-checkpoint.json',*[src/n for n in proof['source_sha256']]];manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest));(out/'who-and-prompts.txt').write_text('Coordinator linked actual warm NPC source scheduler selfyield/loop/selection/message/display/movie/sourceGPUexit/state2/facing with retained CPU/RAM/GPU/DSP/peripheral context. No source message-entry capture or device reset after warmresumption. Existing source bodies unchanged; no localmodelcodeprompts/training.\nInitial ready-world source-created NPC/assets capture, controllednearplayer/cash0/taskquiescence/sourcebootSSP/sourceGPUstartup and file/clock/BIOS providers remain. EB04 animation is a captured nextboundary, not executed. Physicaltiming/firmware/worldrenderer/wholegame incomplete; nominalaudio tails remain.\nNative reference sourcehelper E588 was missing from the harnessPCmap after facing began; adding its actualdecoded interval allowed the comparison. No sourceprogram edit or fallback.\n')
    save(ROOT/'verification/retained-merchant-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — RETAINED MERCHANT DIALOGUE AND FACING\n'+now+'\n\n'+cp['checked_answer']+'\n\nMessage60 /187frames/125audioenqueues / source state2/facing / nextEB04. Initial readycapture/providers stilldeclared; no message-entry reset. No complete world/animation/movement/renderer yet. No new training/defaults.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),frames=187,next_boundary='0xeb04')))
if __name__=='__main__':main()

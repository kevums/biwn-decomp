"""Publish source-created merchant capture/trigger/message60 full movie linkage."""
import json,hashlib,shutil,wave
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ready=read(ROOT/'verification/BIWN-dialogue-ready-NPC.json');trigger=read(ROOT/'verification/BIWN-live-NPC-dialogue-trigger.json');proof=read(ROOT/'verification/BIWN-merchant-movie-bridge.json');raw=Path(proof['directory']);assert read(raw/'status.json')['status']=='terminal_pass'
    assert (ready['current_task'],ready['actor_slot'],trigger['source_message'],proof['frames'],proof['audio_samples'])==('0xc1528',4,60,187,125)
    assert sha(Path(ready['RAM_file']))==ready['RAM_sha256'] and sha(Path(trigger['RAM_file']))==trigger['RAM_sha256']
    a=read(raw/'message-60-native.json');b=read(raw/'message-60-C.json');assert a==b and b['summary']['CPU']['pc']==0xeea8
    assert not proof['messages'][0]['original_CPU_GPU_DSP_instructions_on_C_path']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_merchant_movie_bridge.py')==proof['script_sha256']
    rebuilt=raw/'message-60-C.wav';assert rebuilt.read_bytes()==(raw/'message-60-native.wav').read_bytes();preview=ROOT/'verified-previews/C-merchant-message-60-controlled-audio.wav';shutil.copy2(rebuilt,preview)
    with wave.open(str(preview),'rb') as w:audio=dict(file=str(preview),sha256=sha(preview),frames=w.getnframes(),sample_rate=w.getframerate(),seconds=w.getnframes()/w.getframerate(),caption='Source merchant-selected message60 under declared clock/disc schedule; reference-matched audio, final queued token remains at stop.')
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='A merchant task and model21/output assets created by the checked source world-loading path now trigger dialogue from their source task frame. Controlled nearby-player coordinates and cash0 make the source distance/money branch select message60. Source207CC chooses the actual message-table movie arguments and display setup, runs the full user-mode movie caller through187frames/125audioenqueues, shuts down and returns to merchantEEA8. Native/C CPU/RAM/GPU/DSP/devices/trace/audio match. These linked captured boundaries do not yet prove an uninterrupted world/dialogue/renderer lifecycle or physical firmware/timing.',
        source_created_merchant_task=True,merchant_task='0xc1528',actor_slot=4,source_model21_and_output_allocation=True,source_merchant_distance_money_branch_verified=True,source_selected_message=60,source_message_table_arguments_and_display_setup_verified=True,source_return_to_merchant='0xeea8',
        video_frames=187,audio_samples_enqueued=125,controlled_word_clocks=proof['word_clocks'],source_state_dispatches=proof['source_dispatches'],source_disc_requests=proof['disc_requests'],
        C_CPU_GPU_DSP=True,original_CPU_GPU_DSP_instructions_on_C_path=False,
        task_origins='Native/C replay of checked controlled gates/worldload/task creation/NPC coldinit/firstyield, captured before NPC kill. No replacement merchantTCB or manually supplied model references.',
        trigger_inputs='Other existing task contexts blocked for scheduler selfyield; nearbyplayer XY and cash0 supplied. Source chooses message60 and pushes its actual JSRframe.',
        bridge_boundary='Captured source207CC CPU/RAM enters message bridge. Source movie/display/GPU/DSP initialization under prior checked providers resets peripheral context; SSP uses sourceboot200000. Movie args, message index, framebuffer, sample addresses and merchantreturn are source-controlled.',
        audio_tail_limit='Nominal schedule leaves final audio token queued, same as matched reference.125enqueues does not prove everybyte audible or physicalsync.',
        declared_providers=['Controlled worldgate/pose/pad/clock/disc inputs from preceding world proof','Ready and message-entry capture boundaries; other tasks quiescent for trigger','Nearbyplayer/cash0 and sourcebootSSP200000','Queued file-backed CD/BIOS3000 ABI/nominal SSI/VBI clocks from movie proof'],
        uninterrupted_world_dialogue_lifecycle_verified=False,post_dialogue_merchant_loop_verified=False,purchases_or_choice_branches_verified=False,BIOS_actual_firmware=False,physical_AV_synchronization_verified=False,every_queued_audio_byte_played=False,in_game_playback_verified=False,native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator linked existing source world/NPC/scheduler/movie/CPU/GPU/DSP implementations and added capture/bridge checks. No new localmodelimplementationprompts/training;139selectedregistry/171localbodies unchanged.',
        reports=[str(ROOT/'verification/BIWN-dialogue-ready-NPC.json'),str(ROOT/'verification/BIWN-live-NPC-dialogue-trigger.json'),str(ROOT/'verification/BIWN-merchant-movie-bridge.json')],audio_preview=audio,
        next_work=['Run world scheduler and merchant dialogue without captured/peripheral-reset handoffs; resume source merchant state2/facing/animation/movement afterEEA8.', 'Exercise choices/purchases/repeats/cancel and source GPU timer/global timing, then actual boot/scanout/firmware or verified platform replacement.', 'Continue visible native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/merchant-dialogue-checkpoint.json',cp);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';s=read(p);s['merchant_dialogue_checkpoint']=cp;save(p,s)
    out=ROOT/'verification/merchant-dialogue-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);files=[ROOT/'scripts/capture_biwn_dialogue_ready_NPC.py',ROOT/'scripts/check_biwn_live_NPC_dialogue_trigger.py',ROOT/'scripts/check_biwn_merchant_movie_bridge.py',Path(__file__),ROOT/'verification/BIWN-dialogue-ready-NPC.json',ROOT/'verification/BIWN-live-NPC-dialogue-trigger.json',ROOT/'verification/BIWN-merchant-movie-bridge.json',ROOT/'verification/merchant-dialogue-checkpoint.json'];manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest));(out/'who-and-prompts.txt').write_text('Coordinator replayed checked worldsource to capture createdmerchant/model21/outputallocator beforekill; native/C readyRAM and CPUmatch. Nearbyplayer/cash0 and taskquiescence are inputs. Actualscheduler selfyield resumes merchant; source distance/money selectsmessage60 and pushes207CCcall.\nSource207CC/18160/message table constructs sixmovieargs; existing CuserD3FC engine plays187frames/125audioenqueues and returnsEEA8. Original processors reference only, rebuilt path executesnone.\nCaptured ready/message-entry/peripheralinit boundaries remain; no continuousworlddialogue/rendererclaim. No new localcodeprompts/training. Prior139registry/171localbodies unchanged. Nominalaudio tail/firmware/physicaltiming remain unverified.\n')
    save(ROOT/'verification/merchant-dialogue-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SOURCE-CREATED MERCHANT SELECTS AND RUNS DIALOGUE\n'+now+'\n\n'+cp['checked_answer']+'\n\nTask C1528 / actor4 / source message60 /187frames/125audioenqueues / merchant returnEEA8. Actual task/assets and caller frames preserved. Earlier allsix normal/busy user movie runs remain separate.\n\nCaptured boundaries/controlled pose/cash/taskquiescence/disc/clocks remain declared. No uninterrupted world lifecycle or full game yet; audio tail remains queued under nominal schedule. No new training/defaults.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),message=60,frames=187,audio_samples=125)))
if __name__=='__main__':main()

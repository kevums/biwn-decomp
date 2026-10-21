"""Publish matched C first movie frames with exact CRY pixels and scoped previews."""
import json,hashlib,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from inventory_renderer import png_rgb
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    proof=read(ROOT/'verification/BIWN-movie-GPU-C.json');directory=Path(proof['directory']);native=Path(proof['native_reference_directory'])
    assert read(directory/'status.json')['status']=='terminal_pass'
    assert (proof['frames'],proof['GPU_commands'],proof['source_instruction_coverage'],proof['host_guards'])==(6,12,[186,186],18)
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in proof['source_sha256'].items():assert sha(source/n)==digest
    tables_path=ROOT/'tools/pinned-CRY-color-tables.json';assert sha(tables_path)=='a20c8fedd516b611d546f1abe04a0b1f59fdf7a2662556b1306cb5e4da49b181';tables=read(tables_path)['tables']
    previews=[]
    for message in range(58,64):
        p=directory/f'message-{message}-C-first-frame.CRY16';q=native/f'message-{message}-first-frame.CRY16';data=p.read_bytes();assert data==q.read_bytes() and len(data)==224*180*2
        rgb=bytearray()
        for offset in range(0,len(data),2):
            color=int.from_bytes(data[offset:offset+2],'big');cyan=(color>>12)&15;red=(color>>8)&15;intensity=color&255
            rgb.extend((tables[name][cyan][red]*intensity)>>8 for name in ['redcv','greencv','bluecv'])
        target=ROOT/'verified-previews'/f'C-movie-message-{message}-first-frame.png'
        enlarged=b''.join(b''.join(rgb[(y*224+x)*3:(y*224+x+1)*3]*3 for x in range(224))*3 for y in range(180))
        target.write_bytes(png_rgb(672,540,enlarged))
        previews.append(dict(message_id=message,relative_png=str(target.relative_to(ROOT)),png_sha256=sha(target),source_dimensions=[224,180],preview_scale=3,
            raw_CRY_sha256=sha(p),raw_CRY_matches_original=True,RGB_sha256=hashlib.sha256(rgb).hexdigest(),
            verified_caption=f'First real disc movie frame for message{message}, decoded by the reconstructed C GPU program. Raw pixels and complete logical GPU/RAM/interrupt effects match the original under supplied command states. This is a saved comparison frame, not full movie playback or a playable game.',
            original_reference_pixels_match=True,pinned_emulator_CRY_conversion=True,physical_hardware_validation=False,live_gameplay=False,
            source_report=str(ROOT/'verification/BIWN-movie-GPU-C.json')))
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=dict(recorded_at=now,status=proof['status'],
        checked_answer='The C movie GPU decoder now produces the first real frames of six dialogue movies, with identical raw224x180CRY pixels to the original. Twelve codebook/drawing commands match full4396logicalGPUbytes, full2MBRAM, exact outer PC sequence, mandatory delay counts and the CPU interrupt frame under captured stopped CPU/bus state. Full movie playback is unfinished.',
        frames=6,total_video_samples_in_six_movies=763,GPU_commands=12,source_instruction_coverage=[186,186],host_guards=18,
        source_instructions_including_mandatory_delays=proof['source_instructions_including_mandatory_delays'],
        native_counter_scope='Pinned native GPU opcode counter counts outer calls only; inline branch delays are accounted separately. Older probe source_instructions fields refer to that outer counter.',
        full_logical_GPU_and_RAM_and_interrupt_frame_match=True,source_C_GPU_original_GPU_instructions=0,
        source_CPU_video_wrappers_native_only=True,source_CPU_STOP_IRQ_RTE_native_reference=True,source_CPU_wrappers_C_verified=False,
        initialization='Source GPU self-relocation is captured separately:delta258hex/42changedhalfwords. C decoder uses the relocated image; C relocation not yet checked.',
        code_scope='186execution-proven code/delay addresses from these six first frames. Other PCs returnBAD_PC; no complete overlay/code coverage claim.',
        original_GPU_pipeline_microstate_verified=False,physical_timing_verified=False,BIOS_streaming_verified=False,full_dialogue_playback_verified=False,in_game_playback_verified=False,
        native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator authored source C GPU decoder/probes/checks. No new local-model code/training; prior171local instruction bodies retained.',
        previously_selected_component_registry=139,new_components_added_to_registry=0,
        previews=previews,report=str(ROOT/'verification/BIWN-movie-GPU-C.json'),native_report=str(ROOT/'verification/BIWN-original-movie-frames.json'),
        next_work=['Extend the decoder to remaining/key/delta frames with source codebook lifetimes retained.',
                   'Reconstruct CPU video/STOP/IRQ interfaces and startup relocation, then connect the movie controller, streaming and scheduler.',
                   'Verify complete dialogue movies, remaining game tasks/boot/scanout and visible LM Studio Chat.'])
    save(ROOT/'verification/movie-video-checkpoint.json',checkpoint)
    scene_path=ROOT/'verified-previews/scene-previews.json';scene=read(scene_path);scene['previews']['checked_movie_frame']=previews[0];scene['movie_video_follow_on']=dict(recorded_at=now,report=checkpoint['report']);save(scene_path,scene)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);summary_path=session/'emulator-runtime/summary.json';summary=read(summary_path);summary['movie_video_checkpoint']=checkpoint;save(summary_path,summary)
    out=ROOT/'verification/movie-video-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[source/'biwn_movie_GPU.c',source/'biwn_movie_GPU.h',*[ROOT/'scripts'/n for n in ['probe_biwn_movie_GPU.py','probe_biwn_movie_frames.py','generate_biwn_movie_GPU.py','check_biwn_movie_GPU.py']],Path(__file__),
        ROOT/'verification/BIWN-movie-GPU-C.json',ROOT/'verification/BIWN-original-movie-frames.json',ROOT/'verification/movie-video-checkpoint.json',*[ROOT/p['relative_png'] for p in previews]]
    snapshots=[]
    for p in files:
        target=out/'snapshot'/p.name;shutil.copy2(p,target);snapshots.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(recorded_at=now,checkpoint=checkpoint,files=snapshots,
        initial_failed_C_comparison=dict(directory=str(ROOT/'verification/BIWN-movie-GPU-C/20261014T111258.120240Z'),reason='GPU/trace matched; missing original stopped CPU state caused6-byte interrupt-frame mismatch. Captured full stopped-machine input, then preserved and matched actual source interrupt effects; no RAM masking or frame injection.')))
    (out/'who-and-prompts.txt').write_text('Coordinator authored native source GPU relocation/CPU-video/IRQ probes,186observed C GPU blocks and18guard checks.\nNo local-model code prompts/training in this implementation; prior171local instruction bodies unchanged.\nC GPU comparison executes no originalGPUinstructions. NativeCPU prepares the command inputs; shared bus supplies actual IRQ signaling/CPUframe effects.\nOnly six first frames verified; unobserved code returnsBAD_PC. Complete movie/game remains unfinished.\n')
    save(ROOT/'verification/movie-video-review.json',dict(directory=str(out),status='published',checkpoint=checkpoint))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SIX REAL C MOVIE FRAMES\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\n12commands/6firstframes;186observed fixed GPU instructions including delays;18guards. All224x180rawCRYpixels match. CPU stopped state captured so source GPU signal produces the real matching6-byte CPUinterruptframe. OriginalGPU counter excludes inline delays;917,994actual source instructions accounted including them.\n\n763video samples exist in these six movies; only firstframes checked. CPUvideo wrappers remain native reference; C self-relocation, complete streaming/scheduling/video and game playback remain unverified.\n\nSource movie CPU-to-DSP proof retained:12CPUparsercases/319of519instructions;6real first-audio integrations/4,736wordclocks;directTRAP160cases.\n\nCoordinator-authored new GPU code; no new local-model code/training. Registry remains139previously selected components.\n\nPreview: '+str(ROOT/previews[0]['relative_png'])+'\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(checkpoint['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),preview=str(ROOT/previews[0]['relative_png']))))

if __name__=='__main__':main()

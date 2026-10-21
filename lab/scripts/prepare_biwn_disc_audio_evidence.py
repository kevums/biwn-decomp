"""Publish the separate real-sample DSP follow-on without rewriting older proofs."""
import hashlib
import json
import shutil
import wave
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    proof=read(ROOT/'verification/BIWN-disc-audio-DSP.json')
    extraction=read(ROOT/'verification/BIWN-dialogue-audio-extraction.json')
    assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
    assert len(proof['cases'])==6 and proof['word_clocks']==4742
    assert extraction['audio_chunks']==512 and extraction['audio_bytes']==1132004
    assert proof['extraction_report_sha256']==sha(ROOT/'verification/BIWN-dialogue-audio-extraction.json')
    assert proof['script_sha256']==sha(ROOT/'scripts/check_biwn_disc_audio_DSP.py')
    old=read(ROOT/'verification/biwn-dsp-media-audio-checks.json')
    assert proof['C_library_sha256']==sha(Path(old['directory'])/'libdsp-media-audio.dylib')
    for name,digest in old['source_sha256'].items():
        assert sha(ROOT/'projects/black-ice-white-noise/restoration'/name)==digest
    preview=ROOT/'verified-previews/C-DSP-disc-message-58-first-chunk.wav'
    shutil.copy2(proof['cases'][0]['wav'],preview)
    assert sha(preview)==proof['cases'][0]['wav_sha256']
    with wave.open(str(preview),'rb') as w:
        assert (w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth())==(4096,21868,2,2)
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=dict(recorded_at=now,status=proof['status'],
        checked_answer='Actual merchant-dialogue audio bytes have been extracted and supplied to the checked C DSP engine. Six first-chunk tests match the original DSP at every controlled word-clock boundary. The 0.187-second message58 preview uses real disc samples, but movie CPU streaming, full dialogue playback and in-game audio remain unverified.',
        extracted_messages=6,extracted_audio_chunks=512,extracted_audio_bytes=1132004,
        DSP_cases=6,word_clocks=4742,source_instruction_coverage=proof['source_instruction_coverage'],
        scope='Message58:4096 clocks; messages59..63:128 clocks each, plus shutdown. Five prefixes are silent. Explicit host buffer/clock fixtures; not the original movie producer.',
        comparison=proof['boundary_comparison'],real_disc_samples=True,
        movie_CPU_producer_executed=False,BIOS_seek_mapping_verified=False,in_game_playback_verified=False,
        native_Chat_verified=False,whole_game_complete=False,new_components=0,
        implementation_authorship='Coordinator authored the extraction and comparison scripts; existing source C DSP unchanged. No new local-model code or training.',
        previous_accepted_local_model_instruction_bodies=171,
        report=str(ROOT/'verification/BIWN-disc-audio-DSP.json'),extraction_report=str(ROOT/'verification/BIWN-dialogue-audio-extraction.json'),
        preview=dict(path=str(preview),sha256=sha(preview),frames=4096,declared_Hz=21868,physical_timing_verified=False),
        next_work=['Connect original movie CPU state handlers, BIOS seek/progress and actual buffer lifetimes.',
                   'Reconstruct and check movie video GPU, then integrate CPU/DSP/video scheduling without overlapping the CPU stacks.'])
    save(ROOT/'verification/disc-audio-DSP-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    summary=session/'emulator-runtime/summary.json';data=read(summary);data['disc_audio_DSP_checkpoint']=checkpoint;save(summary,data)
    out=ROOT/'verification/disc-audio-DSP-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out/'snapshot').mkdir(parents=True)
    files=[ROOT/'scripts/extract_biwn_dialogue_audio.py',ROOT/'scripts/check_biwn_disc_audio_DSP.py',Path(__file__),
           ROOT/'verification/BIWN-dialogue-audio-extraction.json',ROOT/'verification/BIWN-disc-audio-DSP.json',
           ROOT/'verification/disc-audio-DSP-checkpoint.json',ROOT/'chat_tools.py',preview,ROOT/'CURRENT DECOMPILATION.txt']
    snapshots=[]
    for p in files:
        dest=out/'snapshot'/p.name;shutil.copy2(p,dest)
        snapshots.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(recorded_at=now,checkpoint=checkpoint,files=snapshots,
        retained_failed_runs=[dict(path=str(ROOT/'verification/BIWN-disc-audio-DSP/20261014T102110.886163Z'),
            reason='Native/C match passed for message58 and message59 prefix, but an unnecessary assertion required a silent prefix to contain nonzero samples; removed without changing source code or reference matching.')]))
    (out/'who-and-prompts.txt').write_text('Coordinator: traced the source movie layout, authored bounded extraction/comparison/publishing scripts and reviewed all matching fields.\nLocal models: no new code prompts or training in this implementation. Previous171accepted local instruction bodies unchanged.\nComparison: original DSP is the reference; reconstructed C executes no original DSP instructions. Shared pinned bus/DAC model.\nNative LM Studio Chat: Mac remains locked; no visible Chat response claimed.\n')
    save(ROOT/'verification/disc-audio-DSP-review.json',dict(directory=str(out),status='published',checkpoint=checkpoint))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — ACTUAL DISC SAMPLE FOLLOW-ON\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\nSix dialogue movies:512audiochunks/1,132,004bytes recovered with boundaries. Six first-chunk DSP comparisons:4,742clockevents. All8,496logicalDSPbytes, mainRAM, DAC and source instruction count match after each word-clock/idle segment; C executes no original DSP instructions.\n\nSource C engine unchanged; selected139components(125CPU/13GPU/1DSP), not a completion percentage. Coordinator authored these scripts; no new model code/training.\n\nPreview: '+str(preview)+'\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(checkpoint['next_work'])+'\nFull goal active/incomplete. Native Chat remains unverified while locked.\n')
    print(json.dumps(dict(directory=str(out),preview=str(preview))))

if __name__=='__main__':main()

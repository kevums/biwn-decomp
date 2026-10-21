"""Archive source evidence and failed/fixed plain local music explanations."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');engine=read(ROOT/'verification/music-DSP-engine-checks.json');cases=read(Path(engine['directory'])/'cases.json')
    assert engine['cases']==8 and engine['source_instruction_coverage']==[209,209]and engine['original_DSP_instructions_on_C_path']==0
    assert [x['nonzero_PCM_pairs']for x in cases]==[0,0,0,0,48,48,48,48]
    assert cp['source_bank1_startup_mixer_verified']and cp['source_music_word_events']==13 and cp['source_music_timer2_events']==4 and not cp['startup_music_PCM_nonzero']and not cp['all_voice_paths_and_audible_disc_music_verified']
    local=Path(read(ROOT/'verification/easy-music-engine-scope-pointer.json')['directory']);a=read(local/'protocol.json');item=a['results'][0]
    assert a['status']=='completed_pending_coordinator_review'and not item['quality_flags']and item['words']<160 and all(s['stats']['stopReason']=='eosFound'for s in item['prediction_stats'])
    assert all(t in item['answer']for t in ['13 supplied','4 supplied','silent','256 supplied','Neither proves recovered game music'])
    old=ROOT/'verification/easy-music-engine-scope/20261014T205452.580582Z';now=datetime.now(timezone.utc);out=ROOT/'verification/music-engine-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[local/'protocol.json',local/'prompts-and-responses.txt',old/'protocol.json',old/'prompts-and-responses.txt',old/'coordinator-review.json',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/music-DSP-engine-checks.json',ROOT/'verification/music-engine-MCP-check.json',ROOT/'chat_tools.py',ROOT/'scripts/biwn_music_engine_runtime.py',ROOT/'scripts/test_music_engine_scope.py',Path(__file__)]
    manifest=[]
    for i,p in enumerate(files):
        dest=out/f'{i:02d}-{p.name}';shutil.copy2(p,dest);assert sha(p)==sha(dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(p)))
    report=dict(status='source_banked_mixer_silence_synthetic_voice_and_live_startup_verified_local_scope_repaired',directory=str(out),recorded_at=now.isoformat(),source_audit=cp['audit'],source_engine_directory=engine['directory'],model=a['model'],interface=a['interface'],words=item['words'],seconds=item['seconds'],first_answer_rejected='Historical31case mediaDSP scope substituted for newest music engine; fixed tool routing/docstring to current DSP/music checkpoint.',final_answer_review='Correct live13SSI/4timer2 silent-default scope and synthetic256byte type8 interpolation distinction; no recovered music/physicalrates/globaltime/firmware/playability claim. Concise music-specific scope, not full game provider inventory.',native_Chat_verified=False,new_training=False,model_defaults_changed=False,full_audible_music_verified=False,whole_goal_complete=False,authorship=cp['implementation_authorship'],manifest=manifest)
    save(out/'review.json',report);save(ROOT/'verification/music-engine-local-review.json',report)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\nChecked true producer/consumer wait boundary; canonicalized/restored exact initial DAC state for standalone synthetic comparison; preserved failed/superseded trials. Tests compare original instructions to C, not model agreement.\n\nFIRST LOCAL GAME ASSISTANT — REJECTED STALE TOOL SCOPE\n'+(old/'prompts-and-responses.txt').read_text()+'\n\nREPEATED SAME PLAIN QUESTION AFTER CURRENT MUSIC TOOL ROUTING FIX\n'+(local/'prompts-and-responses.txt').read_text())
    note='LATEST — LIVE BANKED DSP MIXER\n'+now.isoformat()+'\n\n209static sourceDSP blocks matched every atomic block in8profiles:4silent startup and4synthetic sample-voice profiles, each64SSI strobes/4timer2 assertions. Synthetic output48/64nonzero pairs matches original; waveform/voice are explicit test inputs, not game-disc music. Live cold-stage startup now initializes bank1 mixer and runs13externalSSI/DAC words/4timer2events (silent default3BCE0/index0), then movie187frames125enqueues and12world/NPC/renderercycles in2matched Native/C profiles. Persisted states/RAM/requests/GPU-DSP evidence/AVdigests and WAV bytes match. Firmware/globaltime/physicalrates/remaining voices/music loading/commands/tasks/scanout/playability/nativeChat remain unverified.\n\n'+f'Local plain-question rerun: {item["words"]}words/{item["seconds"]:.2f}s, correct music/synthetic distinction. First reply used old audio scope because tool routing/docstring was stale; routing fixed and same question repeated. No newtraining/defaultchanges.\n\nWHO / EXACT PROMPTS / RESPONSES\n'+str(out/'who-prompts-and-responses.txt')+'\n\nSOURCE AUDIT\n'+cp['audit']+'\n\nREVIEW\n'+str(out/'review.json')+'\n\n'
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        p=ROOT/name;p.write_text(note+p.read_text())
    (out/'readable-results.txt').write_text(note)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(last_turn_classification='progress',source_audit=cp['audit'],local_audit=str(out))
    n['next_source_work']=[t.replace('Implement source bank1 DSP music engine/SSI/mixer afterF1B148 and remaining commands/resources. Startup acknowledgement is now source code, not music playback.','Bank1 default-song mixer/SSI is now linked to startup; implement remaining voice types, CPU commands including music stop/reload, actual source music/sound resource loading and audible disc music. Synthetic sample voice alone does not prove game music.')for t in n['next_source_work']];save(p,n)
    print(json.dumps(dict(status=report['status'],directory=str(out),local_seconds=item['seconds'],source_instructions=209)))
if __name__=='__main__':main()

"""Archive exact source startup question, dependencies and scope review."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    raw=Path(read(ROOT/'verification/easy-source-startup-scope-pointer.json')['directory']);protocol=read(raw/'protocol.json');item=protocol['results'][0]
    assert protocol['status']=='completed_pending_coordinator_review'and not item['quality_flags']and item['words']<160
    assert all(p['stats']['stopReason']=='eosFound'for p in item['prediction_stats'])
    answer=item['answer'];assert all(t in answer for t in ['19','21','12','758,846','earlier startup capture','no reached game-helper ABI scripts','GPU/DSP','playability remain unverified'])
    assert all(t in answer for t in ['Frozen RAM','two-context','free pool','emulated buttons','modal bit 0','0x303C/0x3042','0xDF60','reset/reseed','synchronous blitter','scheduler switching'])
    calls=[b['toolCallRequest']for e in item['events']for b in e['content']if b['type']=='toolCallRequest'];assert len(calls)==1 and calls[0]['name']=='project_evidence'and calls[0]['arguments']=={'topic':'render_startup'}
    cp=read(ROOT/'verification/source-startup-CPU-checkpoint.json');assert cp['no_reached_game_helper_ABI_scripts']and cp['earlier_startup_capture_still_supplied_to_connected_game']
    now=datetime.now(timezone.utc);out=ROOT/'verification/source-startup-inference-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    # Supplement the C/CPU comparison archive with concrete runtime/input
    # binaries. The raw track remains preserved at its internal source path.
    disc=read(ROOT/'verification/biwn-disc-resources.json');track=Path(disc['raw_track_path']);assert sha(track)==disc['source_raw_track_sha256']
    runtime_files=[ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'render-assets/jaguarcd_bios.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'verification/biwn-disc-resources.json',ROOT/'scripts/check_biwn_scheduler.py',ROOT/'scripts/check_biwn_world_movement_pipeline.py',ROOT/'scripts/check_biwn_render_queue_cpu.py',ROOT/'scripts/check_biwn_cd_cpu.py']
    files=[raw/'protocol.json',raw/'prompts-and-responses.txt',ROOT/'scripts/test_source_startup_scope.py',ROOT/'scripts/check_source_startup_mcp.py',ROOT/'verification/source-startup-CPU-MCP-check.json',ROOT/'verification/source-startup-CPU-checkpoint.json',ROOT/'chat_tools.py',Path(__file__)]+runtime_files
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    transcript=out/'prompts-and-responses.txt';shutil.copy2(raw/'prompts-and-responses.txt',transcript)
    review=dict(status='accepted_scoped_source_startup_answer',recorded_at=now.isoformat(),directory=str(out),model=protocol['model'],interface=protocol['interface'],words=item['words'],seconds=item['seconds'],quality_flags=[],tool_calls=calls,coordinator_semantic_review='Exact answer correctly separates reached source/C startup helpers from the unchanged connected game capture,19 creations/21 contexts and12 requests/758846bytes per case. It discloses all principal supplied initial/input/BIOS/completion/spriteGPU/blitter provider categories and scheduler/inheritedGPU-DSP/boot/firmware/scanout/playability limits. Accepted for this scoped question, not general reliability or complete branch coverage.',complete_principal_provider_summary=True,native_Chat_verified=False,new_training=False,model_defaults_changed=False,local_model_authored_new_C=False,whole_goal_complete=False,source_CPU_review=cp['audit'],preserved_raw_track=dict(path=str(track),sha256=disc['source_raw_track_sha256']),files=manifest)
    save(out/'review.json',review);save(ROOT/'verification/source-startup-inference-review.json',review)
    note='LATEST LOCAL QUESTION — SOURCE STARTUP\n'+now.isoformat()+'\n\nEveryday27B6bit/32K/one-worker model:115 words in17.50seconds, one project_evidence(render_startup) call, natural completion and no mechanical output flags. Coordinator accepted the source/helper/capture/count facts and principal provider inventory. No new training/model default changes. Backend SDK tested; native LM Studio Chat remains unverified.\n\nUSER PROMPT\n'+protocol['questions'][0]['user']+'\n\nEXACT LOCAL ANSWER\n'+answer+'\n\nEXACT SYSTEM PROMPT, TOOL CALL AND RESPONSE\n'+str(transcript)+'\n\nREVIEW\n'+str(out/'review.json')+'\n\n'
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';p.write_text(note+p.read_text())
    p=ROOT/'START HERE.txt';p.write_text('Latest source startup:8 cases run source17C40->17DC2 with all reached game helpers real, including scene/player/static objects/HUD;19 creations form21 contexts,12 transfers758846bytes per case. FullCPU/privateRAM/TOM-display/blitter/bus/disc match original plus independent CPU. Supplied initialization/buttons/BIOS/synchronousCDcompletion and isolatedGPU/sharedblitter remain. Startup scheduling/inheritedGPU-DSP/sourceboot unverified; connected movie/world still uses earlier startup capture.\nLocal assistant:115words/17.50seconds, correct scoped facts/provider summary. SDK test, not verified native Chat.\nAudit: '+str(out)+'\n\n'+p.read_text())
    (out/'readable-results.txt').write_text(note);print(json.dumps({k:review[k]for k in ['status','directory','seconds','words']}))
if __name__=='__main__':main()

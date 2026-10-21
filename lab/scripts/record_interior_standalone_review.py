"""Record standalone progress without changing the live scene component total."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 proof=read(ROOT/'verification/biwn-gpu-interior-checks.json');assert proof['cases']==72 and proof['programs']['0x6ae0']['source_instruction_coverage']==[276,276]and proof['programs']['0x6da0']['source_instruction_coverage']==[94,94]
 live=read(ROOT/'verification/overlay-text-scene-checkpoint.json');assert not proof['source_CPU_E0F2_E148_linked']and proof['new_published_components']==0
 local=Path(read(ROOT/'verification/interior-local-output-current.json')['directory']);roles=read(local/'protocol.json')['roles'];assert len(roles)==2 and not any(r['quality_flags']for r in roles)
 review=dict(status='bounded_core_summary_correct_final_gameplay_implication_needs_correction',mechanical_checks_pass=True,raw_roles_identical=roles[0]['text']==roles[1]['text'],independent_models=False,reviewer_caught_issue=False,issue='Final phrase to enable actual gameplay overstates what integrating only these two routines establishes; many full-game gaps remain.',coordinator_corrected_answer='The interiors are not playable yet. Two standalone GPU routines matched the original emulator in72tests, covering all370source instructions. Their CPU submission wrappers and actual scene-loading/texture path still need integration and testing. The main checkpoint remains130components. Other game systems and the visible LM Studio Chat workflow remain unfinished.',weights_or_defaults_changed=False)
 save(local/'coordinator-review.json',review);(local/'source-reviewed-answer.txt').write_text(review['coordinator_corrected_answer']+'\n')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=ROOT/'verification/interior-standalone-review'/stamp;out.mkdir(parents=True);snap=out/'snapshot';snap.mkdir()
 files=[ROOT/'scripts/generate_biwn_gpu_interior.py',ROOT/'scripts/check_biwn_gpu_interior.py',ROOT/'scripts/test_interior_progress_local.py',ROOT/'scripts/record_interior_standalone_review.py',ROOT/'verification/biwn-gpu-interior-checks.json']
 for h in ['6ae0','6da0']:
  for ext in ['c','h']:files.append(ROOT/f'projects/black-ice-white-noise/restoration/biwn_gpu_interior{h}.{ext}')
 for p in files:shutil.copy2(p,snap/p.name)
 audit=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='two_fixed_C_GPU_programs_standalone_verified_unpublished_in_scene',directory=str(out),proof_directory=proof['directory'],cases=72,source_instructions=[276,94],guards=31,main_checkpoint_components=130,new_main_components=0,CPU_wrappers_linked=False,whole_game_complete=False,code_authorship='Codex coordinator generated source-specific fixed C using existing checked integer primitives; no local model code authored or trained this step.',local_model_roles=[dict(role=r['role'],seconds=r['seconds'],words=r['word_count'],quality_flags=r['quality_flags'])for r in roles],local_model_prompt_response_directory=str(local),local_model_semantic_review=review,native_LM_Studio_Chat_verified=False,rejected_or_repaired=['First strict compile caught unused wr16 helper in6AE0; removed only unused generated helper. Final C compiled with Wall/Wextra/Werror.', 'Initial decoder extraction mistakenly retained the decoder tuple rather than its rows; corrected before C generation/test. No invalid decode used for acceptance.', 'Added source stage/payload/fixture hash assertions and unchanged rawflags/control checks; reran same72fixtures. This is not144distinctcases.'],limits=proof['scope'],files={str(p):sha(p)for p in files})
 save(out/'manifest.json',audit);save(ROOT/'verification/interior-standalone-review.json',audit)
 note='''INTERIOR GPU STANDALONE PROGRESS
{timestamp}

Two fixed C GPU programs, source6AE0(276instructions) and6DA0(94), match the original pinned emulator in72standalone fixtures across four preserved interior payloads. Full banks/flags/matrix/divider/4KBGPU RAM/2MBmain RAM/directPC/orderedexternalbusshape/storevalues match;31hostguards pass. Raw accumulator/hidata/dataorganization/activebank/rawflags/control are preserved. No originalGPU executes on the C path. Source bytes pinned to the preserved stage and payload hashes. Declared relocation/camera/sector/seeds/DIV0/fixedGPUinitialRAM; actual CPUscene loader, texture acquisition and CPUE0F2/E148 wrappers not executed. No dispatcher/liveinterior/raster/scanout/playablegame claim. Main scene checkpoint remains130selectedcomponents; these candidates are not yet added.

WHO / PROMPTS / LOCAL OUTPUT TEST
Codex coordinator generated and checked both C programs. Everyday27B Analyst5.03seconds and Reviewer4.82seconds ran sequential fresh contexts through local nativeREST, reasoningoff. Both50word responses passed mechanicalchecks but were identical and retained an overbroad final gameplay implication. Coordinator corrected that implication; sameweights are not independent verification. No newtraining/defaultchange. Exactsystem/userprompts, rawresponses and review: {local}

NEXT
Integrate and check original CPU submission wrappers plus the real interior loading/texture path, then compare source mode2 scene behavior. GlobalGPUcontext, othertasks/scenes/audio/boot/OPscanout/backendaccuracy and fullgame remain. Visible nativeLMStudioChat/easyworkflow remains unverified. No approvalneeded.

AUDIT
{audit}
Fullgoal active/incomplete.
'''.format(timestamp=audit['recorded_at'],local=local,audit=out)
 (out/'progress.txt').write_text(note)
 for p in [ROOT/'CURRENT DECOMPILATION.txt',ROOT/'CURRENT LOCAL INFERENCE.txt']:
  current=p.read_text();marker='\nINTERIOR GPU STANDALONE PROGRESS\n';current=current.split(marker)[0];p.write_text(current.rstrip()+'\n\n'+note)
 print(json.dumps(dict(audit=str(out),proof=proof['directory'],local=str(local),main_components=130,new_main_components=0)))
if __name__=='__main__':main()

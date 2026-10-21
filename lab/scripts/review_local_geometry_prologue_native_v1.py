"""Freeze one actual corrected local Repair and its unedited native prototype proofs."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 jp=V/'local-geometry-records-prologue-repair-v2-current.json';job=read(jp);assert job['status']=='terminal_local_prologue_repair_v2_host_pass_native_pending_unpromoted'and job['new_predictions']==1
 folder=Path(job['directory']);role=folder/'Repair_Corrected';response=read(role/'inference.json');assert response['seconds']==44.56 and response['usage']['completion_tokens']==686 and response['stream']['time_to_first_message_seconds']==6.61
 planned=read(V/'geometry-prologue-corrected-repair-prepared-v2.json');assert planned['prompt']==read(role/'prompt.json')
 composite=Path(job['accepted_composite']);staged=ROOT/'projects/black-ice-white-noise/restoration/experimental/local-geometry-prologue-repair-v2/accepted-composite.inc';assert composite.read_bytes()==staged.read_bytes()
 raw=(role/'response.txt').read_text();interior=(role/'unedited-model-interior.inc').read_text();text=raw.strip()[5:-3].strip();assert interior==text[text.index('{')+1:text.rfind('}')] and '\n {'+interior+'}\n'in composite.read_text()
 hostp=role/'host-gate/report.json';host=read(hostp);assert host['completed']==512 and host['host_guards']==19
 out=V/'local-geometry-prologue-native-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={str(Path(__file__)):sha(__file__),str(jp):sha(jp),str(staged):sha(staged)};proofs={}
 for name in ['local-geometry-prologue-native-v1','scene17-local-geometry-prologue-bridge-v1','local-geometry-prologue-copied-rebuild-v1']:
  p=V/(name+'-current.json');g=read(p);assert g['status'].startswith('terminal_')and 'failed'not in g['status']
  for source,h in g['source_sha256'].items():assert sha(source)==h,source
  deps.update(g['source_sha256']);deps[str(p)]=sha(p);save(out/(name+'.json'),g);proofs[name]=g
 n=proofs['local-geometry-prologue-native-v1'];s=proofs['scene17-local-geometry-prologue-bridge-v1'];c=proofs['local-geometry-prologue-copied-rebuild-v1'];assert n['completed']==512 and s['completed']==772 and n['payload_sha256']==s['payload_sha256']==c['sha256'] and c['bytes']==54446
 assert n['maximum_C_stack_bytes']==108 and s['maximum_C_stack_bytes']==168
 for path in folder.rglob('*'):
  if path.is_file():deps[str(path)]=sha(path)
 transcript=out/'prompts-and-responses.txt';shutil.copy2(folder/'prompts-and-responses.txt',transcript);deps[str(transcript)]=sha(transcript)
 report=ROOT/'reports/BIWN Local Prologue Repair Native Verification.txt'
 report.write_text('BIWN — local corrected Repair: verified component\n\n'
  'One actual local Repair used the configured copied27B model identifier. Generated686tokens in44.56seconds;first streamed text after6.61seconds. These timings exclude the earlier shared-resource queue. Prompt3059tokens,reasoningoff. The prepared prompt exactly matches the actual request. Prior Author50.23seconds and Repair34.62seconds produced complete source but both failed strict compilation for unusedu;original feedback had hidden the extra budget guard behind an assertion. This run supplied explicit compiler/guard feedback. No prediction was replayed.\n\n'
  'The22instruction prologue is model-authored. A complete outer Markdown fence and the function wrapper were removed;the interior statements were inserted verbatim into a nested scope within the unchanged coordinator remainder. Exact byte equality is checked. Supplied primitives and explicit register/flag/stack rules were exposed;coordinator target block was withheld. This is scaffolded development with same-task feedback,not held-out evaluation,independent review or weight training. Zero new unique original functions.\n\n'
  'Full combined function passes512host cases and19error guards,with5782actualcopy and2569matrix submissions. Actual68000native512cases pass full logical CPU/banks,nonprivateRAM,helper entry/return and scoped ordered public bus,including nativeCLRdummyreads and continuous trace. Connectedscene772cases pass with declared original copy/matrix and synchronous originalGPU4320providers. Body stack108bytes;connected168/208. Copied source and SDK rebuild byte-identically54,446bytes.\n\n'
  'This v35local-block component is unpromoted. It is232bytes larger than the v33module and312larger than v34signed-stride module;no efficiency claim. No new CDI,final relocation/retained/fallback/alias/observer or fresh-gameplay qualification for v35. The v34game candidate remains coordinator-authored. GPU/DSP/HLE/original-code dependencies and video/audio/IRQ/console fidelity are unresolved. No source installed into the preview,no model-weight updates,and copied-weight nativeChat rendering remains unverified.\n\nExact transcript:'+str(transcript)+'\n')
 facts=dict(status='terminal_local_corrected_prologue_host_native_scene_and_copied_verified_unpromoted',directory=str(out),report=str(report),profile='deck-shared-v35-local-record-prologue-v1',artifact_type='mixed_source_component_prototype_not_disc_image',original_run_directory=str(folder),actual_predictions=1,seconds=44.56,first_stream_message_seconds=6.61,prompt_tokens=3059,output_tokens=686,queue_time_included=False,model_identifier=job['model_identifier'],model_original_instructions=22,model_block_statement_edits=0,coordinator_target_block_supplied=False,coordinator_remainder_used=True,primitive_scaffolding_supplied=True,host_cases=512,host_guards=19,native_body_cases=512,prototype_scene_cases=772,module_bytes=54446,body_C_stack_bytes=108,connected_C_stack_bytes=168,C_stack_reserved=208,copied_prototype_module_byte_identical=True,new_unique_original_functions=0,new_disc_built=False,disc_integrated=False,fresh_gameplay_verified=False,model_source_installed=False,native_Chat_verified=False,new_training=False,optimizer_updates=0,held_out_benchmark=False,whole_game_complete=False,source_sha256=deps,next_action='Keep this exact unedited local block as a separate prototype. Before adoption,qualify all retained callers,exact-image relocation/startup/heap,bus/fallback/aliases/read-only observers and fresh gameplay. Continue useful untouched-task training and copied-weight Chat usability without treating prompt repair as weight training.')
 save(out/'review.json',facts);shutil.copy2(report,out/report.name);save(V/'local-geometry-prologue-native-reviewed-v1-current.json',facts)
 for p in [*map(Path,deps),out/'review.json',report,V/'local-geometry-prologue-native-reviewed-v1-current.json']:
  if p.is_relative_to(ROOT):
   d=P/'workbench'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 for root in [ROOT,P/'workbench']:
  p=root/'BIWN Corrected Repair Results.command';assert not p.exists();p.write_text('#!/bin/zsh\nset -eu\nBIWN_PACKAGE="$HOME/Desktop/BIWN Portable Lab"\nBIWN_PACKAGE=${BIWN_PACKAGE:A}\nopen -a TextEdit "$BIWN_PACKAGE/workbench/'+str(transcript.relative_to(ROOT))+'"\n');p.chmod(0o755)
 print(facts['status'],flush=True)
if __name__=='__main__':main()

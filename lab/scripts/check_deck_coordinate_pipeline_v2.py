"""Exercise the new readable caller inside the retained source Deck pipeline.

Forks the existing finite experimental-selector world-loop checker in a new
artifact directory. Never edits its canonical generated flow or prior proofs.
"""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-update'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def main():
 trial=read(ROOT/'verification/Deck-coordinate-source-candidate-current.json')
 assert trial['status']=='terminal_component_source_selected_pending_pipeline'
 glue=Path(trial['glue_directory'])
 body=Path(trial['candidate']);assert sha(body)==trial['candidate_sha256']
 receipt=read(trial['receipt']);assert receipt['completed']==576 and receipt['all_2MB_RAM_and_full_CPU_match']
 for p,h in receipt['source_bindings'].items():assert sha(p)==h,p
 out=ROOT/'verification/deck-coordinate-source-pipeline-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 original=ROOT/'projects/black-ice-white-noise/restoration/experimental/mode3-flow/biwn_mode3_scene_flow_cpu.c'
 flow=original.read_text();start=flow.index('  case 0x11d1au:');end=flow.index('  case 0x11e62u:')
 removed=flow[start:end];assert '  case 0x11e6cu:'not in removed
 replacement='''  case 0x11d1au: /* Recovered structured Deck/C-Space caller, explicit services. */
   {struct biwn_deck_context deck={bus,s.cpu,service,context,4,0};
    biwn_deck_coordinate_body(&deck);CHECK(deck.error);s.cpu=deck.cpu;}
   biwn_deck_semantic_calls++;break;
'''
 flow='#include "deck-coordinate-contract.h"\nuint32_t biwn_deck_semantic_calls;\n'+flow[:start]+replacement+flow[end:]
 # Keep the original generated source/header beside this isolated variant.
 target=out/'biwn_mode3_scene_flow_cpu.c';target.write_text(flow)
 (out/'biwn_mode3_scene_flow_cpu.h').write_bytes(original.with_suffix('.h').read_bytes())
 (out/'removed-instruction-cases.c.txt').write_text(removed)
 (out/'component-receipt.json').write_text(Path(trial['receipt']).read_text())
 template=ROOT/'scripts/check_mode3_source_flow.py';text=template.read_text()
 anchor="proof_name='mode3-recorded-world-loop-roundtrip'"
 assert anchor in text
 line=next(x for x in text.splitlines()if x.lstrip().startswith(anchor))
 text=text.replace(line," proof_name='deck-coordinate-readable-world-loop-v2'")
 old="source/'experimental/mode3-flow/biwn_mode3_scene_flow_cpu.c'"
 assert text.count(old)==1
 text=text.replace(old,"Path("+repr(str(target))+")")
 marker=";library=out/'libmode3-flow.dylib'";assert marker in text
 text=text.replace(marker,";files += [Path("+repr(str(body))+"),Path("+repr(str(glue/'deck-coordinate-adapter.c'))+")];library=out/'libmode3-flow.dylib'")
 text=text.replace("'-I',str(source),*map(str,files)","'-I',str(source),'-I',"+repr(str(glue))+",*map(str,files)")
 anchor="  report['heap_trampoline_used']=not options.inline_selector";assert anchor in text
 inserted="""  semantic_calls=c.c_uint32.in_dll(runtime.lib,'biwn_deck_semantic_calls').value
  assert semantic_calls>0
  report['readable_Deck_coordinate_calls']=semantic_calls
  report['new_readable_caller']='0x11D1A..0x11E64'
  report['caller_authorship']=DECK_AUTHORSHIP
  report['prior_generated_caller_replaced']=True
  report['native_disc_changed']=False
  report['natural_unpatched_gameplay_verified']=False
"""
 text=text.replace(anchor,inserted.replace('DECK_AUTHORSHIP',repr(trial['authorship']))+anchor)
 # Existing driver hashes itself and file list, and writes its own isolated
 # current pointer. Its integration limits remain explicit in that receipt.
 runner=out/'pipeline-as-run.py';runner.write_text(text)
 state=dict(status='running',pid=os.getpid(),directory=str(out),template=str(template),template_sha256=sha(template),runner=str(runner),runner_sha256=sha(runner),generated_parent_source_sha256=sha(original),new_flow_source_sha256=sha(target),candidate=str(body),candidate_sha256=sha(body),component_receipt=str(out/'component-receipt.json'),whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/Deck-coordinate-pipeline-current.json',state)
 mark();command=[str(ROOT/'.venv/bin/python3.12'),str(runner),'--frames','16','--inline-selector','--inventory-entry','--exit-viewer','--world-entry','--world-loop'];state['command']=command
 try:
  with(out/'pipeline.log').open('w')as log:
   child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')});state['child_pid']=child.pid;mark();code=child.wait(timeout=600)
  state['child_pid']=None;state['exit_code']=code;assert code==0,(out/'pipeline.log').read_text()[-7000:]
  proof=ROOT/'verification/deck-coordinate-readable-world-loop-v2-current.json';report=read(proof)
  assert report['readable_Deck_coordinate_calls']>0 and report['original_CPU_GPU_on_C_path']is False
  state.update(status='terminal_readable_Deck_coordinate_source_world_loop_match',integration_proof=str(proof),integration_proof_sha256=sha(proof),readable_calls=report['readable_Deck_coordinate_calls'],paired_checkpoints=report['paired_checkpoints']);mark();print(state['status'],state['readable_calls'],'readablecalls',flush=True)
 except BaseException as e:state.update(status='terminal_pipeline_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

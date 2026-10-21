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
 out=ROOT/'verification/deck-face-contact-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 original=ROOT/'projects/black-ice-white-noise/restoration/experimental/mode3-flow/biwn_mode3_scene_flow_cpu.c'
 flow=original.read_text();start=flow.index('  case 0x11d1au:');end=flow.index('  case 0x11e62u:')
 removed=flow[start:end];assert '  case 0x11e6cu:'not in removed
 replacement='''  case 0x11d1au: /* Recovered structured Deck/C-Space caller, explicit services. */
   {struct biwn_deck_context deck={bus,s.cpu,service,context,4,0};
    biwn_deck_coordinate_body(&deck);CHECK(deck.error);s.cpu=deck.cpu;}
   biwn_deck_semantic_calls++;break;
'''
 flow='#include "deck-coordinate-contract.h"\n#include "deck-scene-contract.h"\n#include "deck-input-source.h"\nuint32_t biwn_deck_input_calls;\nuint32_t biwn_deck_semantic_calls;\nuint32_t biwn_deck_scene_calls[2];\n'+flow[:start]+replacement+flow[end:]
 scene=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-scene-source'
 scene_receipt=read(ROOT/'verification/Deck-scene-source-current.json');assert scene_receipt['completed']==512 and scene_receipt['status']=='terminal_two_readable_Deck_scene_callers_native_match'
 for p,h in scene_receipt['source_sha256'].items():assert sha(p)==h,p
 for index,entry,rts in [(0,'0x11828u','0x11868u'),(1,'0x11ad4u','0x11b4au')]:
  begin=flow.index('  case '+entry+':');stop=flow.index('  case '+rts+':')
  flow=flow[:begin]+('  case '+entry+': /* Complete structured Deck scene caller. */\n   CHECK(biwn_deck_scene_body(bus,&s.cpu,service,context,128));\n   biwn_deck_scene_calls['+str(index)+']++;break;\n')+flow[stop:]
 input_source=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-input-source'
 input_receipt=read(ROOT/'verification/Deck-input-source-current.json');assert input_receipt['completed']==2048
 for p,h in input_receipt['source_sha256'].items():assert sha(p)==h,p
 begin=flow.index('  case 0x11b4cu:');stop=flow.index('  case 0x11d18u:')
 flow=flow[:begin]+('  case 0x11b4cu: /* Complete structured Deck input caller. */\n   CHECK(biwn_deck_input_body(bus,&s.cpu,service,context,128));\n   biwn_deck_input_calls++;break;\n')+flow[stop:]
 task_source=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-task-source'
 task_receipt=read(ROOT/'verification/Deck-task-source-current.json')
 assert task_receipt['completed']==1280 and task_receipt['status']=='terminal_complete_readable_Deck_outer_task_original_CPU_match'
 for p,h in task_receipt['source_sha256'].items():assert sha(p)==h,p
 flow='#include "deck-task-source.h"\nuint32_t biwn_deck_outer_calls;\n'+flow
 begin=flow.index('  case 0x11e6cu:');stop=flow.index('  case 0x11f6au:')
 entries=[0x11e6c,0x11e86,0x11e8c,0x11ec4,0x11ed6,0x11edc,0x11ee4,0x11f12,0x11f1a,0x11f32,0x11f38,0x11f4a,0x11f50,0x11f58,0x11f5e,0x11f64]
 replacement=''.join('  case '+hex(pc)+'u:\n'for pc in entries)+'   {int deck_status=biwn_deck_task_resume(bus,&s.cpu,service,context,128,4096);\n    biwn_deck_outer_calls++;\n    if(deck_status==6&&s.cpu.pc==0x11e86u&&!stop_on_yield)break;\n    CHECK(deck_status);}break;\n'
 flow=flow[:begin]+replacement+flow[stop:]
 contact_source=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-face-contact'
 contact_receipt=read(ROOT/'verification/Deck-face-contact-current.json')
 assert contact_receipt['completed']==2112 and contact_receipt['status']=='terminal_complete_readable_Deck_face_contact_original_CPU_match'
 for p,h in contact_receipt['source_sha256'].items():assert sha(p)==h,p
 # Keep the original generated source/header beside this isolated variant.
 target=out/'biwn_mode3_scene_flow_cpu.c';target.write_text(flow)
 (out/'biwn_mode3_scene_flow_cpu.h').write_bytes(original.with_suffix('.h').read_bytes())
 (out/'removed-instruction-cases.c.txt').write_text(removed)
 (out/'component-receipt.json').write_text(Path(trial['receipt']).read_text())
 template=ROOT/'scripts/check_mode3_source_flow.py';text=template.read_text()
 anchor="proof_name='mode3-recorded-world-loop-roundtrip'"
 assert anchor in text
 line=next(x for x in text.splitlines()if x.lstrip().startswith(anchor))
 text=text.replace(line," proof_name='deck-face-contact-world-loop-v1'")
 old="source/'experimental/mode3-flow/biwn_mode3_scene_flow_cpu.c'"
 assert text.count(old)==1
 text=text.replace(old,"Path("+repr(str(target))+")")
 marker=";library=out/'libmode3-flow.dylib'";assert marker in text
 text=text.replace(marker,";files += [Path("+repr(str(body))+"),Path("+repr(str(glue/'deck-coordinate-adapter.c'))+"),Path("+repr(str(scene/'deck-scene-source.c'))+"),Path("+repr(str(input_source/'deck-input-source.c'))+"),Path("+repr(str(task_source/'deck-task-source.c'))+"),Path("+repr(str(contact_source/'deck-face-contact.c'))+")];library=out/'libmode3-flow.dylib'")
 text=text.replace("'-I',str(source),*map(str,files)","'-I',str(source),'-I',"+repr(str(glue))+",'-I',"+repr(str(scene))+",'-I',"+repr(str(input_source))+",'-I',"+repr(str(task_source))+",*map(str,files)")
 anchor="  report['heap_trampoline_used']=not options.inline_selector";assert anchor in text
 inserted="""  semantic_calls=c.c_uint32.in_dll(runtime.lib,'biwn_deck_semantic_calls').value
  assert semantic_calls>0
  report['readable_Deck_coordinate_calls']=semantic_calls
  outer_calls=c.c_uint32.in_dll(runtime.lib,'biwn_deck_outer_calls').value;assert outer_calls>0
  report['readable_Deck_outer_task_calls']=outer_calls
  report['new_readable_outer_task']='11E6C..11F6C'
  report['outer_authorship']='Coordinator structured recovery;source services remain explicit'
  input_calls=c.c_uint32.in_dll(runtime.lib,'biwn_deck_input_calls').value;assert input_calls>0
  report['readable_Deck_input_calls']=input_calls
  scene_calls=list((c.c_uint32*2).in_dll(runtime.lib,'biwn_deck_scene_calls'));assert all(scene_calls)
  report['readable_Deck_scene_calls']=scene_calls
  report['new_readable_scene_callers']=['11828..1186A','11AD4..11B4C']
  report['new_readable_caller']='0x11D1A..0x11E64'
  report['caller_authorship']=DECK_AUTHORSHIP
  report['prior_generated_caller_replaced']=True
  report['native_disc_changed']=False
  report['natural_unpatched_gameplay_verified']=False
"""
 text=text.replace(anchor,inserted.replace('DECK_AUTHORSHIP',repr(trial['authorship']))+anchor)
 # Bind the new helper directly: the old generated flow omitted its jump
 # table. Native runs the untouched original routine; C uses this body.
 anchor=" math=runtime.lib.biwn_startup_rng_math_cpu_body;"
 assert anchor in text
 text=text.replace(anchor," contact=runtime.lib.biwn_deck_face_contact_body;contact.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.world_cpu.SERVICE,c.c_void_p,c.c_uint32];contact.restype=c.c_int\n"+anchor)
 text=text.replace('phases={};results=[]','phases={};results=[];contact_samples={}')
 text=text.replace('events=[];bios=[];errors=[];trace=[]','events=[];bios=[];errors=[];trace=[];face_entries=[];face_returns=[];contact_samples[mode]=dict(entries=face_entries,returns=face_returns)')
 anchor='   def service(_,passed,state,target):'
 insertion="""   def contact_checkpoint(state):
    descriptor=runtime.device.read(0x400e6,4)&0xffffff
    count=runtime.device.read(descriptor+0x88,2)
    return dict(CPU=media.scheduler.cpu_dict(state),RAM=sha(runtime.device.ram()),descriptor=descriptor,descriptor_face_count=count,face_kinds=[runtime.device.read(descriptor+16+20*i,2)for i in range(min(count,6))])
"""
 assert anchor in text;text=text.replace(anchor,insertion+anchor)
 anchor='    if target==0xe26c:return cube(passed,state,10000)'
 replacement="""    if target==0x1186a:
     face_entries.append(contact_checkpoint(state.contents));status=contact(passed,state,service_cb,None,128);face_returns.append(contact_checkpoint(state.contents));return status
"""+anchor
 assert anchor in text;text=text.replace(anchor,replacement)
 anchor='      trace.append(pc)'
 replacement="""      if pc==0x1186a:face_entries.append(contact_checkpoint(runtime.cpu()))
      if pc==0x11ad2:face_returns.append(contact_checkpoint(runtime.cpu()))
"""+anchor
 assert text.count(anchor)>=1;text=text.replace(anchor,replacement,1)
 anchor="     mark('boundary_'+str(frame));frame+=1"
 assert anchor in text;text=text.replace(anchor,anchor+"\n     if frame==1:pads.set_buttons([0]) # Up: positive Deck speed, reaches1186A")
 anchor="  report['heap_trampoline_used']=not options.inline_selector"
 inserted="""  assert contact_samples['native']==contact_samples['C']
  contacts=contact_samples['C'];assert len(contacts['entries'])==len(contacts['returns'])>0
  assert any(row['descriptor_face_count']>0 for row in contacts['entries'])
  report['readable_Deck_face_contact_calls']=len(contacts['entries'])
  report['face_contact_original_C_checkpoints']=contact_samples
  report['face_contact_input']='Up held during sixteen Deck iterations,then source0key exit'
  report['face_contact_component_cases']=2112
"""
 assert anchor in text;text=text.replace(anchor,inserted+anchor)
 # Existing driver hashes itself and file list, and writes its own isolated
 # current pointer. Its integration limits remain explicit in that receipt.
 runner=out/'pipeline-as-run.py';runner.write_text(text)
 state=dict(status='running',pid=os.getpid(),directory=str(out),template=str(template),template_sha256=sha(template),runner=str(runner),runner_sha256=sha(runner),generated_parent_source_sha256=sha(original),new_flow_source_sha256=sha(target),candidate=str(body),candidate_sha256=sha(body),component_receipt=str(out/'component-receipt.json'),whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/Deck-face-contact-pipeline-current.json',state)
 mark();command=[str(ROOT/'.venv/bin/python3.12'),str(runner),'--frames','16','--inline-selector','--inventory-entry','--exit-viewer','--world-entry','--world-loop'];state['command']=command
 try:
  with(out/'pipeline.log').open('w')as log:
   child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')});state['child_pid']=child.pid;mark();code=child.wait(timeout=600)
  state['child_pid']=None;state['exit_code']=code;assert code==0,(out/'pipeline.log').read_text()[-7000:]
  proof=ROOT/'verification/deck-face-contact-world-loop-v1-current.json';report=read(proof)
  assert report['readable_Deck_coordinate_calls']>0 and report['original_CPU_GPU_on_C_path']is False
  state.update(status='terminal_readable_Deck_six_callers_positive_motion_world_loop_match',integration_proof=str(proof),integration_proof_sha256=sha(proof),face_contact_calls=report['readable_Deck_face_contact_calls'],outer_task_calls=report['readable_Deck_outer_task_calls'],readable_calls=report['readable_Deck_coordinate_calls'],paired_checkpoints=report['paired_checkpoints'],input_calls=report['readable_Deck_input_calls'],scene_calls=report['readable_Deck_scene_calls'],scene_component_receipt=str(ROOT/'verification/Deck-scene-source-current.json'));mark();print(state['status'],state['readable_calls'],'readablecalls',flush=True)
 except BaseException as e:state.update(status='terminal_pipeline_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

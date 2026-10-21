"""Publish unedited local source running in a shared native prototype, not a disc."""
import hashlib,json,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 packet=load(ROOT);packet.pop('proof_sha256',None)
 names=['native-Deck-local-clear-real-v1-current.json','native-deck-retained-local-clear-v1-current.json','native-local-clear-module-order-v1-current.json','native-local-clear-full-module-v1-current.json','native-local-clear-cost-v1-current.json']
 proofs=[read(V/name)for name in names]
 for proof in proofs:
  assert proof['status'].startswith('terminal_')
  for p,h in proof.get('source_sha256',{}).items():assert sha(p)==h,p
 geometry,retained,order,full,cost=proofs
 assert geometry['completed']==256 and retained['completed']==4992 and full['completed']==260 and full['budget_cases']==42
 assert geometry['payload_sha256']==full['payload_sha256']
 out=V/'native-local-clear-prototype-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name in names:shutil.copy2(V/name,out/name)
 report=ROOT/'reports/Local Model Shared Native Prototype Review.txt'
 facts=dict(status='terminal_unedited_local_clear_shared_native_prototype_correctness_pass_cost_regression_unpromoted',directory=str(out),report=str(report),entry='0x10968',raw_model_body_edited=False,new_predictions=0,new_training=False,shared_native_module_executed=True,module_bytes=geometry['code_bytes'],payload_sha256=full['payload_sha256'],geometry_cases=256,retained_caller_cases=4992,exact_body_original_cases=260,exact_body_budget_cases=42,ordered_body_trace='Independent Unicorn exact linked bytes compared with raw portable body for all260normal and42budget cases',maximum_geometry_C_stack_bytes=164,reserved_geometry_C_stack_bytes=176,comparisons=cost['comparisons'],disc_integrated=False,installed_preview_changed=False,fresh_gameplay_tested=False,final_address_disc_gates_verified=False,fidelity_verified=False,decision='Keep the optimized coordinator routine in the current disc. The unedited local body is correct in this prototype but its measured clear loop costs about2.9times as many emulated cycles.',scope='One local Repair body plus coordinator primitives, native bus/ALU profile and symbol-only rename. Four actual geometry-entry captures independently qualify ordered body accesses. The full raw-body matrix compares logical CPU/publicRAM/order and physical callee-saved registers/private fences;native directbus cannot inject host callback failures. Geometry256 includes original formatter/text and blitter but GPU submission remains a declared fixture. Retained4992 plus16fallback controls pass. No final-address/whole-module fallback/aliases/outer/fresh-disc qualification is implied. Emulator cycle samples are not physical console timing. No whole-game or broader model-quality claim.')
 save(out/'facts.json',facts)
 report.write_text('LOCAL MODEL — SHARED NATIVE PROTOTYPE\n\nThe existing unedited10968Repair body now executes inside a40064byte native geometry prototype. Symbol rename only;coordinator typed primitives/native bus and ALU profile are declared dependencies.256geometry cases with real originalformatter/text/blitter and4992retained callers pass;164/176bytes observed geometry C stack. Exact linkedbody passes260originalCPU/publicRAM/ordered-access cases and42partial-budget cases,including boundarycounts/allCCR/bothbanks. Physical callee-saved registers/contextmetadata/privatefences remain intact.\n\nPerformance prevents promotion:sample clear-loop costs181622emulatedcycles versus62708optimized and16246original. Wholegeometry samples are1.61..2.29times slower than the optimized candidate. These are pinned-emulator instructioncosts,notphysicalconsolemeasurements. The currentdisc andinstalledpreview retain their prior implementations. No new predictions/training ordiscbuild.\n\nRemaining:qualifyperformance andnativeintegrationbeforeadoption;whole-module/finaladdress/fallback/alias/outer/freshgameplaygates are not supplied by these componenttests. Fullgame source rebuilding andfidelity remain incomplete.\n\n'+facts['scope']+'\n\nEvidence:'+str(out)+'\n')
 deps=[Path(__file__),out/'facts.json',report,*[out/name for name in names]]
 pub=V/'native-local-clear-prototype-reviewed-v1-current.json';save(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),dependencies_sha256={str(p):sha(p)for p in deps},whole_objective_complete=False))
 wrapper_path=V/'native-Deck-current-status-v1-current.json';wrapper=read(wrapper_path);save(out/'before-wrapper.json',wrapper);save(out/'before-packet.json',packet)
 packet['local_native_module_prototype']=facts
 packet['latest_local_source_generation_trial'].update(shared_native_module_executed=True,shared_native_module_bytes=40064,shared_native_original_cases=260,shared_native_budget_cases=42,shared_native_geometry_cases=256,shared_native_retained_cases=4992,shared_native_geometry_stack_bytes=164,shared_native_performance_approved=False,shared_native_review=str(pub),shared_native_report=str(report),native_disc_integrated=False)
 packet['checked_current_summary']+=' The unedited local10968Repair also passes shared-native component execution,including260fullbody/42budget cases and164/176byte geometry stack;its clear loop is about2.9times slower than the optimized routine,so remains outside the disc.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();pp=out/'current-status-packet.json';save(pp,packet);wrapper['packet']=str(pp);wrapper['dependencies_sha256'].update({str(p):sha(p)for p in [pp,pub,*deps]});save(wrapper_path,wrapper);load(ROOT)
 print(facts['status']);print(report)
if __name__=='__main__':main()

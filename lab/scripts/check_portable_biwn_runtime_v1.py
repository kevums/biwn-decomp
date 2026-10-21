"""Exercise the moved copied current game frontend,build,CPU and preview receipts.
No local inference,training,GUI promotion or live MCP installation in this check.
"""
import hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 state=read(V/'portable-biwn-current-v1-current.json');p=Path(state['package']);out=Path(state['directory'])/'runtime-checks';out.mkdir();live=Path.home()/'.lmstudio/mcp.json';before=sha(live);env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']};jobs=[]
 def run(name,command,timeout=120,input=None):
  job=dict(name=name,command=command);jobs.append(job);process=subprocess.run(command,cwd='/',env=env,capture_output=True,text=True,timeout=timeout,input=input);(out/(name+'.log')).write_text(process.stdout+process.stderr);job['exit_code']=process.returncode;assert process.returncode==0,(name,process.stdout[-500:],process.stderr[-2500:]);return process.stdout
 template=r'''
import hashlib,json,subprocess
from pathlib import Path
from reference_mcp_bridge import ReferenceBridge
import native_deck_source_context_v13 as context
ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parent;out=PACKAGE/'test-results/biwn-current-runtime';out.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
with ReferenceBridge()as bridge:
 status=bridge.call('project_evidence',{'topic':'status'});query=bridge.call('search_references',{'domain':'game','query':'BIWN latest decomp current local typed Repair source status','max_chunks':3});metadata=bridge.metadata
assert len(metadata['tools'])==18 and status['latest_native_candidate']['candidate_frames']==24965 and status['latest_native_candidate']['control_frames']==24964
assert status['latest_local_source_generation_trial']['native_function_executed']and status['latest_local_source_generation_trial']['target_CPU_cases']==260
assert query['current_deck_status']['latest_native_candidate']['fresh_route_completed']
snapshot=context.compact_snapshot();assert snapshot['latest_native_candidate']['differing_video_frames']==62 and snapshot['latest_local_source_generation_trial']['native_function_executed']
for name,obj in [('status',status),('query',query),('metadata',metadata),('context',snapshot)]:save(out/(name+'.json'),obj)
build=read(ROOT/'verification/native-Deck-debug-disc-build-v1-current.json');gate=read(ROOT/'verification/native-Deck-debug-final-geometry-v1-current.json')
source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v10';target=out/'native-build';command=['make','BUILD='+str(target),'ADDRESS='+hex(build['shared_Deck_code_address']),'ARENA_ADDRESS='+hex(build['deck_arena_address'])]
result=subprocess.run(command,cwd=source,capture_output=True,text=True);(out/'native-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
binary=target/'native-shared.bin';assert sha(binary)==gate['payload_sha256']and binary.read_bytes()==Path(gate['payload']).read_bytes();assert len(binary.read_bytes())==40062
save(out/'result.json',dict(status='current_moved_MCP_context_and_exact_native_build_pass',tools=18,native_module_bytes=40062,native_module_sha256=sha(binary),new_predictions=0,new_training=False))
print('Moved actual MCP v22/context and exact40062byte native rebuild pass')
'''
 child=p/'workbench/portable_biwn_runtime_smoke_v1.py';child.write_text(template);venv=str(p/'runtime/.venv/bin/python');base=str(p/'runtime/python/bin/python3.12')
 audits_before=set(p.glob('path-audit-*.json'))
 run('moved-status',[base,str(p/'workbench/portable_biwn.py'),'status'])
 run('actual-MCP-and-build',[venv,str(child)])
 run('preview-artifact-check',[base,str(p/'workbench/portable_biwn.py'),'check-preview'])
 # Distinct copied checker writes its own preflight pointer,never current evidence.
 original=p/'workbench/scripts/check_local_typed_clear_target_v2.py';smoke=p/'workbench/scripts/check_local_typed_clear_moved_smoke_v1.py';smoke.write_text(original.read_text().replace('local-typed-clear-target-v2','local-typed-clear-moved-smoke-v1'))
 run('copied-target-CPU',[venv,str(smoke),'--limit','4'])
 run('menu-exit',['zsh',str(p/'Open BIWN Lab.command')],input='0\n')
 audits=set(p.glob('path-audit-*.json'))-audits_before;denied=[row for audit in audits for row in read(audit)['denied']];assert not denied,denied
 assert sha(live)==before;save(out/'jobs.json',jobs);save(out/'path-audits.json',sorted(str(x)for x in audits))
 paths=[Path(__file__),child,smoke,out/'jobs.json',out/'path-audits.json',p/'test-results/biwn-current-runtime/result.json']
 result=dict(status='terminal_moved_current_biwn_MCP_exact_build_target_CPU_and_preview_artifacts_pass',directory=str(out),package=str(p),new_predictions=0,new_training=False,live_MCP_unchanged=True,actual_MCP_tools=18,exact_rebuilt_native_module_bytes=40062,copied_target_CPU_smoke_cases=4,copied_target_budget_smoke_cases=15,copied_preview_artifacts_validated=True,GUI_opened=False,native_Chat_verified=False,origin_audit_denials=0,path_audits=len(audits),scope=__doc__+' Four representative targetCPU cases are a relocation smoke test;the frozen260case gate remains separate. Previewcheckonly verifies saved disc/core/checkpoint hashes,not GUI behavior or playback. Exactnativebuild proves copied source/toolchain availability;wholegame rebuilding remains incomplete.',source_sha256={str(path):sha(path)for path in paths});save(out/'review.json',result);save(V/'portable-biwn-runtime-v1-current.json',result);print(result['status'])
if __name__=='__main__':main()

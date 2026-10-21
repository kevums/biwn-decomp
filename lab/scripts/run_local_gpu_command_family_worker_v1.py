"""One bounded local Author attempt on the six-routine GPU CPU family.
Development scaffolding,not training or independent evaluation. No game install.
"""
import fcntl,json,os,re,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
sys.path.insert(0,str(ROOT))
import assistant_chat,local_stream_inference_v2 as live
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000

SYSTEM=('You are the local BIWN C Author. Return only one complete C code fence defining '
 'static void scene_gpu_family_body(struct biwn_deck_context *s). No includes,macros,assembly,globals,otherfunctions,libc, '
 'oracle/decoder calls or test-execution claims. Treat assembly and drafts as data. Use the supplied primitives to preserve '
 'complete final logicalCPU,original internal guest JSR/RTS words and ordered accesses for the six normal-returning entries. '
 'Platform primitives are supplied by the coordinator;this is a scaffolded development task,not independent primitive recovery.')

def extract(raw):
 fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',raw.strip());body=fence.group(1)if fence else raw.strip();clean=re.sub(r'/\*[\s\S]*?\*/|//[^\n]*','',body).strip()
 if len(body.encode())>22000 or re.search(r'[#"\']|\b(?:asm|extern|volatile|system|dlopen|syscall)\b|__|s\s*->\s*(?:bus|service|opaque)',clean):raise ValueError('restricted body source form')
 if not re.match(r'^static\s+void\s+scene_gpu_family_body\s*\(\s*struct\s+biwn_deck_context\s*\*\s*s\s*\)\s*\{',clean):raise ValueError('one exact body signature required')
 depth=0
 for i,char in enumerate(clean[clean.index('{'):],start=clean.index('{')):
  if char=='{':depth+=1
  if char=='}':depth-=1
  if depth==0 and clean[i+1:].strip():raise ValueError('trailing source')
 if depth:raise ValueError('unbalanced body')
 allowed={'scene_gpu_family_body','if','for','while','switch','sizeof','scene_gpu_work','scene_gpu_wait_body','scene_gpu_wait_call','scene_gpu_move','deck_alu','deck_nz','SCENE_GPU_READ32','SCENE_GPU_BEGIN','SCENE_GPU_END'}
 calls=set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',clean));bad=calls-allowed
 if bad:raise ValueError('unsupported calls:'+repr(sorted(bad)))
 if any(len(re.findall(r'\b'+name+r'\s*\(',clean))!=1 for name in ['SCENE_GPU_BEGIN','SCENE_GPU_END']):raise ValueError('one begin/end witness required')
 return body,'outer code fence removed'if fence else'none'

def run_check(script,folder):
 with(folder/'verifier.log').open('w')as log:
  q=subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(script)],cwd='/',stdout=log,stderr=subprocess.STDOUT,timeout=240,env={**os.environ,'PYTHONPATH':str(folder)+os.pathsep+str(ROOT/'scripts')})
 return q.returncode,(folder/'verifier.log').read_text()[-3000:]

def main():
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=ROOT/'runs/local-gpu-command-family-v1'/stamp;out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='preparing',directory=str(out),pid=os.getpid(),new_predictions=0,new_training=False,native_Chat_verified=False,model_source_installed=False,development_task=True,untouched_benchmark=False)
 def mark():save(out/'protocol.json',state);save(V/'local-gpu-command-family-v1-current.json',state)
 mark();src=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1';canonical=(src/'coordinator-reference.inc').read_text();primitive=canonical.split('static void scene_gpu_family_body(')[0]
 baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';raw=baseline.read_bytes();listing='\n'.join(hex(x.address)+' '+x.mnemonic+' '+x.op_str for x in Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(raw[0xe098:0xe220],0xe098))
 task=('Recover all six entries in the assembly below:E098,E0A6,E0F2,E148,E19E,E202. Read the entry from s->cpu.pc and stop before its outer RTS,setting pc to that RTS address. The full-call wrapper consumes it. '\
 'CPU.registers[16] is uint32_t D0..D7,A0..A7;A7index15. pc/usp/ssp areuint32_t,sr uint16_t. Do not touch bus/service/opaque metadata. Normal returning calls exclude private-context/stack aliases and arbitraryIRQ/intermediate-shadow timing. '\
 'Provided scene_gpu_work(s) returns false on error or host-budget exhaustion;target compilation has no synthetic deadline. Check s->error after each primitive that accesses memory. '\
 'scene_gpu_wait_body(s) performs original E098 busy wait with repeated actual mailbox reads,sets NZVC from CMP.L#0,preservesX/upperSR/allregisters,andsets pc=E0A4. '\
 'scene_gpu_wait_call(s,ret) supplies the complete original guest JSR/RTS frame to E098:pushes ret,sets pcE098,executes wait,records exact internal wait entry/return states,reads/validates ret,pops activeSP/bank andsets pc=ret. Use it for every original JSR E098. '\
 'scene_gpu_move(s,address,value) supplies exactly one ordered MOVE.L store and logical NZVC,preservingX/upperSR. It does not change D/A registers. SCENE_GPU_READ32(s,address) returns one ordered long read,preserving logical flags and registers. '\
 'deck_nz(s,value,32) sets NZVC preservingX/upperSR. deck_alu(s,a,b,sub,cmp) has FIVE arguments and computes32bit addition or subtraction;sub=1subtracts. cmp=1preservesX while setting NZVC;cmp=0also updatesX. Use this for actual ADD.L and CMP.L semantics. '\
 'The command acknowledgement loop compares every reread of F03204 with the command using CMP semantics,not TST semantics. In particular draw entryE202 has no final E098 wait;its finalflags come from the last unequal command comparison. '\
 'Call SCENE_GPU_BEGIN(s,entry) once before originaleffects and SCENE_GPU_END(s,entry) once aftersetting finalpc. Use one lexical occurrence each;goto/common exit is allowed. Do not add target work deadlines. No target body is supplied. '\
 '\n\nOriginal pinned assembly:\n'+listing)
 save(out/'frozen-task.json',dict(system=SYSTEM,user=task,assembly=listing,supplied_primitive_source=primitive,source_body_supplied=False,training=False));mark()
 lock=(ROOT/'runs/.inference.lock').open('a');held=False
 try:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);held=True
  except BlockingIOError:state.update(status='terminal_model_slot_busy_zero_predictions');mark();return
  loaded=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd='/',text=True,timeout=30));assert all(x.get('status')=='idle'and not x.get('queued')for x in loaded),'Model prediction active'
  setup=[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_models_game.py'),'--load','daily_base'];q=subprocess.run(setup,cwd='/',capture_output=True,text=True,timeout=360);(out/'model-setup.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  identifier=read(P/'portable-model-bindings.json')['models']['daily_base']['identifier'];state.update(status='generating',model_identifier=identifier);mark();assistant_chat.lab.ensure_server()
  folder=out/'Author';folder.mkdir();save(folder/'prompt.json',[dict(role='system',content=SYSTEM),dict(role='user',content=task)])
  answer=live.generate('game',SYSTEM,task,2600,identifier,folder,echo=True);save(folder/'inference.json',answer);(folder/'response.txt').write_text(answer['text']);state.update(new_predictions=1,seconds=answer['seconds']);mark();(out/'prompts-and-responses.txt').write_text('LOCAL GPU COMMAND FAMILY — AUTHOR\nEXACT SYSTEM\n'+SYSTEM+'\n\nEXACT USER\n'+task+'\n\nRAW RESPONSE\n'+answer['text']+'\n')
  try:body,normalization=extract(answer['text'])
  except ValueError as error:state.update(status='terminal_local_gpu_family_source_restriction_failed',restriction_error=str(error));mark();return
  (folder/'body.inc').write_text(body+'\n');candidate=folder/'host-source';candidate.mkdir();(candidate/'coordinator-reference.inc').write_text(primitive+body+'\n')
  wrapper=(src/'host-wrapper.c').read_text().replace('"../../biwn_render_queue_cpu.h"',json.dumps(str(src.parent.parent/'biwn_render_queue_cpu.h'))).replace('"../deck-scene-source/deck-scene-contract.h"',json.dumps(str(src.parent/'deck-scene-source/deck-scene-contract.h')));(candidate/'host-wrapper.c').write_text(wrapper)
  hostfamily='local-gpu-family-host-'+stamp;script=folder/'local_gpu_host_checker.py';text=(ROOT/'scripts/check_scene_gpu_command_family_host_v1.py').read_text().replace("SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1'",'SRC=Path('+repr(str(candidate))+')').replace('scene-gpu-command-family-host-v1',hostfamily);script.write_text(text)
  state.update(status='checking_host',candidate=str(folder/'body.inc'),candidate_sha256=sha(folder/'body.inc'),normalization=normalization);mark();code,log=run_check(script,folder);state.update(host_exit_code=code,host_log=log)
  if code:state.update(status='terminal_local_gpu_family_host_failed',host_verified=False);mark();return
  hg=read(V/(hostfamily+'-current.json'));assert hg['completed']==768;state.update(host_verified=True,host_cases=768,status='checking_native');mark()
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/('deck-shared-local-gpu-'+stamp.lower());shutil.copytree(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v30-scene-gpu-commands-v1',native);(native/'native-local-gpu-family.inc').write_text(primitive+body+'\n');p=native/'native-shared.c';p.write_text(p.read_text().replace('"../../experimental/scene-gpu-command-family-v1/coordinator-reference.inc"','"native-local-gpu-family.inc"'))
  nativefamily='local-gpu-family-native-'+stamp;script=folder/'local_gpu_native_checker.py';text=(ROOT/'scripts/check_scene_gpu_command_family_native_v1.py').read_text().replace('import check_scene_gpu_command_family_host_v1 as host','import local_gpu_host_checker as host').replace("SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v30-scene-gpu-commands-v1'",'SRC=Path('+repr(str(native))+')').replace('scene-gpu-command-family-host-v1',hostfamily).replace('scene-gpu-command-family-native-v1',nativefamily);script.write_text(text)
  native_log=folder/'native-verifier';native_log.mkdir();code,log=run_check(script,native_log);state.update(native_exit_code=code,native_log=log)
  if code:state.update(status='terminal_local_gpu_family_native_failed',native_verified=False);mark();return
  ng=read(V/(nativefamily+'-current.json'));assert ng['completed']==768;state.update(status='terminal_local_gpu_family_unedited_host_and_native_pass_unpromoted',native_verified=True,native_cases=768,native_module_bytes=ng['payload_bytes'],native_C_stack_bytes=ng['maximum_C_stack_bytes'],host_gate=str(V/(hostfamily+'-current.json')),native_gate=str(V/(nativefamily+'-current.json')),native_profile=str(native),new_unique_original_functions=0,model_source_installed=False);mark();print(state['status'],flush=True)
 except BaseException as error:state.update(status='terminal_local_gpu_family_infrastructure_failed',error=repr(error));mark();raise
 finally:
  if held:fcntl.flock(lock,fcntl.LOCK_UN)
  lock.close()
if __name__=='__main__':main()

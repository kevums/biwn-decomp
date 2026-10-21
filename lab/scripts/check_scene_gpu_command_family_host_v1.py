"""Six structured CPU mailbox routines versus original68000 and Unicorn.
GPU busy/ack values are declared device inputs, not executing GPU programs.
"""
import argparse,ctypes as c,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_render_queue_cpu as queue
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
CPU=queue.CPU;SP=queue.SP;STOP=queue.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1'
ENTRIES={0xe098:0xe0a4,0xe0a6:0xe0f0,0xe0f2:0xe146,0xe148:0xe19c,0xe19e:0xe200,0xe202:0xe21e}
HEADERS={0xe0a6:0x4d80,0xe0f2:0x6ae0,0xe148:0x6da0,0xe19e:0x52e0,0xe202:0x57a0}
POLL={0xe0de,0xe134,0xe18a,0xe1ee,0xe212}
queue.ENTRIES={0xe098};queue.RETURNS={0xe0a4};queue.SCRIPTS=set()
EVENT=c.CFUNCTYPE(None,c.c_uint,c.POINTER(CPU))

class Runtime(queue.Runtime):
 def __init__(self,*args):
  super().__init__(*args);self.events=[]
  self.event=EVENT(self.observe);self.lib.lab_scene_gpu_set_observer.argtypes=[EVENT];self.lib.lab_scene_gpu_set_observer(self.event)
 def observe(self,kind,cpu):
  value=queue.cd.scheduler.cpu_dict(cpu.contents)
  if kind==0:self.calls.append(dict(target=0xe098,actual_body=True,incoming=value))
  else:self.calls[-1]['return']=value
 def write(self,a,w,v):
  if a==0xf03204:
   assert w==4;self.trace.append(['w',a,w,v]);self.core.GPUWriteLong(a,v,0);return
  return super().write(a,w,v)
 def native(self,ram,case,coverage):
  self.reset(ram,case,0);queue.lifecycle.seed_cpu(self,queue.make_cpu(case));steps=[];stack=[];pending=False
  for _ in range(20000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP or(case['body']and pc==case['outer_RTS']):break
   assert pc in self.rows,hex(pc)
   if pending and pc==0xe098:
    row=dict(target=pc,actual_body=True,incoming=queue.cd.scheduler.cpu_dict(self.cpu()));self.calls.append(row);stack.append(row);pending=False
   if pc==0xe0a4 and stack:stack.pop()['return']=queue.cd.scheduler.cpu_dict(self.cpu())
   if self.rows[pc]['assembly'].startswith('jsr '):pending=True
   if pc==0xe098:self.inject(0xf03200,4)
   if pc in POLL:self.inject(0xf03204,4)
   coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
  else:raise AssertionError('Original GPU command family exceeded fixture bound')
  assert not stack
  return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())

def cases():
 rng=random.Random(0xe098e220);rows=[]
 for n in range(128):
  for entry,outer in ENTRIES.items():
   sup=bool((n//32)%2);header=HEADERS.get(entry,0)
   final=[0xffffffff,0,1,0x80000000,0x7fffffff,header-1,header+1,header^0x80000000][n%8]&0xffffffff
   busy=[1,0x80000000,0xffffffff][n%3]
   queues=[dict(address=0xf03200,width=4,values=[busy]*(n%4)+[0]+[busy]*((n//4)%4)+[0])]
   if header:queues.append(dict(address=0xf03204,width=4,values=[header]*(n%3)+[final]))
   rows.append(dict(id=len(rows),entry=entry,outer_RTS=outer,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if sup else 0)|((n%8)<<8)|(n%32),usp=0x170000 if sup else SP,ssp=SP if sup else 0x1d0000,body=n>=64,render=False,read_queues=queues,record_count=[0,1,59,0x7fffffff,0x80000000,0xffffffff,rng.getrandbits(32),0x12345678][n%8],scene_pointer=rng.getrandbits(32),sector=rng.getrandbits(32)))
 return rows

def fixture(snapshot,case):
 ram=bytearray(snapshot);ram[SP:SP+4]=STOP.to_bytes(4,'big')
 for a,k in [(0x49b88,'record_count'),(0x49c18,'scene_pointer'),(0x49c1c,'sector')]:ram[a:a+4]=case[k].to_bytes(4,'big')
 return bytes(ram)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=V/'scene-gpu-command-family-host-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  library=out/'gpu-command-family.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(SRC/'host-wrapper.c'),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();instructions,_=queue.cd.gen.base.binary_tools.m68k_instructions(snapshot[0xe098:0xe220],0xe098)
  runtime=Runtime(library,instructions);vectors=cases();vectors=vectors[:args.limit]if args.limit else vectors;rows=[];coverage=set()
  for case in vectors:
   ram=fixture(snapshot,case);left,expected,original=runtime.native(ram,case,coverage);independent,other,uc=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
   valid=not rebuilt['status']and bytes(expected)==bytes(other)==bytes(actual)and left==independent==right and uc['trace']==rebuilt['trace']and original['calls']==rebuilt['calls']
   if not valid:
    save(out/'counterexample.json',dict(case=case,original_CPU=queue.cd.scheduler.cpu_dict(expected),Unicorn_CPU=queue.cd.scheduler.cpu_dict(other),rebuilt_CPU=queue.cd.scheduler.cpu_dict(actual),original=original,Unicorn=uc,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:24]));raise AssertionError(out/'counterexample.json')
   rows.append(dict(case=case['id'],entry=hex(case['entry']),body=case['body'],CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),ordered_bus_events=len(rebuilt['trace']),internal_wait_calls=len(rebuilt['calls']),full_CPU_2MB_RAM_private_returns_order_and_wait_states_match=True));state.update(status='checking',completed=len(rows));mark()
   if len(rows)%64==0:print('GPU family host',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows);save(out/'vectors.json',vectors)
  if not args.limit:
   assert len(coverage)==len(instructions),(len(coverage),len(instructions))
   for entry in ENTRIES:assert len({(x['CCR'],x['supervisor'],x['body'])for x in rows if x['entry']==hex(entry)})==128
  guards=[];case=cases()[1];ram=fixture(snapshot,case)
  for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
   _,_,d=runtime.translated(ram,case,**options);assert d['status']==1 and d['CPU_unchanged']and not d['trace'];guards.append(dict(options=options,status=1))
  for options,status in [(dict(bad_pc=True),7),(dict(budget=1),4),(dict(fail=('read',4)),2),(dict(fail=('write',4)),2)]:
   _,_,d=runtime.translated(ram,case,**options);assert d['status']==status and d['CPU_unchanged'],(options,d);guards.append(dict(options=options,status=status))
  corrupt={**case,'read_queues':case['read_queues']+[dict(address=SP-4,width=4,values=[0])]};_,_,d=runtime.translated(ram,corrupt);assert d['status']==5 and d['CPU_unchanged'];guards.append(dict(corrupt_return=True,status=5));save(out/'guards.json',guards)
  paths=[Path(__file__),Path(queue.__file__),*SRC.iterdir(),library,out/'cases.json',out/'vectors.json',out/'guards.json',ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-update-v2/deck-coordinate-contract.h']
  state.update(status='terminal_six_gpu_command_structured_host_preflight'if args.limit else'terminal_six_gpu_command_structured_dual_CPU_RAM_bus_and_wait_states_pass',library=str(library),host_guards=len(guards),source_instruction_coverage=[len(coverage),len(instructions)],entries=[hex(x)for x in ENTRIES],source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' AllCCR/bothbanks/body+fullcall,full2MBRAM including internalguestJSRwords and orderedread/write widths/values. InternalwaitCPUentry/returnstatescompare. No targetCPU/code-size/game/IRQ/asyncGPU/console proof;target loops are unbounded while host callbacks retain finite budgets. Valid normal calls exclude private-context/stack alias corruption. Six existing recovered functions are structured together,zero new unique original functions.')
  mark()
  if not args.limit:save(V/'scene-gpu-command-family-host-v1-current.json',state)
  print(state['status'],len(rows),len(guards),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:
  if runtime:runtime.close()
if __name__=='__main__':main()

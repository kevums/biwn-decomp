"""Added host errors leave CPU continuation unchanged and retain prior stores."""
import ctypes as c,json,sys
from datetime import datetime,timezone
from pathlib import Path
import task_runtime_C as runtime
original=runtime.original;scheduler=original.scheduler;world=runtime.world;ROOT=original.ROOT
def main():
 library=Path(sys.argv[1]).resolve();assert library.is_relative_to(ROOT/'verification/biwn-task-runtime')
 lib=c.CDLL(str(library));step=lib.biwn_task_loop_step;step.argtypes=[c.POINTER(world.Bus),c.POINTER(scheduler.CPU),runtime.BODY,c.c_void_p,c.c_uint32];step.restype=c.c_int
 success=runtime.BODY(lambda context,bus,cpu:0);failure=runtime.BODY(lambda context,bus,cpu:1);rows=[]
 for label in ['null_bus','null_cpu','wrong_mode','zero_limit','missing_body','unsupported_PC','failed_write','failed_read','body_failure','bad_vector']+['missing_'+str(i)for i in range(4)]:
  memory=bytearray(0x200000);trace=[];cpu=original.initial_cpu([0x12340000+i for i in range(16)]);expected=1
  if label=='wrong_mode':cpu.sr|=0x2000
  if label=='unsupported_PC':cpu.pc=0xdead;expected=5
  if label=='bad_vector':cpu.pc=0xf360;expected=4
  if label in ['failed_write','failed_read']:expected=2
  if label=='body_failure':expected=3
  before=bytes(cpu)
  def reader(width):
   def call(_,a,v):
    if label=='failed_read':return 1
    if a>len(memory)-width:return 1
    v[0]=int.from_bytes(memory[a:a+width],'big');trace.append(['r',a,width,v[0]]);return 0
   return call
  def writer(width):
   def call(_,a,v):
    if label=='failed_write':return 1
    if a>len(memory)-width:return 1
    memory[a:a+width]=v.to_bytes(width,'big');trace.append(['w',a,width,v]);return 0
   return call
  types=[world.R16,world.R32,world.W16,world.W32];callbacks=[types[0](reader(2)),types[1](reader(4)),types[2](writer(2)),types[3](writer(4))]
  if label.startswith('missing_')and label!='missing_body':i=int(label.split('_')[1]);callbacks[i]=types[i]()
  bus=world.Bus(world.R8(),*callbacks,world.CALL(),None,0)
  status=step(None if label=='null_bus'else c.byref(bus),None if label=='null_cpu'else c.byref(cpu),runtime.BODY()if label=='missing_body'else failure if label=='body_failure'else success,None,0 if label=='zero_limit'else 64)
  assert status==expected and bytes(cpu)==before,(label,status,expected)
  if label in ['body_failure','failed_read','bad_vector']:assert any(x[0]=='w'for x in trace)
  elif label!='failed_write':assert not trace
  rows.append({'guard':label,'status':status,'CPU_unchanged':True,'partial_trace':trace})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fourteen_task_loop_host_guards_passed','library':str(library),'source_sha256':{name:world.select.binary_tools.sha(ROOT/'projects/black-ice-white-noise/restoration'/name)for name in ['biwn_task_loops.c','biwn_task_loops.h']},'guards':rows,'scope':'Added host errors/unsupported cases, not original game behavior or general task dispatch.'};(ROOT/'verification/task-loop-host-guards.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'host_guards':len(rows)}))
if __name__=='__main__':main()

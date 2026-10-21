"""Attach-only clocked-scheduler backend: captured-frame input guards."""
import ctypes as c
from datetime import datetime,timezone
import json,os,subprocess
from pathlib import Path
import numpy as np
from check_biwn_coordinate_task_execution import ROOT,DTYPE,cpu_record,sha,save,scheduler,flow,Ticket
from check_biwn_coordinate_yield import Memory

def main():
 out=ROOT/'verification/coordinate-yield-attach'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 proof=json.loads((ROOT/'verification/natural-coordinate-scheduler-current.json').read_text());folder=Path(proof['directory']);plan=json.loads((folder/'capture-plan.json').read_text());first=plan['first'];captures=folder/'captures'
 before=(captures/f'{first}.ram').read_bytes();entry=np.frombuffer((captures/f'{first}.cpu').read_bytes(),dtype=DTYPE)[0]
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libattach.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_coordinate_yield_attach.c'),str(source/'biwn_coordinate_yield.c'),str(source/'biwn_scheduler.c'),'-o',str(library)]
 result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 lib=c.CDLL(str(library));attach=lib.biwn_coordinate_yield_attach
 attach.argtypes=[c.POINTER(scheduler.cleanup.world.Bus),c.POINTER(Ticket),c.POINTER(flow.Request),c.POINTER(scheduler.CPU)];attach.restype=c.c_int
 guards=[]
 def call(name,expected=2,change_request=None,change_cpu=None,change_ram=None,active=False,missing=False,fail=None,null=None):
  memory=Memory(before,fail_at=fail);ticket=Ticket();cpu=scheduler.make_cpu(cpu_record(entry));request=flow.Request(11,12,7,0xdf60,0,0,0,cpu.registers[0])
  if change_request:change_request(request)
  if change_cpu:change_cpu(cpu)
  if change_ram:change_ram(memory.memory)
  if active:ticket.phase=1
  if missing:memory.bus.read32=type(memory.bus.read32)()
  snapshots=(bytes(ticket),bytes(cpu),bytes(memory.memory),bytes(request));args=[c.byref(memory.bus),c.byref(ticket),c.byref(request),c.byref(cpu)]
  if null is not None:args[null]=None
  result=attach(*args);assert result==expected,(name,result)
  assert bytes(cpu)==snapshots[1]and bytes(memory.memory)==snapshots[2]and bytes(request)==snapshots[3]
  assert not any(event[0]=='w'for event in memory.trace)
  if expected!=0:assert bytes(ticket)==snapshots[0]
  if expected==2:assert not memory.trace
  if expected==0:
   assert len(memory.trace)==2 and ticket.owner==proof['coordinate_owner']and ticket.return_sp==cpu.registers[15]+4
  guards.append(dict(case=name,status=result,no_guest_or_request_change=True,no_writes=True,ticket_unchanged_on_error=expected!=0))
 call('actual_frame',expected=0)
 for field,value in [('context',0),('sequence',0),('kind',3),('address',0xdf22),('argument_count',1),('incoming_d0',int(entry['registers'][0])^1)]:call('bad_'+field,change_request=lambda request,f=field,v=value:setattr(request,f,v))
 for index in range(4):call('null_'+str(index),null=index)
 call('already_active',active=True);call('missing_read32',missing=True)
 call('wrong_PC',expected=3,change_cpu=lambda cpu:setattr(cpu,'pc',0xdf64))
 call('supervisor',expected=3,change_cpu=lambda cpu:setattr(cpu,'sr',cpu.sr|0x2000))
 call('stack_wrap',expected=3,change_cpu=lambda cpu:cpu.registers.__setitem__(15,0xfffffffe))
 sp=int(entry['registers'][15])
 call('wrong_return',expected=3,change_ram=lambda ram:ram.__setitem__(slice(sp,sp+4),(0x19760).to_bytes(4,'big')))
 call('null_owner',expected=3,change_ram=lambda ram:ram.__setitem__(slice(0xc0920,0xc0924),bytes(4)))
 for index in [1,2]:call('read_failure_'+str(index),expected=4,fail=index)
 report=dict(status='attach_only_backend_guards_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(guards),library=str(library),library_sha256=sha(library),compile_command=command,source_sha256={str(source/name):sha(source/name)for name in ['biwn_coordinate_yield_attach.c','biwn_coordinate_yield_attach.h','biwn_coordinate_yield.c','biwn_coordinate_yield.h','biwn_scheduler.c','biwn_scheduler.h','biwn_coordinate_flow.h','biwn_world_update.h']},guest_CPU_or_RAM_writes=False,scope='Actual captured coordinate frame and argument/error guards; this component attaches a ticket without dispatching. Live clocked execution is a separate required check.',whole_game_complete=False)
 save(out/'guards.json',guards);save(out/'report.json',report);save(ROOT/'verification/coordinate-yield-attach-current.json',report);print(json.dumps(dict(status=report['status'],cases=len(guards),directory=str(out))),flush=True)

if __name__=='__main__':main()

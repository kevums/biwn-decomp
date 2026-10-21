"""Host continuation dispatch for the three reconstructed original task loops.

The world body remains on the host C/Python callback stack during an inner
yield. The other two original task bodies contain only yield/BRA, so each
can advance as an explicit step until the suspended world continuation is
selected. Other captured game task bodies are deliberately unsupported.
"""
import ctypes as c
import task_runtime_native as original
scheduler=original.scheduler;world=scheduler.cleanup.world
BODY=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(scheduler.CPU))

class Runtime:
 def __init__(self,library,device,registers,world_updates=2):
  self.lib=c.CDLL(str(library));self.device=device;self.cpu=original.initial_cpu(registers);self.live=c.pointer(self.cpu);self.updates=world_updates
  self.step=self.lib.biwn_task_loop_step;self.step.argtypes=[c.POINTER(world.Bus),c.POINTER(scheduler.CPU),BODY,c.c_void_p,c.c_uint32];self.step.restype=c.c_int
  self.yield_fn=self.lib.biwn_scheduler_yield;self.yield_fn.argtypes=[c.POINTER(world.Bus),c.POINTER(scheduler.CPU),c.c_uint32];self.yield_fn.restype=c.c_int
  self.handoffs=[];self.yields=[];self.errors=[];self.frames=[];self.boundary=None;self.body_calls=0;self.body_active=False;self.steps=[];self.dispatch_active=False;self.dispatch_unload_seen=False
 private=staticmethod(original.private)
 def read_private(self,address,width):return int.from_bytes(c.string_at(self.device.pointer+address,width),'big')
 def current(self):return self.read_private(0xc0920,4)
 def handoff(self):self.handoffs.append({'context':self.current(),'PC':self.live.contents.pc,'SP':self.live.contents.registers[15]})
 def record_yield(self,stack,return_pc):self.yields.append({'context':hex(self.current()),'SP':stack,'return_PC':return_pc,'body_calls':self.body_calls})
 def boundary_enter(self,target):
  cpu=self.live.contents;self.frames.append((cpu.registers[15],self.boundary));self.boundary=target
  # World prologue:12local+44saved bytes. Helper stack:6argument+4JSR
  # bytes; type1 additionally savesA2/D2(8). Confirmed by original native
  # yield SP observations; these are virtual ABI offsets, not oracle inputs.
  cpu.registers[15]-=18 if target==0x19f2c else 10;cpu.usp=cpu.registers[15]
 def boundary_leave(self):
  stack,self.boundary=self.frames.pop();self.live.contents.registers[15]=stack;self.live.contents.usp=stack
 def dispatch_enter(self):
  assert not self.dispatch_active
  self.dispatch_active=True;self.dispatch_unload_seen=False;self.dispatch_stack=self.live.contents.registers[15]
  # Original JSR4 plus MOVEM7registers28; retained PEA4 is added at yield.
  self.live.contents.registers[15]-=32;self.live.contents.usp=self.live.contents.registers[15]
 def dispatch_leave(self):
  self.live.contents.registers[15]=self.dispatch_stack;self.live.contents.usp=self.dispatch_stack;self.dispatch_active=False
 def dispatch_call(self,target):
  if self.dispatch_active and target==0x1b002:self.dispatch_unload_seen=True
 def inner_yield(self,incoming_d0):
  assert self.body_active and(self.boundary in[0x19f2c,0x19fda]or self.dispatch_active)
  if self.dispatch_active:
   self.live.contents.registers[15]-=4;self.live.contents.usp=self.live.contents.registers[15]
   return_pc=0x1968e if self.dispatch_unload_seen else 0x194e6
  else:return_pc=0x19f8e if self.boundary==0x19f2c else 0x1a0bc
  cpu=self.live.contents;stack=cpu.registers[15]
  cpu.registers[0]=incoming_d0;cpu.registers[15]-=4;cpu.usp=cpu.registers[15];cpu.pc=0xdf60;self.device.direct(cpu.registers[15],4,return_pc)
  self.record_yield(cpu.registers[15],return_pc);status=self.yield_fn(c.byref(self.bus),self.live,64);assert status==0,(status,self.errors);self.handoff()
  for _ in range(1000):
   if self.live.contents.pc==return_pc:
    assert self.current()==original.MAIN and self.live.contents.registers[15]==stack
    result=self.live.contents.registers[0]
    if self.dispatch_active:self.live.contents.registers[15]+=4;self.live.contents.usp=self.live.contents.registers[15]
    return result
   assert self.current()!=original.MAIN,'Selected an unsupported main-task continuation'
   self.step_once()
  raise AssertionError('Suspended world continuation did not resume')
 def step_once(self):
  pc=self.live.contents.pc;self.steps.append(pc)
  is_yield=pc in [0x1a54a,0xf360,0xf880]
  if is_yield:
   self.device.trace.append(['call',0xdf60,[]]);self.record_yield(self.live.contents.registers[15]-4,pc+6)
  status=self.step(c.byref(self.bus),self.live,self.body_callback,None,64);assert status==0,(status,self.errors,hex(pc))
  if is_yield:self.handoff()
 def run(self,bus,body):
  self.bus=bus
  def run_body(_,passed_bus,cpu_ptr):
   previous=self.live;entry=cpu_ptr.contents.registers[15];callee=[cpu_ptr.contents.registers[i]for i in range(16)]
   try:
    assert not self.body_active,'Other game task bodies/reentrant world calls are not implemented'
    self.body_active=True;self.live=cpu_ptr;self.body_calls+=1;self.device.trace.append(['call',0x1a188,[]])
    cpu_ptr.contents.registers[15]-=56;cpu_ptr.contents.usp=cpu_ptr.contents.registers[15]
    status=body(passed_bus);assert status==0,status
    cpu_ptr.contents.registers[15]=entry;cpu_ptr.contents.usp=entry
    for i in [2,3,4,5,6,7,10,11,12,13,14]:cpu_ptr.contents.registers[i]=callee[i]
    return 0
   except Exception as error:self.errors.append(repr(error));return 1
   finally:self.live=previous;self.body_active=False
  self.body_callback=BODY(run_body)
  for _ in range(10000):
   if self.cpu.pc==0x1a550 and self.body_calls>=self.updates:break
   self.step_once()
  else:raise AssertionError('Reconstructed three-task runtime did not finish its bounded test')
  assert not self.errors
 def metadata(self):return {'handoffs':self.handoffs,'yields':self.yields,'task_steps':[hex(x)for x in self.steps],'world_body_calls':self.body_calls,'CPU':scheduler.cpu_dict(self.cpu),'original_CPU_instructions_executed':0}

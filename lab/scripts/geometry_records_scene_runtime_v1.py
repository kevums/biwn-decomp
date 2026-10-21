"""Actual scene/record/copy/matrix CPU fixture with synchronous originalGPU4320.

Other scene GPU commands retain declared idle/ack/completion fixtures. No
scripted geometry helper, task repair, asynchronous timing or console proof.
"""
import scene_gpu_family_scene_runtime_v2 as old
base=old.base
GPU_ENTRIES=old.GPU_ENTRIES
native_sites=old.native_sites
base.queue.ENTRIES.update({0x170a0,0x185b2,0xe3e0,0xe220})
base.queue.RETURNS.update({0x17324,0x18852,0xe4a8,0xe26a})
base.queue.SCRIPTS.difference_update({0x170a0,0x185b2})
assert not base.queue.SCRIPTS
class Runtime(old.Runtime):
 def native(self,ram,case,coverage):
  self.reset(ram,case,0);base.lifecycle.seed_cpu(self,base.queue.make_cpu(case));steps=[];stack=[];pending=None
  for _ in range(1000000):
   current=self.cpu();pc=current.pc
   if pc==base.STOP:break
   assert pc in self.rows,hex(pc)
   if pending==pc:
    row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(current));self.calls.append(row);stack.append(row);pending=None
   if pc in base.queue.RETURNS:
    assert stack,hex(pc);stack.pop()['return']=base.cd.scheduler.cpu_dict(current)
   if pc in [0x17e18,0x17e34,0x17e6e,0x17ef8]:self.inject(0x49c60,2)
   if pc in [0x17e5c,0x17ed6]:self.inject(0x10a684,4)
   if pc==0xe098:self.inject(0xf03200,4)
   if pc in old.POLL:self.inject(0xf03204,4)
   source=self.rows[pc]
   if source['assembly'].startswith('jsr '):
    target=int(source['assembly'].split('$')[1].split('.')[0],16);pending=target if target in base.queue.ENTRIES else None
   steps.append(pc);coverage.add(pc);self.core.m68k_execute(1)
   command=self.core.GPUReadLong(0xf03204,0)
   if pc in old.WRITES:self.command_written(command)
   if command==0x4320:
    # Same pinned original movementGPU provider used by standalone record proof.
    self.device.write(0xf03204,0x4320)
   if pc==0xe03e:
    values=self.queues.get((0xf02238,4))
    if values:self.core.m68k_set_reg(0,values.pop(0))
  else:raise AssertionError('Actual scene/records CPU instruction bound')
  assert not stack
  return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())

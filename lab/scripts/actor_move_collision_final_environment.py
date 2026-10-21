"""Final movement context fixture environment; observed before scripted effects."""
from pathlib import Path
import check_biwn_native_actor_move_linked as engine
from run_biwn_native_fast_gameplay_route import ROOT

def prepare(build):
 import check_native_movement_collision_joint as joint
 global engine
 engine=joint.e
 snapshot,payload,symbols,parent,collision=joint.prepare(ROOT/'verification/native-actor-collision-final-current.json')
 assert parent['component_sha256']==build['component_sha256']
 return snapshot,payload,symbols

def native_replay(engine,native,snapshot,case,payload,symbols,compiled,expected,observer=None):
 """Observe BEFORE prescribed services mutateD0/RAM; execute every instruction."""
 memory=bytearray(snapshot);entry=case['entry']
 memory[engine.BASE:engine.BASE+len(payload)]=payload
 memory[engine.COLLBASE:engine.COLLBASE+len(engine.COLL_PAYLOAD)]=engine.COLL_PAYLOAD
 if compiled:
  for root,width in engine.g.COLL_PATCH_WIDTHS.items():
   memory[root:root+width]=b'\x4e\xf9'+engine.COLL_SYMBOLS['biwn_native_actor_collision_outdoor'if root==0x13b5a else'biwn_native_actor_collision_indoor'].to_bytes(4,'big')+(b'\x4e\x71'if width==8 else b'')
 if hasattr(engine,'INIT_PAYLOAD'):memory[engine.INITBASE:engine.INITBASE+len(engine.INIT_PAYLOAD)]=engine.INIT_PAYLOAD
 if compiled:memory[engine.ENTRY:engine.ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_actor_move'].to_bytes(4,'big')+b'\x4e\x71'
 memory=bytearray(engine.g.prior.Script(memory,case).memory)
 for address in engine.g.SERVICES:memory[address:address+2]=b'\x4e\x75'
 SP,STOP=engine.SP,engine.STOP;params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],engine.g.prior.WIDTHS[entry]));memory[SP:SP+4+len(params)]=STOP.to_bytes(4,'big')+params
 boundary=SP-0x3bc+38;canary_start=SP-0x3bc-128;canary=bytes((i*73+19)&255 for i in range(boundary-canary_start));memory[canary_start:boundary]=canary
 native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
 for sr,sp in [(0x2000,SP if case['sr']&0x2000 else 0x1fd000),(0,SP if not case['sr']&0x2000 else 0x1fc000)]:lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
 lib.m68k_set_reg(17,case['sr'])
 for i,value in enumerate(case['incoming']):lib.m68k_set_reg(i,value)
 lib.m68k_set_reg(15,SP);lib.m68k_set_reg(16,entry);events=[]
 if observer:observer.begin()
 def reg(i):return lib.m68k_get_reg(None,i)
 for index,step in enumerate(expected['machine']):
  pc=reg(16);assert pc==step['pc'],('NativePC',index,hex(pc),hex(step['pc']))
  for a,w,v in step['queue_injections']:native.device.direct(a,w,v)
  if observer:observer.step(pc)
  if pc in(engine.g.MEMBERS-{entry})|engine.g.SERVICES:
   ram=native.device.ram();sp=reg(15);offset=4;args=[]
   for width in engine.g.prior.WIDTHS[pc]:args.append(int.from_bytes(ram[sp+offset:sp+offset+width],'big'));offset+=width
   events.append(dict(target=pc,args=args,registers=[reg(i)for i in range(15)],SP=sp,SR=reg(17)))
  if 'service'in step:
   service=step['service'];assert events[-1]['args']==service['args']and reg(0)==service['incoming']
   for a,w,v in service['effects']:native.device.direct(a,w,v)
   lib.m68k_set_reg(0,service['result'])
  lib.m68k_execute(1)
 assert reg(16)==STOP and reg(15)==SP+4
 ram=native.device.ram();assert ram[canary_start:boundary]==canary,'Task header or lower guard overwritten'
 assert ram[SP+4:SP+4+len(params)]==params and ram[engine.BASE:engine.BASE+len(payload)]==payload
 if hasattr(engine,'INIT_PAYLOAD'):assert ram[engine.INITBASE:engine.INITBASE+len(engine.INIT_PAYLOAD)]==engine.INIT_PAYLOAD
 assert engine.normalized(ram,snapshot,len(payload))==expected['ram'],'Native/Unicorn publicRAM'
 regs=[reg(i)for i in range(16)];assert regs[:15]==expected['registers'];sr=reg(17)
 return dict(registers=regs,SR=sr,USP=native.prefix[16]if sr&0x2000 else regs[15],SSP=regs[15]if sr&0x2000 else native.prefix[17],events=events)

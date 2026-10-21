"""23260resident fixture setup; three roots and previous compiled selectors."""
import copy
from pathlib import Path
import check_biwn_native_actor_triple_engine as joint
import check_biwn_native_actor_initialize_final as initializer
import check_biwn_native_sprite_create_linked as sprite
from run_biwn_native_fast_gameplay_route import ROOT
SPRITE=b''
def prepare(build):
 global SPRITE
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();snapshot=bytearray(baseline);snapshot[0x4000:0x100000]=Path(build['derived_stage']).read_bytes();resident=build['resident_address'];payload=Path(build['component']).read_bytes();snapshot[resident:resident+len(payload)]=payload
 for a in [0x13ae0,0x134dc,0x137e0]:snapshot[a:a+8]=baseline[a:a+8]
 joint.BASE=build['actor_dispatch_start'];joint.INITBASE=build['actor_initialize_start'];joint.SPRITEBASE=build['sprite_create_start'];joint.PARENT_RANGE=(resident,resident+build['linked_component_bytes'])
 dispatch=payload[joint.BASE-resident:build['actor_dispatch_end']-resident];init=payload[joint.INITBASE-resident:build['actor_initialize_end']-resident];SPRITE=payload[joint.SPRITEBASE-resident:build['sprite_create_end']-resident]
 assert [len(dispatch),len(init),len(SPRITE)]==[572,1620,2180]
 joint.INIT_PAYLOAD=init;joint.INIT_SYMBOLS=build['symbols'];joint.SPRITE_PAYLOAD=SPRITE;joint.SPRITE_SYMBOLS=build['symbols'];initializer.BASE=joint.INITBASE;initializer.PARENT_RANGE=joint.PARENT_RANGE;sprite.BASE=joint.SPRITEBASE;sprite.PARENT_RANGE=joint.PARENT_RANGE
 return bytes(snapshot),dispatch,init,build['symbols']
def dispatch_vectors():
 rows=joint.vectors()
 for original in sprite.vectors():
  c=copy.deepcopy(original);c['entry']=0x13ae0;c['sprite_joint_extra']=True;id=c['params'][0];signed=id if id<32768 else id-65536;flag=next(value for a,w,value in reversed(c['initial'])if a==0x4208c+id and w==1);c['initial'].append([0x4208c+signed,1,flag]);rows.append(c)
 return rows

def native_replay(engine,native,snapshot,case,payload,symbols,compiled,expected,observer=None):
 """Observe BEFORE prescribed services mutateD0/RAM; execute every instruction."""
 memory=bytearray(snapshot);entry=case['entry']
 memory[engine.BASE:engine.BASE+len(payload)]=payload
 if hasattr(engine,'INIT_PAYLOAD'):memory[engine.INITBASE:engine.INITBASE+len(engine.INIT_PAYLOAD)]=engine.INIT_PAYLOAD;memory[engine.SPRITEBASE:engine.SPRITEBASE+len(engine.SPRITE_PAYLOAD)]=engine.SPRITE_PAYLOAD
 if compiled:
  if entry==0x13ae0:
   memory[0x13ae0:0x13ae8]=b'\x4e\xf9'+symbols['biwn_native_actor_dispatch'].to_bytes(4,'big')+b'\x4e\x71';memory[0x134dc:0x134e4]=b'\x4e\xf9'+symbols['biwn_native_actor_initialize'].to_bytes(4,'big')+b'\x4e\x71';memory[0x137e0:0x137e8]=b'\x4e\xf9'+symbols['biwn_native_sprite_create'].to_bytes(4,'big')+b'\x4e\x71'
  elif entry==0x137e0:memory[0x137e0:0x137e8]=b'\x4e\xf9'+symbols['biwn_native_sprite_create'].to_bytes(4,'big')+b'\x4e\x71'
  else:memory[0x134dc:0x134e4]=b'\x4e\xf9'+symbols['biwn_native_actor_initialize'].to_bytes(4,'big')+b'\x4e\x71'
 memory=bytearray(engine.g.prior.Script(memory,case).memory)
 for address in engine.g.SERVICES:memory[address:address+2]=b'\x4e\x75'
 SP,STOP=engine.SP,engine.STOP;params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],engine.g.prior.WIDTHS[entry]));memory[SP:SP+4+len(params)]=STOP.to_bytes(4,'big')+params
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
 ram=native.device.ram();assert ram[SP+4:SP+4+len(params)]==params and ram[engine.BASE:engine.BASE+len(payload)]==payload
 if hasattr(engine,'INIT_PAYLOAD'):assert ram[engine.INITBASE:engine.INITBASE+len(engine.INIT_PAYLOAD)]==engine.INIT_PAYLOAD
 assert engine.normalized(ram,snapshot,len(payload))==expected['ram'],'Native/Unicorn publicRAM'
 regs=[reg(i)for i in range(16)];assert regs[:15]==expected['registers'];sr=reg(17)
 return dict(registers=regs,SR=sr,USP=native.prefix[16]if sr&0x2000 else regs[15],SSP=regs[15]if sr&0x2000 else native.prefix[17],events=events)

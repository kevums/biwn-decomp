"""Read-only native debug service/capture budget and parent-context contract.
Actual original/native CPU execution supplies snapshots. Synthetic corruptions
are applied to copied observation bytes only,never to guest RAM or code.
"""
import importlib.util,json,struct
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 master=read(V/'native-Deck-debug-final-v1-current.json');gate=read(V/'native-Deck-debug-final-geometry-v1-current.json');assert gate['completed']==256 and gate['deployed_module_byte_identity']
 script=Path(master['directory'])/'geometry.py';spec=importlib.util.spec_from_file_location('debug_final_context_geometry',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);out=V/'native-debug-context-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];e=m.Engine();e.real_dependencies=True;e.debug_out=out;execute=e.core.m68k_execute;rows=[];faults=[]
 def word(memory,at):return int.from_bytes(memory[at:at+4],'big')
 def validate(kind,memory,sp,frame,budget,service,target=None):
  errors=[]
  for name,condition in [('active',word(memory,frame+114)==1),('budget',word(memory,frame+90)==budget),('service',word(memory,frame+82)==service),('opaque',word(memory,frame+86)==frame)]:
   if not condition:errors.append(name)
  if kind=='capture':
   for name,condition in [('frame_arg',word(memory,sp+4)==frame),('CPU_arg',word(memory,sp+8)==frame+4),('return_arg',word(memory,sp+12)==syms['biwn_v4_geometry_helper_return']),('logical_PC',word(memory,frame+68)==target)]:
    if not condition:errors.append(name)
  return errors
 try:
  for ram,initial,case in m.connected.fixtures():
   i=case['variant']
   if i not in [0,1,64,65,128,129,192,193]:continue
   memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,off,_,_ in m.shared.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+off+114:m.ARENA+slot*m.STRIDE+off+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;frame=m.ARENA+(task-m.POOL)+16;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=memory[m.connected.h.SP-256:m.connected.h.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp;initial.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)<<8);initial.usp=0x1d8000 if initial.sr&0x2000 else sp;initial.ssp=sp if initial.sr&0x2000 else 0x1ff000
   memory[0x403cc:0x403ce]=[0,1,0x8000,0xffff][i//64].to_bytes(2,'big');memory[0x403ca:0x403cc]=[0,1,2,31][i%4].to_bytes(2,'big');memory[0xb29d0:0xb5130]=bytes([0xa5])*(0xb5130-0xb29d0);case=dict(case,mutate_globals=i%3==0);ram=bytes(memory);original_finish=None
   def watch_original(cycles):
    nonlocal original_finish
    if e.core.m68k_get_reg(None,16)==0x10966:
     assert original_finish is None;original_finish=(e.native.device.ram(),e.cpu())
    return execute(cycles)
   e.core.m68k_execute=watch_original;expected,cpu,entries,_,_,hardware=e.original(ram,initial,case);e.core.m68k_execute=execute;assert original_finish is not None
   parent=None;captures=0;returned=0;events=[]
   def watch_native(cycles):
    nonlocal parent,captures,returned
    pc=e.core.m68k_get_reg(None,16);csp=e.core.m68k_get_reg(None,15)
    if pc==syms['service_geometry_debug']:
     raw=e.native.device.ram();parent=(word(raw,csp),csp,word(raw,frame+90),word(raw,frame+82));assert parent[2]==2 and parent[3]==syms['service_geometry'];assert not validate('entry',raw,csp,frame,parent[2],parent[3]);events.append(('entry',raw,csp,parent[2],parent[3],None))
    if pc in [syms['biwn_v4_capture_debug_formatter'],syms['biwn_v4_capture_debug_text']]:
     raw=e.native.device.ram();target=0x1b45a if pc==syms['biwn_v4_capture_debug_formatter']else 0x149ae;budget=15-captures;service=syms['service_geometry_debug_helpers'];assert not validate('capture',raw,csp,frame,budget,service,target);events.append(('capture',raw,csp,budget,service,target));captures+=1
    if parent and pc==parent[0]and csp==parent[1]+4:
     raw=e.native.device.ram();assert not validate('return',raw,csp,frame,parent[2],parent[3]);events.append(('return',raw,csp,parent[2],parent[3],None));values=struct.unpack('>19IH',raw[frame+4:frame+82]);virtual=m.CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
     if virtual.sr&0x2000:virtual.usp=initial.usp
     else:virtual.ssp=initial.ssp
     assert m.cpu_dict(virtual)==m.cpu_dict(original_finish[1])
     a=bytearray(raw);b=bytearray(original_finish[0]);a[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=ram[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE];b[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=ram[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE];assert a==b;returned+=1;parent=None
    return execute(cycles)
   e.core.m68k_execute=watch_native;actual,got,observed,details=e.compiled(ram,initial,case,syms,payload,entries);e.core.m68k_execute=execute
   assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed and hardware==e.native.device.registers();assert returned==1 and captures==(0 if i<64 else 16)
   # Independently prove each observed contract field rejects corruption.
   if i in [0,64]:
    for kind,raw,csp,budget,service,target in events:
     fields=[('active',frame+114),('budget',frame+90),('service',frame+82),('opaque',frame+86)]
     if kind=='capture':fields += [('frame_arg',csp+4),('CPU_arg',csp+8),('return_arg',csp+12),('logical_PC',frame+68)]
     for name,at in fields:
      broken=bytearray(raw);broken[at+3]^=2;errors=validate(kind,broken,csp,frame,budget,service,target);assert name in errors;faults.append(dict(case=i,event=kind,field=name,rejected=True))
   rows.append(dict(case=i,real_formatter_text_captures=captures,parent_budget_restored=2,parent_service_restored=True,original_RTS_CPU_and_public_RAM_match=True,geometry_stack_peak=details['C_stack_bytes']));print('case',i,'passed',flush=True)
 finally:e.core.m68k_execute=execute;e.native.close()
 save(out/'cases.json',rows);save(out/'faults.json',faults);paths=[Path(__file__),script,V/'native-Deck-debug-final-v1-current.json',V/'native-Deck-debug-final-geometry-v1-current.json',Path(gate['payload']),out/'cases.json',out/'faults.json'];state=dict(status='terminal_native_debug_actual_parent_budget_capture_and_RTS_context_match',directory=str(out),completed=len(rows),synthetic_observation_faults_rejected=len(faults),new_training=False,new_predictions=0,native_disc_changed=False,source_sha256={str(p):m.file_sha(p)for p in paths},scope=__doc__+' Both stack banks at all four debug flag groups;16nestedoriginal dependencies for active displays. Original RTS10966CPU/publicRAM compared at the actual C return. Only privatearena bytes normalized;no guest writes by this observer.');save(out/'review.json',state);save(V/'native-debug-context-v1-current.json',state)
if __name__=='__main__':main()

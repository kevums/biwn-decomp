"""Measure CPU work for three experimental target-ALU geometry fixtures.

GPU/debug bodies remain the identical declared fixtures on both sides.
Cycle totals are pinned-emulator instruction costs, not physical timing.
"""
import ctypes as c,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 gate=read(V/'native-geometry-alu-v1-current.json');script=ROOT/'scripts/check_native_geometry_alu_v1.py'
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 spec=importlib.util.spec_from_file_location('faces_cost_final_geometry',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];out=V/'native-alu-cost-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);e=m.Engine();e.debug_out=out;rows=[]
 execute=e.core.m68k_execute
 try:
  for ram,initial,case in m.connected.fixtures():
   i=case['variant']
   if i not in [0,3,12]:continue
   memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,offset,_,_ in m.shared.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+offset+114:m.ARENA+slot*m.STRIDE+offset+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;memory[0xc0920:0xc0924]=task.to_bytes(4,'big');sp=task+[0x3c0,0x3be,0x200][i%3];memory[sp-256:sp+32]=memory[m.connected.h.SP-256:m.connected.h.SP+32]
   initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   ram=bytes(memory);costs={}
   for lane in ['original','compiled']:
    counters=dict(instructions=0,cycles=0,face_instructions=0,face_cycles=0);active=False;return_pc=None;entry_sp=None
    def counted(cycles):
     nonlocal active,return_pc,entry_sp
     pc=e.core.m68k_get_reg(None,16);at=e.core.m68k_get_reg(None,15)
     if pc==(0x1142e if lane=='original'else syms['service_geometry_faces']):
      assert not active;active=True;entry_sp=at;return_pc=e.native.device.read(at,4)
     if active and pc==return_pc and at==entry_sp+4:active=False
     used=execute(cycles);counters['instructions']+=1;counters['cycles']+=used
     if active:counters['face_instructions']+=1;counters['face_cycles']+=used
     return used
    e.core.m68k_execute=counted
    if lane=='original':expected,cpu,entries,_,_=e.original(ram,initial,case)
    else:
     actual,got,observed,details=e.compiled(ram,initial,case,syms,payload,entries)
     assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed
    assert not active;costs[lane]=dict(counters);e.core.m68k_execute=execute
   rows.append(dict(variant=i,descriptor_faces=[0,1,2,3,6][(i//3)%5],costs=costs,CPU_RAM_entries_match=True))
 finally:e.core.m68k_execute=execute;e.native.close()
 assert len(rows)==3
 save(out/'cases.json',rows);paths=[Path(__file__),script,V/'native-Deck-faces-final-geometry-v1-current.json',Path(gate['payload']),out/'cases.json']
 state=dict(status='terminal_native_face_path_CPU_cost_samples_measured',directory=str(out),cases=rows,new_training=False,new_predictions=0,native_disc_changed=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Entry-to-return costs include bridge overhead for compiled face service;injected GPU/debug effects have no CPU body cost. This diagnoses overhead without altering game code,inputs or proof gates.')
 save(out/'review.json',state);save(V/'native-alu-cost-v1-current.json',state);print(out);print(json.dumps(rows,indent=2))
if __name__=='__main__':main()

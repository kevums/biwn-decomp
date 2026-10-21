"""Exact full-CPU/full-RAM fallback across all CCR values and both banks."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import check_native_deck_shared_v2 as m
ROOT=m.ROOT;save=m.save;sha=m.sha
def main():
 bp=ROOT/'verification/native-deck-shared-final-v2-current.json';gate=json.loads(bp.read_text());assert gate['deployed_module_byte_identity'];m.CODE=gate['actual_code_address'];m.ARENA=gate['actual_arena_address'];payload=Path(gate['payload']).read_bytes();syms=gate['symbols']
 for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
 out=ROOT/'verification/shared-Deck-fallback-ABI-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='checking',pid=os.getpid(),directory=str(out),new_training=False,whole_game_complete=False);save(out/'protocol.json',state);rows=[]
 for kind,(_,offset,_,_)in m.LAYOUT.items():
  m.configure(kind);ram,initial,case=m.fixtures(kind)[0];engine=m.Engine(kind)
  try:
   for mode in [0,0x2000]:
    for flags in range(32):
     for task,busy in [(0,False),(m.POOL+1,False),(m.POOL+m.SLOTS*1024,False),(m.POOL,True)]:
      memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*1024]=bytes([0xa5])*(m.SLOTS*1024)
      for slot in range(m.SLOTS):
       for _,off,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*1024+off+114:m.ARENA+slot*1024+off+118]=bytes(4)
      memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
      if busy:memory[m.ARENA+offset+114:m.ARENA+offset+118]=(1).to_bytes(4,'big')
      sp=m.POOL+0x3c0;memory[sp-256:sp+32]=ram[m.SP-256:m.SP+32];memory[sp:sp+4]=m.STOP.to_bytes(4,'big');cpu=m.CPU.from_buffer_copy(bytes(initial));cpu.sr=mode|flags;cpu.registers[15]=sp;cpu.usp=0x1d8000 if mode else sp;cpu.ssp=sp if mode else 0x1ff000
      # Dirty upper words and signed extremes vary with flags; no full Cartesian claim.
      cpu.registers[2]=[0,0xffffffff,0x80000000,0x7fffffff,0xa55a8000,0x1234ffff][flags%6];cpu.registers[3]=cpu.registers[2]^0x5aa5f00f
      before=bytes(memory);case={**case,'payload':payload};expected,want,entries,*_=engine.reference(before,cpu,case);_,got,observed,details=engine.compiled(before,cpu,case,syms,entries,True);raw=engine.native.device.ram()
      assert raw==expected and m.cpu_dict(got)==m.cpu_dict(want)and observed==entries,(kind,mode,flags,task,busy)
      assert raw[m.ARENA:m.ARENA+m.SLOTS*1024]==before[m.ARENA:m.ARENA+m.SLOTS*1024]
      rows.append(dict(kind=kind,mode=mode,flags=flags,task=hex(task),busy=busy,full_CPU_and_entire_RAM_match_without_normalization=True,**details))
   print(kind,'fallback cases passed',flush=True)
  finally:engine.native.close()
 save(out/'cases.json',rows);paths=[Path(__file__),Path(m.__file__),bp,Path(gate['payload'])]
 state.update(status='terminal_all_CCR_banks_three_root_fallback_ABI_match',completed=len(rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' 768 cases:3roots x2banks x32CCR x3invalid task pointers plus busy same-root fallback. Dirty D2/D3 values vary with flags, not a full additional Cartesian dimension. Scan minimum-save no-active-object path; input poll/helper fixtures and coordinate GPU fixture; E540 actual CPU. No arbitrary asynchronous reentrancy claim.');save(out/'protocol.json',state);save(ROOT/'verification/shared-Deck-fallback-ABI-v2-current.json',state);print(state['status'],len(rows),flush=True)
if __name__=='__main__':main()

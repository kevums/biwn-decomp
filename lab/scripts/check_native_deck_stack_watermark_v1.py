"""Measure real C-stack depth, excluding SP-only frame-address lookup."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_coordinate_v2 as m
ROOT=m.ROOT;V=ROOT/'verification'
def main():
 gate=json.loads((V/'native-deck-coordinate-v2-current.json').read_text());build=Path(gate['payload']).parent;payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];engine=m.Engine();rows=[];original_step=engine.core.m68k_execute
 try:
  for i,(ram,initial,case)in enumerate(m.original.fixtures()[:8]):
   task=m.POOL+i*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory=bytearray(ram);memory[sp-256:sp+32]=memory[m.SP-256:m.SP+32];memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE);memory[0xc0920:0xc0924]=task.to_bytes(4,'big');initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   low=1008;lookup=0
   def step(cycles):
    nonlocal low,lookup
    pc=engine.core.m68k_get_reg(None,16);actual=engine.core.m68k_get_reg(None,15);base=m.ARENA+i*m.STRIDE
    if base<=actual<base+m.STRIDE:
     if pc==syms['biwn_native_deck_helper_return']+12:lookup+=1;assert actual==base+16
     else:low=min(low,actual-base)
    return original_step(cycles)
   engine.core.m68k_execute=step
   _,_,_,details=engine.native_candidate(bytes(memory),initial,{**case,'payload':payload},syms)
   assert lookup==4 and low>116
   rows.append(dict(case=i,task=hex(task),actual_C_stack_low_offset=low,usable_top=1008,C_stack_bytes=1008-low,frame_end_offset=116,minimum_frame_clearance=low-116,SP_only_frame_lookups=lookup,guards_and_other_slots_unchanged=True))
 finally:engine.core.m68k_execute=original_step;engine.native.close()
 out=V/'native-deck-stack-watermark'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);m.save(out/'cases.json',rows)
 state=dict(status='terminal_native_Deck_C_stack_watermark_excluding_SP_lookup_pass',directory=str(out),cases=len(rows),maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),minimum_frame_clearance=min(x['minimum_frame_clearance']for x in rows),scope='EightactualcompiledCPUwitnesses,bothbanks/3gueststackdepths. EarlierminimumSPoffset16is a flag-neutralframeaddresslookuplusingSP,not actual Cstackdepth. GPU resultfixture;realE540. Not arbitraryIRQ/reentrancy/physicalproof.',source_sha256={str(p):m.sha(p.read_bytes())for p in[Path(__file__),Path(m.__file__),build/'native-deck.bin',ROOT/'scripts/check_native_deck_coordinate_v1.py']})
 m.save(out/'report.json',state);m.save(V/'native-deck-stack-watermark-current.json',state);print(state['status'],state['maximum_C_stack_bytes'],state['minimum_frame_clearance'],flush=True)
if __name__=='__main__':main()

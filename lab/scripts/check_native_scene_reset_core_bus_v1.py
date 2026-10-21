"""Compare actual pinned68000 RAM-bus traces for original and hybrid reset.
Four descriptor cases independently check the19realCLRdummyreads omitted by
Unicorn. Core recorder has no width field; the separate768-case gate checks widths.
"""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_native_scene_reset_context_v1 as p
h=p.h;ROOT=p.ROOT;V=p.V
class Event(c.Structure):
 _fields_=[('seq',c.c_uint64),('frame',c.c_uint32),('halfline',c.c_uint16),('type',c.c_uint8),('who',c.c_uint8),('pc',c.c_uint32),('addr',c.c_uint32),('value',c.c_uint32)]
def main():
 proof=V/'native-scene-reset-hybrid-v1-current.json';g=json.loads(proof.read_text());assert g['completed']==768
 for path,digest in g['source_sha256'].items():assert p.sha(path)==digest,path
 out=V/'native-scene-reset-core-bus-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);payload=Path(g['payload']).read_bytes();elf=Path(g['directory'])/'reset.elf'
 import subprocess
 syms=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);entry=next(int(x.split()[0],16)for x in syms.splitlines()if x.endswith(' run'));engine=h.Engine();core=engine.core;assert c.sizeof(Event)==32
 core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int;rows=[]
 def private(a):return p.DATA<=a<p.DATA+78 or p.CSP-2048<=a<p.CSP+8
 def trace(memory,s,start):
  engine.native.device.seed(memory,0);physical=h.CPU.from_buffer_copy(bytes(s));physical.pc=start;engine.set_cpu(physical,True);core.vjtrace_disarm();core.vjtrace_watch_clear();assert core.vjtrace_watch_add(0,0x1fffff,3)>=0;begin=core.vjtrace_ring_head();core.vjtrace_arm()
  for _ in range(10000):
   if core.m68k_get_reg(None,16)==h.STOP:break
   core.m68k_execute(1)
  else:raise AssertionError('no return')
  core.vjtrace_disarm();end=core.vjtrace_ring_head();events=[]
  for index in range(begin,end):
   event=Event();assert core.vjtrace_ring_read(index,c.byref(event));a=event.addr
   if event.type not in [11,12]or private(a)or p.CODE<=a<p.CODE+len(payload)or 0x1102a<=a<0x110d4 or h.STOP<=a<h.STOP+2:continue
   events.append(dict(kind='r'if event.type==11 else'w',address=a,value=event.value,PC=hex(event.pc),who=event.who))
  return events
 try:
  for ram,initial,case in p.fixtures():
   if case['variant']not in [0,256,512,576]:continue
   memory=bytearray(ram);memory[p.CODE:p.CODE+len(payload)]=payload;memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[p.DATA:p.DATA+78]=p.pack(initial);memory[p.CSP:p.CSP+8]=struct.pack('>2I',h.STOP,p.DATA);memory=bytes(memory)
   native=h.CPU();native.registers[:]=[(0x1234567*(n+1))&0xffffffff for n in range(15)]+[p.CSP];native.sr=initial.sr&0x2000;native.usp=0x1d8000 if native.sr else p.CSP;native.ssp=p.CSP if native.sr else 0x1ff000
   original=trace(memory,initial,0x1102a);compiled=trace(memory,native,entry);normal=lambda seq:[(x['kind'],x['address'],x['value'])for x in seq]
   p.save(out/('case-'+str(case['variant'])+'.json'),dict(case=case,original=original,native=compiled));assert normal(original)==normal(compiled),(case,len(original),len(compiled));assert len(original)==49,(case,len(original));rows.append(dict(case=case,actual_original_and_native_bus_events=49,all_kind_address_values_match=True))
 finally:core.vjtrace_disarm();engine.native.close()
 paths=[Path(__file__),proof,*out.glob('case-*.json')];d=dict(status='terminal_four_actual68000_reset_bus_traces_match_49_events',directory=str(out),completed=len(rows),cases=rows,payload_sha256=g['payload_sha256'],new_predictions=0,new_training=False,source_sha256={str(x):p.sha(x)for x in paths},scope=__doc__+' Codefetch/privateCstack/context excluded;test descriptors do not point into excluded code/private memory. No CPU/RAMmutation byrecorder. No IRQ/devicefault/wholegame claim.');p.save(out/'review.json',d);p.save(V/'native-scene-reset-core-bus-v1-current.json',d);print(d['status'])
if __name__=='__main__':main()

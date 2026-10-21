"""Trace the unedited local clear body in the shared prototype module.
Capture its real native entry state in the qualified geometry harness,then
independently execute that exact ELF byte range in Unicorn until its C return.
Compare public RAM and ordered accesses with the retained helper contract.
"""
import ctypes as c,importlib.util,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return h.sha(Path(p).read_bytes())
def cpu(raw):
 v=struct.unpack('>19IH',raw);s=h.CPU();s.registers[:]=v[:16];s.pc,s.usp,s.ssp,s.sr=v[16:];return s
def main():
 gatepath=V/'native-Deck-local-clear-real-v1-current.json';g=read(gatepath);assert g['completed']==256
 for p,digest in g['source_sha256'].items():assert sha(p)==digest,p
 script=ROOT/'scripts/check_native_deck_local_clear_v1.py';spec=importlib.util.spec_from_file_location('local_clear_module_order_geometry',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=V/'native-local-clear-module-order-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 payload=Path(g['payload']).read_bytes();syms=g['symbols'];clear=next(a for n,a in syms.items()if n.startswith('local_typed_clear_records'));library=out/'portable.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(h.SRC),str(h.SRC/'coordinator-reference.c'),str(h.SRC/'helper-adapter.c'),'-o',str(library)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(library)).biwn_geometry_helper_call;fn.argtypes=[c.POINTER(h.Bus),h.W8,c.POINTER(h.CPU),h.SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
 engine=m.Engine();engine.real_dependencies=True;engine.debug_out=out;execute=engine.core.m68k_execute;rows=[];captured=None
 try:
  for ram,initial,case in m.connected.fixtures():
   i=case['variant']
   if i not in [0,1,3,12]:continue
   memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,off,_,_ in m.shared.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+off+114:m.ARENA+slot*m.STRIDE+off+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=memory[m.connected.h.SP-256:m.connected.h.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   ram=bytes(memory);expected,reference_cpu,entries,_,_,hardware=engine.original(ram,initial,case);captured=None
   def observe(cycles):
    nonlocal captured
    if engine.core.m68k_get_reg(None,16)==clear:
     assert captured is None;captured=(engine.native.device.ram(),engine.cpu())
    return execute(cycles)
   engine.core.m68k_execute=observe
   actual,got,_,_=engine.compiled(ram,initial,case,syms,payload,entries);engine.core.m68k_execute=execute;assert expected==actual and m.cpu_dict(reference_cpu)==m.cpu_dict(got)and captured is not None
   raw,physical=captured;frame=m.ARENA+(task-m.POOL)+16;logical=cpu(raw[frame+4:frame+82]);assert logical.pc==0x10968
   result=h.Engine.translated(engine,fn,raw,logical,dict(case,root=0x10968));assert result[0]==0 and not result[-1];expected_events=result[4];assert expected_events[-1][:3]==['r',logical.registers[15],4];expected_events=expected_events[:-1]
   expected_cpu=h.CPU.from_buffer_copy(bytes(result[2]));expected_cpu.pc=0x1098e;expected_cpu.registers[15]=logical.registers[15]
   if expected_cpu.sr&0x2000:expected_cpu.ssp=logical.registers[15]
   else:expected_cpu.usp=logical.registers[15]
   u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,raw);u.reg_write(UC_M68K_REG_SR,physical.sr)
   for reg,value in zip(REGS,physical.registers):u.reg_write(reg,value)
   ret=int.from_bytes(raw[physical.registers[15]:physical.registers[15]+4],'big');events=[]
   def private(a,w):return m.ARENA<=a and a+w<=m.ARENA+m.SLOTS*m.STRIDE
   def on_read(uc,access,a,w,value,data):
    if not private(a,w):events.append(['r',a,w,int.from_bytes(u.mem_read(a,w),'big')])
   def on_write(uc,access,a,w,value,data):
    if not private(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
   u.hook_add(UC_HOOK_MEM_READ,on_read);u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.emu_start(clear,ret,count=100000,timeout=3000000);assert u.reg_read(UC_M68K_REG_PC)==ret
   if events!=expected_events:save(out/'trace-mismatch.json',dict(case=i,expected=expected_events[:30],actual=events[:30],counts=[len(expected_events),len(events)]));raise AssertionError(out/'trace-mismatch.json')
   memory=bytearray(u.mem_read(0,0x200000));translated_cpu=cpu(memory[frame+4:frame+82]);assert h.cpu_dict(translated_cpu)==h.cpu_dict(expected_cpu)
   reference=bytearray(result[1]);reference[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=raw[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE];memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=raw[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE];assert memory==reference
   rows.append(dict(case=i,physical_supervisor=bool(physical.sr&0x2000),public_events=len(events),logical_CPU_public_RAM_and_order_match=True));print('case',i,'passed',flush=True)
 finally:engine.core.m68k_execute=execute;engine.native.close()
 save(out/'cases.json',rows);paths=[Path(__file__),gatepath,script,Path(g['payload']),out/'cases.json'];state=dict(status='terminal_actual_shared_module_local_clear_order_and_CPU_RAM_match',directory=str(out),completed=len(rows),deployed_payload_sha256=g['payload_sha256'],new_training=False,new_predictions=0,installed_preview_changed=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Four actual shared-prototype geometry contexts;logical helper arguments1,7. No disc/final-layout,arbitrary aliases,IRQ or timing proof. Full helper boundaries and budgets use the separate standalone260/35matrix.');save(out/'review.json',state);save(V/'native-local-clear-module-order-v1-current.json',state)
if __name__=='__main__':main()

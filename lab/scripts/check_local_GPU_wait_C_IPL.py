"""Native68000 oracle for the local Author's exact unmodified six-case C."""
import argparse,ctypes as c,json,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from check_biwn_scheduler import Native,CPU,cpu_dict
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16);W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);CALL=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32),c.c_uint32,c.POINTER(c.c_uint32))
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('write32',W32),('call',CALL),('context',c.c_void_p),('poll_limit',c.c_uint32)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--author-proof',type=Path,default=ROOT/'verification/GPU-wait-Code-Author-current.json');args=ap.parse_args();author=json.loads(args.author_proof.read_text());source=Path(author['source']);assert sha(source)==author['source_text_sha256']
 out=ROOT/'verification/GPU-wait-local-C-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);libpath=out/'wait.dylib';rest=ROOT/'projects/black-ice-white-noise/restoration'
 cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(rest),str(source),'-o',str(libpath)];built=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr)
 if built.returncode:
  state=dict(status='terminal_local_C_compile_rejected',directory=str(out),author_proof=str(args.author_proof),author_proof_sha256=sha(args.author_proof),source_sha256=sha(source),accepted=False,compiler_return=built.returncode);save(out/'protocol.json',state);save(ROOT/'verification/GPU-wait-local-C-check-current.json',state);print(built.stderr);return
 library=c.CDLL(str(libpath));fn=library.biwn_GPU_wait_repair_step;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU)];fn.restype=c.c_int
 b=json.loads((ROOT/'verification/native-fast-core-wait-format-disc-build-current.json').read_text());image=bytearray(0x200000);image[0x4000:0x100000]=Path(b['derived_stage']).read_bytes();image[b['resident_address']:b['resident_address']+b['component_bytes']]=Path(b['component']).read_bytes()
 n=Native();n.device.seed(bytes(image),0);l=n.lib;l.GPUGetRAM.restype=c.c_void_p;gpu=l.GPUGetRAM();l.m68k_set_irq(0);rng=random.Random(0xe098162708);rows=[];errors=[];reads=[];fail_reads=False
 def rd(_,address,p):
  reads.append(address)
  if fail_reads:return 1
  if address in [0xf03200,0xf03204]:p[0]=mailbox[address];return 0
  if address>0x1ffffc:return 1
  p[0]=int.from_bytes(image[address:address+4],'big');return 0
 callback=R32(rd);bus=Bus(R8(),R16(),callback,W16(),W32(),CALL(),None,0)
 cases=[]
 for mode in [s|ipl for s in [0,0x2000]for ipl in range(0,0x800,0x100)]:
  for flags in range(32):
   for pc in [0xe098,0x162712,0x16271e,0x162720]:cases.append((pc,mode|flags,0))
   for pc in [0x162708,0x162714]:
    for value in [0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]:cases.append((pc,mode|flags,value))
 try:
  for index,(pc,sr,value)in enumerate(cases):
   registers=[rng.getrandbits(32)for _ in range(14)]+[0x140000,0x1d0000];image[0x1d0000:0x1d0004]=(0x190000).to_bytes(4,'big');image[0x140000:0x140004]=(0x180000).to_bytes(4,'big');n.device.direct(0x1d0000,4,0x190000);n.device.direct(0x140000,4,0x180000)
   mailbox={0xf03200:value,0xf03204:value};c.memmove(gpu+0x200,value.to_bytes(4,'big')*2,8)
   l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1c0000);l.m68k_set_reg(17,sr)
   for i,v in enumerate(registers):l.m68k_set_reg(i,v)
   l.m68k_set_reg(16,pc)
   before=CPU();before.registers[:]=registers;before.pc=pc;before.sr=sr;before.usp=n.prefix[16]if sr&0x2000 else registers[15];before.ssp=registers[15]if sr&0x2000 else n.prefix[17]
   actual=CPU.from_buffer_copy(bytes(before));reads.clear();status=fn(c.byref(bus),c.byref(actual));assert status==0
   cycles=l.m68k_execute(1);assert cycles>0
   expected=CPU();expected.registers[:]=[l.m68k_get_reg(None,i)for i in range(16)];expected.pc=l.m68k_get_reg(None,16);expected.sr=l.m68k_get_reg(None,17);expected.usp=n.prefix[16]if expected.sr&0x2000 else expected.registers[15];expected.ssp=expected.registers[15]if expected.sr&0x2000 else n.prefix[17]
   matched=cpu_dict(actual)==cpu_dict(expected)
   row=dict(case=index,PC=hex(pc),incoming_SR=sr,operand=value,matched=matched,C_bus_reads=list(reads),native_cycles=cycles);rows.append(row)
   if not matched and len(errors)<8:errors.append(dict(**row,before=cpu_dict(before),expected=cpu_dict(expected),actual=cpu_dict(actual)))
  guards=[]
  initial=CPU();initial.pc=0x162708;initial.sr=0x201f;initial.registers[15]=0x1d0000
  for name,ptr,target in [('nullbus',None,initial),('nullstate',c.byref(bus),None),('missingread',c.byref(Bus()),initial)]:
   before=bytes(initial);status=fn(ptr,c.byref(target)if target is not None else None);assert status==1 and bytes(initial)==before;guards.append(name)
  for pc in [0x162708,0x162714,0x162720]:
   initial.pc=pc;before=bytes(initial);fail_reads=True;assert fn(c.byref(bus),c.byref(initial))==2 and bytes(initial)==before;fail_reads=False;guards.append('failedread-'+hex(pc))
  initial.pc=0x1234;before=bytes(initial);assert fn(c.byref(bus),c.byref(initial))==7 and bytes(initial)==before;guards.append('unknownPC')
 finally:n.close()
 save(out/'cases.json',rows);save(out/'first-mismatches.json',errors)
 state=dict(status='terminal_local_GPU_wait_C_pass'if all(v['matched']for v in rows)else'terminal_local_GPU_wait_C_semantics_rejected',directory=str(out),author_proof=str(args.author_proof),author_proof_sha256=sha(args.author_proof),source=str(source),source_text_sha256=sha(source),library=str(libpath),cases=len(rows),failed_cases=sum(not v['matched']for v in rows),host_error_guards=guards,accepted=not errors,source_unmodified=True,new_training=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),args.author_proof,source,libpath,rest/'biwn_scheduler.h',rest/'biwn_world_update.h',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']})
 save(out/'protocol.json',state);save(ROOT/'verification/GPU-wait-local-C-check-current.json',state);print(json.dumps({k:state[k]for k in ['status','cases','failed_cases','host_error_guards','accepted']},indent=2),flush=True)
if __name__=='__main__':main()

"""Native single-instruction edge fixtures for the414 added C instruction cases."""
import ctypes as c,json,random
from datetime import datetime,timezone
from pathlib import Path
from check_local_GPU_wait_C import Bus,R8,R16,R32,W16,W32,CALL
from check_biwn_scheduler import Native,CPU,cpu_dict
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 bp=ROOT/'verification/native-formatter-C-bridge-current.json';bridge=json.loads(bp.read_text());candidate=json.loads(Path(bridge['CPU_candidate']).read_text());library=c.CDLL(candidate['library']);fn=getattr(library,candidate['function']);fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),c.c_void_p,c.c_void_p,c.c_void_p];fn.restype=c.c_int
 unavailable=ROOT/'verification/route-CPU-build/20261018T230148.268237Z/unsupported.json';pcs=sorted(int(v['PC'],16)for v in json.loads(unavailable.read_text()));assert len(pcs)==414
 atlas=Path(candidate['instruction_RAM_source']).read_bytes();out=ROOT/'verification/native-formatter-C-new-forms'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 n=Native();l=n.lib;rows=[];failures=[];rng=random.Random(0x4144916);image=bytearray(atlas);accesses=[];reference=bytes(image)
 def read(width):
  def callback(_,a,p):
   if a>0x200000-width:raise ValueError(('readoutside fixture',hex(a)))
   p[0]=int.from_bytes(image[a:a+width],'big');accesses.append(['r',a,width]);return 0
  return callback
 def write(width):
  def callback(_,a,v):
   if a>0x200000-width:raise ValueError(('writeoutside fixture',hex(a)))
   image[a:a+width]=int(v).to_bytes(width,'big');accesses.append(['w',a,width]);return 0
  return callback
 callbacks=[R8(read(1)),R16(read(2)),R32(read(4)),W16(write(2)),W32(write(4))];bus=Bus(*callbacks,CALL(),None,0)
 # Map valid distinct RAM operands and explicit exception vectors. These
 # are controlled instruction fixtures, not live helper calling contexts.
 try:
  for pattern in [0,0xffffffff,0x270f270f]:
   fixture=bytearray(reference)
   for a in [0x130000+i*0x1000 for i in range(8)]+[0x1c0000,0x1d0000,0x1e0000]:fixture[a-256:a+1024]=pattern.to_bytes(4,'big')*320
   fixture[0x20:0x24]=(0x190000).to_bytes(4,'big');fixture[0x1d0000:0x1d0006]=bytes.fromhex('201f00190000')
   n.device.seed(bytes(fixture),0)
   for mode in [0,0x2000]:
    for flags in range(32):
     for pc in pcs:
      image[:]=fixture;accesses.clear();regs=[rng.getrandbits(32)for _ in range(8)]+[0x130000+i*0x1000 for i in range(7)]+[0x1d0000]
      # No case in this414set uses a Dregister as a memory index.
      l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1c0000);l.m68k_set_reg(17,mode|flags)
      for i,v in enumerate(regs):l.m68k_set_reg(i,v)
      l.m68k_set_reg(16,pc);before=CPU();before.registers[:]=regs;before.pc=pc;before.sr=mode|flags;before.usp=n.prefix[16]if mode else regs[15];before.ssp=regs[15]if mode else n.prefix[17];actual=CPU.from_buffer_copy(bytes(before));status=fn(c.byref(bus),c.byref(actual),None,None,None)
      assert status in [0,11],(hex(pc),status)
      cycles=l.m68k_execute(1);assert cycles>0
      expected=CPU();expected.registers[:]=[l.m68k_get_reg(None,i)for i in range(16)];expected.pc=l.m68k_get_reg(None,16);expected.sr=l.m68k_get_reg(None,17);expected.usp=n.prefix[16]if expected.sr&0x2000 else expected.registers[15];expected.ssp=expected.registers[15]if expected.sr&0x2000 else n.prefix[17]
      native_ram=n.device.ram();matched=cpu_dict(actual)==cpu_dict(expected)and native_ram==bytes(image)
      if not matched and len(failures)<16:
       differences=[a for a,(x,y)in enumerate(zip(native_ram,image))if x!=y]
       failures.append(dict(PC=hex(pc),mode=mode,flags=flags,pattern=hex(pattern),before=cpu_dict(before),expected=cpu_dict(expected),actual=cpu_dict(actual),first_RAM_differences=[hex(a)for a in differences[:12]],C_accesses=list(accesses)))
      rows.append(dict(PC=hex(pc),mode=mode,flags=flags,pattern=pattern,matched=matched))
      # Restore exactly the RAM writes made by either execution. Code and
      # operands are bounded to this RAM fixture; no device contexts used.
      for action,a,width in accesses:
       if action=='w':n.device.direct(a,width,int.from_bytes(fixture[a:a+width],'big'))
      if native_ram!=bytes(image):
       for a,(x,y)in enumerate(zip(native_ram,fixture)):
        if x!=y:n.device.direct(a,1,y)
    print('pattern',hex(pattern),'mode',hex(mode),'cases',len(rows),'failures',sum(not row['matched']for row in rows),flush=True)
 finally:n.close()
 save(out/'first-mismatches.json',failures);save(out/'cases.json',rows)
 state=dict(status='terminal_native_formatter_C_new_forms_pass'if not failures else'terminal_native_formatter_C_new_forms_rejected',directory=str(out),cases=len(rows),instruction_entries=len(pcs),failures=sum(not row['matched']for row in rows),CPU_and_entire_RAM_compared=True,patterns=[0,0xffffffff,0x270f270f],all32_CCR=True,both_CPU_modes=True,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,Path(bridge['CPU_candidate']),Path(candidate['library']),unavailable,Path(candidate['instruction_RAM_source']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']},scope='Singleinstruction414added fixednative-image cases in valid distinctRAM contexts; fullD/A/PC/SR/USP/SSP and2MBRAM. Threeoperandpatterns,allCCR,bothmodes. Not arbitraryaliasing,busfault/device/prefetch/IRQ timing or wholefunction/game proof.',new_training=False,default_promoted=False)
 save(out/'protocol.json',state);save(ROOT/'verification/native-formatter-C-new-forms-current.json',state);print(json.dumps({k:state[k]for k in ['status','cases','instruction_entries','failures']}),flush=True)
if __name__=='__main__':main()

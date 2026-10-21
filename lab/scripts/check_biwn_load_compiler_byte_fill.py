"""New freestanding compiler support: target ABI, byte semantics and write bounds."""
from pathlib import Path
from datetime import datetime,timezone
import json,random,subprocess
from check_biwn_native_button_digit import ROOT,sha,save
import check_biwn_scheduler as sched
SP=0x1e0000;STOP=0x1f0000

def main():
 pp=ROOT/'verification/native-load-bundle-preflight-current.json';p=json.loads(pp.read_text());binary=Path(p['binary']);assert sha(binary)==p['binary_sha256'];payload=binary.read_bytes();base=p['resident_base'];entry=p['symbols']['memset'];elf=binary.with_suffix('.elf');prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
 row=next(l.split()for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(elf)],text=True).splitlines()if l.split()[-1]=='memset');end=entry+int(row[1],16)
 out=ROOT/'verification/load-compiler-byte-fill'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rng=random.Random(0x5930);rows=[];n=sched.Native()
 try:
  for count in [0,1,2,3,7,16,31,68,69,128]:
   for value in [0,1,128,255,511,0xffffffff]:
    for mode in [0,0x2000]:
     for ccr in [0,31]:
      for align in [0,1]:
       dest=0x120100+align;initial=bytearray(0x200000);initial[base:base+len(payload)]=payload;initial[dest-16:dest+count+16]=bytes([0xa5])*(count+32)
       for i,v in enumerate([STOP,dest,value,count]):initial[SP+i*4:SP+4+i*4]=v.to_bytes(4,'big')
       regs=[rng.getrandbits(32)for _ in range(15)]+[SP];sr=mode|ccr;core=n.lib;n.device.seed(initial,0);core.m68k_pulse_reset();core.m68k_set_irq(0);core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,SP if mode else 0x1fc000);core.m68k_set_reg(17,0);core.m68k_set_reg(15,0x1fd000 if mode else SP);core.m68k_set_reg(17,sr)
       for i,v in enumerate(regs):core.m68k_set_reg(i,v)
       core.m68k_set_reg(16,entry);minimum=SP
       for _ in range(10000):
        pc=core.m68k_get_reg(None,16)
        if pc==STOP:break
        assert entry<=pc<end,hex(pc);minimum=min(minimum,core.m68k_get_reg(None,15));core.m68k_execute(1)
       else:raise AssertionError('memset support failed to return')
       actual=[core.m68k_get_reg(None,i)for i in range(16)];assert actual[0]==dest and actual[15]==SP+4
       assert all(actual[i]==regs[i]for i in [2,3,4,5,6,7,10,11,12,13,14]);assert core.m68k_get_reg(None,17)&~31==sr&~31
       expected=bytearray(initial);expected[dest:dest+count]=bytes([value&255])*count;ram=bytearray(n.device.ram());assert SP-4096<=minimum<=SP;ram[minimum:SP]=initial[minimum:SP];assert ram==expected
       rows.append(dict(count=count,value=value,mode=mode,CCR=ccr,unaligned=align,private_stack_bytes=SP-minimum,return_pointer_and_callee_saves_and_whole_RAM_bounds_match=True))
 finally:n.close()
 save(out/'cases.json',rows);report=dict(status='terminal_compiler_byte_fill_native_ABI_and_byte_bounds_pass',directory=str(out),cases=len(rows),bundle_proof=str(pp),bundle_proof_sha256=sha(pp),bundle_binary_sha256=sha(binary),runtime_support_not_recovered_game_function=True,source_sha256={str(q):sha(q)for q in [Path(__file__),ROOT/'projects/black-ice-white-noise/restoration/native-m68k/compiler-byte-fill.c']},scope='480nativeM68000cases:0..128count including RNG68byteframe, lowbyte truncation/zero/nonzero, even/odd destinations,user/supervisor/CCR0/31. D0destination,callee-savedregs,RTS/SP,upperSR and wholeRAM outside bounded output/privatehelperstack checked. Caller-saved registers/CCR unspecified by C ABI. FullRNG/game/IRQ/physical gates remain unrun for compactbundle.',full_compact_bundle_accepted=False)
 assert len(rows)==480;save(out/'protocol.json',report);save(ROOT/'verification/load-compiler-byte-fill-current.json',report);print(report['status'],len(rows),flush=True)
if __name__=='__main__':main()

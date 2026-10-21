"""Typed register operations versus actual individual68000instructions.
8320finite comparisons cover word preservation,sign extension,CCR/X,branches
and both physical stack banks;no arbitrary register index or memory operation.
"""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/typed-deck-primitives-v1';CODE=0x180000
save=h.save;cpu_dict=h.cpu_dict
def sha(p):return h.sha(Path(p).read_bytes())
def main():
 out=V/'typed-deck-primitives-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=out/'primitives.c';source.write_text('#include "'+str(SRC/'typed-registers.h')+'"\n'+r'''
int apply(struct biwn_task_cpu *cpu,unsigned op){
 struct biwn_deck_context s;s.cpu=*cpu;int branch=-1;
 switch(op){
 case0:deck_cpu_move_w_d(&s,0,s.cpu.registers[2]);break;
 case1:deck_cpu_ext_l_d(&s,0);break;
 case2:deck_cpu_asl6_l_d(&s,0);break;
 case3:deck_cpu_move_l_d_a(&s,0,1);break;
 case4:deck_cpu_adda_l(&s,1,0x47b88);break;
 case5:deck_cpu_clr_w_d(&s,1);break;
 case6:deck_cpu_addq1_w_d(&s,1);break;
 case7:deck_cpu_movea_w_d_a(&s,1,0);break;
 case8:deck_cpu_cmp_l_a_d(&s,0,0);break;
 case9:branch=deck_cpu_bhi(&s);break;
 }
 *cpu=s.cpu;return branch;
}
'''.replace('case0','case 0').replace('case1','case 1').replace('case2','case 2').replace('case3','case 3').replace('case4','case 4').replace('case5','case 5').replace('case6','case 6').replace('case7','case 7').replace('case8','case 8').replace('case9','case 9'))
 lib=out/'primitives.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(lib)).apply;fn.argtypes=[c.POINTER(h.CPU),c.c_uint];fn.restype=c.c_int
 operations=['move.w %d2,%d0','ext.l %d0','asl.l #6,%d0','movea.l %d0,%a1','adda.l #0x47b88,%a1','clr.w %d1','addq.w #1,%d1','movea.w %d1,%a0','cmp.l %a0,%d0','bhi.s taken\nnop\ntaken:nop']
 asm=out/'instructions.S';asm.write_text('.text\n'+''.join('.globl op'+str(n)+'\nop'+str(n)+':'+op+'\n'for n,op in enumerate(operations)));tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');obj=out/'instructions.o';elf=out/'instructions.elf';binary=out/'instructions.bin'
 for command in [[tool+'as','-m68000',str(asm),'-o',str(obj)],[tool+'ld','-Ttext',hex(CODE),'-e','op0',str(obj),'-o',str(elf)],[tool+'objcopy','-O','binary',str(elf),str(binary)]]:subprocess.run(command,check=True,capture_output=True)
 names=subprocess.check_output([tool+'nm','-n',str(elf)],text=True);syms={line.split()[-1]:int(line.split()[0],16)for line in names.splitlines()if len(line.split())==3};memory=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());payload=binary.read_bytes();memory[CODE:CODE+len(payload)]=payload;engine=h.Engine();engine.native.device.seed(bytes(memory),0);rng=random.Random(0xd0a068000);rows=[]
 vals=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff,0x80010001,0xffff7fff,0x7fff8000]
 try:
  for op in range(10):
   for supervisor in [0,1]:
    for flags in range(32):
     for i,value in enumerate(vals):
      initial=h.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[h.SP];initial.registers[0]=(initial.registers[0]&0xffff0000)|(value&65535);initial.registers[1]=(initial.registers[1]&0xffff0000)|(value&65535);initial.registers[2]=value;initial.registers[8]=value;initial.registers[9]=value;initial.pc=syms['op'+str(op)];initial.sr=(0x2000 if supervisor else 0)|((i%8)<<8)|flags;initial.usp=0x1d8000 if supervisor else h.SP;initial.ssp=h.SP if supervisor else 0x1ff000
      engine.set_cpu(initial,True);engine.core.m68k_execute(1);expected=engine.cpu();actual=h.CPU.from_buffer_copy(bytes(initial));branch=fn(c.byref(actual),op)
      if op==9:assert expected.pc==initial.pc+(4 if branch else 2)
      else:assert branch==-1 and expected.pc==syms['op'+str(op+1)]
      actual.pc=expected.pc
      if cpu_dict(actual)!=cpu_dict(expected):save(out/'counterexample.json',dict(op=op,supervisor=supervisor,flags=flags,value=value,initial=cpu_dict(initial),native=cpu_dict(expected),C=cpu_dict(actual)));raise AssertionError(out/'counterexample.json')
      rows.append(dict(op=op,supervisor=supervisor,flags=flags,value=value,full_CPU_match=True))
   print('operation',op,'passed',flush=True)
  assert engine.native.device.ram()==bytes(memory)
 finally:engine.native.close()
 save(out/'cases.json',rows);paths=[Path(__file__),SRC/'typed-registers.h',source,asm,binary,lib,out/'cases.json'];state=dict(status='terminal_typed_register_width_flags_and_branches_match_original_CPU',directory=str(out),completed=len(rows),new_predictions=0,new_training=False,installed_preview_changed=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__);save(out/'review.json',state);save(V/'typed-deck-primitives-v1-current.json',state)
if __name__=='__main__':main()

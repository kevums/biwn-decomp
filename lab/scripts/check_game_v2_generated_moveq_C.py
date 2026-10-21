"""Compile raw local outputs and compare 512 cases against original CPU effects."""
import ctypes as c,json,os,subprocess,argparse
from pathlib import Path
import check_biwn_scheduler as scheduler
parser=argparse.ArgumentParser();parser.add_argument('--grounded',action='store_true');parser.add_argument('--evaluation-pointer',type=Path);parser.add_argument('--report-pointer',type=Path);options=parser.parse_args()
ROOT=scheduler.ROOT;j=json.loads((options.evaluation_pointer or ROOT/'verification/game-source-v2-evaluation-current.json').read_text());out=Path(j['directory'])/('grounded-ISA'if options.grounded else'');run=scheduler.Native();core=run.lib;oracle=[]
try:
 for imm in range(256):
  for X in [0,1]:
   ram=bytearray(0x200000);ram[0x1000:0x1004]=bytes([0x70,imm,0x4e,0x75]);ram[0x1ff000:0x1ff004]=(0x1ffff0).to_bytes(4,'big');run.device.seed(bytes(ram),0);core.m68k_pulse_reset();core.m68k_set_irq(0);initial=0x270f|(X<<4);core.m68k_set_reg(17,initial);core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(0,0x12345678);core.m68k_set_reg(16,0x1000)
   for i in range(16):
    if core.m68k_get_reg(None,16)==0x1ffff0:break
    core.m68k_execute(1)
   else:raise AssertionError('Native return')
   oracle.append((imm,initial,core.m68k_get_reg(None,0),core.m68k_get_reg(None,17)))
 reports=[]
 for phase in ['base','adapter']:
  row=json.loads((out/((phase+'.json')if options.grounded else(phase+'-m68k-C-effect.json'))).read_text());text=row['response'];src=out/(phase+'-moveq.c');src.write_text(text);assert text.startswith('#include <stdint.h>') and '```'not in text
  lib=out/(phase+'-moveq.dylib');command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src),'-o',str(lib)];build=subprocess.run(command,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'},capture_output=True,text=True);(out/(phase+'-compiler.log')).write_text(build.stdout+build.stderr);assert build.returncode==0
  fn=c.CDLL(str(lib)).biwn_moveq_effect;fn.argtypes=[c.c_uint8,c.POINTER(c.c_uint32),c.POINTER(c.c_uint16)];fn.restype=None;failures=[];count=0
  for imm,initial,expected_D,expected_SR in oracle:
   D=c.c_uint32(0x12345678);SR=c.c_uint16(initial);fn(imm,c.byref(D),c.byref(SR))
   if D.value!=expected_D or SR.value!=expected_SR:
    count+=1
    if len(failures)<12:failures.append(dict(immediate=imm,initial_SR=hex(initial),expected_D=hex(expected_D),actual_D=hex(D.value),expected_SR=hex(expected_SR),actual_SR=hex(SR.value)))
  reports.append(dict(phase=phase,compiled=True,cases=512,failures=count,examples=failures,accepted=count==0))
 report=dict(status='generated_C_all_accepted'if all(x['accepted']for x in reports)else'generated_C_semantic_failures',directory=str(out),results=reports,oracle='Original pinned M68000 MOVEQ/RTS with synthetic RAM/stack and both X inputs; full D0/SR compared.',scope='One synthetic instruction-effect routine, not full CPU state/RTS implementation or game proof.',new_local_C_body_accepted=any(x['accepted']for x in reports))
 (out/'compiled-moveq-review.json').write_text(json.dumps(report,indent=2)+'\n');(options.report_pointer or ROOT/('verification/game-source-v2-grounded-C-review.json'if options.grounded else'verification/game-source-v2-C-review.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(results=[{k:x[k]for k in ['phase','cases','failures','accepted']}for x in reports])))
finally:run.close()

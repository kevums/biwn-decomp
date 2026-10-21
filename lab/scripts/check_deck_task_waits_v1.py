"""Qualify outer-task volatile waits against original CPU read boundaries.

The test provider changes one declared flag before each original TST. This
does not model timing or interrupts. Ordered read count is checked only for
that one flag, in addition to CPU/RAM/helper-entry comparisons.
"""
import argparse,ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_deck_task_source_v1 as base
ROOT=base.ROOT;SRC=base.SRC;save=base.save;sha=base.sha;CPU=base.CPU;Bus=base.Bus;SERVICE=base.SERVICE
class Engine(base.Engine):
 def original_wait(self,ram,initial,case,wait_reads):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);entries=[];polls=0
  for step in range(2000):
   state=self.cpu();pc=state.pc
   if pc==base.STOP or(step and pc==0x11e86):return (0 if pc==base.STOP else 6),self.native.device.ram(),state,entries,polls
   if pc in base.HELPERS:
    memory=bytearray(self.native.device.ram());entries.append(self.entry(memory,state));assert self.helper(memory,state,pc,case,len(entries)-1)==0
    self.native.device.seed(bytes(memory),0);state.pc=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big');state.registers[15]+=4
    if state.sr&0x2000:state.ssp=state.registers[15]
    else:state.usp=state.registers[15]
    self.set_cpu(state);continue
   assert 0x11e6c<=pc<0x11f6c,hex(pc)
   if pc==0x11f50:
    self.native.device.direct(0x10a684,4,1 if polls<wait_reads else 0);polls+=1
   self.core.m68k_execute(1)
  raise AssertionError('original wait bound')
def check(source,out):
 out.mkdir(parents=True,exist_ok=True);library=out/'libdeck-task.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(source),'-o',str(library)]
 p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_deck_task_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
 engine=Engine();rows=[]
 try:
  for bank in range(2):
   ram,initial,case=next(x for x in base.fixtures()if x[1].pc==0x11f50 and x[2]['variant']==bank)
   for count in [0,1,3,8,63,65]:
    expected=engine.original_wait(ram,initial,case,count);got=engine.translated(fn,ram,initial,case,poll_budget=128,wait_reads=count)
    polls=sum(e[0]=='r'and e[1]==0x10a684 for e in got[4])
    ok=expected[0]==got[0]and expected[1]==got[1]and base.cpu_dict(expected[2])==base.cpu_dict(got[2])and expected[3]==got[3]and not got[5]and polls==expected[4]==count+1
    if not ok:
     save(out/'counterexample.json',dict(wait_reads=count,bank=bank,original_polls=expected[4],C_polls=polls,original_status=expected[0],C_status=got[0],original_CPU=base.cpu_dict(expected[2]),C_CPU=base.cpu_dict(got[2]),original_entries=expected[3],C_entries=got[3],errors=got[5]));return False,rows
    rows.append(dict(bank=bank,nonzero_reads=count,polls=polls,full_CPU_RAM_and_helper_entry_match=True))
 finally:engine.native.close()
 save(out/'cases.json',rows);return True,rows
def main():
 out=ROOT/'verification/deck-task-volatile-waits'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=SRC/'deck-task-source.c';ok,rows=check(source,out/'positive');assert ok
 mutations=[];text=source.read_text()
 for name,old,new in [('skips_nonzero_wait','if(!v)goto end_display;','if(1)goto end_display;'),('omits_volatile_read','v=deck_read(&s,0x10a684,4);','v=0;')]:
  assert text.count(old)==1;folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(text.replace(old,new));accepted,_=check(candidate,folder/'checks');assert not accepted,name
  mutations.append(dict(name=name,rejected=True,source_sha256=sha(candidate.read_bytes()),counterexample=str(folder/'checks/counterexample.json')))
 paths=[source,SRC/'deck-task-source.h',Path(__file__),Path(base.__file__)]
 report=dict(status='terminal_Deck_task_volatile_waits_and_two_defects_checked',directory=str(out),cases=len(rows),mutations=mutations,source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},scope='12finitewaitcasesinbothbanks with0/1/3/8/63/65externalnonzeroflagreads. OriginalTST/BNEexecutednative;explicitproviderinjectsflagvalueatreadboundary. FullCPU/2MBRAM/privateframes/helperentries plus flagreadcountmatch. Not timing/IRQ/displayhardwareproof.')
 save(out/'report.json',report);save(ROOT/'verification/Deck-task-volatile-waits-current.json',report);print(report['status'],flush=True)
if __name__=='__main__':main()

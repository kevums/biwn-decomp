"""Two original CPU GPU-submit wrappers: ordered accesses, full CPU/SR/banks.

Scripted asynchronous mailbox schedules do not execute GPU code or game frames.
Both the original E098 and the existing derived-disc pending-command repair run
as real machine code. No original command wrapper fallback is permitted.
"""
import argparse,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_mailbox_engine as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=e.ND/'gpu-mailbox-reference-v1.c');args=ap.parse_args()
 out=e.ROOT/'verification/native-gpu-mailbox-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 run=subprocess.run(['make','-f','Makefile.gpu-mailbox','gpu-mailbox','BUILD='+str(out/'build'),'MAILBOX_SOURCE='+str(args.source.resolve())],cwd=e.ND,capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 binary=out/'build/gpu-mailbox.bin';elf=out/'build/gpu-mailbox.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
 snapshot_path=e.ROOT/'render-assets/biwn-inventory-baseline.bin';snapshot=snapshot_path.read_bytes();assert e.sha(snapshot_path)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
 rows=e.cases()
 if args.limit:rows=[row for entry in e.ROOTS for helper in ['original','pending_repair']for row in [c for c in rows if c['entry']==entry and c['helper']==helper][:args.limit]]
 inputs=[Path(__file__),Path(e.__file__),args.source.resolve(),binary,elf,snapshot_path,*[e.ND/name for name in ['gpu-mailbox-native.h','gpu-mailbox-shim-v1.S','gpu-mailbox.ld','Makefile.gpu-mailbox']],e.ROOT/'scripts/check_biwn_scheduler.py',e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
 parent=e.read(e.ROOT/'verification/native-actor-direction-disc-build-current.json');inputs += [Path(parent['derived_stage']),Path(parent['component'])];hashes={str(p):e.sha(p)for p in inputs}
 state=dict(status='checking_native_gpu_mailbox',pid=os.getpid(),directory=str(out),planned=len(rows),completed=0,binary=str(binary),ELF=str(elf),binary_bytes=len(payload),code_address=e.BASE,symbols=symbols,source_sha256=hashes,disc_integrated=False,new_predictions=0,scope=__doc__)
 def mark():e.save(out/'protocol.json',state);e.save(e.ROOT/'verification/native-gpu-mailbox-active.json',state)
 mark();e.save(out/'fixtures.json',rows);results=[];coverage=set();native=e.Native()
 try:
  for index,case in enumerate(rows):
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[key for key in ['ram','registers','trace','mmio']if a[key]!=b[key]]
   if diff:e.save(out/'mismatch.json',dict(index=index,case=case,differences=diff,original_trace=a['trace'],candidate_trace=b['trace'],original_regs=a['registers'],candidate_regs=b['registers']));raise AssertionError('Ordered GPU mailbox comparison failed')
   an=e.replay(native,snapshot,case,payload,symbols,False,a);bn=e.replay(native,snapshot,case,payload,symbols,True,b)
   if an!=bn:e.save(out/'native-mismatch.json',dict(index=index,case=case,original=an,candidate=bn));raise AssertionError('Native GPU mailbox CPU/SR/banks/helper-entry mismatch')
   ram=native.device.ram();context=e.SP-96;shadow=[int.from_bytes(ram[context+4*i:context+4*i+4],'big')for i in range(18)];assert shadow[:15]==bn['registers'][:15]and shadow[15]==e.SP and shadow[16]==bn['SR']and shadow[17]==case['entry'],'Returned logical C context mismatch'
   coverage.update(a['coverage']);results.append(dict(index=index,entry=case['entry'],helper=case['helper'],original_steps=len(a['machine']),candidate_steps=len(b['machine']),original_depth=a['private_depth'],candidate_depth=b['private_depth']))
   if index%64==0:state['completed']=len(results);mark();print('Mailbox',index+1,'/',len(rows),flush=True)
  assert all(e.sha(p)==h for p,h in hashes.items());e.save(out/'results.json',results)
  state.update(status='terminal_native_gpu_mailbox_preflight_pass'if args.limit else'terminal_native_gpu_mailbox_prototype_pass',completed=len(results),cases=len(results),per_root_helper_cases={hex(entry)+'/'+helper:sum(row['entry']==entry and row['helper']==helper for row in rows)for entry in e.ROOTS for helper in ['original','pending_repair']},original_sites=sorted(coverage),max_private_depth=max(row['candidate_depth']for row in results));mark()
  if not args.limit:e.save(e.ROOT/'verification/native-gpu-mailbox-current.json',state)
  print(state['status'],len(rows),'bytes',len(payload),'depth',state['max_private_depth'])
 except BaseException as error:state.update(status='terminal_native_gpu_mailbox_failed',error=repr(error),completed=len(results));mark();raise
 finally:native.close()
if __name__=='__main__':main()

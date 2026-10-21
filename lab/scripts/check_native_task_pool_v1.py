"""Complete supervisor-entry task-pool initialization, including native user switch."""
import argparse,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_task_pool_engine_v1 as e
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=e.ND/'task-pool-reference-v1.c');args=ap.parse_args();out=e.ROOT/'verification/native-task-pool-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 p=subprocess.run(['make','-f','Makefile.task-pool','task-pool','BUILD='+str(out/'build'),'POOL_SOURCE='+str(args.source.resolve())],cwd=e.ND,capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 binary=out/'build/task-pool.bin';elf=out/'build/task-pool.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=e.cases();rows=rows[:args.limit]if args.limit else rows;native=e.Native();results=[];coverage=set()
 inputs=[Path(__file__),Path(e.__file__),args.source.resolve(),binary,elf,*[e.ND/name for name in ['task-pool-native.h','task-pool-shim-v1.S','task-pool.ld','Makefile.task-pool']],e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',e.ROOT/'render-assets/biwn-inventory-baseline.bin'];hashes={str(p):e.sha(p)for p in inputs};state=dict(status='checking_native_task_pool',pid=os.getpid(),directory=str(out),planned=len(rows),completed=0,binary=str(binary),ELF=str(elf),binary_bytes=len(payload),symbols=symbols,code_address=e.BASE,source_sha256=hashes,disc_integrated=False,new_predictions=0)
 def mark():e.save(out/'protocol.json',state);e.save(e.ROOT/'verification/native-task-pool-active.json',state)
 mark()
 try:
  for index,case in enumerate(rows):
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[k for k in ['ram','registers','USP','trace']if a[k]!=b[k]]
   if diff:e.save(out/'mismatch.json',dict(index=index,case=case,differences=diff,original_trace=a['trace'],candidate_trace=b['trace'],original_regs=a['registers'],candidate_regs=b['registers']));raise AssertionError('Task-pool prefix comparison failed')
   an=e.replay(native,snapshot,case,payload,symbols,False,a);bn=e.replay(native,snapshot,case,payload,symbols,True,b);assert an['pre']==bn['pre']and an['final']==bn['final'],(index,an,bn)
   ram=native.device.ram();main=int.from_bytes(ram[0xc0920:0xc0924],'big');free=int.from_bytes(ram[0xc0924:0xc0928],'big');nodes=[]
   while free:assert free==0xc0d28+len(nodes)*0x400 and len(nodes)<101;nodes.append(free);free=int.from_bytes(ram[free:free+4],'big')
   assert main==0xc0928 and len(nodes)==100 and nodes[-1]==0xd9928 and bn['final']['registers'][15]==0xc0d28 and bn['final']['SSP']==case['ssp']and not bn['final']['SR']&0x2000
   coverage.update(a['coverage']);results.append(dict(index=index,pre=bn['pre'],final=bn['final'],ordered_events=len(a['trace']),free_nodes=len(nodes),candidate_depth=b['private_depth']))
   if index%64==0:state['completed']=len(results);mark();print('Task pool',index+1,'/',len(rows),flush=True)
  assert all(e.sha(p)==h for p,h in hashes.items());e.save(out/'cases.json',rows);e.save(out/'results.json',results);state.update(status='terminal_native_task_pool_preflight_pass'if args.limit else'terminal_native_task_pool_CPU_RAM_USP_order_and_mode_pass',completed=len(results),cases=len(results),original_sites=sorted(coverage),max_private_depth=max(x['candidate_depth']for x in results),task_pool_base=0xc0928,task_stride=1024,free_task_slots=100,total_task_slots=101,task_pool_end_exclusive=0xd9d28,main_stack_top=0xc0d28,scope=__doc__+' Fixed initialized task pool; supervisor/noIRQ domain. Faults,asynchronousIRQ,timing,actual main task execution and resource ownership beyond this initialized region remain separate.');mark()
  if not args.limit:e.save(e.ROOT/'verification/native-task-pool-current.json',state)
  print({k:state[k]for k in ['status','cases','binary_bytes','max_private_depth']})
 except BaseException as error:state.update(status='terminal_native_task_pool_failed',error=repr(error),completed=len(results));mark();raise
 finally:native.close()
if __name__=='__main__':main()

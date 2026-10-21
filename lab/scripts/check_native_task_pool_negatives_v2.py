"""Four initializer defects, including USP order with identical final RAM/CPU."""
import capstone,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_task_pool_engine_v1 as e
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(e.ROOT/'verification/native-task-pool-current.json');assert gate['cases']==512;out=e.ROOT/'verification/native-task-pool-negatives-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=(e.ND/'task-pool-reference-v1.c').read_text();snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();rows=[];coverage=set();case=e.cases()[0]
 wait=' biwn_native_task_pool_set_usp(r[9]);r[17]=r[9];\n';late=source.replace(wait,'');assert source!=late;at=late.rfind('}');late=late[:at]+wait+late[at:]
 defects=[('wrong_link_count',source.replace('|98u','|97u')),('wrong_record_stride',source.replace('r[8]+0x400u','r[8]+0x404u')),('lost_D0_upper_word',source.replace('(r[0]&0xffff0000u)|98u','98u')),('USP_moved_after_header_clears',late)]
 try:
  for name,text in defects:
   assert text!=source;folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(text);run=subprocess.run(['make','-f','Makefile.task-pool','task-pool','BUILD='+str(folder/'build'),'POOL_SOURCE='+str(candidate)],cwd=e.ND,capture_output=True,text=True);(folder/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
   binary=folder/'build/task-pool.bin';elf=folder/'build/task-pool.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[k for k in ['ram','registers','USP','trace']if a[k]!=b[k]];left=e.replay(native,snapshot,case,payload,symbols,False,a);right=None
   try:right=e.replay(native,snapshot,case,payload,symbols,True,b)
   except AssertionError as error:diff.append('native_good_USP_or_execution_invariant:'+repr(error))
   if right is not None and(left['pre']!=right['pre']or left['final']!=right['final']):diff.append('native_CPU_SR_banks')
   assert diff,(name,'Escaped')
   if name=='USP_moved_after_header_clears':assert diff==['trace']and a['ram']==b['ram']and left['final']==right['final']
   coverage.update(a['coverage']);coverage.update(left['tail_steps']);row=dict(defect=name,rejected=True,differences=diff,binary_sha256=e.sha(binary));e.save(folder/'result.json',row);rows.append(row);print(name,diff,flush=True)
  decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);sites={i.address for i in decoder.disasm(snapshot[e.ENTRY:e.END],e.ENTRY)};assert sites<=coverage
  e.save(out/'results.json',rows);paths=[Path(__file__),Path(e.__file__),out/'results.json',e.ND/'task-pool-reference-v1.c'];state=dict(status='terminal_task_pool_four_semantic_negatives_and_all_sites_pass',directory=str(out),negative_controls=rows,original_instruction_sites=[len(sites),len(sites&coverage)],native_mode_transition_included=True,source_sha256={str(p):e.sha(p)for p in paths},new_predictions=0,new_training=False,scope=__doc__);e.save(out/'protocol.json',state);e.save(e.ROOT/'verification/native-task-pool-negatives-current.json',state);print(state['status'],len(sites))
 finally:native.close()
if __name__=='__main__':main()

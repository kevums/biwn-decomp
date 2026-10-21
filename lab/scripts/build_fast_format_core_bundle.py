"""Compiler-only inline specialization on the same expanded resident layout."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import lower_biwn_format_core_native as core
import lower_biwn_format_number_native as number
def main():
 pp=ROOT/'verification/native-core-format-bundle-current.json';parent=json.loads(pp.read_text());native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 out=ROOT/'verification/native-fast-core-bundle'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);sources=out/'sources';sources.mkdir()
 for record,key in [(parent,'source_sha256')]:
  for p,h in record[key].items():assert sha(p)==h,p
 original={};fast={}
 for name,lowerer in [('core',core),('number',number)]:
  code,facts=lowerer.generate();canonical=native/f'format-{name}-native.c';assert code==canonical.read_text()
  transformed=code.replace('static inline ','static inline __attribute__((always_inline)) ')
  for helper in ['np_unsigned','np_shift']:
   transformed=transformed.replace('static void '+helper+'(', 'static inline __attribute__((always_inline)) void '+helper+'(')
  path=sources/f'format-{name}-native.c';path.write_text(transformed);original[name]=canonical;fast[name]=path
  save(sources/(name+'-facts.json'),facts)
 helper=native/'m68k-fact-helpers-v2.h';fasthelper=sources/helper.name;fasthelper.write_text(helper.read_text().replace('static inline ','static inline __attribute__((always_inline)) '))
 oldmake=Path(parent['directory'])/'Makefile';text=oldmake.read_text()
 for name in ['core','number']:
  old=f'$(BUILD)/format-{name}-native.o: format-{name}-native.c';new=f'$(BUILD)/format-{name}-native.o: '+str(fast[name]);assert text.count(old)==1;text=text.replace(old,new)
 make=out/'Makefile';make.write_text(text);result=subprocess.run(['make','-f',str(make),'format-bundle','BUILD='+str(out/'build')],cwd=native,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 binary=out/'build/native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();assert len(payload)<=parent['reserved_bytes'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
 for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
  a=line.split()
  if len(a)==3:symbols[a[2]]=int(a[0],16)
 save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
 before=Path(parent['binary']).read_bytes();first=parent['symbols']['biwn_native_format_number_body']-parent['base']
 # Earlier helper bodies remain exactly linked. Local unused flag helpers may
 # disappear before the number body, so verify globals and full concrete diff.
 changes=[dict(offset=i,address=hex(parent['base']+i),old=x,new=y)for i,(x,y)in enumerate(zip(before,payload))if x!=y]
 stable=['biwn_native_heap_allocate_body','biwn_native_heap_compact_body','biwn_native_scheduler_dispatch','biwn_native_scheduler_remove','biwn_native_scheduler_select','biwn_native_scheduler_rte','biwn_native_task_create','biwn_native_copy_body','biwn_native_free_body','biwn_native_heap_initialize','biwn_native_resource_release_body','biwn_native_resource_acquire','biwn_native_resource_acquire_body','biwn_native_resource_load','biwn_native_resource_load_body','biwn_native_load_scan']
 assert all(symbols[k]==parent['symbols'][k]for k in stable)
 paths=[Path(__file__),pp,oldmake,make,original['core'],original['number'],helper,fasthelper,*fast.values(),ROOT/'scripts/lower_biwn_format_core_native.py',ROOT/'scripts/lower_biwn_format_number_native.py',*out.glob('build/*.o'),binary,elf]
 state={**parent,'status':'compiler_inline_specialized_full_formatter_pending_revalidation','directory':str(out),'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'binary_bytes':len(payload),'padding_bytes':parent['reserved_bytes']-len(payload),'symbols':symbols,'parent_bundle_proof':str(pp),'parent_bundle_sha256':sha(pp),'source_sha256':{str(p):sha(p)for p in paths},'optimized_sources':{k:str(v)for k,v in fast.items()},'optimized_header':str(fasthelper),'optimization':'Always-inline pure register/CCR helpers and constant-path adapters; instruction semantics/volatile accesses unchanged. No source-entry fallback or timing compensation. Same Os compiler flags,16384reservation/heap162DC0/F8000..FE000staging.','previous_prefix_changes':changes,'previous_prefix_change_count':len(changes),'previous_number_body_offset':first,'common_resource_symbol_positions_unchanged':stable,'standalone_source_accepted':False,'disc_built':False,'whole_game_complete':False,'default_promoted':False}
 save(out/'bundle.json',state);save(ROOT/'verification/native-fast-core-format-bundle-current.json',state);print(json.dumps({k:state[k]for k in ['status','directory','binary_bytes','padding_bytes','previous_prefix_change_count']}))
if __name__=='__main__':main()

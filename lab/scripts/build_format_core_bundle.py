"""Native formatter/core bundle; explicit heap and zero-staging expansion."""
import datetime,json,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 pp=ROOT/'verification/native-number-format-bundle-current.json';parent=json.loads(pp.read_text());gp=ROOT/'verification/native-format-core-current.json';gate=json.loads(gp.read_text());assert gate['source_accepted']and gate['status']=='terminal_native_format_core_full_CPU_RAM_ordered_pass'
 for record,key in [(parent,'source_sha256'),(gate,'dependencies_sha256')]:
  for p,h in record[key].items():assert sha(p)==h,p
 out=ROOT/'verification/native-core-bundle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 reserve=16384;heap=parent['base']+reserve;staging=0xf8000;clear=24576
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=session/'nextstage-68000-candidate.bin';original=stage.read_bytes();assert original[staging-0x4000:staging-0x4000+clear]==bytes(clear)
 oldmake=Path(parent['directory'])/'Makefile';oldld=Path(parent['directory'])/'number-bundle.ld';ld=out/'core-bundle.ld'
 text=oldld.read_text();assert text.count(hex(parent['heap_start']))==1 and text.count(hex(parent['reserved_bytes']))==1
 ld.write_text('EXTERN(biwn_native_format_core biwn_native_format_variadic)\n'+text.replace(hex(parent['heap_start']),hex(heap)).replace(hex(parent['reserved_bytes']),hex(reserve)).replace('11264byte','16384byte'))
 oldstartup=ROOT/'verification/native-format-bundle/20261018T151216.180656Z/startup-format.S';startup=out/'startup-core.S'
 startup.write_text(oldstartup.read_text().replace('New8KB staging window FB000..FE000','New24KB staging window F8000..FE000').replace('0xfb000','0xf8000').replace('#6143','#12287'))
 text=oldmake.read_text().replace(str(oldld),str(ld)).replace(str(oldstartup),str(startup));objects='$(BUILD)/format-core-shim.o $(BUILD)/format-core-native.o'
 line=next(x for x in text.splitlines()if x.startswith('$(BUILD)/native-format-bundle.elf:'));text=text.replace(line,line+' '+objects)
 line=next(x for x in text.splitlines()if x.startswith('\t$(CROSS)ld --gc-sections'));new=line.replace('$(filter-out ','$(filter-out '+objects+' ')+' '+objects;assert line!=new;text=text.replace(line,new)
 text+='''
$(BUILD)/format-core-shim.o: format-core-shim.S | $(BUILD)
\t$(CROSS)as -m68000 -o $@ $<
$(BUILD)/format-core-native.o: format-core-native.c format-core-native.h | $(BUILD)
\t$(CROSS)gcc $(CFLAGS) -Os -fstack-usage -Wall -Wextra -Werror -I. -c $< -o $@
'''
 make=out/'Makefile';make.write_text(text);native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 result=subprocess.run(['make','-f',str(make),'format-bundle','BUILD='+str(out/'build')],cwd=native,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 binary=out/'build/native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();prior=Path(parent['binary']).read_bytes();assert len(payload)<=reserve
 prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={};global_symbols={}
 for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
  a=line.split()
  if len(a)==3:
   symbols[a[2]]=int(a[0],16)
   if a[1].isupper():global_symbols[a[2]]=int(a[0],16)
 save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
 changes=[dict(offset=i,address=hex(parent['base']+i),old=x,new=y)for i,(x,y)in enumerate(zip(prior,payload))if x!=y]
 expected=bytearray(prior)
 for displacement in [0,4,8]:
  expected=bytearray(expected.replace((parent['heap_start']+displacement).to_bytes(4,'big'),(heap+displacement).to_bytes(4,'big')))
 # Source-assembled startup has the same instruction footprint. Only its
 # zero-range address/DBRA limit differ; entire remaining prefix must be exact.
 pos=parent['symbols']['biwn_native_startup_finalize']-parent['base'];oldbytes=prior[pos:pos+32];newbytes=oldbytes.replace((0xfb000).to_bytes(4,'big'),staging.to_bytes(4,'big')).replace((6143).to_bytes(2,'big'),(12287).to_bytes(2,'big'));expected[pos:pos+32]=newbytes
 assert payload[:len(prior)]==expected,'Undeclared previous-prefix change'
 assert all(v==parent['symbols'][k]for k,v in global_symbols.items()if k in parent['symbols']and k!='biwn_native_heap_start'),'Existing global symbol moved'
 state={**parent,'status':'native_core_variadic_expanded_layout_linked_pending_integration','directory':str(out),'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'binary_bytes':len(payload),'symbols':symbols,'reserved_bytes':reserve,'heap_start':heap,'padding_bytes':reserve-len(payload),'staging':staging,'staging_clear_bytes':clear,'parent_bundle_proof':str(pp),'parent_bundle_sha256':sha(pp),'existing_prefix_bytes_exact':False,'previous_prefix_changes':changes,'previous_global_function_symbols_unchanged':True,'new_original_entries':['0x1B29C','0x1B45A'],'disc_built':False,'whole_game_complete':False,'source_sha256':{str(p):sha(p)for p in [Path(__file__),pp,gp,oldmake,oldld,oldstartup,startup,stage,make,ld,*out.glob('build/*.o'),binary,elf,native/'format-core-native.c',native/'format-core-native.h',native/'format-core-shim.S']}}
 save(out/'bundle.json',state);save(ROOT/'verification/native-core-format-bundle-current.json',state)
 print(json.dumps({k:state[k]for k in ['status','directory','binary_bytes','padding_bytes','heap_start','staging','staging_clear_bytes','previous_prefix_changes']}))
if __name__=='__main__':main()

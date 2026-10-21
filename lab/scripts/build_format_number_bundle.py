"""Link proven number C into the resident image with an explicit larger heap floor."""
import datetime,json,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 parent_path=ROOT/'verification/native-unsigned-bundle-current.json';parent=json.loads(parent_path.read_text())
 proof_path=ROOT/'verification/native-format-number-current.json';proof=json.loads(proof_path.read_text())
 assert proof['status']=='terminal_native_format_number_CPU_RAM_ordered_zero_fault_pass'
 assert sha(parent['binary'])==parent['binary_sha256']
 for record,table in [(parent,'source_sha256'),(proof,'dependencies_sha256')]:
  for p,h in record[table].items():assert sha(p)==h,p
 out=ROOT/'verification/native-number-bundle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 old_make=Path(parent['directory'])/'Makefile';old_ld=Path(parent['directory'])/'unsigned-bundle.ld'
 reserve=11264;heap=parent['base']+reserve;ld=out/'number-bundle.ld'
 text=old_ld.read_text();assert text.count('0x1611c0')==1 and text.count('0x2400')==1
 text='EXTERN(biwn_native_format_number)\n'+text.replace('0x1611c0',hex(heap)).replace('0x2400',hex(reserve)).replace('9216byte','11264byte');ld.write_text(text)
 text=old_make.read_text().replace(str(old_ld),str(ld))
 line=next(x for x in text.splitlines() if x.startswith('$(BUILD)/native-format-bundle.elf:'))
 objects='$(BUILD)/format-number-shim.o $(BUILD)/semantic-divide-zero.o $(BUILD)/format-number-native.o'
 text=text.replace(line,line+' '+objects)
 # Keep all previous text objects/libgcc/math in their existing order. New
 # number objects are appended after them, not before the established prefix.
 old='$(filter-out $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o,$(filter %.o,$^)) $(LIBGCC) $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o'
 new='$(filter-out $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o '+objects+',$(filter %.o,$^)) $(LIBGCC) $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o '+objects
 assert text.count(old)==1;text=text.replace(old,new)
 text+='''
$(BUILD)/format-number-shim.o: format-number-shim.S | $(BUILD)
\t$(CROSS)as -m68000 -o $@ $<
$(BUILD)/semantic-divide-zero.o: semantic-divide-zero.S | $(BUILD)
\t$(CROSS)as -m68000 -o $@ $<
$(BUILD)/format-number-native.o: format-number-native.c format-number-native.h | $(BUILD)
\t$(CROSS)gcc $(CFLAGS) -Os -fstack-usage -Wall -Wextra -Werror -I. -c $< -o $@
'''
 make=out/'Makefile';make.write_text(text);native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 result=subprocess.run(['make','-f',str(make),'format-bundle','BUILD='+str(out/'build')],cwd=native,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 binary=out/'build/native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();prior=Path(parent['binary']).read_bytes();assert len(payload)<=reserve
 prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={a[2]:int(a[0],16) for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines() if len(a:=line.split())==3}
 save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
 changes=[dict(offset=i,address=hex(parent['base']+i),old=x,new=y) for i,(x,y)in enumerate(zip(prior,payload)) if x!=y]
 moves={k:[v,symbols.get(k)] for k,v in parent['symbols'].items() if symbols.get(k)!=v}
 state={**parent,'status':'native_number_larger_reservation_linked_pending_integration','directory':str(out),'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'binary_bytes':len(payload),'symbols':symbols,'reserved_bytes':reserve,'heap_start':heap,'padding_bytes':reserve-len(payload),'parent_bundle_proof':str(parent_path),'parent_bundle_sha256':sha(parent_path),'existing_prefix_bytes_exact':False,'previous_prefix_changes':changes,'previous_symbol_moves':moves,'new_original_entries':[hex(0x1b212)],'disc_built':False,'whole_game_complete':False,'source_sha256':{str(p):sha(p)for p in [Path(__file__),parent_path,proof_path,old_make,old_ld,make,ld,*out.glob('build/*.o'),binary,elf,native/'format-number-native.c',native/'format-number-native.h',native/'format-number-shim.S',native/'semantic-divide-zero.S']}}
 save(out/'bundle.json',state);save(ROOT/'verification/native-number-format-bundle-current.json',state)
 print(json.dumps({k:state[k]for k in ['status','directory','binary_bytes','padding_bytes','heap_start','previous_prefix_changes','previous_symbol_moves']}))
if __name__=='__main__':main()

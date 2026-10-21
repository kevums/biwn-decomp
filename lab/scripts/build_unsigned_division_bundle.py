"""Append verified unsigned bodies without moving any existing payload byte."""
import datetime,json,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
parent_path=ROOT/'verification/native-string-ccr-bundle-current.json';parent=json.loads(parent_path.read_text());proof_path=ROOT/'verification/native-unsigned-division-current.json';proof=json.loads(proof_path.read_text())
assert proof['status']=='terminal_native_unsigned_full_CPU_public_accesses_zero_fault_pass'
assert sha(parent['binary'])==parent['binary_sha256']
for p,h in parent['source_sha256'].items():assert sha(p)==h,p
for p,h in proof['dependencies_sha256'].items():assert sha(p)==h,p
out=ROOT/'verification/native-unsigned-bundle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
old_make=Path(parent['directory'])/'Makefile';text=old_make.read_text();old_ld=ROOT/'verification/native-format-bundle/20261018T151216.180656Z/format-bundle.ld';ld=out/'unsigned-bundle.ld';ld.write_text('EXTERN(biwn_native_unsigned_divide biwn_native_unsigned_remainder)\n'+old_ld.read_text())
text=text.replace(str(old_ld),str(ld))
elfline=next(line for line in text.splitlines() if line.startswith('$(BUILD)/native-format-bundle.elf:'))
text=text.replace(elfline,elfline+' $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o')
old='$(filter %.o,$^) $(LIBGCC)';new='$(filter-out $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o,$(filter %.o,$^)) $(LIBGCC) $(BUILD)/unsigned-division-shim.o $(BUILD)/unsigned-division-native.o';assert text.count(old)==1;text=text.replace(old,new)
text+='''\n$(BUILD)/unsigned-division-shim.o: unsigned-division-shim.S | $(BUILD)
\t$(CROSS)as -m68000 -o $@ $<
$(BUILD)/unsigned-division-native.o: unsigned-division-native.c unsigned-division-native.h | $(BUILD)
\t$(CROSS)gcc -m68000 -msoft-float -std=c99 -O2 -ffreestanding -ffunction-sections -fdata-sections -fno-common -fno-pie -fno-pic -fno-stack-protector -Os -Wall -Wextra -Werror -I. -c $< -o $@
'''
make=out/'Makefile';make.write_text(text);native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';cmd=['make','-f',str(make),'format-bundle','BUILD='+str(out/'build')];result=subprocess.run(cmd,cwd=native,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
binary=out/'build/native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();old_payload=Path(parent['binary']).read_bytes();assert payload[:len(old_payload)]==old_payload,'Existing prefix changed'
assert len(payload)<=parent['reserved_bytes']
prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
 fields=line.split()
 if len(fields)==3:symbols[fields[2]]=int(fields[0],16)
assert all(symbols[k]==v for k,v in parent['symbols'].items())
state={**parent,'status':'unsigned_division_appended_existing_prefix_exact_pending_integration','directory':str(out),'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'binary_bytes':len(payload),'symbols':symbols,'padding_bytes':parent['reserved_bytes']-len(payload),'parent_bundle_proof':str(parent_path),'parent_bundle_sha256':sha(parent_path),'existing_prefix_bytes_exact':len(old_payload),'new_original_entries':[hex(0xe61c),hex(0xe67c)],'disc_built':False,'whole_game_complete':False,'source_sha256':{str(p):sha(p) for p in [Path(__file__),parent_path,proof_path,old_make,old_ld,make,ld,*out.glob('build/*.o'),binary,elf,native/'unsigned-division-native.c',native/'unsigned-division-native.h',native/'unsigned-division-shim.S']}}
save(out/'bundle.json',state);save(ROOT/'verification/native-unsigned-bundle-current.json',state);print(json.dumps({k:state[k] for k in ['status','directory','binary_bytes','existing_prefix_bytes_exact','padding_bytes']}))

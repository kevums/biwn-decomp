"""Separate format-integration build; no existing build or preview is replaced."""
import hashlib,json,os,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
BASE,RESERVE,STAGING,CLEAR=0x15edc0,0x2400,0xfb000,0x3000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'verification/native-format-bundle'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'build';print(out,flush=True)
    pad=NATIVE/'format-pad-reference.c';string_gate=json.loads((ROOT/'verification/native-format-string-current.json').read_text());string=Path(string_gate['source']);assert sha(string)==string_gate['source_sha256']and string_gate['source_accepted']
    pad_gate=json.loads((ROOT/'verification/native-format-pad-current.json').read_text());assert pad_gate['source_accepted']and pad_gate['coordinator_reference']and pad_gate['source_sha256']==sha(pad)
    startup=out/'startup-format.S';startup.write_text((NATIVE/'startup-finalize-heap.S').read_text().replace('FC000..FE000','FB000..FE000').replace('0xfc000','0xfb000').replace('#4095','#6143'))
    linker=out/'format-bundle.ld';text=(NATIVE/'load-scan-bundle.ld').read_text().replace('0x160bc0',hex(BASE+RESERVE)).replace('0x1e00','0x2400').replace('7680byte','9216byte');text='EXTERN(biwn_native_format_pad biwn_native_format_string)\n'+text;linker.write_text(text)
    line=next(x for x in(NATIVE/'Makefile.load-scan-bundle').read_text().splitlines()if x.startswith('$(BUILD)/native-load-scan-bundle.elf:'))
    objects=list(dict.fromkeys(re.findall(r'\$\(BUILD\)/[\w.-]+\.o',line)));objects.remove('$(BUILD)/startup-finalize-heap.o');objects += ['$(BUILD)/startup-format.o','$(BUILD)/format-pad-shim.o','$(BUILD)/format-pad-body.o','$(BUILD)/format-string-shim.o','$(BUILD)/format-string-body.o']
    makefile=out/'Makefile';makefile.write_text('include Makefile.load-scan-bundle\n.DEFAULT_GOAL := format-bundle\nformat-bundle: $(BUILD)/native-format-bundle.bin\n'+
      f'$(BUILD)/startup-format.o: {startup} | $(BUILD)\n\t$(CROSS)as -m68000 -o $@ $<\n'+
      '$(BUILD)/format-pad-shim.o: format-pad-shim.S | $(BUILD)\n\t$(CROSS)as -m68000 -o $@ $<\n'+
      '$(BUILD)/format-string-shim.o: format-string-shim.S | $(BUILD)\n\t$(CROSS)as -m68000 -o $@ $<\n'+
      f'$(BUILD)/format-pad-body.o: {pad} format-pad-native.h | $(BUILD)\n\t$(CROSS)gcc $(CFLAGS) -I. -Wall -Wextra -Werror -c $< -o $@\n'+
      f'$(BUILD)/format-string-body.o: {string} format-string-native.h m68k-fact-helpers-v2.h | $(BUILD)\n\t$(CROSS)gcc $(CFLAGS) -I. -Wall -Wextra -Werror -c $< -o $@\n'+
      '$(BUILD)/native-format-bundle.elf: '+' '.join(objects)+f' {linker} $(LIBGCC)\n\t$(CROSS)ld --gc-sections -T {linker} -Map $(BUILD)/native-format-bundle.map -o $@ $(filter %.o,$^) $(LIBGCC)\n'+
      '$(BUILD)/native-format-bundle.bin: $(BUILD)/native-format-bundle.elf\n\t$(CROSS)objcopy -O binary $< $@\n')
    command=['make','-f',str(makefile),'format-bundle','BUILD='+str(build)]
    p=subprocess.run(command,cwd=NATIVE,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    binary=build/'native-format-bundle.bin';payload=binary.read_bytes();assert len(payload)<=RESERVE
    prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=build/'native-format-bundle.elf';symbols={}
    for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
        row=line.split()
        if len(row)==3:symbols[row[2]]=int(row[0],16)
    assert symbols['biwn_native_heap_start']==BASE+RESERVE
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage[STAGING-0x4000:STAGING-0x4000+CLEAR]==bytes(CLEAR)
    (out/'symbols.json').write_text(json.dumps(symbols,indent=2)+'\n');(out/'linked-disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-d',str(elf)],text=True))
    paths=[Path(__file__),makefile,linker,startup,pad,string,NATIVE/'format-pad-shim.S',NATIVE/'format-string-shim.S',NATIVE/'format-pad-native.h',NATIVE/'format-string-native.h',NATIVE/'m68k-fact-helpers-v2.h',binary,elf]
    # Every linked object and dependency file is kept with this separate build.
    paths += [p for p in build.glob('*.o')]
    report=dict(status='native_format_bundle_linked_pending_callers_and_boot',pid=os.getpid(),directory=str(out),binary=str(binary),binary_sha256=sha(binary),ELF=str(elf),symbols=symbols,base=BASE,reserved_bytes=RESERVE,heap_start=BASE+RESERVE,staging=STAGING,staging_clear_bytes=CLEAR,binary_bytes=len(payload),padding_bytes=RESERVE-len(payload),pad_source=str(pad),pad_authorship='Codex coordinator reference, full original-CPU helper proof',string_source=str(string),string_authorship='deterministic typed-instruction lifter, full original-CPU helper proof',source_sha256={str(p):sha(p)for p in paths},disc_built=False,default_promoted=False,whole_game_complete=False)
    (out/'protocol.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/native-format-bundle-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','binary_bytes','reserved_bytes','heap_start','padding_bytes']}),flush=True)
if __name__=='__main__':main()

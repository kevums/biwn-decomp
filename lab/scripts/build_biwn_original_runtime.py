"""Recover named assembler source and reproduce the original compiler runtime.

Every instruction is emitted as a mnemonic with branch labels. No embedded
opcode arrays or binary includes substitute for recovered source.
"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import binary_tools
from extract_biwn_stage import STAGE_SHA


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()==STAGE_SHA
    original=stage[0xe540-0x4000:0xe61c-0x4000]
    rows,_=binary_tools.m68k_instructions(original,0xe540)
    assert rows[-1]['address']+rows[-1]['size']==0xe61c
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    source=native/'runtime-original.S'
    lines=['/* Recovered M68000 compiler-runtime assembly from verified original instructions.',
           ' * Labels and mnemonics replace raw machine bytes; exact same-address linking is checked. */',
           '.section .text.biwn_original_runtime,"ax",@progbits',
           '.globl biwn_runtime_multiply,biwn_runtime_division,biwn_runtime_remainder']
    exports={0xe540:'biwn_runtime_multiply',0xe588:'biwn_runtime_division',0xe60a:'biwn_runtime_remainder'}
    addresses={row['address']for row in rows}
    for row in rows:
        address=row['address'];instruction=row['assembly']
        if address in exports:lines.append(exports[address]+':')
        lines.append('L_'+format(address,'x')+':')
        instruction=re.sub(r'\$([0-9a-f]+)',lambda m:'L_'+m[1]if int(m[1],16)in addresses else'0x'+m[1],instruction)
        instruction=re.sub(r'\b(d[0-7]|a[0-7])\b',r'%\1',instruction)
        lines.append(' '+instruction.replace('bra.b','bra.s').replace('exg.l','exg'))
    source.write_text('\n'.join(lines)+'\n')
    linker=native/'runtime-original.ld'
    linker.write_text('ENTRY(biwn_runtime_multiply)\nSECTIONS { . = 0xe540; .text : { KEEP(*(.text.biwn_original_runtime)) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }\nASSERT(SIZEOF(.text)==220,"Recovered runtime size changed")\n')
    out=ROOT/'verification/native-original-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    p=subprocess.run([prefix+'as','-m68000','-o',str(out/'runtime.o'),str(source)],capture_output=True,text=True)
    (out/'assemble.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    subprocess.run([prefix+'ld','-T',str(linker),'-o',str(out/'runtime.elf'),str(out/'runtime.o')],check=True)
    subprocess.run([prefix+'objcopy','-O','binary',str(out/'runtime.elf'),str(out/'runtime.bin')],check=True)
    actual=(out/'runtime.bin').read_bytes()
    if actual!=original:
        first=next((index for index,(a,b)in enumerate(zip(actual,original))if a!=b),None)
        raise AssertionError(dict(actual_bytes=len(actual),original_bytes=len(original),first_difference=first))
    report=dict(status='terminal_recovered_runtime_source_assembles_byte_exact',directory=str(out),
        instructions=len(rows),bytes=len(original),source=str(source),source_sha256=sha(source),
        linker=str(linker),linker_sha256=sha(linker),runtime_binary=str(out/'runtime.bin'),runtime_binary_sha256=sha(out/'runtime.bin'),
        ELF=str(out/'runtime.elf'),ELF_sha256=sha(out/'runtime.elf'),same_address=True,extra_entry_jump_instructions=0,
        source_authorship='Coordinator instruction-to-mnemonic/label conversion from verified original disassembly; no model-authored code or raw opcode embedding.',
        generator_sha256=sha(Path(__file__)),new_training=False,
        scope='Three compiler-runtime helpers atE540/E588/E60A. Byte identity proves their instruction stream is reproduced from source; not yet a new RNG/game image or whole-game timing proof.')
    text=json.dumps(report,indent=2)+'\n';(out/'report.json').write_text(text);(ROOT/'verification/native-original-runtime-current.json').write_text(text)
    print(report['status'],len(rows),len(actual),flush=True)


if __name__=='__main__':main()

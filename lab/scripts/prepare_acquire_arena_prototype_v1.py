"""Build an uninstalled resource compiler-stack arena prototype and exact stubs."""
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    bp=V/'native-input-callsite-disc-build-v1-current.json';b=read(bp)
    for p,h in b['source_sha256'].items():assert sha(p)==h,p
    src=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/resource-acquire-arena-v1'
    out=V/'acquire-arena-prototype-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    address=0x1f0000
    linker=src/'native.ld'
    assert not linker.exists()
    linker.write_text('SECTIONS { .text NATIVE_ADDRESS : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
    tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    commands=[[tool+'as','-m68000','-o',str(out/'native.o'),str(src/'native-acquire.S')],
        [tool+'ld','--defsym=NATIVE_ADDRESS='+hex(address),'--defsym=GPU_ARENA_BASE='+hex(b['arena_address']),'--defsym=ACQUIRE_BODY='+hex(b['symbols']['biwn_native_resource_acquire_body']),'-T',str(linker),'-o',str(out/'native.elf'),str(out/'native.o')],
        [tool+'objcopy','-O','binary',str(out/'native.elf'),str(out/'native.bin')]]
    for command in commands:subprocess.run(command,check=True,capture_output=True)
    nm=subprocess.run([tool+'nm','-n',str(out/'native.elf')],check=True,capture_output=True,text=True).stdout
    (out/'symbols.txt').write_text(nm);symbols={parts[2]:int(parts[0],16)for line in nm.splitlines()if len(parts:=line.split())==3}
    assert symbols['biwn_acquire_arena_entry']==address
    (out/'disassembly.txt').write_text(subprocess.run([tool+'objdump','-dr',str(out/'native.elf')],check=True,capture_output=True,text=True).stdout)
    resident=bytearray(Path(b['component']).read_bytes());patches=[]
    pairs=[('biwn_native_resource_acquire','biwn_acquire_arena_entry'),('biwn_native_acquire_wait_capture','biwn_acquire_arena_wait'),('biwn_native_acquire_signal_capture','biwn_acquire_arena_signal'),('biwn_native_acquire_allocate_capture','biwn_acquire_arena_allocate'),('biwn_native_acquire_load_capture','biwn_acquire_arena_load')]
    for old,new in pairs:
        at=b['symbols'][old]-b['resident_address'];replacement=bytes.fromhex('4ef9')+symbols[new].to_bytes(4,'big')
        patches.append(dict(entry=b['symbols'][old],old=resident[at:at+6].hex(),new=replacement.hex(),target=symbols[new]));resident[at:at+6]=replacement
    component=out/'resident-arena-prototype.bin';component.write_bytes(resident)
    state=dict(status='terminal_acquire_arena_source_built_UNINSTALLED',pid=os.getpid(),directory=str(out),source_profile=str(src),payload=str(out/'native.bin'),payload_sha256=sha(out/'native.bin'),code_bytes=(out/'native.bin').stat().st_size,code_address=address,fixture_address_not_game_allocation=True,symbols=symbols,component=str(component),component_sha256=sha(component),parent_build=str(bp),stub_patches=patches,existing_GPU_arena_base=b['arena_address'],slot_stride=256,context_offset=168,context_bytes=72,new_RAM_reserved=0,new_disc_built=False,default_promoted=False,stack_bound_proven=False,arena_lifetime_aliases_qualified=False,scheduler_IRQ_qualified=False,new_predictions=0,optimizer_updates=0,scope=__doc__)
    paths=[Path(__file__),bp,src/'native-acquire.S',linker,component,*[p for p in out.iterdir()if p.is_file()]]
    state['source_sha256']={str(p):sha(p)for p in paths};save(out/'protocol.json',state);save(V/'acquire-arena-prototype-v1-current.json',state)
    print({k:state[k]for k in ['status','code_bytes','new_RAM_reserved']},flush=True)


if __name__=='__main__':main()

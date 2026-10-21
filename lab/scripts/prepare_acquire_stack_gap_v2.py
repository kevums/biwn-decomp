"""Assemble a provisional smaller private acquire gap at unchanged addresses.

This is a source-level stack-layout experiment, not a qualified image. Rebuild
the original512 version byte-identically before comparing the448 candidate.
Nested helper/private-state overlap and total task bounds require execution.
"""
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    bp = V/'native-input-callsite-disc-build-v1-current.json'
    b = read(bp)
    for p,h in b['source_sha256'].items():
        assert sha(p) == h,p
    root = ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    original = root/'resource-acquire-shim.S'
    text = original.read_text()
    assert text.count('.equ ACQUIRE_PRIVATE_RESERVE,512') == 1
    profile = root/'resource-acquire-gap-v3'
    profile.mkdir(exist_ok=False)
    source = profile/'resource-acquire-shim.S'
    source.write_text(text.replace('.equ ACQUIRE_PRIVATE_RESERVE,512','.equ ACQUIRE_PRIVATE_RESERVE,448'))
    out = V/'acquire-stack-gap-prototype-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    entry = b['symbols']['biwn_native_resource_acquire']
    end = b['symbols']['biwn_native_resource_load']
    linker = profile/'native.ld'
    linker.write_text('SECTIONS { .text '+hex(entry)+' : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
    tool = str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    def build(src,name):
        obj,elf,blob = (out/(name+suffix)for suffix in ['.o','.elf','.bin'])
        commands = [[tool+'as','-m68000','-o',str(obj),str(src)], [tool+'ld','--defsym=biwn_native_resource_acquire_body='+hex(b['symbols']['biwn_native_resource_acquire_body']),'-T',str(linker),'-o',str(elf),str(obj)], [tool+'objcopy','-O','binary',str(elf),str(blob)]]
        for command in commands:
            subprocess.run(command,check=True,capture_output=True)
        disassembly = subprocess.run([tool+'objdump','-dr',str(elf)],check=True,capture_output=True,text=True).stdout
        (out/(name+'-disassembly.txt')).write_text(disassembly)
        named = subprocess.run([tool+'nm','-n',str(elf)],check=True,capture_output=True,text=True).stdout
        (out/(name+'-symbols.txt')).write_text(named)
        return blob.read_bytes(),{parts[2]:int(parts[0],16)for line in named.splitlines()if len(parts:=line.split())==3}
    old,old_symbols = build(original,'original512')
    candidate,symbols = build(source,'candidate448')
    resident = Path(b['component']).read_bytes()
    at = entry-b['resident_address']
    assert old_symbols['biwn_native_resource_acquire']==symbols['biwn_native_resource_acquire']==entry
    assert len(old) == len(candidate) == end-entry
    assert old == resident[at:at+len(old)], 'Source does not reproduce inherited acquire shim'
    assert {k:v for k,v in old_symbols.items()if k!='ACQUIRE_PRIVATE_RESERVE'} == {k:v for k,v in symbols.items()if k!='ACQUIRE_PRIVATE_RESERVE'}
    changed = [i for i,(x,y)in enumerate(zip(old,candidate))if x!=y]
    assert len(changed)>0
    # Each change must be the immediate word in a LEA displacement. Resolve
    # both complete instructions independently; no executable opcode changes.
    rows=[]
    words=sorted({i&~1 for i in changed})
    allowed=[]
    for offset in words:
        assert offset>=2
        assert old[offset-2:offset] in [bytes.fromhex('4fef'),bytes.fromhex('41ef')]
        assert candidate[offset-2:offset] == old[offset-2:offset]
        left=int.from_bytes(old[offset:offset+2],'big',signed=True)
        right=int.from_bytes(candidate[offset:offset+2],'big',signed=True)
        assert abs(left-right)==64
        allowed.extend([offset,offset+1])
        rows.append(dict(instruction_address=entry+offset-2,operand_address=entry+offset,opcode=old[offset-2:offset].hex(),old_displacement=left,new_displacement=right))
    assert len(rows)==7 and all(i in allowed for i in changed)
    copy = bytearray(resident)
    copy[at:at+len(candidate)] = candidate
    component = out/'resident-gap448-prototype.bin'
    component.write_bytes(copy)
    save(out/'changed-displacements.json',rows)
    state=dict(status='terminal_acquire_gap448_source_prototype_built_UNQUALIFIED',directory=str(out),pid=os.getpid(),source_profile=str(profile),source=str(source),source_authorship='Coordinator assembly stack-layout constant change only',old_reserve=512,new_reserve=448,entry=entry,shim_bytes=len(candidate),changed_displacement_instructions=len(rows),changed_bytes=len(changed),all_function_addresses_identical=True,original512_rebuild_byte_identical=True,component=str(component),component_sha256=sha(component),parent_build=str(bp),new_disc_built=False,task_stack_bound_verified=False,nested_private_state_overlap_verified=False,arbitrary_IRQ_qualified=False,default_promoted=False,new_predictions=0,optimizer_updates=0,scope=__doc__)
    paths=[Path(__file__),bp,original,source,linker,component,*[p for p in out.iterdir()if p.is_file()]]
    state['source_sha256']={str(p):sha(p)for p in paths}
    save(out/'protocol.json',state)
    save(V/'acquire-stack-gap-prototype-v2-current.json',state)
    print({k:state[k]for k in ['status','shim_bytes','changed_displacement_instructions','changed_bytes']},flush=True)


if __name__=='__main__':
    main()

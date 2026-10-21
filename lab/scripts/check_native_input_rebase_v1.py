"""Audit every rebase change against actual ELF32/M68k relocation records."""
import os
import struct
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone


def elf(path):
    raw=Path(path).read_bytes();h=struct.unpack_from('>16sHHIIIIIHHHHHH',raw)
    assert h[0][:7]==b'\x7fELF\x01\x02\x01'and h[1]==2 and h[2]==4
    assert h[11]==40
    sections=[struct.unpack_from('>10I',raw,h[6]+i*40)for i in range(h[12])]
    shstr=sections[h[13]];strings=raw[shstr[4]:shstr[4]+shstr[5]]
    def name(data,at):return data[at:data.index(0,at)].decode()
    section_names=[name(strings,s[0])for s in sections]
    rows=[]
    for sec in sections:
        if sec[1]not in [4,9]:continue
        target=sections[sec[7]]
        if not target[2]&2:continue
        assert sec[1]==4 and sec[9]==12,'Expected explicit RELA addends'
        syms=sections[sec[6]];strs=sections[syms[6]];symnames=raw[strs[4]:strs[4]+strs[5]]
        assert syms[9]==16
        for offset in range(sec[4],sec[4]+sec[5],12):
            address,info,addend=struct.unpack_from('>IIi',raw,offset);symbol=info>>8;kind=info&255
            st=struct.unpack_from('>IIIBBH',raw,syms[4]+symbol*16)
            symbol_name=name(symnames,st[0])if st[0]else(section_names[st[5]]if st[5]<len(sections)else'ABS')
            assert target[3]<=address<target[3]+target[5]
            rows.append(dict(address=address,type=kind,addend=addend,symbol=symbol_name,
                             symbol_value=st[1],symbol_section=st[5],target_section=section_names[sec[7]]))
    return h[4],sorted(rows,key=lambda x:(x['address'],x['type'],x['symbol'],x['addend']))


def main():
    proof_path=V/'native-input-admission-entry-v1-current.json';proof=read(proof_path)
    for path,digest in proof['source_sha256'].items():assert sha(path)==digest,path
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    old=nd/'input-dispatch-native-v4-admission';new=nd/'input-dispatch-native-v5-rebased'
    info=read(new/'rebase-provenance.json')
    for path,digest in info['source_sha256'].items():assert sha(path)==digest,path
    for name in ['native-input.c','input-source.c','physical-call.S','native-entry.S','admission.c','admission-entry.S']:
        assert(old/name).read_bytes()==(new/name).read_bytes(),name
    out=V/'native-input-rebase-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'native-input-rebase-v1-current.json';state=dict(status='linking_old_profile_relocation_audit_only',directory=str(out),pid=os.getpid(),new_predictions=0,optimizer_updates=0,new_disc_built=False)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();cross=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');lib=ROOT/'tools/m68k-elf/m68000-soft/libgcc.a'
    objects=[old/'build-portable'/name for name in ['admission.o','guard.o','adapter.o','dispatch.o','division.o','physical-call.o','entry.o']]
    commands=[[cross+'ld','--gc-sections','--emit-relocs','-T',str(old/'native.ld'),'-o',str(out/'old-with-relocations.elf'),*map(str,objects),str(lib)],
              [cross+'objcopy','-O','binary',str(out/'old-with-relocations.elf'),str(out/'old.bin')]]
    for cmd in commands:subprocess.run(cmd,check=True,capture_output=True)
    old_bytes=(old/'build-portable/native-input.bin').read_bytes();assert(out/'old.bin').read_bytes()==old_bytes
    new_path=new/'build-portable/native-input.bin';new_bytes=new_path.read_bytes()
    assert len(new_bytes)==len(old_bytes)==10580
    old_entry,old_rows=elf(out/'old-with-relocations.elf');new_entry,new_rows=elf(new/'build-portable/native-input.elf')
    old_base=0x1c0000;new_base=0x17c724;delta=new_base-old_base
    assert new_entry-old_entry==delta and len(old_rows)==len(new_rows)
    covered=set();audited=[];changed_relocs=0
    widths={1:4,2:2,3:1,4:4,5:2,6:1}
    for a,b in zip(old_rows,new_rows):
        assert a['type']in widths,a
        assert(a['address']-old_base,a['type'],a['addend'],a['symbol'],a['target_section'])==(b['address']-new_base,b['type'],b['addend'],b['symbol'],b['target_section'])
        internal=old_base<=a['symbol_value']<old_base+len(old_bytes)
        assert b['symbol_value']==a['symbol_value']+(delta if internal else 0),(a,b)
        width=widths[a['type']];at=a['address']-old_base;mask=(1<<(8*width))-1
        def value(row):
            result=row['symbol_value']+row['addend']
            if row['type']in[4,5,6]:result-=row['address']
            return result&mask
        assert int.from_bytes(old_bytes[at:at+width],'big')==value(a),a
        assert int.from_bytes(new_bytes[at:at+width],'big')==value(b),b
        covered.update(range(at,at+width));changed=old_bytes[at:at+width]!=new_bytes[at:at+width];changed_relocs+=changed
        audited.append(dict(offset=at,type=a['type'],symbol=a['symbol'],internal=internal,changed=changed,old_value=value(a),new_value=value(b)))
    changed_bytes=[i for i,(a,b)in enumerate(zip(old_bytes,new_bytes))if a!=b]
    assert changed_bytes and all(i in covered for i in changed_bytes)
    save(out/'relocations.json',audited);save(out/'changed-byte-offsets.json',changed_bytes)
    assert not(new_base<0x1c8000 and new_base+len(new_bytes)>0x1c0000)
    # New address/profile: perform one fresh copied-SDK build, not an old
    # build replay. The source files and relative recipe handle package spaces.
    relative=new.relative_to(ROOT);copied=P/'workbench'/relative;copied.mkdir(parents=True)
    for path in new.iterdir():
        if path.is_file():clone(path,copied/path.name)
    build=P/'workbench/builds/native-input-rebased-v1'/out.name
    build_rel=Path('../../../../../builds/native-input-rebased-v1')/out.name
    assert(copied/build_rel).resolve()==build
    result=subprocess.run(['make','-f','Makefile.portable','BUILD='+str(build_rel)],cwd=copied,capture_output=True,text=True)
    (out/'copied-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    assert(build/'native-input.bin').read_bytes()==new_bytes
    save(out/'commands.json',commands)
    state.update(status='terminal_rebase_ELF_relocations_only_same_runtime_sources_copied_identical',bytes=10580,
        old_base=old_base,new_base=new_base,old_entry=old_entry,new_entry=new_entry,
        relocation_records=len(audited),changed_relocation_records=changed_relocs,changed_byte_count=len(changed_bytes),
        non_relocation_bytes_identical=True,runtime_source_statements_changed=0,
        entry_offset_preserved=True,code_end=new_base+len(new_bytes),stream_staging_no_longer_overlapped=True,
        copied_build=str(build),copied_source=str(copied),copied_build_byte_identical=True,
        planned_address_not_allocated_game_image=True,source_profile=str(new),payload=str(new_path),
        source_sha256={str(path):sha(path)for path in [Path(__file__),proof_path,new_path,new/'build-portable/native-input.elf',
            out/'old-with-relocations.elf',out/'old.bin',out/'relocations.json',out/'changed-byte-offsets.json',out/'copied-build.log',out/'commands.json',
            *objects,*[p for p in new.iterdir()if p.is_file()]]},
        scope='Relinked10580bytesatplannedv34inputaddress17C724. AllruntimeC/assemblysourcesidenticaltov4;everychangedbytebelongs to a checkedELFrelocation. Existingbodyproofsinheritedbyexplicitrelocationaudit,newconnectedexecutionstillrequired. CopiedSDKrebuildidentical. Plannedresidentaddressisnotallocatedorinstalledinanimage;IRQ/arenaheap/provider/freshgatesopen.')
    mark();print(state['status'],len(audited),'relocations;',changed_relocs,'changed;',len(changed_bytes),'bytes',flush=True)


if __name__=='__main__':main()

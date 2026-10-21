"""Experimental formatting disc: explicit larger reservation, no default promotion."""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from extract_biwn_stage import swap16,STAGE_SHA,IMAGE_SHA
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
    bp=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bp.read_text())
    for p,h in bundle['source_sha256'].items():assert sha(p)==h,p
    parentp=ROOT/'verification/native-load-scan-disc-build-current.json';parent=json.loads(parentp.read_text());assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    out=ROOT/'builds/BIWN-native-fast-core-format'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()==STAGE_SHA
    source=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(source)==IMAGE_SHA
    base=bundle['base'];reserve=bundle['reserved_bytes'];staging=bundle['staging'];clear=bundle['staging_clear_bytes'];symbols=bundle['symbols'];heap=bundle['heap_start']
    assert stage[staging-0x4000:staging-0x4000+clear]==bytes(clear)
    payload=Path(bundle['binary']).read_bytes();padded=out/'resident-padded.bin';padded.write_bytes(payload+bytes(reserve-len(payload)))
    entry_source=out/'stage-entry.S';entry_source.write_text(f'''.text
.globl biwn_native_stage_entry
biwn_native_stage_entry:
move.w #0x2700,%sr
movea.l #0x200000,%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea biwn_resident_payload(%pc),%a0
lea {hex(base)},%a1
move.w #{reserve//2-1},%d0
1: move.w (%a0)+,(%a1)+
dbra %d0,1b
jmp {hex(symbols['biwn_native_startup_finalize'])}
.balign 2
biwn_resident_payload:
.incbin "{padded}"
''')
    linker=out/'entry.ld';linker.write_text(f'ENTRY(biwn_native_stage_entry)\nSECTIONS {{ . = {hex(staging)}; .text : {{ *(.text*) }} /DISCARD/ : {{ *(.comment) *(.note*) *(.eh_frame*) }} }}\nASSERT(SIZEOF(.text)<{hex(clear)},"Entry exceeds temporary staging window")\n')
    prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    for command in [[prefix+'as','-m68000','-o',str(out/'entry.o'),str(entry_source)],[prefix+'ld','-T',str(linker),'-o',str(out/'entry.elf'),str(out/'entry.o')],[prefix+'objcopy','-O','binary',str(out/'entry.elf'),str(out/'native-entry.bin')]]:subprocess.run(command,check=True,capture_output=True,text=True)
    entry=(out/'native-entry.bin').read_bytes();assert len(entry)==reserve+40 and len(entry)<clear
    candidate=bytearray(stage);patches=[]
    def patch(address,old,new,reason):
        offset=address-0x4000;assert stage[offset:offset+len(old)]==old,(hex(address),'bad original bytes');assert len(old)==len(new)
        assert candidate[offset:offset+len(old)]==old,(hex(address),'overlapping patch')
        candidate[offset:offset+len(new)]=new;patches.append(dict(address=hex(address),original=old.hex(),replacement=new.hex(),reason=reason))
    oldsymbols=json.loads((Path(parent['directory'])/'symbols.json').read_text());reverse={v:k for k,v in oldsymbols.items()}
    for row in json.loads(Path(parent['patch_manifest']).read_text())['patches']:
        address=int(row['address'],16);old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement'])
        if address==parent['staging_address']:continue
        if address==0x4000:new=b'\x4e\xf9'+staging.to_bytes(4,'big')+b'\x4e\x71'*2
        elif address in [0x1521c,0x1526c]:new=heap.to_bytes(4,'big')
        elif new[:2]==b'\x4e\xf9':
            target=int.from_bytes(new[2:6],'big')
            if base<=target<base+parent['linked_component_bytes']:
                name=reverse[target];assert name in symbols,name;new=new[:2]+symbols[name].to_bytes(4,'big')+new[6:]
        patch(address,old,new,'Inherited native28 contract/repair; redirect relinked where necessary. '+row['reason'])
    patch(staging,bytes(len(entry)),entry,'Larger temporary stage loader/payload; cleared by resident startup before original400A.')
    for address,name in [(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string'),(0xe61c,'biwn_native_unsigned_divide'),(0xe67c,'biwn_native_unsigned_remainder'),(0x1b212,'biwn_native_format_number'),(0x1b29c,'biwn_native_format_core'),(0x1b45a,'biwn_native_format_variadic')]:
        patch(address,stage[address-0x4000:address-0x4000+6],b'\x4e\xf9'+symbols[name].to_bytes(4,'big'),'New complete compiled formatting helper with original external-entry contract.')
    stagefile=out/'mainstage-native-fast-core-format.bin';stagefile.write_bytes(candidate);manifest=out/'stage-patches.json';save(manifest,dict(patches=patches,original_stage_sha256=STAGE_SHA,derived_stage_sha256=sha(stagefile),heap_start=heap,heap_bytes_reserved=reserve))
    offset=mapping['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-fast-core-format-experimental.cdi';shutil.copyfile(source,disc)
    with disc.open('r+b')as stream:
        for row in patches:
            start=offset+int(row['address'],16)-0x4000;old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement']);assert len(old)%2==0 and start%2==0
            stream.seek(start);assert stream.read(len(old))==swap16(old);stream.seek(start);stream.write(swap16(new))
        stream.flush();os.fsync(stream.fileno())
    with disc.open('rb')as stream:stream.seek(offset);assert swap16(stream.read(len(stage)))==candidate
    intervals=sorted((offset+int(p['address'],16)-0x4000,offset+int(p['address'],16)-0x4000+len(bytes.fromhex(p['original'])))for p in patches);pos=0;changed=0
    with source.open('rb')as a,disc.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals),(pos+i,'undeclared CDI change');changed+=1
            pos+=len(left)
    assert pos==source.stat().st_size and sha(source)==IMAGE_SHA
    report=dict(status='terminal_partial_native_format_disc_built_pending_execution',directory=str(out),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),component=str(padded),component_bytes=reserve,linked_component=str(bundle['binary']),linked_component_bytes=len(payload),native_entry_bytes=len(entry),staging_address=staging,staging_bytes_cleared=clear,staging_end=staging+clear,resident_address=base,heap_start=heap,heap_bytes_reserved=reserve,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),changed_CDI_bytes=changed,symbols=symbols,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,parentp,Path(parent['patch_manifest']),entry_source,linker,stagefile,padded,manifest]},original_disc_modified=False,physical_console_verified=False,full_linked_component_gates_revalidated=False,game_frames=0,whole_game_complete=False,default_promoted=False,scope='Experimental derived disc only. Larger16384byte heap reservation and24KBstartup staging clear; source C formatting redirects plus relinked native28 contracts. Startup/callers/fresh game paths and all affected linked components require their own checks. Parent timing/equivalence qualifications remain; no whole-source/physical proof.')
    save(out/'build.json',report);save(ROOT/'verification/native-fast-core-format-disc-build-current.json',report);print(report['status'],len(payload),reserve,changed,flush=True)
if __name__=='__main__':main()

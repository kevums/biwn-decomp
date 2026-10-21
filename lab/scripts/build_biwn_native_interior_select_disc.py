"""Link the accepted local actor/sprite selector into the bounded resident layout."""
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from check_biwn_native_button_digit import ROOT, sha, save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';parentp=v/'native-doorway-disc-build-current.json';parent=read(parentp)
    selectedp=v/'native-interior-select-selected-current.json';selected=read(selectedp)
    assert selected['status']=='terminal_local_interior_kernel_component_reviewed'
    gp=Path(selected['component_proof']);gate=read(gp)
    assert sha(gp)==selected['component_proof_sha256'] and gate['source_accepted']
    assert gate['stable_cases']==1958 and gate['changing_cases']==768
    source=Path(selected['source']);assert sha(source)==gate['source_sha256']==selected['source_sha256']
    for p,h in gate['dependencies_sha256'].items():assert sha(p)==h,p
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    assert sha(parent['derived_stage'])==parent['derived_stage_sha256']
    out=ROOT/'builds/BIWN-native-interior-select'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    shutil.copy2(parentp,out/'parent-build.json');shutil.copy2(selectedp,out/'selected-kernel.json')
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    state=dict(status='linking_local_interior_selector',pid=os.getpid(),directory=str(out),
               parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),
               selection=str(out/'selected-kernel.json'),selection_sha256=sha(out/'selected-kernel.json'),
               source=str(source),source_sha256=sha(source),new_training=False,default_promoted=False,
               physical_console_verified=False,whole_game_complete=False,game_frames=0)
    def mark():
        save(out/'protocol.json',state);save(v/'native-interior-select-disc-build-active.json',state)
    mark()
    try:
        old=Path(parent['linked_component']).read_bytes()
        assert len(old)==parent['linked_component_bytes']
        address=(parent['resident_address']+len(old)+3)&~3
        alignment=address-parent['resident_address']-len(old)
        assert alignment in [0,2] and address>=0x160000
        command=[sys.executable,str(ROOT/'scripts/check_biwn_native_interior_select_v2.py'),
                 '--source',str(source),'--address',hex(address),'--parent-build',str(out/'parent-build.json'),'--no-publish']
        state.update(status='checking_final_address',final_gate_command=command);mark()
        with(out/'final-gate.log').open('w')as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=480)
        linkedgate=read(v/'native-interior-select-active.json')
        assert result.returncode==0,(out/'final-gate.log').read_text()[-3000:]
        assert linkedgate['source']==str(source) and linkedgate['code_address']==address and linkedgate['source_accepted']
        finalproof=Path(linkedgate['directory'])/'protocol.json'
        code=Path(linkedgate['binary']).read_bytes();standalone=Path(gate['binary']).read_bytes()
        assert len(code)==len(standalone)
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        elf=Path(linkedgate['directory'])/'build/interior-select.elf'
        assert not subprocess.check_output([prefix+'nm','-u',str(elf)],text=True).strip()
        sections=subprocess.check_output([prefix+'size','-A',str(elf)],text=True)
        (out/'sections.txt').write_text(sections)
        for line in sections.splitlines():
            fields=line.split()
            if len(fields)==3 and fields[0] in ['.data','.bss','.rodata']:
                assert int(fields[1])==0,'Undeclared non-code section: '+line
        relocations=subprocess.check_output([prefix+'objdump','-r',str(Path(linkedgate['directory'])/'build/shim.o')],text=True)
        (out/'relocations.txt').write_text(relocations)
        normalized=bytearray(code);changes=[]
        for line in relocations.splitlines():
            fields=line.split()
            if len(fields)==3 and fields[1]=='R_68K_32':
                at=int(fields[0],16);assert fields[2]=='biwn_interior_select_kernel'
                before=int.from_bytes(standalone[at:at+4],'big');after=int.from_bytes(code[at:at+4],'big')
                assert after==before+address-0x180000
                normalized[at:at+4]=standalone[at:at+4]
                changes.append(dict(offset=at,before=before,after=after,symbol=fields[2]))
        assert len(changes)==1 and bytes(normalized)==standalone
        pad=b'\x4e\x71'*(alignment//2);linked=out/'resident-linked.bin'
        linked.write_bytes(old+pad+code);reserve=parent['component_bytes']
        assert linked.stat().st_size<=reserve and parent['resident_address']+reserve==parent['heap_start']
        padded=out/'resident-padded.bin';padded.write_bytes(linked.read_bytes()+bytes(reserve-linked.stat().st_size))
        assert padded.read_bytes()[:len(old)]==old
        symbols=linkedgate['symbols'];stage=bytearray(Path(parent['derived_stage']).read_bytes());patches=[]
        def patch(at,before,after,reason):
            index=at-0x4000;assert len(before)==len(after) and stage[index:index+len(before)]==before
            stage[index:index+len(before)]=after
            patches.append(dict(address=hex(at),original=before.hex(),replacement=after.hex(),reason=reason))
        patch(parent['staging_address']+40+len(old),bytes(alignment+len(code)),pad+code,
              'Append shared actor/sprite selector and declared NOP alignment inside the existing reserve.')
        baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
        for entry,name in [(0x10520,'biwn_native_interior_actor_select'),(0x105da,'biwn_native_interior_sprite_select')]:
            patch(entry,baseline[entry:entry+8],b'\x4e\xf9'+symbols[name].to_bytes(4,'big')+b'\x4e\x71',
                  'Redirect complete original entry to the accepted C kernel and native ABI shim.')
        stagefile=out/'mainstage-native-interior-select.bin';stagefile.write_bytes(stage)
        from check_biwn_scheduler import Native
        session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
        original=bytearray(0x200000);original[0x4000:0x100000]=(session/'nextstage-68000-candidate.bin').read_bytes()
        installed=bytearray(original);installed[0x4000:0x100000]=stage
        n=Native();rng=random.Random(0x10520);entryrows=[]
        def entry(image,regs,sr,new):
            lib=n.lib;n.device.seed(bytes(image),0);lib.m68k_pulse_reset();lib.m68k_set_irq(0);lib.m68k_set_reg(17,sr)
            for i,value in enumerate(regs):lib.m68k_set_reg(i,value)
            lib.m68k_set_reg(16,0x4000)
            for _ in range(100000):
                pc=lib.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert pc in [0x4000,0x4004]or(new and(parent['staging_address']<=pc<parent['staging_address']+parent['native_entry_bytes']or parent['resident_address']<=pc<parent['resident_address']+reserve))
                lib.m68k_execute(1)
            else:raise AssertionError('Startup did not resume400A')
            return [lib.m68k_get_reg(None,i)for i in range(18)],n.device.ram()
        state['status']='checking_stage_loader';mark()
        try:
            for variant in range(3):
                for ccr in range(32):
                    regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=0x180000
                    a,_=entry(original,regs,0x2000|ccr,False);b,ram=entry(installed,regs,0x2000|ccr,True);assert a==b
                    expected=bytearray(installed);expected[parent['resident_address']:parent['resident_address']+reserve]=padded.read_bytes()
                    expected[parent['staging_address']:parent['staging_address']+parent['staging_bytes_cleared']]=bytes(parent['staging_bytes_cleared'])
                    assert ram[:0x1fffc4]==expected[:0x1fffc4]
                    entryrows.append(dict(variant=variant,CCR=ccr,CPU=b,payload_and_staging_RAM_match=True))
        finally:n.close()
        save(out/'entry-cases.json',entryrows)
        mapping=read(session/'nextstage-mapping.json');offset=mapping['payload_raw_cdi_offset']
        disc=out/'BIWN-23-native-interior-select-experimental.cdi';shutil.copyfile(parent['derived_disc'],disc)
        from extract_biwn_stage import swap16
        with disc.open('r+b')as stream:
            for row in patches:
                at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement'])
                stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after))
            stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
        intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in patches]
        position=0;changed=0
        with Path(parent['derived_disc']).open('rb')as left,disc.open('rb')as right:
            while True:
                a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                if not a:break
                if a!=b:
                    for i,(x,y)in enumerate(zip(a,b)):
                        if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changed+=1
                position+=len(a)
        assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
        manifest=out/'stage-patches.json';prior=read(parent['patch_manifest'])
        save(manifest,dict(patches=prior['patches']+patches,delta_patches=patches,parent=str(out/'parent-build.json'),parent_sha256=sha(out/'parent-build.json')))
        sources=[Path(__file__),source,nd/'interior-select-native.h',nd/'interior-select-shim.S',nd/'Makefile.interior-select',
                 ROOT/'scripts/check_biwn_native_interior_select_v2.py',finalproof,out/'selected-kernel.json',out/'parent-build.json']
        inherited={k:value for k,value in parent.items()if k.endswith(('_entry','_return','_start','_end'))or k in ['frame_acquire_payload_start','components','resource_table_initialize_entry','resource_table_initialize_return','heap_bytes_reserved','staging_address','staging_bytes_cleared','native_entry_bytes']}
        state.update(inherited)
        state.update(status='terminal_native_interior_select_disc_built_entry_verified_pending_gameplay',
                     derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),
                     linked_component=str(linked),linked_component_bytes=linked.stat().st_size,component=str(padded),component_bytes=reserve,
                     resident_address=parent['resident_address'],heap_start=parent['heap_start'],
                     interior_actor_entry=symbols['biwn_native_interior_actor_select'],interior_sprite_entry=symbols['biwn_native_interior_sprite_select'],
                     interior_select_return=symbols['biwn_native_interior_select_return'],interior_select_start=address,interior_select_end=address+len(code),
                     symbols={**parent['symbols'],**symbols},relocations=changes,component_gate=str(finalproof),component_gate_sha256=sha(finalproof),
                     linked_native_cases=1958,linked_changing_cases=768,linker_alignment_bytes=alignment,semantic_code_bytes=len(code),
                     appended_bytes=alignment+len(code),parent_resident_prefix_byte_identical=True,entry_cases=len(entryrows),
                     delta_CDI_changed_bytes=changed,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),
                     source_sha256={str(p):sha(p)for p in sources},original_disc_modified=False,
                     scope='Complete already-recovered10520/105DA selectors compiled from accepted unchanged local output using coordinator ABI/contract/verifier. Local output uses volatile scalar-width helpers rather than the requested struct fields. Shared kernel once, two entry shims; unchanged parent prefix/reserve/heap. Full final-address1958stable+768changing CPU/publicRAM/ordered cases and96startup. No new logical-function count, training gain, cycle/physical/full-game or gameplay proof.')
        mark();save(v/'native-interior-select-disc-build-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','linked_component_bytes','appended_bytes','entry_cases','delta_CDI_changed_bytes']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__=='__main__':main()

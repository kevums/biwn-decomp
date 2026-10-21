"""Append checked native1AE56 C inside existing reservation; isolated derived CDI."""
import json,os,random,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from check_biwn_native_button_digit import ROOT,sha,save
import check_biwn_native_frame_reference_single as gate

def main():
    parent_path=ROOT/'verification/native-fast-core-wait-format-disc-build-current.json';parent=json.loads(parent_path.read_text())
    proof_path=ROOT/'verification/native-frame-reference-single-current.json';proof=json.loads(proof_path.read_text())
    assert proof['status']=='terminal_native_frame_reference_single_CPU_RAM_ordered_pass'and proof['source_accepted']
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256']and sha(parent['derived_stage'])==parent['derived_stage_sha256']
    for path,digest in proof['artifacts_sha256'].items():assert sha(path)==digest
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';out=ROOT/'builds/BIWN-native-frame-single'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building_isolated_frame_single',pid=os.getpid(),directory=str(out),parent_build=str(parent_path),parent_build_sha256=sha(parent_path),component_gate=str(proof_path),component_gate_sha256=sha(proof_path),game_frames=0,physical_console_verified=False,whole_game_complete=False,default_promoted=False,new_training=False)
    def mark():save(out/'build.json',state);save(ROOT/'verification/native-frame-single-disc-build-active.json',state)
    mark()
    try:
        sources=[Path(__file__),Path(gate.__file__),*[nd/name for name in ['frame-reference-single-native.c','frame-reference-single-native.h','frame-reference-single-shim.S']]];snapshots=out/'source-snapshot';snapshots.mkdir()
        for p in sources:shutil.copy2(p,snapshots/p.name)
        old=Path(parent['linked_component']).read_bytes();assert len(old)==parent['linked_component_bytes'];address=parent['resident_address']+len(old);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        commands=[[prefix+'gcc','-m68000','-msoft-float','-std=c99','-Os','-ffreestanding','-fno-pie','-fno-common','-Wall','-Wextra','-Werror','-I'+str(nd),'-c',str(nd/'frame-reference-single-native.c'),'-o',str(out/'body.o')],
           [prefix+'as','-m68000','-o',str(out/'shim.o'),str(nd/'frame-reference-single-shim.S')],
           [prefix+'ld','-Ttext='+hex(address),'-e','biwn_native_frame_reference_single','-o',str(out/'frame-single.elf'),str(out/'shim.o'),str(out/'body.o')],
           [prefix+'objcopy','-O','binary',str(out/'frame-single.elf'),str(out/'frame-single.bin')]]
        with(out/'build.log').open('w')as log:
            for command in commands:assert subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode==0,command
        code=(out/'frame-single.bin').read_bytes();standalone=Path(proof['compiled_binary']).read_bytes()
        nm=subprocess.check_output([prefix+'nm','-n',str(out/'frame-single.elf')],text=True)
        symbols={parts[2]:int(parts[0],16)for line in nm.splitlines()if len(parts:=line.split())==3 and parts[1].upper()in ['T','A']}
        function_entry=symbols['biwn_native_frame_reference_single'];alignment=function_entry-address
        assert alignment in [0,2]and code==bytes.fromhex('4e71')*(alignment//2)+standalone,'Only explicit linker alignment padding may differ; semantic bytes must match'
        linked=out/'resident-linked.bin';linked.write_bytes(old+code);reserve=parent['component_bytes'];assert len(old)+len(code)<=reserve
        padded=out/'resident-padded.bin';padded.write_bytes(old+code+bytes(reserve-len(old)-len(code)));assert padded.read_bytes()[:len(old)]==old
        (out/'frame-single-disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(out/'frame-single.elf')],text=True))
        # Execute the exact linked code at its final address, retaining old payload bytes.
        gate.BASE=address;baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();common=bytearray(baseline);common[parent['resident_address']:parent['resident_address']+reserve]=padded.read_bytes();candidate=bytearray(common);candidate[gate.ENTRY:gate.ENTRY+6]=b'\x4e\xf9'+function_entry.to_bytes(4,'big')
        n=gate.Native();cases=gate.vectors();coverage=set();rows=[];traces=0;state['status']='checking_final_link_address';mark()
        try:
            for i,case in enumerate(cases):
                a=gate.native(n,common,case,len(code),True);b=gate.native(n,candidate,case,len(code),False)
                assert a[1]==b[1]and gate.normalize(b[0],a[0],len(code))==a[0],('linked CPU/RAM',i)
                x=gate.trace(common,case,len(code),True);y=gate.trace(candidate,case,len(code),False)
                assert x[1]==y[1]and gate.normalize(y[0],x[0],len(code))==x[0],('linked ordered access',i)
                coverage.update(a[2]);traces+=1;rows.append(dict(case=i,CPU=b[1],ordered_events=len(x[1])))
                if i%128==0:state['linked_cases_completed']=len(rows);mark();print('Linked frame release',len(rows),'/',len(cases),flush=True)
            for sr in [0,16,0x2000,0x201f]:
                case=dict(mode=0,wanted=0,count=1,pattern='all',incoming=[0x80000000]*15,sr=sr,changing=True)
                x=gate.trace(common,case,len(code),True);y=gate.trace(candidate,case,len(code),False);assert x[1]==y[1]and gate.normalize(y[0],x[0],len(code))==x[0]
                left=gate.native(n,common,dict(case,_external_changes=x[2]),len(code),True);right=gate.native(n,candidate,dict(case,_external_changes=y[2]),len(code),False);assert left[1]==right[1]and gate.normalize(right[0],left[0],len(code))==left[0];traces+=1
        finally:n.close()
        save(out/'final-address-cases.json',rows);save(out/'final-address-fixtures.json',cases)
        state.update(linked_native_cases=len(rows),linked_trace_cases=traces,linked_original_instruction_addresses=sorted(coverage));mark()
        stage=bytearray(Path(parent['derived_stage']).read_bytes());patches=[]
        def patch(at,before,after,reason):
            offset=at-0x4000;assert len(before)==len(after)and stage[offset:offset+len(before)]==before;stage[offset:offset+len(before)]=after;patches.append(dict(address=hex(at),original=before.hex(),replacement=after.hex(),reason=reason))
        patch(parent['staging_address']+40+len(old),bytes(len(code)),code,'Append compiled frame-reference release in existing zero padding; prior14690resident bytes unchanged.')
        patch(gate.ENTRY,baseline[gate.ENTRY:gate.ENTRY+6],b'\x4e\xf9'+function_entry.to_bytes(4,'big'),'Redirect original1AE56entry to complete nativeC/ABI routine at its actual aligned symbol.')
        stagefile=out/'mainstage-native-frame-single.bin';stagefile.write_bytes(stage)
        # Verify the unchanged loader actually copies all new bytes, clears staging,
        # preserves entry registers/SR and returns to400A. No unrelated component reruns.
        from check_biwn_scheduler import Native
        original=bytearray(0x200000);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);original[0x4000:0x100000]=(session/'nextstage-68000-candidate.bin').read_bytes();installed=bytearray(original);installed[0x4000:0x100000]=stage
        n=Native();rng=random.Random(0x1ae56);entry_rows=[]
        def entry(image,regs,sr,new):
            l=n.lib;n.device.seed(bytes(image),0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,sr)
            for i,v in enumerate(regs):l.m68k_set_reg(i,v)
            l.m68k_set_reg(16,0x4000)
            for steps in range(100000):
                pc=l.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert pc in [0x4000,0x4004]or(new and(parent['staging_address']<=pc<parent['staging_address']+parent['native_entry_bytes']or parent['resident_address']<=pc<parent['resident_address']+reserve));l.m68k_execute(1)
            else:raise AssertionError('Entry did not resume400A')
            return [l.m68k_get_reg(None,i)for i in range(18)],n.device.ram()
        state['status']='checking_stage_loader';mark()
        try:
            for variant in range(3):
                for ccr in range(32):
                    regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=0x180000;a,_=entry(original,regs,0x2000|ccr,False);b,ram=entry(installed,regs,0x2000|ccr,True);assert a==b
                    expected=bytearray(installed);expected[parent['resident_address']:parent['resident_address']+reserve]=padded.read_bytes();expected[parent['staging_address']:parent['staging_address']+parent['staging_bytes_cleared']]=bytes(parent['staging_bytes_cleared'])
                    assert ram[:0x1fffc4]==expected[:0x1fffc4];assert ram[parent['resident_address']:parent['resident_address']+len(old)]==old
                    entry_rows.append(dict(variant=variant,CCR=ccr,CPU=b,payload_and_staging_RAM_match=True))
        finally:n.close()
        save(out/'entry-cases.json',entry_rows)
        mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-frame-single-experimental.cdi';shutil.copyfile(parent['derived_disc'],disc)
        from extract_biwn_stage import swap16
        with disc.open('r+b')as stream:
            for row in patches:
                at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement']);stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after))
            stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
        intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in patches];position=0;changes=0
        with Path(parent['derived_disc']).open('rb')as left,disc.open('rb')as right:
            while True:
                a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                if not a:break
                if a!=b:
                    for i,(x,y)in enumerate(zip(a,b)):
                        if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changes+=1
                position+=len(a)
        assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
        manifest=out/'stage-patches.json';prior=json.loads(Path(parent['patch_manifest']).read_text());save(manifest,dict(patches=prior['patches']+patches,delta_patches=patches,parent=str(parent_path),parent_sha256=sha(parent_path)))
        state.update(status='terminal_native_frame_single_disc_built_entry_verified_pending_gameplay',derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=linked.stat().st_size,component=str(padded),component_bytes=reserve,resident_address=parent['resident_address'],frame_single_entry=function_entry,payload_start=address,linker_alignment_bytes=alignment,semantic_code_bytes=len(standalone),appended_bytes=len(code),parent_resident_prefix_byte_identical=True,heap_start=parent['heap_start'],heap_bytes_reserved=parent['heap_bytes_reserved'],entry_cases=len(entry_rows),delta_CDI_changed_bytes=changes,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),source_sha256={str(p):sha(p)for p in sources},original_disc_modified=False,
          scope='One already-recovered routine1AE56 now compiled for native68000,The complete native C/ABI bytes plus explicit linker alignment after unchanged14690byte repaired parent; same16384reservation/heap/staging.Final-address CPU/RAM and ordered comparisons across the complete frozen fixture set and96stage-entry cases. No new logical-function count, local-model authorship, training gain, whole-game build, physical boot, gameplay or cycle-equivalence claim. Existing long route remains on its original parent. New disc needs independent gameplay checks.')
        mark();save(ROOT/'verification/native-frame-single-disc-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','linked_component_bytes','appended_bytes','entry_cases','delta_CDI_changed_bytes']}),flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()

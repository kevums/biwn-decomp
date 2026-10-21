"""Isolated 1AC68 disc: exact final-address gates, unchanged16KB reserve, entry/heap tests."""
import json,os,random,re,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_frame_acquire_lean as g
from extract_biwn_stage import swap16,IMAGE_SHA
ROOT=g.ROOT;sha=g.sha;save=g.save

def main():
    parentp=ROOT/'verification/native-fast-core-wait-format-disc-build-current.json';parent=json.loads(parentp.read_text())
    proofp=ROOT/'verification/native-frame-acquire-lean-current.json';proof=json.loads(proofp.read_text());nestedp=ROOT/'verification/native-frame-acquire-lean-nested-current.json';nested=json.loads(nestedp.read_text())
    assert proof['source_accepted'] and nested['source_accepted']
    for p,h in proof['dependencies_sha256'].items():assert sha(p)==h
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256'] and sha(parent['derived_stage'])==parent['derived_stage_sha256']
    out=ROOT/'builds/BIWN-native-frame-acquire-lean'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building_isolated_frame_acquire',pid=os.getpid(),directory=str(out),parent_build=str(parentp),parent_build_sha256=sha(parentp),component_gate=str(proofp),component_gate_sha256=sha(proofp),nested_gate=str(nestedp),nested_gate_sha256=sha(nestedp),game_frames=0,physical_console_verified=False,whole_game_complete=False,default_promoted=False,new_training=False)
    def mark():save(out/'build.json',state);save(ROOT/'verification/native-frame-acquire-lean-disc-build-active.json',state)
    mark();n=None
    try:
        paths=[Path(__file__),Path(g.__file__),*[g.ND/x for x in ['frame-acquire-lean.c','frame-acquire-lean.h','frame-acquire-lean-shim.S']]];snap=out/'source-snapshot';snap.mkdir()
        for p in paths:shutil.copy2(p,snap/p.name)
        old=Path(parent['linked_component']).read_bytes();oldstage=Path(parent['derived_stage']).read_bytes();base=parent['resident_address'];staging=parent['staging_address'];clear=parent['staging_bytes_cleared'];reserve=parent['component_bytes'];heap=base+reserve;address=base+len(old);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        assert oldstage[staging-0x4000+40:staging-0x4000+40+len(old)]==old
        commands=[[prefix+'gcc','-m68000','-msoft-float','-std=c99','-Os','-ffreestanding','-fno-pie','-fno-common','-Wall','-Wextra','-Werror','-I'+str(g.ND),'-c',str(g.ND/'frame-acquire-lean.c'),'-o',str(out/'body.o')],[prefix+'as','-m68000','-o',str(out/'shim.o'),str(g.ND/'frame-acquire-lean-shim.S')],[prefix+'ld','-Ttext='+hex(address),'-e','biwn_native_frame_acquire','-o',str(out/'frame-acquire.elf'),str(out/'shim.o'),str(out/'body.o')],[prefix+'objcopy','-O','binary',str(out/'frame-acquire.elf'),str(out/'frame-acquire.bin')]]
        with (out/'build.log').open('w') as log:
            for cmd in commands:assert subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode==0,cmd
        code=(out/'frame-acquire.bin').read_bytes();symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(out/'frame-acquire.elf')],text=True).splitlines():
            q=line.split()
            if len(q)==3:symbols[q[2]]=int(q[0],16)
        entry=symbols['biwn_native_frame_acquire'];alignment=entry-address;assert alignment in [0,2]
        assert len(code)==alignment+proof['binary_bytes'] and code[:alignment]==b'\x4e\x71'*(alignment//2)
        # C emits absolute references to outlined local flag helpers. Those
        # legitimately relocate; exact input objects, final-address execution
        # and all linked symbol addresses are checked instead of byte identity.
        for name in ['body.o','shim.o']:assert (out/name).read_bytes()==(Path(proof['binary']).parent/name).read_bytes(),'Changed compiler input object'
        baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert sha(ROOT/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        resident=bytearray(old);resident.extend(code);assert len(resident)<reserve
        assert resident[:len(old)]==old and heap==parent['heap_start']
        linked=out/'resident-linked.bin';linked.write_bytes(resident);padded=out/'resident-padded.bin';padded.write_bytes(resident+bytes(reserve-len(resident)))
        (out/'compiled.asm').write_text(subprocess.check_output([prefix+'objdump','-dr',str(out/'frame-acquire.elf')],text=True));save(out/'frame-symbols.json',symbols)
        state.update(status='checking_final_address',resident_address=base,component_bytes=reserve,heap_start=heap,heap_bytes_reserved=reserve,linked_component=str(linked),linked_component_bytes=len(resident),frame_acquire_entry=entry,payload_start=address,linker_alignment_bytes=alignment,semantic_code_bytes=proof['binary_bytes']);mark()
        # Re-run the complete standalone matrix at final addresses, with fixture
        # loader; production-loader nesting has its own independently bound gate.
        g.BASE=address;image,cases,zeros=g.vectors();fixture_helper=Path(proof['directory'])/'fixture-loader.bin';helper=fixture_helper.read_bytes();common=bytearray(image);common[base:base+reserve]=padded.read_bytes();common[g.PROVIDER:g.PROVIDER+len(helper)]=helper;common[g.LOADER:g.LOADER+6]=b'\x4e\xf9'+g.PROVIDER.to_bytes(4,'big');candidate=bytearray(common);candidate[g.ENTRY:g.ENTRY+8]=b'\x4e\xf9'+entry.to_bytes(4,'big')+b'\x4e\x71'
        # The reference shares all resident bytes but calls the original routine.
        n=g.Native();normal=[];fault_rows=[]
        for i,c in enumerate(cases):
            x=g.trace(common,c,len(code),len(helper),True);y=g.trace(candidate,c,len(code),len(helper),False)
            assert x[1]==y[1] and g.normalize(y[0],x[0],len(code))==x[0],('Linked ordered',i)
            a=g.run(n,common,c,len(code),len(helper),True,x[2]);b=g.run(n,candidate,c,len(code),len(helper),False,y[2]);g.compare(out,i,c,a,b,len(code),symbols);normal.append(dict(case=i,CPU=b['cpu'],calls=len(b['calls'])))
            if i%128==0:state['linked_normal_cases']=len(normal);mark();print('Final-address frame acquire',len(normal),'/',len(cases),flush=True)
        read_pcs=[int(m.group(1),16) for m in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\bmovew (?:0x)?15b532\b',(out/'compiled.asm').read_text(),re.M)];assert len(read_pcs)==3
        for i,c in enumerate(zeros):
            a=g.run(n,common,c,len(code),len(helper),True);b=g.run_zero(n,candidate,c,len(code),len(helper),read_pcs);g.compare(out,i,c,a,b,len(code),symbols);fault_rows.append(dict(case=i,CPU=b['cpu'],faults=len(b['faults'])))
        n.close();n=None;save(out/'linked-normal-results.json',normal);save(out/'linked-zero-results.json',fault_rows)
        # Existing copy count/reservation are unchanged; startup must copy the appended bytes.
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
jmp {hex(parent['symbols']['biwn_native_startup_finalize'])}
.balign 2
biwn_resident_payload:
.incbin "{padded}"
''')
        with (out/'entry-build.log').open('w') as log:
            for cmd in [[prefix+'as','-m68000','-o',str(out/'entry.o'),str(entry_source)],[prefix+'ld','-Ttext='+hex(staging),'-e','biwn_native_stage_entry','-o',str(out/'entry.elf'),str(out/'entry.o')],[prefix+'objcopy','-O','binary',str(out/'entry.elf'),str(out/'native-entry.bin')]]:assert subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode==0
        startup=(out/'native-entry.bin').read_bytes();assert len(startup)==reserve+40 and len(startup)<clear
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);source_stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert source_stage[staging-0x4000:staging-0x4000+clear]==bytes(clear)
        stage=bytearray(oldstage);patches=[]
        def patch(at,before,after,reason):
            k=at-0x4000;assert len(before)==len(after) and stage[k:k+len(before)]==before,(hex(at),'Unexpected before bytes');stage[k:k+len(after)]=after;patches.append(dict(address=hex(at),original=before.hex(),replacement=after.hex(),reason=reason))
        patch(staging,oldstage[staging-0x4000:staging-0x4000+len(startup)],startup,'Copy the new resident payload using the unchanged16KB reservation and24KB staging; all prior resident bytes and heap floor remain identical.')
        patch(g.ENTRY,baseline[g.ENTRY:g.ENTRY+6],b'\x4e\xf9'+entry.to_bytes(4,'big'),'Redirect complete original1AC68 entry to checked native C routine.')
        stagefile=out/'mainstage-native-frame-acquire-lean.bin';stagefile.write_bytes(stage)
        # Stage entry: all original registers/SR and persistent RAM, 96 cases.
        original=bytearray(0x200000);original[0x4000:0x100000]=source_stage;installed=bytearray(original);installed[0x4000:0x100000]=stage;n=g.Native();rng=random.Random(0x1ac684000);entries=[]
        def enter(image,regs,sr,new):
            n.device.seed(bytes(image),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,sr)
            for i,v in enumerate(regs):l.m68k_set_reg(i,v)
            l.m68k_set_reg(16,0x4000)
            for step in range(100000):
                pc=l.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert pc in [0x4000,0x4004] or new and (staging<=pc<staging+len(startup) or base<=pc<base+reserve),hex(pc);l.m68k_execute(1)
            else:raise AssertionError('Stage entry limit')
            return g.cpu(n),n.device.ram()
        state['status']='checking_entry_and_heap';mark()
        for variant in range(3):
            for flags in range(32):
                regs=[rng.getrandbits(32) for _ in range(16)];regs[15]=0x180000;a,_=enter(original,regs,0x2000|flags,False);b,ram=enter(installed,regs,0x2000|flags,True);assert a==b
                expected=bytearray(installed);expected[base:base+reserve]=padded.read_bytes();expected[staging:staging+clear]=bytes(clear);assert ram[:0x1fffc4]==expected[:0x1fffc4];entries.append(dict(variant=variant,CCR=flags,CPU=b))
        save(out/'entry-cases.json',entries)
        def memory_call(image,at,args):
            n.device.seed(bytes(image),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2700)
            for i in range(16):l.m68k_set_reg(i,0)
            sp=0x1e0000;stop=0x1f0000;l.m68k_set_reg(15,sp);l.m68k_set_reg(16,at);n.device.direct(sp,4,stop)
            for i,v in enumerate(args):n.device.direct(sp+4+4*i,4,v)
            for steps in range(2000000):
                pc=l.m68k_get_reg(None,16)
                if pc==stop:break
                assert 0x15200<=pc<0x155c2 or pc in [0xe3e0,0xe3ee] or base<=pc<base+len(resident),hex(pc);l.m68k_execute(1)
            else:raise AssertionError('Heap call limit')
            result=n.device.ram();assert result[base:base+reserve]==padded.read_bytes(),'Heap overwrote resident code'
            return result,l.m68k_get_reg(None,0),steps
        initialized,_,steps=memory_call(ram,0x1557a,[]);u=lambda mem,a:int.from_bytes(mem[a:a+4],'big')
        assert u(initialized,0x112d60)==heap and u(initialized,heap)==0x1c0000-heap and u(initialized,0x112d64)==0x1c0000-heap and initialized[0x112960:0x112d60]==bytes(1024)
        allocated,h1,_=memory_call(initialized,0x152a2,[137]);allocated,h2,_=memory_call(allocated,0x152a2,[260]);compacted,_,_=memory_call(allocated,0x15200,[])
        assert h1 and h2 and all(u(compacted,h)>=heap+8 for h in [h1,h2]);(out/'installed-and-heap-initialized-RAM.bin').write_bytes(initialized);n.close();n=None
        # Publish only a derived copy after final-address/startup/heap checks.
        state['status']='writing_derived_disc';mark();mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-frame-acquire-lean-experimental.cdi';shutil.copyfile(parent['derived_disc'],disc)
        with disc.open('r+b') as stream:
            for row in patches:
                at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement']);stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after))
            stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
        intervals=[(offset+int(p['address'],16)-0x4000,offset+int(p['address'],16)-0x4000+len(bytes.fromhex(p['original']))) for p in patches];pos=0;changes=0
        with Path(parent['derived_disc']).open('rb') as a,disc.open('rb') as b:
            while True:
                left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
                if not left:break
                if left!=right:
                    for i,(x,y) in enumerate(zip(left,right)):
                        if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changes+=1
                pos+=len(left)
        assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
        manifest=out/'stage-patches.json';prior=json.loads(Path(parent['patch_manifest']).read_text());save(manifest,dict(patches=prior['patches']+patches,delta_patches=patches,parent=str(parentp),parent_sha256=sha(parentp)))
        merged=dict(parent['symbols']);merged.update(symbols);merged['biwn_native_heap_start']=heap
        state.update(status='terminal_native_frame_acquire_disc_built_entry_heap_verified_pending_gameplay',derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),component=str(padded),linked_native_cases=len(normal),linked_zero_cases=len(fault_rows),entry_cases=len(entries),heap_initialize_instructions=steps,heap_allocation_compaction_witness=True,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=len(startup),patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),symbols=merged,parent_resident_prefix_byte_identical=True,changed_parent_heap_initializer_bytes=0,delta_CDI_changed_bytes=changes,source_sha256={str(p):sha(p) for p in paths},original_disc_modified=False,scope='Experimental partial native game disc. Complete lean frame acquisition appended after byte-identical parent14690resident bytes in existing16KB reservation/same24KBstaging. Heap floor unchanged.631normal/192zero final-address native checks,96full entry cases,heap init/137+260byte allocations/compaction preserve all resident bytes. Prior parent heap regressions remain applicable because all old bytes/floor are identical;no redundant full rerun claimed. Production nested-loader gate separately bound at standalone address. No gameplay/IRQ/timing/physical/whole-source proof or preview/default promotion.');mark();save(ROOT/'verification/native-frame-acquire-lean-disc-build-current.json',state);print(state['status'],len(resident),reserve,len(entries),changes,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()

if __name__=='__main__':main()

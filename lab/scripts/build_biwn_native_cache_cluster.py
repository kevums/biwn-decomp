"""Compose complete cache lookup/acquire/release/init ports in a20KB resident.
Keep as-run sources/old discs immutable; verify final addresses and raised heap.
"""
import json,os,random,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_native_frame_lookup_v2 as lookup
import check_biwn_native_frame_reference_single_lean as single
import check_biwn_native_frame_reference_release as multi
import check_biwn_native_frame_acquire_lean as acquire
import check_biwn_native_resource_table_initialize as table
import check_biwn_native_fast_core_format_bundle_heap as heap_gate
from extract_biwn_stage import swap16
ROOT=lookup.ROOT;ND=lookup.ND;sha=lookup.sha;save=lookup.save
def main():
    parentp=ROOT/'verification/native-resource-table-initialize-disc-build-current.json';parent=json.loads(parentp.read_text());assert sha(parent['derived_disc'])==parent['derived_disc_sha256'] and sha(parent['derived_stage'])==parent['derived_stage_sha256']
    ancestor=json.loads(Path(parent['parent_build']).read_text());symbols=dict(ancestor['symbols']);base=parent['resident_address'];reserve=20480;floor=base+reserve;old=Path(parent['linked_component']).read_bytes();assert old[:ancestor['linked_component_bytes']]==Path(ancestor['linked_component']).read_bytes()
    specs=[dict(id='lookup',proof='native-frame-lookup-current.json',source='frame-lookup-local-verified.c',shim='frame-lookup-shim.S',entry='biwn_native_frame_lookup',return_symbol='biwn_native_frame_lookup_return',original=0x1ac3c,gate=lookup),dict(id='single',proof='native-frame-reference-single-lean-current.json',source='frame-reference-single-lean.c',shim='frame-reference-single-lean-shim.S',entry='biwn_frame_single_lean',return_symbol=None,original=0x1ae56,gate=single),dict(id='multi',proof='native-frame-reference-release-current.json',source='frame-reference-release-native.c',shim='frame-reference-release-shim.S',entry='biwn_native_frame_reference_release',return_symbol=None,original=0x1ae88,gate=multi)]
    proofs={};provenance=json.loads((ROOT/'verification/native-frame-lookup-model-reviewed-current.json').read_text());assert sha(ND/specs[0]['source'])==provenance['canonical_sha256']
    for spec in specs:
        p=ROOT/'verification'/spec['proof'];proof=json.loads(p.read_text());assert proof['source_accepted'];proofs[spec['id']]=proof
        for field in ['dependencies_sha256','artifacts_sha256']:
            for path,h in proof.get(field,{}).items():assert sha(path)==h,path
    out=ROOT/'builds/BIWN-native-cache-cluster'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),parent_build=str(parentp),parent_build_sha256=sha(parentp),new_training=False,default_promoted=False,current_preview_restarted=False,game_frames=0,physical_console_verified=False,whole_game_complete=False)
    def mark():save(out/'build.json',state);save(ROOT/'verification/native-cache-cluster-build-active.json',state)
    mark();n=None
    try:
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');paths=[Path(__file__),Path(acquire.__file__),Path(table.__file__),Path(heap_gate.__file__),ND/'heap-initialize.S',*[p for spec in specs for p in [ND/spec['source'],ND/spec['shim'],Path(spec['gate'].__file__)]]];snap=out/'source-snapshot';snap.mkdir()
        for p in paths:shutil.copy2(p,snap/p.name)
        payload=bytearray(old);init_offset=symbols['biwn_native_heap_initialize']-base;baseline_path=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline_path)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';baseline=baseline_path.read_bytes();oldinit=bytearray(baseline[0x1557a:0x155c2]);newinit=bytearray(oldinit)
        for offset,delta in [(2,0),(18,0),(24,0),(30,4),(36,8)]:oldinit[offset:offset+4]=(parent['heap_start']+delta).to_bytes(4,'big');newinit[offset:offset+4]=(floor+delta).to_bytes(4,'big')
        assert payload[init_offset:init_offset+72]==oldinit;payload[init_offset:init_offset+72]=newinit
        occurrences=[i for i in range(len(old)-3) if old[i:i+4]==parent['heap_start'].to_bytes(4,'big')];assert occurrences==[init_offset+2,init_offset+18,init_offset+24,4504,4564]
        for offset,opcode in [(4504,b'\x26\x3c'),(4564,b'\x0c\x80')]:assert old[offset-2:offset]==opcode;payload[offset:offset+4]=floor.to_bytes(4,'big')
        records=[]
        with (out/'compile.log').open('w') as log:
            for spec in specs:
                d=out/spec['id'];d.mkdir();start=base+len(payload)
                commands=[[prefix+'gcc','-m68000','-msoft-float','-std=c99','-Os','-ffreestanding','-fno-pie','-fno-common','-Wall','-Wextra','-Werror','-I'+str(ND),'-c',str(ND/spec['source']),'-o',str(d/'body.o')],[prefix+'as','-m68000','-o',str(d/'shim.o'),str(ND/spec['shim'])],[prefix+'ld','-Ttext='+hex(start),'-e',spec['entry'],'-o',str(d/'component.elf'),str(d/'shim.o'),str(d/'body.o')],[prefix+'objcopy','-O','binary',str(d/'component.elf'),str(d/'component.bin')]]
                for command in commands:assert subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode==0,command
                local={}
                for line in subprocess.check_output([prefix+'nm','--defined-only',str(d/'component.elf')],text=True).splitlines():
                    p=line.split()
                    if len(p)==3:local[p[2]]=int(p[0],16)
                code=(d/'component.bin').read_bytes();alignment=local[spec['entry']]-start;assert alignment in [0,2] and code[:alignment]==b'\x4e\x71'*(alignment//2);expected=proofs[spec['id']].get('binary_bytes');assert len(code)==expected+alignment
                payload.extend(code);symbols.update(local);records.append(dict(id=spec['id'],original_entry=spec['original'],address=start,entry=local[spec['entry']],end=start+len(code),bytes=len(code),semantic_bytes=expected,alignment=alignment,return_address=local[spec['return_symbol']] if spec['return_symbol'] else local[spec['entry']]+52 if spec['id']=='single' else local[spec['entry']]+46,proof=str(ROOT/'verification'/spec['proof']),proof_sha256=sha(ROOT/'verification'/spec['proof']),source=str(ND/spec['source']),source_sha256=sha(ND/spec['source']),binary=str(d/'component.bin'),binary_sha256=sha(d/'component.bin')))
                (d/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(d/'component.elf')],text=True))
        assert len(payload)<reserve;symbols['biwn_native_heap_start']=floor;linked=out/'resident-linked.bin';linked.write_bytes(payload);padded=out/'resident-padded.bin';padded.write_bytes(payload+bytes(reserve-len(payload)));save(out/'components.json',records);state.update(status='checking_final_component_addresses',components=records,resident_address=base,component_bytes=reserve,linked_component=str(linked),linked_component_bytes=len(payload),heap_start=floor,heap_bytes_reserved=reserve,symbols=symbols);mark()
        image=bytearray(baseline);image[base:base+reserve]=padded.read_bytes();n=lookup.Native();component_rows={}
        for spec,record in zip(specs,records):
            g=spec['gate'];g.BASE=record['address'];length=record['bytes'];candidate=bytearray(image);candidate[g.ENTRY:g.ENTRY+8]=b'\x4e\xf9'+record['entry'].to_bytes(4,'big')+b'\x4e\x71';rows=[];dynamic=[]
            for i,c in enumerate(g.vectors()):
                x=g.trace(image,c,length,True);y=g.trace(candidate,c,length,False);assert x[1]==y[1] and g.normalize(y[0],x[0],length)==x[0],(spec['id'],'ordered',i)
                a=g.native(n,image,c,length,True);b=g.native(n,candidate,c,length,False);assert a[1]==b[1] and g.normalize(b[0],a[0],length)==a[0],(spec['id'],'CPU/RAM',i);rows.append(dict(case=i,CPU=b[1],ordered_events=len(x[1])))
                if i%256==0:state['current_component']=spec['id'];state['component_cases_done']=len(rows);mark();print(spec['id'],len(rows),flush=True)
            for mode in [0,0x2000]:
                for flags in range(32):
                    if spec['id']=='lookup':
                        for kind in range(4):
                            c=dict(wanted=0xffff,pattern='first' if kind==1 else 'last' if kind==2 else 'none',refs=0xa55a,incoming=[0x80000000]*15,sr=mode|flags);c['changing_tags']=[(0x15b4a0,0xffff)] if kind==0 else [(0x15b4a0,0),(0x15b4b0,0xffff)] if kind==1 else [(0x15b52c,0)] if kind==2 else [(0x15b4a8,0xffff)]
                            x=g.trace(image,c,length,True);y=g.trace(candidate,c,length,False);assert x[1]==y[1] and g.normalize(y[0],x[0],length)==x[0];a=g.native(n,image,c,length,True,x[2]);b=g.native(n,candidate,c,length,False,y[2]);assert a[1]==b[1] and g.normalize(b[0],a[0],length)==a[0];dynamic.append(dict(SR=c['sr'],kind=kind,CPU=b[1]))
                    elif spec['id']=='single':
                        for queue in [[1,0],[0,1],[0xffff,0],[0x8000,0xffff]]:
                            c=dict(wanted=0xffff,pattern='first',refs=1,incoming=[0x80000000]*15,sr=mode|flags,read_queue=queue);x=g.trace(image,c,length,True);y=g.trace(candidate,c,length,False);assert x[1]==y[1] and g.normalize(y[0],x[0],length)==x[0];a=g.native(n,image,dict(c,_external_changes=x[2]),length,True);b=g.native(n,candidate,dict(c,_external_changes=y[2]),length,False);assert a[1]==b[1] and g.normalize(b[0],a[0],length)==a[0];dynamic.append(dict(SR=c['sr'],queue=queue,CPU=b[1]))
                    elif flags in [0,16,31] and mode==0:
                        c=dict(mode=0,wanted=0,count=1,pattern='all',incoming=[0x80000000]*15,sr=mode|flags,changing=True);x=g.trace(image,c,length,True);y=g.trace(candidate,c,length,False);assert x[1]==y[1] and g.normalize(y[0],x[0],length)==x[0];dynamic.append(dict(SR=c['sr'],ordered_only=True))
            save(out/(spec['id']+'-results.json'),rows);save(out/(spec['id']+'-changing.json'),dynamic);component_rows[spec['id']]=dict(stable=len(rows),changing=len(dynamic),changing_full_native=spec['id']!='multi')
        # Preserve and recheck existing complete acquisition/initializer at their
        # unchanged addresses with the modified resident/heap context.
        acquire.BASE=parent['frame_acquire_payload_start'];alen=parent['frame_acquire_end']-acquire.BASE;ap=json.loads((ROOT/'verification/native-frame-acquire-lean-current.json').read_text());helper=(Path(ap['directory'])/'fixture-loader.bin').read_bytes();common=bytearray(image);common[acquire.PROVIDER:acquire.PROVIDER+len(helper)]=helper;common[acquire.LOADER:acquire.LOADER+6]=b'\x4e\xf9'+acquire.PROVIDER.to_bytes(4,'big');ac=bytearray(common);ac[acquire.ENTRY:acquire.ENTRY+8]=b'\x4e\xf9'+parent['frame_acquire_entry'].to_bytes(4,'big')+b'\x4e\x71';_,cases,zeros=acquire.vectors();arows=[];zrows=[]
        for i,c in enumerate(cases):
            x=acquire.trace(common,c,alen,len(helper),True);y=acquire.trace(ac,c,alen,len(helper),False);assert x[1]==y[1] and acquire.normalize(y[0],x[0],alen)==x[0];a=acquire.run(n,common,c,alen,len(helper),True,x[2]);b=acquire.run(n,ac,c,alen,len(helper),False,y[2]);acquire.compare(out,i,c,a,b,alen,symbols);arows.append(dict(case=i,CPU=b['cpu']))
        asm=(Path(ap['directory'])/'compiled.asm').read_text();delta=parent['frame_acquire_entry']-0x148000;read_pcs=[int(m.group(1),16)+delta for m in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\bmovew (?:0x)?15b532\b',asm,re.M)];assert len(read_pcs)==3
        for i,c in enumerate(zeros):a=acquire.run(n,common,c,alen,len(helper),True);b=acquire.run_zero(n,ac,c,alen,len(helper),read_pcs);acquire.compare(out,i,c,a,b,alen,symbols);zrows.append(dict(case=i,CPU=b['cpu'],faults=len(b['faults'])))
        save(out/'acquire-results.json',arows);save(out/'acquire-zero-results.json',zrows);table.BASE=parent['resource_table_initialize_entry'];tlen=78;tc=bytearray(image);tc[table.ENTRY:table.ENTRY+8]=b'\x4e\xf9'+table.BASE.to_bytes(4,'big')+b'\x4e\x71';trows=[]
        for i,c in enumerate(table.vectors()):
            a=table.native(n,image,c,tlen,True);b=table.native(n,tc,c,tlen,False);x=table.trace(image,c,tlen,True);y=table.trace(tc,c,tlen,False);assert a[1]==b[1] and table.normalize(b[0],a[0],tlen)==a[0] and x[1]==y[1] and table.normalize(y[0],x[0],tlen)==x[0];trows.append(dict(case=i,CPU=b[1]))
        save(out/'table-results.json',trows);n.close();n=None
        state.update(status='checking_raised_heap',component_cases=component_rows,existing_acquire_cases=len(arows),existing_acquire_zero_cases=len(zrows),existing_table_cases=len(trows));mark();heap_gate.BASE=base;hi=bytearray(baseline)
        for at in [0x1521c,0x1526c]:hi[at:at+4]=floor.to_bytes(4,'big')
        hc=bytearray(hi);hc[base:base+len(payload)]=payload
        for at,name in [(0x15200,'biwn_native_heap_compact'),(0x152a2,'biwn_native_heap_allocate'),(0xe3e0,'biwn_native_copy_source_first'),(0xe3ee,'biwn_native_copy_destination_first')]:hc[at:at+6]=b'\x4e\xf9'+symbols[name].to_bytes(4,'big')
        n=lookup.Native();hrows=[]
        for i,v in enumerate(heap_gate.vectors(floor)):
            c=dict(v,read_queues=[]);a=heap_gate.native(n,bytes(heap_gate.old.Script(hi,c).memory),c,len(payload),True);b=heap_gate.native(n,bytes(heap_gate.old.Script(hc,c).memory),c,len(payload),False);assert a[1]==b[1] and heap_gate.normalize(b[0],a[0],len(payload))==a[0] and a[4]==b[4] and a[5]==b[5],('heap CPU',i);x,xram,xregs=heap_gate.trace(bytes(hi),v,len(payload),True);y,yram,yregs=heap_gate.trace(bytes(hc),v,len(payload),False);assert x==y and xregs==yregs and heap_gate.normalize(yram,xram,len(payload))==xram,('heap ordered',i);assert b[0][base:base+len(payload)]==payload;hrows.append(dict(case=i,CPU=b[1]))
            if i%256==0:state['heap_completed']=len(hrows);mark();print('heap',len(hrows),flush=True)
        save(out/'heap-results.json',hrows);n.close();n=None
        # Unchanged24KB staging,larger word-copy count. Resident finalizer is
        # unchanged; it clears staging and restores the original entry CPU.
        staging=parent['staging_address'];clear=parent['staging_bytes_cleared'];entry_source=out/'stage-entry.S';entry_source.write_text(f'''.text
.globl biwn_native_stage_entry
biwn_native_stage_entry:
move.w #0x2700,%sr
movea.l #0x200000,%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea biwn_resident_payload(%pc),%a0
lea {hex(base)},%a1
move.w #{reserve//2-1},%d0
1:move.w (%a0)+,(%a1)+
dbra %d0,1b
jmp {hex(symbols['biwn_native_startup_finalize'])}
.balign 2
biwn_resident_payload:
.incbin "{padded}"
''')
        with (out/'entry-build.log').open('w') as log:
            for cmd in [[prefix+'as','-m68000','-o',str(out/'entry.o'),str(entry_source)],[prefix+'ld','-Ttext='+hex(staging),'-e','biwn_native_stage_entry','-o',str(out/'entry.elf'),str(out/'entry.o')],[prefix+'objcopy','-O','binary',str(out/'entry.elf'),str(out/'native-entry.bin')]]:assert subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode==0
        startup=(out/'native-entry.bin').read_bytes();assert len(startup)==reserve+40 and len(startup)<clear;oldstage=Path(parent['derived_stage']).read_bytes();stage=bytearray(oldstage);patches=[]
        def patch(at,before,after,reason):
            offset=at-0x4000;assert len(before)==len(after) and stage[offset:offset+len(before)]==before,(hex(at),'before mismatch');stage[offset:offset+len(after)]=after;patches.append(dict(address=hex(at),original=before.hex(),replacement=after.hex(),reason=reason))
        patch(staging,oldstage[staging-0x4000:staging-0x4000+len(startup)],startup,'20KB resident inexisting24KB staging;newcache ports andseven heap-floor operand bytes;prior non-heap bytes unchanged.')
        for at in [0x1521c,0x1526c]:patch(at,parent['heap_start'].to_bytes(4,'big'),floor.to_bytes(4,'big'),'Reserve anadditional4KB before heap.')
        for record in records:patch(record['original_entry'],baseline[record['original_entry']:record['original_entry']+6],b'\x4e\xf9'+record['entry'].to_bytes(4,'big'),'Redirect whole cache routine toits checked final-address C/ABI implementation.')
        stagefile=out/'mainstage-cache-cluster.bin';stagefile.write_bytes(stage);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);original=bytearray(0x200000);original[0x4000:0x100000]=(session/'nextstage-68000-candidate.bin').read_bytes();installed=bytearray(original);installed[0x4000:0x100000]=stage;n=lookup.Native();rng=random.Random(0x1ac3c4000);entryrows=[]
        def enter(image,regs,sr,new):
            l=n.lib;n.device.seed(bytes(image),0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,sr)
            for i,v in enumerate(regs):l.m68k_set_reg(i,v)
            l.m68k_set_reg(16,0x4000)
            for _ in range(100000):
                pc=l.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert pc in [0x4000,0x4004] or new and (staging<=pc<staging+len(startup) or base<=pc<base+reserve),hex(pc);l.m68k_execute(1)
            else:raise AssertionError('Entry limit')
            return [l.m68k_get_reg(None,i) for i in range(18)],n.device.ram()
        for variant in range(3):
            for flags in range(32):
                regs=[rng.getrandbits(32) for _ in range(16)];regs[15]=0x180000;a,_=enter(original,regs,0x2000|flags,False);b,ram=enter(installed,regs,0x2000|flags,True);assert a==b;expected=bytearray(installed);expected[base:base+reserve]=padded.read_bytes();expected[staging:staging+clear]=bytes(clear);assert ram[:0x1fffc4]==expected[:0x1fffc4];entryrows.append(dict(variant=variant,CCR=flags,CPU=b))
        save(out/'entry-cases.json',entryrows);n.close();n=None;mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-cache-cluster-experimental.cdi';shutil.copyfile(parent['derived_disc'],disc)
        with disc.open('r+b') as stream:
            for row in patches:
                at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement']);stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after))
            stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
        intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original']))) for row in patches];pos=changes=0
        with Path(parent['derived_disc']).open('rb') as left,disc.open('rb') as right:
            while True:
                a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                if not a:break
                if a!=b:
                    for i,(x,y) in enumerate(zip(a,b)):
                        if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changes+=1
                pos+=len(a)
        assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];manifest=out/'stage-patches.json';prior=json.loads(Path(parent['patch_manifest']).read_text());save(manifest,dict(patches=prior['patches']+patches,delta_patches=patches,parent=str(parentp),parent_sha256=sha(parentp)))
        state.update(status='terminal_native_cache_cluster_built_final_addresses_heap_entry_verified_pending_gameplay',derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),component=str(padded),entry_cases=len(entryrows),heap_native_and_ordered_cases=len(hrows),staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=len(startup),patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),frame_acquire_entry=parent['frame_acquire_entry'],frame_acquire_payload_start=parent['frame_acquire_payload_start'],frame_acquire_end=parent['frame_acquire_end'],resource_table_initialize_entry=parent['resource_table_initialize_entry'],resource_table_initialize_return=parent['resource_table_initialize_return'],source_sha256={str(p):sha(p) for p in paths},changed_old_resident_offsets=[hex(i) for i,(a,b) in enumerate(zip(old,payload)) if a!=b],delta_CDI_changed_bytes=changes,scope='Complete nativecache lookup,acquire,single/group reference releases and50-slot resource initializer composed inone experimental disc. Exact final-address component gates andcontrolled reads,3392raised-heap CPU/RAM/blitter/ordered cases,96startup cases. Original private-frame/IRQ/fault/timing limits fromcomponent proofs remain;onlyacquisition DIVSzero modeled with actualinertRTE. Lookup scalar authored bylocalLLM afterone feedbackrepair;allABI/otherC/checks coordinator. Larger20KB reserve changesheap floor4KB. No gameplay/physical/full-source/default-promotion proof.');mark();save(ROOT/'verification/native-cache-cluster-build-current.json',state);print(state['status'],len(payload),reserve,component_rows,flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:
        if n:n.close()
if __name__=='__main__':main()

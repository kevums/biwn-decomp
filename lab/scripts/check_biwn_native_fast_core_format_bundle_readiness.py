"""Compiled acquire in original two-client load/wait/wake native execution.
Original resource/CD/kernel bodies, preserved disc bytes via explicit BIOS adapters.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess
import check_biwn_resource_readiness as ready
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x15edc0;ENTRY=0x1af04
class Runtime(ready.Runtime):
    linked_bundle=None
    def run(self,ram,initial,case,payload,symbols,compiled):
        self.setup(ram,0,case);ready.scene.lifecycle.seed_cpu(self,initial);steps=[];minimum={ctx:ctx+0x400 for ctx in ready.CLIENTS}
        last_user=ready.CLIENTS[0]
        minimum_ssp=initial.ssp
        ranges=[(x,y)for x,y in ready.gen.RANGES.items()]+[(0xd1e0,0xd2a0),(0xd2f0,0xd30a),(0xdf04,0xdf22),(0xdf8c,0xdfa6),(0xdef6,0xdf04),(0xde08,0xde5c),(0xdeb6,0xdee2),(0xdf60,0xdf6c),(0xdf7a,0xdf7c),(ready.DONE[0],ready.DONE[0]+6)]
        if compiled:ranges.append((BASE,BASE+len(payload)))
        if compiled and self.linked_bundle:ranges.append((self.linked_bundle['resident_address'],self.linked_bundle['resident_address']+self.linked_bundle['component_bytes']))
        for _ in range(500000):
            pc=self.core.m68k_get_reg(None,16);state=self.cpu();ctx=self.current()
            if state.sr&0x2000:minimum_ssp=min(minimum_ssp,state.registers[15]);assert initial.ssp-4096<=state.registers[15]<=initial.ssp
            if not(state.sr&0x2000):minimum[ctx]=min(minimum[ctx],state.registers[15]);assert ctx+38<=state.registers[15]<=ctx+0x404,(hex(ctx),hex(state.registers[15]))
            if compiled and pc!=ENTRY and not any(x<=pc<y for x,y in self.acquire_private_ranges)and pc not in ready.DONE and not(state.sr&0x2000):
                assert state.registers[15]>=ctx+0x400-512-24+72,('helper stack overlaps compiled frame',hex(pc),hex(state.registers[15]))
            if self.linked_bundle:
                while self.frames[ctx]and pc==self.frames[ctx][-1]['_return_PC']and state.registers[15]==self.frames[ctx][-1]['_entry_SP']+4:self.end(state)
            if pc in ready.DONE:
                self.returned_observe(state)
                if pc==ready.DONE[1]:break
            if pc in ready.RES_ENTRIES:
                row=self.begin(state,pc)
                if self.linked_bundle:row.update(_return_PC=ready.get(self.device.ram(),state.registers[15]),_entry_SP=state.registers[15])
            if not self.linked_bundle:
                if pc in ready.RES_RETURNS and not(compiled and pc==0x1b000):self.end(state)
                if compiled and pc==symbols['biwn_native_resource_acquire_return']:self.end(state)
            if pc in ready.CD_ENTRIES:self.cdstart(state,pc)
            if pc in ready.CD_RETURNS:self.cdend(state)
            if pc in [0xdf8c,0xdf9c]:self.sync_observe(state,pc)
            if pc==0xdfa4:self.ready('after_signal',state)
            if pc in [0x303c,0x3042]:
                opcode=ready.get(self.device.ram(),pc,2);self.bios_cd_adapter(state,pc)
                if pc==0x3042:self.cdend(state)
                for reg in [0,1,8,9,10]:self.core.m68k_set_reg(reg,state.registers[reg])
                self.core.m68k_set_reg(17,state.sr);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);steps.append(pc);continue
            assert any(x<=pc<y for x,y in ranges),hex(pc)
            if compiled:assert not(ENTRY<pc<0x1b002),hex(pc)
            if compiled and self.linked_bundle:
                assert not any(x<pc<y for x,y in [(0x15200,0x152a2),(0x152a2,0x1545c),(0xe3ee,0xe4aa),(0xde08,0xde5c),(0xdeb6,0xdee2)]),hex(pc)
                assert not(0xe3e0<pc<0xe3ee),hex(pc)
            if pc in [0xdf60,0xdf8c]:self.yields.append(self.event(state))
            steps.append(pc);self.core.m68k_execute(1)
            if self.linked_bundle:
                after=self.cpu()
                if not(after.sr&0x2000)and self.current()!=last_user:self.handoff(after,self.handoffs);last_user=self.current()
            elif pc in [0xdf6a,0xdf9a]or(pc==0xde5a and self.core.m68k_get_reg(None,16)not in [0xdf66,0xdf96]):self.handoff(self.cpu(),self.handoffs)
        else:raise AssertionError('compiled two-client resource run did not finish')
        info=self.info();info['steps']=steps;info['minimum_SP']={str(k):v for k,v in minimum.items()};info['minimum_SSP']=minimum_ssp;return self.device.ram(),self.cpu(),info

def normalize(ram,ref,length):
    b=bytearray(ram);b[BASE:BASE+length]=ref[BASE:BASE+length];b[ENTRY:ENTRY+8]=ref[ENTRY:ENTRY+8]
    for ctx in ready.CLIENTS:b[ctx+38:ctx+0x400-24]=ref[ctx+38:ctx+0x400-24]
    return b

def public_info(info):
    return dict(disc_requests=info['disc_requests'],disc_completions=info['disc_completions'],disc_stops=info['disc_stops'],returned=info['returned'],readiness=[{k:v for k,v in x.items()if k!='CPU'}for x in info['readiness']],resource_calls=[dict(target=x['target'],args=x['args'],payload=x.get('payload'))for x in info['resource_body_calls']],handoff_contexts=[x['context']for x in info['handoffs']],yield_contexts=[x['context']for x in info['yields']])

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);p.add_argument('--relocated',action='store_true');args=p.parse_args();nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=(args.source or nd/'resource-acquire-reference.c').resolve()
    bundle=None;redirects={};bundle_paths=[]
    if args.relocated:
        bp=ROOT/'verification/native-fast-core-format-bundle-linked-fixture-current.json';bundle=json.loads(bp.read_text());bundle_paths=[bp,Path(bundle['component']),Path(bundle['patch_manifest'])]
        assert sha(bundle['component'])==bundle['component_sha256']and sha(bundle['patch_manifest'])==bundle['patch_manifest_sha256']
        assert bundle['resident_address']==0x15edc0 and bundle['heap_start']==0x162dc0 and bundle['component_bytes']==16384
        patches=json.loads(Path(bundle['patch_manifest']).read_text())['patches']
        redirects={int(x['address'],16):bytes.fromhex(x['replacement'])for x in patches if int(x['address'],16)in [0x15200,0x152a2,0xe3e0,0xe3ee,0xde08,0xdeb6]}
        assert len(redirects)==6
    layout=json.loads((ROOT/'verification/native-fast-core-format-bundle-linked-fixture-current.json').read_text())
    name='native-fast-core-format-bundle-readiness-relocated'if args.relocated else'native-fast-core-format-bundle-readiness'
    oldpath=ROOT/'verification/biwn-resource-readiness-checks.json';old=json.loads(oldpath.read_text());assert old['resource_readiness_verified'];od=Path(old['directory']);library=od/'libresource-readiness.dylib'
    out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),limit=args.limit,source_accepted=False,real_readiness_component_pass=False,game_frames=0,whole_game_complete=False,BIOS_adapters=[0x303c,0x3042],private_stack_policy='Only client stack bytesctx+38..entrySP-24 are excluded; original24savebytes and contextrecords retained.',coordinator_reference=source==nd/'resource-acquire-reference.c')
    state['source_built_relocated_dependencies']=args.relocated
    state['both_lanes_heap_reservation']=layout['component_bytes']
    state['both_lanes_heap_start']=layout['heap_start']
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        build=out/'build';r=subprocess.run(['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-fast-core-bundle/20261018T220820.261448Z/Makefile','format-bundle','BUILD='+str(build),'ACQUIRE_SOURCE='+str(source)],cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-format-bundle.elf')],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);binary=build/'native-format-bundle.bin';payload=binary.read_bytes();(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/'native-format-bundle.elf')],text=True))
        assert sha(binary)=='35a80f52ff4bdede73aa8ec84abd8fa94a1e8c2bea9e3c85349318ded41a509a', "Wrong linked bundle"
        cases=[x['case']for x in json.loads((od/'fixtures.json').read_text())][:args.limit or None];save(out/'fixtures.json',cases);rt=Runtime(library);rt.linked_bundle=bundle;rows=[]
        asmrow=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(build/'resource-acquire-shim.o')],text=True).splitlines()if '.text.biwn_native_resource_acquire 'in l)
        bodyrow=next(l.split()for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'native-format-bundle.elf')],text=True).splitlines()if l.split()[-1]=='biwn_native_resource_acquire_body')
        owned={}
        for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'resource-acquire-native.o')],text=True).splitlines():
            fields=line.split()
            if len(fields)==4 and fields[2].lower()=='t':owned[fields[3]]=int(fields[1],16)
        rt.acquire_private_ranges=[(symbols['biwn_native_resource_acquire'],symbols['biwn_native_resource_acquire']+int(asmrow[2],16))]
        found=[]
        for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'native-format-bundle.elf')],text=True).splitlines():
            fields=line.split()
            if len(fields)==4 and fields[3]in owned:
                assert int(fields[1],16)==owned[fields[3]]
                found.append(fields[3]);rt.acquire_private_ranges.append((int(fields[0],16),int(fields[0],16)+int(fields[1],16)))
        assert sorted(found)==sorted(owned),found
        state['acquire_compiler_private_PC_ranges']=rt.acquire_private_ranges
        try:
            for i,case in enumerate(cases):
                path=Path(case['capture']);capture=path.parent;info=json.loads((capture/('startup-capture-'+path.stem.split('-')[-1]+'.json')).read_text());original_ram=path.read_bytes();assert sha(path)==info['C_RAM_sha256'];image,initial=ready.fixture(original_ram,case,info)
                if layout:
                    image=bytearray(image);base=layout['resident_address'];floor=layout['heap_start'];reserve=floor-base
                    assert ready.get(image,0x112d60)==base and ready.get(image,base+4)==ready.get(image,base+8)==0
                    size=ready.get(image,base);assert size>reserve and ready.get(image,0x112d64)==size
                    assert all(not(base<=ready.get(image,0x112960+j*4)<floor)for j in range(256))
                    for addr,val in [(floor,size-reserve),(floor+4,0),(floor+8,0),(0x112d60,floor),(0x112d64,size-reserve)]:image[addr:addr+4]=val.to_bytes(4,'big')
                    for addr in [0x1521c,0x1526c]:assert ready.get(image,addr)==base;image[addr:addr+4]=floor.to_bytes(4,'big')
                candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_resource_acquire'].to_bytes(4,'big')+b'\x4e\x71'
                if bundle:
                    candidate[base:base+bundle['component_bytes']]=Path(bundle['component']).read_bytes()
                    for addr,data in redirects.items():candidate[addr:addr+len(data)]=data
                left=rt.run(image,initial,case,payload,symbols,False);right=rt.run(candidate,initial,case,payload,symbols,True)
                la,ra=public_info(left[2]),public_info(right[2]);norm=normalize(right[0],left[0],len(payload));save(out/('case-'+str(i)+'-original.json'),left[2]);save(out/('case-'+str(i)+'-compiled.json'),right[2])
                if bundle:
                    norm[base:base+bundle['component_bytes']]=left[0][base:base+bundle['component_bytes']]
                    for addr,data in redirects.items():norm[addr:addr+len(data)]=left[0][addr:addr+len(data)]
                    # Existing native scheduler ABI reserves private C scratch
                    # below the original six-byte RTE frame. Exclude only the
                    # actually observed stack footprint, retaining that frame.
                    low=min(left[2]['minimum_SSP'],right[2]['minimum_SSP']);norm[low:initial.ssp-6]=left[0][low:initial.ssp-6]
                    state['supervisor_private_stack_policy']='Observed minimumSSP..initialSSP-6 only; original six-byte exception/RTE frame and returned SSP retained.'
                if bytes(left[1])!=bytes(right[1])or norm!=left[0]or la!=ra:
                    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=ready.scene.live.prior.scheduler.cpu_dict(left[1]),compiled_CPU=ready.scene.live.prior.scheduler.cpu_dict(right[1]),original_public_info=la,compiled_public_info=ra,RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:128]));(out/'original-RAM.bin').write_bytes(left[0]);(out/'compiled-RAM.bin').write_bytes(right[0]);raise AssertionError(str(out/'mismatch.json'))
                assert right[0][BASE:BASE+len(payload)]==payload
                assert right[2]['steps'].count(symbols['biwn_native_resource_acquire_body'])==2
                assert len(right[2]['disc_requests'])==len(right[2]['disc_completions'])==len(right[2]['completion_events'])==1 and right[2]['disc_stops']==1
                assert [x['target']for x in right[2]['sync_calls']]==[0xdf8c,0xdf9c]
                wait,signal,awake=right[2]['readiness'];assert wait['ready_word']==0 and wait['reference_count']==2 and signal['ready_word']==1 and signal['client_wait_masks'][1]==1 and awake['client_wait_masks'][1]==0
                handles=[x['CPU']['registers'][0]for x in right[2]['returned']];assert len(handles)==2 and handles[0]==handles[1]and handles[0]!=0 and ready.get(right[0],handles[0])!=0
                payloads=[x['payload']for x in right[2]['resource_body_calls']if 'payload'in x];assert len(payloads)==1 and payloads[0]['matches_preserved_normalized_disc_payload']
                if bundle:
                    assert right[0][base:base+bundle['component_bytes']]==Path(bundle['component']).read_bytes()
                    hits={key:right[2]['steps'].count(bundle['symbols'][key])for key in ['biwn_native_heap_allocate_body','biwn_native_copy_body','biwn_native_scheduler_select']};assert all(hits.values()),hits
                    state['last_relocated_dependency_hits']=hits
                rows.append(dict(case=i,parameters=case,initial_fixture_sha256=hashlib.sha256(image).hexdigest(),shared_handle=handles[0],payload=payloads[0],compiled_acquire_body_hits=2,minimum_SP=right[2]['minimum_SP'],returned_CPU=ready.scene.live.prior.scheduler.cpu_dict(right[1]),full_return_CPU_public_RAM_semantic_calls_readiness_payload_match=True));state['completed']=len(rows);mark();print('Readiness',len(rows),'/',len(cases),flush=True)
        finally:rt.close()
        save(out/'results.json',rows);paths=[Path(__file__),Path(ready.__file__),ROOT/'scripts/check_biwn_disc_scene_actors.py',source,oldpath,library,*[nd/n for n in ['resource-acquire-native.h','resource-acquire-shim.S','resource-acquire.ld','Makefile.resource-acquire','Makefile']],*bundle_paths]
        state.update(status='terminal_native_acquire_readiness_preflight_pass'if args.limit else'terminal_native_acquire_real_load_wait_signal_component_pass',source_accepted=False,real_readiness_component_pass=not args.limit,cases=len(rows),acquisition_returns=len(rows)*2,compiled_acquire_body_hits=sum(x['compiled_acquire_body_hits']for x in rows),verified_payload_bytes=sum(x['payload']['bytes']for x in rows),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),artifacts_sha256={str(q):sha(q)for q in paths},scope='Compiled acquire runs in original two-client loader/wait/wake test. Native original allocator/loader/CD math/copy/blitter/kernel/task removal execute actual instructions. Two explicitBIOSadapters and externaldisccompletion afteractualhandoff retained. ReturnCPU, publicRAM including original24savebytes/contextrecords, semantic helperargs/readiness/wakemask/payload/returnstates match. Clientprivatestack bytes excluded. Synthetic2clientring/startupcaptures; no coldgame/nativebundle/IRQ/physical/fullgame proof.')
        if bundle:state['scope']+=' Relocatedprofile additionally reserves16384bytes from the checked single free head block in both lanes; applies6existingnativehelper redirects on candidate only. Source-built allocator/copy/scheduler execute; loader/CD/wait/signal retain original bodies. This is a transformed startup fixture, not a new coldgame/disc build.'
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

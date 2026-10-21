"""Compiled loader in two-client load/wait/wake execution with actual dependencies.
Explicit BIOS adapters and preserved-disc completion remain, as in the reference.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess
import check_biwn_resource_readiness as ready
import check_biwn_native_acquire_compact_bundle_readiness as old
from check_biwn_native_button_digit import ROOT,sha,save
BASE,ENTRY=0x148000,0x1b044
class Runtime(ready.Runtime):
 def run(self,ram,initial,case,payload,symbols,compiled,bundle):
  self.setup(ram,0,case);ready.scene.lifecycle.seed_cpu(self,initial);steps=[];minimum={ctx:ctx+0x400 for ctx in ready.CLIENTS};last_user=ready.CLIENTS[0];min_ssp=initial.ssp
  load_ends={};acquire_ends={};load_helper_headroom=[];acquire_helper_headroom=[]
  ranges=[(x,y)for x,y in ready.gen.RANGES.items()]+[(0xd1e0,0xd2a0),(0xd2f0,0xd30a),(0xdf04,0xdf22),(0xdf8c,0xdfa6),(0xdef6,0xdf04),(0xde08,0xde5c),(0xdeb6,0xdee2),(0xdf60,0xdf6c),(0xdf7a,0xdf7c),(ready.DONE[0],ready.DONE[0]+6)]
  if compiled:ranges.append((BASE,BASE+len(payload)))
  if compiled and bundle:ranges.append((bundle['resident_address'],bundle['resident_address']+bundle['component_bytes']))
  for _ in range(700000):
   pc=self.core.m68k_get_reg(None,16);state=self.cpu();ctx=self.current();sp=state.registers[15]
   if state.sr&0x2000:min_ssp=min(min_ssp,sp);assert initial.ssp-4096<=sp<=initial.ssp
   else:
    minimum[ctx]=min(minimum[ctx],sp);assert ctx+38<=sp<=ctx+0x404,(hex(pc),hex(ctx),hex(sp))
    in_load=any(a<=pc<b for a,b in self.load_ranges)
    in_acquire=any(a<=pc<b for a,b in self.acquire_ranges)
    if compiled and ctx in load_ends and not in_load and pc!=ENTRY:
     assert sp>=load_ends[ctx],('load helper stack overlaps C frame',hex(pc),hex(sp),hex(load_ends[ctx]));load_helper_headroom.append(sp-load_ends[ctx])
    if compiled and ctx in acquire_ends and not in_acquire and pc!=0x1af04:
     assert sp>=acquire_ends[ctx],('nested loader overlaps acquire frame',hex(pc),hex(sp),hex(acquire_ends[ctx]));acquire_helper_headroom.append(sp-acquire_ends[ctx])
   while self.frames[ctx]and pc==self.frames[ctx][-1]['_return_PC']and sp==self.frames[ctx][-1]['_entry_SP']+4:
    target=self.frames[ctx][-1]['target'];self.end(state)
    if target==ENTRY:load_ends.pop(ctx,None)
    if target==0x1af04:acquire_ends.pop(ctx,None)
   if pc in ready.DONE:
    self.returned_observe(state)
    if pc==ready.DONE[1]:break
   if pc in ready.RES_ENTRIES:
    row=self.begin(state,pc);row.update(_return_PC=ready.get(self.device.ram(),sp),_entry_SP=sp)
    if compiled and pc==ENTRY:load_ends[ctx]=sp-24-256+72
    if compiled and bundle and pc==0x1af04:acquire_ends[ctx]=sp-24-512+72
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
   if compiled:assert not ENTRY<pc<0x1b154,hex(pc)
   if compiled and bundle:assert not 0x1af04<pc<0x1b002,hex(pc)
   if pc in [0xdf60,0xdf8c]:self.yields.append(self.event(state))
   steps.append(pc);self.core.m68k_execute(1)
   after=self.cpu()
   if not(after.sr&0x2000)and self.current()!=last_user:self.handoff(after,self.handoffs);last_user=self.current()
  else:raise AssertionError('compiled loader two-client run did not finish')
  info=self.info();info.update(steps=steps,minimum_SP={str(k):v for k,v in minimum.items()},minimum_SSP=min_ssp,min_loader_helper_headroom=min(load_helper_headroom,default=None),min_acquire_helper_headroom=min(acquire_helper_headroom,default=None));return self.device.ram(),self.cpu(),info

def main():
 global BASE
 p=argparse.ArgumentParser();p.add_argument('--component',type=Path,required=True);p.add_argument('--nested',action='store_true');p.add_argument('--limit',type=int);p.add_argument('--label',required=True);args=p.parse_args();name=args.label
 cp=args.component.resolve();component=json.loads(cp.read_text());assert component['controlled_component_pass']and not component['limit'];assert component['reference_instruction_coverage'][0]==component['reference_instruction_coverage'][1]
 BASE=component['payload_base'];combined=bool(component.get('target_proof'));word=component['word_scan']
 binary=Path(component['compiled_binary']);assert sha(binary)==component['compiled_binary_sha256'];payload=binary.read_bytes();symbols=component['symbols'];assert component['compiled_binary_sha256']=='6d4c4c6cd953df0a7000309acd27fd69d4a426783d79133cde2150a2a1cec972';nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 for path,h in component['source_sha256'].items():assert sha(path)==h,path
 bp=ROOT/('verification/native-format-bundle-linked-fixture-current.json'if combined else'verification/native-acquire-compact-bundle-linked-fixture-current.json');layout=json.loads(bp.read_text());bundle=layout if args.nested else None;redirects={}
 assert layout['heap_start']==layout['resident_address']+layout['component_bytes'] and layout['component_bytes']==(9216 if combined else 6144)
 if bundle:
  assert sha(bundle['component'])==bundle['component_sha256']and sha(bundle['patch_manifest'])==bundle['patch_manifest_sha256']
  redirects={int(x['address'],16):bytes.fromhex(x['replacement'])for x in json.loads(Path(bundle['patch_manifest']).read_text())['patches']if int(x['address'],16)in [0x15200,0x152a2,0xe3e0,0xe3ee,0xde08,0xdeb6]};assert len(redirects)==6
 rp=ROOT/'verification/biwn-resource-readiness-checks.json';reference=json.loads(rp.read_text());rd=Path(reference['directory']);library=rd/'libresource-readiness.dylib';cases=[x['case']for x in json.loads((rd/'fixtures.json').read_text())][:args.limit or None]
 out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),nested_native_acquire=args.nested,limit=args.limit,real_readiness_component_pass=False,source_accepted=False,word_scan=word,combined_payload=combined,game_frames=0,whole_game_complete=False,component_proof=str(cp),component_proof_sha256=sha(cp),compiled_binary=str(binary),compiled_binary_sha256=sha(binary))
 def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
 mark();rt=Runtime(library);rows=[]
 prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
 def owner_ranges(elf,obj,section,entry):
  parent=Path(elf).parent;asm=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(parent/obj)],text=True).splitlines()if section+' 'in l)
  owned={t[3]:int(t[1],16)for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(parent/obj.replace('shim.o','native.o'))],text=True).splitlines()if len(t:=l.split())==4 and t[2].lower()=='t'}
  ranges=[(entry,entry+int(asm[2],16))];found=[]
  for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(elf)],text=True).splitlines():
   t=l.split()
   if len(t)==4 and t[3]in owned:
    assert int(t[1],16)==owned[t[3]];found.append(t[3]);ranges.append((int(t[0],16),int(t[0],16)+int(t[1],16)))
  assert sorted(found)==sorted(owned);return ranges
 rt.load_ranges=owner_ranges(binary.with_suffix('.elf'),'resource-load-shim.o','.text.biwn_native_resource_load',symbols['biwn_native_resource_load']);rt.acquire_ranges=[]
 if 'biwn_native_load_scan'in symbols:
  obj=binary.parent/'resource-load-scan.o';row=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(obj)],text=True).splitlines()if '.text.biwn_native_resource_load_scan 'in l);entry=symbols['biwn_native_load_scan'];rt.load_ranges.append((entry,entry+int(row[2],16)))
 if bundle:
  ap=Path(component['target_proof'])if combined else ROOT/'verification/native-acquire-compact-preflight-current.json';acq=json.loads(ap.read_text());rt.acquire_ranges=owner_ranges(Path(acq['binary']).with_suffix('.elf'),'resource-acquire-shim.o','.text.biwn_native_resource_acquire',bundle['symbols']['biwn_native_resource_acquire'])
 state['compiler_private_PC_ranges']=dict(loader=rt.load_ranges,acquire=rt.acquire_ranges)
 repair_paths=[]
 if word:
  repair_path=ROOT/'verification/native-word-scan-build-current.json';repair=json.loads(repair_path.read_text());repair_binary=Path(repair['binary']);assert sha(repair_binary)==repair['binary_sha256'];repair_bytes=repair_binary.read_bytes();assert len(repair_bytes)==18;repair_paths=[repair_path,repair_binary]

 try:
  for i,case in enumerate(cases):
   capture=Path(case['capture']);info=json.loads((capture.parent/('startup-capture-'+capture.stem.split('-')[-1]+'.json')).read_text());assert sha(capture)==info['C_RAM_sha256'];image,initial=ready.fixture(capture.read_bytes(),case,info);image=bytearray(image)
   base=layout['resident_address'];floor=layout['heap_start'];reserve=floor-base;assert ready.get(image,0x112d60)==base and ready.get(image,base+4)==ready.get(image,base+8)==0;size=ready.get(image,base);assert size>reserve and ready.get(image,0x112d64)==size
   for a,val in [(floor,size-reserve),(floor+4,0),(floor+8,0),(0x112d60,floor),(0x112d64,size-reserve)]:image[a:a+4]=val.to_bytes(4,'big')
   for a in [0x1521c,0x1526c]:assert ready.get(image,a)==base;image[a:a+4]=floor.to_bytes(4,'big')
   if word:image[0x1b0ee:0x1b100]=repair_bytes
   candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_resource_load'].to_bytes(4,'big')+b'\x4e\x71'
   if bundle:
    candidate[base:base+bundle['component_bytes']]=Path(bundle['component']).read_bytes()
    for a,data in redirects.items():candidate[a:a+len(data)]=data
    candidate[0x1af04:0x1af0c]=b'\x4e\xf9'+bundle['symbols']['biwn_native_resource_acquire'].to_bytes(4,'big')+b'\x4e\x71'
   left=rt.run(image,initial,case,payload,symbols,False,None);right=rt.run(candidate,initial,case,payload,symbols,True,bundle);norm=bytearray(right[0])
   for a,z in [(BASE,len(payload)),(ENTRY,8)]:norm[a:a+z]=left[0][a:a+z]
   for ctx in ready.CLIENTS:norm[ctx+38:ctx+0x400-24]=left[0][ctx+38:ctx+0x400-24]
   if bundle:
    for a,z in [(base,bundle['component_bytes']),(0x1af04,8),*[(a,len(data))for a,data in redirects.items()]]:norm[a:a+z]=left[0][a:a+z]
    low=min(left[2]['minimum_SSP'],right[2]['minimum_SSP']);norm[low:initial.ssp-6]=left[0][low:initial.ssp-6]
   la,ra=old.public_info(left[2]),old.public_info(right[2]);save(out/(str(i)+'-original.json'),left[2]);save(out/(str(i)+'-compiled.json'),right[2])
   if bytes(left[1])!=bytes(right[1])or norm!=left[0]or la!=ra:
    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=ready.scene.live.prior.scheduler.cpu_dict(left[1]),compiled_CPU=ready.scene.live.prior.scheduler.cpu_dict(right[1]),original_public_info=la,compiled_public_info=ra,RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:128]));raise AssertionError(str(out/'mismatch.json'))
   assert right[2]['steps'].count(symbols['biwn_native_resource_load_body'])==1 and not any(ENTRY<x<0x1b154 for x in right[2]['steps'])
   if bundle:assert right[2]['steps'].count(bundle['symbols']['biwn_native_resource_acquire_body'])==2 and right[2]['min_acquire_helper_headroom']is not None
   assert len(right[2]['disc_requests'])==len(right[2]['disc_completions'])==len(right[2]['completion_events'])==1 and right[2]['disc_stops']==1
   assert [x['target']for x in right[2]['sync_calls']]==[0xdf8c,0xdf9c]
   wait,signal,awake=right[2]['readiness'];assert wait['ready_word']==0 and wait['reference_count']==2 and signal['ready_word']==1 and signal['client_wait_masks'][1]==1 and awake['client_wait_masks'][1]==0
   handles=[x['CPU']['registers'][0]for x in right[2]['returned']];assert len(handles)==2 and handles[0]==handles[1]and handles[0]!=0
   payloads=[x['payload']for x in right[2]['resource_body_calls']if 'payload'in x];assert len(payloads)==1 and payloads[0]['matches_preserved_normalized_disc_payload']
   assert right[0][BASE:BASE+len(payload)]==payload
   rows.append(dict(case=i,shared_handle=handles[0],payload=payloads[0],minimum_SP=right[2]['minimum_SP'],min_loader_helper_headroom=right[2]['min_loader_helper_headroom'],min_acquire_helper_headroom=right[2]['min_acquire_helper_headroom'],full_return_CPU_public_RAM_semantic_calls_readiness_payload_match=True));state['completed']=len(rows);mark();print('Loader readiness',len(rows),'/',len(cases),flush=True)
  save(out/'results.json',rows);paths=[Path(__file__),Path(ready.__file__),Path(old.__file__),cp,binary,rp,library,bp,Path(layout['component']),Path(layout['patch_manifest']),*repair_paths,*[nd/n for n in ['resource-load-reference.c','resource-load-word-scan.c','resource-load-native.h','resource-load-shim.S','Makefile.resource-load','resource-load.ld']]]
  state.update(status='terminal_native_loader_readiness_preflight_pass'if args.limit else'terminal_native_loader_real_load_wait_wake_component_pass',real_readiness_component_pass=not args.limit,cases=len(rows),verified_payload_bytes=sum(x['payload']['bytes']for x in rows),source_sha256={str(q):sha(q)for q in paths},scope='Fresh two-client transformedstartupfixture, sameexplicitheapreserve both lanes. Nativecompiledloader plus actualoriginalCDoffset/math/transfer/stop/copy/kernel/task bodies; nested profile additionallycompiledacquire,allocator/copy/scheduler. TwoexplicitBIOSadapters and preserved-disc externalcompletion after actualhandoff remain. FullreturnedCPU/publicRAM/readiness/payload/callsequences match; privateclientstack excludesctx+38..entrySP-24, nested observesSSPprivatearea excludingoriginal6byteRTEframe. Stackgapwatchchecksnonoverlap at observed instructions. No newCDI/game/IRQ/reentrancy/physical/fullgame claim.')
  mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:rt.close()
if __name__=='__main__':main()

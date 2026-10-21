"""Reproduce captured S=task+530 with full providers and protected task bytes."""
import os
from datetime import datetime,timezone
from pathlib import Path
import check_frame_acquire_phased_nested_v1 as nested
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
g=nested.g


def main():
    component_path=V/'frame-acquire-phased-v1-current.json';component=read(component_path)
    nested_path=V/'frame-acquire-phased-nested-v1-current.json';prior=read(nested_path)
    fault_path=V/'v39-frame-acquire-header-fault-reviewed-v1-current.json';fault=read(fault_path)
    assert component['source_accepted'] and prior['source_accepted'] and fault['frame_acquire_context_before_task_bytes']==26
    for r in [component,prior]:
        for p,h in r['dependencies_sha256'].items():assert sha(p)==h,p
    out=V/'frame-phased-watch-selected-functional-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='running_captured_depth_task_layout_provider_pairs',directory=str(out),pid=os.getpid(),new_disc_built=False,new_predictions=0,new_training=False)
    def mark():save(out/'protocol.json',state);save(V/'frame-phased-watch-selected-functional-v1-current.json',state)
    mark();n=None
    try:
        parent_path=V/'frame-acquire-phased-disc-build-v1-current.json';parent=read(parent_path)
        startup_path=V/'frame-acquire-phased-image-startup-heap-v1-current.json';startup=read(startup_path)
        assert startup['native_startup_cases']==startup['Unicorn_startup_cases']==6 and startup['heap_initialize_cases']==192
        for path,digest in parent['source_sha256'].items():assert sha(path)==digest,path
        resident=Path(parent['component']).read_bytes();payload=Path(component['binary']).read_bytes()
        helpers_path=Path(prior['directory'])/'providers.bin';helpers=helpers_path.read_bytes()
        nm=Path(prior['directory'])/'providers.elf';symbols={}
        import subprocess
        for line in subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'--defined-only',str(nm)],text=True).splitlines():
            parts=line.split()
            if len(parts)==3:symbols[parts[2]]=int(parts[0],16)
        baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
        image=bytearray(baseline);image[0x4000:0x100000]=Path(parent['derived_stage']).read_bytes()
        image[parent['resident_address']:parent['heap_start']]=resident
        actual_entry=bytes(image[g.ENTRY:g.ENTRY+8]);image[g.ENTRY:g.END]=baseline[g.ENTRY:g.END]
        image[nested.PROVIDER:nested.PROVIDER+len(helpers)]=helpers
        for at,(name,_)in nested.loader.HELPERS.items():image[at:at+6]=bytes.fromhex('4ef9')+symbols['load_provider_'+name].to_bytes(4,'big')
        def allowed(pc,frame_length,provider_length,build,compiled,native_loader):
            if pc in nested.loader.HELPERS or nested.PROVIDER<=pc<nested.PROVIDER+provider_length:return True
            if g.ENTRY<=pc<g.END and(not compiled or pc==g.ENTRY):return True
            if compiled and any(build[k]<=pc<build[k]+build[n]for k,n in [('frame_phased_early_address','frame_phased_early_bytes'),('frame_phased_tail_address','frame_phased_tail_bytes')]):return True
            if g.LOADER<=pc<0x1b154 and(not native_loader or pc==g.LOADER):return True
            return native_loader and build['resident_address']<=pc<build['resident_address']+build['linked_component_bytes']
        nested.allowed=allowed
        def normalize(ram,reference,length,zero=False):
            out=bytearray(ram)
            for lo,hi in [(g.ENTRY,g.ENTRY+8),(g.SP-384,g.SP-44)]:out[lo:hi]=reference[lo:hi]
            return bytes(out)
        g.normalize=normalize
        cases=nested.cases();plans=[(slot,i)for slot in [0,100]for i in [0,3,12,15,24,27]]
        n=g.Native();rows=[];maximum=0;minimum_headroom=1024
        for index,(slot,i)in enumerate(plans):
            task=0xc0928+slot*1024;g.SP=task+530
            case=cases[i];guard=bytes((j*37+slot*11+index)%256 for j in range(64))
            root=bytearray(image);root[task:task+64]=guard;root[0xc0920:0xc0924]=task.to_bytes(4,'big')
            item=dict(slot=slot,fixture=i,entry_SP=g.SP,lanes=[])
            for compiled_loader in [False,True]:
                common=bytearray(root)
                if not compiled_loader:common[g.LOADER:0x1b154]=baseline[g.LOADER:0x1b154]
                if compiled_loader:common[g.LOADER:g.LOADER+6]=bytes.fromhex('4ef9')+parent['symbols']['biwn_native_resource_load'].to_bytes(4,'big')
                candidate=bytearray(common);candidate[g.ENTRY:g.ENTRY+8]=actual_entry
                left=nested.run(n,common,case,len(payload),len(helpers),parent,False,compiled_loader)
                right=nested.run(n,candidate,case,len(payload),len(helpers),parent,True,compiled_loader)
                assert left['ram'][task:task+64]==right['ram'][task:task+64]==guard,(index,'task guard')
                assert right['ram'][parent['resident_address']:parent['heap_start']]==resident,'Resident modules or reserved arenas changed'
                assert right['minimum']>=task+64,(index,'SP below protected task bytes',right['minimum']-task)
                if left['cpu']!=right['cpu'] or left['calls']!=right['calls'] or g.normalize(right['ram'],left['ram'],len(payload))!=left['ram']:
                    save(out/'mismatch.json',dict(index=index,slot=slot,fixture=i,compiled_loader=compiled_loader,original_CPU=left['cpu'],candidate_CPU=right['cpu'],original_helpers=left['calls'],candidate_helpers=right['calls']));raise AssertionError('Captured-depth public comparison failed')
                maximum=max(maximum,g.SP-right['minimum']);minimum_headroom=min(minimum_headroom,right['minimum']-task)
                item['lanes'].append(dict(compiled_loader=compiled_loader,minimum_SP=right['minimum'],headroom_after_metadata=right['minimum']-task-38,protected64_bytes_unchanged=True,CPU_public_RAM_and_helper_contexts_equal=True))
            rows.append(item)
            if index%32==0:state['completed']=len(rows);mark();print('Task stack',len(rows),'/',len(plans),flush=True)
        save(out/'cases.json',rows)
        state.update(status='terminal_phased_frame_acquire_captured_depth_all101slots_task_guards_and_providers_pass',completed=len(rows),paired_provider_cases=len(rows)*2,CPU_lanes=len(rows)*4,task_slots=101,full72fixture_slots=[0,50,100],captured_entry_SP_above_task=530,protected_task_bytes=64,actual_metadata_bytes=38,actual_v40_image_addresses=True,all_resident_modules_and_reserved_arenas_unchanged=True,maximum_stack_bytes=maximum,minimum_SP_above_task=minimum_headroom,source_private_comparison_bytes=340,original_and_compiled_loaders=True,lower_CD_yield_copy_controlled=True,game_frames=0,arbitrary_IRQ_qualified=False,same_task_nested_frame_calls_qualified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(nested.__file__),Path(g.__file__),component_path,nested_path,fault_path,parent_path,Path(parent['component']),Path(component['binary']),helpers_path,startup_path,Path(parent['derived_stage']),out/'cases.json']});mark();print(state['status'],state['paired_provider_cases'],maximum,minimum_headroom,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()


if __name__=='__main__':main()

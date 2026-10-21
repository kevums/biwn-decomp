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
    out=V/'frame-acquire-phased-task-stack-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='running_captured_depth_task_layout_provider_pairs',directory=str(out),pid=os.getpid(),new_disc_built=False,new_predictions=0,new_training=False)
    def mark():save(out/'protocol.json',state);save(V/'frame-acquire-phased-task-stack-v1-current.json',state)
    mark();n=None
    try:
        parent_path=Path(prior['parent_build']);parent=read(parent_path)
        resident=Path(parent['linked_component']).read_bytes();payload=Path(component['binary']).read_bytes()
        helpers_path=Path(prior['directory'])/'providers.bin';helpers=helpers_path.read_bytes()
        nm=Path(prior['directory'])/'providers.elf';symbols={}
        import subprocess
        for line in subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'--defined-only',str(nm)],text=True).splitlines():
            p=line.split()
            if len(p)==3:symbols[p[2]]=int(p[0],16)
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());image[nested.PROVIDER:nested.PROVIDER+len(helpers)]=helpers
        image[parent['resident_address']:parent['resident_address']+len(resident)]=resident
        for at,(name,_)in nested.loader.HELPERS.items():image[at:at+6]=bytes.fromhex('4ef9')+symbols['load_provider_'+name].to_bytes(4,'big')
        cases=nested.cases();plans=[(slot,i)for slot in [0,50,100]for i in range(len(cases))]+[(slot,slot%len(cases))for slot in range(101)]
        n=g.Native();rows=[];maximum=0;minimum_headroom=1024
        for index,(slot,i)in enumerate(plans):
            task=0xc0928+slot*1024;g.SP=task+530
            case=cases[i];guard=bytes((j*37+slot*11+index)%256 for j in range(64))
            root=bytearray(image);root[task:task+64]=guard;root[0xc0920:0xc0924]=task.to_bytes(4,'big')
            item=dict(slot=slot,fixture=i,entry_SP=g.SP,lanes=[])
            for compiled_loader in [False,True]:
                common=bytearray(root)
                if compiled_loader:common[g.LOADER:g.LOADER+6]=bytes.fromhex('4ef9')+parent['symbols']['biwn_native_resource_load'].to_bytes(4,'big')
                candidate=bytearray(common);candidate[g.BASE:g.BASE+len(payload)]=payload;candidate[g.ENTRY:g.ENTRY+8]=bytes.fromhex('4ef9')+g.BASE.to_bytes(4,'big')+bytes.fromhex('4e71')
                left=nested.run(n,common,case,len(payload),len(helpers),parent,False,compiled_loader)
                right=nested.run(n,candidate,case,len(payload),len(helpers),parent,True,compiled_loader)
                assert left['ram'][task:task+64]==right['ram'][task:task+64]==guard,(index,'task guard')
                assert right['minimum']>=task+64,(index,'SP below protected task bytes',right['minimum']-task)
                if left['cpu']!=right['cpu'] or left['calls']!=right['calls'] or g.normalize(right['ram'],left['ram'],len(payload))!=left['ram']:
                    save(out/'mismatch.json',dict(index=index,slot=slot,fixture=i,compiled_loader=compiled_loader,original_CPU=left['cpu'],candidate_CPU=right['cpu'],original_helpers=left['calls'],candidate_helpers=right['calls']));raise AssertionError('Captured-depth public comparison failed')
                maximum=max(maximum,g.SP-right['minimum']);minimum_headroom=min(minimum_headroom,right['minimum']-task)
                item['lanes'].append(dict(compiled_loader=compiled_loader,minimum_SP=right['minimum'],headroom_after_metadata=right['minimum']-task-38,protected64_bytes_unchanged=True,CPU_public_RAM_and_helper_contexts_equal=True))
            rows.append(item)
            if index%32==0:state['completed']=len(rows);mark();print('Task stack',len(rows),'/',len(plans),flush=True)
        save(out/'cases.json',rows)
        state.update(status='terminal_phased_frame_acquire_captured_depth_all101slots_task_guards_and_providers_pass',completed=len(rows),paired_provider_cases=len(rows)*2,CPU_lanes=len(rows)*4,task_slots=101,full72fixture_slots=[0,50,100],captured_entry_SP_above_task=530,protected_task_bytes=64,actual_metadata_bytes=38,maximum_stack_bytes=maximum,minimum_SP_above_task=minimum_headroom,source_private_comparison_bytes=340,original_and_compiled_loaders=True,lower_CD_yield_copy_controlled=True,game_frames=0,arbitrary_IRQ_qualified=False,same_task_nested_frame_calls_qualified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(nested.__file__),Path(g.__file__),component_path,nested_path,fault_path,parent_path,Path(parent['linked_component']),Path(component['binary']),helpers_path,out/'cases.json']});mark();print(state['status'],state['paired_provider_cases'],maximum,minimum_headroom,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()


if __name__=='__main__':main()

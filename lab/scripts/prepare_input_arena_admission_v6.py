"""Raise the provisional input reserve for the measured shared-arena chain.

Keep v5 C algorithms and all addresses unchanged; one immediate byte changes
512to768. The bound remains provisional for other real helpers/IRQ nesting.
"""
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone


def main():
    prior_path=V/'native-input-acquire-arena-caller-v1-current.json';prior=read(prior_path)
    assert prior['completed']==18 and prior['native_max_caller_stack']==786 and prior['minimum_private_arena_stack_offset']==60
    for p,h in prior['source_sha256'].items():assert sha(p)==h,p
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    old=nd/'input-dispatch-native-v5-rebased';new=nd/'input-dispatch-native-v6-arena-admission';new.mkdir(exist_ok=False)
    for source in old.iterdir():
        if source.is_file():clone(source,new/source.name)
    path=new/'admission-entry.S';text=path.read_text();assert text.count('move.l #512,-(%sp)')==1
    path.write_text(text.replace('move.l #512,-(%sp)','move.l #768,-(%sp)').replace('Native reserve512 is provisional for the currently bounded helper test.','Native reserve768 is provisional for the shared-arena helper chain.'))
    out=V/'native-input-arena-admission-v6'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proc=subprocess.run(['make','-f','Makefile.portable'],cwd=new,capture_output=True,text=True);(out/'Root-build.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
    before=(old/'build-portable/native-input.bin').read_bytes();after=(new/'build-portable/native-input.bin').read_bytes()
    assert len(before)==len(after)==10580
    offsets=[i for i,(a,b)in enumerate(zip(before,after))if a!=b]
    pattern=bytes.fromhex('2f3c00000200');positions=[i for i in range(len(before))if before[i:i+6]==pattern];assert len(positions)==1
    at=positions[0];assert offsets==[at+4] and after[at:at+6]==bytes.fromhex('2f3c00000300')
    copied=P/'workbench'/new.relative_to(ROOT);copied.mkdir(parents=True)
    for source in new.iterdir():
        if source.is_file():clone(source,copied/source.name)
    copied_build=P/'workbench/builds/native-input-arena-admission-v6'/out.name
    relative=Path('../../../../../builds/native-input-arena-admission-v6')/out.name
    proc=subprocess.run(['make','-f','Makefile.portable','BUILD='+str(relative)],cwd=copied,capture_output=True,text=True);(out/'copied-build.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
    assert(copied_build/'native-input.bin').read_bytes()==after
    state=dict(status='terminal_v6_input_reserve768_single_immediate_change_copied_SDK_identical',directory=str(out),pid=os.getpid(),source_profile=str(new),payload=str(new/'build-portable/native-input.bin'),payload_sha256=sha(new/'build-portable/native-input.bin'),module_bytes=10580,base=0x17c724,entry=0x17efdc,native_reserve=768,old_reserve=512,changed_bytes=1,changed_byte_offsets=offsets,all_other_bytes_identical=True,algorithm_runtime_C_statements_changed=0,all_symbol_addresses_unchanged=True,copied_build=str(copied_build),copied_build_byte_identical=True,shared_arena_chain_full_caller_peak=786,caller_entry_overhead=60,measured_chain_below768=True,global_real_helper_IRQ_bound_proven=False,new_disc_built=False,new_predictions=0,optimizer_updates=0,default_promoted=False,scope=__doc__)
    paths=[Path(__file__),prior_path,old/'build-portable/native-input.bin',new/'build-portable/native-input.bin',new/'build-portable/native-input.elf',out/'Root-build.log',out/'copied-build.log',*[p for p in new.iterdir()if p.is_file()]]
    state['source_sha256']={str(p):sha(p)for p in paths};save(out/'protocol.json',state);save(V/'native-input-arena-admission-v6-current.json',state)
    print(state['status'],flush=True)


if __name__=='__main__':main()

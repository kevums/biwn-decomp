"""Classify exact-call instruction-observer histograms using deployed ELF sizes."""
import collections,csv,json,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    out=V/'record-strides-first-scene-profile-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    bp=V/'native-record-strides-disc-build-v1-current.json';b=read(bp);build=Path(b['directory'])/'five-build'
    payload=(build/'native-shared.bin').read_bytes();resident=Path(b['component']).read_bytes();off=b['shared_Deck_code_address']-b['resident_address']
    assert resident[off:off+len(payload)]==payload and len(payload)==54134
    raw=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-S',str(build/'native-shared.elf')],text=True);(out/'ELF-symbol-sizes.txt').write_text(raw)
    functions=[]
    for line in raw.splitlines():
        parts=line.split()
        if len(parts)!=4 or parts[2].lower()!='t':continue
        address,size=int(parts[0],16),int(parts[1],16);name=parts[3]
        if re.search(r'biwn_v\d+_(?:records|gpu|clear|rotation|display)_(?:begin|end)$',name):continue
        functions.append((address,address+size,name))
    proofs={};deps={str(Path(__file__)):sha(__file__),str(bp):sha(bp),str(build/'native-shared.elf'):sha(build/'native-shared.elf'),str(build/'native-shared.bin'):sha(build/'native-shared.bin'),str(out/'ELF-symbol-sizes.txt'):sha(out/'ELF-symbol-sizes.txt')}
    for lane in ['candidate','control']:
        jp=V/f'record-strides-first-scene-profile-v1-{lane}-current.json';j=read(jp)
        assert j['status']=='terminal_readonly_first_scene_profile_prior_1000_frame_hashes_preserved'
        for path,h in j['source_sha256'].items():assert sha(path)==h,path
        deps[str(jp)]=sha(jp);deps.update(j['source_sha256'])
        rows=[{k:int(v)for k,v in x.items()}for x in csv.DictReader(Path(j['histogram']).open())]
        groups=collections.Counter();events=[json.loads(x)for x in Path(j['trace']).read_text().splitlines()]
        assert len(events)==2 and [e['kind']for e in events]==['entry','return']
        total=sum(x['count']for x in rows);assert events[1]['instruction_ordinal']-events[0]['instruction_ordinal']==total
        assert not sum(x['other_task_count']for x in rows)
        for row in rows:
            pc=row['pc'];matches=[(end-start,name)for start,end,name in functions if start<=pc<end]
            label=min(matches)[1]if matches else next((name for start,end,name in [(0x170a0,0x17326,'original records170A0'),(0x17e0e,0x17f14,'original scene17E0E'),(0xe03a,0xe098,'original clearE03A'),(0x17f14,0x185b2,'original rotation17F14'),(0x185b2,0x18854,'original display185B2')]if start<=pc<end),'outside shared')
            groups[label]+=row['count']
        proofs[lane]=dict(total_observer_callbacks=total,other_task_callbacks=0,entry=events[0],caller_return=events[1],exclusive_PC_groups=dict(groups.most_common()),prior_1000_frame_hashes_preserved=True)
    assert proofs['candidate']['entry']==proofs['control']['entry']
    assert proofs['candidate']['total_observer_callbacks']==23929 and proofs['control']['total_observer_callbacks']==14359
    facts=dict(status='terminal_first_scene_record_builder_overhead_localized_cycles_unmeasured',directory=str(out),profile='deck-shared-v34-record-strides-v1',lanes=proofs,
        coordinator_selected_optimization='Fuse the record loop ADDQ.W #1,D3 and CMPI.W #39,D3 condition update/branch while preserving logical upper D3,SR upper bits and ADD-produced X. Existing source synthesizes/copies logical flags separately for both operations at each of80loop endings.',
        same_public_entry_and_caller_return=True,new_predictions=0,new_training=False,installed_preview_changed=False,cycle_cost_measured=False,physical_speed_ratio_measured=False,
        scope='Single first scene call,exact common public entry and caller return,host-only PC histogram. Each lane preserves every prior recorded1000frameCPU/RAM/GPU/DSP/video hash. Exclusive function groups are callback counts using ELF symbol sizes;inlined work remains assigned to containing function. The compiled record body has6166callbacks versus706original record-body callbacks;separate provider/bridge work belongs to other groups. Root busywait is4496iterations versus4497original,not the main callback excess. This is not cycle accounting or a causal isolated-stride experiment.',source_sha256=deps)
    save(out/'review.json',facts);save(V/'record-strides-first-scene-profile-reviewed-v1-current.json',facts)
    print('First call23929/14359callbacks;record body6166/706. Native loop flag synthesis is next optimization.',flush=True)

if __name__=='__main__':main()

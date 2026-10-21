"""Known payload relocation through actual target-compiled copy/emulatedblitter."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json
import check_biwn_native_fast_core_format_bundle_heap as check
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',action='store_true');args=p.parse_args();name='native-fast-core-format-bundle-heap-blitter-witness'if args.bundle else'native-heap-blitter-witness'
    gp=ROOT/'verification'/('native-fast-core-format-bundle-heap-current.json'if args.bundle else'native-heap-current.json');gate=json.loads(gp.read_text());assert gate['source_accepted']and gate['native_cases']==3392 and gate['trace_cases']==3392
    for p,d in gate['source_sha256'].items():assert sha(p)==d,p
    check.BASE=0x15edc0 if args.bundle else 0x140000;symbols=gate['symbols'];payload=Path(gate['compiled_binary']).read_bytes();assert sha(gate['compiled_binary'])==gate['compiled_binary_sha256'];floor=gate['heap_floor']
    image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    for a in [0x1521c,0x1526c]:image[a:a+4]=floor.to_bytes(4,'big')
    candidate=bytearray(image);candidate[check.BASE:check.BASE+len(payload)]=payload
    for a,k in [(0x15200,'biwn_native_heap_compact'),(0x152a2,'biwn_native_heap_allocate')]:candidate[a:a+6]=b'\x4e\xf9'+symbols[k].to_bytes(4,'big')
    for a,k in [(0xe3e0,'biwn_native_copy_source_first'),(0xe3ee,'biwn_native_copy_destination_first')]:candidate[a:a+6]=b'\x4e\xf9'+symbols[k].to_bytes(4,'big')
    case=next(x for x in check.vectors(floor)if x['entry']==0x15200 and x['kind']==3);base=0x1bfa00;expected=[]
    for block,source in enumerate([base+64,base+320]):
        pattern=bytes((37+block*71+i*13)&255 for i in range(116));expected.append(pattern)
        for offset in range(0,116,4):case['initial'].append([source+12+offset,4,int.from_bytes(pattern[offset:offset+4],'big')])
    out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);n=check.sched.Native();profiles=[];raw=[]
    try:
        for name2,data,original in [('original',image,True),('compiled',candidate,False)]:
            seeded=check.old.Script(data,case);ram,cpu,pcs,cycles,calls,hw,stats=check.native(n,bytes(seeded.memory),case,len(payload),original)
            for i,pattern in enumerate(expected):assert ram[base+i*128+12:base+i*128+128]==pattern,(name2,i)
            assert int.from_bytes(ram[0x112960:0x112964],'big')==base+8 and int.from_bytes(ram[0x112964:0x112968],'big')==base+136
            raw.append((ram,cpu,hw,calls))
            profiles.append(dict(profile=name2,copy_calls=calls,hardware=hw,payload_patterns_preserved=True,
                compiled_copy_body_calls=sum(pc==symbols['biwn_native_copy_body']for pc in pcs),
                old_copy_body_steps=sum(0xe3e0<=pc<0xe4aa and pc not in [0xe3e0,0xe3ee]for pc in pcs)))
    finally:n.close()
    assert raw[0][1:]==raw[1][1:] and check.normalize(raw[1][0],raw[0][0],len(payload))==raw[0][0]
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='terminal_native_heap_real_large_copy_payload_witness_pass',directory=str(out),component_proof=str(gp),component_proof_sha256=sha(gp),profiles=profiles,payload_bytes_checked=232,copy_sizes=[128,128],heap_floor=floor,host_guest_copy=False,host_MMIO_writes_during_execution=False,source_sha256={str(Path(__file__)):sha(__file__)},scope='Actual native CPU original/compiled compactors call target-compiledcopy/emulatedblitter. Two116byte known allocated payloads relocate exactly; handles/fullCPU/publicRAM/hardware/copycalls match. Host-shim blit_commands is not a counter of CPU-origin blits; itszero is not interpreted as native inactivity. No frame/IRQ/physical timing proof.')
    save(out/'report.json',report);save(ROOT/'verification'/(name+'-current.json'),report);print(report['status'],out,flush=True)
if __name__=='__main__':main()

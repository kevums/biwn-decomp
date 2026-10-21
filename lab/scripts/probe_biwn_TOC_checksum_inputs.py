"""Controlled captured-state TOC input tests, not a natural boot continuation."""
import ctypes as c,json,struct,sys
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_scheduler as scheduler
ROOT=scheduler.ROOT
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    source=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T083153.831713Z'
    baseline_RAM=(source/'fourth-DSP-command/RAM-after-CPU.bin').read_bytes()
    baseline_DSP=(source/'fourth-DSP-command/DSP-after-CPU.bin').read_bytes()
    assert int.from_bytes(baseline_DSP[0x20:0x24],'big')==1
    expected=baseline_RAM[0xfb004:0xfb014]
    out=ROOT/'verification/BIWN-TOC-checksum-inputs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    runtime=scheduler.Native();core=runtime.lib
    core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t
    core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t
    core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32
    core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPExec.argtypes=[c.c_int32]
    core.DSPGetPC.restype=c.c_uint32;counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
    core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool
    assert core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode())
    for name,n in [('CDIntfGetTrackDuration',2),('CDIntfGetTrackSession',1),('CDIntfGetTrackInfo',2)]:
        fn=getattr(core,name);fn.argtypes=[c.c_uint32]*n;fn.restype=c.c_uint8
    # Values come from the independent CDI header parser, not the expected checksum.
    layout=json.loads((ROOT/'projects/black-ice-white-noise/analysis/session-20261012T191624.705232Z/cdi-layout.json').read_text())
    toc=bytearray(baseline_DSP[0x800:0xc00]);assert toc[:8].hex()=='0000010502413120'
    cases=[('captured_source_TOC',False,False,False),('CDI_sessions',True,False,False),('CDI_durations',False,True,False),('CDI_sessions_durations',True,True,False),('CDI_sessions_durations_first_track_start',True,True,True),('CDI_index01_start_hypothesis',False,True,False),('CDI_index01_adjacent_duration_hypothesis',False,True,False)]
    rows=[]
    try:
        for label,sessions,durations,first_start in cases:
            runtime.device.seed(baseline_RAM,0);state=bytearray(baseline_DSP);table=bytearray(toc)
            for t in layout['tracks']:
                offset=8*t['track']
                if sessions:table[offset+4]=t['session']
                if durations:
                    sectors=t['program_sectors'];table[offset+5:offset+8]=bytes([sectors//4500,(sectors//75)%60,sectors%75])
            if label.startswith('CDI_index01'):
                for index,t in enumerate(layout['tracks']):
                    offset=8*t['track'];absolute=t['declared_start_lba']+150
                    table[offset+1:offset+4]=bytes([absolute//4500,(absolute//75)%60,absolute%75])
                    if 'adjacent'in label and index+1<len(layout['tracks']) and layout['tracks'][index+1]['session']==t['session']:
                        duration=layout['tracks'][index+1]['declared_start_lba']-t['declared_start_lba'];table[offset+5:offset+8]=bytes([duration//4500,(duration//75)%60,duration%75])
            if first_start:table[9:12]=bytes([0,2,0])
            state[0x800:0xc00]=table;assert core.DSPStateLoad(c.create_string_buffer(bytes(state)))==8729
            start=counter.value;stop='budget'
            for i in range(200000):
                if i and core.DSPReadLong(0xf1b020,0)&0x80000000:stop='source_command_acknowledged';break
                core.DSPExec(1)
            assert stop=='source_command_acknowledged'
            instructions=(counter.value-start)&0xffffffff
            # Same CPU interrupt request as the observed source50DD6; supplied input here.
            core.DSPWriteLong(0xf1b3f8,0xffffffff,6);core.DSPWriteLong(0xf1a114,5,6)
            start=counter.value;irq_stop='budget'
            for i in range(1000):
                if i and not core.DSPReadLong(0xf1b3f8,0)&0x80000000 and not core.DSPReadLong(0xf1a100,0)&8:irq_stop='source_IRQ_returned';break
                core.DSPExec(1)
            assert irq_stop=='source_IRQ_returned'
            digest=runtime.device.ram()[0xfb1b0:0xfb1c0]
            row=dict(label=label,TOC_prefix_hex=table[:48].hex(),changed_TOC_bytes=[i for i,(a,b)in enumerate(zip(toc,table))if a!=b],source_hash_instructions=instructions,source_IRQ_instructions=(counter.value-start)&0xffffffff,computed_checksum=digest.hex(),expected_header_checksum=expected.hex(),matches_header=digest==expected,supplied_boundary_state=True,SSI_and_all_clocks_held=True,natural_boot=False)
            rows.append(row);print(json.dumps(row),flush=True)
        report=dict(status='terminal_controlled_TOC_input_probe',directory=str(out),source_boundary=str(source),core='pinned ordinary core',cases=rows,scope='Captured CPU/RAM/DSP boundary and explicit TOC-data/CPU-IRQ inputs; no clocks or normal boot. Original DSP computes every result; no expected result is injected.',source_C_verified=False,full_boot_verified=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-TOC-checksum-inputs-current.json',report)
    finally:core.CDIntfCloseImage();runtime.close()

if __name__=='__main__':main()

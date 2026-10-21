"""Trace actual input addresses of the captured fourth-DSP checksum command."""
import ctypes as c,hashlib,json,struct
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import check_biwn_scheduler as scheduler
import generate_biwn_entry_setup_cpu as generation
ROOT=scheduler.ROOT
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    source=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T083153.831713Z/fourth-DSP-command'
    ram=(source/'RAM-after-CPU.bin').read_bytes();incoming=(source/'DSP-after-CPU.bin').read_bytes()
    out=ROOT/'verification/BIWN-TOC-checksum-trace'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    run=scheduler.Native();core=run.lib
    core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t
    core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t
    core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32
    core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32
    buffer=c.create_string_buffer(12000);counts=Counter();reads=[];visits={};counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
    try:
        run.device.seed(ram,0);assert core.DSPStateLoad(c.create_string_buffer(incoming))==8729;start=counter.value
        for i in range(200000):
            if i and core.DSPReadLong(0xf1b020,0)&0x80000000:break
            assert core.DSPStateSave(buffer)==8729;state=buffer.raw[:8729];pc=core.DSPGetPC();bank=state[8495];regs=struct.unpack_from('=64I',state,8239)[bank*32:bank*32+32]
            offset=pc-0xf1b000;word=int.from_bytes(state[offset:offset+2],'big');op,m,n=word>>10,(word>>5)&31,word&31
            size=6 if op==38 else 2;payload=state[offset:offset+size];counts[(pc,payload)]+=1
            if (pc,payload)not in visits:visits[(pc,payload)]=generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0]
            address=None
            if op in [39,40,41]:address=regs[m]
            elif op in [43,44]:address=regs[14 if op==43 else 15]+4*(m or 32)
            elif op in [58,59]:address=regs[14 if op==58 else 15]+regs[m]
            if address is not None:
                # This trace records effective-address operands. Local LOADB/W
                # use a full aligned long in the pinned core; no byte-read claim.
                aligned=address&0xfffffffc
                reads.append(dict(PC=hex(pc),opcode=op,address=hex(address),aligned_long=hex(aligned),value=hex(core.DSPReadLong(aligned,2)),bank=bank,TOC=0xf1b800<=aligned<0xf1bc00))
            core.DSPExec(1)
        else:raise AssertionError('Source command budget exceeded')
        toc_reads=[r for r in reads if r['TOC']];addresses=sorted({int(r['aligned_long'],16)for r in toc_reads})
        report=dict(status='terminal_original_checksum_trace',directory=str(out),source_boundary=str(source),instructions=(counter.value-start)&0xffffffff,outer_blocks=sum(counts.values()),TOC_read_events=len(toc_reads),unique_TOC_longs=len(addresses),TOC_offsets=[a-0xf1b800 for a in addresses],effective_address_read_scope='DSPExec1 boundary operands only; taken delay-slot loads require separate validation',captured_state_supplied=True,clocks_held=True,source_C_verified=False,whole_boot=False,visited_instructions=[{**visits[key],'count':count}for key,count in sorted(counts.items())])
        save(out/'report.json',report);save(out/'reads.json',reads);save(ROOT/'verification/BIWN-TOC-checksum-trace-current.json',report)
        print(json.dumps({k:report[k]for k in ['directory','instructions','TOC_read_events','unique_TOC_longs','TOC_offsets']}),flush=True)
    finally:run.close()

if __name__=='__main__':main()

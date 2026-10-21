"""Observe actual E942 music DSP initialization, without mailbox scripting."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
import check_biwn_dsp_media_audio as dsp
import generate_biwn_entry_setup_cpu as generator
ROOT=media.ROOT
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded']
    proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',rows);core=runtime.core
    core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32
    out=ROOT/'verification/BIWN-music-DSP-bootstrap-probe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    def raw():
        b=c.create_string_buffer(12000);n=runtime.savers['DSP'](b);assert n==8729;return b.raw[:n]
    def decode(payload,pc):
        offset=pc-0xf1b000;size=6 if int.from_bytes(payload[offset:offset+2],'big')>>10==38 else 2
        return generator.loader.base.binary_tools.jaguar_instructions(payload[offset:offset+size],pc,'dsp')[0][0]
    try:
        ram=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());ram[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');runtime.reset(bytes(ram),0)
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x180000;s.pc=0xe942;s.sr=0x2700;runtime.seed_cpu(s);CPU_trace=[];bootstrap_trace=[];bootstrap_decoded={}
        counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
        for _ in range(10000):
            pc=core.m68k_get_reg(None,16)
            if pc==0xea08:break
            if pc==0xe9a8:
                for __ in range(100):
                    dp=core.DSPGetPC()
                    if dp==0xf1b144:break
                    payload=c.string_at(core.DSPGetRAM(),8192);row=decode(payload,dp);bootstrap_decoded[dp]=row;before=counter.value;core.DSPExec(1);bootstrap_trace.append(dict(PC=dp,instructions=(counter.value-before)&0xffffffff))
                else:raise AssertionError('DSP flag bootstrap bound')
            assert pc in runtime.rows,hex(pc);CPU_trace.append(pc);core.m68k_execute(1)
        else:raise AssertionError('music CPU loader bound')
        initial=raw();(out/'initial-DSP.bin').write_bytes(initial);(out/'initial-RAM.bin').write_bytes(runtime.device.ram());trace=[];decoded=dict(bootstrap_decoded);counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');start=counter.value
        for _ in range(100000):
            pc=core.DSPGetPC();mailbox=core.DSPReadLong(0xf1badc,6)
            if mailbox==0:break
            assert 0xf1b000<=pc<0xf1c210,hex(pc)
            offset=pc-0xf1b000;payload=c.string_at(core.DSPGetRAM(),8192);row=decoded.get(pc)or decode(payload,pc);decoded[pc]=row
            before=counter.value;core.DSPExec(1);delta=(counter.value-before)&0xffffffff;assert delta in [1,2],(hex(pc),delta)
            if delta==2:
                a=pc+row['size'];o=a-0xf1b000;decoded[a]=decoded.get(a)or decode(payload,a)
            trace.append(dict(PC=pc,instructions=delta,mailbox_before=mailbox))
        else:raise AssertionError(('DSP mailbox bound',hex(pc),mailbox))
        final=raw();(out/'final-DSP.bin').write_bytes(final);(out/'final-RAM.bin').write_bytes(runtime.device.ram())
        report=dict(status='native_music_DSP_source_bootstrap_mailbox_ack_observed',directory=str(out),CPU_loader_trace=CPU_trace,DSP_bootstrap_trace=bootstrap_trace,DSP_trace=trace,DSP_instructions=(counter.value-start)&0xffffffff,visited_rows=sorted(decoded.values(),key=lambda r:r['address']),initial_DSP_PC=hex(struct.unpack_from('=I',initial,8192)[0]),final_DSP_PC=hex(core.DSPGetPC()),mailbox=mailbox,original_source_payload_sha256=media.sha(bytes(ram[0x7248:0x8458])),DSP_instruction_execution_C_verified=False,whole_game_complete=False,limits=['Native-only discovery from supplied FrozenRAM/CPU/device state. No SSI events, physical clock, full music sequencing/output, full4000boot or C comparison yet.'])
        media.save(out/'report.json',report);media.save(out/'status.json',dict(status='terminal_pass'));media.save(ROOT/'verification/music-DSP-bootstrap-probe.json',report)
        print(json.dumps({k:v for k,v in report.items()if k not in ['visited_rows','CPU_loader_trace','DSP_trace','DSP_bootstrap_trace']}));print('\n'.join(hex(r['address'])+' '+r['assembly']for r in report['visited_rows']))
    except BaseException as e:media.save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()

"""Original source303C->BUTCH IRQ1->GPU FIFO->304E/3042 stream probe.

Hostloaded firmware/code, CPU API frames and controller ticks are explicit;
no file payload memcpy, synthetic progress completion or processor resets
between CPU calls. This is an original-instruction probe, not yet C linkage.
"""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_bios_transport_cpu as cpu
import check_biwn_movie_source_overlay_AV as overlay
ROOT=cpu.ROOT;media=cpu.media;save=cpu.save;sha=cpu.sha
class Runtime(cpu.Runtime):
    def reset(self,ram,seed):
        super().reset(ram,seed)
        b=c.create_string_buffer(200000);n=self.core.GPUStateSave(b);raw=bytearray(b.raw[:n]);bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();raw[0x50:0x130]=bios[0x84a6+0xea:0x84a6+0x1ca];raw[0x10:0x1c]=bytes.fromhex('981e305c00f0d3c0e400e400');regs=[(seed*101+i*73)&0xffffffff for i in range(64)];regs[31]=0xf04000
        struct.pack_into('=64I',raw,4139,*regs);struct.pack_into('=I',raw,4096,0xf031ce);struct.pack_into('=I',raw,4112,0x20);struct.pack_into('=I',raw,4128,1);raw[4136:4139]=bytes([0,0,0]);raw[4395]=0
        assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
    def cpu_call(self,target):
        # Push declared host API frame on current CPU, without resetting it.
        stack=self.core.m68k_get_reg(None,15)-4;self.device.direct(stack,4,media.STOP);self.core.m68k_set_reg(15,stack);self.core.m68k_set_reg(16,target)
        for _ in range(1000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==media.STOP:return self.cpu()
            assert pc in self.rows,hex(pc)
            if pc in cpu.POLLS:self.tick()
            self.core.m68k_execute(1)
        raise AssertionError('Retained CPU API call limit')
def main():
    proof=json.loads((ROOT/'verification/bios-transport-CPU-checks.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'bios-transport-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-native-CD-stream'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    runtime=Runtime(Path(proof['directory'])/'libbios-transport.dylib',mapping['instructions_decoded']);runtime.prequeue=0;runtime.initial_progress=0;core=runtime.core;core.GPUExec.argtypes=[c.c_int];core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUGetPC.restype=c.c_uint32
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();ram=bytearray(0x200000);ram[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram[0x3074:0x3078]=(0xf03050).to_bytes(4,'big');ram[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');results=[]
    try:
        for case,count in enumerate([64,4096]):
            state=media.CPU();state.registers[:]=[case*19+i*71 for i in range(16)];state.registers[0]=0x023a1b;state.registers[8]=0x1c0000;state.registers[9]=0x1c0000+count;state.registers[15]=0x1ff000;state.ssp=0x1ff000;state.usp=0x180000;state.sr=0x2700;state.pc=0x303c
            save(out/'status.json',dict(status='running',case=case));runtime.native(bytes(ram),state,case,set());events=[];steps=0
            for tick in range(100000):
                core.BUTCHExec(0)
                if core.GPUGetPC()!=0xf031ce:
                    pcs=[]
                    for _ in range(200):
                        pc=core.GPUGetPC()
                        if pc==0xf031ce:break
                        assert 0xf03010<=pc<0xf0312e,hex(pc);pcs.append(pc);core.GPUExec(1);steps+=1
                    else:raise AssertionError('GPU stream event budget')
                    progress=runtime.cpu_call(0x304e);events.append(dict(tick=tick,PC_trace=pcs,A0=progress.registers[8],A1=progress.registers[9],GPU_SHA256=sha(overlay.video.gpu_state(core)[0][:4396])))
                    if progress.registers[8]>=0x1c0000+count:break
            else:raise AssertionError(('Stream bound',hex(core.GPUGetPC()),hex(core.GPUReadLong(0xf03050,6)),len(events)))
            runtime.cpu_call(0x3042);payload=runtime.device.ram()[0x1c0000:0x1c0000+count];(out/f'case-{case}-payload.bin').write_bytes(payload);save(out/f'case-{case}-events.json',events)
            results.append(dict(case=case,count=count,ticks=tick+1,interrupts=len(events),GPU_steps=steps,final_A0=hex(progress.registers[8]),final_A1=hex(progress.registers[9]),payload_sha256=sha(payload),payload_prefix=payload[:32].hex(),CPU=media.scheduler.cpu_dict(runtime.cpu()),hardware=runtime.snapshot()['hardware']));save(out/'cases.json',results)
        report=dict(status='original_source_CPU_BUTCH_GPU_FIFO_stream_progress_stop_completed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=results,C_linkage_verified=False,file_payload_delivery_or_scripted_progress=False,source_CPU303C_304E_3042=True,source_GPU_CD_ISR=True,CDROM_timing_extension_compared=False,whole_game_complete=False,limits=['Hostloaded BIOS/GPU descriptor code and declared initial CPU/GPU/device seed plus private API return frames. CPU SR2700 masks external interrupts.','One external BUTCH tick per loop; original controller IRQ delivery enters GPU handler. No full firmware boot/global scheduling/C linked comparison/game asset alignment proof.','Caller stops I2S after progress crosses end; source GPU32bytegranularity may write beyond requested interval. Buffer padding/caller limits not yet proved.']);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/native-CD-stream-probe.json',report);print(json.dumps(report))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()

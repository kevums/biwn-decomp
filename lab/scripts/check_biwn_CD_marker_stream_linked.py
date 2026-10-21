"""Actual CPU303C/304E/3042 and GPU IRQ1/FIFO linkage, without payload delivery scripts."""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import probe_biwn_native_CD_stream as native
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import Bus,W16
ROOT=native.ROOT;media=native.media;save=native.save;sha=native.sha
class Runtime(native.Runtime):
    def __init__(self,*args):
        self.path='native';self.C_GPU=None
        super().__init__(*args);self.GPU_run=self.lib.biwn_gpu_cd_marker_ISR_run;self.GPU_run.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32,c.c_uint32];self.GPU_run.restype=c.c_int;self.GPU_event=self.lib.biwn_gpu_cd_marker_ISR_assert;self.GPU_event.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State)];self.GPU_event.restype=c.c_int;self.gpu_counter=c.c_uint32.in_dll(self.core,'gpu_exec_opcode_count')
        self.coverage=set();self.GPU_trace=[];self.GPU_callbacks=[gpu.R16(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(self.core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(self.core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(lambda _,pc:self.GPU_trace.append(pc))];self.GPU_bus=Bus(*self.GPU_callbacks,None)
    def reset(self,ram,seed):
        self.C_GPU=None;super().reset(ram,seed);b=c.create_string_buffer(200000);n=self.core.GPUStateSave(b);raw=bytearray(b.raw[:n]);bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();raw[0x50:0x1a0]=bios[0x84a6+0x382:0x84a6+0x4d2];raw[0x10:0x1c]=bytes.fromhex('981e306400f0d3c0e400e400');assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==n;self.shadow_template=bytes(raw)
        if self.path=='C':self.C_GPU=gpu.state_from_raw(self.shadow_template)
    def read(self,a,w):
        if self.C_GPU is not None and 0xf03000<=a<=0xf04000-w:
            v=int.from_bytes(bytes(self.C_GPU.local_RAM[a-0xf03000:a-0xf03000+w]),'big');self.observe(0,a,w,v);return v
        return super().read(a,w)
    def write(self,a,w,v):
        if self.C_GPU is not None and 0xf03000<=a<=0xf04000-w:
            self.C_GPU.local_RAM[a-0xf03000:a-0xf03000+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
        return super().write(a,w,v)
    def translated_call(self,state):
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8]
        def rd(w):
            def f(_,a,v):v[0]=self.read(a,w);return 0
            return f
        def wr(w):
            def f(_,a,v):self.write(a,w,v);return 0
            return f
        callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4)),types[5](wr(1))];bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,passed,cpu,target):
            assert target==0x3712,hex(target);return self.mode_body(passed,cpu,callbacks[5],cb,None,100000,0)
        cb=media.world_cpu.SERVICE(service);assert self.mode_call(c.byref(bus),c.byref(state),callbacks[5],cb,None,100000,0)==0;return state
    def C_cpu_call(self,state,target):
        state.registers[15]-=4;state.ssp=state.registers[15];self.device.direct(state.registers[15],4,media.STOP);state.pc=target;return self.translated_call(state)
    def snapshot(self):
        s=super().snapshot()
        if self.path=='C':raw=gpu.logical(self.C_GPU)
        else:raw=native.overlay.video.gpu_state(self.core)[0][:4396]
        s['hardware']['GPU']=dict(size=4396,sha256=sha(raw));return s
    def gpu_event(self):
        if self.path=='native':
            pcs=[];delays=0;code=c.string_at(self.core.GPUGetRAM(),4096)
            for _ in range(500):
                pc=self.core.GPUGetPC()
                if pc==0xf031ce:break
                pcs.append(pc);self.coverage.add(pc);opcode=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if opcode>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1;self.coverage.add(pc+2)
            else:raise AssertionError('Native IRQ budget')
            return pcs,len(pcs)+delays
        self.GPU_trace.clear();before=self.C_GPU.instructions;counter=self.gpu_counter.value
        assert self.GPU_event(c.byref(self.GPU_bus),c.byref(self.C_GPU))==0
        assert self.GPU_run(c.byref(self.GPU_bus),c.byref(self.C_GPU),500,0xf031ce)==0
        assert self.gpu_counter.value==counter
        # Mirror owned logical state to the shared MMIO/IRQ shadow. Pipeline
        # tail is a declared initial fixture; no original instructions run.
        raw=bytearray(self.shadow_template);raw[:4396]=gpu.logical(self.C_GPU);assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
        return list(self.GPU_trace),self.C_GPU.instructions-before
    def stream(self,ram,state,case,path):
        self.path=path;counter=self.gpu_counter.value
        if path=='native':self.native(ram,state,case,set());cpu=self.cpu()
        else:self.reset(ram,case);cpu=media.CPU.from_buffer_copy(bytes(state));self.translated_call(cpu)
        events=[];end=state.registers[9]
        for tick in range(500000):
            self.core.BUTCHExec(0)
            if self.core.GPUReadLong(0xf02100,3)&8:
                pcs,instructions=self.gpu_event();cpu=self.cpu_call(0x304e)if path=='native'else self.C_cpu_call(cpu,0x304e)
                events.append(dict(tick=tick,PC_trace=pcs,instructions=instructions,CPU=media.scheduler.cpu_dict(cpu),hardware=self.snapshot()['hardware'],RAM=sha(self.device.ram())))
                if cpu.registers[8]>end:break
        else:raise AssertionError(('Linked stream limit',path,len(events),hex(self.core.GPUGetPC())))
        cpu=self.cpu_call(0x3042)if path=='native'else self.C_cpu_call(cpu,0x3042)
        if path=='C':assert self.gpu_counter.value==counter
        return dict(ticks=tick+1,events=events,CPU=media.scheduler.cpu_dict(cpu),hardware=self.snapshot()['hardware'],RAM=sha(self.device.ram()))
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);cpu_map=json.loads((session/'bios-transport-fullCPU-generation.json').read_text());gpu_map=json.loads((session/'GPU-CD-marker-ISR-C-generation.json').read_text());out=ROOT/'verification/BIWN-CD-marker-stream-linked'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_transport_cpu.c','biwn_media_setup_cpu.c','biwn_gpu_cd_marker_ISR.c'];library=out/'libCD-stream.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    runtime=Runtime(library,cpu_map['instructions_decoded']);runtime.prequeue=0;runtime.initial_progress=0;core=runtime.core;core.GPUExec.argtypes=[c.c_int];core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUGetPC.restype=c.c_uint32
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();ram=bytearray(0x200000);ram[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram[0x3074:0x3078]=(0xf03050).to_bytes(4,'big');ram[0x3072]=255;ram[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');results=[]
    try:
        for case,(count,packed,expected_asset_sha) in enumerate([(4096,0x023217,None),(1032192,0x023217,'52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453')]):
            initial=media.CPU();initial.registers[:]=[case*19+i*71 for i in range(16)];initial.registers[0]=packed;initial.registers[1]=0x53545542;initial.registers[2]=0;initial.registers[8]=0x4000;initial.registers[9]=0x4000+count;initial.registers[15]=0x1ff000;initial.ssp=0x1ff000;initial.usp=0x180000;initial.sr=0x2700;initial.pc=0x303c;observed={};RAM={}
            for path in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,path=path));observed[path]=runtime.stream(bytes(ram),initial,case,path);RAM[path]=runtime.device.ram();save(out/f'case-{case}-{path}.json',observed[path]);(out/f'case-{case}-{path}-RAM.bin').write_bytes(RAM[path]);(out/f'case-{case}-{path}-payload.bin').write_bytes(RAM[path][0x4000:0x4000+count])
            if observed['native']!=observed['C']or RAM['native']!=RAM['C']:save(out/'mismatch.json',observed);raise AssertionError(str(out/'mismatch.json'))
            if expected_asset_sha:assert sha(RAM['C'][0x4000:0x4000+count])==expected_asset_sha
            results.append(dict(case=case,count=count,packed_binary_MSF=packed,matched_existing_startup_asset_sha256=expected_asset_sha,ticks=observed['C']['ticks'],interrupts=len(observed['C']['events']),payload_sha256=sha(RAM['C'][0x4000:0x4000+count]),CPU=observed['C']['CPU'],full_CPU_GPU_RAM_controller_timing_extension_peripherals_events_match=True));save(out/'cases.json',results)
        selected={r['address']for r in gpu_map['instructions_decoded']};prior=json.loads((ROOT/'verification/GPU-CD-marker-ISR-checks.json').read_text());combined=(selected-set(prior['uncovered_PC']))|runtime.coverage
        report=dict(status='actual_CPU_BUTCH_GPU_FIFO_progress_stop_linked_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),payload_counts=[4096,1032192],CDROM_timing_extension_compared=True,file_payload_delivery_or_scripted_progress=False,source_CPU303C_304E_3042=True,source_GPU_CD_ISR=True,original_CPU_GPU_instructions_on_C_path=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,game_asset_integration_verified=False,linked_GPU_instruction_coverage=[len(selected&runtime.coverage),len(selected)],combined_GPU_instruction_coverage=[len(selected&combined),len(selected)],linked_native_GPU_coverage=sorted(runtime.coverage),stage_payload_sha256=results[-1]['payload_sha256'],caller_poll_end_strictly_greater=True,marker=hex(0x53545542),marker_run_words=16,packed_binary_MSF=hex(0x023217),game180000_caller_executed=False,limits=['Hostloaded BIOS/GPU code,declared CPU/GPU/device seed and host API frames,CPU SR2700. Actual source calls and controller IRQ1/FIFO drive transfers; no intermediate CPU/GPU reset or payload memcpy.','One external controller tick per loop; shared pinned CDI normalization/IRQ device model. Owned C logical GPU state mirrored to MMIO shadow; pipeline tail remains supplied. Physical/global scheduling and firmware boot unverified.','Marker3060 handler/D2=0 patch mode/STUB16-long synchronization; source32bytegranularity overshoots supplied end. Game caller/asset integration,padding,patched variants,globaltiming/playability unverified.']);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/CD-marker-stream-linked-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()

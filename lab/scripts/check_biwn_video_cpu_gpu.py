"""Native CPU/GPU versus source C relocation/video/STOP/IRQ/RTE and C GPU.

Host supplies actual video samples and GPU/CPU alternation at STOP. Native
path executes original instructions; C path executes none of either core.
"""
import ctypes as c,json,os,struct,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
from check_biwn_movie_GPU import State,Bus as GPUBus,R8,R16,R32,W32,OBS,state_from_raw,logical
from probe_biwn_gpu_projection import gpu_state
from extract_biwn_stage import swap16
ROOT=media.ROOT;save=media.save;sha=media.sha;STOP=0x190000

class Runtime(media.Runtime):
    def __init__(self,library,CPU_rows):
        super().__init__(library,CPU_rows);self.video=self.lib.biwn_video_cpu_call;self.body_video=self.lib.biwn_video_cpu_body
        for fn in [self.video,self.body_video]:fn.argtypes=self.fn.argtypes;fn.restype=c.c_int
        self.stop=self.lib.biwn_video_cpu_stop;self.stop.argtypes=[c.POINTER(media.CPU)];self.stop.restype=c.c_int
        self.interrupt=self.lib.biwn_video_cpu_GPU_interrupt;self.interrupt.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.interrupt.restype=c.c_int
        self.reloc=self.lib.biwn_movie_relocation_GPU_run;self.draw=self.lib.biwn_movie_sequence_GPU_run
        for fn in [self.reloc,self.draw]:fn.argtypes=[c.POINTER(GPUBus),c.POINTER(State),c.c_uint32];fn.restype=c.c_int
        core=self.core;core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
        core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16;core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
        core.TOMSetPendingGPUInt.argtypes=[];core.TOMIRQEnabled.argtypes=[c.c_int];core.TOMIRQEnabled.restype=c.c_int
        self.gpu_counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');self.gpu=None;self.mode='native';self.pending_init=False;self.C_CPU=None;self.C_stopped=False
        self.gpu_trace=hashlib.sha256();self.gpu_blocks=0;self.gpu_calls=[];self.errors=[];self.C_original_CPU_attempts=0;self.gpu_controls=[];self.native_coverage=set()
        self.original_execute=core.m68k_execute
        def execute(cycles):
            if self.mode=='C':self.C_original_CPU_attempts+=1;raise AssertionError('Original CPU forbidden on C path')
            return self.original_execute(cycles)
        core.m68k_execute=execute
        CPU_types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8]
        def rd(w):
            def cb(_,a,v):
                try:v[0]=self.read(a,w);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        def wr(w):
            def cb(_,a,v):
                try:self.write(a,w,v);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        self.callbacks=[CPU_types[0](rd(1)),CPU_types[1](rd(2)),CPU_types[2](rd(4)),CPU_types[3](wr(2)),CPU_types[4](wr(4)),CPU_types[5](wr(1))];self.bus=media.Bus(*self.callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,bus,cpu,target):
            if target==0x229f4:return self.body_video(bus,cpu,self.callbacks[5],self.service,None,200000,1)
            self.errors.append('Unimplemented video helper '+hex(target));return 1
        self.service=media.world_cpu.SERVICE(service)
        def gpu_rd(w):
            def cb(_,a,v):v[0]=core.JaguarReadByte(a,3) if w==1 else core.GPUReadWord(a,3) if w==2 else core.GPUReadLong(a,3);return 0
            return cb
        def gpu_wr(_,a,v):
            if a>=0xf00000:self.gpu_controls.append([hex(a),hex(v),self.C_stopped,hex(self.C_CPU.pc) if self.C_CPU is not None else None])
            # Publish the C-owned stopped state to the shared device event
            # semantics. The original core CPU shadow is deliberately not
            # stopped, so its GPUWriteLong would defer this signal; suppress
            # that shadow event and perform the same pending-GPU transition.
            core.GPUWriteLong(a,v&~2 if a==0xf02114 and self.C_stopped else v,3)
            if a==0xf02114 and v&2 and self.C_stopped:
                assert core.TOMIRQEnabled(1)
                core.TOMSetPendingGPUInt()
                result=self.interrupt(c.byref(self.bus),c.byref(self.C_CPU))
                self.gpu_controls.append(['IRQ',result,hex(self.C_CPU.pc),hex(self.C_CPU.sr)])
                assert result==0
                self.C_stopped=False
            return 0
        def observer(_,pc):self.gpu_trace.update(struct.pack('>I',pc));self.gpu_blocks+=1
        self.gpu_callbacks=[R8(gpu_rd(1)),R16(gpu_rd(2)),R32(gpu_rd(4)),W32(gpu_wr),OBS(observer)];self.gpu_bus=GPUBus(*self.gpu_callbacks,None)
    def read(self,a,w):
        if self.mode=='C' and self.pending_init and a==0xf039ec:
            self.run_C_GPU(True);self.pending_init=False
        if self.mode=='C' and self.gpu is not None and 0xf03000<=a<=0xf04000-w:
            value=int.from_bytes(bytes(self.gpu.local_RAM[a-0xf03000:a-0xf03000+w]),'big');self.observe(0,a,w,value);return value
        return super().read(a,w)
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode!='C' or self.gpu is None:return
        if 0xf03000<=a<=0xf04000-w:self.gpu.local_RAM[a-0xf03000:a-0xf03000+w]=v.to_bytes(w,'big')
        if a==0xf02110 and w==4:self.gpu.pc=v
        if a==0xf02114 and w==4:
            self.gpu.control=(self.gpu.control&0xf7c0)|(v&~0xf7c6)
            if v&1 and self.gpu.pc==0xf03258:self.pending_init=True
    def run_C_GPU(self,initialize=False):
        self.gpu_trace=hashlib.sha256();self.gpu_blocks=0;count=self.gpu_counter.value;old=self.gpu.instructions
        status=(self.reloc if initialize else self.draw)(c.byref(self.gpu_bus),c.byref(self.gpu),1000000)
        assert status==0,(status,hex(self.gpu.pc));assert self.gpu_counter.value==count
        c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096)
        self.gpu_calls.append(dict(initialization=initialize,blocks=self.gpu_blocks,PC_sha256=self.gpu_trace.hexdigest(),instructions=self.gpu.instructions-old,logical_GPU_sha256=sha(logical(self.gpu))))
    def native_GPU(self,initialize=False):
        trace=hashlib.sha256();blocks=0;delays=0;code=c.string_at(self.core.GPUGetRAM(),4096)
        for _ in range(500000):
            pc=self.core.GPUGetPC()
            if blocks and pc==0xf032c8 and (initialize or self.core.GPUReadLong(0xf039f0,6)==0):break
            raw=c.string_at(self.core.GPUGetRAM(),4096) if initialize else code;word=int.from_bytes(raw[pc-0xf03000:pc-0xf03000+2],'big');trace.update(struct.pack('>I',pc));self.core.GPUExec(1);blocks+=1
            if word>>10 in [52,53] and self.core.GPUGetPC()!=pc+2:delays+=1
        else:raise AssertionError('Native video GPU bound')
        raw,state=gpu_state(self.core);self.gpu_calls.append(dict(initialization=initialize,blocks=blocks,PC_sha256=trace.hexdigest(),instructions=blocks+delays,logical_GPU_sha256=sha(raw[:4396])))
    def start(self,ram,seed,mode):
        self.mode=mode;self.gpu=None;self.pending_init=False;self.gpu_calls=[];self.errors=[];self.C_stopped=False;self.C_original_CPU_attempts=0
        self.reset(ram,seed);raw,state=gpu_state(self.core)
        if mode=='C':
            self.gpu=state_from_raw(raw)
            # Shared device model may queue CPU IRQs but never execute the
            # original CPU or create frames. C STOP/IRQ owns that transition.
            self.core.m68k_pulse_reset();self.core.m68k_set_reg(17,0x2700)
    def hardware(self):
        result=self.snapshot()['hardware'];result['GPU']=dict(size=4396,sha256=sha(logical(self.gpu) if self.mode=='C' else gpu_state(self.core)[0][:4396]))
        return result
    def call(self,entry,args,registers=None,sr=0x2000):
        initial=media.CPU();initial.registers[:]=(registers or [0]*15)+[0x1ff000];initial.ssp=0x1ff000;initial.usp=0x1fe000;initial.sr=sr;initial.pc=entry
        self.device.direct(0x1ff000,4,STOP)
        if args:c.memmove(self.device.pointer+0x1ff004,args,len(args))
        if self.mode=='native':
            self.seed_cpu(initial);steps=0
            for _ in range(1000000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:return self.cpu(),steps
                assert pc in self.rows,hex(pc);self.native_coverage.add(pc)
                if pc==0xd384 and self.core.GPUGetPC()!=0xf032c8:self.native_GPU(True)
                if pc==0x22a0e:
                    self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1);steps+=1
            raise AssertionError(('Native video CPU bound',hex(pc),hex(self.core.GPUGetPC()),hex(self.core.GPUReadLong(0xf039ec,6)),self.gpu_calls[:2]))
        self.C_CPU=initial;steps=0
        for _ in range(100):
            if self.C_CPU.pc==STOP:return self.C_CPU,steps
            status=self.video(c.byref(self.bus),c.byref(self.C_CPU),self.callbacks[5],self.service,None,1000000,1)
            if status==6:
                assert self.C_CPU.pc==0x22a0e
                assert self.stop(c.byref(self.C_CPU))==0;self.C_stopped=True;self.run_C_GPU(False)
                assert not self.C_stopped and self.C_CPU.pc==0xe7d4,(self.C_stopped,hex(self.C_CPU.pc),self.gpu_controls[-12:])
            else:assert status==0,(status,self.errors,hex(self.C_CPU.pc))
            if self.C_CPU.pc==0x22a12:self.gpu_controls.append(['RTE',hex(self.read(0xbd850,2)),hex(self.read(0xf000e0,2)),hex(self.C_CPU.registers[8])])
            steps+=1
        raise AssertionError('C video continuation bound')

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'video-fullCPU-generation.json').read_text())
    out=ROOT/'verification/BIWN-video-CPU-GPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libvideo-CPU-GPU.dylib'
    names=['biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/n) for n in names],'-o',str(library)];compiled=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=Runtime(library,mapping['instructions_decoded']);base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    # Frozen runtime RAM already contains the relocated source GPU image.
    # D340 startup must receive its canonical pre-relocation bytes.
    payload=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();base[0x21ea8:0x22770]=payload;base=bytes(base)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());results=[]
    try:
        with (session/'raw-tracks/track-04-raw.bin').open('rb') as stream:
            for case,message in enumerate(extraction['messages']):
                video=next(x for x in message['sample_records'] if not x['audio']);stream.seek(video['normalized_track_offset']);data=swap16(stream.read(video['bytes']))
                snapshots={}
                for mode in ['native','C']:
                    save(out/'status.json',dict(status='running',message=message['message_id'],mode=mode));runtime.start(base,case%3,mode);stages=[]
                    for entry,args in [(0xd340,b''),(0xe7aa,b'')]:
                        cpu,count=runtime.call(entry,args);stages.append(dict(entry=hex(entry),CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.hardware(),GPU_calls=list(runtime.gpu_calls)))
                    # Declared overlay reload/restart; source D3C6 dispatcher
                    # integration remains separate from this interface test.
                    payload=runtime.device.ram()[0x21ea8:0x22770];c.memmove(runtime.core.GPUGetRAM()+0x240,payload,len(payload))
                    runtime.core.GPUWriteLong(0xf02110,0xf03240,6);runtime.core.GPUWriteLong(0xf02114,1,6)
                    if mode=='C':runtime.gpu.local_RAM[0x240:0x240+len(payload)]=payload;runtime.gpu.pc=0xf03240;runtime.gpu.control|=1;runtime.run_C_GPU(True)
                    else:runtime.native_GPU(True)
                    c.memmove(runtime.device.pointer+0x1c0000,data,len(data));c.memset(runtime.device.pointer+0x1a0000,0,80640)
                    for entry,args in [(0x227a0,struct.pack('>HIII',1,0x1c0000,0xbd904,0)),(0x228d4,struct.pack('>IIIII',448,0x1a0000,0x1c0000,0xbd904,0))]:
                        cpu,count=runtime.call(entry,args);stages.append(dict(entry=hex(entry),CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.hardware(),GPU_calls=list(runtime.gpu_calls)))
                    snapshots[mode]=stages
                    assert not runtime.C_original_CPU_attempts
                if snapshots['native']!=snapshots['C']:
                    save(out/'mismatch.json',dict(case=case,native=snapshots['native'],C=snapshots['C'],errors=runtime.errors));raise AssertionError(str(out/'mismatch.json'))
                results.append(dict(message_id=message['message_id'],stages=snapshots['C'],original_CPU_and_GPU_instructions_on_C_path=0));save(out/'fixtures.json',results)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='source_CPU_relocation_video_STOP_IRQ_RTE_and_C_GPU_first_frames_native_match',directory=str(out),cases=len(results),CPU_generated_instructions=254,
            source_sha256={n:sha((source/n).read_bytes()) for n in ['biwn_video_cpu.c','biwn_video_cpu.h','biwn_movie_relocation_GPU.c','biwn_movie_relocation_GPU.h','biwn_movie_sequence_GPU.c','biwn_movie_sequence_GPU.h']},script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_or_GPU_instructions_on_C_path=False,source_STOP_IRQ_RTE_C=True,whole_game_complete=False,new_published_components=0,
            limits=['Six first real frames; host invokes source functions and supplies samples. Source overlay reload/start is a declared host event, not D3C6 resident dispatcher.',
                    'Both processors are C on rebuilt path; shared pinned peripheral bus. Compare fullCPU/RAM/logicalGPU/peripherals and GPUtrace/counts per stage; GPUopcode/pipeline microstate excluded.',
                    'No movie controller/firmware streaming/global scheduler/audio synchronization/physical timing/gameplay.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-video-CPU-GPU.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),cases=len(results))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()

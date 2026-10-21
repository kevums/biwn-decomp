"""Native/Unicorn/C movie controller over actual supplied FILM/STAB buffers.

Firmware calls are explicit seek/progress providers. Host delivery supplies
disc bytes, not validated BIOS DMA/seek timing. Video helpers fail explicitly.
"""
import ctypes as c
import hashlib,json,os,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_media_setup_cpu as media
import generate_biwn_movie_cpu as generator
from check_biwn_68000_slices import make_toc
from extract_biwn_stage import swap16
ROOT=generator.ROOT;CPU=media.CPU;Bus=media.Bus;W8=media.W8;STOP=media.STOP
save=media.save;sha=media.sha

class Runtime(media.Runtime):
    def __init__(self,library,rows):
        super().__init__(library,rows)
        self.movie_body=self.lib.biwn_movie_cpu_body;self.movie_call=self.lib.biwn_movie_cpu_call
        for f in [self.movie_body,self.movie_call]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
        self.poll=self.lib.biwn_input_poll_cpu_body;self.poll.argtypes=[c.POINTER(Bus),c.POINTER(CPU)];self.poll.restype=c.c_int
        self.queries=[];self.deliveries=[];self.progress=0;self.timer_reads=0;self.mode=''
        self.callbacks=[]
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,
               media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,W8]
        def rd(w):
            def cb(_,a,out):
                try:out[0]=self.read(a,w);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        def wr(w):
            def cb(_,a,v):
                try:self.write(a,w,v);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        self.callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4)),types[5](wr(1))]
        self.bus=Bus(*self.callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,bus,state,target):
            try:
                if target in [0x303c,0x304e]:self.bios(state.contents,target);return 0
                if target==0xe4c0:return self.poll(bus,state)
                if target in self.rows:return self.movie_body(bus,state,self.callbacks[5],self.service,None,200000,1)
                self.errors.append('Unimplemented helper '+hex(target));return 1
            except Exception as e:self.errors.append(repr(e));return 1
        self.service=media.world_cpu.SERVICE(service)

    def bios(self,s,target):
        self.queries.append(dict(target=hex(target),D0=s.registers[0],D1=s.registers[1],A0=s.registers[8],A1=s.registers[9]))
        if target==0x304e:s.registers[8]=self.progress
        # CD_read only records the requested ABI. Delivery occurs explicitly
        # between caller invocations, avoiding a claim of validated firmware.

    def read(self,a,w):
        if self.mode=='C' and a==0xbd852 and w==4 and self.timer_arm:
            self.timer_reads+=1
            if self.timer_reads==3:self.device.direct(a,4,1)
        return super().read(a,w)

    def start(self,ram,seed,mode):
        self.reset(ram,seed);self.queries=[];self.deliveries=[];self.progress=0x1c0000;self.mode=mode;self.timer_arm=False;self.timer_reads=0
        # The accepted source C loader initializes both comparisons; no DSP
        # program runs during this CPU-only parser/producer test.
        initial=CPU();initial.registers[15]=0x1fe000;initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.pc=0xe840;initial.sr=0x700
        self.device.direct(initial.registers[15],4,STOP)
        assert self.fn(c.byref(self.bus),c.byref(initial),self.callbacks[5],self.service,None,10000,0)==0

    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(200000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:return self.cpu(),steps
            if pc in [0x303c,0x304e]:
                state=self.cpu();self.bios(state,pc)
                self.core.m68k_set_reg(8,state.registers[8])
                value=self.device.read(pc,2);self.device.direct(pc,2,0x4e75)
                self.core.m68k_execute(1);self.device.direct(pc,2,value)
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
                self.core.m68k_execute(1)
            steps+=1
        raise AssertionError('Native movie bound')

    def run_C(self,s):
        status=self.movie_call(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,200000,1)
        assert status==0,(status,self.errors)
        return s,None

    def run_unicorn(self,s,coverage):
        engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        for a,z in [(0,0x200000),(0x800000,0x110000),(0xf00000,0x20000)]:engine.mem_map(a,z)
        engine.mem_write(0,self.device.ram());engine.reg_write(UC_M68K_REG_SR,s.sr)
        for reg,value in zip(media.REGS,s.registers):engine.reg_write(reg,value)
        for a in [0x303c,0x304e]:engine.mem_write(a,b'\x4e\x75')
        def code(cpu,pc,size,_):
            if pc in [0x303c,0x304e]:
                state=CPU.from_buffer_copy(bytes(s));state.registers[:]=[cpu.reg_read(r) for r in media.REGS];state.pc=pc;self.bios(state,pc);cpu.reg_write(UC_M68K_REG_A0,state.registers[8])
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
        def rd(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def wr(cpu,access,a,w,v,_):self.write(a,w,v)
        hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,rd);engine.hook_add(UC_HOOK_MEM_WRITE,wr)
        engine.emu_start(s.pc,STOP,count=200000,timeout=15000000);assert engine.reg_read(UC_M68K_REG_PC)==STOP
        result=CPU.from_buffer_copy(bytes(s));result.registers[:]=[engine.reg_read(r) for r in media.REGS];result.pc=STOP
        engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);result.sr=engine.reg_read(UC_M68K_REG_D7)&65535
        if result.sr&0x2000:result.ssp=result.registers[15]
        else:result.usp=result.registers[15]
        return result,None

    def sequence(self,base,message,initial,seed,mode,coverage):
        self.start(base,seed,mode);steps=[];phases=[]
        for phase in range(8):
            # Source state0 performs its TOC/MSF seek arithmetic. For later
            # parser states, supply the known mastered bytes as a fixture.
            if phase==1:
                address=0x1c0000;data=message['stream_fixture']
                c.memmove(self.device.pointer+address,data,len(data));self.progress=address+len(data)
                self.device.direct(0xbd848,4,self.progress)
                self.deliveries.append(dict(address=address,bytes=len(data),sha256=sha(data),phase=phase))
            if phase==4:
                self.timer_arm=True;self.timer_reads=0
            s=CPU.from_buffer_copy(bytes(initial));s.pc=0xd4a8;self.device.direct(s.registers[15],4,STOP)
            self.trace=hashlib.sha256();self.trace_count=0;self.bus_events=[]
            self.mode=mode
            if mode=='native':result,count=self.run_native(s,coverage)
            elif mode=='Unicorn':result,count=self.run_unicorn(s,coverage)
            else:result,count=self.run_C(s)
            self.timer_arm=False
            phases.append(dict(phase=phase,state=self.device.read(0xbd85c,2),CPU=media.scheduler.cpu_dict(result),
                RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],ordered_bus_sha256=self.trace.hexdigest(),ordered_bus_events=self.trace_count))
            steps.append(count)
        pointer=self.core.DSPReadLong(0xf1b13c,6);length=self.core.DSPReadLong(0xf1b138,6)
        assert length==message['first_audio_length'] and self.device.ram()[pointer:pointer+length]==message['first_audio_data']
        assert [p['state'] for p in phases]==[1,2,3,4,5,6,7,7]
        return dict(phases=phases,queries=self.queries,deliveries=self.deliveries,pointer=pointer,length=length,CPU_steps=sum(x or 0 for x in steps)),self.device.ram()

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'movie-fullCPU-generation.json').read_text());setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    poll=generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    rows=mapping['instructions_decoded']+setup['instructions_decoded']+poll
    out=ROOT/'verification/BIWN-movie-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovie.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in ['biwn_movie_cpu.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c']],'-o',str(library)]
    compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    runtime=Runtime(library,rows);runtime.core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];runtime.core.DSPReadLong.restype=c.c_uint32
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());raw_path=session/'raw-tracks/track-04-raw.bin'
    message_markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();layout=json.loads((session/'cdi-layout.json').read_text());toc=make_toc(layout)
    rng=random.Random(0xd3fcd4a8);results=[];native_coverage=set();uc_coverage=set()
    try:
        for message in extraction['messages']:
            start=message['FILM_normalized_track_offset']-64
            with raw_path.open('rb') as f:f.seek(start);data=swap16(f.read(0x20000))
            assert data[:64]==struct.pack('>I',message_markers[message['message_id']])*16 and data[64:68]==b'FILM'
            audio=Path(message['first_chunk_path']).read_bytes();message={**message,'stream_fixture':data,'first_audio_length':len(audio),'first_audio_data':audio}
            for sup in [False,True]:
                case=len(results);save(out/'status.json',dict(status='running',case=case,message=message['message_id'],supervisor=sup))
                initial=CPU();initial.registers[:]=[rng.getrandbits(32) for _ in range(15)]+[0x1ff000 if sup else 0x1fe000];initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x2700 if sup else 0x700
                ram=bytearray(base);ram[0x2c00:0x2c00+len(toc)]=toc
                for address,value in [(0xbd884,0x1c0000),(0xbd888,0x1ffc00),(0xbd890,3),(0xbd894,message['message_offset']),(0xbd8ac,message_markers[message['message_id']]),(0xbd880,0x802000),(0xbd852,0),(0x47b84,0x22002000)]:ram[address:address+4]=value.to_bytes(4,'big')
                ram[0xbd85c:0xbd85e]=bytes(2);ram=bytes(ram)
                native,left=runtime.sequence(ram,message,initial,case%3,'native',native_coverage)
                independent,middle=runtime.sequence(ram,message,initial,case%3,'Unicorn',uc_coverage)
                rebuilt,right=runtime.sequence(ram,message,initial,case%3,'C',set())
                for i,(a,b,z) in enumerate(zip(native['phases'],independent['phases'],rebuilt['phases'])):
                    keys=['state','CPU','RAM','hardware']
                    if any(a[k]!=z[k] or b[k]!=z[k] for k in keys) or any(b[k]!=z[k] for k in ['ordered_bus_sha256','ordered_bus_events']):
                        save(out/'mismatch.json',dict(case=case,phase=i,native=a,Unicorn=b,C=z,errors=runtime.errors));raise AssertionError(str(out/'mismatch.json'))
                assert left==middle==right and native['queries']==independent['queries']==rebuilt['queries'] and native['deliveries']==rebuilt['deliveries']
                results.append(dict(case=case,message=message['message_id'],supervisor=sup,native=native,Unicorn=independent,C=rebuilt,source_sample_matches_extracted_bytes=True))
                save(out/'fixtures.json',results)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='actual_FILM_STAB_source_CPU_parser_and_first_audio_producer_native_Unicorn_C_match',directory=str(out),
            cases=len(results),states_per_case=8,source_movie_instruction_coverage=[len(native_coverage&set(r['address'] for r in mapping['instructions_decoded'])),mapping['instructions']],
            native_PC_coverage=sorted(native_coverage),Unicorn_PC_coverage=sorted(uc_coverage),source_sha256=mapping['source_sha256'],
            compiler=command,script_sha256=sha(Path(__file__).read_bytes()),native_CPU_steps=sum(x['native']['CPU_steps'] for x in results),
            matched=['Full CPU/SR/USP/SSP, whole main RAM and serialized GPU/DSP/TOM/JERRY/DAC plus cartridge retention after all eight source state dispatches.',
                     'Unicorn/C ordered data-bus reads/writes, source helper/BIOS request ABI, host deliveries and first E902 DSP sample pointer/length/bytes.'],
            BIOS_provider_actual_firmware=False,movie_video_helpers_executed=False,DSP_sample_engine_executed=False,full_movie_playback_verified=False,whole_game_complete=False,new_published_components=0,
            limits=['Host supplies 128KB of actual mastered bytes between state0/1; seek/progress firmware is a declared ABI provider, not a physical/native BIOS witness. Source state4 gets a declared clock change after its third clock read.',
                    'First audio sample only; subsequent video/helpers, ring-buffer reload/wrap, complete dialogue, actual boot scheduling and unmasked physical hardware remain unverified. Direct TRAP0 caller path remains separate.'])
        assert native_coverage==uc_coverage
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-CPU.json',report);save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),cases=len(results),coverage=report['source_movie_instruction_coverage'])))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()

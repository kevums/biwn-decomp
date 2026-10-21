"""Complete source D3FC caller with queued file-backed disc and nominal clocks.

MSF requests map declared CDI track ranges, swap16, +2-byte word alignment.
DMA rate2x/352800Bps, source600unit video timeline and controlled SSI/VBI.
Not actual BIOS firmware/global scheduling/physical A-V verification.
"""
import ctypes as c,json,os,struct,subprocess,hashlib,argparse,wave
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_boot_exit_AV as source
import check_biwn_movie_controller_video as controller
import check_biwn_movie_controller_AV as AV
import check_biwn_full_video_cpu_gpu as video
ROOT=source.ROOT;media=source.media;save=source.save;sha=source.sha

class Disc:
    def __init__(self,session):
        self.layout=json.loads((session/'cdi-layout.json').read_text());self.tracks=[]
        for t in self.layout['tracks']:
            path=session/f'raw-tracks/track-{t["track"]:02d}-raw.bin';assert path.stat().st_size==t['raw_bytes']
            self.tracks.append((t['declared_start_lba']*2352,t['declared_start_lba']*2352+t['raw_bytes'],path.open('rb'),t['track']))
    def read(self,absolute,n):
        result=bytearray();spans=[]
        while n:
            start,end,f,track=next(x for x in self.tracks if x[0]<=absolute<x[1]);size=min(n,end-absolute);f.seek(absolute-start);raw=f.read(size);assert len(raw)==size
            assert not size&1 and not (absolute-start)&1
            result.extend(controller.swap16(raw));spans.append(dict(track=track,offset=absolute-start,bytes=size));absolute+=size;n-=size
        return bytes(result),spans
    def close(self):
        for _,_,f,_ in self.tracks:f.close()

class Runtime(source.Runtime):
    def __init__(self,*args,disc,out,frame_directory):
        super().__init__(*args);self.disc=disc;self.out=out;self.frame_directory=frame_directory;self.full_running=False;self.pending=None;self._in_clock=False
        self.vbi=self.lib.biwn_movie_VBI_event;self.vbi.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.vbi.restype=c.c_int
        self.core.TOMSetPendingVideoInt.argtypes=[]
        for name in ['DSPGetPC','DSPGetFlags','DSPGetControl','DSPGetReg']:getattr(self.core,name).restype=c.c_uint32
        self.core.DSPGetReg.argtypes=[c.c_int]
        self.previous_service=self.service
        def service(_,bus,cpu,target):
            try:
                if target==0xdc7c:return self.body(bus,cpu,self.callbacks[5],self.service,None,2000000,1)
                if self.full_running and target==0xd4a8:
                    self.before_dispatch(cpu.contents)
                    status=self.previous_service(_,bus,cpu,target)
                    if not status:self.after_dispatch(cpu.contents)
                    else:self.errors.append('D4A8 provider returned '+str(status)+' at '+hex(cpu.contents.pc)+' SP '+hex(cpu.contents.registers[15]))
                    return status
                status=self.previous_service(_,bus,cpu,target)
                if status:self.errors.append('Provider '+hex(target)+' returned '+str(status)+' at '+hex(cpu.contents.pc)+' SP '+hex(cpu.contents.registers[15]))
                return status
            except Exception as e:self.errors.append(repr(e));return 1
        self.service=media.world_cpu.SERVICE(service)
    def bios(self,s,target):
        self.queries.append(dict(target=hex(target),D0=s.registers[0],D1=s.registers[1],A0=s.registers[8],A1=s.registers[9]))
        if target==0x303c:
            d0=s.registers[0];lba=((d0>>16)&127)*60*75+((d0>>8)&255)*75+(d0&255)-150;dest=s.registers[8];end=s.registers[9];assert 0<=dest<end<=0x1ffc00
            data,spans=self.disc.read(lba*2352+2,end-dest)
            self.pending=dict(dest=dest,end=end,data=data,written=0,lba=lba,index=len(self.deliveries));self.progress=dest-4
            self.deliveries.append(dict(lba=lba,dest=hex(dest),end=hex(end),bytes=len(data),alignment=2,source_ranges=spans,source_sha256=sha(data)))
            s.registers[8]=dest-4
        elif target==0x304e:
            s.registers[8]=self.progress;s.registers[9]=0
    def advance_dma(self,ticks):
        p=self.pending
        if not p:return
        amount=min(len(p['data'])-p['written'],ticks*588);amount&=~1
        if amount:
            c.memmove(self.device.pointer+p['dest']+p['written'],p['data'][p['written']:p['written']+amount],amount);p['written']+=amount
        self.progress=(p['dest']-4+((p['written']+4)//32)*32) if p['written']<len(p['data']) else p['end']+28
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode!='C' or self.C_DSP is None or w!=4:return
        s=self.C_DSP
        if a==0xf1a110:s.pc=v
        elif a==0xf1a114:s.control=(s.control&0x1f7c0)|(v&~(0x1f7c0|6))
        elif a==0xf1a100:
            assert not v&0x4000;s.flags=(v&~8)|((s.flags&8) if v&8 else 0);s.z=s.flags&1;s.c=(s.flags>>1)&1;s.n=(s.flags>>2)&1;s.control&=~((s.flags&0x3e00)>>3);s.control&=~((s.flags&0x20000)>>1)
        elif a==0xf1a10c:s.data_organization=v
    def read(self,a,w):
        if self.full_running and a==0xf1a114 and w==4 and not self._in_clock:
            # Source E918 requests stop in shared DSP RAM, then pollsGO.
            dsp_raw=self.logical_DSP()
            if int.from_bytes(dsp_raw[0x140:0x144],'big') and (self.C_DSP.control&1 if self.mode=='C' else self.core.DSPGetControl()&1):self.sound_stream(1)
        if self.mode=='C' and self.C_DSP is not None and w==4:
            if a==0xf1a114:v=self.C_DSP.control;self.observe(0,a,w,v);return v
            if a==0xf1a110:v=self.C_DSP.pc;self.observe(0,a,w,v);return v
            if a==0xf1a100:
                s=self.C_DSP;s.flags=(s.flags&~7)|s.z|(s.c<<1)|(s.n<<2);v=s.flags&0xffffc1ff;self.observe(0,a,w,v);return v
        return super().read(a,w)
    def external_read8(self,a,out):
        try:
            out[0]=self.core.JaguarReadByte(a,2)
            if self.full_running:
                while self.audio_cursor<len(self.audio_tokens) and not self.audio_tokens[self.audio_cursor]['pointer']<=a<self.audio_tokens[self.audio_cursor]['pointer']+len(self.audio_tokens[self.audio_cursor]['data']):self.audio_cursor+=1
                assert self.audio_cursor<len(self.audio_tokens),('DSP address has no chronological queued audio token',hex(a))
                token=self.audio_tokens[self.audio_cursor];assert out[0]==token['data'][a-token['pointer']],('Queued source audio overwritten before C DSP read',token['sample'],hex(a))
                self.audio_reads+=1
            return 0
        except Exception as e:self.errors.append(repr(e));return 1
    def external_write32(self,a,v):
        if self.full_running:assert a in [0xf1a148,0xf1a14c],hex(a)
        return super().external_write32(a,v)
    def idle_native(self):
        pc=self.core.DSPGetPC()
        return not self.core.DSPGetControl()&1 or (pc==0xf1b074 and self.core.DSPGetReg(27)==0 and not self.core.DSPGetFlags()&8)
    def segment(self):
        if self.mode=='C':return super().segment()
        before=self.counter.value
        for _ in range(10000):
            pc=self.core.DSPGetPC()
            if (pc==0xf1b074 and self.core.DSPGetReg(27)==0 and not self.core.DSPGetFlags()&8) or (pc==0xf1b130 and not self.core.DSPGetControl()&1):return (self.counter.value-before)&0xffffffff
            self.core.DSPExec(1)
        raise AssertionError('Fast native DSP segment bound')
    def sound_stream(self,ticks):
        before_RAM=sha(self.device.ram()) if ticks else None
        self._in_clock=True
        try:
            for _ in range(ticks):
                self.core.DACWordStrobe();pair=AV.dsp.strobed_pair(self.dac());encoded=struct.pack('<hh',*pair);self.pcm.extend(encoded)
                if self.mode=='C':assert self.dsp_irq(c.byref(self.C_DSP))==0
                else:self.core.DSPSetIRQLine(1,1)
                instructions=self.segment()
                self.sound_digest.update(self.logical_DSP());self.sound_digest.update(self.dac());self.sound_digest.update(struct.pack('>I',instructions));self.sound_digest.update(encoded);self.word_clocks+=1
        finally:self._in_clock=False
        if ticks:assert sha(self.device.ram())==before_RAM, 'DSP wordclock block mutated main RAM'
    def source_vbi(self,cpu):
        self.core.TOMSetPendingVideoInt()
        if self.mode=='C':
            assert self.vbi(c.byref(self.bus),c.byref(cpu))==0 and cpu.pc==0xe7d4
            assert self.body_video(c.byref(self.bus),c.byref(cpu),self.callbacks[5],self.service,None,1000,1)==0
            assert cpu.pc==0xd4a8
        else:
            self.core.m68k_set_irq(2);self.core.m68k_execute(1)
            for _ in range(1000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0xd4a8:break
                if pc==0x304e:
                    state=self.cpu();self.bios(state,pc);self.core.m68k_set_reg(8,state.registers[8]);self.core.m68k_set_reg(9,state.registers[9]);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,old)
                else:assert pc in self.rows,hex(pc);self.native_coverage.add(pc);self.core.m68k_execute(1)
            else:raise AssertionError('Native VBI bound')
    def before_dispatch(self,cpu):
        state=self.device.read(0xbd85c,2);self.phase=state;self.sample=None;self.timer_arm=(state==4);self.timer_reads=0
        if state<=4:self.advance_dma(60)
        elif state==7:
            pointer=self.device.read(0xbd8e8,4);time=self.device.read(pointer+8,4)
            self.sample=self.message['sample_records'][self.sample_index]
            if time!=0xffffffff:
                time&=0x7fffffff;delta=max(0,time-self.timeline);self.advance_dma(delta);target=round(time*self.rate/600)
                self.sound_stream(max(0,target-self.word_clocks));self.timeline=time;self.device.direct(0xbd852,4,time)
        self.segment()  # source E840 may have restarted the program
        self.source_vbi(cpu)
    def after_dispatch(self,cpu):
        self.timer_arm=False;witness=None
        if self.phase==7:
            record=self.sample
            if record['audio']:
                raw=self.logical_DSP();length=int.from_bytes(raw[0x138:0x13c],'big');pointer=int.from_bytes(raw[0x13c:0x140],'big');data=self.device.ram()[pointer:pointer+length]
                assert length==record['bytes'] and sha(data)==record['sha256'],('audio sample',self.sample_index,length)
                self.audio_tokens.append(dict(pointer=pointer,data=data,sample=self.sample_index));witness=dict(audio=True,pointer=hex(pointer),bytes=length,sha256=sha(data));self.sound_stream(1)
            else:
                target=self.device.read(0xbd88c,4);frame=self.device.ram()[target:target+80640];expected=(self.frame_directory/f'message-{self.message["message_id"]}-frame-{self.video_index:03d}.CRY16').read_bytes();assert frame==expected,('video frame',self.video_index)
                witness=dict(audio=False,frame=self.video_index,sha256=sha(frame),destination=hex(target));self.video_index+=1
            self.sample_index+=1
        self.stages.append(dict(phase=self.phase,sample=self.sample_index-1 if witness else None,witness=witness,CPU=media.scheduler.cpu_dict(cpu),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],timeline=self.timeline,word_clocks=self.word_clocks,sound_digest=self.sound_digest.hexdigest(),GPU_calls=list(self.gpu_calls[self.last_GPU_call:])))
        self.last_GPU_call=len(self.gpu_calls)
        if len(self.stages)%30==0:print(json.dumps(dict(message=self.message['message_id'],mode=self.mode,dispatches=len(self.stages),samples=self.sample_index,frames=self.video_index)),flush=True)
        assert len(self.stages)<10000,('Source caller dispatch bound',self.phase,self.errors[-3:])
    def full_call(self,message,base,seed,mode):
        self.full_running=False;self.pending=None;self.start(base,seed,mode)
        # Existing startup probe entered movie mode; source exit returns to
        # resident readiness before D3FC makes its own source entry request.
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x1fe000;s.pc=0xd3ec;s.sr=0x2000;self.device.direct(s.registers[15],4,controller.STOP)
        self.run_native(s,set()) if mode=='native' else self.run_C(s);self.run_boot_exit('movie_exit');self.run_dispatch(True)
        self.message=message;self.rate=round(26590906/(64*(message['SCLK']+1)));self.timeline=0;self.sample_index=0;self.video_index=0;self.word_clocks=0;self.stages=[];self.audio_tokens=[];self.audio_cursor=0;self.audio_reads=0;self.pcm=bytearray();self.sound_digest=hashlib.sha256();self.last_GPU_call=len(self.gpu_calls)
        self.full_running=True
        initial=media.CPU();initial.registers[:]=[0]*15+[0x1fffe4];initial.ssp=0x1fffe4;initial.usp=0x1fe000;initial.sr=0x2000;initial.pc=0xd3fc
        self.device.direct(initial.registers[15],4,controller.STOP)
        args=struct.pack('>6I',3,message['message_offset'],0, message['marker'],224,0);c.memmove(self.device.pointer+initial.registers[15]+4,args,len(args))
        self.begin_CPU=initial;GPU_before=self.gpu_counter.value;DSP_before=self.counter.value
        result,steps=self.run_native(initial,self.native_coverage) if mode=='native' else self.run_C(initial)
        assert self.sample_index==len(message['sample_records']) and self.video_index==message['video_samples'],('Complete sample table',self.sample_index,len(message['sample_records']))
        assert self.device.read(0xbd85c,2)==0xffff and self.device.read(0xbd85e,2)==0 and self.device.read(0x47b82,2)==0
        self.run_boot_exit('movie_exit');self.run_dispatch(True)
        if mode=='C':assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        name=f'message-{message["message_id"]}-{mode}.wav'
        with wave.open(str(self.out/name),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(self.rate);w.writeframes(self.pcm)
        summary=dict(CPU=media.scheduler.cpu_dict(result),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],source_state=self.device.read(0xbd85c,2),samples=self.sample_index,frames=self.video_index,word_clocks=self.word_clocks,sound_digest=self.sound_digest.hexdigest(),PCM_sha256=sha(self.pcm),audio_enqueued=len(self.audio_tokens),queries=self.queries,deliveries=self.deliveries,final_GPU_calls=self.gpu_calls[self.last_GPU_call:])
        self.full_running=False
        return dict(summary=summary,stages=self.stages),dict(audio_reads=self.audio_reads,source_audio_tokens_reached=self.audio_cursor+1,wav=str(self.out/name))
    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(20000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==controller.STOP:return self.cpu(),steps
            if self.full_running and pc==0xd4a8:self.before_dispatch(self.cpu())
            if self.full_running and pc==0xd4de:self.after_dispatch(self.cpu())
            if pc in [0x3000,0x303c,0x304e]:
                state=self.cpu();self.bios(state,pc);self.core.m68k_set_reg(8,state.registers[8]);self.core.m68k_set_reg(9,state.registers[9]);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,old)
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if pc==0xd3d6 and 0xf031be<=self.core.GPUGetPC()<0xf03200:self.run_dispatch(False);assert self.core.GPUGetPC()==0xf03240;self.native_GPU(True)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
                if self.full_running and pc==0xe926:
                    raw=self.logical_DSP()
                    if int.from_bytes(raw[0x140:0x144],'big') and self.core.DSPGetControl()&1:self.sound_stream(1)
                if pc==0x22a0e:self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1)
            steps+=1
        raise AssertionError(('Native full movie caller bound',hex(pc)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--native-reference',type=Path);options=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0];geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text());boot_CPU=json.loads((session/'GPU-boot-fullCPU-generation.json').read_text())
    rows=boot_CPU['instructions_decoded']+sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-full-movie-caller'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfull-movie.dylib'
    previous=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(previous['source_sha256'])+['biwn_movie_VBI_event.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    disc=Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';runtime=Runtime(library,rows,*[m['instructions_decoded'] for m in mappings],disc=disc,out=out,frame_directory=frames)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=controller.make_toc(disc.layout);base[0x2c00:0x2c00+len(toc)]=toc
    results=[];coverage=set()
    try:
        for case,m in enumerate(extraction['messages'] if options.all else extraction['messages'][:1]):
            message={**m,'marker':markers[m['message_id']]};snapshots={};checks={}
            if options.native_reference:
                snapshots['native']=json.loads((options.native_reference/f'message-{m["message_id"]}-native.json').read_text());checks['native']={}
            for mode in (['C'] if options.native_reference else ['native','C']):
                save(out/'status.json',dict(status='running',message=m['message_id'],mode=mode));snapshot,check=runtime.full_call(message,bytes(base),case%3,mode);snapshots[mode]=snapshot;checks[mode]=check
                save(out/f'message-{m["message_id"]}-{mode}.json',snapshot)
                if mode=='native':coverage.update(runtime.native_coverage)
            if snapshots['native']!=snapshots['C']:
                save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],samples=len(m['sample_records']),audio_samples=m['audio_chunks'],video_frames=m['video_samples'],source_dispatches=len(snapshots['C']['stages']),word_clocks=snapshots['C']['summary']['word_clocks'],disc_requests=len(snapshots['C']['summary']['deliveries']),PCM_sha256=snapshots['C']['summary']['PCM_sha256'],C_checks=checks['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='complete_source_caller_match',frames=m['video_samples'])),flush=True)
        report=dict(status='complete_source_D3FC_movie_callers_native_C_match_under_queued_disc_and_declared_clocks',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),all_six=options.all,messages=results,frames=sum(x['video_frames'] for x in results),audio_samples=sum(x['audio_samples'] for x in results),source_CPU_coverage=[len(coverage&set(x['address'] for x in mappings[0]['instructions_decoded'])),mappings[0]['instructions']],native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),word_clocks=sum(x['word_clocks'] for x in results),source_dispatches=sum(x['source_dispatches'] for x in results),disc_requests=sum(x['disc_requests'] for x in results),whole_game_complete=False,BIOS_actual_firmware=False,physical_AV_synchronization=False,
            limits=['Source fullD3FC with renderer-ready0, repeatcount0, no cancellation/busyTRAP0 test. Source movie samples/arguments/pointers/endstate/audio-stop/exit are not host replaced.',
                    'File-backed MSF/LBA disc provider reads declaredrawtracks/swap16/+2alignment at352800Bps with bootstrap ticks; BIOS3000 no-op. No actualfirmware/timing claim.',
                    'Host nominal600unit video clock, sourceVBI progress handler and SCLK18 SSI clocks at dispatch boundaries; no global game schedule/physical scanout.',
                    'Source DSP audio pointer/bytes verified at every enqueue; everyC externalaudio byte checked against its chronological original disc token. FullCPU/RAM/GPU/DSP/peripherals and GPUtrace/counts perdispatch; allDSP/DAC/PCM/counts perwordclock in cumulative digest. Microstates excluded.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-full-movie-caller.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=report['frames'],audio_samples=report['audio_samples'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors[-5:]));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()

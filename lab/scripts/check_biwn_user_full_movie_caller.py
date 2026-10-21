"""Full source movie caller in user mode with actual privilege STOP/nested IRQ."""
import ctypes as c,json,os,struct,subprocess,argparse,wave,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_full_movie_caller as full
ROOT=full.ROOT;media=full.media;save=full.save;sha=full.sha;controller=full.controller;video=full.video;AV=full.AV;Disc=full.Disc
class Runtime(full.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.privilege=self.lib.biwn_movie_privilege_cpu_body;self.privilege.argtypes=self.fn.argtypes;self.privilege.restype=c.c_int
        self.privilege_exception=self.lib.biwn_movie_user_STOP_exception;self.privilege_exception.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.privilege_exception.restype=c.c_int
        self.privilege_stop=self.lib.biwn_movie_privilege_STOP_event;self.privilege_stop.argtypes=[c.POINTER(media.CPU)];self.privilege_stop.restype=c.c_int
        self.interrupt=self.lib.biwn_movie_wait_GPU_interrupt;self.interrupt.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.interrupt.restype=c.c_int
        self.vbi=self.lib.biwn_movie_user_VBI_event;self.vbi.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.vbi.restype=c.c_int
        self.user_previous_service=self.service
        def service(_,bus,cpu,target):
            if target in self.video_rows:
                saved=self.C_CPU;self.C_CPU=cpu.contents
                try:
                    for _ in range(100):
                        pc=cpu.contents.pc;fn=self.privilege if pc in [0xddfe,0xde02,0xde06,0x22a10] else self.body_video
                        status=fn(bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                        if status==6:
                            if cpu.contents.pc==0x22a0e:
                                if not cpu.contents.sr&0x2000:
                                    assert self.privilege_exception(bus,cpu)==0;continue
                                assert self.stop(cpu)==0
                            else:assert cpu.contents.pc==0xddfe and self.privilege_stop(cpu)==0
                            self.C_stopped=True;self.run_C_GPU(False);assert not self.C_stopped and cpu.contents.pc==0xe7d4;continue
                        if status:self.errors.append('User video provider '+hex(target)+' status '+str(status)+' PC '+hex(cpu.contents.pc));return status
                        if cpu.contents.pc in [0xde02,0x22a10,0x22a12]:continue
                        return 0
                    raise AssertionError('User privilege video continuation bound')
                except Exception as e:self.errors.append(repr(e));return 1
                finally:self.C_CPU=saved
            return self.user_previous_service(_,bus,cpu,target)
        self.service=media.world_cpu.SERVICE(service)
    def full_call(self,message,base,seed,mode):
        self.full_running=False;self.pending=None;self.start(base,seed,mode)
        # Existing startup probe entered movie mode; source exit returns to
        # resident readiness before D3FC makes its own source entry request.
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x1fe000;s.pc=0xd3ec;s.sr=0x2000;self.device.direct(s.registers[15],4,controller.STOP)
        self.run_native(s,set()) if mode=='native' else self.run_C(s);self.run_boot_exit('movie_exit');self.run_dispatch(True)
        self.message=message;self.rate=round(26590906/(64*(message['SCLK']+1)));self.timeline=0;self.sample_index=0;self.video_index=0;self.word_clocks=0;self.stages=[];self.audio_tokens=[];self.audio_cursor=0;self.audio_reads=0;self.pcm=bytearray();self.sound_digest=hashlib.sha256();self.last_GPU_call=len(self.gpu_calls)
        self.full_running=True
        initial=media.CPU();initial.registers[:]=[0]*15+[0x180fe4];initial.ssp=0x200000;initial.usp=0x180fe4;initial.sr=0;initial.pc=0xd3fc
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
                if pc==0x22a0e:
                    supervisor=bool(self.core.m68k_get_reg(None,17)&0x2000);self.core.m68k_execute(1);steps+=1
                    if supervisor:self.native_GPU(False)
                    continue
                if pc==0xddfe:self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1)
            steps+=1
        raise AssertionError(('Native full movie caller bound',hex(pc)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--native-reference',type=Path);options=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0];geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text());boot_CPU=json.loads((session/'GPU-boot-fullCPU-generation.json').read_text())
    privilege=json.loads((session/'movie-privilege-fullCPU-generation.json').read_text())
    rows=privilege['instructions_decoded']+boot_CPU['instructions_decoded']+sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-user-full-movie-caller'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfull-movie.dylib'
    previous=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(previous['source_sha256'])+['biwn_movie_VBI_event.c','biwn_movie_privilege_cpu.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
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
        report=dict(status='complete_user_source_D3FC_movie_callers_privilege_STOP_native_C_match_under_queued_disc_and_declared_clocks',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),all_six=options.all,messages=results,frames=sum(x['video_frames'] for x in results),audio_samples=sum(x['audio_samples'] for x in results),user_mode_caller=True,source_privilege_STOP_and_nested_IRQ_verified=True,source_CPU_coverage=[len(coverage&set(x['address'] for x in mappings[0]['instructions_decoded'])),mappings[0]['instructions']],native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),word_clocks=sum(x['word_clocks'] for x in results),source_dispatches=sum(x['source_dispatches'] for x in results),disc_requests=sum(x['disc_requests'] for x in results),whole_game_complete=False,BIOS_actual_firmware=False,physical_AV_synchronization=False,
            limits=['Source fullD3FC with renderer-ready0, repeatcount0, no cancellation/busyTRAP0 test. Source movie samples/arguments/pointers/endstate/audio-stop/exit are not host replaced.',
                    'File-backed MSF/LBA disc provider reads declaredrawtracks/swap16/+2alignment at352800Bps with bootstrap ticks; BIOS3000 no-op. No actualfirmware/timing claim.',
                    'Host nominal600unit video clock, sourceVBI progress handler and SCLK18 SSI clocks at dispatch boundaries; no global game schedule/physical scanout.',
                    'Source DSP audio pointer/bytes verified at every enqueue; everyC externalaudio byte checked against its chronological original disc token. FullCPU/RAM/GPU/DSP/peripherals and GPUtrace/counts perdispatch; allDSP/DAC/PCM/counts perwordclock in cumulative digest. Microstates excluded.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-user-full-movie-caller.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=report['frames'],audio_samples=report['audio_samples'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors[-5:]));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()

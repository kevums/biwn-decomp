"""Retained source CPU/GPU codebooks across every video sample in six movies.

Store raw frames and bounded new-code witnesses, not every instruction log
or whole-machine snapshot for every frame. Native outer PC order is hashed;
inline branch delays are counted separately from the GPU opcode counter.
"""
import ctypes as c,hashlib,json,struct,time,os,subprocess
from check_biwn_movie_GPU import State,Bus,R8,R16,R32,W32,OBS,state_from_raw,logical
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
from probe_biwn_gpu_projection import gpu_state
from extract_biwn_stage import swap16
ROOT=media.ROOT;save=media.save;sha=media.sha;STOP=0x190000

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text())
    relocation=json.loads((ROOT/'verification/BIWN-movie-GPU-original.json').read_text());before=(Path(relocation['directory'])/'before-GPU.bin').read_bytes();image=(Path(relocation['directory'])/'relocated-GPU.bin').read_bytes()[:4096]
    existing=json.loads((session/'media-video-gpu-21ea0/first-frames-C-generation.json').read_text());known={x['address'] for x in existing['instructions_decoded']}
    runtime=media.Runtime(Path(proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded']);core=runtime.core
    core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    out=ROOT/'verification/BIWN-movie-sequence-GPU-C'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'frames').mkdir();verifier=Verifier(runtime,core,out)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    observed={};commands=[];frames=[];witnesses=[];opcode_cache={};started=time.monotonic();current_message=None;current_frame=None
    def decoded(pc):
        if pc not in opcode_cache:
            off=pc-0xf03000;assert 0<=off<=4094,hex(pc);word=int.from_bytes(image[off:off+2],'big');size=6 if word>>10==38 else 2
            opcode_cache[pc]=(word>>10,size,image[off:off+size].hex())
        return opcode_cache[pc]
    def observe(pc,kind):
        op,size,data=decoded(pc)
        if pc not in observed:observed[pc]=dict(address=pc,size=size,bytes=data,direct=0,delay=0)
        observed[pc][kind]+=1
    def machine_save():
        n=core.retro_serialize_size();buf=c.create_string_buffer(n);assert core.retro_serialize(buf,n);return buf.raw
    def cpu_call(entry,args):
        initial=media.CPU();initial.registers[:]=[0]*15+[0x1ff000];initial.ssp=0x1ff000;initial.usp=0x1fe000;initial.sr=0x2000;initial.pc=entry
        runtime.device.direct(0x1ff000,4,STOP);c.memmove(runtime.device.pointer+0x1ff004,args,len(args));runtime.seed_cpu(initial)
        cpu_steps=0;irq_steps=0;command_ids=[]
        for _ in range(500000):
            pc=core.m68k_get_reg(None,16)
            if pc==STOP:return dict(CPU_steps=cpu_steps,IRQ_steps=irq_steps,command_ids=command_ids)
            assert 0x22780<=pc<0x22a18 or 0xe7aa<=pc<0xe822,hex(pc)
            cpu_steps+=1;irq_steps+=0xe7d4<=pc<0xe822
            if pc!=0x22a0e:core.m68k_execute(1);continue
            core.m68k_execute(1)
            index=len(commands);params=[core.GPUReadLong(0xf039f4+i*4,6) for i in range(8)];raw_in,state=gpu_state(core);ram_in=runtime.device.ram();machine=machine_save();cpu_in=media.scheduler.cpu_dict(runtime.cpu())
            trace=hashlib.sha256();blocks=0;delays=0;seen=set();start_counter=counter.value
            for __ in range(500000):
                gpc=core.GPUGetPC()
                if blocks and gpc==0xf032c8 and core.GPUReadLong(0xf039f0,6)==0:break
                op,size,data=decoded(gpc);observe(gpc,'direct');seen.add(gpc);trace.update(struct.pack('>I',gpc));core.GPUExec(1);blocks+=1
                after=core.GPUGetPC()
                if op in [52,53] and after!=gpc+2:observe(gpc+2,'delay');seen.add(gpc+2);delays+=1
            else:raise AssertionError('Sequence GPU bound')
            assert (counter.value-start_counter)&0xffffffff==blocks
            raw_out,state=gpu_state(core);ram_out=runtime.device.ram()
            # Observed source code must retain the relocated instruction
            # bytes; mutable mailboxes/data are not classified as code.
            for address in seen:
                _,size,data=decoded(address);assert raw_out[address-0xf03000:address-0xf03000+size].hex()==data,hex(address)
            verifier.verify(index,current_message,current_frame,raw_in,raw_out,ram_in,ram_out,machine,cpu_in,trace.hexdigest(),blocks,delays)
            new=sorted(seen-known)
            if new:
                stem=f'command-{index:04d}';target=out/'new-code-witnesses';target.mkdir(exist_ok=True)
                for suffix,data in [('before-machine',machine),('before-GPU',raw_in),('after-GPU',raw_out),('before-RAM',ram_in),('after-RAM',ram_out)]:
                    (target/f'{stem}-{suffix}.bin').write_bytes(data)
                witnesses.append(dict(stem=stem,command=index,message_id=current_message,frame=current_frame,new_PC=new,CPU_before=cpu_in,CPU_after_GPU_signal=media.scheduler.cpu_dict(runtime.cpu())))
                known.update(new)
            row=dict(index=index,message_id=current_message,frame=current_frame,CPU_entry=hex(entry),params=params,outer_PC_sha256=trace.hexdigest(),outer_instruction_blocks=blocks,mandatory_delay_instructions=delays,
                source_instructions=blocks+delays,logical_GPU_before_sha256=sha(raw_in[:4396]),logical_GPU_after_sha256=sha(raw_out[:4396]),RAM_before_sha256=sha(ram_in),RAM_after_sha256=sha(ram_out),CPU_after_GPU_signal=media.scheduler.cpu_dict(runtime.cpu()))
            commands.append(row);command_ids.append(index)
        raise AssertionError('Sequence CPU bound')
    try:
        with (session/'raw-tracks/track-04-raw.bin').open('rb') as stream:
            for case,message in enumerate(extraction['messages']):
                current_message=message['message_id'];videos=[x for x in message['sample_records'] if not x['audio']]
                runtime.reset(base,case%3)
                # DACStateLoad re-derives the resample ratio from SMODE/SCLK.
                # Start the declared fixture with that same coherent derived
                # value, rather than DACReset's provisional ratio=1. No GPU
                # audio writes are performed and no field is masked.
                # Use the public save/load path; the rate updater itself is
                # private to the pinned DAC implementation.
                verifier.restore(machine_save())
                buf=c.create_string_buffer(before);assert core.GPUStateLoad(buf)==len(before)
                for _ in range(20000):
                    if core.GPUGetPC()==0xf032c8:break
                    core.GPUExec(1)
                else:raise AssertionError('Sequence relocation bound')
                runtime.device.direct(0xbd84c,4,0x258);c.memset(runtime.device.pointer+0x1a0000,0,224*180*2);cpu_call(0xe7aa,b'')
                for number,video in enumerate(videos):
                    current_frame=number;save(out/'status.json',dict(status='running',message=current_message,frame=number,total_frames_done=len(frames),GPU_commands=len(commands),observed_instructions=len(observed)))
                    stream.seek(video['normalized_track_offset']);data=swap16(stream.read(video['bytes']));assert len(data)==video['bytes']
                    assert data[0] in [0,1] and (int.from_bytes(data[4:6],'big'),int.from_bytes(data[6:8],'big'))==(224,180)
                    c.memmove(runtime.device.pointer+0x1c0000,data,len(data))
                    book=cpu_call(0x227a0,struct.pack('>HIII',1,0x1c0000,0xbd904,0));assert runtime.device.read(0x1ff00e,4)==0
                    frame=cpu_call(0x228d4,struct.pack('>IIIII',448,0x1a0000,0x1c0000,0xbd904,0));assert runtime.device.read(0x1ff014,4)==0
                    pixels=runtime.device.ram()[0x1a0000:0x1a0000+224*180*2];path=out/'frames'/f'message-{current_message}-frame-{number:03d}.CRY16';path.write_bytes(pixels)
                    frames.append(dict(message_id=current_message,frame=number,header_flag=data[0],source=video,video_sha256=sha(data),pixels_sha256=sha(pixels),pixels_path=str(path),codebook=book,drawing=frame))
                    if number%20==0:print(json.dumps(dict(message=current_message,frame=number,total=len(frames),instructions_observed=len(observed),seconds=round(time.monotonic()-started,1))),flush=True)
                save(out/'frames.json',frames);save(out/'commands.json',commands);save(out/'observed-code.json',sorted(observed.values(),key=lambda x:x['address']));save(out/'new-code-witnesses.json',witnesses)
        assert len(frames)==763
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='all_six_movies_retained_C_GPU_video_sequences_match_original',directory=str(out),
            movies=6,frames=len(frames),key_frames=sum(x['header_flag']==0 for x in frames),delta_frames=sum(x['header_flag']==1 for x in frames),GPU_commands=len(commands),
            source_instructions=sum(x['source_instructions'] for x in commands),outer_instruction_blocks=sum(x['outer_instruction_blocks'] for x in commands),observed_code_instructions=len(observed),new_code_witnesses=len(witnesses),
            elapsed_seconds=time.monotonic()-started,script_sha256=sha(Path(__file__).read_bytes()),initial_DAC_ratio_derived_from_supplied_SMODE_SCLK=True,C_decoder_all_frames_verified=True,C_GPU_state_retained_between_commands=True,original_GPU_instructions_on_C_path=0,C_GPU_checks=verifier.summary(),CPU_video_wrappers_C_verified=False,whole_game_complete=False,new_published_components=0,
            limits=['Host supplies every video sample, preserving source GPU/codebook/pixel state between samples in each movie. Native CPU wrappers/STOP/IRQ/RTE execute; fixed destination/pitch and explicit CPU/GPU alternation.',
                    'No movie controller, disc firmware stream, audio/video synchronization, physical timing or full game. C GPU code matches at all command boundaries; native CPU wrappers and relocated GPU startup remain explicit reference providers.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-sequence-GPU-C.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=len(frames),commands=len(commands),observed_code=len(observed))))
    except Exception as e:
        save(out/'frames.json',frames);save(out/'commands.json',commands);save(out/'observed-code.json',sorted(observed.values(),key=lambda x:x['address']));save(out/'new-code-witnesses.json',witnesses);save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()




class Verifier:
    def __init__(self,runtime,core,out):
        self.runtime=runtime;self.core=core;self.out=out;self.state=None;self.message=None;self.rows=[];self.events=0
        (out/'C-frames').mkdir()
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        self.mapping=json.loads((session/'media-video-gpu-21ea0/sequence-C-generation.json').read_text())
        source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovie-sequence-GPU.dylib'
        command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_movie_sequence_GPU.c'),'-o',str(library)]
        p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        self.lib=c.CDLL(str(library));self.run=self.lib.biwn_movie_sequence_GPU_run;self.run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];self.run.restype=c.c_int
        core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
        core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
        core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
        core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');self.fail=None
        def rd(w):
            def cb(_,a,v):
                if self.fail==('read',w):return 1
                v[0]=core.JaguarReadByte(a,3) if w==1 else core.GPUReadWord(a,3) if w==2 else core.GPUReadLong(a,3);return 0
            return cb
        def wr(_,a,v):
            if self.fail==('write',4):return 1
            core.GPUWriteLong(a,v,3);self.events+=1;return 0
        def observe(_,pc):self.trace.update(struct.pack('>I',pc));self.blocks+=1
        self.callbacks=[R8(rd(1)),R16(rd(2)),R32(rd(4)),W32(wr),OBS(observe)];self.bus=Bus(*self.callbacks,None)
    def snapshot(self):
        n=self.core.retro_serialize_size();buf=c.create_string_buffer(n);assert self.core.retro_serialize(buf,n);return buf.raw
    def restore(self,data):
        buf=c.create_string_buffer(data);assert self.core.retro_unserialize(buf,len(data))
    def verify(self,index,message,frame,raw_in,raw_out,ram_in,ram_out,machine,cpu_in,PC_hash,blocks,delays):
        after_machine=self.snapshot();expected_cpu=media.scheduler.cpu_dict(self.runtime.cpu())
        expected_hw=self.runtime.snapshot()['hardware'];expected_hw.pop('GPU')
        if self.message!=message:
            self.state=state_from_raw(raw_in);self.message=message
        else:
            # Source CPU writes only the live argument/command mailbox.
            # Preserve every C-derived register/flag and all other GPU RAM.
            incoming=state_from_raw(raw_in)
            assert logical(self.state)[4096:]==logical(incoming)[4096:]
            assert bytes(self.state.local_RAM[:0x9f0])==bytes(incoming.local_RAM[:0x9f0])
            assert bytes(self.state.local_RAM[0xa18:])==bytes(incoming.local_RAM[0xa18:])
            self.state.local_RAM[0x9f0:0xa18]=incoming.local_RAM[0x9f0:0xa18]
        assert logical(self.state)==raw_in[:4396]
        self.restore(machine);assert self.runtime.device.ram()==ram_in
        assert media.scheduler.cpu_dict(self.runtime.cpu())==cpu_in
        self.trace=hashlib.sha256();self.blocks=0;count=self.counter.value;before=self.state.instructions
        status=self.run(c.byref(self.bus),c.byref(self.state),1000000)
        actual_ram=self.runtime.device.ram();actual_cpu=media.scheduler.cpu_dict(self.runtime.cpu());actual_hw=self.runtime.snapshot()['hardware'];actual_hw.pop('GPU')
        if status or actual_ram!=ram_out or logical(self.state)!=raw_out[:4396] or self.trace.hexdigest()!=PC_hash or self.blocks!=blocks or self.state.instructions-before!=blocks+delays or actual_cpu!=expected_cpu or actual_hw!=expected_hw:
            (self.out/'mismatch-C-GPU.bin').write_bytes(logical(self.state));(self.out/'mismatch-native-GPU.bin').write_bytes(raw_out)
            save(self.out/'mismatch.json',dict(index=index,message=message,frame=frame,status=status,GPU_diff=[hex(i) for i,(a,b) in enumerate(zip(logical(self.state),raw_out[:4396])) if a!=b][:30],RAM_diff=[hex(i) for i,(a,b) in enumerate(zip(actual_ram,ram_out)) if a!=b][:30],trace_match=self.trace.hexdigest()==PC_hash,C_instructions=self.state.instructions-before,expected=blocks+delays,CPU_match=actual_cpu==expected_cpu,hardware_match=actual_hw==expected_hw,expected_hardware=expected_hw,actual_hardware=actual_hw))
            raise AssertionError(str(self.out/'mismatch.json'))
        assert self.counter.value==count
        command=int.from_bytes(raw_in[0x9f4:0x9f8],'big')
        if command in [0,1,2]:
            pixels=actual_ram[0x1a0000:0x1a0000+224*180*2]
            (self.out/'C-frames'/f'message-{message}-frame-{frame:03d}.CRY16').write_bytes(pixels)
        self.rows.append(dict(index=index,message_id=message,frame=frame,blocks=blocks,delay_instructions=delays,logical_GPU_sha256=sha(logical(self.state)),RAM_sha256=sha(actual_ram),C_original_GPU_instructions=0,CPU_and_device_interrupt_effects_match=True))
        # Restore the matched source CPU/peripheral continuation and opaque
        # native pipeline fields. The persistent C architecture is retained
        # above and must match the next source command before any execution.
        self.restore(after_machine)
    def summary(self):
        save(self.out/'C-command-checks.json',self.rows)
        return dict(commands=len(self.rows),source_sha256=self.mapping['source_sha256'],retained_C_GPU_architecture=True,allowed_source_CPU_GPU_RAM_update='F039F0..F03A18 command/argument mailbox only',logical_GPU_RAM_CPU_IRQ_and_devices_match=True,external_writes=self.events,original_GPU_instructions=0)

if __name__=='__main__':main()

"""Original CPU video wrappers + relocated GPU + source GPU IRQ, six frames.

Frames are supplied from the preserved disc; no original movie stream or
full game scheduler. STOP/wakeup/ISR/RTE execute in the original CPU core.
"""
import ctypes as c,json,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
from probe_biwn_gpu_projection import gpu_state
from extract_biwn_stage import swap16
ROOT=media.ROOT;save=media.save;sha=media.sha;STOP=0x190000

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-GPU-original.json').read_text());before=(Path(proof['directory'])/'before-GPU.bin').read_bytes()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());setup_proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text())
    runtime=media.Runtime(Path(setup_proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded']);core=runtime.core
    core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
    out=ROOT/'verification/BIWN-original-movie-frames'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();results=[]
    def cpu_call(entry,args,case,collect=False):
        initial=media.CPU();initial.registers[:]=[0]*15+[0x1ff000];initial.ssp=0x1ff000;initial.usp=0x1fe000;initial.sr=0x2000;initial.pc=entry
        runtime.device.direct(0x1ff000,4,STOP);c.memmove(runtime.device.pointer+0x1ff004,args,len(args))
        runtime.seed_cpu(initial);steps=[];commands=[];irq_steps=[]
        for _ in range(500000):
            pc=core.m68k_get_reg(None,16)
            if pc==STOP:return dict(CPU_steps=len(steps),CPU_PC=steps,GPU_commands=commands,IRQ_PC=irq_steps,CPU=media.scheduler.cpu_dict(runtime.cpu()))
            if pc==0x304e:raise AssertionError('Unexpected VBI firmware call during GPU-only IRQ test')
            assert (0x22780<=pc<0x22a18 or 0xe7aa<=pc<0xe822),hex(pc)
            steps.append(pc)
            if 0xe7d4<=pc<0xe822:irq_steps.append(pc)
            if pc==0x22a0e:
                # Execute the source STOP; the GPU completion signal then
                # wakes the CPU through the source E7D4 handler and RTE.
                core.m68k_execute(1)
                command_index=len(commands);params=[core.GPUReadLong(0xf039f4+i*4,6) for i in range(8)]
                input_raw,state=gpu_state(core);memory=runtime.device.ram();stem=f'case-{case}-command-{command_index}-{entry:x}'
                machine_size=core.retro_serialize_size();machine=c.create_string_buffer(machine_size);assert core.retro_serialize(machine,machine_size)
                (out/f'{stem}-before-machine.bin').write_bytes(machine.raw)
                CPU_before=media.scheduler.cpu_dict(runtime.cpu())
                (out/f'{stem}-before-GPU.bin').write_bytes(input_raw);(out/f'{stem}-before-RAM.bin').write_bytes(memory)
                shader=[]
                for __ in range(500000):
                    gpc=core.GPUGetPC()
                    if shader and gpc==0xf032c8 and core.GPUReadLong(0xf039f0,6)==0:break
                    raw=c.string_at(core.GPUGetRAM(),4096);offset=gpc-0xf03000
                    assert 0<=offset<4096,hex(gpc)
                    word=int.from_bytes(raw[offset:offset+2],'big');size=6 if word>>10==38 else 2
                    old_count=counter.value;core.GPUExec(1);delta=(counter.value-old_count)&0xffffffff
                    assert delta in [1,2],(hex(gpc),delta)
                    shader.append(dict(pc=gpc,bytes=raw[offset:offset+size].hex(),instructions=delta,after_pc=core.GPUGetPC()))
                else:raise AssertionError('Movie shader bound')
                after_raw,state=gpu_state(core);(out/f'{stem}-after-GPU.bin').write_bytes(after_raw);(out/f'{stem}-after-RAM.bin').write_bytes(runtime.device.ram())
                commands.append(dict(stem=stem,params=params,blocks=len(shader),source_instructions=sum(x['instructions'] for x in shader),PC_sequence=shader,
                    before_RAM_sha256=sha(memory),after_RAM_sha256=sha(runtime.device.ram()),after_logical_GPU_sha256=sha(after_raw[:4396]),
                    CPU_before=CPU_before,CPU_after_GPU_signal=media.scheduler.cpu_dict(runtime.cpu()),stopped_machine_bytes=machine_size))
                continue
            core.m68k_execute(1)
        raise AssertionError('Video CPU/IRQ bound')
    try:
        for case,message in enumerate(extraction['messages']):
            save(out/'status.json',dict(status='running',message=message['message_id']))
            video=next(x for x in message['sample_records'] if not x['audio'])
            with (session/'raw-tracks/track-04-raw.bin').open('rb') as f:f.seek(video['normalized_track_offset']);data=swap16(f.read(video['bytes']))
            runtime.reset(base,case%3);buf=c.create_string_buffer(before);assert core.GPUStateLoad(buf)==len(before)
            # Re-run the actual GPU initialization, not a host relocation.
            for _ in range(20000):
                if core.GPUGetPC()==0xf032c8:break
                core.GPUExec(1)
            else:raise AssertionError('GPU relocation bound')
            runtime.device.direct(0xbd84c,4,0x258)
            c.memmove(runtime.device.pointer+0x1c0000,data,len(data))
            c.memset(runtime.device.pointer+0x1a0000,0,224*180*2)
            initialization=cpu_call(0xe7aa,b'',case)
            codebook=cpu_call(0x227a0,struct.pack('>HIII',1,0x1c0000,0xbd904,0),case)
            assert runtime.device.read(0x1ff00e,4)==0
            frame=cpu_call(0x228d4,struct.pack('>IIIII',448,0x1a0000,0x1c0000,0xbd904,0),case)
            assert runtime.device.read(0x1ff014,4)==0
            pixels=runtime.device.ram()[0x1a0000:0x1a0000+224*180*2];(out/f'message-{message["message_id"]}-first-frame.CRY16').write_bytes(pixels)
            assert any(pixels)
            result=dict(message_id=message['message_id'],video_sample=video,video_sha256=sha(data),initialization=initialization,codebook=codebook,frame=frame,
                width=224,height=180,pixel_sha256=sha(pixels),GPU_commands=len(codebook['GPU_commands'])+len(frame['GPU_commands']))
            results.append(result);save(out/'fixtures.json',results)
            print(json.dumps(dict(message=message['message_id'],GPU_commands=result['GPU_commands'],pixels=sha(pixels))),flush=True)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_source_CPU_GPU_first_disc_video_frames_captured_C_unverified',directory=str(out),cases=len(results),
            GPU_commands=sum(x['GPU_commands'] for x in results),source_CPU_STOP_IRQ_RTE_executed=True,original_movie_streaming=False,C_decoder_verified=False,whole_game_complete=False,new_published_components=0,
            script_sha256=sha(Path(__file__).read_bytes()),limits=['Host invokes source IRQ setup and video wrappers over one supplied real frame per dialogue; fixed destination/pitch and explicit CPU/GPU alternation at STOP. No original movie controller/firmware stream/global scheduler or physical timing.',
                'Pinned original emulator CPU/GPU reference only; C decoder remains unverified. Pixel bytes are primary; any preview conversion remains separate.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-original-movie-frames.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),cases=len(results),GPU_commands=report['GPU_commands'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()

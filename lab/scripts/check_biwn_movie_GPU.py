"""C movie GPU codebook/frame commands vs captured source CPU/native GPU.

Compare complete4396logicalGPUbytes and2MBRAM at each command boundary,
and exact outer PC sequence. The native GPU counter excludes inline delays;
their actual instruction count is calculated separately from taken branches.
"""
import ctypes as c,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);OBS=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]
class State(c.Structure):_fields_=[('registers',(c.c_uint32*32)*2)]+[(n,c.c_uint32) for n in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','instructions','accumulator','hidata','flags','data_organization','control','active_bank']]+[('local_RAM',c.c_uint8*4096)]
def state_from_raw(raw):
    s=State();s.local_RAM[:]=raw[:4096]
    for name,value in zip(['pc','accumulator','remainder','hidata','flags','matrix_control','matrix_pointer','data_organization','control','division_control'],struct.unpack_from('=10I',raw,4096)):setattr(s,name,value)
    s.z,s.n,s.c=raw[4136:4139]
    for i,value in enumerate(struct.unpack_from('=64I',raw,4139)):s.registers[i//32][i%32]=value
    s.active_bank=raw[4395];return s
def logical(s):
    raw=bytes(s.local_RAM)+struct.pack('=10I',*[getattr(s,n) for n in ['pc','accumulator','remainder','hidata','flags','matrix_control','matrix_pointer','data_organization','control','division_control']])+bytes([s.z,s.n,s.c])+struct.pack('=64I',*[v for bank in s.registers for v in bank])+bytes([s.active_bank]);assert len(raw)==4396;return raw

def main():
    native=json.loads((ROOT/'verification/BIWN-original-movie-frames.json').read_text());capture=Path(native['directory']);fixtures=json.loads((capture/'fixtures.json').read_text())
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'media-video-gpu-21ea0/first-frames-C-generation.json').read_text());decoded={x['address']:x for x in mapping['instructions_decoded']}
    out=ROOT/'verification/BIWN-movie-GPU-C'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovie-GPU.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_movie_GPU.c'),'-o',str(library)]
    compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());setup_proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text());runtime=media.Runtime(Path(setup_proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded'])
    lib=c.CDLL(str(library));run=lib.biwn_movie_GPU_run;run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];run.restype=c.c_int
    core=runtime.core;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8;core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
    def translated(row,options=None):
        options=options or {};ram=(capture/f'{row["stem"]}-before-RAM.bin').read_bytes();raw=(capture/f'{row["stem"]}-before-GPU.bin').read_bytes();runtime.reset(ram,0)
        machine=(capture/f'{row["stem"]}-before-machine.bin').read_bytes();buf=c.create_string_buffer(machine);assert core.retro_unserialize(buf,len(machine))
        assert runtime.device.ram()==ram and media.scheduler.cpu_dict(runtime.cpu())==row['CPU_before']
        s=state_from_raw(raw);pcs=[];events=[];errors=[]
        def rd(w):
            def cb(_,a,v):
                if options.get('fail')==('read',w):return 1
                try:
                    v[0]=core.JaguarReadByte(a,3) if w==1 else core.GPUReadWord(a,3) if w==2 else core.GPUReadLong(a,3)
                    events.append(['read',a,w,v[0]]);return 0
                except Exception as e:errors.append(repr(e));return 1
            return cb
        def wr(_,a,v):
            if options.get('fail')==('write',4):return 1
            try:events.append(['write',a,4,v]);core.GPUWriteLong(a,v,3);return 0
            except Exception as e:errors.append(repr(e));return 1
        callbacks=[R8(rd(1)),R16(rd(2)),R32(rd(4)),W32(wr),OBS(lambda _,pc:pcs.append(pc))]
        if 'missing' in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        if options.get('no_trace'):callbacks[4]=OBS()
        bus=Bus(*callbacks,None)
        if options.get('bad_PC'):s.pc=0
        if options.get('bad_bank'):s.active_bank=1
        if options.get('bad_flag'):setattr(s,options['bad_flag'],2)
        before=bytes(s);count=counter.value
        status=run(None if options.get('null_bus') else c.byref(bus),None if options.get('null_state') else c.byref(s),options.get('budget',1000000))
        assert counter.value==count
        return runtime.device.ram(),s,dict(status=status,outer_PC=pcs,state_unchanged=bytes(s)==before,errors=errors,external_events=events,original_GPU_instructions=0,CPU_after_GPU_signal=media.scheduler.cpu_dict(runtime.cpu()))
    results=[];coverage=set();guards=[]
    commands=[(f['message_id'],kind,row) for f in fixtures for kind in ['codebook','frame'] for row in f[kind]['GPU_commands']]
    try:
        for case,(message,kind,row) in enumerate(commands):
            save(out/'status.json',dict(status='running',case=case,message=message,kind=kind));expected_RAM=(capture/f'{row["stem"]}-after-RAM.bin').read_bytes();expected_GPU=(capture/f'{row["stem"]}-after-GPU.bin').read_bytes()
            actual_RAM,s,record=translated(row);direct=[x['pc'] for x in row['PC_sequence']]
            delays=[x['pc']+2 for x in row['PC_sequence'] if int(x['bytes'][:4],16)>>10 in [52,53] and x['after_pc']!=x['pc']+2]
            if record['status'] or actual_RAM!=expected_RAM or logical(s)!=expected_GPU[:4396] or record['outer_PC']!=direct or s.instructions!=len(direct)+len(delays) or record['CPU_after_GPU_signal']!=row['CPU_after_GPU_signal']:
                save(out/'mismatch.json',dict(case=case,status=record['status'],GPU_diff=[hex(i) for i,(a,b) in enumerate(zip(logical(s),expected_GPU[:4396])) if a!=b][:40],RAM_diff=[hex(i) for i,(a,b) in enumerate(zip(actual_RAM,expected_RAM)) if a!=b][:40],C_PC=hex(s.pc),C_instructions=s.instructions,expected=len(direct)+len(delays),trace_match=record['outer_PC']==direct,errors=record['errors']));raise AssertionError(str(out/'mismatch.json'))
            coverage.update(direct);coverage.update(delays)
            (out/f'{row["stem"]}-C-GPU.bin').write_bytes(logical(s))
            if kind=='frame':
                pixels=actual_RAM[0x1a0000:0x1a0000+224*180*2];(out/f'message-{message}-C-first-frame.CRY16').write_bytes(pixels)
            results.append(dict(case=case,message_id=message,kind=kind,command=row['params'][0],outer_instruction_blocks=len(direct),mandatory_delay_instructions=len(delays),source_instructions=s.instructions,logical_GPU_sha256=sha(logical(s)),RAM_sha256=sha(actual_RAM),C_original_GPU_instructions=0,external_writes=sum(x[0]=='write' for x in record['external_events'])));save(out/'fixtures.json',results)
        first=commands[0][2];frame=commands[1][2]
        options=[dict(missing=i) for i in range(4)]+[dict(null_bus=True),dict(null_state=True),dict(budget=0),dict(bad_bank=True)]+[dict(bad_flag=k) for k in ['z','c','n']]
        for opt in options:
            _,_,record=translated(first,opt);assert record['status']==1 and record['state_unchanged'];guards.append(dict(options=opt,status=1))
        for opt,expected in [(dict(bad_PC=True),3),(dict(budget=1),4),(dict(fail=('read',1)),2),(dict(fail=('read',2)),2),(dict(fail=('read',4)),2),(dict(fail=('write',4)),2)]:
            row=frame if opt.get('fail') in [('read',1),('read',4)] else first
            _,_,record=translated(row,opt);assert record['status']==expected and record['state_unchanged'],(opt,record['status']);guards.append(dict(options=opt,status=expected))
        _,_,record=translated(first,dict(no_trace=True));assert record['status']==0 and record['outer_PC']==[];guards.append(dict(optional_trace=True,status=0))
        assert coverage==set(decoded)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='six_real_first_movie_frames_C_GPU_commands_match_original',directory=str(out),frames=6,GPU_commands=len(results),source_instruction_coverage=[len(coverage),len(decoded)],host_guards=len(guards),
            source_sha256=mapping['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),native_reference_directory=str(capture),
            source_instructions_including_mandatory_delays=sum(x['source_instructions'] for x in results),original_GPU_counter_counts_only_outer_blocks=True,
            all4396logical_GPU_bytes_and_all_main_RAM_compared_each_command=True,exact_outer_PC_sequence_and_delay_count_match=True,original_GPU_instructions_on_C_path=0,
            CPU_wrappers_source_native_in_reference=True,CPU_wrappers_reconstructed_C=False,full_video_GPU_program_coverage=False,complete_movie_playback_verified=False,whole_game_complete=False,new_published_components=0,
            limits=['Six first real frames/12book and drawing commands; execution-proven186fixed GPU instructions only. Other addresses returnBAD_PC; native relocation/CPU preparation supplies snapshots.',
                'Full logical GPU state4396bytes, complete2MB RAM, raw CRY pixels, directPCsequence and mandatory delay counts match per command. Native GPU opcode counter excludes inline delay instructions; accounted separately.',
                'Shared pinned memory/CPU-interrupt bus, no physical timing, full movie controller/streaming/scheduler/objectprocessor scanout or whole game. Native GPU opcode/pipeline microstate excluded.'])
        save(out/'report.json',report);save(out/'guards.json',guards);save(ROOT/'verification/BIWN-movie-GPU-C.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=6,commands=12,coverage=report['source_instruction_coverage'],guards=len(guards))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()

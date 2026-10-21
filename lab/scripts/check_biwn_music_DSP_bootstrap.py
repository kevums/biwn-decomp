"""Per-block native/C DSP startup, command2 IRQ frame and source acknowledgement."""
import ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
import check_biwn_dsp_media_audio as dsp
ROOT=media.ROOT;save=media.save;sha=media.sha
W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16)
class Bus(c.Structure):_fields_=dsp.Bus._fields_[:3]+[('write16',W16)]+dsp.Bus._fields_[3:]
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'music-DSP-bootstrap-generation.json').read_text());out=ROOT/'verification/BIWN-music-DSP-bootstrap'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmusic-bootstrap.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_dsp_music_bootstrap.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',[]);core=runtime.core;core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.DSPSetIRQLine.argtypes=[c.c_int,c.c_int]
    for n,typ in [('DSPReadLong',c.c_uint32),('DSPWriteLong',None),('DSPWriteWord',None)]:
        f=getattr(core,n);f.argtypes=[c.c_uint32,c.c_uint32]if n=='DSPReadLong'else[c.c_uint32,c.c_uint32,c.c_uint32]
        if n=='DSPReadLong':f.argtypes=[c.c_uint32,c.c_uint32];f.restype=typ
    core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8;counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
    lib=c.CDLL(str(library));step=lib.biwn_dsp_music_bootstrap_step;step.argtypes=[c.POINTER(Bus),c.POINTER(dsp.State)];step.restype=c.c_int;event=lib.biwn_dsp_music_bootstrap_cpu_interrupt;event.argtypes=[c.POINTER(dsp.State)];event.restype=c.c_int
    rows={r['address']:r for r in mapping['instructions_decoded']};baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();payload=baseline[0x7248:0x8458];rng=random.Random(0xb126c);coverage=set();results=[];trace=[]
    def raw():
        b=c.create_string_buffer(12000);n=runtime.savers['DSP'](b);assert n==8729;return b.raw[:n]
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['DSP']=dict(size=8496,sha256=sha(dsp.logical(state)if state is not None else raw()[:8496]));return h
    callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(core.DSPWriteLong(a,v,2),0)[1]),W16(lambda _,a,v:(core.DSPWriteWord(a,v,2),0)[1]),dsp.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None)
    try:
        for case in range(32):
            runtime.reset(baseline,case%3);c.memmove(core.DSPGetRAM(),payload,len(payload));core.DSPWriteLong(0xf1badc,2,6);core.DSPWriteLong(0xf1bae0,0x3bce0,6);core.DSPWriteLong(0xf1bae4,0,6)
            initial=bytearray(raw());struct.pack_into('=I',initial,8192,0xf1b126);struct.pack_into('=I',initial,8212,(0x40000 if case%2 else 0)|(case%8));struct.pack_into('=I',initial,8228,0x2001);initial[8236:8239]=bytes([case&1,(case>>2)&1,(case>>1)&1]);struct.pack_into('=64I',initial,8239,*[rng.getrandbits(32)for _ in range(64)]);initial[8495]=0;initial=bytes(initial);assert core.DSPStateLoad(c.create_string_buffer(initial))==len(initial)
            initial_RAM=runtime.device.ram();frames=[];event_frame=None
            for stage,stop in [('flags',0xf1b144),('command2',0xf1b148)]:
                if stage=='command2':core.DSPWriteLong(0xf1a114,5,6);event_frame=raw()[:8496];assert core.DSPGetPC()==0xf1b000
                for _ in range(10000):
                    pc=core.DSPGetPC()
                    if pc==stop:break
                    assert pc in rows,hex(pc);before=counter.value;core.DSPExec(1);count=(counter.value-before)&0xffffffff;assert count in [1,2]
                    coverage.add(pc)
                    if count==2:coverage.add(pc+rows[pc]['size'])
                    frames.append(dict(stage=stage,PC=pc,instructions=count,raw_DSP=raw()[:8496],RAM_sha256=sha(runtime.device.ram()),hardware=hardware()))
                else:raise AssertionError(('Native music bound',stage,hex(pc)))
            expected_RAM=runtime.device.ram();assert core.DSPReadLong(0xf1badc,6)==0
            runtime.reset(initial_RAM,case%3);assert core.DSPStateLoad(c.create_string_buffer(initial))==len(initial);state=dsp.state_from_raw(initial);trace.clear();before_counter=counter.value;event_applied=False
            for i,frame in enumerate(frames):
                if frame['stage']=='command2'and not event_applied:
                    # Same CPU write to shared MMIO shadow; source flags/IRQ frame are C-owned.
                    core.DSPWriteLong(0xf1a114,5,6);state.control=(state.control&0x1f7c0)|(5&~0x1f7c4);assert event(c.byref(state))==0;assert dsp.logical(state)==event_frame;event_applied=True
                assert state.pc==frame['PC'];before=state.instructions;status=step(c.byref(bus),c.byref(state))
                if status or dsp.logical(state)!=frame['raw_DSP']or sha(runtime.device.ram())!=frame['RAM_sha256']or hardware(state)!=frame['hardware']or state.instructions-before!=frame['instructions']:
                    (out/'native-DSP.bin').write_bytes(frame['raw_DSP']);(out/'C-DSP.bin').write_bytes(dsp.logical(state));save(out/'mismatch.json',dict(case=case,index=i,PC=hex(frame['PC']),status=status,C_PC=hex(state.pc),DSP_differences=[j for j,(a,b)in enumerate(zip(frame['raw_DSP'],dsp.logical(state)))if a!=b][:80],RAM_match=sha(runtime.device.ram())==frame['RAM_sha256'],hardware_native=frame['hardware'],hardware_C=hardware(state)));raise AssertionError(str(out/'mismatch.json'))
            assert runtime.device.ram()==expected_RAM and counter.value==before_counter and trace==[f['PC']for f in frames]and state.pc==0xf1b148
            assert int.from_bytes(bytes(state.local_RAM[0xadc:0xae0]),'big')==0
            results.append(dict(case=case,blocks=len(frames),instructions=state.instructions,DSP_sha256=sha(dsp.logical(state)),RAM_sha256=sha(expected_RAM),full_logical_DSP8496_RAM_peripherals_IRQ_frame_PC_trace_and_counts_match=True));save(out/'cases.json',results);save(out/'status.json',dict(status='running',case=case))
        selected=set(rows);assert selected<=coverage
        report=dict(status='music_DSP_flag_bootstrap_CPU_IRQ0_command2_source_ack_native_C_match',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),cases=len(results),source_instruction_coverage=[len(selected&coverage),len(selected)],covered_PC=sorted(coverage),original_DSP_instructions_on_C_path=0,source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,full_music_mixer_verified=False,whole_game_complete=False,limits=['Standalone exact source payload/command2/song pointer3BCE0/index0 from supplied FrozenRAM; randomized incoming registers/ZNC/flags within bank0, declared CPUIRQ after source flag init atF1B144. No concurrent IRQ/physical interleaving/global timing proof.','Source bootstrap/copy/timer programming/mailbox acknowledgement throughF1B148 only; bank1 music engine/SSI/mixer, other commands/resources, CPU4000/globalboot/playablegame not proved. Shared pinned device models and logicalDSP microstate exclusion retained.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/music-DSP-bootstrap-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['covered_PC','source_sha256','compiler']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()

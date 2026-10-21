"""Every native/C mixer block, bank/IRQ frame, wait, DAC strobe and full state."""
import argparse,ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_music_DSP_bootstrap as boot
dsp=boot.dsp;media=boot.media;ROOT=boot.ROOT;sha=boot.sha;save=boot.save
Bus=boot.Bus
class State(c.Structure):_fields_=dsp.State._fields_+[(n,c.c_uint32)for n in ['bank','prestore_bank','flags_delay']]
def state_from_raw(raw):
    bank=raw[8495];b=bytearray(raw);b[8495]=0;base=dsp.state_from_raw(bytes(b));s=State()
    for name,_ in dsp.State._fields_:setattr(s,name,getattr(base,name))if name!='registers'and name!='local_RAM'else None
    for k in range(2):s.registers[k][:]=base.registers[k]
    s.local_RAM[:]=base.local_RAM;s.bank=s.prestore_bank=bank;return s
def logical(s):return dsp.logical(s)[:-1]+bytes([s.bank])
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owner-candidate',type=Path);parser.add_argument('--core',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--coverage-only',action='store_true')
    parser.add_argument('--bootstrap-proof',type=Path,help='Separate matching-owner startup/command1/2 proof to extend the complete program coverage gate')
    args=parser.parse_args()
    assert not any([args.owner_candidate,args.core,args.output])or all([args.owner_candidate,args.core,args.output]),'Owner experiment requires separate core,candidate and output'
    bootstrap=None
    if args.bootstrap_proof:
        assert args.owner_candidate and not args.coverage_only
        bootstrap=json.loads(args.bootstrap_proof.read_text())
        assert bootstrap['status']=='DSP_source_owner_startup_command1_command2_native_match'
        assert bootstrap['core_sha256']==sha(args.core.read_bytes())
        assert bootstrap['owner_candidate_sha256']==sha(args.owner_candidate.read_bytes())
        candidate=json.loads(args.owner_candidate.read_text())
        assert bootstrap['owner_library_sha256']==sha(Path(candidate['library']).read_bytes())
        assert len(bootstrap['cases'])==8 and all(case['matched']for case in bootstrap['cases'])
        assert not bootstrap['coverage']['missing_PC']
        for case in bootstrap['cases']:
            proof=json.loads(Path(case['owner_report']).read_text())
            assert proof['errors']==proof['uncovered']==proof['core_counts']['Original']==proof['core_counts']['Rejected']==0
            assert proof['core_counts']['Owned']>0
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'music-DSP-engine-generation.json').read_text());probe=json.loads((ROOT/'verification/music-DSP-engine-probe.json').read_text());folder=Path(probe['directory']);initial=(folder/'initial-DSP.bin').read_bytes();RAM=(folder/'initial-RAM.bin').read_bytes();out=ROOT/'verification/BIWN-music-DSP-engine'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmusic-engine.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_dsp_music_engine.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    old=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(old['directory'])/'libentry-helpers.dylib',[],diagnostic_core=args.core);core=runtime.core
    core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPGetFlags.restype=c.c_uint32;core.DSPGetReg.argtypes=[c.c_int];core.DSPGetReg.restype=c.c_uint32;core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.DSPSetIRQLine.argtypes=[c.c_int,c.c_int];core.DACWordStrobe.argtypes=[];core.DACStateLoad.argtypes=[c.c_void_p,c.c_uint32];core.DACStateLoad.restype=c.c_size_t
    core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
    lib=c.CDLL(str(library));step=lib.biwn_dsp_music_engine_step;step.argtypes=[c.POINTER(Bus),c.POINTER(State)];step.restype=c.c_int;event=lib.biwn_dsp_music_engine_assert_interrupt;event.argtypes=[c.POINTER(State),c.c_uint32];event.restype=c.c_int;counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');rows={r['address']:r for r in mapping['instructions_decoded']};coverage=set();results=[];trace=[]
    def raw():
        b=c.create_string_buffer(12000);n=runtime.savers['DSP'](b);assert n==8729;return b.raw[:n]
    def hardware(s=None):
        h=runtime.snapshot()['hardware'];h['DSP']=dict(size=8496,sha256=sha(logical(s)if s is not None else raw()[:8496]));return h
    def dac():
        b=c.create_string_buffer(200000);n=runtime.savers['DAC'](b);return b.raw[:n]
    callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(core.DSPWriteLong(a,v,2),0)[1]),boot.W16(lambda _,a,v:(core.DSPWriteWord(a,v,2),0)[1]),dsp.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None)
    def capture(kind,**kw):return dict(kind=kind,**kw)if args.coverage_only else dict(kind=kind,DSP=raw()[:8496],RAM=sha(runtime.device.ram()),hardware=hardware(),**kw)
    def native_pump(frames,label):
        for _ in range(100000):
            pc=core.DSPGetPC()
            if pc==0xf1b212 and raw()[8495]==1 and not core.DSPGetFlags()&8 and core.DSPGetReg(2)==core.DSPGetReg(28)and struct.unpack_from('=I',raw(),8239+21*4)[0]==core.DSPGetReg(28):return
            assert pc in rows,hex(pc);before=counter.value;core.DSPExec(1);count=(counter.value-before)&0xffffffff;assert count in [1,2];coverage.add(pc)
            if count==2:coverage.add(pc+rows[pc]['size'])
            frames.append(capture('step',PC=pc,instructions=count))
        raise AssertionError(('Native music wait bound',label,hex(pc)))
    rng=random.Random(0xb1e0c);owner_reports=[]
    try:
        for case in range(8):
            scenario='silent_startup'if case<4 else 'synthetic_sample_voice'
            active_folder=folder if case<4 else Path(json.loads((ROOT/'verification/music-DSP-sample-voice-probe.json').read_text())['directory'])
            initial=(active_folder/'initial-DSP.bin').read_bytes();RAM=(active_folder/'initial-RAM.bin').read_bytes();fixture=bytearray(initial)
            if case:
                regs=list(struct.unpack_from('=64I',fixture,8239))
                for bank in [0,1]:
                    for reg in range(29):regs[bank*32+reg]=rng.getrandbits(32)
                struct.pack_into('=64I',fixture,8239,*regs)
            fixture=bytes(fixture);runtime.reset(RAM,case%3);DAC_input=dac();assert core.DACStateLoad(c.create_string_buffer(DAC_input),9)==len(DAC_input);DAC_input=dac();assert core.DSPStateLoad(c.create_string_buffer(fixture))==len(fixture);frames=[];PCM=[];native_pump(frames,'init')
            for tick in range(64):
                for irq in ([2,1]if tick%16==0 else [1]):core.DSPSetIRQLine(irq,1);frames.append(capture('irq',irq=irq));native_pump(frames,f'{tick}/{irq}')
                core.DACWordStrobe();pair=dsp.strobed_pair(dac());PCM.append(pair);frames.append(capture('strobe',PCM=pair))
            if args.coverage_only:
                results.append(dict(case=case,scenario=scenario,original_atomic_steps=sum(f['kind']=='step'for f in frames),nonzero_PCM_pairs=sum(any(pair)for pair in PCM)));continue
            expected_RAM=runtime.device.ram();expected=raw()[:8496];runtime.reset(RAM,case%3);assert core.DACStateLoad(c.create_string_buffer(DAC_input),9)==len(DAC_input);assert dac()==DAC_input;assert core.DSPStateLoad(c.create_string_buffer(fixture))==len(fixture);s=state_from_raw(fixture);trace.clear();before_counter=counter.value;C_PCM=[]
            if args.owner_candidate:
                import biwn_DSP_program_router as owner_module
                owner_folder=out/('owner-case-'+str(case));owner_folder.mkdir()
                owner=owner_module.install(core,owner_folder,args.owner_candidate)
            for index,f in enumerate(frames):
                if args.owner_candidate:
                    status=0;count=None
                    if f['kind']=='step':
                        assert core.DSPGetPC()==f['PC'];trace.append(core.DSPGetPC());owned_before=core.BIWNDSPOwnedInstructionCount();core.DSPExec(1);count=core.BIWNDSPOwnedInstructionCount()-owned_before
                    elif f['kind']=='irq':core.DSPSetIRQLine(f['irq'],1)
                    else:core.DACWordStrobe();C_PCM.append(dsp.strobed_pair(dac()))
                    s=state_from_raw(raw());s.instructions=core.BIWNDSPOwnedInstructionCount()
                elif f['kind']=='step':
                    assert s.pc==f['PC'];before=s.instructions;status=step(c.byref(bus),c.byref(s));count=s.instructions-before
                elif f['kind']=='irq':status=event(c.byref(s),f['irq']);count=None
                else:core.DACWordStrobe();status=0;count=None;C_PCM.append(dsp.strobed_pair(dac()))
                if status or logical(s)!=f['DSP']or sha(runtime.device.ram())!=f['RAM']or hardware(s)!=f['hardware']or(f['kind']=='step'and count!=f['instructions']):
                    (out/'native-DSP.bin').write_bytes(f['DSP']);(out/'C-DSP.bin').write_bytes(logical(s));save(out/'mismatch.json',dict(case=case,index=index,kind=f['kind'],PC=hex(f.get('PC',s.pc)),C_PC=hex(s.pc),status=status,DSP_differences=[i for i,(a,b)in enumerate(zip(f['DSP'],logical(s)))if a!=b][:80],native_hardware=f['hardware'],C_hardware=hardware(s),RAM_match=sha(runtime.device.ram())==f['RAM'],bank=s.bank,flags_delay=s.flags_delay));raise AssertionError(str(out/'mismatch.json'))
            assert logical(s)==expected and runtime.device.ram()==expected_RAM and C_PCM==PCM and trace==[f['PC']for f in frames if f['kind']=='step']
            if args.owner_candidate:
                owned=owner[3]();owner_reports.append(owned)
                assert owned['errors']==owned['uncovered']==owned['core_counts']['Original']==owned['core_counts']['Rejected']==0 and owned['core_counts']['Owned']>0
                if scenario=='synthetic_sample_voice':assert any(any(pair)for pair in C_PCM),'Synthetic voice was silent'
            else:assert counter.value==before_counter
            results.append(dict(case=case,scenario=scenario,atomic_blocks=len(trace),instructions=s.instructions,SSI_events=64,timer2_events=4,nonzero_PCM_pairs=sum(any(x)for x in C_PCM),DSP_sha256=sha(expected),RAM_sha256=sha(expected_RAM),PCM_sha256=sha(b''.join(struct.pack('<hh',*p)for p in C_PCM)),full_logical_DSP8496_banks_RAM_peripherals_IRQ_frames_trace_counts_DAC_PCM_match=True));save(out/'cases.json',results);save(out/'status.json',dict(status='running',case=case))
        coverage_report=dict(status='original_native_coverage_complete'if set(rows)<=coverage else'original_native_coverage_incomplete',directory=str(out),expected=len(rows),observed=len(set(rows)&coverage),missing=[rows[pc]for pc in sorted(set(rows)-coverage)],cases=results,scope='Original native DSP coverage diagnostic only; no reconstructed owner is installed in coverage-only mode.')
        save(out/'coverage.json',coverage_report)
        if args.coverage_only:
            save(args.output or out/'coverage-only.json',coverage_report);print(json.dumps(coverage_report));return
        mixer_coverage=set(coverage)
        if bootstrap:coverage.update(bootstrap['coverage']['covered_PC'])
        assert set(rows)<=coverage
        report=dict(status='source_bank1_mixer_SSI_timer2_banks_IRQ_DAC_silence_and_synthetic_sample_voice_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(set(rows)&coverage),len(rows)],banks=[0,1],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,original_DSP_instructions_on_C_path=0,full_music_playback_verified=False,whole_game_complete=False,limits=['Captured discovery boundary atF1B148 produced by actual source4000 cold-stage startup; standalone engine comparison, not yet continuous linked startup/world/music. Four input-register profiles each for silent startup and an explicit synthetic type8voice/256encoded waveform bytes, source song3BCE0/index0,64SSI strobes plus4 externally assertedtimer2 events/profile.','Startup song is silent; separate synthetic voice exercises nonzero PCM interpolation but is not game-disc music playback. Other voice paths/commands/resources, complete song/globaltime/physical rates/mixer edge cases unverified.','Exact initial DAC state canonicalized/restored on both paths because pinned DACReset leaves right holding register unchanged; pinned DSP flag-store retirement and logical8496bytes/bothbanks/full2MBRAM/peripherals/IRQframe/PCtrace/instructioncounts/DAC/PCM compare each atomic source block; microstate excluded.'])
        if args.owner_candidate:
            report.update(status='source_DSP_owner_silence_and_synthetic_sample_voice_native_match',owner_candidate=str(args.owner_candidate),core=str(args.core),core_sha256=sha(args.core.read_bytes()),owner_reports=owner_reports,PC_trace_scope='Coordinator observes native DSPGetPC at each source atomic callback boundary; instruction/delay identities are byte-fenced by the owner. Not an independent kernel PC callback trace.',original_DSP_IRQ_provider=True,standalone_kernel_compiled_but_not_used=True)
            report['limits'][0]='Explicit captured silent/sample-voice fixtures with varied register profiles,64SSIstrobes and4timer2IRQs percase. Source owner executes actual core DSPExec callbacks; original DSP IRQ dispatch/device services retained. Not natural gameplay or song playback.'
        if bootstrap:
            report.update(bootstrap_proof=str(args.bootstrap_proof),
                mixer_fixture_source_instruction_coverage=[len(set(rows)&mixer_coverage),len(rows)],
                coverage_scope='Union of eight mixer/SSI/timer/sample-voice fixtures and eight separate startup/command1/2 profiles, same pinned core and source-owner library. All316 selected instruction locations covered across these fixtures; no single uninterrupted startup-to-song proof.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(args.output or ROOT/'verification/music-DSP-engine-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','owner_reports']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()

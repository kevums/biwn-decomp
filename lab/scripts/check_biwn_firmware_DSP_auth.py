"""Fresh native/C guarded decryption and firmware-check path comparison.

The incoming DSP/RAM fixture was produced by the natural original CPU
bootstrap. This standalone component comparison does not reconstruct the
preceding firmware CPU/GPU or establish an uninterrupted C firmware boot.
"""
import ctypes as c,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_firmware_relocation_cpu as relocation
import check_biwn_media_setup_cpu as media
import check_biwn_dsp_media_audio as dsp

ROOT=media.ROOT;save=media.save;sha=media.sha

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'firmware-DSP-auth-generation.json').read_text())
    discovery=Path(mapping['source_observation']);incoming=(discovery/'DSP-at-CPU-wait.bin').read_bytes();RAM=(discovery/'RAM-final.bin').read_bytes()
    assert len(incoming)==8729 and len(RAM)==0x200000 and sha(incoming[:8496])==mapping['initial_fixture_DSP_sha256']
    out=ROOT/'verification/BIWN-firmware-DSP-auth'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libfirmware-DSP-auth.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_firmware_DSP_auth.c'),'-o',str(lib)]
    save(out/'protocol.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),mapping=mapping,compiler=cmd,fixture_origin=str(discovery),scope='Standalone DSP body from naturalCPU-derived fixture; initial peripheral model reset supplied on both paths',checkpoints='After each first observed sourcePC/branch-delayPC, every100000blocks, and final sourceGO clear',logical_DSP_bytes=8496,excluded_DSP_microstate_bytes=233,whole_game_complete=False))
    build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    relocation_proof=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text());runtime=relocation.Runtime(Path(relocation_proof['directory'])/'libfirmware-relocation.dylib',[]);core=runtime.core
    core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
    functions=c.CDLL(str(lib));run=functions.biwn_firmware_DSP_auth_run;run.argtypes=[c.POINTER(dsp.Bus),c.POINTER(dsp.State),c.c_uint32];run.restype=c.c_int
    counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');rows={r['address']:r for r in mapping['instructions_decoded']};buffer=c.create_string_buffer(12000);coverage=set();frames=[];closed=False
    def raw():
        n=runtime.savers['DSP'](buffer);assert n==8729;return buffer.raw[:n]
    def hardware(s=None):
        result=runtime.snapshot()['hardware'];result['DSP']=dict(size=8496,sha256=sha(dsp.logical(s)if s is not None else raw()[:8496]));return result
    def reset():
        runtime.reset(RAM,0);assert core.DSPStateLoad(c.create_string_buffer(incoming))==len(incoming)
        initial=media.CPU();initial.pc=0x5021c;initial.sr=0x2000;initial.registers[15]=initial.ssp=0x200000;initial.usp=0x180000;runtime.seed_cpu(initial)
        assert raw()[:8496]==incoming[:8496]
    def capture(blocks,count,trace):
        data=raw()[:8496]
        return dict(blocks=blocks,instructions=count,DSP_hex=data.hex(),RAM_sha256=sha(runtime.device.ram()),hardware=hardware(),PC_trace_sha256=trace.hexdigest(),CPU=media.scheduler.cpu_dict(runtime.cpu()))
    try:
        reset();CPU_before=bytes(runtime.cpu());begin=counter.value;trace=__import__('hashlib').sha256();blocks=0
        while core.DSPReadLong(0xf1a114,0)&1:
            pc=core.DSPGetPC();assert pc in rows,hex(pc);row=rows[pc]
            assert c.string_at(core.DSPGetRAM()+pc-0xf1b000,row['size']).hex()==row['bytes'],('native code differs',hex(pc))
            before=counter.value;new=pc not in coverage;coverage.add(pc);trace.update(struct.pack('>I',pc));core.DSPExec(1);count=(counter.value-before)&0xffffffff;assert count in [1,2],count
            if count==2:
                delay=pc+row['size'];assert delay in rows,hex(delay);new=new or delay not in coverage;coverage.add(delay);trace.update(struct.pack('>I',delay))
            blocks+=1
            if new or blocks%100000==0 or not core.DSPReadLong(0xf1a114,0)&1:
                frames.append(capture(blocks,(counter.value-begin)&0xffffffff,trace))
            assert blocks<=12000000
            if blocks%2000000==0:print(json.dumps(dict(native_blocks=blocks,PC=hex(pc))),flush=True)
        assert coverage==set(rows) and bytes(runtime.cpu())==CPU_before
        assert frames[-1]['instructions']==mapping['original_program_instructions']
        save(out/'native-checkpoints.json',frames)
        assert core.DSPReadLong(0xf1b000,0)==0x03d0dead
        native_final=raw();(out/'native-final-DSP.bin').write_bytes(native_final)
        reset();initial_hardware=hardware();s=dsp.state_from_raw(incoming);c_trace=__import__('hashlib').sha256();c_count=[0];errors=[]
        def read8(_,a,v):
            try:v[0]=core.JaguarReadByte(a,2);return 0
            except Exception as error:errors.append(repr(error));return 1
        def read32(_,a,v):
            try:v[0]=core.DSPReadLong(a,2);return 0
            except Exception as error:errors.append(repr(error));return 1
        def write32(_,a,v):
            try:core.DSPWriteLong(a,v,2);return 0
            except Exception as error:errors.append(repr(error));return 1
        def observe(_,pc):c_trace.update(struct.pack('>I',pc));c_count[0]+=1
        callbacks=[dsp.R8(read8),dsp.R32(read32),dsp.W32(write32),dsp.OBS(observe)];bus=dsp.Bus(*callbacks,None)
        before_counter=counter.value;completed=0;results=[]
        for index,frame in enumerate(frames):
            status=run(c.byref(bus),c.byref(s),frame['blocks']-completed);completed=frame['blocks']
            expected=bytes.fromhex(frame['DSP_hex']);actual=dsp.logical(s);h=hardware(s)
            if status not in [0,4]or actual!=expected or sha(runtime.device.ram())!=frame['RAM_sha256']or h!=frame['hardware']or c_trace.hexdigest()!=frame['PC_trace_sha256']or s.instructions!=frame['instructions']or media.scheduler.cpu_dict(runtime.cpu())!=frame['CPU']:
                (out/'native-mismatch-DSP.bin').write_bytes(expected);(out/'C-mismatch-DSP.bin').write_bytes(actual)
                save(out/'mismatch.json',dict(index=index,blocks=completed,status=status,C_PC=hex(s.pc),native_PC=hex(struct.unpack_from('=I',expected,8192)[0]),DSP_differences=[i for i,(x,y)in enumerate(zip(expected,actual))if x!=y][:50],RAM_match=sha(runtime.device.ram())==frame['RAM_sha256'],hardware_C=h,hardware_native=frame['hardware'],C_trace=c_trace.hexdigest(),native_trace=frame['PC_trace_sha256'],C_instructions=s.instructions,native_instructions=frame['instructions'],errors=errors));raise AssertionError(str(out/'mismatch.json'))
            assert counter.value==before_counter and c_count[0]==s.instructions
            results.append(dict(index=index,blocks=completed,instructions=s.instructions,PC=hex(s.pc),all_logical_DSP_CPU_RAM_hardware_trace_counts_matched=True))
        assert s.local_RAM[:4]==list(bytes.fromhex('03d0dead')) and not s.control&1
        (out/'C-final-DSP.bin').write_bytes(dsp.logical(s));save(out/'checkpoint-comparisons.json',results)
        bad=dsp.state_from_raw(incoming);bad.local_RAM[0x2ec]^=1;before=bytes(bad);guard=run(c.byref(bus),c.byref(bad),1);assert guard==7 and bytes(bad)==before
        save(out/'status.json',dict(status='comparisons_matched_pending_emulator_shutdown'))
        runtime.oracle.close();closed=True
        report=dict(status='source_firmware_DSP_guarded_decryption_and_ROM_check_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=1,source_instruction_coverage=[len(coverage),len(rows)],execution_blocks=completed,instructions=s.instructions,checkpoints=len(frames),success_word='0x03d0dead',source_GO_cleared=True,original_DSP_instructions_on_C_path=0,logical_DSP8496_bothbanks_CPU_private2MBRAM_peripherals_PC_trace_counts_match=True,changed_live_instruction_guard=dict(status=guard,CPU_state_unchanged=True),initial_fixture_origin=str(discovery),initial_fixture_DSP_sha256=sha(incoming[:8496]),source_BIOS_sha256=mapping['source_BIOS_sha256'],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,emulator_shutdown_completed=True,implementation_authorship='coordinator',local_model_authored_bodies_added=0,decrypted_code_host_copy=False,linked_into_C_firmware_boot=False,full_firmware_boot_verified=False,whole_game_complete=False,limits=['One pinned retail userROM path and incoming fixture derived by originalCPU ROM802000->500D6->firstDSP wait. Both standalone paths use supplied initial peripheral resets; this is not an uninterrupted reconstructed firmware boot.', 'Live byte guards cover462observed instructions, including the source-produced plaintext kernel. Unreached failure branches/otherROMkeys/mutatedROM authentication semantics remain unimplemented.233DSP microstate bytes excluded; logical8496 bytes/bothbanks,fullCPU/privateRAM/peripherals,executed-PC trace and instruction counts compared at first-use and periodic checkpoints.', 'GPU drawing shutdown, authenticated disc-header transport/loading, originalCPU dependencies beyond49instructionbootstrap/global scheduling and natural firmware-to-game dispatch remain. Success word comes from executed arithmetic/ROM check, never a host magic-value write.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/firmware-DSP-auth-checks.json',report)
        print(json.dumps({k:report[k]for k in ['status','directory','source_instruction_coverage','execution_blocks','instructions','checkpoints','success_word']}),flush=True)
    except BaseException as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:
        if not closed:runtime.oracle.close()

if __name__=='__main__':main()

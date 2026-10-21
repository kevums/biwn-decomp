"""Observe natural ROM bootstrap -> relocated main and first unmet dependency.

Source CPU execution only; no decoder runs the program. Decoder listings
are made afterward from actually visited instruction addresses. This is a
bounded observation, not authenticated firmware boot or a C match proof.
"""
import ctypes as c
import argparse
import os,subprocess
import hashlib,json,struct
from collections import Counter,deque
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_firmware_relocation_cpu as relocation
import check_biwn_media_setup_cpu as media
import generate_biwn_entry_setup_cpu as generation
import check_biwn_dsp_media_audio as dsp
import check_biwn_movie_GPU as firmware_gpu_state
from check_biwn_main_GPU_boot import W16 as firmware_W16

ROOT=media.ROOT;save=media.save;sha=media.sha

def run_firmware_GPU_C(runtime,incoming_GPU,budget,observer):
    import check_biwn_firmware_GPU_renderer as renderer
    gbuffer=c.create_string_buffer(12000)
    checked=json.loads((ROOT/'verification/firmware-GPU-renderer-checks.json').read_text());assert checked['emulator_shutdown_completed']
    helper=c.CDLL(str(Path(checked['directory'])/'libfirmware-GPU-renderer.dylib'));fn=helper.biwn_firmware_GPU_renderer_run;fn.argtypes=[c.POINTER(renderer.Bus),c.POINTER(firmware_gpu_state.State),c.c_uint32];fn.restype=c.c_int
    source_state=firmware_gpu_state.state_from_raw(incoming_GPU);counter=c.c_uint32.in_dll(runtime.core,'gpu_exec_opcode_count');counter_before=counter.value
    runtime.core.GPUStateLoad.argtypes=[c.c_void_p];runtime.core.GPUStateLoad.restype=c.c_size_t
    runtime.core.GPUReadByte.argtypes=[c.c_uint32,c.c_uint32];runtime.core.GPUReadByte.restype=c.c_uint8
    runtime.core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.GPUReadWord.restype=c.c_uint16
    runtime.core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];runtime.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    def sync(_,pointer,after):
        try:
            if after==0:
                image=bytearray(incoming_GPU);image[:4396]=firmware_gpu_state.logical(pointer.contents);assert runtime.core.GPUStateLoad(c.create_string_buffer(bytes(image)))==4416
            else:
                assert runtime.savers['GPU'](gbuffer)==4416;loaded=firmware_gpu_state.state_from_raw(gbuffer.raw[:4416]);loaded.instructions=pointer.contents.instructions;c.memmove(pointer,c.byref(loaded),c.sizeof(loaded))
            return 0
        except Exception as error:sync_errors.append(repr(error));return 1
    sync_errors=[]
    callbacks=[firmware_gpu_state.R8(lambda _,a,v:(v.__setitem__(0,runtime.core.GPUReadByte(a,3)),0)[1]),firmware_gpu_state.R16(lambda _,a,v:(v.__setitem__(0,runtime.core.GPUReadWord(a,3)),0)[1]),firmware_gpu_state.R32(lambda _,a,v:(v.__setitem__(0,runtime.core.GPUReadLong(a,3)),0)[1]),firmware_W16(lambda _,a,v:(runtime.core.GPUWriteWord(a,v,3),0)[1]),firmware_gpu_state.W32(lambda _,a,v:(runtime.core.GPUWriteLong(a,v,3),0)[1]),renderer.OBS(observer),renderer.SYNC(sync)];bus=renderer.Bus(*callbacks,None)
    status=fn(c.byref(bus),c.byref(source_state),budget)
    assert not sync_errors,sync_errors
    assert counter.value==counter_before
    image=bytearray(incoming_GPU);image[:4396]=firmware_gpu_state.logical(source_state);assert runtime.core.GPUStateLoad(c.create_string_buffer(bytes(image)))==4416
    return status,source_state

def run_firmware_post_GPU_CPU_C(runtime,out,initial,budget,observer):
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfirmware-post-GPU-CPU.dylib'
    build=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_firmware_post_GPU_cpu.c'),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'post-GPU-CPU-compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    loaded=c.CDLL(str(library));fn=loaded.biwn_firmware_post_GPU_cpu_call
    fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int
    types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8]
    def reader(width):return lambda _,a,v:(v.__setitem__(0,runtime.read(a,width)),0)[1]
    def writer(width):return lambda _,a,v:(runtime.write(a,width,v),0)[1]
    cbs=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
    bus=media.Bus(*cbs[:5],media.scheduler.cleanup.world.CALL(),None,0)
    service=media.world_cpu.SERVICE(observer);translated=media.CPU.from_buffer_copy(bytes(initial))
    before=bytes(runtime.cpu());status=fn(c.byref(bus),c.byref(translated),cbs[5],service,None,budget,0)
    assert bytes(runtime.cpu())==before,'Shared core CPU must not execute during reconstructed main CPU phase'
    return status,translated

def CD_diagnostics(runtime):
    names=['BUTCH_ticks','FIFO_IRQs','DSA_IRQs','FIFO_reads','seeks','global_interrupt_disabled','HLE_bytes'];values=[c.c_uint32()for _ in names]
    fn=runtime.core.CDROMDiagGetCounters;fn.argtypes=[c.POINTER(c.c_uint32)]*7;fn(*[c.byref(v)for v in values]);result={k:v.value for k,v in zip(names,values)}
    extra=[c.c_uint32()for _ in range(3)];fn=runtime.core.CDROMDiagGetSeekWedgeState;fn.argtypes=[c.POINTER(c.c_uint32)]*3;fn(*[c.byref(v)for v in extra]);result.update(dict(zip(['seek_starts','seek_completions','FIFO_drains'],[v.value for v in extra])))
    for name in ['CDROMDiagGetButchIntCtrl','CDROMDiagGetI2SCtrl']:
        fn=getattr(runtime.core,name);fn.restype=c.c_uint8;result[name]=fn()
    if hasattr(runtime.core,'ButchIsReadyToSend'):
        runtime.core.ButchIsReadyToSend.restype=c.c_bool;result['BUTCH_ready_for_SSI']=runtime.core.ButchIsReadyToSend()
    else:result['BUTCH_ready_for_SSI']=None
    runtime.core.CDROMDiagGetFirstSeekBlock.restype=c.c_uint32;result['first_seek_LBA']=runtime.core.CDROMDiagGetFirstSeekBlock()
    result['BUTCH_control']=hex(runtime.core.DSPReadLong(0xdfff00,2));return result

def SSI_clock_registers(runtime):
    # SMODE/SCLK are write-only; ordinary bus reads do not expose the stored configuration.
    mode=c.POINTER(c.c_uint32).in_dll(runtime.core,'smode').contents.value
    divider=c.POINTER(c.c_uint8).in_dll(runtime.core,'sclk').contents.value
    return mode,divider


def deliver_SSI(runtime,swap_diagnostic,previous_right_diagnostic):
    runtime.core.JERRYI2SCallback()
    mode,divider=SSI_clock_registers(runtime)
    runtime.SSI_register_samples[(mode,divider)]+=1
    left=c.c_uint16.in_dll(runtime.core,'lrxd');right=c.c_uint16.in_dll(runtime.core,'rrxd')
    before=(left.value,right.value)
    if previous_right_diagnostic:
        right.value=runtime.SSI_previous_right_word;runtime.SSI_previous_right_word=before[1]
        runtime.SSI_previous_right_applications+=1
    if swap_diagnostic:
        left=c.c_uint16.in_dll(runtime.core,'lrxd');right=c.c_uint16.in_dll(runtime.core,'rrxd')
        left.value,right.value=right.value,left.value
        runtime.SSI_receive_swaps+=1
    bus_left=runtime.core.DSPReadLong(0xf1a148,2)&0xffff;bus_right=runtime.core.DSPReadLong(0xf1a14c,2)&0xffff
    assert (bus_left,bus_right)==(left.value,right.value),'Peripheral swap globals must match source bus reads'
    if len(runtime.SSI_pair_samples)<12 or ((bus_right<<16)|bus_left)==0x41545249:
        if len(runtime.SSI_pair_samples)<64:runtime.SSI_pair_samples.append(dict(callback=sum(runtime.SSI_register_samples.values()),stored_SMODE=mode,stored_SCLK=divider,before=list(before),after=[bus_left,bus_right],source_packed_word=hex((bus_right<<16)|bus_left)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-first-DSP',action='store_true');parser.add_argument('--DSP-budget',type=int,default=100000);parser.add_argument('--DSP-quantum',type=int,default=1);parser.add_argument('--DSP-C',action='store_true');parser.add_argument('--continue-CPU',action='store_true');parser.add_argument('--probe-GPU-shutdown',action='store_true');parser.add_argument('--probe-CPU-video-IRQ',action='store_true');parser.add_argument('--video-IRQ-C',action='store_true');parser.add_argument('--resume-GPU-after-IRQ',action='store_true');parser.add_argument('--GPU-renderer-C',action='store_true');parser.add_argument('--GPU-initial-wait-C',action='store_true');parser.add_argument('--continue-CPU-after-GPU',action='store_true');parser.add_argument('--post-GPU-CPU-C',action='store_true');parser.add_argument('--advance-video-events',type=int,default=0);parser.add_argument('--attach-CDI',action='store_true');parser.add_argument('--DSP-ROM-view-mame-diagnostic',action='store_true');parser.add_argument('--DSP-boot-probe-C',action='store_true');parser.add_argument('--CPU-continuation-budget',type=int,default=300000);parser.add_argument('--BUTCH-clock-from-CPU-cycles',action='store_true');parser.add_argument('--run-second-DSP',action='store_true');parser.add_argument('--second-DSP-budget',type=int,default=2000000);parser.add_argument('--continue-CPU-after-second-DSP',action='store_true');parser.add_argument('--run-third-DSP',action='store_true');parser.add_argument('--third-DSP-budget',type=int,default=3000000);parser.add_argument('--continue-CPU-after-third-DSP',action='store_true');parser.add_argument('--run-CD-descriptor-DSP',action='store_true');parser.add_argument('--continue-CPU-after-CD-descriptor',action='store_true');parser.add_argument('--run-CD-header-DSP',action='store_true');parser.add_argument('--initialize-third-DSP-at-source-GO',action='store_true');parser.add_argument('--run-CD-read-command-DSP',action='store_true');parser.add_argument('--continue-CPU-after-CD-read-command',action='store_true');parser.add_argument('--continue-CPU-after-CD-header',action='store_true');parser.add_argument('--SSI-receive-word-swap-diagnostic',action='store_true');parser.add_argument('--SSI-previous-right-word-diagnostic',action='store_true');parser.add_argument('--run-header-auth-DSP',action='store_true');parser.add_argument('--continue-CPU-after-header-auth',action='store_true');parser.add_argument('--run-auth-result-DSP',action='store_true');parser.add_argument('--continue-CPU-after-auth-result',action='store_true');parser.add_argument('--advance-CD-challenge-phases',type=int,default=0);parser.add_argument('--diagnostic-core',type=Path);parser.add_argument('--force-repeated-seek-diagnostic',action='store_true');parser.add_argument('--run-fourth-DSP',action='store_true');parser.add_argument('--advance-fourth-DSP-phases',type=int,default=0);parser.add_argument('--initialize-fourth-DSP-at-source-GO',action='store_true');parser.add_argument('--TOC-origin-diagnostic',action='store_true');parser.add_argument('--TOC-read-origin-diagnostic',action='store_true');parser.add_argument('--fourth-DSP-budget',type=int);parser.add_argument('--post-auth-video-events',type=int,default=0);args=parser.parse_args();assert 0<args.CPU_continuation_budget<=10000000;assert 0<=args.advance_video_events<=32
    assert args.DSP_budget>0 and 1<=args.DSP_quantum<=1000
    if args.DSP_boot_probe_C:args.DSP_C=True
    if args.DSP_ROM_view_mame_diagnostic:assert args.DSP_C or args.run_first_DSP
    prior=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text())
    assert prior['emulator_shutdown_completed'] and prior['initial_RAM_domain']=='zero-filled main RAM'
    proof=Path(prior['directory']);mapping=json.loads((proof/'protocol.json').read_text())['source_mapping']
    out=ROOT/'verification/BIWN-relocated-firmware-observation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    protocol=dict(status='running',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source_BIOS_sha256=mapping['BIOS_sha256'],pinned_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),interface='pinned original 68000, single instruction steps',initial_RAM='zero-filled2MB; supplied userBIOSROM and CPU/device seed',initial_PC='0x802000',initial_SR='0x2700',initial_stack='0x1ff000',supplied_event_schedule='Optional controlled firstDSP and GPUshutdown steps while CPU waits; no physical/global controller/VBI/timer schedule',disc_attached=False,whole_game_complete=False,full_firmware_boot_verified=False,emulator_BIOS_boot_stub_injection_and_GPU_magic_stomp_disabled=True,emulator_shortcut_bookkeeping_fixture='JaguarCDBiosStateLoad magicCDB1, injected flag1 after CPU initialization. No stub injected or source bytes changed; flag prevents host shortcuts, does not authenticate source boot.')
    protocol['SSI_receive_word_swap_diagnostic']=dict(selected=args.SSI_receive_word_swap_diagnostic,scope='After every actual pinned JERRYI2SCallback in third-DSP phases, exchange actual16bit LRXD/RRXD. Record stored SMODE/SCLK and application count. Supplied diagnostic peripheral-input transform, not hardware-verified channel or strobe behavior. No RAM/header/payload copy, core/BIOS source unchanged.')
    protocol['SSI_previous_right_word_diagnostic']=dict(selected=args.SSI_previous_right_word_diagnostic,scope='Keep current callback LRXD and previous callback RRXD. Declared one-word temporal receive provider, not hardware-verified strobe timing. Never copies payload/header to RAM.')
    assert not(args.SSI_receive_word_swap_diagnostic and args.SSI_previous_right_word_diagnostic)
    assert not args.force_repeated_seek_diagnostic or args.diagnostic_core
    assert not args.TOC_origin_diagnostic or args.diagnostic_core
    assert not args.TOC_read_origin_diagnostic or args.TOC_origin_diagnostic
    assert args.fourth_DSP_budget is None or 0<args.fourth_DSP_budget<=80000000
    protocol["TOC_read_origin_diagnostic"]=args.TOC_read_origin_diagnostic
    protocol["TOC_origin_diagnostic"]=args.TOC_origin_diagnostic
    protocol['execution_core_path']=str(args.diagnostic_core or ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib')
    protocol['execution_core_sha256']=sha(Path(protocol['execution_core_path']).read_bytes())
    protocol['force_repeated_seek_diagnostic']=args.force_repeated_seek_diagnostic
    protocol['core_scope']='Separate test core when selected; pinned hash is reference, execution_core_sha256 is actual. Force-reseek switch is an unverified diagnostic drive input. No hardware fix or game completion claim.'
    save(out/'protocol.json',protocol);print(out,flush=True)
    runtime=relocation.Runtime(proof/'libfirmware-relocation.dylib',mapping['instructions_decoded'],diagnostic_core=args.diagnostic_core);runtime.SSI_receive_swaps=0;runtime.SSI_register_samples=Counter();runtime.SSI_pair_samples=[];runtime.SSI_previous_right_word=0;runtime.SSI_previous_right_applications=0;closed=False
    if hasattr(runtime.core,'BlitterStateSave'):
        runtime.core.BlitterStateSave.argtypes=[c.c_void_p];runtime.core.BlitterStateSave.restype=c.c_size_t;runtime.savers['Blitter']=runtime.core.BlitterStateSave
    try:
        ram=bytes(0x200000);runtime.reset(ram,0)
        if args.attach_CDI:
            disc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert disc.stat().st_size==669867743
            runtime.core.CDIntfOpenImage.argtypes=[c.c_char_p];runtime.core.CDIntfOpenImage.restype=c.c_bool
            assert runtime.core.CDIntfOpenImage(os.fsencode(disc));runtime.core.CDROMInit();runtime.core.CDROMReset()
            if args.diagnostic_core:
                runtime.core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];runtime.core.BIWNDiagnosticRepeatSeek.restype=None;runtime.core.BIWNDiagnosticRepeatSeek(int(args.force_repeated_seek_diagnostic))
            if args.TOC_origin_diagnostic:
                runtime.core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];runtime.core.BIWNDiagnosticTOCOrigin.restype=None;runtime.core.BIWNDiagnosticTOCOrigin(3 if args.TOC_read_origin_diagnostic else 1)
            if os.environ.get('VJ_CD_TRACE')=='1':
                runtime.core.CDTraceSetEnabled.argtypes=[c.c_int];runtime.core.CDTraceSetEnabled(1)
            protocol.update(disc_attached=True,disc_image=str(disc),disc_image_bytes=disc.stat().st_size,disc_interface='Pinned CDIntfOpenImage/CDROMInit/CDROMReset; no extracted boot payload hostcopy');save(out/'protocol.json',protocol)
        initial=media.CPU();initial.pc=0x802000;initial.sr=0x2700;initial.registers[15]=initial.ssp=0x1ff000;initial.usp=0x180000;runtime.seed_cpu(initial)
        runtime.core.JaguarCDBiosStateLoad.argtypes=[c.c_void_p];runtime.core.JaguarCDBiosStateLoad.restype=c.c_size_t
        runtime.core.JaguarCDBiosStateSave.argtypes=[c.c_void_p];runtime.core.JaguarCDBiosStateSave.restype=c.c_size_t
        shortcut_fixture=struct.pack('<I',0x31424443)+b'\x01'
        assert runtime.core.JaguarCDBiosStateLoad(c.create_string_buffer(shortcut_fixture))==5
        shortcut_check=c.create_string_buffer(5);assert runtime.core.JaguarCDBiosStateSave(shortcut_check)==5 and shortcut_check.raw==shortcut_fixture
        counts=Counter();trace=hashlib.sha256();changes=[];signatures=Counter();boundary=None;last=None;stop='instruction_budget';repeated=None
        runtime.core.GPUGetPC.restype=c.c_uint32
        runtime.core.DSPGetPC.restype=c.c_uint32
        runtime.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];runtime.core.GPUReadLong.restype=c.c_uint32
        runtime.core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];runtime.core.DSPReadLong.restype=c.c_uint32
        for step in range(300000):
            pc=runtime.core.m68k_get_reg(None,16)
            if pc==0x500d6 and boundary is None:
                boundary=dict(step=step,CPU=media.scheduler.cpu_dict(runtime.cpu()),hardware=runtime.snapshot()['hardware'],RAM_sha256=sha(runtime.device.ram()))
                (out/'RAM-at-relocated-entry.bin').write_bytes(runtime.device.ram());save(out/'relocated-entry.json',boundary)
            if boundary is not None:
                state=runtime.cpu();signature=bytes(state);signatures[signature]+=1
                if signatures[signature]>=64:
                    stop='repeated_exact_CPU_state_without_explicit_device_events';repeated=dict(PC=hex(pc),repetitions=signatures[signature],CPU=media.scheduler.cpu_dict(state));break
                if pc<0x200000 or 0x800000<=pc<0x840000:
                    pass
                else:
                    stop='unexpected_execution_address';repeated=dict(PC=hex(pc));break
            if last is None or pc!=last+runtime.rows.get(last,{}).get('size',0):
                if len(changes)<300:changes.append(dict(step=step,from_PC=hex(last)if last is not None else None,to_PC=hex(pc)))
            counts[pc]+=1;trace.update(struct.pack('>I',pc));last=pc;runtime.core.m68k_execute(1)
        state=runtime.cpu();final=runtime.device.ram();(out/'RAM-final.bin').write_bytes(final)
        DSP_buffer=c.create_string_buffer(12000);DSP_size=runtime.savers['DSP'](DSP_buffer);assert DSP_size==8729
        DSP_initial=DSP_buffer.raw[:DSP_size];(out/'DSP-at-CPU-wait.bin').write_bytes(DSP_initial)
        first_DSP=None
        original_ROM_header=c.string_at(runtime.rom+0x408,4)
        if args.DSP_ROM_view_mame_diagnostic:
            assert original_ROM_header==bytes.fromhex('00000001')
            c.memmove(runtime.rom+0x408,bytes.fromhex('00000005'),4)
            protocol.update(DSP_only_ROM_header_diagnostic=dict(address='0x800408',original_CPU_view=1,temporary_DSP_view=5,method='Temporary in-memory ROM data word while CPU held; restored before CPU continuation. Original BIOS file untouched.',hardware_behavior_verified=False,reference='MAME jaguarcd_state::cd_bios_r reset workaround',source_magic_result_injection=False));save(out/'protocol.json',protocol)
        if args.DSP_C:
            assert state.pc==0x5021c and stop=='repeated_exact_CPU_state_without_explicit_device_events'
            checked=json.loads((ROOT/'verification/firmware-DSP-auth-checks.json').read_text());assert checked['emulator_shutdown_completed']
            if args.DSP_boot_probe_C:
                src=ROOT/'projects/black-ice-white-noise/restoration';target=out/'libfirmware-DSP-boot-probe.dylib'
                build=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_firmware_DSP_boot_probe.c'),'-o',str(target)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'DSP-boot-probe-compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
                library=c.CDLL(str(target));fn=library.biwn_firmware_DSP_boot_probe_run
            else:
                library=c.CDLL(str(Path(checked['directory'])/'libfirmware-DSP-auth.dylib'));fn=library.biwn_firmware_DSP_auth_run
            fn.argtypes=[c.POINTER(dsp.Bus),c.POINTER(dsp.State),c.c_uint32];fn.restype=c.c_int
            runtime.core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadByte.restype=c.c_uint8
            runtime.core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
            runtime.core.DSPStateLoad.argtypes=[c.c_void_p];runtime.core.DSPStateLoad.restype=c.c_size_t
            DSP_trace=hashlib.sha256();DSP_counts=Counter()
            def observe(_,pc):DSP_trace.update(struct.pack('>I',pc));DSP_counts[pc]+=1
            callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,runtime.core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,runtime.core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(runtime.core.DSPWriteLong(a,v,2),0)[1]),dsp.OBS(observe)]
            bus=dsp.Bus(*callbacks,None);translated=dsp.state_from_raw(DSP_initial)
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');before=counter.value
            status=fn(c.byref(bus),c.byref(translated),12000000);assert status==0,status
            assert counter.value==before and bytes(runtime.cpu())==bytes(state)
            mirrored=bytearray(DSP_initial);mirrored[:8496]=dsp.logical(translated)
            assert runtime.core.DSPStateLoad(c.create_string_buffer(bytes(mirrored)))==len(mirrored)
            assert runtime.savers['DSP'](DSP_buffer)==8729;DSP_after=DSP_buffer.raw[:8729]
            assert DSP_after[:8496]==dsp.logical(translated)
            (out/'DSP-after-first-program.bin').write_bytes(DSP_after);(out/'RAM-after-first-DSP.bin').write_bytes(runtime.device.ram())
            first_DSP=dict(status='source_firmware_DSP_C_from_live_natural_CPU_loader_state',stop_reason='source_DSP_GO_cleared',instructions=translated.instructions,CPU_held_at=hex(state.pc),CPU_state_unchanged=bytes(runtime.cpu())==bytes(state),initial_DSP_PC=hex(struct.unpack_from('=I',DSP_initial,8192)[0]),final_DSP_PC=hex(translated.pc),final_control=translated.control,initial_DSP_bank=DSP_initial[8495],final_DSP_bank=DSP_after[8495],PC_trace_sha256=DSP_trace.hexdigest(),PC_trace_scope='every compiled original-source instruction, including branch delay slots',initial_logical_DSP_sha256=sha(DSP_initial[:8496]),final_logical_DSP_sha256=sha(DSP_after[:8496]),main_RAM_sha256=sha(runtime.device.ram()),header_word_F1B000=runtime.core.DSPReadLong(0xf1b000,0),hardware=runtime.snapshot()['hardware'],observed_C_PC_counts={hex(k):v for k,v in sorted(DSP_counts.items())},source_C_verified=True,original_DSP_instructions_on_C_path=0,live_CPU_loader_state_used=True,earlier_DSP_boundary_hostloaded=False,decrypted_code_host_copy=False,pipeline_tail='Retained initial233byte pipeline tail when mirroring C logicalDSP into the shared peripheral bus; excluded from equivalence, as declared.')
            save(out/'first-DSP-observation.json',first_DSP)
        elif args.run_first_DSP:
            assert state.pc==0x5021c and stop=='repeated_exact_CPU_state_without_explicit_device_events'
            runtime.core.DSPExec.argtypes=[c.c_int32]
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');begin=counter.value
            DSP_counts=Counter();DSP_trace=hashlib.sha256();DSP_words={};DSP_signatures=Counter();recent=deque();DSP_stop='budget'
            for block in range(args.DSP_budget):
                pc=runtime.core.DSPGetPC();control=runtime.core.DSPReadLong(0xf1a114,0)
                if not control&1:DSP_stop='source_DSP_GO_cleared';break
                if not 0xf1b000<=pc<0xf1d000:DSP_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6)
                word=int.from_bytes(raw6[:2],'big');size=6 if word>>10==38 else 2;raw=raw6[:size]
                assert pc not in DSP_words or DSP_words[pc]==raw,'SourceDSP self-modification requires separate listing'
                DSP_words[pc]=raw;DSP_counts[pc]+=1;DSP_trace.update(struct.pack('>I',pc))
                before=counter.value;runtime.core.DSPExec(args.DSP_quantum)
                if args.DSP_quantum==1 and ((counter.value-before)&0xffffffff)>1 and word>>10 in [52,53]:
                    delay=pc+2;delayraw=c.string_at(location+2,6);delayword=int.from_bytes(delayraw[:2],'big');size=6 if delayword>>10==38 else 2
                    DSP_words[delay]=delayraw[:size];DSP_counts[delay]+=1;DSP_trace.update(struct.pack('>I',delay))
                if block%1024==0:
                    assert runtime.savers['DSP'](DSP_buffer)==8729
                    signature=hashlib.sha256(DSP_buffer.raw[:8496]).digest();DSP_signatures[signature]+=1;recent.append(signature)
                    if len(recent)>8192:DSP_signatures[recent.popleft()]-=1
                    if DSP_signatures[signature]>=64:DSP_stop='repeated_DSP_state';break
                if block and block%2000000==0:
                    print(json.dumps(dict(DSP_execution_blocks=block,PC=hex(pc))),flush=True)
            DSP_after=DSP_buffer.raw[:8729];assert runtime.savers['DSP'](DSP_buffer)==8729;DSP_after=DSP_buffer.raw[:8729]
            (out/'DSP-after-first-program.bin').write_bytes(DSP_after);(out/'RAM-after-first-DSP.bin').write_bytes(runtime.device.ram())
            DSP_rows=[{**generation.loader.base.binary_tools.jaguar_instructions(raw,pc,'dsp')[0][0],'count':DSP_counts[pc]}for pc,raw in sorted(DSP_words.items())]
            first_DSP=dict(status='native_only_controlled_first_firmware_DSP_observation',stop_reason=DSP_stop,blocks=block,instructions=(counter.value-begin)&0xffffffff,CPU_held_at=hex(state.pc),CPU_state_unchanged=bytes(runtime.cpu())==bytes(state),initial_DSP_PC=hex(struct.unpack_from('=I',DSP_initial,8192)[0]),final_DSP_PC=hex(runtime.core.DSPGetPC()),final_control=runtime.core.DSPReadLong(0xf1a114,0),initial_DSP_bank=DSP_initial[8495],final_DSP_bank=DSP_after[8495],PC_trace_sha256=DSP_trace.hexdigest(),initial_logical_DSP_sha256=sha(DSP_initial[:8496]),final_logical_DSP_sha256=sha(DSP_after[:8496]),main_RAM_sha256=sha(runtime.device.ram()),header_word_F1B000=runtime.core.DSPReadLong(0xf1b000,0),hardware=runtime.snapshot()['hardware'],visited_instructions=DSP_rows,source_C_verified=False)
            first_DSP.update(execution_quantum=args.DSP_quantum,PC_trace_scope='every execution block and taken delay instruction'if args.DSP_quantum==1 else'onePCsampleperDSPExec quantum; not complete instruction coverage')
            save(out/'first-DSP-observation.json',first_DSP)
        if args.DSP_ROM_view_mame_diagnostic:
            assert bytes(runtime.cpu())==bytes(state)
            c.memmove(runtime.rom+0x408,original_ROM_header,4);assert c.string_at(runtime.rom+0x408,4)==original_ROM_header
            protocol['DSP_only_ROM_header_diagnostic']['restored_before_CPU_continuation']=True;save(out/'protocol.json',protocol)
            first_DSP.update(DSP_ROM_header_diagnostic=True,hardware_ROM_view_verified=False);save(out/'first-DSP-observation.json',first_DSP)
        continuation=None
        if args.continue_CPU and first_DSP and not first_DSP['final_control']&1:
            ccounts=Counter();seen=Counter();ctrace=hashlib.sha256();cstop='budget';CD_ticks=0;CPU_cycles=0;CD_cycle_remainder=0
            if args.BUTCH_clock_from_CPU_cycles:
                runtime.core.BUTCHExec.argtypes=[c.c_uint32];runtime.core.JaguarGetHalflinePeriodUs.restype=c.c_double
                halfline_us=runtime.core.JaguarGetHalflinePeriodUs();cycle_us=(0.03760684198 if halfline_us<32 else 0.03760260812)*2
                CD_tick_period_CPU_cycles=int(halfline_us/cycle_us+0.5)
                protocol.update(CD_clock_provider=dict(method='BUTCHExec once per pinned halfline equivalent in returned original CPU cycles, only after first DSP completion',halfline_us=halfline_us,CPU_cycle_us=cycle_us,CPU_cycles_per_BUTCH_tick=CD_tick_period_CPU_cycles,global_physical_schedule_verified=False,DSP_GPU_video_timing_not_advanced=True));save(out/'protocol.json',protocol)
            for cstep in range(args.CPU_continuation_budget):
                pc=runtime.core.m68k_get_reg(None,16);s=runtime.cpu();seen[bytes(s)]+=1
                if seen[bytes(s)]>=64:cstop='repeated_CPU_state_after_first_DSP';break
                ccounts[pc]+=1;ctrace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);CPU_cycles+=cycles
                if args.BUTCH_clock_from_CPU_cycles:
                    CD_cycle_remainder+=cycles
                    while CD_cycle_remainder>=CD_tick_period_CPU_cycles:
                        runtime.core.BUTCHExec(0);CD_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            (out/'RAM-after-CPU-continuation.bin').write_bytes(runtime.device.ram())
            continuation=dict(status='native_only_natural_CPU_continuation_after_first_DSP',stop_reason=cstop,steps=sum(ccounts.values()),PC_trace_sha256=ctrace.hexdigest(),PC_visits={hex(k):v for k,v in sorted(ccounts.items())},CPU=media.scheduler.cpu_dict(runtime.cpu()),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CPU_reseeded=False)
            continuation.update(CD_clock_ticks=CD_ticks,returned_CPU_cycles=CPU_cycles,CD_cycle_remainder=CD_cycle_remainder,CD_clock_from_CPU_cycles=args.BUTCH_clock_from_CPU_cycles)
            save(out/'CPU-continuation.json',continuation)
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-at-continued-CPU-wait.bin').write_bytes(DSP_buffer.raw[:8729])
        second_DSP=None
        if args.run_second_DSP:
            assert args.BUTCH_clock_from_CPU_cycles and continuation and continuation['CPU']['pc']==0x5048e
            assert runtime.savers['DSP'](DSP_buffer)==8729;second_initial=DSP_buffer.raw[:8729]
            second_CPU=bytes(runtime.cpu());second_words={};second_counts=Counter();second_trace=hashlib.sha256();second_byte_trace=hashlib.sha256();second_seen=Counter();second_stop='budget';second_ticks=second_delays=second_blocks=0;RISC_remainder=0;header_completion=None
            runtime.core.DSPExec.argtypes=[c.c_int32];counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');second_counter_start=counter.value
            RISC_cycles_per_CD_tick=CD_tick_period_CPU_cycles*2
            for block in range(args.second_DSP_budget):
                pc=runtime.core.DSPGetPC()
                if runtime.core.DSPReadLong(0xf1b000,0)==0 and header_completion is None:header_completion=dict(execution_blocks=second_blocks,instructions=(counter.value-second_counter_start)&0xffffffff,PC=hex(pc))
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:second_stop='source_DSP_GO_cleared';break
                if not 0xf1b000<=pc<0xf1d000:second_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');size=6 if word>>10==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);second_words[key]=payload;second_counts[key]+=1;second_trace.update(struct.pack('>I',pc));second_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;second_blocks+=1
                if consumed>1 and word>>10 in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');size=6 if dw>>10==38 else 2;payload_delay=delay6[:size];key=(delay,payload_delay);second_words[key]=payload_delay;second_counts[key]+=1;second_trace.update(struct.pack('>I',delay));second_byte_trace.update(struct.pack('>I',delay)+payload_delay);second_delays+=1
                RISC_remainder+=consumed
                while RISC_remainder>=RISC_cycles_per_CD_tick:
                    runtime.core.BUTCHExec(0);second_ticks+=1;RISC_remainder-=RISC_cycles_per_CD_tick
                if block%1024==0:
                    assert runtime.savers['DSP'](DSP_buffer)==8729;signature=sha(DSP_buffer.raw[:8496]);second_seen[signature]+=1
                    if second_seen[signature]>=64:second_stop='repeated_logical_DSP_state_with_CD_clock_only';break
            assert runtime.savers['DSP'](DSP_buffer)==8729;second_after=DSP_buffer.raw[:8729]
            (out/'DSP-after-second-program.bin').write_bytes(second_after);(out/'RAM-after-second-DSP.bin').write_bytes(runtime.device.ram())
            second_DSP=dict(status='native_second_firmware_DSP_discovery_after_diagnostic_ROM_view',stop_reason=second_stop,execution_blocks=second_blocks,instructions=(counter.value-second_counter_start)&0xffffffff,observed_branch_delays=second_delays,initial_PC=hex(struct.unpack_from('=I',second_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),header_word=runtime.core.DSPReadLong(0xf1b000,0),control=runtime.core.DSPReadLong(0xf1a114,0),logical_DSP_sha256=sha(second_after[:8496]),RAM_sha256=sha(runtime.device.ram()),CPU_state_unchanged=bytes(runtime.cpu())==second_CPU,CD_clock_ticks=second_ticks,CD_tick_RISC_cycles=RISC_cycles_per_CD_tick,CD_tick_cycle_scope='Opcode-count cadence with source DSPExec1; pending pipeline/bus stalls and global GPU/CPU/SSI/video clocks are not modeled here.',PC_trace_sha256=second_trace.hexdigest(),instruction_byte_trace_sha256=second_byte_trace.hexdigest(),visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':second_counts[(pc,payload)]}for(pc,payload)in sorted(second_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_header_word_write=False,source_boot_stub_loaded=False,header_word_completion=header_completion)
            save(out/'second-DSP-observation.json',second_DSP);print(json.dumps({k:second_DSP[k]for k in ['stop_reason','instructions','final_PC','header_word','CD_clock_ticks']}),flush=True)
        after_second_CPU=None
        if args.continue_CPU_after_second_DSP:
            assert second_DSP and second_DSP['stop_reason']=='source_DSP_GO_cleared'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc
                if args.initialize_third_DSP_at_source_GO and pc==0x50976:after_stop='source_third_DSP_GO_started_before_read_command';break
                after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-second-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-second-CPU.bin').write_bytes(runtime.device.ram())
            after_second_CPU=dict(status='native_CPU_continuation_after_source_DSP_TOC_completion',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-second-DSP.json',after_second_CPU);print(json.dumps(dict(after_second_CPU_steps=after_second_CPU['steps'],PC=hex(after_second_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        third_DSP=None
        if args.run_third_DSP:
            assert after_second_CPU and after_second_CPU['final_CPU']['pc']==(0x50976 if args.initialize_third_DSP_at_source_GO else 0x509ec)
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;third_initial=DSP_buffer.raw[:8729];(out/'DSP-before-third-program.bin').write_bytes(third_initial)
            third_CPU=bytes(runtime.cpu());third_words={};third_counts=Counter();third_trace=hashlib.sha256();third_byte_trace=hashlib.sha256();third_stop='budget';third_blocks=third_delays=third_CD_ticks=third_SSI_events=third_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');third_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4c8,0)
                if flag&0x80000000 and any(key[0]==0xf1b078 for key in third_counts):third_stop='source_CD_read_mailbox_negative';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:third_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:third_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);third_words[key]=payload;third_counts[key]+=1;third_trace.update(struct.pack('>I',pc));third_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;third_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);third_words[key]=dr;third_counts[key]+=1;third_trace.update(struct.pack('>I',delay));third_byte_trace.update(struct.pack('>I',delay)+dr);third_delays+=1
                elapsed=int(costs[opcode]);third_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);third_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);third_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(third_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=third_SSI_events,CD_ticks=third_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;third_after=DSP_buffer.raw[:8729];(out/'DSP-after-third-program.bin').write_bytes(third_after);(out/'RAM-after-third-DSP.bin').write_bytes(runtime.device.ram())
            third_DSP=dict(status='native_third_DSP_CD_read_with_pinned_CD_SSI_callbacks',stop_reason=third_stop,execution_blocks=third_blocks,instructions=(counter.value-third_count_start)&0xffffffff,observed_branch_delays=third_delays,initial_PC=hex(struct.unpack_from('=I',third_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4c8,0)),SSI_events=third_SSI_events,CD_clock_ticks=third_CD_ticks,pinned_opcode_cycle_budget=third_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==third_CPU,logical_DSP_sha256=sha(third_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=third_trace.hexdigest(),instruction_byte_trace_sha256=third_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':third_counts[(pc,payload)]}for(pc,payload)in sorted(third_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'third-DSP-observation.json',third_DSP);print(json.dumps({k:third_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_third_CPU=None
        if args.continue_CPU_after_third_DSP:
            assert third_DSP and third_DSP['stop_reason']=='source_CD_read_mailbox_negative'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-third-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-third-CPU.bin').write_bytes(runtime.device.ram())
            after_third_CPU=dict(status='native_CPU_continuation_after_source_DSP_read_engine_initialization_ack',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-third-DSP.json',after_third_CPU);print(json.dumps(dict(after_third_CPU_steps=after_third_CPU['steps'],PC=hex(after_third_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        command_DSP=None
        if args.run_CD_read_command_DSP:
            assert after_third_CPU and after_third_CPU['final_CPU']['pc']==0x509ec
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;command_initial=DSP_buffer.raw[:8729];(out/'DSP-before-command-program.bin').write_bytes(command_initial)
            command_CPU=bytes(runtime.cpu());command_words={};command_counts=Counter();command_trace=hashlib.sha256();command_byte_trace=hashlib.sha256();command_stop='budget';command_blocks=command_delays=command_CD_ticks=command_SSI_events=command_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');command_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4c8,0)
                if flag&0x80000000 and command_blocks>0:command_stop='source_CD_read_command_acknowledged';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:command_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:command_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);command_words[key]=payload;command_counts[key]+=1;command_trace.update(struct.pack('>I',pc));command_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;command_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);command_words[key]=dr;command_counts[key]+=1;command_trace.update(struct.pack('>I',delay));command_byte_trace.update(struct.pack('>I',delay)+dr);command_delays+=1
                elapsed=int(costs[opcode]);command_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);command_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);command_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(command_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=command_SSI_events,CD_ticks=command_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;command_after=DSP_buffer.raw[:8729];(out/'DSP-after-command-program.bin').write_bytes(command_after);(out/'RAM-after-command-DSP.bin').write_bytes(runtime.device.ram())
            command_DSP=dict(status='native_command_DSP_CD_read_with_pinned_CD_SSI_callbacks',stop_reason=command_stop,execution_blocks=command_blocks,instructions=(counter.value-command_count_start)&0xffffffff,observed_branch_delays=command_delays,initial_PC=hex(struct.unpack_from('=I',command_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4c8,0)),SSI_events=command_SSI_events,CD_clock_ticks=command_CD_ticks,pinned_opcode_cycle_budget=command_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==command_CPU,logical_DSP_sha256=sha(command_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=command_trace.hexdigest(),instruction_byte_trace_sha256=command_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':command_counts[(pc,payload)]}for(pc,payload)in sorted(command_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'command-DSP-observation.json',command_DSP);print(json.dumps({k:command_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_command_CPU=None
        if args.continue_CPU_after_CD_read_command:
            assert command_DSP and command_DSP['stop_reason']=='source_CD_read_command_acknowledged'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-command-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-command-CPU.bin').write_bytes(runtime.device.ram())
            after_command_CPU=dict(status='native_CPU_continuation_after_source_DSP_read_command_ack',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-command-DSP.json',after_command_CPU);print(json.dumps(dict(after_command_CPU_steps=after_command_CPU['steps'],PC=hex(after_command_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        descriptor_DSP=None
        if args.run_CD_descriptor_DSP:
            descriptor_predecessor=after_command_CPU if args.continue_CPU_after_CD_read_command else after_third_CPU
            assert descriptor_predecessor and descriptor_predecessor['final_CPU']['pc']==0x50a4e
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;descriptor_initial=DSP_buffer.raw[:8729];(out/'DSP-before-descriptor-program.bin').write_bytes(descriptor_initial)
            descriptor_CPU=bytes(runtime.cpu());descriptor_words={};descriptor_counts=Counter();descriptor_trace=hashlib.sha256();descriptor_byte_trace=hashlib.sha256();descriptor_stop='budget';descriptor_blocks=descriptor_delays=descriptor_CD_ticks=descriptor_SSI_events=descriptor_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');descriptor_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4a4,0)
                if not flag&0x80000000 and not runtime.core.DSPReadLong(0xf1a100,0)&8:descriptor_stop='source_CD_descriptor_flag_nonnegative_after_IRQ_return';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:descriptor_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:descriptor_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);descriptor_words[key]=payload;descriptor_counts[key]+=1;descriptor_trace.update(struct.pack('>I',pc));descriptor_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;descriptor_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);descriptor_words[key]=dr;descriptor_counts[key]+=1;descriptor_trace.update(struct.pack('>I',delay));descriptor_byte_trace.update(struct.pack('>I',delay)+dr);descriptor_delays+=1
                elapsed=int(costs[opcode]);descriptor_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);descriptor_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);descriptor_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(descriptor_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=descriptor_SSI_events,CD_ticks=descriptor_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;descriptor_after=DSP_buffer.raw[:8729];(out/'DSP-after-descriptor-program.bin').write_bytes(descriptor_after);(out/'RAM-after-descriptor-DSP.bin').write_bytes(runtime.device.ram())
            descriptor_DSP=dict(status='native_CD_descriptor_DSP_with_pinned_CD_SSI_callbacks',stop_reason=descriptor_stop,execution_blocks=descriptor_blocks,instructions=(counter.value-descriptor_count_start)&0xffffffff,observed_branch_delays=descriptor_delays,initial_PC=hex(struct.unpack_from('=I',descriptor_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4a4,0)),SSI_events=descriptor_SSI_events,CD_clock_ticks=descriptor_CD_ticks,pinned_opcode_cycle_budget=descriptor_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==descriptor_CPU,logical_DSP_sha256=sha(descriptor_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=descriptor_trace.hexdigest(),instruction_byte_trace_sha256=descriptor_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':descriptor_counts[(pc,payload)]}for(pc,payload)in sorted(descriptor_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'descriptor-DSP-observation.json',descriptor_DSP);print(json.dumps({k:descriptor_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_descriptor_CPU=None
        if args.continue_CPU_after_CD_descriptor:
            assert descriptor_DSP and descriptor_DSP['stop_reason']=='source_CD_descriptor_flag_nonnegative_after_IRQ_return'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-descriptor-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-descriptor-CPU.bin').write_bytes(runtime.device.ram())
            after_descriptor_CPU=dict(status='native_CPU_continuation_after_source_DSP_descriptor_copy_completion',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-descriptor-DSP.json',after_descriptor_CPU);print(json.dumps(dict(after_descriptor_CPU_steps=after_descriptor_CPU['steps'],PC=hex(after_descriptor_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        header_DSP=None
        if args.run_CD_header_DSP:
            assert after_descriptor_CPU and after_descriptor_CPU['final_CPU']['pc']==0x50a8e
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;header_initial=DSP_buffer.raw[:8729];(out/'DSP-before-header-program.bin').write_bytes(header_initial)
            header_CPU=bytes(runtime.cpu());header_words={};header_counts=Counter();header_trace=hashlib.sha256();header_byte_trace=hashlib.sha256();header_stop='budget';header_blocks=header_delays=header_CD_ticks=header_SSI_events=header_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');header_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4a4,0)
                if not flag&0x80000000 and not runtime.core.DSPReadLong(0xf1a100,0)&8:header_stop='source_CD_header_flag_nonnegative_after_IRQ_return';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:header_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:header_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);header_words[key]=payload;header_counts[key]+=1;header_trace.update(struct.pack('>I',pc));header_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;header_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);header_words[key]=dr;header_counts[key]+=1;header_trace.update(struct.pack('>I',delay));header_byte_trace.update(struct.pack('>I',delay)+dr);header_delays+=1
                elapsed=int(costs[opcode]);header_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);header_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);header_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(header_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=header_SSI_events,CD_ticks=header_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;header_after=DSP_buffer.raw[:8729];(out/'DSP-after-header-program.bin').write_bytes(header_after);(out/'RAM-after-header-DSP.bin').write_bytes(runtime.device.ram())
            header_DSP=dict(status='native_CD_header_DSP_with_pinned_CD_SSI_callbacks',stop_reason=header_stop,execution_blocks=header_blocks,instructions=(counter.value-header_count_start)&0xffffffff,observed_branch_delays=header_delays,initial_PC=hex(struct.unpack_from('=I',header_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4a4,0)),SSI_events=header_SSI_events,CD_clock_ticks=header_CD_ticks,pinned_opcode_cycle_budget=header_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==header_CPU,logical_DSP_sha256=sha(header_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=header_trace.hexdigest(),instruction_byte_trace_sha256=header_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':header_counts[(pc,payload)]}for(pc,payload)in sorted(header_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'header-DSP-observation.json',header_DSP);print(json.dumps({k:header_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_header_CPU=None
        if args.continue_CPU_after_CD_header:
            assert header_DSP and header_DSP['stop_reason']=='source_CD_header_flag_nonnegative_after_IRQ_return'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-header-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-header-CPU.bin').write_bytes(runtime.device.ram())
            after_header_CPU=dict(status='native_CPU_continuation_after_source_DSP_header_copy_completion',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-header-DSP.json',after_header_CPU);print(json.dumps(dict(after_header_CPU_steps=after_header_CPU['steps'],PC=hex(after_header_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        auth_DSP=None
        if args.run_header_auth_DSP:
            assert after_header_CPU and after_header_CPU['final_CPU']['pc']==0x50ab4
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;auth_initial=DSP_buffer.raw[:8729];(out/'DSP-before-auth-program.bin').write_bytes(auth_initial)
            auth_CPU=bytes(runtime.cpu());auth_words={};auth_counts=Counter();auth_trace=hashlib.sha256();auth_byte_trace=hashlib.sha256();auth_stop='budget';auth_blocks=auth_delays=auth_CD_ticks=auth_SSI_events=auth_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');auth_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4c8,0)
                if flag&0x80000000 and auth_blocks>0:auth_stop='source_header_auth_command_acknowledged';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:auth_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:auth_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);auth_words[key]=payload;auth_counts[key]+=1;auth_trace.update(struct.pack('>I',pc));auth_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;auth_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);auth_words[key]=dr;auth_counts[key]+=1;auth_trace.update(struct.pack('>I',delay));auth_byte_trace.update(struct.pack('>I',delay)+dr);auth_delays+=1
                elapsed=int(costs[opcode]);auth_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);auth_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);auth_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(auth_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=auth_SSI_events,CD_ticks=auth_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;auth_after=DSP_buffer.raw[:8729];(out/'DSP-after-auth-program.bin').write_bytes(auth_after);(out/'RAM-after-auth-DSP.bin').write_bytes(runtime.device.ram())
            auth_DSP=dict(status='native_header_auth_DSP_with_pinned_CD_SSI_callbacks',stop_reason=auth_stop,execution_blocks=auth_blocks,instructions=(counter.value-auth_count_start)&0xffffffff,observed_branch_delays=auth_delays,initial_PC=hex(struct.unpack_from('=I',auth_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4c8,0)),SSI_events=auth_SSI_events,CD_clock_ticks=auth_CD_ticks,pinned_opcode_cycle_budget=auth_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==auth_CPU,logical_DSP_sha256=sha(auth_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=auth_trace.hexdigest(),instruction_byte_trace_sha256=auth_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':auth_counts[(pc,payload)]}for(pc,payload)in sorted(auth_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'auth-DSP-observation.json',auth_DSP);print(json.dumps({k:auth_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_auth_CPU=None
        if args.continue_CPU_after_header_auth:
            assert auth_DSP and auth_DSP['stop_reason']=='source_header_auth_command_acknowledged'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-auth-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-auth-CPU.bin').write_bytes(runtime.device.ram())
            after_auth_CPU=dict(status='native_CPU_continuation_after_source_DSP_header_auth_ack',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-auth-DSP.json',after_auth_CPU);print(json.dumps(dict(after_auth_CPU_steps=after_auth_CPU['steps'],PC=hex(after_auth_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        auth_result_DSP=None
        if args.run_auth_result_DSP:
            assert after_auth_CPU and after_auth_CPU['final_CPU']['pc']==0x50ae6
            runtime.core.JERRYI2SCallback.argtypes=[];runtime.core.JERRYI2SCallback.restype=None
            runtime.core.JaguarReadWord.argtypes=[c.c_uint32,c.c_uint32];runtime.core.JaguarReadWord.restype=c.c_uint16
            costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
            assert runtime.savers['DSP'](DSP_buffer)==8729;auth_result_initial=DSP_buffer.raw[:8729];(out/'DSP-before-auth-result-program.bin').write_bytes(auth_result_initial)
            auth_result_CPU=bytes(runtime.cpu());auth_result_words={};auth_result_counts=Counter();auth_result_trace=hashlib.sha256();auth_result_byte_trace=hashlib.sha256();auth_result_stop='budget';auth_result_blocks=auth_result_delays=auth_result_CD_ticks=auth_result_SSI_events=auth_result_cycles=0;CD_remainder=SSI_remainder=0.0
            counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');auth_result_count_start=counter.value;cycle_us_RISC=cycle_us/2
            for block in range(args.third_DSP_budget):
                flag=runtime.core.DSPReadLong(0xf1b4a4,0)
                if not flag&0x80000000 and not runtime.core.DSPReadLong(0xf1a100,0)&8:auth_result_stop='source_CD_auth_result_flag_nonnegative_after_IRQ_return';break
                if not runtime.core.DSPReadLong(0xf1a114,0)&1:auth_result_stop='source_DSP_GO_cleared';break
                pc=runtime.core.DSPGetPC()
                if not 0xf1b000<=pc<0xf1d000:auth_result_stop='outside_local_DSP_RAM';break
                location=runtime.core.DSPGetRAM()+pc-0xf1b000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');opcode=word>>10;size=6 if opcode==38 else 2;payload=raw6[:size];delay6=c.string_at(location+2,6)
                key=(pc,payload);auth_result_words[key]=payload;auth_result_counts[key]+=1;auth_result_trace.update(struct.pack('>I',pc));auth_result_byte_trace.update(struct.pack('>I',pc)+payload);before_count=counter.value;runtime.core.DSPExec(1);consumed=(counter.value-before_count)&0xffffffff;auth_result_blocks+=1
                if consumed>1 and opcode in [52,53]:
                    delay=pc+2;dw=int.from_bytes(delay6[:2],'big');ds=6 if dw>>10==38 else 2;dr=delay6[:ds];key=(delay,dr);auth_result_words[key]=dr;auth_result_counts[key]+=1;auth_result_trace.update(struct.pack('>I',delay));auth_result_byte_trace.update(struct.pack('>I',delay)+dr);auth_result_delays+=1
                elapsed=int(costs[opcode]);auth_result_cycles+=elapsed;CD_remainder+=elapsed;SSI_remainder+=elapsed
                while CD_remainder>=CD_tick_period_CPU_cycles*2:
                    runtime.core.BUTCHExec(0);auth_result_CD_ticks+=1;CD_remainder-=CD_tick_period_CPU_cycles*2
                SMODE,SCLK=SSI_clock_registers(runtime)
                SSI_period_cycles=64*(SCLK+1)if SMODE&1 else 22.675737/cycle_us_RISC
                while SSI_remainder>=SSI_period_cycles:
                    deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);auth_result_SSI_events+=1;SSI_remainder-=SSI_period_cycles
                if block and block%500000==0:print(json.dumps(dict(auth_result_DSP_blocks=block,PC=hex(runtime.core.DSPGetPC()),mailbox=hex(flag),SSI_events=auth_result_SSI_events,CD_ticks=auth_result_CD_ticks)),flush=True)
            assert runtime.savers['DSP'](DSP_buffer)==8729;auth_result_after=DSP_buffer.raw[:8729];(out/'DSP-after-auth-result-program.bin').write_bytes(auth_result_after);(out/'RAM-after-auth-result-DSP.bin').write_bytes(runtime.device.ram())
            auth_result_DSP=dict(status='native_CD_auth_result_DSP_with_pinned_CD_SSI_callbacks',stop_reason=auth_result_stop,execution_blocks=auth_result_blocks,instructions=(counter.value-auth_result_count_start)&0xffffffff,observed_branch_delays=auth_result_delays,initial_PC=hex(struct.unpack_from('=I',auth_result_initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),control=runtime.core.DSPReadLong(0xf1a114,0),mailbox_flag=hex(runtime.core.DSPReadLong(0xf1b4a4,0)),SSI_events=auth_result_SSI_events,CD_clock_ticks=auth_result_CD_ticks,pinned_opcode_cycle_budget=auth_result_cycles,clock_policy='Pinned DSP outer-opcode cost table; nested branch delay uncharged per core DSPExec. BUTCH halfline cadence; actual JERRYI2SCallback uses current SMODE/SCLK, external22.675737us. CPU/GPU/video/PIT/bus stalls not advanced; physical/global timing unverified.',CPU_state_unchanged=bytes(runtime.cpu())==auth_result_CPU,logical_DSP_sha256=sha(auth_result_after[:8496]),RAM_sha256=sha(runtime.device.ram()),PC_trace_sha256=auth_result_trace.hexdigest(),instruction_byte_trace_sha256=auth_result_byte_trace.hexdigest(),PC_trace_scope='DSPExec1 boundary PCs and detected taken branch delays; asynchronous IRQ/pipeline effects require separate validation',visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'dsp')[0][0],'count':auth_result_counts[(pc,payload)]}for(pc,payload)in sorted(auth_result_words)],source_C_verified=False,hardware_ROM_view_verified=False,host_mailbox_flag_write=False,boot_stub_hostcopied=False,physical_global_schedule_verified=False)
            save(out/'auth-result-DSP-observation.json',auth_result_DSP);print(json.dumps({k:auth_result_DSP[k]for k in ['stop_reason','instructions','final_PC','mailbox_flag','SSI_events','CD_clock_ticks']}),flush=True)
        after_auth_result_CPU=None
        if args.continue_CPU_after_auth_result:
            assert auth_result_DSP and auth_result_DSP['stop_reason']=='source_CD_auth_result_flag_nonnegative_after_IRQ_return'
            import capstone
            decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            after_counts=Counter();after_trace=hashlib.sha256();after_seen=Counter();after_rows={};after_stop='budget';after_CPU_initial=media.scheduler.cpu_dict(runtime.cpu());after_cycles=after_ticks=0
            for step in range(args.CPU_continuation_budget):
                cpu=runtime.cpu();pc=cpu.pc;after_seen[bytes(cpu)]+=1
                if after_seen[bytes(cpu)]>=64:after_stop='repeated_exact_CPU_state_without_other_devices';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:after_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(decoder.disasm(raw,pc,count=1),None)
                if decoded is None:after_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());after_rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str);after_counts[key]+=1;after_trace.update(struct.pack('>I',pc));cycles=runtime.core.m68k_execute(1);after_cycles+=cycles;CD_cycle_remainder+=cycles
                while CD_cycle_remainder>=CD_tick_period_CPU_cycles:runtime.core.BUTCHExec(0);after_ticks+=1;CD_cycle_remainder-=CD_tick_period_CPU_cycles
            assert runtime.savers['DSP'](DSP_buffer)==8729;(out/'DSP-after-auth-result-CPU.bin').write_bytes(DSP_buffer.raw[:8729]);(out/'RAM-after-auth-result-CPU.bin').write_bytes(runtime.device.ram())
            after_auth_result_CPU=dict(status='native_CPU_continuation_after_source_DSP_auth_result_copy_completion',stop_reason=after_stop,steps=sum(after_counts.values()),initial_CPU=after_CPU_initial,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=after_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],CD_clock_ticks=after_ticks,returned_CPU_cycles=after_cycles,DSP_PC=hex(runtime.core.DSPGetPC()),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),GPU_PC=hex(runtime.core.GPUGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),visited_instructions=[{**after_rows[key],'count':count}for key,count in sorted(after_counts.items())],CPU_reseeded=False,source_C_verified=False,boot_stub_hostcopied=False,hardware_ROM_view_verified=False,physical_global_schedule_verified=False)
            save(out/'CPU-after-auth-result-DSP.json',after_auth_result_CPU);print(json.dumps(dict(after_auth_result_CPU_steps=after_auth_result_CPU['steps'],PC=hex(after_auth_result_CPU['final_CPU']['pc']),stop_reason=after_stop)),flush=True)
        challenge_observation=None
        if args.advance_CD_challenge_phases:
            assert 1<=args.advance_CD_challenge_phases<=16
            assert after_auth_result_CPU and after_auth_result_CPU['final_CPU']['pc']==0x50be2
            import observe_biwn_CD_challenge_phases as challenge
            import sys
            challenge_observation,CD_cycle_remainder=challenge.advance(sys.modules[__name__],runtime,out,args,CD_tick_period_CPU_cycles,cycle_us,CD_cycle_remainder)
        fourth_DSP=None
        if args.run_fourth_DSP:
            assert challenge_observation and challenge_observation['final_CPU']['pc']==(0x50d98 if args.initialize_fourth_DSP_at_source_GO else 0x50dc4)
            folder=out/'fourth-DSP-command'
            fourth=challenge.DSP_phase(sys.modules[__name__],runtime,folder,'fourth_firmware_DSP_command',args,0xf1b020,False,CD_tick_period_CPU_cycles,cycle_us,0xf1b0ee if args.initialize_fourth_DSP_at_source_GO else None)
            fourth_DSP=dict(directory=str(folder),DSP=fourth)
            if fourth['stop_reason']=='source_DSP_command_acknowledged':
                follow,CD_cycle_remainder=challenge.CPU_phase(sys.modules[__name__],runtime,folder,args,CD_tick_period_CPU_cycles,CD_cycle_remainder);fourth_DSP['CPU']=follow
            save(out/'fourth-DSP-command.json',fourth_DSP)
        fourth_phases=None
        if args.advance_fourth_DSP_phases:
            assert 1<=args.advance_fourth_DSP_phases<=16
            assert fourth_DSP and fourth_DSP.get('CPU',{}).get('final_CPU',{}).get('pc')in([0x50dc4,0x50dc6]if args.initialize_fourth_DSP_at_source_GO else[0x50dde])
            fourth_phases,CD_cycle_remainder=challenge.advance_fourth(sys.modules[__name__],runtime,out,args,CD_tick_period_CPU_cycles,cycle_us,CD_cycle_remainder)
        post_auth_video=None
        if args.post_auth_video_events:
            assert fourth_phases and fourth_phases['final_CPU']['pc']==0x50f40
            assert 0<args.post_auth_video_events<=4
            post_auth_video,CD_cycle_remainder=challenge.advance_after_auth_video(sys.modules[__name__],runtime,out,args,CD_tick_period_CPU_cycles,CD_cycle_remainder)
        if post_auth_video:
            import biwn_firmware_checkpoint
            protocol['resume_checkpoint']=biwn_firmware_checkpoint.save_current(sys.modules[__name__],runtime,out,protocol,CD_cycle_remainder)
        GPU_observation=None
        if args.probe_GPU_shutdown:
            assert continuation and continuation['CPU']['pc']==0x50292
            runtime.core.GPUExec.argtypes=[c.c_int32]
            gbuffer=c.create_string_buffer(12000);n=runtime.savers['GPU'](gbuffer);assert n==4416
            initial_GPU=gbuffer.raw[:n];(out/'GPU-at-CPU-stop-wait.bin').write_bytes(initial_GPU)
            GPU_words={};gcounts=Counter();gtrace=hashlib.sha256();signatures=Counter();recent=deque();gstop='budget';CPU_before_GPU=bytes(runtime.cpu())
            gcounter=c.c_uint32.in_dll(runtime.core,'gpu_exec_opcode_count');gstart=gcounter.value;gdelays=0;gblocks=0
            if args.GPU_initial_wait_C:
                def initial_observed(_,pointer,pc):
                    nonlocal gdelays
                    state=pointer.contents;off=pc-0xf03000;word=int.from_bytes(bytes(state.local_RAM[off:off+2]),'big');size=6 if word>>10==38 else 2;payload=bytes(state.local_RAM[off:off+size])
                    GPU_words[pc]=payload;gcounts[pc]+=1;gtrace.update(struct.pack('>I',pc))
                    if word>>10 in [52,53]:
                        cc=word&31;flags=state.z|(state.c<<1)|(state.n<<2)
                        condition=not((cc&1 and flags&1)or(cc&2 and not flags&1)or(cc&4 and flags&(2<<(cc>>4)))or(cc&8 and not flags&(2<<(cc>>4))))
                        if condition:gdelays+=1
                status,source_state=run_firmware_GPU_C(runtime,initial_GPU,194561,initial_observed)
                assert status==4,(status,hex(source_state.pc))
                gblocks=source_state.instructions-gdelays;gstop='explicit_matching_native_observation_quantum'
            for block in range(0 if args.GPU_initial_wait_C else 1000000):
                pc=runtime.core.GPUGetPC();control=runtime.core.GPUReadLong(0xf02114,0)
                if not control&1:gstop='source_GPU_GO_cleared';break
                if not 0xf03000<=pc<0xf04000:gstop='outside_local_GPU_RAM';break
                location=runtime.core.GPUGetRAM()+pc-0xf03000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');size=6 if word>>10==38 else 2;payload=raw6[:size]
                if pc in GPU_words and GPU_words[pc]!=payload:gstop='GPU_self_modifying_instruction_needs_new_listing';break
                delay_before=c.string_at(location+2,6)
                GPU_words[pc]=payload;gcounts[pc]+=1;gtrace.update(struct.pack('>I',pc));gblocks+=1;runtime.core.GPUExec(1)
                if word>>10 in [52,53] and runtime.core.GPUGetPC()!=pc+2:
                    gdelays+=1
                    delay=pc+2;dr=delay_before;dw=int.from_bytes(dr[:2],'big');ds=6 if dw>>10==38 else 2;GPU_words[delay]=dr[:ds];gcounts[delay]+=1;gtrace.update(struct.pack('>I',delay))
                if block%1024==0:
                    assert runtime.savers['GPU'](gbuffer)==4416;sig=hashlib.sha256(gbuffer.raw[:4396]).digest();signatures[sig]+=1;recent.append(sig)
                    if len(recent)>8192:signatures[recent.popleft()]-=1
                    if signatures[sig]>=64:gstop='repeated_logical_GPU_state_without_global_events';break
            assert runtime.savers['GPU'](gbuffer)==4416;after=gbuffer.raw[:4416]
            (out/'GPU-after-shutdown-probe.bin').write_bytes(after);(out/'RAM-after-GPU-shutdown-probe.bin').write_bytes(runtime.device.ram())
            grows=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'gpu')[0][0],'count':gcounts[pc]}for pc,payload in sorted(GPU_words.items())]
            GPU_observation=dict(status='native_only_GPU_shutdown_boundary_observation',stop_reason=gstop,instructions=gblocks+gdelays,execution_blocks=gblocks,executed_branch_delay_slots=gdelays,core_opcode_counter_delta=(gcounter.value-gstart)&0xffffffff,counter_scope='Pinned GPU counter excludes nested branch-delay execution; source-instruction count includes observed taken delay slots',CPU_held_at=hex(continuation['CPU']['pc']),CPU_state_unchanged=bytes(runtime.cpu())==CPU_before_GPU,initial_GPU_PC=hex(struct.unpack_from('=I',initial_GPU,4096)[0]),final_GPU_PC=hex(runtime.core.GPUGetPC()),initial_logical_GPU_sha256=sha(initial_GPU[:4396]),final_logical_GPU_sha256=sha(after[:4396]),PC_trace_sha256=gtrace.hexdigest(),visited_instructions=grows,source_GPU_C_verified=False,explicit_GPU_steps=True,physical_global_schedule_verified=False,final_control=runtime.core.GPUReadLong(0xf02114,0),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'])
            if args.GPU_initial_wait_C:GPU_observation.update(status='C_initial_GPU_wait_from_live_CPU_loader_state',source_GPU_C_verified=True,original_GPU_instructions_on_C_path=0,initial_GPU_boundary_hostloaded=False,observation_quantum_outer_blocks=194561,pipeline_tail_excluded_bytes=20)
            save(out/'GPU-shutdown-observation.json',GPU_observation)
        video_IRQ=None
        if args.probe_CPU_video_IRQ:
            assert GPU_observation and runtime.cpu().pc==0x50292
            assert int.from_bytes(runtime.device.ram()[0x100:0x104],'big')==0x194c90
            before_CPU=runtime.cpu();before_RAM=runtime.device.ram();before_GPU=c.string_at(runtime.core.GPUGetRAM(),4096)
            runtime.core.TOMSetPendingVideoInt.argtypes=[];runtime.core.TOMSetPendingVideoInt.restype=None
            runtime.core.m68k_set_irq2.argtypes=[c.c_uint32];runtime.core.m68k_set_irq2.restype=None
            vcounts=Counter();vtrace=hashlib.sha256();vseen=Counter();vwords={};vstop='budget'
            if args.video_IRQ_C:
                src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfirmware-video-IRQ.dylib'
                cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_firmware_video_irq_cpu.c'),str(src/'biwn_firmware_video_irq_event.c'),'-o',str(library)]
                build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'video-IRQ-compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
                helper=c.CDLL(str(library));event=helper.biwn_firmware_video_irq_event;event.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];event.restype=c.c_int
                handler=helper.biwn_firmware_video_irq_cpu_call;handler.argtypes=runtime.fn.argtypes;handler.restype=c.c_int
                types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8]
                def reader(width):return lambda _,a,v:(v.__setitem__(0,runtime.read(a,width)),0)[1]
                def writer(width):return lambda _,a,v:(runtime.write(a,width,v),0)[1]
                cbs=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
                bus=media.Bus(*cbs[:5],media.scheduler.cleanup.world.CALL(),None,0)
                def observed(_,bus,state,pc):vcounts[pc]+=1;vtrace.update(struct.pack('>I',pc));return 0
                service=media.world_cpu.SERVICE(observed);translated=media.CPU.from_buffer_copy(bytes(before_CPU))
                runtime.core.TOMSetPendingVideoInt();runtime.core.m68k_set_irq(0)
                assert event(c.byref(bus),c.byref(translated))==0;entry=media.CPU.from_buffer_copy(bytes(translated))
                status=handler(c.byref(bus),c.byref(translated),cbs[5],service,None,300000,0)
                if status!=8 or bytes(translated)!=bytes(before_CPU):
                    save(out/'video-IRQ-C-error.json',dict(status=status,before=media.scheduler.cpu_dict(before_CPU),after=media.scheduler.cpu_dict(translated),last_PCs=[hex(k)for k in list(vcounts)[-8:]],RAM_sha256=sha(runtime.device.ram())));raise AssertionError(str(out/'video-IRQ-C-error.json'))
                assert bytes(runtime.cpu())==bytes(before_CPU),'C handler RTE restores caller; core CPU remains at caller throughout'
                vstop='source_handler_RTE_returned';vstep=0
            else:
                runtime.core.TOMSetPendingVideoInt();runtime.core.m68k_set_irq2(2)
                entry=runtime.cpu();assert entry.pc==0x194c90,hex(entry.pc)
            for vstep in range(0 if args.video_IRQ_C else 300000):
                pc=runtime.core.m68k_get_reg(None,16);s=runtime.cpu()
                if pc==before_CPU.pc:vstop='source_handler_RTE_returned';break
                vseen[bytes(s)]+=1
                if vseen[bytes(s)]>=64:vstop='repeated_CPU_state_inside_video_handler';break
                if pc<0x200000:code=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:code=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:vstop='outside_observed_source_memory';break
                import capstone
                md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
                ins=next(md.disasm(code,pc,count=1),None);assert ins is not None,hex(pc)
                row=generation.loader.base.binary_tools.m68k_instructions(code[:ins.size],pc)[0][0]
                assert pc not in vwords or vwords[pc]['bytes']==row['bytes'];vwords[pc]=row
                vcounts[pc]+=1;vtrace.update(struct.pack('>I',pc));runtime.core.m68k_execute(1)
            after_GPU=c.string_at(runtime.core.GPUGetRAM(),4096);after_RAM=runtime.device.ram()
            (out/'RAM-after-video-IRQ.bin').write_bytes(after_RAM)
            video_IRQ=dict(status='C_firmware_CPU_video_IRQ_from_live_bootstrap'if args.video_IRQ_C else'original_firmware_CPU_video_IRQ_observation',stop_reason=vstop,external_VBI_events=1,source_handler='0x194c90',CPU_before=media.scheduler.cpu_dict(before_CPU),CPU_after_exception_entry=media.scheduler.cpu_dict(entry),CPU_after=media.scheduler.cpu_dict(runtime.cpu()),instructions=sum(vcounts.values()),PC_trace_sha256=vtrace.hexdigest(),PC_visits={hex(pc):count for pc,count in sorted(vcounts.items())},mailbox_before=hex(int.from_bytes(before_GPU[0xf4c:0xf50],'big')),mailbox_after=hex(int.from_bytes(after_GPU[0xf4c:0xf50],'big')),source_mailbox_clear_reached=0x194d18 in vcounts,source_video_counter_before=int.from_bytes(before_RAM[0x1ae4d2:0x1ae4d4],'big'),source_video_counter_after=int.from_bytes(after_RAM[0x1ae4d2:0x1ae4d4],'big'),visited_instructions=[{**row,'count':vcounts[pc]}for pc,row in sorted(vwords.items())],RAM_sha256=sha(after_RAM),hardware=runtime.snapshot()['hardware'],CPU_reseeded=False,host_mailbox_flag_write=False,physical_VBI_period_verified=False,source_C_verified=bool(args.video_IRQ_C),original_CPU_handler_instructions_on_C_path=0 if args.video_IRQ_C else sum(vcounts.values()),initial_handler_boundary_hostloaded=False)
            save(out/'CPU-video-IRQ-observation.json',video_IRQ)
            assert runtime.savers['GPU'](gbuffer)==4416
            (out/'GPU-after-video-IRQ.bin').write_bytes(gbuffer.raw[:4416])
            runtime.core.retro_serialize_size.argtypes=[];runtime.core.retro_serialize_size.restype=c.c_size_t
            runtime.core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];runtime.core.retro_serialize.restype=c.c_bool
            machine_size=runtime.core.retro_serialize_size();assert 0<machine_size<100000000
            machine=c.create_string_buffer(machine_size);assert runtime.core.retro_serialize(machine,machine_size)
            (out/'machine-after-video-IRQ.bin').write_bytes(machine.raw)
        GPU_after_IRQ=None
        if args.resume_GPU_after_IRQ:
            assert video_IRQ and video_IRQ['stop_reason']=='source_handler_RTE_returned' and video_IRQ['mailbox_after']=='0x0'
            resumed_words={};resumed_counts=Counter();resumed_trace=hashlib.sha256();resumed_byte_trace=hashlib.sha256();code_versions={};code_changes=[];rgblocks=rgdelays=0;rstop='budget';seen=Counter();recent=deque();before_CPU=bytes(runtime.cpu())
            if args.GPU_renderer_C:
                assert runtime.savers['GPU'](gbuffer)==4416;incoming_GPU=gbuffer.raw[:4416]
                C_delays=[0]
                def observed(_,pointer,pc):
                    s=pointer.contents;off=pc-0xf03000;word=int.from_bytes(bytes(s.local_RAM[off:off+2]),'big');size=6 if word>>10==38 else 2;payload=bytes(s.local_RAM[off:off+size]);key=(pc,payload);resumed_words[key]=payload;resumed_counts[key]+=1;resumed_trace.update(struct.pack('>I',pc));resumed_byte_trace.update(struct.pack('>I',pc)+payload)
                    if word>>10 in [52,53]:
                        cc=word&31;flags=s.z|(s.c<<1)|(s.n<<2)
                        condition=not((cc&1 and flags&1)or(cc&2 and not flags&1)or(cc&4 and flags&(2<<(cc>>4)))or(cc&8 and not flags&(2<<(cc>>4))))
                        if condition:C_delays[0]+=1
                status,source_state=run_firmware_GPU_C(runtime,incoming_GPU,1000000,observed)
                assert status==0,(status,hex(source_state.pc));assert bytes(runtime.cpu())==before_CPU
                rgdelays=C_delays[0];rgblocks=source_state.instructions-rgdelays;rstop='source_GPU_GO_cleared'
            for block in range(0 if args.GPU_renderer_C else 1000000):
                pc=runtime.core.GPUGetPC();control=runtime.core.GPUReadLong(0xf02114,0)
                if not control&1:rstop='source_GPU_GO_cleared';break
                if not 0xf03000<=pc<0xf04000:rstop='outside_local_GPU_RAM';break
                location=runtime.core.GPUGetRAM()+pc-0xf03000;raw6=c.string_at(location,6);word=int.from_bytes(raw6[:2],'big');size=6 if word>>10==38 else 2;payload=raw6[:size]
                if pc in code_versions and code_versions[pc]!=payload:
                    code_changes.append(dict(block=block,PC=hex(pc),previous_bytes=code_versions[pc].hex(),bytes=payload.hex(),GPU_RAM_sha256=sha(c.string_at(runtime.core.GPUGetRAM(),4096))))
                    if len(code_changes)<=64:(out/f'GPU-code-change-{len(code_changes):03d}.bin').write_bytes(c.string_at(runtime.core.GPUGetRAM(),4096))
                    if len(code_changes)>4096:rstop='instruction_version_limit';break
                delay_before=c.string_at(location+2,6)
                code_versions[pc]=payload;key=(pc,payload);resumed_words[key]=payload;resumed_counts[key]+=1;resumed_trace.update(struct.pack('>I',pc));resumed_byte_trace.update(struct.pack('>I',pc)+payload);rgblocks+=1;runtime.core.GPUExec(1)
                if word>>10 in [52,53] and runtime.core.GPUGetPC()!=pc+2:
                    rgdelays+=1;delay=pc+2;dr=delay_before;dw=int.from_bytes(dr[:2],'big');ds=6 if dw>>10==38 else 2;payload_delay=dr[:ds];key=(delay,payload_delay);resumed_words[key]=payload_delay;resumed_counts[key]+=1;resumed_trace.update(struct.pack('>I',delay));resumed_byte_trace.update(struct.pack('>I',delay)+payload_delay)
                if block%1024==0:
                    assert runtime.savers['GPU'](gbuffer)==4416;sig=hashlib.sha256(gbuffer.raw[:4396]).digest();seen[sig]+=1;recent.append(sig)
                    if len(recent)>8192:seen[recent.popleft()]-=1
                    if seen[sig]>=64:rstop='repeated_logical_GPU_state';break
            assert runtime.savers['GPU'](gbuffer)==4416;result_GPU=gbuffer.raw[:4416]
            (out/'GPU-after-video-IRQ-resume.bin').write_bytes(result_GPU);(out/'RAM-after-video-IRQ-GPU-resume.bin').write_bytes(runtime.device.ram())
            GPU_after_IRQ=dict(status='original_GPU_resumed_after_source_CPU_mailbox_acknowledgement',stop_reason=rstop,source_GPU_C_verified=False,execution_blocks=rgblocks,executed_branch_delay_slots=rgdelays,instructions=rgblocks+rgdelays,PC_trace_sha256=resumed_trace.hexdigest(),instruction_byte_trace_sha256=resumed_byte_trace.hexdigest(),observed_code_changes=code_changes,final_PC=hex(runtime.core.GPUGetPC()),final_control=runtime.core.GPUReadLong(0xf02114,0),logical_GPU_sha256=sha(result_GPU[:4396]),RAM_sha256=sha(runtime.device.ram()),CPU_state_unchanged=bytes(runtime.cpu())==before_CPU,visited_instructions=[{**generation.loader.base.binary_tools.jaguar_instructions(payload,pc,'gpu')[0][0],'count':resumed_counts[(pc,payload)]}for (pc,payload)in sorted(resumed_words)],hardware=runtime.snapshot()['hardware'],host_mailbox_flag_write=False,initial_GPU_boundary_hostloaded=False,explicit_GPU_steps=True,physical_global_timing_verified=False)
            save(out/'GPU-after-video-IRQ-resume.json',GPU_after_IRQ)
            if args.GPU_renderer_C:
                GPU_after_IRQ.update(status='C_GPU_renderer_from_live_firmware_CPU_DSP_videoIRQ_state',source_GPU_C_verified=True,original_GPU_instructions_on_C_path=0,shared_blitter_MMIO_DMA_model=True,pipeline_tail_provider='Initial20GPUtailbytes retained for peripheral mirroring;logical4396compared',source_instruction_guards=True)
                save(out/'GPU-after-video-IRQ-resume.json',GPU_after_IRQ)
        CPU_after_GPU=None
        if args.continue_CPU_after_GPU:
            assert GPU_after_IRQ and GPU_after_IRQ['stop_reason']=='source_GPU_GO_cleared'
            import capstone
            md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            follow_counts=Counter();follow_trace=hashlib.sha256();follow_seen=Counter();follow_rows={};follow_stop='budget';transfers=[];last_PC=None
            initial_follow_CPU=media.scheduler.cpu_dict(runtime.cpu())
            initial_CPU_raw=bytes(runtime.cpu());(out/'CPU-before-post-GPU.bin').write_bytes(initial_CPU_raw);(out/'RAM-before-post-GPU.bin').write_bytes(runtime.device.ram())
            machine_size=runtime.core.retro_serialize_size();machine=c.create_string_buffer(machine_size);assert runtime.core.retro_serialize(machine,machine_size);(out/'machine-before-post-GPU.bin').write_bytes(machine.raw)
            if args.post_GPU_CPU_C:
                mapping=json.loads((Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'firmware-post-GPU-CPU-generation.json').read_text());fixed_rows={r['address']:r for r in mapping['instructions_decoded']}
                def follow_observer(_,bus,pointer,pc):
                    row=fixed_rows[pc];key=(pc,row['bytes']);follow_rows[key]=row;follow_counts[key]+=1;follow_trace.update(struct.pack('>I',pc));return 0
                status,translated=run_firmware_post_GPU_CPU_C(runtime,out,media.CPU.from_buffer_copy(initial_CPU_raw),433,follow_observer)
                assert status==4,status
                # Export the computed C registers/banks/PC without resetting the core CPU.
                runtime.core.m68k_set_reg(17,0x2000);runtime.core.m68k_set_reg(15,translated.ssp)
                runtime.core.m68k_set_reg(17,0);runtime.core.m68k_set_reg(15,translated.usp)
                runtime.core.m68k_set_reg(17,translated.sr)
                for i,value in enumerate(translated.registers):runtime.core.m68k_set_reg(i,value)
                runtime.core.m68k_set_reg(16,translated.pc);assert bytes(runtime.cpu())==bytes(translated)
                follow_stop='explicit_matching_native_433_step_observation_quantum'
            for follow_step in range(0 if args.post_GPU_CPU_C else 300000):
                state_follow=runtime.cpu();pc=state_follow.pc;follow_seen[bytes(state_follow)]+=1
                if follow_seen[bytes(state_follow)]>=64:follow_stop='repeated_exact_CPU_state_without_further_device_events';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:follow_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(md.disasm(raw,pc,count=1),None)
                if decoded is None:follow_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());follow_rows[key]=dict(address=pc,bytes=key[1],size=decoded.size,assembly=decoded.mnemonic+' '+decoded.op_str)
                if last_PC is not None and pc!=last_PC+last_size and len(transfers)<400:transfers.append(dict(step=follow_step,from_PC=hex(last_PC),to_PC=hex(pc)))
                follow_counts[key]+=1;follow_trace.update(struct.pack('>I',pc));last_PC=pc;last_size=decoded.size;runtime.core.m68k_execute(1)
            CPU_after_GPU=dict(status='original_CPU_discovery_after_C_or_original_GPU_source_stop',stop_reason=follow_stop,steps=sum(follow_counts.values()),initial_CPU=initial_follow_CPU,final_CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=follow_trace.hexdigest(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],visited_instructions=[{**follow_rows[k],'count':v}for k,v in sorted(follow_counts.items())],control_transfer_sample=transfers,CPU_reseeded=False,additional_host_video_events=0,disc_attached=False,source_C_verified=False)
            if args.post_GPU_CPU_C:CPU_after_GPU.update(status='C_CPU_copy_jump_and_video_counter_wait_from_live_GPU_stop',source_C_verified=True,original_CPU_instructions_on_C_path=0,initial_CPU_boundary_hostloaded=False,source_C_final_CPU_state_mirrored_to_shared_core=True,source_C_mirror_used_core_pulse_reset=False,observation_quantum_instructions=433)
            save(out/'CPU-after-GPU.json',CPU_after_GPU);(out/'RAM-after-GPU-CPU.bin').write_bytes(runtime.device.ram())
            (out/'CPU-after-GPU.txt').write_text('\n'.join(f"{row['address']:08x} {row['bytes']} {row['assembly']} ; visits={row['count']}"for row in CPU_after_GPU['visited_instructions'])+'\n')
        further_video=[]
        for video_number in range(args.advance_video_events):
            assert CPU_after_GPU
            event_CPU=media.scheduler.cpu_dict(runtime.cpu());counter_before=int.from_bytes(runtime.device.ram()[0x1ae4d2:0x1ae4d4],'big')
            runtime.core.TOMSetPendingVideoInt();runtime.core.m68k_set_irq2(2)
            event_entry=media.scheduler.cpu_dict(runtime.cpu());source_vector=int.from_bytes(runtime.device.ram()[0x100:0x104],'big');assert event_entry['pc']==source_vector,(hex(event_entry['pc']),hex(source_vector))
            event_counts=Counter();event_trace=hashlib.sha256();event_seen=Counter();event_rows={};event_stop='instruction_budget';returned=False
            for event_step in range(300000):
                event_state=runtime.cpu();pc=event_state.pc;event_seen[bytes(event_state)]+=1
                if pc==event_CPU['pc']:returned=True
                if event_seen[bytes(event_state)]>=64:event_stop='repeated_exact_CPU_state_without_more_device_events';break
                if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
                elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
                else:event_stop='outside_mapped_RAM_or_userROM';break
                decoded=next(md.disasm(raw,pc,count=1),None)
                if decoded is None:event_stop='undecodable_instruction';break
                key=(pc,raw[:decoded.size].hex());event_rows[key]=dict(address=pc,bytes=key[1],size=decoded.size,assembly=decoded.mnemonic+' '+decoded.op_str);event_counts[key]+=1;event_trace.update(struct.pack('>I',pc));runtime.core.m68k_execute(1)
            event_record=dict(number=video_number+1,status='native_CPU_discovery_after_explicit_video_event',stop_reason=event_stop,steps=sum(event_counts.values()),CPU_before=event_CPU,CPU_exception_entry=event_entry,CPU_after=media.scheduler.cpu_dict(runtime.cpu()),returned_to_interrupted_PC_observed=returned,video_counter_before=counter_before,video_counter_after=int.from_bytes(runtime.device.ram()[0x1ae4d2:0x1ae4d4],'big'),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],PC_trace_sha256=event_trace.hexdigest(),visited_instructions=[{**event_rows[k],'count':v}for k,v in sorted(event_counts.items())],host_counter_write=False,CPU_reseeded=False,source_C_verified=False,physical_period_verified=False)
            save(out/f'further-video-{video_number+1:02d}.json',event_record);(out/f'RAM-after-further-video-{video_number+1:02d}.bin').write_bytes(runtime.device.ram());further_video.append(event_record)
            print(json.dumps(dict(video_event=video_number+1,steps=event_record['steps'],CPU_PC=hex(event_record['CPU_after']['pc']),counter=event_record['video_counter_after'],stop_reason=event_stop)),flush=True)
            if event_stop!='repeated_exact_CPU_state_without_more_device_events':break
        rows=[]
        for pc in sorted(counts):
            if pc<0x200000:
                image=(out/'RAM-at-relocated-entry.bin').read_bytes()if boundary else final
                raw=image[pc:pc+32]
            elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
            else:continue
            # Decode one actual visited word, then enforce its complete bytes.
            import capstone
            md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            first=next(md.disasm(raw,pc,count=1),None)
            if first is None:rows.append(dict(address=pc,count=counts[pc],decode_error=True));continue
            row=generation.loader.base.binary_tools.m68k_instructions(raw[:first.size],pc)[0][0]
            rows.append({**row,'count':counts[pc],'listing_source':'RAM-at-relocated-entry or supplied userROM; verify later self-modification separately'})
        save(out/'visited-instructions.json',rows)
        (out/'visited-instructions.txt').write_text('\n'.join(f"{row['address']:08x} {row.get('assembly','decode_error')} ; visits={row['count']}"for row in rows)+'\n')
        protocol['post_auth_video_observation']=post_auth_video
        report={**protocol,**dict(status='bounded_natural_relocated_firmware_observation',stop_reason=stop,repeated_state=repeated,executed_steps=sum(counts.values()),unique_visited_PCs=len(counts),PC_trace_sha256=trace.hexdigest(),control_transfer_sample=changes,relocated_entry=boundary,first_CPU_wait_CPU=media.scheduler.cpu_dict(state),first_CPU_wait_RAM_sha256=sha(final),final_CPU=media.scheduler.cpu_dict(state),final_RAM_sha256=sha(final),final_hardware=runtime.snapshot()['hardware'],GPU_PC=hex(runtime.core.GPUGetPC()),DSP_PC=hex(runtime.core.DSPGetPC()),GPU_GO=runtime.core.GPUReadLong(0xf02114,0),DSP_GO=runtime.core.DSPReadLong(0xf1a114,0),source_C_verification=False,legacy_final_fields_scope='final_CPU and final_RAM_sha256 describe firstCPU DSPwait; later phase state is in dedicated phase objects/files',limits=['Initial ROM/CPU/zeroRAM/device state supplied. This is a bounded firmware-prefix observation, not complete boot. FirstDSP andvideoIRQ have separate C comparison gates when selected.',('Internal CDI attached through pinned CD interface; no payload hostcopy.' if args.attach_CDI else 'No disc attached.')+' Optional explicitly delivered DSP/GPU/videoIRQ steps use declared sequencing; physical/global device/timer/VBI scheduling remains unverified.'])}
        report['first_DSP_observation']=first_DSP
        report['second_DSP_observation']=second_DSP
        report['CPU_continuation_after_second_DSP']=after_second_CPU
        report['third_DSP_observation']=third_DSP
        report['CPU_continuation_after_third_DSP']=after_third_CPU
        report['CD_descriptor_DSP_observation']=descriptor_DSP
        report['CPU_continuation_after_CD_descriptor']=after_descriptor_CPU
        report['CD_header_DSP_observation']=header_DSP
        report['CPU_continuation_after_CD_header']=after_header_CPU
        report['header_auth_DSP_observation']=auth_DSP
        report['CPU_continuation_after_header_auth']=after_auth_CPU
        report['auth_result_DSP_observation']=auth_result_DSP
        report['CPU_continuation_after_auth_result']=after_auth_result_CPU
        report['CD_challenge_observation']=challenge_observation
        report['fourth_DSP_observation']=fourth_DSP
        report['fourth_DSP_phases']=fourth_phases
        report['CD_read_command_DSP_observation']=command_DSP
        report['CPU_continuation_after_CD_read_command']=after_command_CPU
        if args.attach_CDI:report['CD_controller_diagnostics']=CD_diagnostics(runtime)
        report['SSI_receive_word_swap_applications']=runtime.SSI_receive_swaps
        report['SSI_previous_right_word_applications']=runtime.SSI_previous_right_applications
        report['SSI_receive_pair_samples']=runtime.SSI_pair_samples
        report['SSI_stored_register_observations']=[dict(SMODE=mode,SCLK=divider,callbacks=count)for (mode,divider),count in sorted(runtime.SSI_register_samples.items())]
        report['SSI_clock_register_read_policy']='Read pinned stored write-only SMODE32/SCLK8 globals; do not use upper-half bus reads or SSTAT as clock divider.'
        report['CPU_continuation_after_first_DSP']=continuation
        report['GPU_shutdown_observation']=GPU_observation
        report['CPU_video_IRQ_observation']=video_IRQ
        report['GPU_after_video_IRQ_observation']=GPU_after_IRQ
        report['CPU_continuation_after_GPU']=CPU_after_GPU
        report['further_explicit_video_events']=further_video
        report['source_C_verification']=bool(args.DSP_C and not args.DSP_boot_probe_C)
        report['initial_GPU_wait_C_selected']=args.GPU_initial_wait_C
        report['source_C_verification_scope']='FirstDSP and selected videoIRQ C; mainfirmwareCPU andGPU still original; no verified global clocks/disc boot'if args.video_IRQ_C else('First firmwareDSP only; preceding/followingCPU and optionalGPU probe run original instructions; no verified global clocks/disc boot'if args.DSP_C else'Native discovery only')
        if args.GPU_renderer_C:report['source_C_verification_scope']='FirstDSP, selectedvideoIRQ and GPUrenderer C; initialGPUwait C only if initial_GPU_wait_C_selected; mainCPU original; no verified globalclocks/discboot'
        if args.DSP_boot_probe_C:report['source_C_verification_scope']='Diagnostic extended C DSP execution with unverified processor ROM-view input; native comparison recorded separately. Following main CPU runs original instructions; no global clock/disc boot proof.'
        save(out/'report-before-shutdown.json',report);save(out/'status.json',dict(status='observation_recorded_pending_shutdown'))
        assert runtime.core.JaguarCDBiosStateSave(shortcut_check)==5 and shortcut_check.raw==shortcut_fixture
        runtime.oracle.close();closed=True;report['emulator_shutdown_completed']=True
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_observation_complete'))
        save(ROOT/'verification/relocated-firmware-observation.json',report)
        if args.DSP_C and not args.probe_GPU_shutdown and not args.DSP_ROM_view_mame_diagnostic:save(ROOT/'verification/relocated-firmware-DSP-C-linked.json',report)
        if args.DSP_ROM_view_mame_diagnostic:save(ROOT/'verification/firmware-DSP-ROM-view-diagnostic.json',report)
        if args.run_third_DSP:save(ROOT/'verification/firmware-third-DSP-CD-read-observation.json',report)
        if args.probe_GPU_shutdown:save(ROOT/'verification/firmware-GPU-shutdown-observation.json',report)
        if args.probe_CPU_video_IRQ:save(ROOT/'verification/firmware-CPU-video-IRQ-observation.json',report)
        if args.video_IRQ_C:save(ROOT/'verification/firmware-CPU-video-IRQ-C-linked.json',report)
        if args.resume_GPU_after_IRQ:save(ROOT/'verification/firmware-GPU-after-video-IRQ-observation.json',report)
        if args.GPU_renderer_C:save(ROOT/'verification/firmware-GPU-renderer-C-linked.json',report)
        if args.post_GPU_CPU_C:save(ROOT/'verification/firmware-post-GPU-CPU-C-linked.json',report)
        elif args.continue_CPU_after_GPU:save(ROOT/'verification/firmware-post-GPU-CPU-native-discovery.json',report)
        if args.advance_video_events:save(ROOT/'verification/firmware-further-video-observation.json',report)
        print(json.dumps({k:report[k]for k in ['status','stop_reason','executed_steps','unique_visited_PCs','final_CPU','GPU_PC','DSP_PC','GPU_GO','DSP_GO']}),flush=True)
    except BaseException as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:
        if not closed:runtime.oracle.close()

if __name__=='__main__':main()

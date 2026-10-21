"""Diagnostic C CPU instructions inside the ordinary frame scheduler.

Warm startup and GPU/DSP remain original providers. Missing C instructions,
service calls and prefetch queues reject; they never silently fall back.
"""
import argparse
import collections
import ctypes as c
import hashlib
import json
import struct
import time
import signal
import capstone
from datetime import datetime, timezone
from pathlib import Path
from probe_biwn_fresh_CD_boot import Variable, Game, write_video_PNG
import check_biwn_media_setup_cpu as media
from biwn_m68k_cycle_cost import Cost

ROOT = Path(__file__).resolve().parents[1]
sha = lambda value: hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['baseline', 'reference', 'C'], required=True)
    parser.add_argument('--warm-frames', type=int, default=600)
    parser.add_argument('--frames', type=int, default=4)
    parser.add_argument('--direction', choices=['none','U','D','L','R'], default='none')
    parser.add_argument('--frame-controller-script', type=Path,
                        help='Fixed ordinary-pad windows, numbered within the owned window')
    parser.add_argument('--navigation-plan',type=Path,help='Read-only waypoint planner; records ordinary buttons for a separate fixed-input comparison')
    parser.add_argument('--OP-GPU-mode', choices=['none','trace','C'], default='none')
    parser.add_argument('--OP-GPU-candidate',type=Path)
    parser.add_argument('--regular-GPU-mode', choices=['none','trace','C'], default='none')
    parser.add_argument('--core', type=Path)
    parser.add_argument('--source-CPU-IRQ-entry',action='store_true',help='Portable IRQ entry after original device ACK; C mode and diagnostic core only')
    parser.add_argument('--restore-original-report',type=Path,
                        help='Controlled continuation from an original run, with exact state round-trip check')
    parser.add_argument('--experimental-code-overlay',type=Path,
                        help='Explicit byte-checked RAM patches after exact checkpoint restore; original disc remains unchanged')
    parser.add_argument('--experimental-mainstage-overlay',type=Path,
                        help='Apply explicit byte-checked RAM patches once the original loader has loaded all matching mainstage bytes')
    parser.add_argument('--GPU-witness-limit',type=int,default=0)
    parser.add_argument('--GPU-witness-only',action='store_true')
    parser.add_argument('--stop-on-GPU-original',action='store_true',help='Diagnostic stop after first frame with an uncovered native GPU bundle')
    parser.add_argument('--renderer-bundles',action='store_true')
    parser.add_argument('--renderer-overlays',action='store_true')
    parser.add_argument('--material-bundles',action='store_true')
    parser.add_argument('--GPU-diagnostic-capture',action='store_true')
    parser.add_argument('--control-bundles',action='store_true')
    parser.add_argument('--setup-bundles',action='store_true')
    parser.add_argument('--native-GPU-bridge',action='store_true')
    parser.add_argument('--native-GPU-candidate',type=Path)
    parser.add_argument('--GPU-frame-only',action='store_true')
    parser.add_argument('--native-cycle-check',action='store_true')
    parser.add_argument('--extended-CPU',action='store_true')
    parser.add_argument('--native-CPU-bridge',action='store_true')
    parser.add_argument('--native-DSP-owner',action='store_true')
    parser.add_argument('--DSP-owner-kind',choices=['media','music','router'],default='media')
    parser.add_argument('--DSP-router-candidate',type=Path,help='Isolated router manifest; defaults unchanged')
    parser.add_argument('--require-owned-DSP',action='store_true',help='Stop at the first frame with uncovered original DSP execution')
    parser.add_argument('--DSP-owner-window',nargs=2,type=int,metavar=('START','STOP'),help='Owned-window frame interval for the fixed DSP media program')
    parser.add_argument('--capture-audio',action='store_true',help='Save exact frontend PCM callbacks for reference/C comparison')
    parser.add_argument('--capture-frame',type=int,action='append',default=[],help='Save a frontend PNG at this owned frame (maximum8)')
    parser.add_argument('--live-window',action='store_true',help='Experimental keyboard-controlled preview; no scripted inputs')
    parser.add_argument('--play-audio',action='store_true',help='Play frontend PCM through the default output device; optional preview sink')
    parser.add_argument('--no-instruction-trace',action='store_true',help='Native bridge counters only; cannot support instruction-trace comparison')
    parser.add_argument('--CPU-candidate',type=Path)
    parser.add_argument('--native-CPU-candidate',type=Path)
    parser.add_argument('--GPU-reference-trace',type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.live_window or (args.mode=='C' and args.native_CPU_bridge and not args.frame_controller_script and args.direction=='none')
    assert not args.navigation_plan or(not args.live_window and not args.frame_controller_script and args.direction=='none'and args.mode=='reference'and args.warm_frames==0)
    assert not args.no_instruction_trace or args.native_CPU_bridge
    live_window=None
    if args.live_window:
        from biwn_live_window import LiveWindow
        live_window=LiveWindow()
        signal.signal(signal.SIGINT,lambda *_:live_window.close())
        signal.signal(signal.SIGTERM,lambda *_:live_window.close())
    DSP_module=None
    if args.native_DSP_owner:
        if args.DSP_owner_kind=='router':
            import biwn_DSP_program_router as DSP_module
        elif args.DSP_owner_kind=='music':
            import biwn_DSP_music_owner as DSP_module
        else:
            import biwn_DSP_media_owner as DSP_module
    assert not args.native_DSP_owner or args.mode=='C'
    assert not args.source_CPU_IRQ_entry or args.mode=='C'
    assert not args.require_owned_DSP or args.native_DSP_owner
    assert not args.DSP_router_candidate or (args.native_DSP_owner and args.DSP_owner_kind=='router')
    assert not args.experimental_code_overlay or args.restore_original_report, 'Experimental overlay requires a recorded starting machine'
    assert not(args.experimental_code_overlay and args.experimental_mainstage_overlay)
    assert not args.experimental_mainstage_overlay or (args.warm_frames==0 and not args.restore_original_report)
    assert len(args.capture_frame)<=8 and all(1<=frame<=args.frames for frame in args.capture_frame)
    assert not args.DSP_owner_window or (args.native_DSP_owner and 1<=args.DSP_owner_window[0]<args.DSP_owner_window[1]<=args.frames+1)
    assert 0<=args.GPU_witness_limit<=256
    # A recorded startup-to-outdoor route exceeds the earlier24,000frame cap.
    # Keep the interactive and unscripted limits; only finite scripts get30,000.
    max_frames = 30000 if args.frame_controller_script else 24000 if args.live_window else 1200
    assert 0 <= args.warm_frames <= 1200 and 1 <= args.frames <= max_frames
    input_windows=[]
    # Pinned libretro default map: retropad X (9) maps to Jaguar keypad 0.
    from biwn_controller import JOYPAD_BUTTONS,KEYBOARD_BUTTONS,BUTTONS
    button_ids=JOYPAD_BUTTONS
    if args.frame_controller_script:
        assert args.direction=='none', 'Use one input schedule'
        input_windows=json.loads(args.frame_controller_script.read_text())['windows']
        for window in input_windows:
            assert set(window)=={'start_frame','stop_frame','buttons'}
            assert 1<=window['start_frame']<window['stop_frame']<=args.frames+1
            assert all(name in BUTTONS for name in window['buttons'])
    out = args.output.resolve()
    out.mkdir(parents=True)
    navigation=None;navigation_buttons=[]
    if args.navigation_plan:
        from biwn_navigation_controller import Navigation
        navigation=Navigation(args.navigation_plan,out)
    core_path = args.core or Path(json.loads((ROOT / 'verification/BIWN-frame-CPU-owner-candidate.json').read_text())['core_path'])
    CPU_candidate=json.loads((args.CPU_candidate or ROOT/('verification/extended-frame-CPU-candidate.json'if args.extended_CPU else'verification/controller-direction-library-current.json')).read_text())
    library=Path(CPU_candidate['library'])
    core = c.CDLL(str(core_path))
    system, saves = out / 'system', out / 'saves'
    system.mkdir(); saves.mkdir()
    options = {b'virtualjaguar_bios':b'enabled', b'virtualjaguar_usefastblitter':b'enabled',
               b'virtualjaguar_cd_boot_mode':b'hle', b'virtualjaguar_crash_detect':b'enabled'}
    paths = {9:str(system).encode(), 30:str(system).encode(), 31:str(saves).encode()}
    errors, video = [], {}
    audio = dict(frames=0, nonzero_samples=0)
    audio_output=None
    audio_output_error=None
    audio_stream=(out/'frontend-PCM.s16le').open('wb')if args.capture_audio else None
    ENV = c.CFUNCTYPE(c.c_bool, c.c_uint, c.c_void_p)
    VIDEO = c.CFUNCTYPE(None, c.c_void_p, c.c_uint, c.c_uint, c.c_size_t)
    AUDIO = c.CFUNCTYPE(None, c.c_int16, c.c_int16)
    BATCH = c.CFUNCTYPE(c.c_size_t, c.c_void_p, c.c_size_t)
    POLL = c.CFUNCTYPE(None)
    INPUT = c.CFUNCTYPE(c.c_int16, c.c_uint, c.c_uint, c.c_uint, c.c_uint)
    OWNER = c.CFUNCTYPE(c.c_int32, c.c_uint32)
    RETIRED = c.CFUNCTYPE(None, c.c_uint32, c.c_int32)
    def environment(cmd, data):
        cmd &= 255
        if cmd in paths:
            c.cast(data, c.POINTER(c.c_char_p))[0] = paths[cmd]; return True
        if cmd in [10,16,67]: return True
        if cmd == 15:
            var = c.cast(data, c.POINTER(Variable)).contents
            var.value = options.get(var.key); return var.value is not None
        if cmd == 17:
            c.cast(data, c.POINTER(c.c_bool))[0] = False; return True
        return False
    def draw(ptr, width, height, pitch):
        if ptr and width and height:
            video.update(width=width, height=height, pitch=pitch, raw=c.string_at(ptr, pitch*height))
    def sample(left, right):
        audio['frames'] += 1; audio['nonzero_samples'] += int(left != 0)+int(right != 0)
        if audio_stream:audio_stream.write(struct.pack('<hh',left,right))
        if audio_output and phase_input:audio_output.submit(struct.pack('<hh',left,right))
    def batch(ptr, frames):
        audio['frames'] += frames
        raw = c.string_at(ptr, frames*4) if ptr else b''
        if audio_stream:audio_stream.write(raw if ptr else bytes(frames*4))
        if audio_output and phase_input:audio_output.submit(raw if ptr else bytes(frames*4))
        audio['nonzero_samples'] += sum(raw[i:i+2] != b'\0\0' for i in range(0,len(raw),2))
        return frames
    direction_ids={'U':4,'D':5,'L':6,'R':7}
    phase_input=False
    owned_frame=0
    input_activity={}
    def input_state(port,device,index,button):
        if not(phase_input and port==0 and device in [1,3] and index==0):return 0
        if live_window:
            value=int(button in (live_window.pressed if device==1 else live_window.keyboard_pressed))
        elif navigation:
            mapping=JOYPAD_BUTTONS if device==1 else KEYBOARD_BUTTONS
            value=int(button in [mapping[name]for name in navigation_buttons if name in mapping])
        elif input_windows:
            mapping=JOYPAD_BUTTONS if device==1 else KEYBOARD_BUTTONS
            value=int(any(window['start_frame']<=owned_frame<window['stop_frame'] and
                button in [mapping[name]for name in window['buttons']if name in mapping]for window in input_windows))
        else:value=int(device==1 and button==direction_ids.get(args.direction))
        if value:
            key=str(device)+':'+str(button)
            input_activity[key]=input_activity.get(key,0)+1
        return value
    callbacks = [ENV(environment),VIDEO(draw),AUDIO(sample),BATCH(batch),POLL(lambda:None),INPUT(input_state)]
    for name, callback in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],callbacks):
        fn = getattr(core, 'retro_set_'+name); fn.argtypes=[type(callback)]; fn(callback)
    core.retro_load_game.argtypes=[c.POINTER(Game)]; core.retro_load_game.restype=c.c_bool
    core.retro_get_memory_data.argtypes=[c.c_uint]; core.retro_get_memory_data.restype=c.c_void_p
    core.BIWNReadCPUState.argtypes=[c.POINTER(media.CPU)]
    core.BIWNWriteCPUState.argtypes=[c.POINTER(media.CPU)]
    core.BIWNSetCPUExecOwner.argtypes=[OWNER,c.c_int]
    core.BIWNSetCPURetiredObserver.argtypes=[RETIRED]
    for name in ['Owned','Original','Rejected']:
        getattr(core,'BIWNCPU'+name+'InstructionCount').restype=c.c_uint64
    for width in [8,16,32]:
        read=getattr(core,'m68k_read_memory_'+str(width));read.argtypes=[c.c_uint32];read.restype=c.c_uint32
        write=getattr(core,'m68k_write_memory_'+str(width));write.argtypes=[c.c_uint32,c.c_uint32]
    clib=c.CDLL(str(library));step=getattr(clib,CPU_candidate.get('function','biwn_source_CPU_step'))
    step.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p];step.restype=c.c_int
    def reader(width):
        def fn(_, address, result):
            result[0]=getattr(core,'m68k_read_memory_'+str(width))(address);return 0
        return fn
    def writer(width):
        def fn(_,address,value):
            getattr(core,'m68k_write_memory_'+str(width))(address,value);return 0
        return fn
    types=media.scheduler.cleanup.world
    bus_callbacks=[types.R8(reader(8)),types.R16(reader(16)),types.R32(reader(32)),
                   types.W16(writer(16)),types.W32(writer(32)),media.W8(writer(8))]
    bus=media.Bus(*bus_callbacks[:5],types.CALL(),None,0)
    def forbidden_service(*_):
        errors.append('unexpected host CPU service');return 1
    service=media.world_cpu.SERVICE(forbidden_service)
    class TraceSink:
        def __init__(self,path):self.file=path.open('wb');self.length=0
        def extend(self,data):self.file.write(data);self.length+=len(data)
        def __len__(self):return self.length
        def close(self):self.file.close()
    streaming=args.frames>120 and not args.no_instruction_trace
    states=TraceSink(out/'CPU-before-instructions.bin')if streaming else bytearray()
    costs=TraceSink(out/'retired-instruction-costs.bin')if streaming else bytearray()
    counts=collections.Counter();frame_records=[]
    HLE_stub_RTS_count = 0
    fixed_C_function_calls = 0
    native_cycle_checks = 0
    core.retro_init()
    loaded=False
    try:
        disc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
        assert core.retro_load_game(c.byref(Game(str(disc).encode(),None,0,None)))
        loaded=True;ram=core.retro_get_memory_data(2);assert ram
        for _ in range(args.warm_frames):core.retro_run()
        restored_checkpoint=None
        if args.restore_original_report:
            assert args.mode in ['reference','C'], 'Original checkpoint continuation requires explicit reference or C mode'
            previous=json.loads(args.restore_original_report.read_text())
            assert previous['mode']=='reference' and (previous.get('original_CPU_instructions',0)>0 or
                previous.get('original_fresh_probe_checkpoint')and previous.get('original_processors_only'))
            assert previous['core_sha256']==sha(core_path.read_bytes())
            source_directory=Path(previous['directory'])
            if not source_directory.is_absolute():
                # Legacy reports used caller-relative paths. Checkpoints
                # carry their own files; anchor to the report we actually read.
                source_directory=args.restore_original_report.resolve().parent
                assert source_directory.name==Path(previous['directory']).name
            source=source_directory/'final-serialized-state.bin'
            if previous.get('ROM_provider_sha256'):
                ROM=(source.parent/'ROM-provider.bin').read_bytes()
                assert sha(ROM)==previous['ROM_provider_sha256']
                pointer=c.c_void_p.in_dll(core,'jaguarMainROM').value
                assert c.string_at(pointer,len(ROM))==ROM, 'Fresh warm ROM provider differs from original checkpoint'
            blob=source.read_bytes();buffer=c.create_string_buffer(blob)
            core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
            assert core.retro_unserialize(buffer,len(blob))
            core.retro_serialize_size.restype=c.c_size_t
            core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
            roundtrip=c.create_string_buffer(core.retro_serialize_size())
            assert core.retro_serialize(roundtrip,len(roundtrip))and roundtrip.raw==blob, 'Restored machine differs before execution'
            assert c.string_at(ram,0x200000)==(source.parent/'final-RAM.bin').read_bytes()
            restored_checkpoint=dict(report=str(args.restore_original_report),state_sha256=sha(blob),
                exact_machine_and_RAM_before_execution=True,scope='Captured original continuation; fresh firmware boot/full route not re-proved by this probe')
        experimental_overlay=None
        def apply_overlay(manifest,frame=None):
            overlay=json.loads(manifest.read_text())
            applied=[]
            for patch in overlay['patches']:
                address=int(patch['address'],16);original=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement'])
                assert len(original)==len(replacement)>0 and 0<=address<=0x200000-len(original)
                assert c.string_at(ram+address,len(original))==original, ('Overlay original bytes differ',hex(address))
                c.memmove(ram+address,replacement,len(replacement));applied.append(patch)
            return dict(manifest=str(manifest.resolve()),sha256=sha(manifest.read_bytes()),patches=applied,
                        after_exact_restore=frame is None,applied_before_frame=frame,original_disc_modified=False)
        if args.experimental_code_overlay:experimental_overlay=apply_overlay(args.experimental_code_overlay)
        (out/'warm-RAM.bin').write_bytes(c.string_at(ram,0x200000))
        state=media.CPU();core.BIWNReadCPUState(c.byref(state))
        warm_CPU=media.scheduler.cpu_dict(state)
        # The selected C library was validated with explicit platform
        # providers. Full-core HLE installs RTS aliases at these four PCs;
        # its ordinary instruction hook supplies the BIOS effects first.
        verified_source = Path(json.loads((ROOT / 'verification/controller-direction-current.json').read_text())['runs']['EQUIP-B-U']['sources']['native'])
        verified_RAM = (verified_source / 'native-RAM.bin').read_bytes()
        selected = CPU_candidate['selected_case_sources']
        if args.extended_CPU:
            verified_RAM_path=Path(CPU_candidate.get('instruction_RAM_source',CPU_candidate['warm_RAM_source']))
            if not verified_RAM_path.is_absolute():verified_RAM_path=ROOT.parents[1]/verified_RAM_path
            verified_RAM=verified_RAM_path.read_bytes()
        expected_opcodes = {int(pc,16):int.from_bytes(verified_RAM[int(pc,16):int(pc,16)+2],'big') for pc in selected}
        decoder = capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
        expected_instructions = {}
        def read_cost(address,width):
            assert 0 <= address <= 0x200000-width, ('cost read outside RAM',hex(address),width)
            return int.from_bytes(c.string_at(ram+address,width),'big')
        cost=Cost(read_cost)
        native_cost=None
        if args.native_cycle_check:
            timing=json.loads((ROOT/'verification/native-cycle-cost-candidate.json').read_text())
            timing_lib=c.CDLL(timing['library']);native_cost=timing_lib.biwn_native_cycle_cost
            native_cost.argtypes=[c.c_uint16,c.POINTER(media.CPU),c.c_void_p];native_cost.restype=c.c_int
        fixed_count=clib.biwn_instruction_observer_count;fixed_count.restype=c.c_uint64
        fixed_before=fixed_count()
        def own(pc):
            nonlocal HLE_stub_RTS_count, fixed_C_function_calls, native_cycle_checks
            if errors:return -1
            try:
                s=media.CPU();core.BIWNReadCPUState(c.byref(s));assert s.pc==pc
                states.extend(struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr));counts[pc]+=1
                if args.mode=='reference':return 0
                opcode = read_cost(pc,2)
                cycles,_=cost.predict(opcode,s)
                if native_cost:
                    actual=native_cost(opcode,c.byref(s),ram)
                    assert actual==cycles,('native cost mismatch',hex(pc),hex(opcode),cycles,actual)
                    native_cycle_checks+=1
                if pc in [0x303c,0x3042,0x304e,0x4088]:
                    assert opcode == 0x4e75, ('HLE stub changed',hex(pc),hex(opcode))
                    s.pc = core.m68k_read_memory_32(s.registers[15])
                    s.registers[15] += 4
                    if s.sr & 0x2000:s.ssp=s.registers[15]
                    else:s.usp=s.registers[15]
                    HLE_stub_RTS_count += 1
                else:
                    assert expected_opcodes.get(pc) == opcode, ('fixed C opcode identity mismatch',hex(pc),hex(opcode),expected_opcodes.get(pc))
                    if pc not in expected_instructions:
                        decoded = next(decoder.disasm(verified_RAM[pc:pc+24],pc,count=1),None)
                        assert decoded is not None and decoded.mnemonic != 'dc.w', ('source instruction length unknown',hex(pc))
                        expected_instructions[pc] = verified_RAM[pc:pc+decoded.size]
                    identity = expected_instructions[pc]
                    assert c.string_at(ram+pc,len(identity)) == identity, ('fixed C instruction bytes changed',hex(pc))
                    status=step(c.byref(bus),c.byref(s),bus_callbacks[5],service,None)
                    assert status in [0,6] and not errors, ('C instruction unsupported',hex(pc),status)
                    fixed_C_function_calls += 1
                core.BIWNWriteCPUState(c.byref(s));return cycles
            except BaseException as error:
                errors.append(repr(error));return -1
        def retired(pc,cycles):costs.extend(struct.pack('>Ii',pc,cycles))
        owner,observer=OWNER(own),RETIRED(retired)
        core.BIWNSetCPUExecOwner(owner if args.mode!='baseline' else OWNER(),int(args.mode=='C'))
        if args.mode!='baseline':core.BIWNSetCPURetiredObserver(observer)
        CPU_native_owner=None
        if args.native_CPU_bridge:
            assert args.extended_CPU and args.mode!='baseline'
            import biwn_fast_CPU_bridge
            CPU_native_owner=biwn_fast_CPU_bridge.install(core,out,args.mode,ram,args.native_CPU_candidate,trace=not args.no_instruction_trace)
        OP_owner=None
        regular_owner=None
        if args.OP_GPU_mode!='none':
            import biwn_frame_OP_GPU
            OP_owner=biwn_frame_OP_GPU.install(core,out,args.OP_GPU_mode,args.regular_GPU_mode,args.OP_GPU_candidate)
        if args.regular_GPU_mode!='none':
            if args.native_GPU_bridge:
                assert args.renderer_bundles and args.renderer_overlays and args.material_bundles and args.control_bundles and args.setup_bundles
                import biwn_fast_GPU_bridge
                regular_owner=biwn_fast_GPU_bridge.install(core,out,args.regular_GPU_mode,not args.GPU_frame_only,args.native_GPU_candidate)
            else:
                import biwn_regular_GPU_bundles
                regular_owner=biwn_regular_GPU_bundles.install(core,out,args.regular_GPU_mode,args.GPU_witness_limit,args.renderer_bundles,args.renderer_overlays,args.GPU_reference_trace,args.material_bundles,args.GPU_diagnostic_capture,args.control_bundles,args.setup_bundles,args.GPU_witness_only)
        if args.play_audio:
            try:
                from biwn_audio_output import AudioOutput,core_audio_rate
                audio_output=AudioOutput(core_audio_rate(core))
                if live_window:
                    live_window.audio_output=audio_output
                    live_window.audio_message='Audio on'
                else:audio_output.set_state(suspended=False)
            except Exception as exc:
                audio_output_error=f'{type(exc).__name__}: {exc}'
                if live_window:live_window.audio_message='Audio unavailable'
                print('Audio output unavailable: '+audio_output_error,flush=True)
        phase_input=True
        DSP_owner=None
        DSP_report=None
        CPU_IRQ_owner=None
        if args.source_CPU_IRQ_entry:
            import biwn_CPU_IRQ_owner
            CPU_IRQ_owner=biwn_CPU_IRQ_owner.install(core,out)
        if args.native_DSP_owner and not args.DSP_owner_window:
            DSP_owner=DSP_module.install(core,out,args.DSP_router_candidate) if args.DSP_owner_kind=='router' else DSP_module.install(core,out)
        for frame in range(args.frames):
            if live_window:
                if not live_window.poll(video,frame):break
                if audio_output:audio_output.set_state(suspended=live_window.paused)
                (out/'live-window.json').write_text(json.dumps(dict(
                    status='paused'if live_window.paused else'running',completed_frames=frame,
                    input_events=live_window.input_events,pressed_buttons=sorted(live_window.pressed),keyboard_codes=sorted(live_window.keyboard_pressed),
                    audio_output=audio_output.report()if audio_output else None,audio_output_error=audio_output_error,
                    keyboard_interaction_verified=False,scope='Application telemetry, not external UI verification.'),indent=2)+'\n')
                while live_window.paused and not live_window.closed:
                    time.sleep(0.03)
                    live_window.poll({},frame)
                if live_window.closed:break
                if audio_output:audio_output.set_state(suspended=False)
            owned_frame=frame+1
            if args.DSP_owner_window:
                if owned_frame==args.DSP_owner_window[0]:
                    DSP_owner=DSP_module.install(core,out,args.DSP_router_candidate) if args.DSP_owner_kind=='router' else DSP_module.install(core,out)
                elif owned_frame==args.DSP_owner_window[1] and DSP_owner:
                    DSP_report=DSP_owner[3]();DSP_owner=None
                    if DSP_report['status']=='rejected':errors.append('Native DSP source rejection '+str(DSP_report));break
            if args.experimental_mainstage_overlay and experimental_overlay is None:
                patches=json.loads(args.experimental_mainstage_overlay.read_text())['patches']
                if all(c.string_at(ram+int(patch['address'],16),len(bytes.fromhex(patch['original'])))==bytes.fromhex(patch['original'])for patch in patches):
                    experimental_overlay=apply_overlay(args.experimental_mainstage_overlay,frame+1)
                    print(json.dumps(dict(event='experimental_mainstage_overlay_applied',before_frame=frame+1,manifest=str(args.experimental_mainstage_overlay))),flush=True)
            if navigation:navigation_buttons=navigation.step(c.string_at(ram+0x49c4c,128),owned_frame)
            core.retro_run();core.BIWNReadCPUState(c.byref(state))
            if CPU_IRQ_owner and core.BIWNCPUIRQRejectedCount():
                errors.append('Source CPU IRQ entry rejected; no original entry fallback')
            frame_records.append(dict(frame=frame+1,CPU=media.scheduler.cpu_dict(state),
                                      RAM=sha(c.string_at(ram,0x200000)),video=sha(video.get('raw',b'')),audio=dict(audio)))
            if frame+1 in args.capture_frame and video.get('raw'):
                write_video_PNG(out/('frame-'+str(frame+1)+'.png'),video['raw'],video['width'],video['height'],video['pitch'])
                (out/('frame-'+str(frame+1)+'-RAM.bin')).write_bytes(c.string_at(ram,0x200000))
                (out/('frame-'+str(frame+1)+'-CPU.json')).write_text(json.dumps(media.scheduler.cpu_dict(state),indent=2)+'\n')
            if (frame+1)%60==0:
                (out/'progress.json').write_text(json.dumps(dict(status='running',completed_frames=frame+1,requested_frames=args.frames,CPU_instructions=(core.BIWNCPUOwnedInstructionCount()if CPU_native_owner and args.mode=='C'else core.BIWNCPUOriginalInstructionCount()if CPU_native_owner else len(states)//78),errors=errors),indent=2)+'\n')
            if errors or core.BIWNCPURejectedInstructionCount() or (OP_owner and OP_owner[3]) or (regular_owner and regular_owner[3]):break
            if DSP_owner and core.BIWNDSPRejectedInstructionCount()>0:break
            if DSP_owner and args.require_owned_DSP and core.BIWNDSPOriginalInstructionCount()>0:
                errors.append('Uncovered DSP execution at owned frame '+str(owned_frame));break
            if args.stop_on_GPU_original:
                assert regular_owner and args.native_GPU_bridge
                if regular_owner[2].biwn_fast_GPU_unknown_count()>0:break
        if args.experimental_mainstage_overlay and experimental_overlay is None:
            errors.append('Mainstage overlay was never applied; all original byte checks must match')
        OP_report=OP_owner[4]() if OP_owner else None
        if OP_report and OP_report['status']=='rejected':errors.extend(OP_report['errors'] or ['OP GPU release rejected'])
        regular_report=regular_owner[4]()if regular_owner else None
        if regular_report and regular_report['status']=='rejected':errors.extend(regular_report['errors'] or ['regular GPU bundle rejected'])
        CPU_native_report=CPU_native_owner[4]()if CPU_native_owner else None
        if DSP_owner:DSP_report=DSP_owner[3]()
        if DSP_report and DSP_report['status']=='rejected':errors.append('Native DSP source rejection '+str(DSP_report))
        CPU_IRQ_report=CPU_IRQ_owner[4]()if CPU_IRQ_owner else None
        if audio_stream:audio_stream.flush()
        if CPU_native_report:
            fixed_C_function_calls=CPU_native_report['steps'];HLE_stub_RTS_count=CPU_native_report['HLE']
            if CPU_native_report['errors']:errors.append('Native CPU bridge rejection '+str(CPU_native_report))
        if streaming:states.close();costs.close()
        elif not CPU_native_owner:
            (out/'CPU-before-instructions.bin').write_bytes(states)
            (out/'retired-instruction-costs.bin').write_bytes(costs)
        (out/'final-RAM.bin').write_bytes(c.string_at(ram,0x200000))
        core.retro_serialize_size.restype=c.c_size_t
        core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
        size=core.retro_serialize_size();blob=c.create_string_buffer(size);assert core.retro_serialize(blob,size)
        (out/'final-serialized-state.bin').write_bytes(blob.raw)
        if video:
            write_video_PNG(out/'final-frame.png',video['raw'],video['width'],video['height'],video['pitch'])
            (out/'final-video.bin').write_bytes(video.pop('raw'))
        report=dict(status='completed_component_uncompared'if not errors and not core.BIWNCPURejectedInstructionCount()else'rejected',
                    directory=str(out),mode=args.mode,core=str(core_path),core_sha256=sha(core_path.read_bytes()),
                    CPU_library=str(library),warm_original_frames=args.warm_frames,warm_CPU=warm_CPU,requested_frames=args.frames,
                    restored_original_checkpoint=restored_checkpoint,
                    experimental_code_overlay=experimental_overlay,
                    direction=args.direction,fixed_C_instruction_steps=fixed_C_function_calls,native_cycle_checks=native_cycle_checks,
                    frame_controller_script=str(args.frame_controller_script)if args.frame_controller_script else None,
                    frame_controller_script_sha256=sha(args.frame_controller_script.read_bytes())if args.frame_controller_script else None,
                    navigation_plan=navigation.finish()if navigation else None,
                    OP_GPU_report=str(out/'OP-GPU-slices/report.json') if OP_report else None,
                    regular_GPU_report=str(out/'regular-GPU-bundles/report.json') if regular_report else None,
                    DSP_report=str(out/'DSP-owner-report.json')if DSP_report else None,
                    CPU_IRQ_report=str(out/'CPU-IRQ-owner-report.json')if CPU_IRQ_report else None,
                    DSP_owner_window=args.DSP_owner_window if args.native_DSP_owner else None,
                    DSP_owner_kind=args.DSP_owner_kind if args.native_DSP_owner else None,
                    PCM_capture=str(out/'frontend-PCM.s16le')if audio_stream else None,
                    instruction_observer_callbacks=fixed_count()-fixed_before,
                    frames=frame_records,errors=errors,CPU_before_instructions=(CPU_native_report['calls']if CPU_native_report else len(states)//78),unique_CPU_PCs=(None if CPU_native_report else len(counts)),
                    PC_counts={hex(k):v for k,v in counts.items()},owned_CPU_instructions=core.BIWNCPUOwnedInstructionCount(),
                    HLE_stub_RTS_count=HLE_stub_RTS_count,expected_opcode_source=str(verified_source),
                    original_CPU_instructions=core.BIWNCPUOriginalInstructionCount(),rejected_CPU_instructions=core.BIWNCPURejectedInstructionCount(),
                    video=video,audio=audio,new_training=False,whole_game_complete=False,
                    limits=['Original warm startup or explicit original checkpoint; requested processor ownership window only. Core IRQ/HLE/devices remain providers.',
                            'Rejects nonempty prefetch queues; no physical timing/full game/standalone claim.'])
        report.update(controller_input_activity=input_activity,interactive_window=bool(live_window),instruction_trace_recorded=not args.no_instruction_trace)
        report.update(audio_output=audio_output.report()if audio_output else None,audio_output_error=audio_output_error)
        if live_window and report['status']!='rejected':
            report['status']='interactive_stopped_uncompared'
            report['live_keyboard_input_verified']=False
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report[k]for k in ['status','owned_CPU_instructions','original_CPU_instructions','rejected_CPU_instructions','errors']}),flush=True)
        if report['status']=='rejected':raise SystemExit(1)
    finally:
        if audio_output:
            try:audio_output.close()
            except Exception as exc:print('Audio output cleanup: '+str(exc),flush=True)
        if live_window and not live_window.closed:live_window.close()
        if args.source_CPU_IRQ_entry and hasattr(core,'BIWNSetCPUIRQOwner'):core.BIWNSetCPUIRQOwner(None)
        if audio_stream:audio_stream.close()
        if args.native_DSP_owner:
            core.BIWNSetDSPInstructionOwner(DSP_module.OWNER())
        core.BIWNSetCPUExecOwner(OWNER(),0);core.BIWNSetCPURetiredObserver(RETIRED())
        if loaded:core.retro_unload_game()
        core.retro_deinit()


if __name__=='__main__':main()

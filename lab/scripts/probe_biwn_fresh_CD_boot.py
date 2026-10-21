"""Fresh libretro CD loads; no seeded CPU, savestate or diagnostic switches.

Original emulation only. This discovers boot prerequisites, not a C decompile.
Each configuration must run in a separate process because the core is global.
"""
import argparse
import ctypes as c
import hashlib
import json
import math
import struct
import time
import wave
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Variable(c.Structure):
    _fields_ = [('key', c.c_char_p), ('value', c.c_char_p)]


class Game(c.Structure):
    _fields_ = [('path', c.c_char_p), ('data', c.c_void_p),
                ('size', c.c_size_t), ('meta', c.c_char_p)]


class Geometry(c.Structure):
    _fields_=[('base_width',c.c_uint),('base_height',c.c_uint),
              ('max_width',c.c_uint),('max_height',c.c_uint),('aspect_ratio',c.c_float)]


class Timing(c.Structure):
    _fields_=[('fps',c.c_double),('sample_rate',c.c_double)]


class AVInfo(c.Structure):
    _fields_=[('geometry',Geometry),('timing',Timing)]


class Strategy(c.Structure):
    _fields_ = [('name', c.c_char_p), ('boot', c.c_void_p),
                ('instruction_hook', c.c_void_p), ('reset', c.c_void_p)]


class BootConfig(c.Structure):
    _fields_ = [('is_CD', c.c_bool), ('show_ROM', c.c_bool),
                ('has_CD_BIOS', c.c_bool), ('strategy', c.POINTER(Strategy))]


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def write_video_PNG(path, raw, width, height, pitch):
    """Encode the core's little-endian XRGB8888 output without extra packages."""
    assert pitch >= width*4 and len(raw) == height*pitch
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        line = raw[y*pitch:y*pitch+width*4]
        for x in range(0,len(line),4):
            pixels.extend((line[x+2],line[x+1],line[x]))
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
                     +chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bios', choices=['retail', 'dev'], default='retail')
    parser.add_argument('--boot', choices=['bios', 'hle'], default='bios')
    parser.add_argument('--frames', type=int, default=600)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--firmware-assists', choices=['default', 'hooks-off', 'all-off'], default='default')
    parser.add_argument('--trace-firmware', action='store_true')
    parser.add_argument('--input-plan', choices=['none', 'up-left'], default='none')
    parser.add_argument('--frame-controller-script', type=Path,
                        help='JSON windows with start_frame/stop_frame and normal U/D/L/R/A/B/C/OPTION/PAUSE inputs')
    parser.add_argument('--no-publish', action='store_true')
    parser.add_argument('--navigate-actor', type=int,
                        help='Reference discovery: steer with ordinary pad inputs toward a live actor record; no guest writes')
    parser.add_argument('--navigate-point', nargs=2, type=int, metavar=('X', 'Z'),
                        help='Reference discovery: ordinary-pad steering toward a fixed coordinate; no guest position writes')
    parser.add_argument('--navigate-waypoints', type=Path,
                        help='JSON points along a source-derived route; ordinary pad inputs only')
    parser.add_argument('--stop-after-scene-change', type=int, default=0,
                        help='With waypoints, stop this many frames after scene/mode changes from warm startup')
    parser.add_argument('--scene-change-controller-script', type=Path,
                        help='Ordinary button windows relative to the first scene/mode change')
    parser.add_argument('--post-scene-navigate-actor', type=int,
                        help='After the button windows, steer toward a live actor with ordinary pad inputs')
    parser.add_argument('--post-scene-navigation-offset', type=int, default=1101)
    parser.add_argument('--post-scene-waypoints', type=Path,
                        help='JSON corridor points to follow before approaching the post-scene actor')
    parser.add_argument('--capture-audio',action='store_true',
                        help='Save original-core frontend PCM callbacks at its declared sample rate')
    parser.add_argument('--save-frame-checkpoints',nargs='+',type=int,default=[],
                        help='Save exact original machine states at selected frame boundaries')
    parser.add_argument('--save-scene-change-checkpoint',action='store_true',
                        help='Save the first ordinary waypoint scene/mode change as an original checkpoint')
    parser.add_argument('--hle-entry', choices=['native', 'C'])
    parser.add_argument('--core', type=Path)
    parser.add_argument('--source-CPU-IRQ-entry',action='store_true',help='Isolated portable IRQ entry after original device ACK; requires its diagnostic core')
    parser.add_argument('--observe-DSP-window',nargs=2,type=int,metavar=('START','STOP'),
                        help='Read-only original DSP main/inline-delay observation in [START,STOP) frames; requires diagnostic observer core')
    parser.add_argument('--DSP-witness-limit',type=int,default=128,
                        help='Maximum distinct DSP instruction/microstate snapshots; counters remain complete')
    parser.add_argument('--own-DSP-window',nargs=2,type=int,metavar=('START','STOP'),help='Experimental fixed C DSP source execution in [START,STOP); requires pinned DSP-owner core')
    parser.add_argument('--DSP-owner-kind',choices=['media','music','router'],default='media',
                        help='Isolated fixed-source DSP program; music requires its context core')
    parser.add_argument('--DSP-router-candidate',type=Path,help='Isolated router manifest; does not change defaults')
    parser.add_argument('--require-owned-DSP',action='store_true',
                        help='Stop at the first frame using an uncovered original DSP instruction in the owner window')
    parser.add_argument('--hle-prefix', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.frames <= (24000 if args.post_scene_navigate_actor is not None or args.frame_controller_script or args.navigate_waypoints else 14400)
    assert all(1<=n<=args.frames for n in args.save_frame_checkpoints)
    assert not args.observe_DSP_window or 1<=args.observe_DSP_window[0]<args.observe_DSP_window[1]<=args.frames+1
    assert 1 <= args.DSP_witness_limit <= 4096
    assert not args.own_DSP_window or 1<=args.own_DSP_window[0]<args.own_DSP_window[1]<=args.frames+1
    assert not args.require_owned_DSP or args.own_DSP_window
    assert not args.DSP_router_candidate or (args.own_DSP_window and args.DSP_owner_kind=='router')
    assert not(args.own_DSP_window and args.observe_DSP_window)
    assert not args.save_scene_change_checkpoint or args.navigate_waypoints
    assert not (args.save_frame_checkpoints or args.save_scene_change_checkpoint) or (args.hle_entry is None and args.own_DSP_window is None)
    assert not args.source_CPU_IRQ_entry or not(args.save_frame_checkpoints or args.save_scene_change_checkpoint or args.hle_entry),'Original-only checkpoints cannot include the source IRQ owner'
    if args.hle_entry: assert args.boot=='hle'
    if args.hle_prefix: assert args.hle_entry is not None
    if args.firmware_assists != 'default':
        assert args.boot == 'bios' and args.bios == 'retail'
    if args.trace_firmware:
        assert args.firmware_assists != 'default'
    button_ids = {'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 8,
                  'B': 0, 'C': 1, 'OPTION': 3, 'PAUSE': 2}
    input_windows = []
    if args.navigate_actor is not None:
        # Source factory13B1C..13B26 scans slots0..0x27 inclusive.
        # Addresses after the40-record pool are unrelated guest data.
        assert 0 <= args.navigate_actor < 40, 'Actor slot must be0..39'
        assert args.input_plan == 'none' and args.frame_controller_script is None
        assert args.navigate_point is None
    if args.navigate_point is not None:
        assert args.input_plan == 'none' and args.frame_controller_script is None
        assert all(-0x80000000 <= value <= 0x7fffffff for value in args.navigate_point)
    waypoints = []
    waypoint_index = 0
    navigation_start_scene = None
    navigation_start_mode = None
    scene_change_frame = None
    scene_change_windows = []
    post_waypoints=[]
    post_waypoint_index=0
    if args.navigate_waypoints:
        assert args.navigate_actor is None and args.navigate_point is None
        assert args.input_plan == 'none' and args.frame_controller_script is None
        waypoints = json.loads(args.navigate_waypoints.read_text())['points']
        assert waypoints and all(isinstance(p,list) and len(p)==2 and
            all(type(v) is int and -0x80000000<=v<=0x7fffffff for v in p) for p in waypoints)
    assert 0 <= args.stop_after_scene_change <= (15000 if args.post_scene_navigate_actor is not None else 1200)
    assert not args.stop_after_scene_change or waypoints
    if args.post_scene_navigate_actor is not None:
        assert 0<=args.post_scene_navigate_actor<40 and waypoints
        assert 1<=args.post_scene_navigation_offset<args.stop_after_scene_change
    if args.post_scene_waypoints:
        assert args.post_scene_navigate_actor is not None
        post_waypoints=json.loads(args.post_scene_waypoints.read_text())['points']
        assert all(isinstance(p,list)and len(p)==2 and all(type(v)is int for v in p)for p in post_waypoints)
    if args.scene_change_controller_script:
        assert waypoints and args.stop_after_scene_change
        scene_change_windows=json.loads(args.scene_change_controller_script.read_text())['windows']
        for window in scene_change_windows:
            assert set(window)=={'start_offset','stop_offset','buttons'}
            assert 1<=window['start_offset']<window['stop_offset']<=args.stop_after_scene_change+1
            assert all(name in button_ids for name in window['buttons'])
    navigation_enabled = args.navigate_actor is not None or args.navigate_point is not None or bool(waypoints)
    if args.frame_controller_script:
        assert args.input_plan == 'none', 'Use one input schedule'
        for window in json.loads(args.frame_controller_script.read_text())['windows']:
            assert set(window) == {'start_frame', 'stop_frame', 'buttons'}
            assert 1 <= window['start_frame'] < window['stop_frame'] <= args.frames + 1
            input_windows.append({**window, 'ids': [button_ids[name] for name in window['buttons']]})
    core_path = args.core or ROOT / 'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    disc = ROOT / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    out = args.output.resolve() if args.output else ROOT / 'verification/BIWN-fresh-CD-boot' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True, exist_ok=False)
    system = out / 'empty-system'; system.mkdir()
    saves = out / 'private-saves'; saves.mkdir()
    options = {
        b'virtualjaguar_bios': b'enabled',
        b'virtualjaguar_usefastblitter': b'enabled',
        b'virtualjaguar_cd_bios_type': args.bios.encode(),
        b'virtualjaguar_cd_boot_mode': args.boot.encode(),
        b'virtualjaguar_crash_detect': b'enabled',
    }
    paths = {9: str(system).encode(), 30: str(system).encode(), 31: str(saves).encode()}
    options_read = {}
    errors = []
    video = {}; audio = {'frames': 0, 'nonzero_samples': 0}
    audio_stream=(out/'frontend-PCM.s16le').open('wb')if args.capture_audio else None
    firmware_trace = []; visit_counts = {}; current_frame = 0; previous_PC = None
    pressed_input_samples = {}; input_sample_count = 0
    navigation = None
    navigation_inputs = set()
    ENV = c.CFUNCTYPE(c.c_bool, c.c_uint, c.c_void_p)
    VIDEO = c.CFUNCTYPE(None, c.c_void_p, c.c_uint, c.c_uint, c.c_size_t)
    AUDIO = c.CFUNCTYPE(None, c.c_int16, c.c_int16)
    BATCH = c.CFUNCTYPE(c.c_size_t, c.c_void_p, c.c_size_t)
    POLL = c.CFUNCTYPE(None)
    INPUT = c.CFUNCTYPE(c.c_int16, c.c_uint, c.c_uint, c.c_uint, c.c_uint)
    HOOK = c.CFUNCTYPE(c.c_bool, c.c_uint32)
    DSP_OBSERVER=c.CFUNCTYPE(None,c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32)
    DSP_observation={'callbacks':0,'PC_opcodes':{},'flags_retire_delays':{},'hazards':{},'witnesses':[],'errors':[]}
    DSP_witness_keys=set()
    def observe_DSP(pc,opcode,retire_delay,pre_bank,hazards):
        try:
            DSP_observation['callbacks']+=1
            key=hex(pc)+':'+hex(opcode)
            DSP_observation['PC_opcodes'][key]=DSP_observation['PC_opcodes'].get(key,0)+1
            for field,value in [('flags_retire_delays',retire_delay),('hazards',hazards)]:
                key=str(value);DSP_observation[field][key]=DSP_observation[field].get(key,0)+1
            key=(pc,opcode,retire_delay,pre_bank,hazards)
            if key not in DSP_witness_keys and len(DSP_witness_keys)<args.DSP_witness_limit:
                DSP_witness_keys.add(key);buffer=c.create_string_buffer(32768);size=core.DSPStateSave(buffer);assert 8496<=size<=len(buffer)
                raw=buffer.raw[:size];name='DSP-witness-%03d.bin'%len(DSP_witness_keys);(out/name).write_bytes(raw)
                DSP_observation['witnesses'].append(dict(frame=current_frame,PC=hex(pc),opcode=hex(opcode),retire_delay=retire_delay,pre_store_bank=pre_bank,hazards=hazards,file=str(out/name),bytes=size,sha256=hashlib.sha256(raw).hexdigest()))
        except BaseException as error:DSP_observation['errors'].append(repr(error))
    DSP_callback=DSP_OBSERVER(observe_DSP)
    DSP_owner=None

    def environment(cmd, data):
        try:
            cmd &= 0xff
            if cmd in paths:
                c.cast(data, c.POINTER(c.c_char_p))[0] = paths[cmd]
                return True
            if cmd in [10, 16, 67]:
                return True
            if cmd == 15:
                var = c.cast(data, c.POINTER(Variable)).contents
                value = options.get(var.key)
                var.value = value
                if value is not None:
                    options_read[var.key.decode()] = value.decode()
                return value is not None
            if cmd == 17:
                c.cast(data, c.POINTER(c.c_bool))[0] = False
                return True
            return False
        except BaseException as error:
            errors.append(repr(error)); return False

    def video_refresh(data, width, height, pitch):
        if data and data != c.c_void_p(-1).value and width and height:
            video.update(width=width, height=height, pitch=pitch,
                         raw=c.string_at(data, pitch * height))

    def sample(left, right):
        audio['frames'] += 1
        audio['nonzero_samples'] += int(left != 0) + int(right != 0)
        if audio_stream:audio_stream.write(struct.pack('<hh',left,right))

    def batch(data, frames):
        audio['frames'] += frames
        if data:
            raw = c.string_at(data, frames * 4)
            if audio_stream:audio_stream.write(raw)
            audio['nonzero_samples'] += sum(raw[i:i+2] != b'\0\0' for i in range(0, len(raw), 2))
        elif audio_stream:
            audio_stream.write(bytes(frames*4))
        return frames

    def input_state(port, device, index, button):
        nonlocal input_sample_count
        input_sample_count += 1
        pressed = (args.input_plan == 'up-left' and port == 0 and device == 1 and index == 0
                   and ((300 <= current_frame < 360 and button == 4)
                        or (360 <= current_frame < 420 and button == 6)))
        if args.frame_controller_script:
            pressed = port == 0 and device == 1 and index == 0 and any(
                w['start_frame'] <= current_frame < w['stop_frame'] and button in w['ids']
                for w in input_windows)
        if navigation_enabled:
            pressed = port == 0 and device == 1 and index == 0 and button in navigation_inputs
        if pressed:
            pressed_input_samples[str(button)] = pressed_input_samples.get(str(button), 0) + 1
        return int(pressed)

    callbacks = [ENV(environment), VIDEO(video_refresh), AUDIO(sample),
                 BATCH(batch), POLL(lambda: None), INPUT(input_state)]
    core = c.CDLL(str(core_path))
    names = ['environment', 'video_refresh', 'audio_sample', 'audio_sample_batch',
             'input_poll', 'input_state']
    for name, callback in zip(names, callbacks):
        fn = getattr(core, 'retro_set_' + name); fn.argtypes = [type(callback)]; fn(callback)
    core.retro_load_game.argtypes = [c.POINTER(Game)]; core.retro_load_game.restype = c.c_bool
    core.m68k_get_reg.argtypes = [c.c_void_p, c.c_int]; core.m68k_get_reg.restype = c.c_uint32
    core.m68k_read_memory_32.argtypes = [c.c_uint32]; core.m68k_read_memory_32.restype = c.c_uint32
    core.GPUGetPC.restype = core.DSPGetPC.restype = c.c_uint32
    core.retro_get_memory_data.argtypes = [c.c_uint]; core.retro_get_memory_data.restype = c.c_void_p
    core.GPUStateSave.argtypes = [c.c_void_p]; core.GPUStateSave.restype = c.c_size_t
    core.CDIntfGetNumSessions.restype = core.CDIntfGetNumTracks.restype = c.c_uint32
    report = dict(status='running', directory=str(out), core=str(core_path),
                  core_sha256=hashlib.sha256(core_path.read_bytes()).hexdigest(),
                  disc=str(disc), disc_sha256=hashlib.sha256(disc.read_bytes()).hexdigest(),
                  requested_options={k.decode(): v.decode() for k, v in options.items()},
                  captured_state_input=False, host_CPU_or_GPU_register_seed=False,
                  external_BIOS_input=False, diagnostic_switches_set=False,
                  firmware_assists=args.firmware_assists,
                  input_plan=args.input_plan,
                  frame_controller_script=str(args.frame_controller_script) if args.frame_controller_script else None,
                  input_windows=input_windows,
                  normal_input_only=True,
                  navigation_actor=args.navigate_actor,
                  navigation_point=args.navigate_point,
                  navigation_waypoints=waypoints,
                  navigation_waypoints_source=str(args.navigate_waypoints) if waypoints else None,
                  stop_after_scene_change_frames=args.stop_after_scene_change,
                  scene_change_controller_windows=scene_change_windows,
                  post_scene_navigation_actor=args.post_scene_navigate_actor,
                  post_scene_navigation_offset=args.post_scene_navigation_offset,
                  post_scene_waypoints=post_waypoints,
                  navigation_scope='Coordinator deterministic steering from live position/heading; ordinary pad inputs only; not local-LLM navigation or C verification',
                  built_in_firmware_assists='Default BIOS strategy clears cart authentication bit; instruction hook writes GPU auth magic and injects boot stub/trampoline/TOC. These are emulator interventions, not source firmware proof.',
                  source_C_execution=bool(args.hle_entry or args.own_DSP_window or args.source_CPU_IRQ_entry), whole_game_complete=False,
                  scope='Original full-core emulation after ordinary libretro content load; included BIOS, private empty system/save dirs, documented normal frontend input. HLE boot bypasses real firmware and cannot prove authenticated boot.')
    save(out / 'protocol.json', report); print(out, flush=True)
    loaded = False; initialized = False
    try:
        core.retro_init(); initialized = True
        game = Game(str(disc).encode(), None, 0, None)
        loaded = bool(core.retro_load_game(c.byref(game)))
        assert loaded, 'Ordinary retro_load_game failed'
        av=AVInfo();assert c.sizeof(av)==40
        core.retro_get_system_av_info.argtypes=[c.POINTER(AVInfo)]
        core.retro_get_system_av_info(c.byref(av))
        report['frontend_declared_fps']=av.timing.fps
        report['frontend_declared_audio_rate']=av.timing.sample_rate
        ram_pointer = core.retro_get_memory_data(2)
        assert ram_pointer
        rom = c.c_void_p.in_dll(core, 'jaguarMainROM').value
        config = BootConfig.in_dll(core, 'bootConfig')
        report['boot_strategy'] = config.strategy.contents.name.decode()
        PC_ring = (c.c_uint32*1024).in_dll(core, 'pcQueue') if args.trace_firmware else None
        PC_ring_pointer = c.c_uint32.in_dll(core, 'pcQPtr') if args.trace_firmware else None
        def observe_firmware(pc):
            nonlocal previous_PC
            try:
                # Returning false leaves execution to the original instruction.
                # Observe only source authentication/setup boundaries, not every
                # polling iteration. No machine state is changed here.
                if pc in [0x802000, 0x500d6, 0x5e40, 0x50b6, 0x50176,
                          0x80000, 0x82fa2, 0x5017c, 0x50222, 0x5022e,
                          0x5023c, 0x50282, 0x1000, 0x180000, 0x4000]:
                    count = visit_counts.get(pc, 0) + 1; visit_counts[pc] = count
                    if count <= 4:
                        ram = c.string_at(ram_pointer, 0x200000)
                        g = c.create_string_buffer(12000); assert core.GPUStateSave(g) == 4416
                        firmware_trace.append(dict(frame=current_frame, PC=hex(pc), visit=count,
                            last_source_CPU_PCs=[hex(PC_ring[(PC_ring_pointer.value-128+j)&1023]) for j in range(128)],
                            previous_PC=hex(previous_PC) if previous_PC is not None else None,
                            previous_instruction_bytes=(c.string_at(ram_pointer+previous_PC, 32).hex()
                                if previous_PC is not None and 0<=previous_PC<0x200000-32
                                else c.string_at(rom+previous_PC-0x800000,32).hex()
                                if previous_PC is not None and 0x800000<=previous_PC<0x840000-32 else None),
                            CPU_registers=[core.m68k_get_reg(None, i) for i in range(18)],
                            RAM_auth_wait_bytes=ram[0x5080:0x50d0].hex(),
                            RAM_GPU_auth_driver=ram[0x5df0:0x5e80].hex(),
                            GPU_PC=hex(core.GPUGetPC()), GPU_state_sha256=hashlib.sha256(g.raw[:4416]).hexdigest(),
                            DSP_local_auth_word=hex(core.m68k_read_memory_32(0xf1b000)),
                            GPU_local_auth_prefix=g.raw[:96].hex(),
                            GPU_R31_banks=[hex(int.from_bytes(g.raw[o:o+4], 'little')) for o in [4263,4391]]))
                        stamp = '%02d-%06x' % (len(firmware_trace), pc)
                        (out/(stamp+'-RAM.bin')).write_bytes(ram)
                        (out/(stamp+'-GPU.bin')).write_bytes(g.raw[:4416])
            except BaseException as error:
                errors.append(repr(error))
            previous_PC = pc
            return False
        trace_callback = HOOK(observe_firmware) if args.trace_firmware else None
        if args.firmware_assists != 'default':
            assert c.sizeof(BootConfig) == 16 and BootConfig.strategy.offset == 8
            assert report['boot_strategy'] == 'bios'
            original_strategy = Strategy.from_buffer_copy(bytes(config.strategy.contents))
            diagnostic_strategy = Strategy(original_strategy.name, original_strategy.boot,
                                           c.cast(trace_callback, c.c_void_p).value if trace_callback else None,
                                           original_strategy.reset)
            config.strategy = c.pointer(diagnostic_strategy)
            report['instruction_hook_disabled_before_first_frame'] = True
        if args.firmware_assists == 'all-off':
            original_bios = (ROOT/'render-assets/jaguarcd_bios.bin').read_bytes()
            modified_bios = bytearray(original_bios); modified_bios[0x40b] &= 0xfe
            assert c.string_at(rom, 0x40000) == bytes(modified_bios)
            c.memmove(rom + 0x40b, original_bios[0x40b:0x40c], 1)
            assert c.string_at(rom, 0x40000) == original_bios
            report['cart_authentication_bypass_restored_to_original_BIOS_byte'] = True
            report['restored_ROM_byte'] = {'offset': '0x40b', 'original': original_bios[0x40b]}
        report.update(loaded=True, mounted_sessions=core.CDIntfGetNumSessions(),
                      mounted_tracks=core.CDIntfGetNumTracks(),
                      options_read=options_read,
                      staged_cart_ROM_sha256=hashlib.sha256(c.string_at(rom, 0x40000)).hexdigest())
        rows = []; gpu = c.create_string_buffer(12000)
        if args.hle_entry:
            import biwn_fresh_HLE_entry
            report['fresh_HLE_game_entry']=biwn_fresh_HLE_entry.run(core,ram_pointer,out,args.hle_entry)
            if args.hle_prefix:
                import biwn_fresh_HLE_prefix
                report['fresh_HLE_game_prefix']=biwn_fresh_HLE_prefix.run(core,ram_pointer,out,args.hle_entry)
            ram=c.string_at(ram_pointer,0x200000);assert core.GPUStateSave(gpu)==4416
        CPU_IRQ_owner=None
        if args.source_CPU_IRQ_entry:
            import biwn_CPU_IRQ_owner
            CPU_IRQ_owner=biwn_CPU_IRQ_owner.install(core,out)
        frame_loop_started = time.monotonic()
        for i in range(0 if args.hle_entry else args.frames):
            current_frame = i+1
            if args.own_DSP_window:
                if current_frame==args.own_DSP_window[0]:
                    if args.DSP_owner_kind == 'router':
                        import biwn_DSP_program_router
                        DSP_owner=biwn_DSP_program_router.install(core,out,args.DSP_router_candidate)
                    elif args.DSP_owner_kind == 'music':
                        import biwn_DSP_music_owner
                        DSP_owner=biwn_DSP_music_owner.install(core,out)
                    else:
                        import biwn_DSP_media_owner
                        DSP_owner=biwn_DSP_media_owner.install(core,out)
                elif current_frame==args.own_DSP_window[1] and DSP_owner:
                    DSP_owner_result=DSP_owner[3]();DSP_owner=None
                    if DSP_owner_result['status']=='rejected':raise RuntimeError('DSP source owner rejected: '+str(DSP_owner_result))
            if args.observe_DSP_window:
                core.BIWNSetDSPInstructionObserver.argtypes=[DSP_OBSERVER]
                core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t
                if current_frame==args.observe_DSP_window[0]:core.BIWNSetDSPInstructionObserver(DSP_callback)
                elif current_frame==args.observe_DSP_window[1]:core.BIWNSetDSPInstructionObserver(DSP_OBSERVER())
            if navigation_enabled and current_frame >= 600:
                before = c.string_at(ram_pointer, 0x200000)
                address = 0x49d6c + args.navigate_actor * 206 if args.navigate_actor is not None else None
                x, z = [int.from_bytes(before[a:a+4], 'big', signed=True) for a in [0x49c50, 0x49c56]]
                tx, tz = ([int.from_bytes(before[a:a+4], 'big', signed=True) for a in [address+4, address+10]]
                          if address is not None else waypoints[waypoint_index] if waypoints else args.navigate_point)
                if navigation_start_scene is None:
                    navigation_start_scene=int.from_bytes(before[0x49c64:0x49c66],'big')
                    navigation_start_mode=int.from_bytes(before[0x49c60:0x49c62],'big')
                if waypoints and (tx-x)**2+(tz-z)**2<=255 and waypoint_index<len(waypoints)-1:
                    waypoint_index+=1
                    tx,tz=waypoints[waypoint_index]
                heading = before[0x49cba]
                dx, dz = tx-x, tz-z
                target = round(math.atan2(-dx, dz) * 128 / math.pi) % 256
                error = (target-heading+128) % 256 - 128
                active = int.from_bytes(before[address:address+2], 'big') != 0 if address is not None else True
                # Match the source's squared-distance threshold; reaching it
                # is observation, never a claim that this actor can speak.
                buttons = [] if not active or dx*dx+dz*dz <= 255 else (
                    ['L'] if error > 2 else ['R'] if error < -2 else ['U'])
                if scene_change_frame is not None:
                    offset=current_frame-scene_change_frame
                    buttons=sorted({name for window in scene_change_windows
                        if window['start_offset']<=offset<window['stop_offset']
                        for name in window['buttons']})
                    if args.post_scene_navigate_actor is not None and offset>=args.post_scene_navigation_offset:
                        address=0x49d6c+args.post_scene_navigate_actor*206
                        tx,tz=[int.from_bytes(before[a:a+4],'big',signed=True)for a in [address+4,address+10]]
                        active=int.from_bytes(before[address:address+2],'big')!=0
                        if post_waypoint_index<len(post_waypoints):
                            tx,tz=post_waypoints[post_waypoint_index]
                            if (tx-x)**2+(tz-z)**2<=255:
                                post_waypoint_index+=1
                                if post_waypoint_index<len(post_waypoints):tx,tz=post_waypoints[post_waypoint_index]
                                else:tx,tz=[int.from_bytes(before[a:a+4],'big',signed=True)for a in [address+4,address+10]]
                        dx,dz=tx-x,tz-z
                        target=round(math.atan2(-dx,dz)*128/math.pi)%256
                        error=(target-heading+128)%256-128
                        buttons=[] if not active or dx*dx+dz*dz<=255 else(
                            ['L']if error>2 else ['R']if error< -2 else ['U'])
                navigation_inputs = {button_ids[name] for name in buttons}
                navigation = dict(actor_address=hex(address) if address is not None else None,
                                  active=active, target_X=tx, target_Z=tz,
                                  player_X=x, player_Z=z, heading=heading, desired_heading=target,
                                  heading_error=error, squared_distance=dx*dx+dz*dz,
                                  actor_state_word=int.from_bytes(before[address+108:address+110], 'big') if address is not None else None,
                                  waypoint_index=waypoint_index if waypoints else None,
                                  post_waypoint_index=post_waypoint_index if post_waypoints else None,
                                  buttons=buttons, no_guest_memory_writes=True)
            core.retro_run()
            if CPU_IRQ_owner and core.BIWNCPUIRQRejectedCount():
                CPU_IRQ_owner[4]()
                raise RuntimeError('Source CPU IRQ entry rejected; no original IRQ-entry fallback')
            if DSP_owner and core.BIWNDSPRejectedInstructionCount()>0:
                DSP_owner_result=DSP_owner[3]();DSP_owner=None
                raise RuntimeError('DSP source owner rejected: '+str(DSP_owner_result))
            if DSP_owner and args.require_owned_DSP and core.BIWNDSPOriginalInstructionCount()>0:
                DSP_owner_result=DSP_owner[3]();DSP_owner=None
                raise RuntimeError('Uncovered DSP instruction in owned frame '+str(current_frame)+': '+str(DSP_owner_result))
            if args.observe_DSP_window and args.observe_DSP_window[0]<=current_frame<=args.observe_DSP_window[1]:
                (out/'DSP-observation.json').write_text(json.dumps({**DSP_observation,'frame_window':args.observe_DSP_window,'scope':'Original main DSP dispatch and inline jump/jr delay callbacks only; idle-probe internals not instrumented. Read-only snapshots, no DSP execution ownership.'},indent=2)+'\n')
            ram = c.string_at(ram_pointer, 0x200000)
            assert core.GPUStateSave(gpu) == 4416
            row = dict(frame=i+1, CPU=hex(core.m68k_get_reg(None, 16)),
                       GPU=hex(core.GPUGetPC()), DSP=hex(core.DSPGetPC()),
                       GPU_R31_banks=[hex(int.from_bytes(gpu.raw[o:o+4], 'little')) for o in [4263, 4391]],
                       stage_prefix=ram[0x4000:0x4010].hex(),
                       raw_player_X=int.from_bytes(ram[0x49c50:0x49c54], 'big'),
                       raw_player_Z=int.from_bytes(ram[0x49c56:0x49c5a], 'big'),
                       scene_word=int.from_bytes(ram[0x49c64:0x49c66], 'big'),
                       player_mode_word=int.from_bytes(ram[0x49c60:0x49c62], 'big'),
                       tile_word=int.from_bytes(ram[0x49c8c:0x49c8e], 'big'),
                       equipped_word=int.from_bytes(ram[0x49d5a:0x49d5c], 'big'),
                       movie_flag_words=[int.from_bytes(ram[a:a+2], 'big') for a in [0x47b80, 0x47b82]],
                       cumulative_nonzero_audio_samples=audio['nonzero_samples'],
                       movie_controller_state_word=int.from_bytes(ram[0xbd85c:0xbd85e],'big'),
                       navigation=navigation,
                       stage_sha256=hashlib.sha256(ram[0x4000:0x100000]).hexdigest())
            rows.append(row)
            first_scene_change=(waypoints and navigation_start_scene is not None and
                scene_change_frame is None and (row['scene_word']!=navigation_start_scene or
                                                row['player_mode_word']!=navigation_start_mode))
            if current_frame in args.save_frame_checkpoints or (args.save_scene_change_checkpoint and first_scene_change):
                target=out/('checkpoint-%08d'%current_frame);target.mkdir()
                core.retro_serialize_size.restype=c.c_size_t
                core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
                blob=c.create_string_buffer(core.retro_serialize_size())
                assert core.retro_serialize(blob,len(blob))
                (target/'final-serialized-state.bin').write_bytes(blob.raw)
                (target/'final-RAM.bin').write_bytes(ram)
                (target/'ROM-provider.bin').write_bytes(c.string_at(rom,0x102000))
                save(target/'report.json',dict(mode='reference',directory=str(target),
                    original_fresh_probe_checkpoint=True,original_processors_only=True,
                    source_probe=str(out/'report.json'),source_frame=current_frame,
                    core_sha256=report['core_sha256'],state_sha256=hashlib.sha256(blob.raw).hexdigest(),
                    ROM_provider_sha256=hashlib.sha256((target/'ROM-provider.bin').read_bytes()).hexdigest(),
                    scene=row['scene_word'],player_mode=row['player_mode_word'],whole_game_complete=False))
            if waypoints and navigation_start_scene is not None and scene_change_frame is None:
                if row['scene_word']!=navigation_start_scene or row['player_mode_word']!=navigation_start_mode:
                    scene_change_frame=current_frame
            if i % 60 == 0:
                row['active_actor_snapshot']=[dict(slot=slot,type=int.from_bytes(ram[a:a+2],'big'),
                    X=int.from_bytes(ram[a+4:a+8],'big',signed=True),Z=int.from_bytes(ram[a+10:a+14],'big',signed=True),
                    state=int.from_bytes(ram[a+108:a+110],'big'),region=int.from_bytes(ram[a+42:a+44],'big'))
                    for slot in range(40)for a in [0x49d6c+slot*206]if any(ram[a:a+2])]
                save(out/'status.json', dict(status='running', latest=row)); print(json.dumps(row), flush=True)
            if args.stop_after_scene_change and scene_change_frame is not None and current_frame>=scene_change_frame+args.stop_after_scene_change:
                break
        if DSP_owner:
            DSP_owner_result=DSP_owner[3]();DSP_owner=None
            if DSP_owner_result['status']=='rejected':raise RuntimeError('DSP source owner rejected: '+str(DSP_owner_result))
        if CPU_IRQ_owner:
            report['source_CPU_IRQ_entry']=CPU_IRQ_owner[4]()
        if args.own_DSP_window:
            report['source_DSP_execution']={'window':args.own_DSP_window,'kind':args.DSP_owner_kind,'report':str(out/'DSP-owner-report.json'),'CPU_GPU_devices_remain_original':True}
        assert not errors, errors
        (out/'RAM-final.bin').write_bytes(ram)
        (out/'GPU-final.bin').write_bytes(gpu.raw[:4416])
        core.retro_serialize_size.restype = c.c_size_t
        core.retro_serialize.argtypes = [c.c_void_p, c.c_size_t]; core.retro_serialize.restype = c.c_bool
        state_size = core.retro_serialize_size(); state = c.create_string_buffer(state_size)
        assert core.retro_serialize(state, state_size)
        (out/'state-final.bin').write_bytes(state.raw)
        if video:
            image_path = out/'original-emulator-final-frame.png'
            write_video_PNG(image_path, video['raw'], video['width'],video['height'],video['pitch'])
            (out/'video-final.xrgb8888').write_bytes(video.pop('raw'))
            video['PNG'] = str(image_path)
        report.update(status='terminal_fresh_libretro_CD_probe', frames=rows,
                      frame_loop_wall_seconds=time.monotonic()-frame_loop_started,
                      options_read=options_read, video=video, audio=audio,
                      final_RAM_sha256=hashlib.sha256(ram).hexdigest(),
                      final_serialized_state_sha256=hashlib.sha256(state.raw).hexdigest(),
                      observational_firmware_hook=args.trace_firmware,
                      firmware_boundary_visits={hex(k): v for k,v in visit_counts.items()},
                      firmware_trace=firmware_trace,
                      controller_input_samples=input_sample_count,
                      pressed_input_samples=pressed_input_samples,
                      boot_completion_proven=False)
        report['scene_change_frame']=scene_change_frame
        report['executed_frames']=len(rows)
        report['final_waypoint_index']=waypoint_index if waypoints else None
        if audio_stream:
            audio_stream.flush();raw_path=out/'frontend-PCM.s16le'
            assert raw_path.stat().st_size==audio['frames']*4
            rate=round(av.timing.sample_rate);assert 8000<=rate<=192000
            wav_path=out/('mixed-original-C-frontend-audio.wav'if args.own_DSP_window else'original-frontend-audio.wav')
            with wave.open(str(wav_path),'wb')as w:
                w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
                with raw_path.open('rb')as source:
                    while True:
                        block=source.read(1048576)
                        if not block:break
                        w.writeframesraw(block)
            report['original_frontend_audio_capture']={'raw':str(raw_path),'WAV':str(wav_path),
                'declared_rate':rate,'frames':audio['frames'],'nonzero_samples':audio['nonzero_samples'],
                'scope':('Frontend callbacks with reconstructed DSP only in the declared window; CPU/GPU/devices original. Not physical timing/standalone.'if args.own_DSP_window else'Original-core frontend callbacks; emulator-declared rate, not physical timing or reconstructed-C playback.')}
        report['stage_equal_to_extracted_reference_at_any_frame'] = any(
            row['stage_sha256'] == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453' for row in rows)
        save(out/'report.json', report)
    except BaseException as error:
        save(out/'status.json', dict(status='terminal_failed', error=repr(error)))
        raise
    finally:
        if args.source_CPU_IRQ_entry and initialized and hasattr(core,'BIWNSetCPUIRQOwner'):core.BIWNSetCPUIRQOwner(None)
        if loaded: core.retro_unload_game()
        if initialized: core.retro_deinit()
        if audio_stream:audio_stream.close()
    save(out/'status.json', dict(status='terminal_pass_probe_only', shutdown_completed=True))
    if args.boot == 'hle' and not args.hle_entry and not args.no_publish:
        save(ROOT/'verification/native-reference-preview-latest.json',dict(report=str(out/'report.json'),
            PNG=video.get('PNG'),scope='Original emulator HLE reference; not reconstructed C, native firmware boot or physical playability.'))
    print(json.dumps(dict(status=report['status'], final=rows[-1] if rows else report.get('fresh_HLE_game_prefix',report.get('fresh_HLE_game_entry',{})).get('CPU'), audio=audio)), flush=True)


if __name__ == '__main__':
    main()

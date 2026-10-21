"""OriginalGPU4D80 versus fixed C: full banks/flags/scratch/RAM/ordered bus."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
ROOT=frame.ROOT
read=lambda p:json.loads(p.read_text())
save=frame.save
R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16);W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);TRACE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read16',R16),('read32',R32),('write16',W16),('write32',W32),('observe_PC',TRACE),('context',c.c_void_p)]
class State(c.Structure):_fields_=[('registers',(c.c_uint32*32)*2)]+[(k,c.c_uint32)for k in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','instructions']]+[('local_RAM',c.c_uint8*4096)]
def state_dict(s):return dict(register_banks=[list(s.registers[b])for b in range(2)],pc=hex(s.pc),flags=s.z|(s.c<<1)|(s.n<<2),matrix_control=s.matrix_control,matrix_pointer=s.matrix_pointer,division_control=s.division_control,remainder=s.remainder,instructions=s.instructions,local_RAM_sha256=hashlib.sha256(bytes(s.local_RAM)).hexdigest())
class Runtime:
    def __init__(self,library,rows,integer_divider=False):
        self.division_control=0 if integer_divider else 0xa5a50001;self.device_library=ROOT/('tools/libbiwn-integer-render-device.dylib'if integer_divider else'tools/libbiwn-geometry-probe.dylib')
        self.device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,self.device_library);self.native=self.device.lib;lib=self.native
        lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
        lib.lab_geometry_original.argtypes=[c.c_uint32];lib.lab_geometry_original.restype=c.c_int;lib.lab_geometry_steps.restype=c.c_uint32
        lib.lab_geometry_PC.argtypes=[c.c_uint32];lib.lab_geometry_PC.restype=c.c_uint32;lib.lab_geometry_final_PC.restype=c.c_uint32;lib.lab_geometry_gpu_RAM.restype=c.c_void_p
        lib.lab_geometry_control.argtypes=[c.c_uint];lib.lab_geometry_control.restype=c.c_uint32;lib.lab_movement_register.argtypes=[c.c_uint,c.c_uint];lib.lab_movement_register.restype=c.c_uint32
        lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
        lib.lab_geometry_initial_GPU_RAM.restype=c.c_void_p
        self.initial_GPU_RAM=None
        self.lib=c.CDLL(str(library));self.init=self.lib.biwn_gpu_geometry_init;self.init.argtypes=[c.POINTER(State),c.c_uint32,c.c_void_p];self.init.restype=c.c_int;self.run=self.lib.biwn_gpu_geometry_run;self.run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];self.run.restype=c.c_int
        self.rows={r['address']:r for r in rows}
    def original(self,ram,seed):
        self.device.seed(ram,0);lib=self.native;status=lib.lab_geometry_original(seed);assert status==0,('OriginalGPU did not return',status)
        self.initial_GPU_RAM=c.string_at(lib.lab_geometry_initial_GPU_RAM(),4096)
        pcs=[lib.lab_geometry_PC(i)for i in range(lib.lab_geometry_steps())];events=[]
        for i in range(lib.lab_movement_event_count()):
            event=(c.c_uint32*5)();assert lib.lab_movement_event(i,event)==0
            if event[1]!=3 or event[0]not in [11,12]:continue
            pc=event[2]-2;op=int(self.rows[pc]['bytes'][:4],16)>>10
            width={40:2,41:4,46:2,47:4,54:2}[op]
            events.append(['r'if event[0]==11 else'w',event[3],width,event[4]])
        state=dict(register_banks=[[lib.lab_movement_register(b,i)for i in range(32)]for b in range(2)],pc=hex(lib.lab_geometry_final_PC()),flags=lib.lab_geometry_control(0)&7,matrix_control=lib.lab_geometry_control(4),matrix_pointer=lib.lab_geometry_control(8),division_control=self.division_control,remainder=lib.lab_geometry_control(0x1c))
        gpu=c.string_at(lib.lab_geometry_gpu_RAM(),4096);state['local_RAM_sha256']=hashlib.sha256(gpu).hexdigest()
        return self.device.ram(),gpu,state,dict(PC_samples=pcs,external_events=events,initial_GPU_RAM_sha256=hashlib.sha256(self.initial_GPU_RAM).hexdigest(),device=self.device.stats())
    def translated(self,ram,seed,budget=100000,missing=None,null_bus=False,null_state=False,bad_pc=False,fail=None):
        memory=bytearray(ram);trace=[];pcs=[];errors=[]
        def reader(width):
            def cb(_,a,out):
                if fail==('read',width):return 1
                if not 0<=a<=len(memory)-width:errors.append(['read',hex(a),width]);return 1
                out[0]=int.from_bytes(memory[a:a+width],'big');trace.append(['r',a,width,out[0]]);return 0
            return cb
        def writer(width):
            def cb(_,a,value):
                if fail==('write',width):return 1
                if not 0<=a<=len(memory)-width:errors.append(['write',hex(a),width]);return 1
                memory[a:a+width]=value.to_bytes(width,'big');trace.append(['w',a,width,value]);return 0
            return cb
        callbacks=[R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4)),TRACE(lambda _,pc:pcs.append(pc))]
        if missing is not None:callbacks[missing]=type(callbacks[missing])()
        bus=Bus(*callbacks,None);state=State();initial=c.create_string_buffer(self.initial_GPU_RAM)if self.initial_GPU_RAM is not None else None;assert self.init(c.byref(state),seed,initial)==0;state.division_control=self.division_control
        if bad_pc:state.pc=0
        before=bytes(state);status=self.run(None if null_bus else c.byref(bus),None if null_state else c.byref(state),budget)
        return bytes(memory),state,dict(status=status,CPU_unchanged=bytes(state)==before,PC_samples=pcs,external_events=trace,errors=errors)
    def close(self):self.device.close()

def cases(capture):
    result=[];rng=random.Random(0x4d80434)
    matrices=[[16384,0,0,0,16384,0,0,0,16384],[0,0,16384,0,16384,0,-16384,0,0],[-16384,0,0,0,16384,0,0,0,-16384],[16384,0,0,0,0,-16384,0,16384,0],[0,-16384,0,16384,0,0,0,0,16384]]
    for p in sorted(capture.glob('startup-C-*.bin')):
        result.append(dict(path=str(p),seed=rng.getrandbits(32),matrix=None,translation=None))
        for i in range(31):result.append(dict(path=str(p),seed=rng.getrandbits(32),matrix=matrices[i%len(matrices)],translation=[rng.choice([-4096,-64,-1,0,1,64,4096])for _ in range(3)]))
    return result
def fixture(case):
    p=Path(case['path']);ram=bytearray(p.read_bytes());meta=read(p.parent/f'startup-capture-{p.stem.split("-")[-1]}.json');assert hashlib.sha256(ram).hexdigest()==meta['C_RAM_sha256']
    if case['matrix']is not None:
        for i,value in enumerate(case['matrix']):ram[0x47b88+i*2:0x47b8a+i*2]=(value&65535).to_bytes(2,'big')
        for i,value in enumerate(case['translation']):ram[0x47b9a+i*2:0x47b9c+i*2]=(value&65535).to_bytes(2,'big')
    return bytes(ram)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);parser.add_argument('--integer-divider',action='store_true');opts=parser.parse_args();out=ROOT/('verification/biwn-gpu-integer-geometry'if opts.integer_divider else'verification/biwn-gpu-geometry')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgpu-geometry.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_geometry.c'),'-o',str(library)];compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-geometry-overlay/C-generation.json');runtime=Runtime(library,mapping['instructions_decoded'],integer_divider=opts.integer_divider);vectors=cases(ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z')
    if opts.limit:vectors=[vectors[i]for i in [0,32,64,96,1,2,3,4,5,6,31,127][:opts.limit]]
    rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',dict(status='running',case=i));ram=fixture(case);left,gpu,expected,original=runtime.original(ram,case['seed']);right,actual,rebuilt=runtime.translated(ram,case['seed']);actual_dict=state_dict(actual)
            shape=[e[:3]for e in original['external_events']]==[e[:3]for e in rebuilt['external_events']];writes=[e for e in original['external_events']if e[0]=='w']==[e for e in rebuilt['external_events']if e[0]=='w']
            if rebuilt['status']or left!=right or gpu!=bytes(actual.local_RAM)or any(expected[k]!=actual_dict[k]for k in expected)or original['PC_samples']!=rebuilt['PC_samples']or not shape or not writes:
                save(out/'mismatch.json',dict(case=case,original_state=expected,C_state=actual_dict,original=original,rebuilt=rebuilt,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:40],GPU_RAM_differences=[hex(0xf03000+j)for j,(a,b)in enumerate(zip(gpu,actual.local_RAM))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            coverage.update(original['PC_samples'])
            inputs=out/'GPU-state-inputs';inputs.mkdir(exist_ok=True);(inputs/f'case-{i:03d}-before.bin').write_bytes(runtime.initial_GPU_RAM);(inputs/f'case-{i:03d}-after.bin').write_bytes(bytes(actual.local_RAM))
            for pc in original['PC_samples']:
                if int(runtime.rows[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
            rows.append(dict(case=case,state=actual_dict,initial_GPU_RAM_sha256=original['initial_GPU_RAM_sha256'],initial_GPU_RAM=str(inputs/f'case-{i:03d}-before.bin'),final_GPU_RAM=str(inputs/f'case-{i:03d}-after.bin'),original_steps=len(original['PC_samples']),C_instructions_including_delays=actual.instructions,external_reads=sum(e[0]=='r'for e in rebuilt['external_events']),external_writes=sum(e[0]=='w'for e in rebuilt['external_events']),RAM_sha256=hashlib.sha256(right).hexdigest(),full_GPU_banks_flags_scratch_RAM_PC_order_and_bus_match=True))
        save(out/'fixtures.json',rows)
        if opts.limit:save(out/'status.json',dict(status='terminal_preflight',cases=len(rows)));print(json.dumps(dict(directory=str(out),cases=len(rows),coverage=[len(coverage),434])));return
        missing=[r for r in mapping['instructions_decoded']if r['address']not in coverage];save(out/'coverage.json',dict(instructions=mapping['instructions_decoded'],uncovered=missing));assert not missing
        guards=[];case=vectors[0];ram=fixture(case)
        for kw in [{'missing':i}for i in range(4)]+[{'null_bus':True},{'null_state':True},{'budget':0}]:
            _,_,r=runtime.translated(ram,case['seed'],**kw);assert r['status']==1 and r['CPU_unchanged']and not r['external_events'];guards.append(kw)
        for kw,status in [({'bad_pc':True},3),({'budget':1},4)]:
            _,_,r=runtime.translated(ram,case['seed'],**kw);assert r['status']==status and r['CPU_unchanged'];guards.append(kw)
        for fail in [('read',2),('read',4),('write',2),('write',4)]:
            _,_,r=runtime.translated(ram,case['seed'],fail=fail);assert r['status']==2 and r['CPU_unchanged'];guards.append(dict(failure=fail))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='GPU4D80_fixed_C_full_banks_flags_scratch_RAM_PC_bus_match_original',directory=str(out),GPU_cases=len(rows),source_instruction_coverage=[434,434],host_guards=len(guards),new_components=1,source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],payload_sha256=mapping['payload_sha256'],original_GPU_core_calls_on_C_side=0,matched=['Full64registers,Z/C/N,matrixcontrol/pointer,dividerremainder,all4KBGPUlocalRAM,whole2MBmainRAM and exact directPCsequence. Externalbus readwidth/address/order and actualstorevalues match originalGPU; trace readvalues placeholders not treated as measuredinputs.', 'Capturedsceneinputs plus valid axisrotation matrices/translation variants,packedMMULT,nonrestoring16.16division,clipping,allmandatorydelay behavior. Source-specificfixedCblocks,no runtimeopcode decode/coreexecution.'],limits=['DirectGPUoverlayentry with suppliedseed,bank0/mailboxes/dividermode and captured assistedstartupRAM. Shared originalGPU oracle, no second GPU emulator/physicalhardware/timing/interrupt proof. Sourcefinitebuffers required; hosterror behavior added.', 'Standalone originalGPUversusCgeometry output only, not liveCPUrenderer linkage,polygon/raster helpers,displaylist/OPscanout/fullviewport/audio/game.'],compiler=command,probe_bridge_sha256=hashlib.sha256((ROOT/'scripts/biwn_geometry_probe_bridge.c').read_bytes()).hexdigest(),probe_library_sha256=hashlib.sha256(runtime.device_library.read_bytes()).hexdigest())
        report.update(GPU_division_control=runtime.division_control,new_components=0 if opts.integer_divider else 1,source_C_shader_changed=False)
        if opts.integer_divider:
            report['matched']=[text.replace('nonrestoring16.16division','nonrestoring integer division (control0)') for text in report['matched']]
            report['probe_bridge_sha256']=hashlib.sha256((ROOT/'scripts/biwn_integer_render_device_bridge.c').read_bytes()).hexdigest()
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/('biwn-gpu-integer-geometry-checks.json'if opts.integer_divider else'biwn-gpu-geometry-checks.json'),report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()

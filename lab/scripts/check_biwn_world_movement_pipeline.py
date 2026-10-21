"""CPU caller with actual E220/GPU4320 and inventory code vs linked native C.

Seven remaining helper boundaries are scripted on both paths. The pinned
blitter and synchronous GPU dispatcher completion model are shared.
"""
import argparse,ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_world_update as world
import check_biwn_inventory_frame as frame
ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;REGS=world.REGS
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

class Device(frame.Device):
    def __init__(self,library=None,core=None):
        super().__init__(core or ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,library or ROOT/'tools/libbiwn-movement-device.dylib')
        self.lib.lab_movement_setup.restype=c.c_int;assert self.lib.lab_movement_setup()==0
        self.lib.lab_movement_write32.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];self.lib.lab_movement_write32.restype=c.c_int
        self.lib.lab_device_write16.argtypes=[c.c_void_p,c.c_uint32,c.c_uint16];self.lib.lab_device_write16.restype=c.c_int
        self.lib.lab_movement_submit_C.argtypes=[c.c_uint32]*5;self.lib.lab_movement_submit_C.restype=c.c_int
        def observe(kind,width,address,value):
            if kind<2:self.trace.append(['r'if kind==0 else'w',address,width,value])
        self.observer=frame.OBSERVER(observe);self.lib.lab_device_observe(self.observer)
    def write(self,address,value):assert self.lib.lab_movement_write32(None,address,value)==0,hex(address)
    def write16(self,address,value):assert self.lib.lab_device_write16(None,address,value)==0,hex(address)
    def scripted_call(self,script,target,args):
        script.changed=[];result=script.call(target,args)
        for address,width,value in script.changed:self.direct(address,width,value)
        return result
    def scripted_read(self,script,address,width):
        if address==0x49c60 and 'mode_reads'in script.case:
            value=script.read(address,width);self.direct(address,width,value)
        return self.read(address,width)

def original(device,ram,script,incoming,boundary_helpers=False,boundary_capture=None,geometry_helpers=False,geometry_capture=None,cleanup_helpers=False):
    device.seed(ram,0)
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(ram));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    helpers=[0xe4c0,0x191f4,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]
    if boundary_helpers:
        import check_biwn_boundary_handlers as boundary
        helpers=[a for a in helpers if a not in [0x19f2c,0x19fda]]+boundary.HELPERS
    geometry_entries=[0x1028e,0x102c4,0x1039c,0x10430,0x10652]
    if geometry_helpers:helpers=[a for a in helpers if a not in geometry_entries]
    cleanup_entries=[];cleanup_ranges={};cleanup_calls={}
    if cleanup_helpers:
        import check_biwn_transition_cleanup as cleanup
        cleanup_ranges=cleanup.RANGES;cleanup_entries=[0x20e8c,0x20f0c]
        helpers=[a for a in helpers if a not in cleanup_entries]
    for target in helpers:cpu.mem_write(target,b'\x4e\x75')
    in_formatter=False;steps=[]
    def code(engine,address,size,_):
        nonlocal in_formatter
        stack=engine.reg_read(UC_M68K_REG_A7)
        def word(offset,width):return int.from_bytes(engine.mem_read(stack+offset,width),'big')
        if address in helpers:
            if address==0xf0fa:args=[engine.reg_read(UC_M68K_REG_D2)&0xffff,engine.reg_read(UC_M68K_REG_D3)&0xffff]
            elif address==0x19f2c:args=[word(4+i*2,2)for i in range(3)]
            elif address==0x19fda:args=[word(4,4),word(8,2)]
            elif address in [0x1039c,0x10652]:args=[word(4,4),word(8,2)]
            elif address==0x10430:args=[word(4,4),word(8,2),word(10,2)]
            elif address in [0xeb04,0x102c4,0x1028e]:args=[word(4,4)]
            elif address in [0x1aa40,0x20f78]:args=[word(4,2)]
            else:args=[]
            if boundary_capture is not None and address in [0x19f2c,0x19fda]:
                boundary_capture.update(target=address,args=args,RAM=device.ram())
            if geometry_capture is not None and address in geometry_entries:
                geometry_capture.update(target=address,args=args,RAM=device.ram(),incoming_d0=engine.reg_read(UC_M68K_REG_D0),incoming_d1=engine.reg_read(UC_M68K_REG_D1),incoming_d3=engine.reg_read(UC_M68K_REG_D3))
            device.trace.append(['call',address,args]);result=device.scripted_call(script,address,args)
            for a,w,v in script.changed:engine.mem_write(a,v.to_bytes(w,'big'))
            engine.reg_write(UC_M68K_REG_D0,result);return
        if address in cleanup_ranges:cleanup_calls[hex(address)]=cleanup_calls.get(hex(address),0)+1
        if address in [0xe220,0x1b786,0x19f2c,0x19fda]+geometry_entries+cleanup_entries:
            if address==0xe220:args=[word(4+i*4,4)for i in range(5)]
            elif address==0x19f2c:args=[word(4+i*2,2)for i in range(3)]
            elif address==0x19fda:args=[word(4,4),word(8,2)]
            elif address in [0x1039c,0x10652]:args=[word(4,4),word(8,2)]
            elif address==0x10430:args=[word(4,4),word(8,2),word(10,2)]
            elif address in [0x1028e,0x102c4]:args=[word(4,4)]
            else:args=[]
            device.trace.append(['call',address,args])
        if address==0x1b45a:in_formatter=True
        if address==0x1b838:in_formatter=False
        assert (0x1a188<=address<0x1a544 or (boundary_helpers and 0x19f2c<=address<0x1a0f8) or (geometry_helpers and(0x1028e<=address<0x10520 or 0x10652<=address<0x106c4)) or any(a<=address<b for a,b in cleanup_ranges.items()) or 0x1b718<=address<0x1b780 or 0xe220<=address<0xe26c or 0x1b786<=address<0x1bc78 or 0x14776<=address<0x14caa or 0xe098<=address<0xe0a6 or 0xe2b8<=address<0xe2f4 or 0xe540<=address<0xe588 or (in_formatter and(0x1b160<=address<0x1b478 or 0xe61c<=address<0xe68c))),hex(address)
        steps.append(address)
    def read(engine,access,address,width,value,_):
        if in_formatter or SP-0x1000<=address<SP+8 or 0x14800<=address<0x14842:return
        engine.mem_write(address,device.scripted_read(script,address,width).to_bytes(width,'big'))
    def write(engine,access,address,width,value,_):
        if SP-0x1000<=address<SP+8:return
        value&=(1<<(width*8))-1
        if in_formatter:
            assert width==1 and 0x15b7a0<=address<0x15b7aa;device.direct(address,width,value);return
        if width==2:device.write16(address,value)
        else:assert width==4;device.write(address,value)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x1a188,STOP,count=250000,timeout=3_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
    return device.ram(),list(device.trace),device.registers(),{'CPU_instructions':len(steps),'device':device.stats(),'cleanup_function_entries':cleanup_calls}

def translated(fn,device,ram,script,boundary_functions=None,geometry_functions=None,cleanup_functions=None,task_runtime=None,input_function=None,input_backend=None,dispatch_functions=None,camera_functions=None,animation_functions=None,animation_backend=None,targeting_function=None):
    device.seed(ram,1);errors=[]
    def reader(width):
        def callback(_,a,v):
            try:
                if input_backend is not None and a==0xf14000:
                    assert width==4;v[0]=input_backend.read_for_C();device.trace.append(['r',a,width,v[0]])
                elif task_runtime is not None and task_runtime.private(a,width):v[0]=task_runtime.read_private(a,width)
                else:v[0]=device.scripted_read(script,a,width)
                return 0
            except Exception as error:errors.append(repr(error));return 1
        return callback
    def writer(width):
        def callback(_,a,v):
            try:
                if input_backend is not None and a==0xf14000:
                    assert width==2;device.trace.append(['w',a,width,v]);input_backend.write_for_C(v)
                elif task_runtime is not None and task_runtime.private(a,width):device.direct(a,width,v)
                elif width==1:
                    assert dispatch_functions is not None and(a==0x49cba or(camera_functions is not None and a==0x49b9f));device.direct(a,width,v);device.trace.append(['w',a,width,v])
                else:device.write16(a,v)if width==2 else device.write(a,v)
                return 0
            except Exception as error:errors.append(repr(error));return 1
        return callback
    def call(_,target,args,count,result):
        try:
            values=list(args[:count]);device.trace.append(['call',target,values])
            if task_runtime is not None:task_runtime.dispatch_call(target)
            if target==0x20820 and targeting_function is not None:
                assert not values;status=targeting_function(c.byref(bus),result[0],result);assert status==0,('targeting_update',status)
            elif target==0xeb04 and animation_functions is not None:
                assert len(values)==1 and animation_backend is not None;animation_backend.begin_update()
                status=animation_functions[target](c.byref(bus),*values,result[0],512,result);assert status==0,('animation_update',status)
            elif target==0xeac4 and animation_functions is not None:
                assert len(values)==4;status=animation_functions[target](c.byref(bus),*values,result[0],result);assert status==0,('animation_queue',status)
            elif target==0xf0fa and camera_functions is not None:
                assert len(values)==2;status=camera_functions[target](c.byref(bus),write8,*values,result);assert status==0,('camera',status)
            elif target==0xe540 and camera_functions is not None:
                assert len(values)==2;result[0]=camera_functions[target](*values)
            elif target==0x13440 and camera_functions is not None:
                assert len(values)==2;status=camera_functions[target](c.byref(bus),*values,result[0],result);assert status==0,('camera_direction',status)
            elif target==0x191f4 and dispatch_functions is not None:
                assert task_runtime is not None and not values;task_runtime.dispatch_enter()
                try:status=dispatch_functions['dispatch'](c.byref(bus),write8,256,result[0],result);assert status==0,('input_dispatch',status)
                finally:task_runtime.dispatch_leave()
            elif target==0xe588 and dispatch_functions is not None:
                assert len(values)==2;remainder=c.c_uint32();status=dispatch_functions['division'](*values,result,c.byref(remainder));assert status==0,('signed_division',status)
            elif target==0x1545c and dispatch_functions is not None:
                assert len(values)==1;status=cleanup_functions[target](c.byref(bus),*values,result[0],100000,result);assert status==0,('input_free',status)
            elif target==0xe4c0 and input_function is not None:
                assert input_backend is not None and not values;input_backend.begin_poll();status=input_function(c.byref(bus));assert status==0,('input_poll',status)
            elif target==0xe220:assert len(values)==5;status=device.lib.lab_movement_submit_C(*values);assert status==0;result[0]=0
            elif target==0x1b786:assert count==0;status=device.lib.lab_device_run_C(100000);assert status==0;result[0]=0
            elif task_runtime is not None and target==0xdf60:
                assert not values;result[0]=task_runtime.inner_yield(result[0])
            elif boundary_functions is not None and target==0x19f2c:
                if task_runtime is not None:task_runtime.boundary_enter(target)
                try:status=boundary_functions[target](c.byref(bus),*values,0,result);assert status==0,(hex(target),status)
                finally:
                    if task_runtime is not None:task_runtime.boundary_leave()
            elif boundary_functions is not None and target==0x19fda:
                if task_runtime is not None:task_runtime.boundary_enter(target)
                try:status=boundary_functions[target](c.byref(bus),*values,0,0,64,result);assert status==0,(hex(target),status)
                finally:
                    if task_runtime is not None:task_runtime.boundary_leave()
            elif geometry_functions is not None and target in geometry_functions:
                if target in [0x1028e,0x10652]:status=geometry_functions[target](c.byref(bus),*values,result[0],result)
                elif target==0x102c4:status=geometry_functions[target](c.byref(bus),*values,64,result)
                elif target==0x10430:status=geometry_functions[target](c.byref(bus),*values,values[1],1,result)
                else:status=geometry_functions[target](c.byref(bus),*values,result)
                assert status==0
            elif cleanup_functions is not None and target in [0x20e8c,0x20f0c]:
                assert not values;status=cleanup_functions[target](c.byref(bus),result[0],100000,result);assert status==0
            else:result[0]=device.scripted_call(script,target,values)
            return 0
        except Exception as error:errors.append({'target':hex(target),'args':list(args[:count]),'error':repr(error)});return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
    bus=world.Bus(*callbacks,None,16)
    if dispatch_functions is not None:write8=dispatch_functions['write8_type'](writer(1))
    if task_runtime is not None:
        try:task_runtime.run(bus,fn);status=0
        except Exception as error:raise AssertionError((repr(error),errors))from error
    else:status=fn(c.byref(bus))
    assert status==0 and not errors,(status,errors)
    stats=device.stats();assert not stats['GPUExec1_calls']and not stats['original_GPU_sprite_decodes']and not stats['game_frames_executed']and not stats['device_error']
    return device.ram(),list(device.trace),device.registers(),stats

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);options=parser.parse_args()
    previous=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());lib=c.CDLL(str(Path(previous['directory'])/'libbiwn-world-update.dylib'));fn=lib.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=ROOT/'verification/biwn-world-movement-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    rng=random.Random(0xe220);rows=[];device=Device()
    try:
        for i,case in enumerate(world.cases()[:options.limit]):
            save(out/'status.json',{'status':'running','case':i});a=world.Script(snapshot,case);b=world.Script(snapshot,case);ram=bytes(a.memory)
            oa,ta,ra,meta=original(device,ram,a,[rng.getrandbits(32)for _ in REGS]);ob,tb,rb,stats=translated(fn,device,ram,b)
            equal=oa[:0x15b7a0]==ob[:0x15b7a0]and oa[0x15b7aa:]==ob[0x15b7aa:]
            if not equal or ta!=tb or ra!=rb:
                save(out/'mismatch.json',{'case':i,'parameters':case,'RAM_match':equal,'original_trace':ta,'C_trace':tb,'original_blitter_registers':ra,'C_blitter_registers':rb,'RAM_differences':[[j,oa[j],ob[j]]for j in range(len(oa))if oa[j]!=ob[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
            row={'case':i,'parameters':case,'original':meta,'rebuilt':stats,'CPU_external_trace_and_helper_calls_match':True,'whole_RAM_except_formatter_scratch_match':True,'final_blitter_registers_match':True,'primary_position_bytes':ob[0x49c50:0x49c60].hex(),'movement_matrix32':ob[0x49ccc:0x49cec].hex(),'inventory_frame_sha256':hashlib.sha256(ob[frame.FRAME_START:frame.FRAME_END]).hexdigest(),'redraw_calls':sum(t[:2]==['call',0x1b786]for t in tb)}
            rows.append(row)
            if i<4:save(out/('trace-'+str(i)+'.json'),tb)
    finally:device.close()
    save(out/'fixtures.json',rows)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'connected_CPU_world_movement_and_inventory_match_original_execution','directory':str(out),'cases':len(rows),'redraw_cases':sum(x['redraw_calls']for x in rows),'additional_original_components':0,'CPU_movement_helper_linked':True,'GPU_movement_algorithm_linked':True,'inventory_pipeline_linked':True,'rebuilt_original_GPU_instructions':0,'rebuilt_original_CPU_instructions':0,'game_frames_executed':0,'bridge_sha256':frame.draw.binary_tools.sha(ROOT/'tools/libbiwn-movement-device.dylib'),
            'matched':['Original completeCPU caller executes real E220mailbox/digit/inventory/text/sprite routines and originalGPU4320/4B00overlays; rebuilt path uses compiledC for these components.','Every externalCPU bus read/write value,width,address/order and declared helper-call args/order; full2MBRAM except10formatter scratchbytes; finalblitterregisters and inventorypanel pixels.','ActualGPU movement generation is connected; existing C caller then applies it to position/fraction words under boundary decisions.'],
            'remaining_scripted_helper_targets':['0xe4c0','0x191f4','0x19f2c','0x19fda','0xf0fa','0xeb04','0x20820'],
            'limits':['Seven polling/input/collision/terrain/scene/entity helper boundaries remain scripted identically. Prior fixtures movement_effects are deliberately unused here; originalGPU or C generates deltas.','Pinned softwareemulator blitter and synchronous GPU dispatcher completion model; not physicalhardware, concurrent timing or unmodifiedBIOS proof.','PrivateCPU stack/formatter10scratchbytes, caller-saved registers/CCR and arbitrary asynchronous scheduling excluded.','Finite assisted-game snapshot fixtures, not a whole rebuilt world viewport/main loop/game or audio.']}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
    if options.limit==256:save(ROOT/'verification/biwn-world-movement-pipeline-checks.json',report)
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()

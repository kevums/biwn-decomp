"""Linked readable scene setup vs original CPU with actual disc transfers.

The fixed stream phases are observed replay conditions. Task scheduling,
firmware I/O and asynchronous completion remain explicit external adapters.
"""
import ctypes as c
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
from collections import deque
import check_biwn_resources_native as native
import check_biwn_scene_loading as scene
import check_biwn_actor_creation as actor

ROOT=native.ROOT
SP=native.SP
STOP=native.STOP
world=native.world
save=native.save
sha=lambda value:hashlib.sha256(value).hexdigest()
EXTERNAL={0x303c:[],0x3042:[],0xdf60:[]}
RANGES={**native.resources.RANGES,**native.memory.RANGES,**scene.RANGES,**actor.RANGES,
        0x1ac3c:0x1ae88,0x1545c:0x1557a,0xd1e0:0xd2a0,0xd2f0:0xd30a,0xe588:0xe61c,
        0x1a0f8:0x1a188,0x20f0c:0x20f78,0x20e40:0x20e8c,0xde5c:0xdeb6,0xdf6c:0xdf7a,
        0xe098:0xe0a6,0xe2b8:0xe2f4,0x102c4:0x1039c}
ENTRIES=set(RANGES)|{0x1ac68,0x1ae56,0xd206,0xd306,0xe60a}
SOURCES=['biwn_scene_stream.c','biwn_scene_loading.c','biwn_texture_cache.c','biwn_actor_creation.c',
         'biwn_resources.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_cd_math.c',
         'biwn_cd_wrappers.c','biwn_signed_division.c','biwn_elevator_scene.c','biwn_elevator_input.c','biwn_task_create.c','biwn_gpu_commands.c','biwn_geometry.c']
class AlignmentFault(c.Structure):
    _fields_=[('logical_address',c.c_uint32),('physical_address',c.c_uint32),('width',c.c_uint32),('is_write',c.c_uint32)]


def check_task_records(left,right,reference):
    """Check public task records even if near an excluded private stack."""
    rows=[]
    for task in reference['created_tasks']:
        address=task['address'];record=left[address:address+38]
        assert len(record)==38 and record==right[address:address+38]
        assert native.get(left,address+8)==native.get(left,address+16)==task['callback']
        assert native.get(left,address+30)==task['parameter']
        neighbors=[native.get(left,address),native.get(left,address+4)]
        for neighbor in neighbors:assert left[neighbor:neighbor+8]==right[neighbor:neighbor+8]
        rows.append(dict(**task,record_sha256=sha(record),neighbor_links_checked=[hex(n)for n in neighbors]))
    return rows


class Runtime(native.Runtime):
    def __init__(self,library):
        super().__init__(library)
        self.stream=self.lib.biwn_scene_stream
        self.stream.argtypes=[c.POINTER(world.Bus),type(self.device.write8),c.c_uint16,*[c.c_uint32]*4,c.POINTER(c.c_uint32)]
        self.stream.restype=c.c_int
        self.stream_fault=self.lib.biwn_scene_stream_with_fault
        self.stream_fault.argtypes=self.stream.argtypes+[c.POINTER(AlignmentFault)];self.stream_fault.restype=c.c_int
        self.elevator=self.lib.biwn_elevator_scene
        self.elevator.argtypes=[c.POINTER(world.Bus),type(self.device.write8),*[c.c_uint32]*4,c.POINTER(c.c_uint32)]
        self.elevator.restype=c.c_int
        self.textures=self.lib.biwn_scene_stream_textures
        self.textures.argtypes=[c.POINTER(world.Bus),type(self.device.write8),c.c_uint16,*[c.c_uint32]*3,c.POINTER(c.c_uint32)]
        self.textures.restype=c.c_int
        self.gpu_mode=1
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32

    def seed(self,ram):
        self.device.seed(ram,self.gpu_mode)
        # GPUReset randomizes argument RAM. Give both isolated oracle lanes
        # the same otherwise-unused argument mailboxes before any command.
        for address in[0xf0320c,0xf03210,0xf03214]:self.device.write(address,4,0)
        for address in range(0xf02200,0xf022a0,4):
            if address!=0xf02238:self.device.write(address,4,0)

    def before_step(self,pc,case):pass
    def after_step(self,pc,case):
        if self.core.GPUReadLong(0xf03204,0)==0x4b00:self.device.write(0xf03204,4,0x4b00)

    def native(self,ram,case):
        self.failure=None
        if hasattr(self,'failure_RAM'):del self.failure_RAM
        self.gpu_mode=0;self.seed(ram);self.disc.reset()
        for target in EXTERNAL:self.device.direct(target,2,0x4e75)
        self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
        for i,value in enumerate(case['incoming']):self.core.m68k_set_reg(i,value)
        self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,case.get('entry',0x20f78))
        self.device.direct(SP,4,STOP);self.device.direct(SP+4,2,case['mode'])
        calls=[];entries={};coverage=set();loads=[];tasks=[];sprites=[];recent=deque(maxlen=32);observer_args=None
        def value(address,width=4):
            physical=address&0xffffff
            if physical>0x200000-width:
                self.failure=dict(kind='host_observer_bounds',PC=hex(pc),logical_address=hex(address),physical_address=hex(physical),width=width,args=observer_args,entries=entries)
                self.failure_RAM=self.device.ram()
                raise RuntimeError('Observer address outside main RAM: '+json.dumps(self.failure))
            return int.from_bytes(c.string_at(self.device.pointer+physical,width),'big')
        for step in range(500000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:break
            if pc in ENTRIES:entries[hex(pc)]=entries.get(hex(pc),0)+1
            if pc==0x1b044:
                stack=self.core.m68k_get_reg(None,15)
                args=[value(stack+4+i*4)for i in range(5)]
                loads.append(dict(args=args,destination=value(args[2])if args[2]else None))
            if pc==0xdf6c:
                stack=self.core.m68k_get_reg(None,15)
                tasks.append(dict(address=value(0xc0924),callback=value(stack+4),parameter=value(stack+8)))
            if pc==0xe2b8:
                stack=self.core.m68k_get_reg(None,15)
                base,index,destination=[value(stack+4+i*4)for i in range(3)]
                observer_args=dict(base=hex(base),index=index,destination=hex(destination))
                frame=(base+value(base+12+index*4))&0xffffffff;width=value(frame,1);height=value(frame+1,1)
                sprites.append(dict(base=base,index=index,destination=destination,frame=frame,width=width,height=height))
            if not(pc in EXTERNAL or any(lo<=pc<hi for lo,hi in RANGES.items())):
                self.failure=dict(PC=hex(pc),recent_PCs=[hex(p)for p in recent],registers=[self.core.m68k_get_reg(None,i)for i in range(18)],entries=entries,calls=calls,sprites=sprites,created_tasks=tasks,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,hardware=self.hardware(),device=self.device.stats(),free_head=hex(int.from_bytes(c.string_at(self.device.pointer+0x112d60,4),'big')))
                for target in EXTERNAL:self.device.direct(target,2,native.get(ram,target,2))
                self.failure_RAM=self.device.ram()
                raise AssertionError('Unexpected native PC '+hex(pc))
            recent.append(pc)
            coverage.add(pc)
            if pc in EXTERNAL:
                stack=self.core.m68k_get_reg(None,15);values=[];offset=4
                for width in EXTERNAL[pc]:values.append(int.from_bytes(c.string_at(self.device.pointer+stack+offset,width),'big'));offset+=width
                if pc==0x303c:
                    values=[self.core.m68k_get_reg(None,i)for i in [8,9,0]];self.disc.start(*values)
                elif pc==0x3042:self.disc.stop()
                elif pc==0xdf60:self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v))
                else:self.core.m68k_set_reg(0,case['external_D0'])
                calls.append([hex(pc),values])
            self.before_step(pc,case)
            self.core.m68k_execute(1)
            self.after_step(pc,case)
        else:
            self.failure=dict(PC=hex(self.core.m68k_get_reg(None,16)),entries=entries,calls=calls[-12:])
            raise AssertionError('Scene setup did not return in500000instructions')
        assert self.core.m68k_get_reg(None,15)==SP+4
        for i,value in enumerate(case['incoming']):
            if i not in[0,1,8,9]:assert self.core.m68k_get_reg(None,i)==value,(i,hex(value),hex(self.core.m68k_get_reg(None,i)))
        for target in EXTERNAL:self.device.direct(target,2,native.get(ram,target,2))
        return self.device.ram(),self.core.m68k_get_reg(None,0),dict(calls=calls,instructions=step,entries=entries,resource_loads=loads,created_tasks=tasks,decoded_sprites=sprites,observed_instruction_addresses=len(coverage),disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,hardware=self.hardware(),device=self.device.stats())

    def translated(self,ram,case,**overrides):
        self.gpu_mode=1;self.seed(ram);self.disc.reset();calls=[];errors=[];bus_errors=[]
        def call(_,target,args,n,out):
            try:
                assert target in EXTERNAL,hex(target)
                values=list(args[:n])if n else[]
                if target==0x303c:assert n==3;self.disc.start(*values)
                elif target==0x3042:assert not n;self.disc.stop()
                elif target==0xdf60:assert not n;self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v))
                else:assert len(values)==len(EXTERNAL[target]);out[0]=case['external_D0']
                calls.append([hex(target),values]);return 0
            except Exception as error:errors.append(repr(error));return 1
        callback=world.CALL(call)
        def checked(fn,kind,width):
            def invoke(_,address,value):
                status=fn(_,address,value)
                if status:bus_errors.append(dict(kind=kind,address=hex(address),width=width,status=status))
                return status
            return invoke
        accessors=[world.R8(checked(self.device.r8,'read',1)),world.R16(checked(self.device.r16,'read',2)),world.R32(checked(self.device.r32,'read',4)),world.W16(checked(self.device.w16,'write',2)),world.W32(checked(self.device.w32,'write',4))]
        bus=world.Bus(*accessors,callback,None,32768)
        output=c.c_uint32(0xa55aa55a)
        args=dict(mode=case['mode'],scratch=SP-512,word_scan=case['word_scan'],budget=32768,incoming_D0=case['incoming'][0]);args.update(overrides)
        if case.get('entry')==0x1aa40:
            args.pop('incoming_D0');status=self.textures(c.byref(bus),self.device.write8,*args.values(),c.byref(output))
        elif case.get('entry')==0x1a0f8:
            args.pop('mode');status=self.elevator(c.byref(bus),self.device.write8,*args.values(),c.byref(output))
        else:
            fault=AlignmentFault();status=self.stream_fault(c.byref(bus),self.device.write8,*args.values(),c.byref(output),c.byref(fault))
        return self.device.ram(),output.value,dict(status=status,errors=errors,bus_errors=bus_errors,calls=calls,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,hardware=self.hardware(),device=self.device.stats(),alignment_fault={name:getattr(fault,name)for name,_ in AlignmentFault._fields_}if case.get('entry')not in[0x1aa40,0x1a0f8]else None)


def main():
    out=ROOT/'verification/scene-stream'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libscene-stream.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(restore/name)for name in SOURCES],'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=Runtime(library)
    snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes()
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(patch['address'],16);before=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(before)]==before
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text())
    captured=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000]
    assert sha(captured)==diagnosis['buffer_sha256']
    historical=runtime.disc.stream_phase
    witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],captured)
    elevator=runtime.disc.stream_phase
    rng=random.Random(0x20f781b044);rows=[];transitions=[]
    try:
        for phase,word_scan in [(historical,0),(historical,1),(elevator,1)]:
            runtime.disc.stream_phase=phase
            for index,cold in [(index,cold)for index in [314,315]for cold in [False,True]]:
                ram=bytearray(snapshot)
                ram[0x47b80:0x47b84]=bytes(4);ram[0x49c64:0x49c66]=index.to_bytes(2,'big')
                # Scene setup starts after cleanup. These empty pending lists
                # are fixture state, not completion or parsed payload results.
                for a in [0x15ece0,0x15ed46,0x15edac]:ram[a:a+2]=bytes(2)
                if cold:
                    for i in range(36):ram[0x15b4a0+i*4:0x15b4a4+i*4]=b'\xff\xff\0\0'
                if word_scan:ram[address:address+len(before)]=replacement
                case=dict(mode=2,index=index,cold_texture_cache=cold,word_scan=word_scan,stream_phase=phase,incoming=[rng.getrandbits(32)for _ in world.REGS],external_D0=0xc001d00d)
                save(out/'status.json',dict(status='running',case=case))
                left,expected,reference=runtime.native(bytes(ram),case)
                right,value,rebuilt=runtime.translated(bytes(ram),case)
                same=native.masked(left)==native.masked(right)and expected==value and rebuilt['status']==0 and not rebuilt['errors']and all(reference[k]==rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware'])
                if not same:
                    save(out/'mismatch.json',dict(case=case,original_D0=expected,C_D0=value,original=reference,C=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(native.masked(left),native.masked(right)))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
                assert native.get(right,0x47b80,2)==0 and native.get(right,0x49c60,2)==2
                assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
                payloads=[]
                assert len(reference['resource_loads'])==len(rebuilt['disc_requests'])
                for load,request in zip(reference['resource_loads'],rebuilt['disc_requests']):
                    if load['destination']is None:continue
                    _,tag,_,size,_=load['args'];pos=request['normalized_track_offset']
                    stream=runtime.disc.data[pos:pos+request['bytes']];marker=tag.to_bytes(4,'big')*16;found=stream.find(marker)
                    assert found>=0 and stream.find(marker,found+1)==-1
                    payload=stream[found+64:found+64+size];dest=load['destination']
                    assert len(payload)==size and right[dest:dest+size]==payload
                    payloads.append(dict(tag=hex(tag),destination=hex(dest),bytes=size,sha256=sha(payload)))
                assert len(payloads)==(2 if cold else 0)
                base=native.get(right,0x49c18);region=right[base:base+4704]
                rows.append(dict(case=case,full_D0=value,original=reference,rebuilt=rebuilt,created_task_records_checked=check_task_records(left,right,reference),copied_texture_payloads_checked=payloads,relocated_region_sha256=sha(region),region_base=hex(base),surfaces=native.get(right,base,2),mode=native.get(right,0x49c60,2)))
                save(out/'cases.json',rows)
        for phase,word_scan in [(historical,0),(historical,1),(elevator,1)]:
            runtime.disc.stream_phase=phase
            for cold in [False,True]:
                ram=bytearray(snapshot);ram[0x47b80:0x47b84]=bytes(4)
                if cold:
                    for i in range(36):ram[0x15b4a0+i*4:0x15b4a4+i*4]=b'\xff\xff\0\0'
                if word_scan:ram[address:address+len(before)]=replacement
                for action,held,expected_index,expected_floor in [('up',0x10,315,3),('down',0x20,314,2)]:
                    ram[0x49ba5]=held
                    case=dict(entry=0x1a0f8,mode=2,action=action,cold_texture_cache=cold,word_scan=word_scan,stream_phase=phase,incoming=[rng.getrandbits(32)for _ in world.REGS],external_D0=0xc001d00d)
                    save(out/'status.json',dict(status='running_elevator',case=case))
                    left,expected,reference=runtime.native(bytes(ram),case)
                    right,value,rebuilt=runtime.translated(bytes(ram),case)
                    same=native.masked(left)==native.masked(right)and expected==value and rebuilt['status']==0 and not rebuilt['errors']and all(reference[k]==rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware'])
                    if not same:
                        save(out/'elevator-mismatch.json',dict(case=case,original_D0=expected,C_D0=value,original=reference,C=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(native.masked(left),native.masked(right)))if a!=b][:40]));raise AssertionError(str(out/'elevator-mismatch.json'))
                    assert native.get(right,0x49c64,2)==expected_index and native.get(right,0x49c62,2)==expected_floor and native.get(right,0x49c60,2)==2 and native.get(right,0x47b80,2)==0
                    assert reference['entries']['0x20f0c']==reference['entries']['0x20f78']==1
                    transitions.append(dict(case=case,full_D0=value,original=reference,rebuilt=rebuilt,created_task_records_checked=check_task_records(left,right,reference),floor=expected_floor,index=expected_index,initial_RAM_sha256=sha(bytes(ram)),final_public_RAM_sha256=sha(native.masked(right))))
                    ram=bytearray(left)
                    save(out/'elevator-cases.json',transitions)
        guards=[]
        for overrides in [dict(scratch=0),dict(word_scan=2),dict(budget=0)]:
            _,value,check=runtime.translated(bytes(ram),case,**overrides)
            assert check['status']==1 and value==0xa55aa55a and not check['calls']and runtime.device.ram()==bytes(ram)
            guards.append(overrides)
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error),native_diagnostic=getattr(runtime,'failure',None)));raise
    finally:runtime.close()
    report=dict(status='linked_readable_indoor_scene_stream_and_elevator_roundtrip_actual_disc_match_native',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),elevator_actions=len(transitions),elevator_roundtrips=len(transitions)//2,cold_texture_cases=sum(row['case']['cold_texture_cache']for row in rows),copied_texture_payloads_checked=sum(len(row['copied_texture_payloads_checked'])for row in rows),guards=guards,scene_indices=[314,315],stream_phases=[historical,elevator],elevator_stream_witness=witness,external_services={hex(k):v for k,v in EXTERNAL.items()},source_sha256={name:sha((restore/name).read_bytes())for name in SOURCES+[n.replace('.c','.h')for n in SOURCES]},script_sha256=sha(Path(__file__).read_bytes()),backend_sha256=sha((ROOT/'scripts/biwn_disc_backend.py').read_bytes()),native_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),normalized_disc_sha256=runtime.disc.manifest['normalized_track_sha256'],new_training=False,default_promoted=False,scope='Linked readable20F78->actual scene loader->copy/header relocation->texture acquisition/lookup/fixups->player position and actor parsing/factory, plus1A0F8input->20F0Ccleanup->same scene setup, using actual disc bytes and source C memory/CD helpers. Original/C fullD0,public2MBRAM,external helper args/order,disc requests/completions andsevenblitter registers compare. Original unchanged at674; explicit experimental wordscan at674andcaptured672phase. Mode2indices314/315 from a supplied frozen merchant RAM/TOC/cache/heap, warm/emptytexturecache andempty pending lists; elevator actions use supplied input bits and chain original RAM from Up into Down. BIOS303C/3042 andDF60completion tick,DF6C task creation is computed by source C (new record and neighbor links checked even near private stack); task execution remains outside this synchronous component. E2B8 executes source CPU4B00submission through host device; original/C GPU decoder integration is established separately by the indoor scene sweep. 102C4outdoor geometry is now linked; mode1 integration is checked separately by the outdoor sweep; only observed entries establish reached branches. No fullscheduler,interrupts,physicaltiming,fullCPUABI,natural entry capture,dispatcher/frame-runtime substitution or fullgame proof. Texture loader handle uses mapped private scratch; private stack excluded.')
    report['task_creation_results_supplied']=False
    report['created_task_records_checked']=sum(len(row['created_task_records_checked'])for row in rows+transitions)
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)));save(ROOT/'verification/scene-stream-current.json',report)
    print(json.dumps({k:report[k]for k in ['status','cases','directory']}),flush=True)


if __name__=='__main__':main()

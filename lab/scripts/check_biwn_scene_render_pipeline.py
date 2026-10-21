"""Fresh disc-backed outdoor setup into linked C scene rendering.

Isolated render entry retains the declared GPU geometry seed fixture and
synchronous devices. No scheduler/scanout/global GPU context claim.
"""
import argparse
import ctypes as c
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import random
import subprocess
from types import SimpleNamespace
import check_biwn_outdoor_scene_stream as outdoor
import check_biwn_disc_scene_actors as actors
import check_biwn_actor_full_movement_runtime as movement

scene=outdoor.scene;ROOT=scene.ROOT;world=scene.world;sha=scene.sha;save=scene.save
SP=scene.SP;STOP=scene.STOP
DEVICE=ROOT/'tools/libbiwn-expanded-scene-render-device.dylib'
EXTRA=['biwn_scene_render_pipeline.c','biwn_render_scene.c','biwn_gpu_render_commands.c','biwn_geometry_records_cpu.c','biwn_display_list.c','biwn_gpu_projection_submit_cpu.c','biwn_gpu_draw_submit_cpu.c']
RANGES=[(0x17e0e,0x17f68),(0xe03a,0xe148),(0xe19e,0xe26c),(0x170a0,0x17326),(0x185b2,0x18854),(0xe3e0,0xe4aa)]


class Render:
    def __init__(self,library):
        self.device=movement.Device(DEVICE)
        self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
        self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32]
        self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32
        self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int
        self.core.m68k_set_irq.argtypes=[c.c_uint32]
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32
        self.lib=c.CDLL(str(library))
        self.owner=SimpleNamespace(device=self.device,core=self.core,lib=self.lib)
        actors.Runtime.enable_GPU_render_submissions(self.owner)
        old_write=self.device.write
        def write(address,value):
            old_write(address,value)
            if address==0xf03204 and value in[0x4d80,0x52e0,0x57a0]:
                self.owner.GPU_submission_events[-1]['public_RAM_sha256']=sha(scene.native.masked(self.device.ram()))
        self.device.write=write
        self.lib=c.CDLL(str(library));self.fn=self.lib.biwn_scene_render_pipeline
        self.fn.argtypes=[c.POINTER(world.Bus),type(self.device.write8),c.c_uint32,c.POINTER(c.c_uint32),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)]
        self.fn.restype=c.c_int

    def seed(self,ram,mode):
        self.device.seed(ram,mode);self.device.errors=[]
        for a in range(0xf02200,0xf022a0,4):
            if a!=0xf02238:self.device.write(a,0)
        for a in[0xf03200,0xf0320c,0xf03210,0xf03214,0xf03218,0xf0321c]:self.device.write(a,0)
        assert self.core.GPUReadLong(0xf03204,0)==0xffffffff

    def state(self):
        result=dict(device=self.device.stats(),hardware=[self.device.read(a,4)for a in[0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]],GPU_mailboxes=[self.core.GPUReadLong(a,0)for a in range(0xf03200,0xf03220,4)],GPU_submissions=[{k:v for k,v in row.items()if k!='RAM_sha256'}for row in self.owner.GPU_submission_events])
        if hasattr(self.device.lib,'lab_expanded_bus_fault'):
            self.device.lib.lab_expanded_bus_fault.argtypes=[c.c_uint];self.device.lib.lab_expanded_bus_fault.restype=c.c_uint32
            result['GPU_bus_fault']=[self.device.lib.lab_expanded_bus_fault(i)for i in range(3)]
            self.device.lib.lab_expanded_bus_aliases.restype=c.c_uint64
            result['GPU_bus_high_byte_aliases']=self.device.lib.lab_expanded_bus_aliases()
        return result

    def native(self,ram,incoming):
        self.seed(ram,0);self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
        for i,value in enumerate(incoming):self.core.m68k_set_reg(i,value)
        self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,0x17e0e);self.device.direct(SP,4,STOP)
        entries={};coverage=set()
        for step in range(500000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:break
            assert any(lo<=pc<hi for lo,hi in RANGES),dict(PC=hex(pc),step=step,entries=entries)
            if pc in[0x17e0e,0xe03a,0xe0a6,0x170a0,0xe3e0,0xe220,0xe19e,0xe202,0x17f14,0x185b2]:entries[hex(pc)]=entries.get(hex(pc),0)+1
            coverage.add(pc);self.core.m68k_execute(1)
            command=self.core.GPUReadLong(0xf03204,0)
            if command in[0x4d80,0x52e0,0x57a0,0x4320]:self.device.write(0xf03204,command)
        else:raise AssertionError('Native render did not return')
        assert self.core.m68k_get_reg(None,15)==SP+4
        for i,value in enumerate(incoming):
            if i not in[0,1,8,9]:assert self.core.m68k_get_reg(None,i)==value,(i,value)
        return self.device.ram(),self.core.m68k_get_reg(None,0),dict(**self.state(),entries=entries,CPU_instructions=step,CPU_instruction_addresses=len(coverage))

    def translated(self,ram,incoming,**overrides):
        self.seed(ram,1);calls=[]
        def call(_,target,args,n,out):calls.append(dict(target=hex(target),args=list(args[:n])));return 1
        cb=world.CALL(call);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,cb,None,32768)
        links=(c.c_uint32*64)();output=c.c_uint32(0xa55aa55a)
        args=dict(scratch=SP-512,capacity=64,budget=32768);args.update(overrides)
        status=self.fn(c.byref(bus),self.device.write8,args['scratch'],links,args['capacity'],args['budget'],incoming[0],c.byref(output))
        return self.device.ram(),output.value,dict(**self.state(),status=status,external_calls=calls,errors=list(self.device.errors))

    def close(self):self.device.close()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args()
    out=ROOT/'verification/scene-render-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=scene.SOURCES+EXTRA;library=out/'libscene-render-pipeline.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/n)for n in names],'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    loader=outdoor.Runtime(library);snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes()
    catalogue=json.loads((ROOT/'verification/outdoor-scene-catalog-current.json').read_text());assert sha(snapshot)==catalogue['resident_flag_RAM_sha256']
    prefix=loader.disc.use_previous_track_prefix()
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0];address=int(patch['address'],16);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(old)]==old
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buffer)==diagnosis['buffer_sha256'];witness=loader.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    initial=bytearray(snapshot);initial[address:address+len(old)]=new;initial[0x47b80:0x47b84]=bytes(4)
    rng=random.Random(0x17e0e20f78);registers=lambda:[rng.getrandbits(32)for _ in scene.world.REGS]
    case=dict(entry=0x1aa40,mode=1,word_scan=1,incoming=registers(),external_D0=0xc001d00d)
    prepared,C_prepared,d0,original,rebuilt=outdoor.compare(loader,bytes(initial),case,out,'textures')
    X=scene.native.get(prepared,0x49c50);Z=scene.native.get(prepared,0x49c56)
    vectors=[dict(X=X,Z=Z),dict(X=X+1024,Z=Z),dict(X=X,Z=Z-1024)]
    if opt.limit:vectors=vectors[:opt.limit]
    loaded=[]
    try:
        for i,vector in enumerate(vectors):
            ram=bytearray(prepared)
            ram[0x49c50:0x49c54]=vector['X'].to_bytes(4,'big');ram[0x49c56:0x49c5a]=vector['Z'].to_bytes(4,'big')
            case=dict(mode=1,word_scan=1,incoming=registers(),external_D0=0xc001d00d)
            left,right,d0,reference,rebuilt=outdoor.compare(loader,bytes(ram),case,out,f'load-{i}')
            assert reference['fault']is None and not reference['texture_queue_overruns']and not reference['unmapped_actor_reads']
            # Fresh C setup is the common render input, with its own load proof.
            loaded.append((vector,right,dict(original=reference,rebuilt=rebuilt,source_C_RAM_sha256=sha(right))))
    finally:loader.close()
    render=Render(library);rows=[]
    try:
        for i,(vector,ram,load_proof)in enumerate(loaded):
            for frame in range(4):
                save(out/'status.json',dict(status='running',scene=i,frame=frame));incoming=registers()
                left,expected,original=render.native(ram,incoming);right,value,rebuilt=render.translated(ram,incoming)
                fields=['hardware','GPU_mailboxes','GPU_submissions']
                match=scene.native.masked(left)==scene.native.masked(right)and expected==value and not rebuilt['status']and not rebuilt['errors']and not rebuilt['external_calls']and all(original[k]==rebuilt[k]for k in fields)
                if not match:
                    (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right)
                    save(out/'mismatch.json',dict(scene=i,frame=frame,expected_D0=expected,C_D0=value,original=original,rebuilt=rebuilt,RAM_differences=[hex(a)for a,(l,r)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if l!=r][:64]));raise AssertionError(str(out/'mismatch.json'))
                stats=rebuilt['device']['scene_render'];assert not stats['native_GPU_steps']and not stats['forbidden_GPU_attempts']and not rebuilt['device']['device_error']
                assert [event['command']for event in rebuilt['GPU_submissions']]==[0x4d80,0x52e0,0x57a0]
                framebuffer=scene.native.get(right,0xbd844);assert framebuffer==scene.native.get(ram,0xbd83c)
                pixels=right[framebuffer:framebuffer+224*180*2];assert pixels==left[framebuffer:framebuffer+224*180*2]and len(pixels)==224*180*2
                image=None
                if not frame:
                    import animation_renderer
                    image=out/f'scene-{i}-matched-frame.png';image.write_bytes(animation_renderer.image_png(pixels,224,180,scale=3));(out/f'scene-{i}-matched-frame.raw16be').write_bytes(pixels)
                rows.append(dict(scene=i,frame=frame,vector=vector,load_proof=load_proof if not frame else None,full_D0=value,record_count=scene.native.get(right,0x49b88),final_public_RAM_sha256=sha(scene.native.masked(right)),framebuffer=hex(framebuffer),framebuffer_sha256=sha(pixels),image=str(image)if image else None,original=original,rebuilt=rebuilt,public_RAM_and_GPU_commands_match=True))
                (out/f'scene-{i}-frame-{frame}-C-RAM.bin').write_bytes(right);ram=right
        guards=[]
        for override in[dict(scratch=0),dict(scratch=SP-511),dict(capacity=0),dict(budget=0)]:
            before=loaded[0][1];after,value,result=render.translated(before,registers(),**override)
            assert result['status']==1 and value==0xa55aa55a and before==after
            guards.append(override)
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error),completed_cases=len(rows)));raise
    finally:render.close()
    save(out/'cases.json',rows)
    report=dict(status='disc_scene_setup_into_linked_C_render_matches_original',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),fresh_scene_setups=len(loaded),frames_per_scene=4,guards=guards,source_sha256={n:sha((source/n).read_bytes())for n in names},header_sha256={n.replace('.c','.h'):sha((source/n.replace('.c','.h')).read_bytes())for n in names},script_sha256=sha(Path(__file__).read_bytes()),GPU_device=str(DEVICE),GPU_device_sha256=sha(DEVICE.read_bytes()),core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),prefix=prefix,stream_witness=witness,original_CPU_instructions=sum(row['original']['CPU_instructions']for row in rows),C_render_blits=sum(row['rebuilt']['device']['blit_commands']for row in rows),external_C_render_calls=0,default_promoted=False,standalone=False,scope='Fresh actual-disc1AA40/20F78setup compares nativeCPU/GPUvsC first, and C-produced RAM becomes common input to original17E0Eand linkedC rendering. FullD0/public2MBRAM after private-stack exclusion,7blitterregs,8GPUmailboxes and each geometry/projection/draw GPUarchitecture/RAM/PCcount/hash compare. Linked readable dispatch/clear/rotation/protocols/displaylist; generated source-specific170A0records and Ccopy/GPUmath. Frozen merchant residentRAM, supplied worldcoordinates, explicitwordscan/672phase/contiguousprevious-track bytes, static tasks not scheduled. Geometry still resets/seeds GPU banks and captured4KB RAM on bothlanes eachframe; synchronousGPU/blitter/BIOScompletion, no globalcross-kernelGPUcontext, naturalentry/fullCPUABI/interrupts/taskexecution/objectprocessor/scanout/physicaltiming/fullgame proof. Mode1 outdoor only; E148interiorpreparation remains external and unexecuted.')
    report['images']=[row['image']for row in rows if row['image']]
    report['image_scope']='Actual matched224x180buffer rendered through pinned numericCRY16tables at3x. Resident merchant actor records/art remain supplied; scenegeometry/textures freshly loaded from disc. No objectprocessor/scanout or physicaldisplaycolor proof.'
    report['original_E220_matrix_calls']=sum(row['original']['entries'].get('0xe220',0)for row in rows)
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('scene-render-pipeline-preflight-current.json'if opt.limit else'scene-render-pipeline-current.json'),report);print(json.dumps(report),flush=True)


if __name__=='__main__':main()

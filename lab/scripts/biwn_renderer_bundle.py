"""Renderer C bridge for live ordinary GPU bundles; no original opcode fallback."""
import ctypes as c
import json
import check_biwn_movie_GPU as GPU
from pathlib import Path
from biwn_frame_OP_GPU import R16,R32,W16,W32,OBS
ROOT=Path(__file__).resolve().parents[1]
BLIT=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint8))
class Bus(c.Structure):
    _fields_=[('read16',R16),('read32',R32),('write32',W32),('blitter_write32',BLIT),('observe_PC',OBS),('context',c.c_void_p)]
class OverlayBus(c.Structure):
    _fields_=[('read16',R16),('read32',R32),('write16',W16),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]
class State(c.Structure):
    _fields_=[('registers',(c.c_uint32*32)*2)]+[(n,c.c_uint32)for n in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','instructions','accumulator']]+[('local_RAM',c.c_uint8*4096)]
class GeometryState(c.Structure):
    _fields_=[x for x in State._fields_ if x[0]!='accumulator']
class Renderer:
    def __init__(self,core,overlays_enabled=False,materials_enabled=False,controls_enabled=False,setup_enabled=False):
        source=json.loads((ROOT/'verification/renderer-bundle-candidate.json').read_text())
        ABI=json.loads((ROOT/'verification/renderer-bundle-ABI-current.json').read_text())
        assert ABI['status']=='compiled_headers_match_ctypes' and ABI['directory']==source['directory']
        types={'resident':(State,Bus),'geometry':(GeometryState,OverlayBus),'projection':(State,OverlayBus)}
        for row in ABI['rows']:
            typ=types[row['name']][0 if row['kind']=='state' else 1]
            actual=c.sizeof(typ)if row['field']=='size'else getattr(typ,row['field']).offset
            assert actual==row['offset_or_size'],('GPU ABI mismatch',row)
        self.source=source;self.expected={r['address']:bytes.fromhex(r['bytes'])for r in source['instructions_decoded']}
        self.library=c.CDLL(source['library']);self.run=self.library.biwn_gpu_resident_bundle_run
        self.run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];self.run.restype=c.c_int
        core.GPUGetRAM.restype=c.c_void_p
        def blit(_,a,v,local_RAM):
            c.memmove(core.GPUGetRAM(),local_RAM,4096)
            core.GPUWriteLong(a,v,6)
            c.memmove(local_RAM,core.GPUGetRAM(),4096)
            return 0
        self.callbacks=[R16(lambda _,a,p:(p.__setitem__(0,core.GPUReadWord(a,6)),0)[1]),
                        R32(lambda _,a,p:(p.__setitem__(0,core.GPUReadLong(a,6)),0)[1]),
                        W32(lambda _,a,v:(core.GPUWriteLong(a,v,6),0)[1]),BLIT(blit),OBS()]
        self.bus=Bus(*self.callbacks,None)
        self.programs=[dict(name='resident',expected=self.expected,run=self.run,bus=self.bus,state_type=State)]
        self.overlay_callbacks=[self.callbacks[0],self.callbacks[1],W16(lambda _,a,v:(core.GPUWriteWord(a,v,6),0)[1]),self.callbacks[2],OBS()]
        self.overlay_bus=OverlayBus(*self.overlay_callbacks,None);self.overlay_libraries=[]
        for overlay in (source.get('overlays',[]) if overlays_enabled else []):
            library=c.CDLL(overlay['library']);self.overlay_libraries.append(library)
            fn=getattr(library,'biwn_gpu_'+overlay['name']+'_bundle_run')
            state_type=GeometryState if overlay['name']=='geometry' else State
            fn.argtypes=[c.POINTER(OverlayBus),c.POINTER(state_type),c.c_uint32];fn.restype=c.c_int
            self.programs.append(dict(name=overlay['name'],expected={r['address']:bytes.fromhex(r['bytes'])for r in overlay['instructions_decoded']},run=fn,bus=self.overlay_bus,state_type=state_type))
        self.materials=None;self.private_after=None
        if materials_enabled:
            from biwn_material_bundle import Materials
            self.materials=Materials(core);self.programs.extend(self.materials.programs)
        self.control_source=None
        if controls_enabled:
            assert self.materials is not None,'Control kernels need material read8 bus'
            self.control_source=json.loads((ROOT/'verification/control-GPU-bundle-candidate.json').read_text())
            assert self.control_source['status']=='compiled_ABI_checked_unverified'
            for row in self.control_source['ABI_checks']:
                typ=GPU.State if row['kind']=='state'else OverlayBus if row['name']=='movement'else type(self.materials.material_bus)
                assert row['value']==(c.sizeof(typ)if row['field']=='size'else getattr(typ,row['field']).offset),('Control GPU ABI mismatch',row)
            for row in self.control_source['overlays']:
                library=c.CDLL(row['library']);self.overlay_libraries.append(library)
                fn=getattr(library,row['function']);bus=self.overlay_bus if row['name']=='movement'else self.materials.material_bus
                fn.argtypes=[c.POINTER(type(bus)),c.POINTER(GPU.State),c.c_uint32];fn.restype=c.c_int
                self.programs.append(dict(name=row['name'],expected={x['address']:bytes.fromhex(x['bytes'])for x in row['instructions_decoded']},run=fn,bus=bus,state_type=GPU.State,control=True))
        self.setup_source=None
        if setup_enabled:
            assert self.materials is not None,'Setup kernel needs live material bus'
            from biwn_material_bundle import PartialState
            from build_biwn_setup_bundle import SetupBus
            self.setup_source=json.loads((ROOT/'verification/setup-bundle-candidate.json').read_text())
            assert self.setup_source['status']=='compiled_ABI_checked_unverified'
            for row in self.setup_source['ABI_checks']:
                typ=PartialState if row['kind']=='state'else SetupBus
                assert row['value']==(c.sizeof(typ)if row['field']=='size'else getattr(typ,row['field']).offset),('Setup GPU ABI mismatch',row)
            library=c.CDLL(self.setup_source['library']);self.overlay_libraries.append(library);fn=library.biwn_gpu_setup57_bundle_run
            callbacks=self.materials.callbacks;self.setup_bus=SetupBus(callbacks[2],callbacks[4],callbacks[5],None)
            fn.argtypes=[c.POINTER(SetupBus),c.POINTER(PartialState),c.c_uint32];fn.restype=c.c_int
            self.programs.append(dict(name='setup57',expected={x['address']:bytes.fromhex(x['bytes'])for x in self.setup_source['instructions_decoded']},run=fn,bus=self.setup_bus,state_type=PartialState,material=True))
        self.addresses=set().union(*(x['expected']for x in self.programs));self.selected=None
    def select(self,pc,opcode,raw):
        offset=pc-0xf03000
        for program in self.programs:
            mapping=program['expected'];identity=mapping.get(pc)
            if identity is None or raw[offset:offset+len(identity)]!=identity:continue
            if opcode>>10 in [52,53]:
                delay=mapping.get(pc+2)
                if delay is None or raw[offset+2:offset+2+len(delay)]!=delay:continue
            self.selected=program;return mapping
        self.selected=None;return None
    def execute(self,full):
        assert full.active_bank==0,('renderer requires active bank0',full.active_bank)
        self.private_after=None
        if self.selected.get('material'):
            status=self.materials.execute(self.selected,full);self.private_after=self.materials.private_after;return status
        state=self.selected['state_type']()
        for name,_ in state._fields_:
            if name=='registers':c.memmove(c.addressof(state.registers),c.addressof(full.registers),256)
            elif name=='local_RAM':state.local_RAM[:]=full.local_RAM[:]
            else:setattr(state,name,getattr(full,name))
        assert self.selected is not None
        status=self.selected['run'](c.byref(self.selected['bus']),c.byref(state),1)
        if status:return status
        for name,_ in state._fields_:
            if name=='registers':c.memmove(c.addressof(full.registers),c.addressof(state.registers),256)
            elif name=='local_RAM':full.local_RAM[:]=state.local_RAM[:]
            else:setattr(full,name,getattr(state,name))
        return 0

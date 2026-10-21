"""Short-state material kernels retain live bus RAM/MMIO effects in full GPU state."""
import ctypes as c,json
from pathlib import Path
import check_biwn_movie_GPU as GPU
from biwn_frame_OP_GPU import R16,R32,W16,W32,OBS
ROOT=Path(__file__).resolve().parents[1]
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8))
class PartialState(c.Structure):
    _fields_=[('registers',(c.c_uint32*32)*2)]+[(n,c.c_uint32)for n in ['pc','z','c','n','instructions']]
class MaterialBus(c.Structure):
    _fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]
class ConsumerBus(c.Structure):
    _fields_=[('read16',R16),('read32',R32),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]
class Materials:
    def __init__(self,core):
        self.core=core;self.source=json.loads((ROOT/'verification/material-bundle-candidate.json').read_text())
        assert self.source['status']=='compiled_ABI_checked_unverified'
        for row in self.source['ABI_checks']:
            typ=PartialState if row['kind']=='state'else MaterialBus if row['name'].startswith('material')else ConsumerBus
            assert row['value']==(c.sizeof(typ)if row['field']=='size'else getattr(typ,row['field']).offset)
        core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
        self.callbacks=[R8(lambda _,a,p:(p.__setitem__(0,core.JaguarReadByte(a,6)),0)[1]),R16(lambda _,a,p:(p.__setitem__(0,core.GPUReadWord(a,6)),0)[1]),R32(lambda _,a,p:(p.__setitem__(0,core.GPUReadLong(a,6)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,6),0)[1]),W32(lambda _,a,v:(core.GPUWriteLong(a,v,6),0)[1]),OBS()]
        self.material_bus=MaterialBus(*self.callbacks,None);self.consumer_bus=ConsumerBus(self.callbacks[1],self.callbacks[2],self.callbacks[4],self.callbacks[5],None)
        self.programs=[];self.libraries=[];self.private_after=None
        for row in self.source['overlays']:
            library=c.CDLL(row['library']);self.libraries.append(library);fn=getattr(library,'biwn_gpu_'+row['name']+'_bundle_run')
            bus=self.material_bus if row['name'].startswith('material')else self.consumer_bus
            fn.argtypes=[c.POINTER(type(bus)),c.POINTER(PartialState),c.c_uint32];fn.restype=c.c_int
            self.programs.append(dict(name=row['name'],expected={x['address']:bytes.fromhex(x['bytes'])for x in row['instructions_decoded']},run=fn,bus=bus,state_type=PartialState,material=True))
    def execute(self,program,full):
        state=PartialState();c.memmove(c.addressof(state.registers),c.addressof(full.registers),256)
        for name in ['pc','z','c','n','instructions']:setattr(state,name,getattr(full,name))
        status=program['run'](c.byref(program['bus']),c.byref(state),1)
        if status:return status
        # Short kernels route all memory/control writes to live core. Keep them.
        buf=c.create_string_buffer(4416);assert self.core.GPUStateSave(buf)==4416;raw=buf.raw;actual=GPU.state_from_raw(raw)
        for name,_ in GPU.State._fields_:
            if name=='local_RAM':full.local_RAM[:]=actual.local_RAM[:]
            elif name not in ['registers','pc','z','c','n','instructions']:setattr(full,name,getattr(actual,name))
        c.memmove(c.addressof(full.registers),c.addressof(state.registers),256)
        for name in ['pc','z','c','n','instructions']:setattr(full,name,getattr(state,name))
        self.private_after=raw[4396:];return 0

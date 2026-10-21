"""Original GPUExec versus isolated OP C, including branch-ending private words."""
import ctypes as c,hashlib,json,struct
from pathlib import Path
import check_biwn_scheduler as scheduler
import check_biwn_movie_GPU as GPU
from biwn_frame_OP_GPU import Bus,R16,R32,W16,W32,OBS
ROOT=Path(__file__).resolve().parents[1]
def main():
    build=json.loads((ROOT/'verification/OP-private-experimental-candidate.json').read_text())
    corepath=ROOT/'verification/BIWN-regular-GPU-owner-build/20261016T035215.288859Z/source/virtualjaguar_libretro.dylib'
    native=scheduler.Native(diagnostic_core=corepath);core=native.lib
    native.device.pointer=native.device.lib.lab_device_ram()
    core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool
    assert core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode())
    core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
    core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool
    for n in ['GPUStateSave','GPUStateLoad']:getattr(core,n).argtypes=[c.c_void_p];getattr(core,n).restype=c.c_size_t
    core.GPUExec.argtypes=[c.c_int32]
    for n,t in [('GPUReadWord',c.c_uint16),('GPUReadLong',c.c_uint32)]:getattr(core,n).argtypes=[c.c_uint32,c.c_uint32];getattr(core,n).restype=t
    for n in ['GPUWriteWord','GPUWriteLong']:getattr(core,n).argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    lib=c.CDLL(build['library']);fn=lib.biwn_gpu_OP_slice_run;fn.argtypes=[c.POINTER(Bus),c.POINTER(GPU.State),c.c_uint32];fn.restype=c.c_int
    callbacks=[R16(lambda _,a,p:(p.__setitem__(0,core.GPUReadWord(a,6)),0)[1]),R32(lambda _,a,p:(p.__setitem__(0,core.GPUReadLong(a,6)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,6),0)[1]),W32(lambda _,a,v:(core.GPUWriteLong(a,v,6),0)[1]),OBS()];bus=Bus(*callbacks,None)
    folder=ROOT/'runs/merchant-playback-C-candidate1';machine=(folder/'final-serialized-state.bin').read_bytes()
    fixtures=[folder/'OP-GPU-slices/004040-before.bin',ROOT/'runs/merchant-audio-start-C-movie-GPU/OP-GPU-slices/000000-before.bin']
    results=[]
    def restore(raw):
        assert core.retro_unserialize(c.create_string_buffer(machine),len(machine));assert core.GPUStateLoad(c.create_string_buffer(raw))==4416
    def raw_state():
        buffer=c.create_string_buffer(4416);assert core.GPUStateSave(buffer)==4416;return buffer.raw
    try:
        for fixture in fixtures:
            raw=fixture.read_bytes();restore(raw);core.GPUExec(16);expected=raw_state();expected_RAM=native.device.ram()
            restore(raw);state=GPU.state_from_raw(raw);state.instructions=0;assert fn(c.byref(bus),c.byref(state),16)==0
            values=(c.c_uint32*3)();lib.biwn_gpu_OP_slice_last_private(values);private=bytearray(raw[4396:]);struct.pack_into('=3I',private,0,*values);rebuilt=GPU.logical(state)+private
            assert rebuilt==expected,('GPU raw mismatch',str(fixture),[(i,a,b)for i,(a,b)in enumerate(zip(rebuilt,expected))if a!=b][:8])
            assert native.device.ram()==expected_RAM
            results.append({'fixture':str(fixture),'private_words':list(values),'GPU_raw_4416_exact':True,'RAM_exact':True,'C_source_instructions':state.instructions})
        proof={'status':'OP_private_metadata_original_GPU_4416bytes_and_RAM_exact','fixtures':results,'library':build['library'],'scope':'Two declared GPU-only atomic fixtures, including actual rejected branch-ending OP input; hardware state seeded from rejected run, not a complete gameplay continuation.','whole_game_complete':False}
        (ROOT/'verification/OP-private-original-checks.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
    finally:native.close()
if __name__=='__main__':main()

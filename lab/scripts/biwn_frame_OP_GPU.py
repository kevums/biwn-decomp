"""Observe or own live OP-triggered GPU releases during ordinary frames.

Only these releases are delegated. The regular GPU scheduler remains original.
Every source input is live; no reference state is loaded into the machine.
"""
import ctypes as c
import hashlib
import json
import struct
from pathlib import Path
import check_biwn_movie_GPU as GPU

ROOT=Path(__file__).resolve().parents[1]
R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16))
R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32))
W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16)
W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
OBS=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
OWNER=c.CFUNCTYPE(c.c_int,c.c_int,c.c_int32)

class Bus(c.Structure):
    _fields_=[('read16',R16),('read32',R32),('write16',W16),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]


def install(core,out,mode,regular_mode="none",candidate=None):
    assert mode in ['trace','C']
    records,errors,stack=[],[],[]
    directory=out/'OP-GPU-slices';directory.mkdir()
    count=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t
    core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    source=json.loads((candidate or ROOT/'verification/OP-GPU-slice-current.json').read_text())
    library=Path(source['library'])
    instructions=source['instructions_decoded']
    expected={row['address']:bytes.fromhex(row['bytes']) for row in instructions}
    assert expected
    lib=c.CDLL(str(library));run=lib.biwn_gpu_OP_slice_run
    run.argtypes=[c.POINTER(Bus),c.POINTER(GPU.State),c.c_uint32];run.restype=c.c_int
    outer_PCs=[]
    input_RAM=None
    def observed(_,pc):
        outer_PCs.append(pc)
        if expected:
            identity=expected.get(pc)
            if identity is None or input_RAM[pc-0xf03000:pc-0xf03000+len(identity)]!=identity:
                errors.append('fixed OP instruction identity changed at '+hex(pc))
    callbacks=[R16(lambda _,a,p:(p.__setitem__(0,core.GPUReadWord(a,6)),0)[1]),
               R32(lambda _,a,p:(p.__setitem__(0,core.GPUReadLong(a,6)),0)[1]),
               W16(lambda _,a,v:(core.GPUWriteWord(a,v,6),0)[1]),
               W32(lambda _,a,v:(core.GPUWriteLong(a,v,6),0)[1]),OBS(observed)]
    bus=Bus(*callbacks,None)
    def snapshot():
        buf=c.create_string_buffer(8192);size=core.GPUStateSave(buf)
        assert size==4416,size
        return buf.raw[:size]
    def observer(phase,cycles):
        nonlocal input_RAM
        if errors:return int(mode=='C')
        try:
            raw=snapshot()
            if phase==0:
                index=len(records)+len(stack)
                row=dict(index=index,cycles=cycles,before_PC=GPU.state_from_raw(raw).pc,
                         before_GPU_sha256=hashlib.sha256(raw[:4396]).hexdigest(),counter_before=count.value)
                (directory/f'{index:06d}-before.bin').write_bytes(raw)
                stack.append(row)
                if mode=='C':
                    assert (c.c_uint8*5).in_dll(core,'vjs')[4]==0,'GPU pipeline profile unsupported'
                    outer_PCs.clear();input_RAM=raw[:4096]
                    state=GPU.state_from_raw(raw);state.instructions=0
                    result=run(c.byref(bus),c.byref(state),cycles)
                    row.update(C_status=result,C_after_PC=state.pc,C_source_instructions=state.instructions)
                    assert result==0,('OP release unsupported',index,result,hex(row['before_PC']),hex(state.pc))
                    assert not errors,errors
                    assert count.value==row['counter_before'],'original GPU opcode inside C release'
                    last_PC=outer_PCs[-1];offset=last_PC-0xf03000
                    opcode=int.from_bytes(input_RAM[offset:offset+2],'big')
                    assert opcode>>10 not in [52,53]or source.get('private_metadata_getter'), 'Ending on a branch needs explicit private delay metadata'
                    # Native GPUExec retains the last outer opcode and its
                    # decoded operand indices. These private fields are part
                    # of the raw state and must not be left stale.
                    private=bytearray(raw[4396:]);struct.pack_into('=3I',private,0,opcode,(opcode>>5)&31,opcode&31)
                    if source.get('private_metadata_getter'):
                        values=(c.c_uint32*3)();lib.biwn_gpu_OP_slice_last_private(values)
                        struct.pack_into('=3I',private,0,*values)
                    blob=GPU.logical(state)+private
                    row['outer_PCs']=list(outer_PCs)
                    assert core.GPUStateLoad(c.create_string_buffer(blob))==4416
            else:
                assert phase==1 and stack
                row=stack.pop();row.update(after_PC=GPU.state_from_raw(raw).pc,
                                           after_GPU_sha256=hashlib.sha256(raw[:4396]).hexdigest(),
                                           original_opcode_delta=(count.value-row['counter_before'])&0xffffffff)
                (directory/f'{row["index"]:06d}-after.bin').write_bytes(raw);records.append(row)
            return int(mode=='C')
        except BaseException as error:
            errors.append(repr(error));return int(mode=='C')
    callback=OWNER(observer);core.BIWNSetOPGPUExecOwner.argtypes=[OWNER];core.BIWNSetOPGPUExecOwner(callback)
    def finish():
        core.BIWNSetOPGPUExecOwner(OWNER())
        report=dict(status='completed_uncompared'if not errors and not stack else'rejected',mode=mode,
                    directory=str(directory),records=records,pending=stack,errors=errors,library=str(library),
                    calls=len(records),regular_GPU_scope=('consult regular-GPU-bundles/report.json for owned/original counts'if regular_mode!='none'else'original provider'),whole_game_complete=False)
        (directory/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        return report
    return callback,callbacks,lib,errors,finish

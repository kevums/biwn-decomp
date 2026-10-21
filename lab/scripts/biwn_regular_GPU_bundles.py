"""Fixed resident GPU bundles in the ordinary GPU loop; uncovered code counted."""
import collections
import ctypes as c
import hashlib
import json
import struct
from pathlib import Path
import check_biwn_movie_GPU as GPU
from biwn_frame_OP_GPU import Bus,R16,R32,W16,W32,OBS

ROOT=Path(__file__).resolve().parents[1]
OWNER=c.CFUNCTYPE(c.c_int,c.c_uint32,c.c_uint16,c.c_uint32)


def install(core,out,mode,witness_limit=0,renderer_enabled=False,renderer_overlays=False,reference_trace=None,material_bundles=False,diagnostic_capture=False,control_bundles=False,setup_bundles=False,witness_only=False):
    assert not witness_only or mode=='trace'
    assert mode in ['trace','C']
    source=json.loads((ROOT/'verification/OP-GPU-slice-current.json').read_text())
    expected={row['address']:bytes.fromhex(row['bytes']) for row in source['instructions_decoded']}
    library=c.CDLL(source['library']);run=library.biwn_gpu_OP_slice_run
    run.argtypes=[c.POINTER(Bus),c.POINTER(GPU.State),c.c_uint32];run.restype=c.c_int
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t
    core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    renderer=None
    if renderer_enabled:
        from biwn_renderer_bundle import Renderer
        renderer=Renderer(core,renderer_overlays,material_bundles,control_bundles,setup_bundles)
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    errors=[];known=collections.Counter();uncovered=collections.Counter()
    states=bytearray();after_states=bytearray();source_instructions=0
    PC_stream=bytearray();recent=collections.deque(maxlen=16)
    reference_hashes=(reference_trace/'regular-GPU-bundles/before-state-hashes.bin').read_bytes()if reference_trace else None
    witnesses=[];witness_keys=set()
    witness_dir=out/'uncovered-GPU-witnesses'
    if witness_limit:witness_dir.mkdir()
    RAM=c.c_void_p.in_dll(core,'jaguarMainRAM').value
    callbacks=[R16(lambda _,a,p:(p.__setitem__(0,core.GPUReadWord(a,6)),0)[1]),
               R32(lambda _,a,p:(p.__setitem__(0,core.GPUReadLong(a,6)),0)[1]),
               W16(lambda _,a,v:(core.GPUWriteWord(a,v,6),0)[1]),
               W32(lambda _,a,v:(core.GPUWriteLong(a,v,6),0)[1]),OBS()]
    bus=Bus(*callbacks,None);buf=c.create_string_buffer(8192)
    def snapshot():
        assert core.GPUStateSave(buf)==4416
        return buf.raw[:4416]
    def callback(pc,opcode,unsupported):
        nonlocal source_instructions
        if errors:return -1
        renderer_raw=None
        renderer_matches=False
        renderer_mapping=None
        if renderer and pc not in expected and pc in renderer.addresses:
            renderer_raw=snapshot();renderer_mapping=renderer.select(pc,opcode,renderer_raw)
            renderer_matches=renderer_mapping is not None
        if pc not in expected and not renderer_matches:
            uncovered[(pc,opcode)]+=1
            if witness_limit and mode=='trace' and unsupported==0 and (pc,opcode)not in witness_keys and len(witnesses)<witness_limit:
                witness_keys.add((pc,opcode));raw=snapshot();index=len(witnesses);stem=f'{index:04d}'
                (witness_dir/(stem+'-GPU.bin')).write_bytes(raw)
                (witness_dir/(stem+'-RAM.bin')).write_bytes(c.string_at(RAM,0x200000))
                witnesses.append(dict(index=index,pc=hex(pc),opcode=hex(opcode),profile_mask=unsupported,
                                      GPU_state_sha256=hashlib.sha256(raw).hexdigest(),
                                      scope='Live pre-bundle witness. No after-state or standalone instruction acceptance yet.'))
            return 0
        try:
            if witness_only:
                known[pc]+=1
                return 0
            raw=renderer_raw or snapshot();mapping=expected if pc in expected else renderer_mapping
            identity=mapping[pc];offset=pc-0xf03000
            assert raw[offset:offset+len(identity)]==identity,('resident instruction bytes changed',hex(pc))
            known[pc]+=1;digest=hashlib.sha256(raw[:4396]).digest();index=len(states)//32
            PC_stream.extend(struct.pack('>I',pc))
            if diagnostic_capture and mode=='trace' and (282959<=index<=282980 or (material_bundles and pc not in expected and renderer.selected.get('material'))):
                diagnostic=out/'GPU-first-divergence';diagnostic.mkdir(exist_ok=True)
                (diagnostic/(str(index)+'-GPU.bin')).write_bytes(raw)
            if reference_hashes is not None and digest!=reference_hashes[index*32:index*32+32]:
                diagnostic=out/'GPU-first-divergence';diagnostic.mkdir(exist_ok=True)
                (diagnostic/'actual-GPU.bin').write_bytes(raw)
                (diagnostic/'actual-RAM.bin').write_bytes(c.string_at(RAM,0x200000))
                (diagnostic/'report.json').write_text(json.dumps(dict(index=index,pc=hex(pc),opcode=hex(opcode),recent=list(recent)),indent=2)+'\n')
                raise AssertionError(('first GPU divergence',index,hex(pc)))
            recent.append(dict(index=index,pc=hex(pc),opcode=hex(opcode),program='OP'if pc in expected else renderer.selected['name']))
            states.extend(digest)
            if mode=='trace':return 0
            assert unsupported==0,('owned GPU profile/late-load unsupported',unsupported,hex(pc))
            state=GPU.state_from_raw(raw);state.instructions=0;before=counter.value
            # Fence any taken branch delay before allowing external stores.
            if opcode>>10 in [52,53]:
                delay=mapping.get(pc+2)
                assert delay is not None and raw[offset+2:offset+2+len(delay)]==delay,('changed delay instruction',hex(pc))
            status=run(c.byref(bus),c.byref(state),1) if pc in expected else renderer.execute(state)
            assert status==0 and state.instructions in [1,2],('fixed GPU bundle',hex(pc),status,state.instructions)
            assert counter.value==before,'original GPU inside owned bundle'
            private=bytearray(renderer.private_after if pc not in expected and renderer.private_after is not None else raw[4396:])
            operand_word=opcode
            if state.instructions==2:
                assert opcode>>10 in [52,53],('unexpected multi-op bundle',hex(pc))
                operand_word=int.from_bytes(raw[offset+2:offset+4],'big')
            struct.pack_into('=3I',private,0,opcode,(operand_word>>5)&31,operand_word&31)
            blob=GPU.logical(state)+private
            assert core.GPUStateLoad(c.create_string_buffer(blob))==4416
            source_instructions+=state.instructions;after_states.extend(hashlib.sha256(blob[:4396]).digest())
            return 1
        except BaseException as error:
            errors.append(repr(error));return -1
    owner=OWNER(callback);core.BIWNSetGPUBundleOwner.argtypes=[OWNER];core.BIWNSetGPUBundleOwner(owner)
    for name in ['Owned','Original','Rejected']:getattr(core,'BIWNGPU'+name+'BundleCount').restype=c.c_uint64
    def finish():
        counts={name: getattr(core,'BIWNGPU'+name+'BundleCount')() for name in ['Owned','Original','Rejected']}
        core.BIWNSetGPUBundleOwner(OWNER())
        directory=out/'regular-GPU-bundles';directory.mkdir()
        (directory/'PC-stream.bin').write_bytes(PC_stream)
        (directory/'before-state-hashes.bin').write_bytes(states);(directory/'C-after-state-hashes.bin').write_bytes(after_states)
        if witness_limit:(witness_dir/'manifest.json').write_text(json.dumps(witnesses,indent=2)+'\n')
        report=dict(status='rejected'if errors or counts['Rejected']else'completed_uncompared',mode=mode,counts=counts,
                    C_source_instructions=source_instructions,known_PC_counts={hex(k):v for k,v in known.items()},
                    uncovered_instruction_variants=[{'pc':hex(pc),'opcode':hex(op),'visits':n}for (pc,op),n in sorted(uncovered.items())],
                    errors=errors,library=source['library'],regular_GPU_fully_owned=False,whole_game_complete=False)
        report['uncovered_pre_bundle_witnesses']=len(witnesses)
        report['known_instruction_state_hashes_omitted_for_witness_discovery']=witness_only
        report['renderer_enabled']=renderer_enabled
        report['renderer_library']=renderer.source['library'] if renderer else None
        report['renderer_overlays']=renderer.source.get('overlays',[]) if renderer and renderer_overlays else []
        report['renderer_overlays_enabled']=renderer_overlays
        report['setup_bundles_enabled']=setup_bundles
        report['setup_source']=renderer.setup_source if renderer and renderer.setup_source else None
        report['control_bundles_enabled']=control_bundles
        report['control_overlays']=renderer.control_source['overlays'] if renderer and renderer.control_source else []
        report['material_bundles_enabled']=material_bundles
        report['material_overlays']=renderer.materials.source['overlays'] if renderer and renderer.materials else []
        (directory/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report
    return owner,callbacks,library,errors,finish

"""Byte/unsupported-state/unknown-PC rejection checks for the external DSP candidate."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from check_biwn_scheduler import Native
from biwn_DSP_music_owner import OWNER
import biwn_DSP_program_router as owner_module

def main():
    cp=ROOT/'verification/external-DSP-experimental-candidate-current.json';candidate=json.loads(cp.read_text());gate=json.loads((ROOT/'verification/external-DSP-native-check-current.json').read_text());assert gate['status']=='terminal_external_DSP_native_pass'and gate['cases']==5580
    observation=json.loads((ROOT/'verification/merchant-DSP-transition-observation-current.json').read_text());w=next(w for w in observation['observer']['witnesses']if w['PC']=='0x0');raw=Path(w['file']).read_bytes()
    fixture=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    for row in json.loads((Path(candidate['directory'])/'external-identities.json').read_text()):fixture[row['address']:row['address']+2]=bytes.fromhex(row['bytes'])
    out=ROOT/'verification/external-DSP-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    n=Native(diagnostic_core=Path(candidate['required_core_path']));core=n.lib;core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t;core.DSPExec.argtypes=[c.c_int32]
    callback,lib,host,finish=owner_module.install(core,out,Path(candidate['directory'])/'candidate.json');fn=lib.biwn_DSP_router_owner;fn.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];fn.restype=c.c_int
    def snapshot():
        b=c.create_string_buffer(32768);size=core.DSPStateSave(b);return b.raw[:size]
    rows=[]
    try:
        for name,pc,opcode,unsupported,change,via_core in [('bytes',0,0xf1,0,True,False),('opcode_argument',0,0xf0,0,False,False),('load_hazard',0,0xf1,2,False,False),('division_hazard',0,0xf1,4,False,False),('both_hazards',0,0xf1,6,False,False),('odd_PC',1,0xf1,0,False,False),('unknown_PC',0x398,0,0,False,False),('core_byte_reject',0,0xf1,0,True,True),('core_unknown_reject',0x398,0,0,False,True)]:
            core.BIWNSetDSPInstructionOwner(OWNER());data=bytearray(fixture)
            if change:data[0]^=0x80
            n.device.seed(bytes(data),0);state=bytearray(raw);struct.pack_into('=I',state,8192,pc);assert core.DSPStateLoad(c.create_string_buffer(bytes(state)))==len(state)
            assert lib.biwn_DSP_router_begin(c.byref(host))==0;core.BIWNSetDSPInstructionOwner(callback);before=snapshot();RAM=n.device.ram()
            if via_core:
                core.DSPExec(1);counts={k:getattr(core,'BIWNDSP'+k+'InstructionCount')()for k in ['Owned','Original','Rejected']};assert counts==dict(Owned=0,Original=0,Rejected=1);result=None;preserved=None
            else:
                result=fn(pc,opcode,unsupported);preserved=snapshot()==before;assert result<0 and preserved;counts=None
            assert n.device.ram()==RAM;rows.append(dict(case=name,negative_result=result,full_DSP_preserved_for_direct_rejection=preserved,full_RAM_preserved=True,core_counts=counts))
        assert lib.biwn_DSP_external_begin(None)==1;rows.append(dict(case='null_host_begin',status=1))
        finish();proof=dict(status='terminal_external_DSP_guards_pass',directory=str(out),cases=len(rows),results=rows,candidate=str(Path(candidate['directory'])/'candidate.json'),source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',Path(candidate['directory'])/'candidate.json',Path(candidate['library']),Path(candidate['external_library'])]},scope='Direct byte/argument/hazard/unknown-PC rejection preserves full savedDSP and2MBRAM. Two actual core hook rejections prove0original opcodefallback and1rejection. Not arbitrary pointers, all peripheral faults or hardware proof.',new_training=False)
        save(out/'protocol.json',proof);save(ROOT/'verification/external-DSP-guards-current.json',proof);print(proof['status'],len(rows),flush=True)
    finally:n.close()

if __name__=='__main__':main()

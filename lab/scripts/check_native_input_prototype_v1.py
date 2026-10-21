"""Execute compiled 68000 input C through its C-ABI fixture entry.

Reference connected425 already executed original191F4andE588. This test
compares the new native component with that checked source's ordered global
accesses and outputs. No original helper instructions execute in these paths.
"""
import argparse,ctypes as c,gc,random
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as dispatch
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    rp=V/'input-timing-connected-v1-current.json';reference=read(rp)
    for path,digest in reference['source_sha256'].items():assert sha(path)==digest,path
    folder=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/input-dispatch-native-v1'
    provenance=read(folder/'source-provenance.json');old=Path(provenance['original_source']).read_text()
    assert sha(provenance['original_source'])==provenance['original_sha256']
    change=provenance['changes'][0];assert (folder/'input-source.c').read_text()==old.replace(change['before'],change['after'])
    payload=(folder/'build/native-input.bin').read_bytes();assert 0<len(payload)<65536
    base=0x1c0000;sp=0x1ff000;stop=0x3000;output=0x1ee000
    refdir=Path(reference['directory']);allcases=read(refdir/'cases.json');vectors=allcases[:args.limit]if args.limit else allcases
    out=V/'native-input-prototype-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    host=c.CDLL(str(refdir/'input-and-division.dylib'));fn=host.biwn_input_dispatch
    fn.argtypes=[c.POINTER(dispatch.world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    divide=host.biwn_signed_division;divide.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];divide.restype=c.c_int
    class Script(dispatch.Script):
        def call(self,address,params):
            assert address==0xe588 and params[1]==300
            self.trace.append(['call',address,params]);q=c.c_uint32();r=c.c_uint32()
            assert divide(*params,c.byref(q),c.byref(r))==0;return q.value
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1c0000);results=[]
    for index,saved in enumerate(vectors):
        vector=saved['vector'];incoming=[rng.getrandbits(32)for _ in dispatch.world.REGS]
        case=dict(kind=vector['kind'],incoming=[0]*len(incoming),initial=[
            [0x4624a,2,0],[0x49d62,2,0],[0x49c4e,2,0],[0x49cb8,2,vector['state']],
            [0x49ba4,4,vector['held']],[0x4c24c,4,vector['dt']],[0x49cc8,4,vector['remainder']]],
            helper_returns={str(x):0 for x in dispatch.HELPERS},default_helper_return=0)
        model=Script(snapshot,case);status,expected=dispatch.translated(fn,model,case)
        assert status==0 and expected==saved['original_and_C_speed']
        oracle=[x for x in model.trace if x[:2]!=['call',0xe588]]
        initial=Script(snapshot,case).memory;cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(initial));cpu.mem_write(base,payload)
        arguments=(0).to_bytes(4,'big')+output.to_bytes(4,'big');cpu.mem_write(sp,stop.to_bytes(4,'big')+arguments)
        cpu.mem_write(output,b'\xa5\x5a\xa5\x5a')
        for reg,value in zip(dispatch.world.REGS,incoming):cpu.reg_write(reg,value)
        cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,sp)
        trace=[];minimum=sp;instructions=0
        def private(address,width):return sp-0x4000<=address and address+width<=sp+16
        def code(engine,address,width,user):
            nonlocal instructions,minimum
            assert base<=address<base+len(payload),hex(address)
            instructions+=1;minimum=min(minimum,engine.reg_read(UC_M68K_REG_A7))
        def memory_read(engine,access,address,width,value,user):
            if private(address,width)or base<=address<base+len(payload)or output<=address<output+4:return
            trace.append(['r',address,width,int.from_bytes(engine.mem_read(address,width),'big')])
        def memory_write(engine,access,address,width,value,user):
            assert not base<=address<base+len(payload),'Native component modified itself'
            if private(address,width)or output<=address<output+4:return
            trace.append(['w',address,width,value&((1<<(8*width))-1)])
        cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,memory_read);cpu.hook_add(UC_HOOK_MEM_WRITE,memory_write)
        cpu.emu_start(base,stop,count=200000,timeout=2000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==stop and cpu.reg_read(UC_M68K_REG_A7)==sp+4
        assert cpu.reg_read(UC_M68K_REG_D0)==0,'Native C returned an error'
        assert int.from_bytes(cpu.mem_read(output,4),'big')==expected
        assert bytes(cpu.mem_read(sp+4,8))==arguments
        for i,reg in enumerate(dispatch.world.REGS):
            if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i],(index,i)
        assert trace==oracle,(index,vector,trace,oracle)
        actual=bytes(cpu.mem_read(0,0x200000));expected_ram=bytes(model.memory)
        intervals=sorted([(base,base+len(payload)),(output,output+4),(sp-0x4000,sp+16)])
        start=0
        for lo,hi in intervals:
            assert actual[start:lo]==expected_ram[start:lo],(index,hex(start),hex(lo));start=hi
        assert actual[start:]==expected_ram[start:]
        assert actual[base:base+len(payload)]==payload
        results.append(dict(index=index,kind=vector['kind'],state=vector['state'],dt=vector['dt'],
            remainder=vector['remainder'],output=expected,instructions=instructions,C_stack_bytes=sp-minimum,
            ordered_global_accesses_match=True,callee_save_arguments_and_immutable_code_match=True))
        if index%32==0:gc.collect()
    save(out/'cases.json',results)
    sources=[Path(__file__),rp,refdir/'cases.json',refdir/'input-and-division.dylib',out/'cases.json',
        ROOT/'projects/black-ice-white-noise/restoration/biwn_input_dispatch.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_input_dispatch.h',
        ROOT/'projects/black-ice-white-noise/restoration/biwn_signed_division.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_signed_division.h',
        *[p for p in folder.iterdir()if p.is_file()],*[p for p in (folder/'build').iterdir()if p.is_file()]]
    facts=dict(status='terminal_native_input_C_ABI_walking_boundary_prototype_pass'if len(results)==425 else'terminal_native_input_partial_preflight_pass',
        directory=str(out),cases=len(results),captured_walking_cases=sum(x['kind']=='captured_walking'for x in results),
        boundary_cases=sum(x['kind']=='connected_boundary'for x in results),payload=str(folder/'build/native-input.bin'),payload_bytes=len(payload),
        C_stack_bytes=max(x['C_stack_bytes']for x in results),whole_source_dispatcher_compiled=True,
        tested_input_states=[5,7,8],all_thirteen_states_qualified=False,caller_191F4_ABI_qualified=False,
        yielding_or_IRQ_qualified=False,private_task_stack_admission_qualified=False,original_helper_fallback_executed=False,
        source_unique_functions_recovered=0,new_disc_built=False,game_image_changed=False,new_predictions=0,new_training=False,
        scope='Standalone C-ABI native68000 fixture at1C0000,not a191F4entry replacement. Existing recovered dispatcher compiled with a braces-only warning fix;direct volatile globalbus,linked source signeddivision and explicit physical helperbridge.425walking/backward/run cases compare checked source/original evidence,including194captured walking inputs. No original helper instructions execute in these cases;other states,originalcaller ABI,IRQ/yield and task-stack limits remain unqualified. No gameimage/default promotion.',
        source_sha256={str(p):sha(p)for p in sources})
    save(out/'review.json',facts);save(V/('native-input-prototype-v1-current.json'if len(results)==425 else'native-input-prototype-v1-preflight-current.json'),facts)
    print(facts['status'],len(results),'cases',len(payload),'bytes','stack',facts['C_stack_bytes'],flush=True)


if __name__=='__main__':main()

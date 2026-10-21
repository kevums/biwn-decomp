"""All-state native component versus original instructions and recovered C.

E588 executes original instructions in the reference and source C in the
native component. Other helpers use explicit scripted dependencies. Capture
their incoming D0 as a separate gate,which the older output-only tests lacked.
"""
import argparse,ctypes as c,gc,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as dispatch
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    rp=V/'native-input-prototype-v1-current.json';prototype=read(rp)
    for path,digest in prototype['source_sha256'].items():assert sha(path)==digest,path
    connected=read(V/'input-timing-connected-v1-current.json')
    folder=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/input-dispatch-native-v2'
    source_info=read(folder/'source-provenance.json');assert sha(source_info['original_source'])==source_info['original_sha256']
    corrected=Path(source_info['original_source']).read_text()
    for change in source_info['changes']:
        assert corrected.count(change['before'])==change['occurrences'];corrected=corrected.replace(change['before'],change['after'])
    assert corrected==(folder/'input-source.c').read_text()
    payload_path=folder/'build-portable/native-input.bin';payload=payload_path.read_bytes();base=0x1c0000;sp=0x1ff000;stop=0x3000;output=0x1ee000
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=dispatch.cases(snapshot)
    for original_case in read(Path(connected['directory'])/'cases.json'):
        vector=original_case['vector']
        vectors.append(dict(kind=vector['kind'],state=vector['state'],held=vector['held'],incoming=[0x13579bdf]*len(dispatch.world.REGS),
            initial=[[0x4624a,2,0],[0x49d62,2,0],[0x49c4e,2,0],[0x49cb8,2,vector['state']],
                [0x49ba4,4,vector['held']],[0x4c24c,4,vector['dt']],[0x49cc8,4,vector['remainder']]],
            helper_returns={str(a):0 for a in dispatch.HELPERS},default_helper_return=0,
            checked_speed=original_case['original_and_C_speed'],checked_remainder=original_case['original_and_C_remainder']))
    assert len(vectors)==2315
    if args.limit:vectors=vectors[:args.limit]
    out=V/'native-input-all-states-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    host_path=out/'corrected-host-input.dylib';restoration=folder.parent.parent
    q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(folder/'input-source.c'),str(restoration/'biwn_signed_division.c'),'-o',str(host_path)],capture_output=True,text=True)
    (out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    host=c.CDLL(str(host_path));fn=host.biwn_input_dispatch
    fn.argtypes=[c.POINTER(dispatch.world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    divide=host.biwn_signed_division;divide.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];divide.restype=c.c_int
    pointer=V/('native-input-all-states-v3-preflight-current.json'if args.limit else'native-input-all-states-v3-current.json')
    state=dict(status='running_native_input_all_state_components',directory=str(out),pid=os.getpid(),case_count=len(vectors),completed=0,
        new_predictions=0,new_training=False,game_image_changed=False)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    class Script(dispatch.Script):
        def __init__(self,case):super().__init__(snapshot,case);self.seeds=[]
        def call(self,address,params):
            if address!=0xe588:return super().call(address,params)
            self.trace.append(['call',address,params]);q=c.c_uint32();r=c.c_uint32()
            assert len(params)==2 and divide(*params,c.byref(q),c.byref(r))==0
            return q.value
    def host_run(script,case):
        def reader(width):
            def cb(_,a,v):v[0]=script.read(a,width);return 0
            return cb
        def writer(width):
            def cb(_,a,v):script.write(a,width,v);return 0
            return cb
        def call(_,address,params,count,result):
            if address!=0xe588:script.seeds.append([address,int(result[0])])
            result[0]=script.call(address,list(params[:count]));return 0
        w=dispatch.world
        callbacks=[w.R8(reader(1)),w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),w.CALL(call),dispatch.W8(writer(1))]
        bus=w.Bus(*callbacks[:6],None,0);result=c.c_uint32(0xa55aa55a)
        status=fn(c.byref(bus),callbacks[6],64,case['incoming'][0],c.byref(result));assert status==0,(status,case)
        return result.value
    def cpu_run(script,case,native):
        cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000)
        cpu.mem_write(0,bytes(script.memory));stubs=[a for a in dispatch.HELPERS if a!=0xe588]
        for address in stubs:cpu.mem_write(address,b'\x4e\x75')
        if native:
            cpu.mem_write(base,payload);argbytes=case['incoming'][0].to_bytes(4,'big')+output.to_bytes(4,'big')
            cpu.mem_write(output,b'\xa5\x5a\xa5\x5a')
        else:argbytes=b''
        cpu.mem_write(sp,stop.to_bytes(4,'big')+argbytes)
        for reg,value in zip(dispatch.world.REGS,case['incoming']):cpu.reg_write(reg,value)
        cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,sp)
        minimum=sp;instructions=0;helper_targets=[]
        def private(address,width):return sp-0x4000<=address and address+width<=sp+16
        def code(engine,address,width,user):
            nonlocal minimum,instructions
            minimum=min(minimum,engine.reg_read(UC_M68K_REG_A7));instructions+=1
            if address in dispatch.HELPERS:
                assert address!=0xe588 or not native,'Linked native division unexpectedly left component'
                stack=engine.reg_read(UC_M68K_REG_A7);offset=4;params=[]
                for width in dispatch.WIDTHS.get(address,[]):
                    params.append(int.from_bytes(engine.mem_read(stack+offset,width),'big'));offset+=width
                if address==0xe588:
                    script.trace.append(['call',address,params]);return
                script.seeds.append([address,engine.reg_read(UC_M68K_REG_D0)]);helper_targets.append(address)
                script.changed=[];result=script.call(address,params)
                for a,w,v in script.changed:engine.mem_write(a,v.to_bytes(w,'big'))
                engine.reg_write(UC_M68K_REG_D0,result)
                if native:
                    # A C-ABI bridge may not depend on volatile registers surviving.
                    for reg in [UC_M68K_REG_D1,UC_M68K_REG_A0,UC_M68K_REG_A1]:engine.reg_write(reg,0x13579bdf)
                return
            assert base<=address<base+len(payload)if native else(0x191f4<=address<0x19f2c or 0xe588<=address<0xe60a),hex(address)
        def memory_read(engine,access,address,width,value,user):
            if private(address,width)or(native and(base<=address<base+len(payload)or output<=address<output+4)):return
            value=script.read(address,width);engine.mem_write(address,value.to_bytes(width,'big'))
        def memory_write(engine,access,address,width,value,user):
            if native:assert not base<=address<base+len(payload),'Native code modified'
            if private(address,width)or(native and output<=address<output+4):return
            script.write(address,width,value&((1<<(8*width))-1))
        cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,memory_read);cpu.hook_add(UC_HOOK_MEM_WRITE,memory_write)
        cpu.emu_start(base if native else 0x191f4,stop,count=500000,timeout=5000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==stop and cpu.reg_read(UC_M68K_REG_A7)==sp+4
        for i,reg in enumerate(dispatch.world.REGS):
            if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i],(i,native)
        if native:
            assert cpu.reg_read(UC_M68K_REG_D0)==0
            result=int.from_bytes(cpu.mem_read(output,4),'big');assert bytes(cpu.mem_read(sp+4,8))==argbytes
        else:result=cpu.reg_read(UC_M68K_REG_D0)
        actual=bytearray(cpu.mem_read(0,0x200000))
        for address in stubs:actual[address:address+2]=script.memory[address:address+2]
        if native:
            assert actual[base:base+len(payload)]==payload
            intervals=sorted([(base,base+len(payload)),(output,output+4),(sp-0x4000,sp+16)])
        else:intervals=[(sp-0x4000,sp+16)]
        at=0
        for lo,hi in intervals:assert actual[at:lo]==script.memory[at:lo],(native,hex(at),hex(lo));at=hi
        assert actual[at:]==script.memory[at:]
        return result,sp-minimum,instructions,helper_targets
    results=[];seed_mismatches=[];targets=set();branches=set();rng=random.Random(0x191f4)
    try:
        for index,case in enumerate(vectors):
            state['current_case']=index
            original=Script(case);model=Script(case);native=Script(case)
            a,original_stack,original_steps,_=cpu_run(original,case,False);b=host_run(model,case)
            assert a==b and original.trace==model.trace and original.memory==model.memory,('original/host',index,case)
            if 'checked_speed'in case:
                assert b==case['checked_speed'] and int.from_bytes(model.memory[0x49cc8:0x49ccc],'big')==case['checked_remainder']
            d,native_stack,native_steps,called=cpu_run(native,case,True)
            expected=[x for x in model.trace if x[:2]!=['call',0xe588]]
            assert d==b and native.trace==expected and native.memory==model.memory,('native/host',index,case,native.trace,expected)
            assert native.seeds==model.seeds,('physical bridge incomingD0',index,native.seeds,model.seeds)
            if original.seeds!=model.seeds:
                seed_mismatches.append(dict(case=index,kind=case['kind'],state=case['state'],original=original.seeds,logical_C=model.seeds))
            targets.update(called);branches.add(case['state'])
            results.append(dict(case=index,parameters=case,full_D0=d,global_trace=model.trace,
                original_steps=original_steps,native_steps=native_steps,original_stack=original_stack,native_C_ABI_stack=native_stack,
                physical_helper_D0_seeds=native.seeds,original_helper_D0_seeds=original.seeds,
                original_helper_seeds_equal=original.seeds==model.seeds,global_memory_and_trace_match=True))
            if index%32==0:
                state.update(completed=len(results),original_helper_seed_mismatch_cases=len(seed_mismatches));mark();gc.collect()
        save(out/'cases.json',results);save(out/'dependency-seed-mismatches.json',seed_mismatches)
        complete=not args.limit
        status=('terminal_all_state_component_fixtures_pass_dependency_seed_gate_failed'if seed_mismatches else'terminal_all_state_component_fixtures_and_dependency_D0_seeds_pass')if complete else'terminal_partial_all_state_preflight_pass'
        state.update(status=status,completed=len(results),tested_input_states=sorted(branches),
            native_component_unchanged=False,payload_bytes=len(payload),payload_sha256=sha(payload_path),payload=str(payload_path),source_directory=str(folder),source_equipment_D0_seed_correction=True,
            original_helpers_scripted_except_real_E588=True,physical_helper_targets=[hex(a)for a in sorted(targets)],
            physical_bridge_seed_argument_and_volatile_register_controls_pass=True,
            original_helper_D0_seed_match=not seed_mismatches,original_helper_seed_mismatch_cases=len(seed_mismatches),
            native_C_ABI_stack_bytes=max(x['native_C_ABI_stack']for x in results),
            all_thirteen_state_fixture_paths_verified=set(range(13)).issubset(branches)and complete,
            original_191F4_caller_ABI_qualified=False,yield_IRQ_qualified=False,physical_helper_bodies_qualified=False,
            scope='Original191F4andE588instructions versus host C and corrected nativeinputcomponent. Otherhelpers use scriptedRTSdependencies. Nativebridge stackarguments/D0seeds checked and D1/A0/A1clobbered at retainedhelperreturns. OriginalhelperentryD0seeds separately compared withlogicalC;any mismatch staysfailed,not waived by matching outputunder scripted helpers. C-ABI fixture only;not originalcaller/yield/taskstack/gameimagequalification.',
            source_sha256={str(p):sha(p)for p in [Path(__file__),rp,payload_path,*[p for p in folder.iterdir()if p.is_file()],*[p for p in (folder/'build-portable').iterdir()if p.is_file()],out/'cases.json',out/'dependency-seed-mismatches.json',
                ROOT/'scripts/check_biwn_input_dispatch.py',ROOT/'render-assets/biwn-inventory-baseline.bin',host_path,ROOT/'projects/black-ice-white-noise/restoration/biwn_input_dispatch_cpu.c']});mark()
        print(status,len(results),'cases',len(seed_mismatches),'seed mismatches','stack',state['native_C_ABI_stack_bytes'],flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',results)
        save(out/'failure-case.json',dict(case=state.get('current_case'),parameters=vectors[state.get('current_case',0)],error=repr(error)))
        state.update(status='terminal_all_state_component_failed',completed=len(results),error=repr(error));mark();raise


if __name__=='__main__':main()

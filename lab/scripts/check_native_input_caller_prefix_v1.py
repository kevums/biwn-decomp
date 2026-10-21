"""Actual caller1A266..1A340,including real E220/E098 CPU instructions.

The synchronous device only acknowledges4320;GPU arithmetic is not tested.
Other input helpers retain explicit scripted bodies. Compare full public
memory/accesses and the caller's integration state,while retaining raw
unused-register differences as evidence rather than declaring full ABI.
"""
import gc,os
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as dispatch
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    ep=V/'native-input-entry-ABI-v2-current.json';gate=read(ep)
    assert gate['completed']==4630 and gate['component_prefix_byte_identical']
    for path,digest in gate['source_sha256'].items():assert sha(path)==digest,path
    cases=read(Path(gate['directory'])/'cases.json');payload_path=Path(gate['payload']);payload=payload_path.read_bytes()
    base=0x1c0000;entry=gate['entry_address'];sp=0x1ff000;alternate=0x1ef400;start=0x1a266;stop=0x1a340
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();patch=b'\x4e\xb9'+entry.to_bytes(4,'big')
    assert snapshot[start:start+6]==b'\x4e\xb9\x00\x01\x91\xf4'
    out=V/'native-input-caller-prefix-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'native-input-caller-prefix-v1-current.json'
    state=dict(status='running_original_caller_prefix_comparison',directory=str(out),pid=os.getpid(),completed=0,
        new_predictions=0,new_training=False,game_image_changed=False)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    def execute(case,native,index):
        script=dispatch.Script(snapshot,case);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(script.memory))
        stubs=[a for a in dispatch.HELPERS if a!=0xe588]
        for a in stubs:cpu.mem_write(a,b'\x4e\x75')
        if native:cpu.mem_write(base,payload);cpu.mem_write(start,patch)
        for reg,value in zip(dispatch.world.REGS,case['incoming']):cpu.reg_write(reg,value)
        sr=case['test_SR'];cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,sp if sr&0x2000 else alternate)
        cpu.reg_write(UC_M68K_REG_SR,0);cpu.reg_write(UC_M68K_REG_A7,alternate if sr&0x2000 else sp);cpu.reg_write(UC_M68K_REG_SR,sr)
        minimum=sp;instructions=0;input_return=None;matrix_args=[];mailbox={};busy_reads=0;ack_reads=0;latency=index%3
        def private(a,w):return sp-0x4000<=a and a+w<=sp+64
        def code(engine,pc,width,user):
            nonlocal minimum,instructions,input_return
            minimum=min(minimum,engine.reg_read(UC_M68K_REG_A7));instructions+=1
            if pc==0x1a26c:
                assert input_return is None
                assert engine.reg_read(UC_M68K_REG_A7)==sp
                for i,reg in enumerate(dispatch.world.REGS):
                    if i not in[0,1,8,9]:assert engine.reg_read(reg)==case['incoming'][i]
                input_return=dict(D0=engine.reg_read(UC_M68K_REG_D0),SR=engine.reg_read(UC_M68K_REG_SR))
            if pc==0xe220:
                a7=engine.reg_read(UC_M68K_REG_A7)
                matrix_args.append([int.from_bytes(engine.mem_read(a7+4+i*4,4),'big')for i in range(5)])
            if pc in dispatch.HELPERS:
                assert pc!=0xe588 or not native
                a7=engine.reg_read(UC_M68K_REG_A7);offset=4;args=[]
                for w in dispatch.WIDTHS.get(pc,[]):args.append(int.from_bytes(engine.mem_read(a7+offset,w),'big'));offset+=w
                if pc==0xe588:script.trace.append(['call',pc,args]);return
                script.changed=[];value=script.call(pc,args)
                for a,w,v in script.changed:engine.mem_write(a,v.to_bytes(w,'big'))
                engine.reg_write(UC_M68K_REG_D0,value)
                if native:
                    for reg in [UC_M68K_REG_D1,UC_M68K_REG_A0,UC_M68K_REG_A1]:engine.reg_write(reg,0x13579bdf)
                return
            assert(start<=pc<stop or 0xe220<=pc<0xe26c or 0xe098<=pc<0xe0a6
                   or(base<=pc<base+len(payload)if native else 0x191f4<=pc<0x19f2c or 0xe588<=pc<0xe60a)),hex(pc)
            assert pc!=entry+22,'Entry adapter rejected the source call'
        def memory_read(engine,access,a,w,value,user):
            nonlocal busy_reads,ack_reads
            if private(a,w)or(native and base<=a<base+len(payload)):return
            if a>=0xf02000:
                assert w==4 and a in [0xf03200,0xf03204],hex(a)
                if a==0xf03200:value=int(busy_reads<latency);busy_reads+=1
                else:value=0x4320 if ack_reads<latency else 0xffffffff;ack_reads+=1
                script.trace.append(['r',a,w,value])
            else:value=script.read(a,w)
            engine.mem_write(a,value.to_bytes(w,'big'))
        def memory_write(engine,access,a,w,value,user):
            value&=(1<<(8*w))-1
            if native:assert not(base<=a<base+len(payload)or start<=a<start+6)
            if private(a,w):return
            if a>=0xf02000:
                assert w==4 and 0xf03204<=a<=0xf0321c
                mailbox[a]=value;script.trace.append(['w',a,w,value])
            else:script.write(a,w,value)
        cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,memory_read);cpu.hook_add(UC_HOOK_MEM_WRITE,memory_write)
        cpu.emu_start(start,stop,count=500000,timeout=5000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==stop and cpu.reg_read(UC_M68K_REG_A7)==sp
        assert input_return is not None and len(matrix_args)==1 and mailbox[0xf03204]==0x4320
        final_SR=cpu.reg_read(UC_M68K_REG_SR);assert final_SR&0xffe0==sr&0xffe0
        regs=[cpu.reg_read(reg)for reg in dispatch.world.REGS]
        cpu.reg_write(UC_M68K_REG_SR,final_SR^0x2000);assert cpu.reg_read(UC_M68K_REG_A7)==alternate
        cpu.reg_write(UC_M68K_REG_SR,final_SR)
        memory=bytearray(cpu.mem_read(0,0x200000));frame=bytes(memory[sp:sp+64]);args_frame=bytes(memory[sp-24:sp])
        for a in stubs:memory[a:a+2]=script.memory[a:a+2]
        intervals=[(sp-0x4000,sp+64)]
        if native:
            assert memory[base:base+len(payload)]==payload and memory[start:start+6]==patch
            assert memory[0x191f4:0x191fe]==snapshot[0x191f4:0x191fe]
            memory[start:start+6]=script.memory[start:start+6];intervals.append((base,base+len(payload)))
        at=0
        for lo,hi in sorted(intervals):assert memory[at:lo]==script.memory[at:lo];at=hi
        assert memory[at:]==script.memory[at:]
        return dict(script=script,registers=regs,SR=final_SR,frame=frame,args_frame=args_frame,
                    matrix_args=matrix_args,mailbox=mailbox,input_return=input_return,instructions=instructions,stack=sp-minimum)
    rows=[];upper_D1_differences=[]
    try:
        for index,saved in enumerate(cases):
            case=saved['parameters'];state['current_case']=index
            left=execute(case,False,index);right=execute(case,True,index)
            assert left['input_return']['D0']==right['input_return']['D0']==saved['full_D0']
            expected=[x for x in left['script'].trace if x[:2]!=['call',0xe588]]
            assert expected==right['script'].trace and left['script'].memory==right['script'].memory
            assert left['frame']==right['frame']and left['args_frame']==right['args_frame']
            assert left['matrix_args']==right['matrix_args']and left['mailbox']==right['mailbox']
            assert left['SR']==right['SR'],'Caller integration still depends on different return flags'
            differences=[i for i,(a,b)in enumerate(zip(left['registers'],right['registers']))if a!=b]
            assert set(differences).issubset({1})
            assert left['registers'][1]&0xffff==right['registers'][1]&0xffff
            if differences:upper_D1_differences.append(dict(case=index,original_D1=left['registers'][1],native_D1=right['registers'][1]))
            rows.append(dict(case=index,input_state=case['state'],initial_SR=case['test_SR'],
                caller_required_state_public_RAM_bus_args_flags_match=True,raw_D1_upper_differs=bool(differences),
                matrix_args=left['matrix_args'],native_stack=right['stack'],original_stack=left['stack']))
            if index%32==0:state['completed']=len(rows);mark();gc.collect()
        save(out/'cases.json',rows);save(out/'remaining-raw-D1-differences.json',upper_D1_differences)
        state.update(status='terminal_caller_prefix_public_state_flags_and_mailbox_match_raw_D1_upper_differs',completed=len(rows),
            caller_start=start,caller_stop=stop,native_stack_bytes=max(x['native_stack']for x in rows),
            whole_public_RAM_and_ordered_accesses_equal=True,caller_local_frame_and_matrix_stack_args_equal=True,
            actual_E220_and_E098_CPU_instructions_executed=True,GPU_provider='Synchronous acknowledgment only;noGPUarithmetic/result fidelity claim.',
            final_SR_equal_all_cases=True,other_fifteen_registers_equal=True,raw_D1_upper_differing_cases=len(upper_D1_differences),
            raw_D1_low_word_equal=True,universal_original_input_ABI_qualified=False,full_caller_or_real_helper_bodies_qualified=False,
            task_stack_admission_qualified=False,yield_IRQ_qualified=False,
            scope='Callsite-specific JSRoperand intervention only at1A266;original191F4globalentryunchanged. Original caller instructions through1A340and originalE220/E098execute. Mailboxprovideracknowledges4320with0..2busyreads;GPUmathisnotunder test. ScriptedinputhelpersincludingDF60remainRTSproviders. PublicRAM/accesses,callerframe,matrixarguments,flags and allregs exceptunused upperD1agree afterplayerintegration. RawupperD1differencesremainrecorded;no fullcaller,universalABI,yield/IRQ,image or hardwareclaim.',
            source_sha256={str(p):sha(p)for p in [Path(__file__),ep,payload_path,Path(gate['directory'])/'cases.json',
                out/'cases.json',out/'remaining-raw-D1-differences.json',ROOT/'render-assets/biwn-inventory-baseline.bin']});mark()
        print(state['status'],len(rows),'cases;raw upperD1 differences',len(upper_D1_differences),flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);save(out/'failure-case.json',dict(case=state.get('current_case'),parameters=cases[state.get('current_case',0)]['parameters'],error=repr(error)))
        state.update(status='terminal_caller_prefix_failed',completed=len(rows),error=repr(error));mark();raise


if __name__=='__main__':main()

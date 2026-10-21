"""Two actual1024-byte tasks;original DF60/TRAP/DE08/RTE/DF66 execute.

Only animation/resource helpers are scripted. A second real task clobbers
callee-saved registers and completes the first task's animation after N turns.
This is a bounded scheduler/stack fixture,not a fresh game or IRQ proof.
"""
import json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    ep=V/'native-input-entry-ABI-v2-current.json';entry_proof=read(ep)
    assert entry_proof['completed']==4630 and entry_proof['component_prefix_byte_identical']
    for path,digest in entry_proof['source_sha256'].items():assert sha(path)==digest,path
    payload_path=Path(entry_proof['payload']);payload=payload_path.read_bytes();native_entry=entry_proof['entry_address'];base=0x1c0000
    out=V/'native-input-real-task-yield-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'native-input-real-task-yield-v2-current.json'
    state=dict(status='building_two_task_yield_fixture',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,new_game_image=False)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    asm=out/'task-B.S';asm.write_text('''.section .text,"ax",@progbits
.globl task_B
task_B:
addq.l #1,0x7000
move.l 0x7000,%d0
cmp.l 0x7004,%d0
bne.s 1f
move.b #1,0x90002
1:
move.l #0x22222222,%d2
move.l #0x33333333,%d3
move.l #0x44444444,%d4
move.l #0x55555555,%d5
move.l #0x66666666,%d6
move.l #0x77777777,%d7
move.l #0xa2a2a2a2,%a2
move.l #0xa3a3a3a3,%a3
move.l #0xa4a4a4a4,%a4
move.l #0xa5a5a5a5,%a5
move.l #0xa6a6a6a6,%a6
jsr 0xdf60
bra.w task_B
''')
    linker=out/'task-B.ld';linker.write_text('ENTRY(task_B)\nSECTIONS {\n . = 0x6200;\n .text : { *(.text*) }\n /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }\n}\n')
    cross=ROOT/'tools/m68k-elf/bin/m68k-elf-';commands=[
        [str(cross)+'as','-m68000',str(asm),'-o',str(out/'task-B.o')],
        [str(cross)+'ld','-T',str(linker),str(out/'task-B.o'),'-o',str(out/'task-B.elf')],
        [str(cross)+'objcopy','-O','binary',str(out/'task-B.elf'),str(out/'task-B.bin')]]
    for number,cmd in enumerate(commands):
        q=subprocess.run(cmd,capture_output=True,text=True);(out/('build-'+str(number)+'.log')).write_text(q.stdout+q.stderr)
        if q.returncode:state.update(status='terminal_two_task_fixture_build_failed',error=q.stderr);mark();raise AssertionError(q.stderr)
    task_code=(out/'task-B.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    A=0xc0928;B=A+1024;STOP=0x6000;SSP=0x1e0000;task_top=A+1024;userdata=0x7000
    MOCKS={0xeb04:[],0x1b002:[2],0x1af04:[2],0x1545c:[4],0x152a2:[4]}
    runtime=scheduler.Native();core=runtime.lib;device=runtime.device
    def execute(native,turns,flags):
        memory=bytearray(snapshot)
        def put(a,w,v):memory[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
        for node in [A,B]:memory[node:node+1024]=bytes([0xa5])*1024
        for node,other,pc in [(A,B,native_entry if native else 0x191f4),(B,A,0x6200)]:
            for off,w,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,node+1020),(16,4,pc),(20,2,flags),
                                (22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(node+off,w,value)
        initial=[(0x80,4,0xde08),(0xc0920,4,A),(0xc0924,4,0),(0x778cc,4,10),
            (0x7000,4,0),(0x7004,4,turns),(0x4624a,2,0),(0x49d62,2,0),(0x49c4e,2,0),
            (0x49cb8,2,1),(0x49c60,2,0),(0x49ba4,4,0x02002000),(0x49c4c,2,0),(0x49d5a,2,1),
            (0x49cb0,4,0x90000),(0x49cb4,4,0x90000),(0x90002,1,0),(0x45dbc,4,0x90000),
            (0x45d9a,2,7),(0x45d9c,2,23),(0x49ca4,4,0x91000),(0x91000,4,0x92000),(0x92008,4,128),
            (0x49caa,4,0x93000),(0x93000,4,0x94000),(A+1020,4,STOP)]
        for a,w,v in initial:put(a,w,v)
        memory[0x6200:0x6200+len(task_code)]=task_code
        for address in MOCKS:put(address,2,0x4e75)
        if native:memory[base:base+len(payload)]=payload
        memory[SSP-256:SSP]=bytes([0x5a])*256
        device.seed(bytes(memory),0);core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,SSP);core.m68k_set_reg(17,flags);core.m68k_set_reg(15,A+1020)
        incoming=[random.Random(0x191f4+i).getrandbits(32)for i in range(15)]
        for i,value in enumerate(incoming):core.m68k_set_reg(i,value)
        core.m68k_set_reg(16,native_entry if native else 0x191f4)
        minimum={A:A+1024,B:B+1024};yields=[];switches=[];helpers=[];last=A;super_low=SSP
        for step in range(500000):
            pc=core.m68k_get_reg(None,16)
            if pc==STOP:break
            sr=core.m68k_get_reg(None,17);sp=core.m68k_get_reg(None,15);active=device.read(0xc0920,4)
            assert active in [A,B],('invalid task',hex(active),hex(pc))
            if not sr&0x2000:
                assert active+64<=sp<=active+1024,('task stack bound',hex(active),hex(pc),sp-active)
                minimum[active]=min(minimum[active],sp)
            else:
                assert SSP-128<=sp<=SSP;super_low=min(super_low,sp)
                assert 0xde08<=pc<0xde5c,('unexpected supervisor code',hex(pc))
            if active!=last:switches.append([last,active,pc]);last=active
            if pc==0xdf60:yields.append(dict(task=active,D0=core.m68k_get_reg(None,0),SR=sr,SP=sp))
            if pc in MOCKS:
                args=[];offset=4
                for width in MOCKS[pc]:args.append(device.read(sp+offset,width));offset+=width
                if pc==0xeb04:args=[device.read(sp+4,4)]
                helpers.append(dict(target=pc,args=args,D0=core.m68k_get_reg(None,0),task=active))
                assert active==A
                value={0xeb04:0x12345678,0x1b002:0x11112222,0x1af04:0x91000,0x1545c:0x44445555,0x152a2:0x93000}[pc]
                core.m68k_set_reg(0,value)
            else:
                assert(0x191f4<=pc<0x19f2c if not native else base<=pc<base+len(payload))or(0x6200<=pc<0x6200+len(task_code))or 0xdf60<=pc<0xdf6c or 0xde08<=pc<0xde5c,hex(pc)
            core.m68k_execute(1)
        else:raise AssertionError('Two task execution instruction limit')
        final=device.ram();cpu=runtime.prefix
        assert core.m68k_get_reg(None,15)==A+1024 and not core.m68k_get_reg(None,17)&0x2000
        assert core.m68k_get_reg(None,0)==0x93000
        for i,value in enumerate(incoming):
            if i not in [0,1,8,9]:assert core.m68k_get_reg(None,i)==value,(i,hex(core.m68k_get_reg(None,i)),hex(value))
        u=lambda a,w=4:int.from_bytes(final[a:a+w],'big')
        assert u(0xc0920)==A and u(0x7000)==turns and u(0x90002,1)==1
        assert len(yields)==len(switches)==turns*2
        assert u(0x49d5a,2)==0 and u(0x49ca4)==0x91000 and u(0x49caa)==0x93000 and u(0x94000)==0x2c000
        for node in [A,B]:assert final[node+38:node+64]==memory[node+38:node+64]
        assert final[SSP-256:SSP-128]==memory[SSP-256:SSP-128]
        assert cpu[17]==SSP and core.m68k_get_reg(None,15)==A+1024
        if native:assert final[base:base+len(payload)]==payload
        return dict(memory=final,helpers=helpers,yields=yields,switches=switches,
            task_A_stack_used=A+1024-minimum[A],task_B_stack_used=B+1024-minimum[B],supervisor_stack_used=SSP-super_low,
            final_D0=core.m68k_get_reg(None,0),final_SR=core.m68k_get_reg(None,17),steps=step)
    rows=[]
    try:
        for turns in [1,2,3,7]:
            for flags in [0,0x1f,0x700,0x71f]:
                state['current_case']=[turns,flags];left=execute(False,turns,flags);right=execute(True,turns,flags)
                assert left['helpers']==right['helpers'],'Retained helper args/D0 differ after real scheduling'
                assert [x['task']for x in left['yields']]==[x['task']for x in right['yields']]
                assert [x['D0']for x in left['yields']]==[x['D0']for x in right['yields']]
                assert left['memory'][B:B+1024]==right['memory'][B:B+1024],'Second task context diverged'
                # Only documented first-task continuation/frame bytes and the
                # supervisor exception scratch differ with the native C stack.
                intervals=sorted([(A,A+1024),(SSP-128,SSP),(base,base+len(payload))]);at=0
                for lo,hi in intervals:assert left['memory'][at:lo]==right['memory'][at:lo],(turns,flags,hex(at),hex(lo));at=hi
                assert left['memory'][at:]==right['memory'][at:]
                rows.append(dict(turns=turns,initial_SR=flags,original_task_A_stack=left['task_A_stack_used'],
                    native_task_A_stack=right['task_A_stack_used'],task_B_stack=right['task_B_stack_used'],
                    supervisor_stack=right['supervisor_stack_used'],actual_yields=len(right['yields']),actual_switches=len(right['switches']),
                    helper_args_D0_and_second_task_context_match=True,task_header_fences_and_native_code_immutable=True,
                    first_task_saved_SR_equal=left['memory'][A+20:A+22]==right['memory'][A+20:A+22]))
                state['completed']=len(rows);mark()
        save(out/'cases.json',rows)
        state.update(status='terminal_two_original_tasks_TRAP_RTE_native_input_resumes_stack_fences_pass',completed=len(rows),
            maximum_native_task_stack=max(x['native_task_A_stack']for x in rows),maximum_B_task_stack=max(x['task_B_stack']for x in rows),
            maximum_supervisor_stack=max(x['supervisor_stack']for x in rows),actual_switches=sum(x['actual_switches']for x in rows),
            original_DF60_TRAP_DE08_RTE_DF66_executed=True,second_task_clobbers_D2_D7_A2_A6=True,
            native_callee_saved_locals_survive=True,actual_task_bytes=1024,guarded_task_stack_capacity=960,
            raw_first_task_saved_context_equal=False,arbitrary_IRQ_or_all_task_paths_qualified=False,
            scope='Sixteenpaired two-task fixtures:original DF60/TRAP/DE08/RTE/DF66execute. TaskBchanges animation flag after1/2/3/7turns andclobbers allcallee-save registers. NativeinputCframe resumes correctly,helperargs/D0/publiceffects match,and secondtask all1024bytesmatch. Firsttaskprivatecontext/frame andsupervisor exception scratch intentionallylayout-dependent and excludedfrom cross-laneRAMequality;theirbounds/fencesseparatelychecked. Animation/resourcehelpersscripted;no realhelperbody,arbitraryIRQ,freshgame or imagequalification.',
            source_sha256={str(p):sha(p)for p in [Path(__file__),ep,payload_path,asm,linker,out/'task-B.bin',out/'cases.json',
                ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']});mark()
        print(state['status'],len(rows),'pairs','native task stack',state['maximum_native_task_stack'],'switches',state['actual_switches'],flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);state.update(status='terminal_two_task_yield_fixture_failed',error=repr(error));mark();raise
    finally:runtime.close()


if __name__=='__main__':main()

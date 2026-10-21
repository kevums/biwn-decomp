"""Actual resource wait/signal/TRAP/RTE and another task's GPU scratch use.

Reference uses the inherited512-gap compiled acquire adapter; candidate uses
the new per-task arena adapter. Both run the same compiled acquire C body,
actual image scheduler and original semaphore instructions. Task programs and
resource readiness are explicit fixtures. GPU4320 is synchronous, IRQ disabled.
This is actual v39 image addresses, not full input/gameplay, same-task nesting or arbitrary IRQ proof.
"""
import ctypes as c
import hashlib
import os
import random
import struct
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    ap=V/'acquire-arena-prototype-v1-current.json';arena=read(ap)
    vp=V/'native-input-arena-admission-v6-current.json';v6=read(vp)
    bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp)
    startup_path=V/'native-input-arena-image-startup-heap-v1-current.json';startup=read(startup_path)
    assert startup['native_startup_cases']==startup['Unicorn_startup_cases']==6 and startup['heap_initialize_cases']==192
    for receipt in [arena,v6,b]:
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    out=V/'resource-input-observer-actual-wait-CPU-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    observer_path=V/'resource-input-arena-observer-qualified-v1-current.json';observer_proof=read(observer_path)
    for path,digest in observer_proof['source_sha256'].items():assert sha(path)==digest,path
    observer=c.CDLL(observer_proof['library']);observer.fixture_live.argtypes=[c.c_void_p,c.POINTER(scheduler.CPU),c.c_uint32]
    observer.fixture_stat.argtypes=[c.c_uint];observer.fixture_stat.restype=c.c_uint64
    pointer=V/'resource-input-observer-actual-wait-CPU-v1-current.json'
    state=dict(status='building_real_wait_two_task_fixture',pid=os.getpid(),directory=str(out),completed=0,new_predictions=0,optimizer_updates=0,new_disc_built=False,game_frames=0)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();print(out,flush=True)
    source=out/'tasks.S'
    source.write_text('''.text
.globl task_A
task_A:
move.w #0,-(%sp)
jsr 0x1af04
addq.l #2,%sp
rts
.org 0x100
.globl task_B
task_B:
addq.l #1,0x7000
pea 1
clr.l -(%sp)
pea 64
clr.l -(%sp)
pea 0x98000
jsr 0xe220
lea 20(%sp),%sp
move.l 0x7000,%d0
cmp.l 0x7004,%d0
bne.s 1f
move.w #1,0x15b53c
1:
pea 1
jsr 0xdf9c
addq.l #4,%sp
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
    linker=out/'tasks.ld';linker.write_text('SECTIONS { .text 0x6100 : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
    tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    commands=[[tool+'as','-m68000','-o',str(out/'tasks.o'),str(source)],[tool+'ld','-T',str(linker),'-o',str(out/'tasks.elf'),str(out/'tasks.o')],[tool+'objcopy','-O','binary',str(out/'tasks.elf'),str(out/'tasks.bin')]]
    for command in commands:subprocess.run(command,check=True,capture_output=True)
    code=(out/'tasks.bin').read_bytes()
    named=subprocess.check_output([tool+'nm','-n',str(out/'tasks.elf')],text=True)
    assert '00006100 T task_A' in named and '00006200 T task_B' in named
    aux=Path(b['resource_arena_payload']).read_bytes();aux_base=b['resource_arena_code_address'];input_code=Path(v6['payload']).read_bytes()
    original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();stage=Path(b['derived_stage']).read_bytes()
    new_resident=Path(b['component']).read_bytes();old_resident=bytearray(new_resident)
    for patch in b['resource_arena_entry_patches']:
        at=patch['entry']-b['resident_address'];assert old_resident[at:at+6]==bytes.fromhex(patch['replacement']);old_resident[at:at+6]=bytes.fromhex(patch['original'])
    old_resident=bytes(old_resident)
    SSP=0x1d0000;STOP=0x6000;POOL=0xc0928
    runtime=scheduler.Native();core=runtime.lib;device=runtime.device
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32

    def execute(changed,turns,flags,index_A):
        A=POOL+index_A*1024;index_B=1 if index_A==0 else 0;B=POOL+index_B*1024
        slot_A=b['arena_address']+index_A*256;slot_B=b['arena_address']+index_B*256
        memory=bytearray(original);memory[0x4000:0x100000]=stage
        resident=new_resident # Both lanes run identical v39 code; changed enables observation.
        memory[b['resident_address']:b['heap_start']]=resident
        memory[v6['base']:v6['base']+len(input_code)]=input_code
        memory[aux_base:aux_base+len(aux)]=aux;memory[0x6100:0x6100+len(code)]=code
        memory[b['arena_address']:b['arena_end']]=bytes([0xa5])*(b['arena_end']-b['arena_address'])
        for node in [A,B]:memory[node:node+1024]=bytes([0xa5])*1024
        def put(address,width,value):memory[address:address+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        for node,other,pc in [(A,B,0x6100),(B,A,0x6200)]:
            for off,width,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,node+1020),(16,4,pc),(20,2,flags),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(node+off,width,value)
        for address,value in [(0x80,0xde08),(0x90,0xdef6),(0xc0920,A),(0xc0924,0),(0x778cc,10),(0x7000,0),(0x7004,turns),(A+1020,STOP),(0x464d0,0x123456),(0x464d4,0x4d455350),(0x464d8,0x200),(0x15b536,0x91000),(0x91000,0xa0000)]:put(address,4,value)
        for address,value in [(0x15b534,0),(0x15b53a,2),(0x15b53c,0)]:put(address,2,value)
        memory[0x98000:0x98020]=bytes(32);memory[SSP-256:SSP]=bytes([0x5a])*256
        device.seed(bytes(memory),0);core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,SSP);core.m68k_set_reg(17,flags);core.m68k_set_reg(15,A+1020)
        incoming=[random.Random(0x1af04+i).getrandbits(32)for i in range(15)]
        for i,value in enumerate(incoming):core.m68k_set_reg(i,value)
        core.m68k_set_reg(16,0x6100)
        observer.fixture_reset();observer_calls=0;readonly_boundary_checks=0
        minimum={A:A+1024,B:B+1024};arena_min={A:240,B:240};ssp_low=SSP;last=A
        switches=[];waits=[];signals=[];yields=[];GPUs=[];parked=None;parked_checks=0;parked_resumes=0;covered=set()
        for steps in range(2000000):
            pc=core.m68k_get_reg(None,16)
            if pc==STOP:break
            sr=core.m68k_get_reg(None,17);sp=core.m68k_get_reg(None,15);active=device.read(0xc0920,4)
            assert active in [A,B],('Unexpected task',hex(pc),hex(active))
            if sr&0x2000:
                assert SSP-192<=sp<=SSP,('Supervisor stack',hex(pc),hex(sp));ssp_low=min(ssp_low,sp)
                assert 0xde08<=pc<0xdf22 or b['resident_address']<=pc<b['heap_start'],('Unexpected supervisor PC',hex(pc))
            elif b['arena_address']<=sp<b['arena_end']:
                slot=slot_A if active==A else slot_B
                assert slot+16<=sp<=slot+240,('Wrong arena owner/fence',hex(pc),hex(sp),hex(active))
                arena_min[active]=min(arena_min[active],sp-slot)
            else:
                assert active+64<=sp<=active+1024,('Guest stack fence',hex(pc),hex(sp),hex(active));minimum[active]=min(minimum[active],sp)
            if active!=last:switches.append([last,active,pc]);last=active
            if changed and parked and pc==b['resource_arena_symbols']['biwn_acquire_arena_wait_return']:
                assert active==A;assert bytes(device.ram()[parked['low']:parked['high']])==parked['bytes'];parked=None;parked_resumes+=1
            if pc==0xdf8c:
                assert active==A and device.read(sp+4,4)==1
                waits.append(dict(task=active,SP=sp,D0=core.m68k_get_reg(None,0)))
                if changed:
                    assert parked is None
                    ctx=slot_A+168;park=device.read(ctx+68,4)
                    assert slot_A+16<=park<=ctx
                    parked=dict(low=park,high=ctx+72,bytes=bytes(device.ram()[park:ctx+72]))
            if pc==0xdf9c:
                assert active==B and device.read(sp+4,4)==1;signals.append(dict(task=active,SP=sp))
            if pc==0xdf60:
                assert active==B;yields.append(dict(task=active,SP=sp))
            if pc==0xe220:
                assert active==B
                args=[device.read(sp+4+i*4,4)for i in range(5)];assert args==[0x98000,0,64,0,1];GPUs.append(args)
            allowed=(0x6100<=pc<0x610e or 0x6200<=pc<0x6100+len(code) or 0x1af04<=pc<0x1b002 or 0xde08<=pc<0xde5c or 0xdef6<=pc<0xdf22 or 0xdf60<=pc<0xdf6c or 0xdf8c<=pc<0xdfa6 or 0xe220<=pc<0xe26c or 0xe098<=pc<0xe0a6 or b['resident_address']<=pc<b['heap_start'] or changed and aux_base<=pc<aux_base+len(aux))
            assert allowed,hex(pc);covered.add(pc)
            if changed:
                captured=scheduler.CPU();captured.registers[:]=[core.m68k_get_reg(None,i)for i in range(16)];captured.pc=pc;captured.sr=sr;captured.usp=runtime.prefix[16]if sr&0x2000 else sp;captured.ssp=sp if sr&0x2000 else runtime.prefix[17]
                before_CPU=bytes(captured)
                boundary=pc in [0x1af04,0xdf8c,0xdf9c,0xe220,symbols_for_observer['biwn_acquire_arena_entry'],symbols_for_observer['biwn_acquire_arena_return']]
                before_RAM=device.ram()if boundary else None
                observer.fixture_live(device.pointer,c.byref(captured),pc)
                after=scheduler.CPU();after.registers[:]=[core.m68k_get_reg(None,i)for i in range(16)];after.pc=core.m68k_get_reg(None,16);after.sr=core.m68k_get_reg(None,17);after.usp=runtime.prefix[16]if sr&0x2000 else after.registers[15];after.ssp=after.registers[15]if sr&0x2000 else runtime.prefix[17]
                assert bytes(after)==before_CPU,'Observer changed actual CPU'
                if boundary:assert device.ram()==before_RAM;readonly_boundary_checks+=1
                observer_calls+=1
            core.m68k_execute(1)
            if core.GPUReadLong(0xf03204,0)==0x4320:device.write(0xf03204,0x4320)
            if changed and parked:
                raw=device.ram();assert raw[parked['low']:parked['high']]==parked['bytes'],('Parked acquire state corrupted while another task runs',hex(pc),hex(active));parked_checks+=1
        else:raise AssertionError('Real wait tasks instruction bound')
        final=device.ram();registers=[core.m68k_get_reg(None,i)for i in range(16)];sr=core.m68k_get_reg(None,17)
        assert registers[15]==A+1024 and registers[0]==0x91000 and not sr&0x2000
        for i in [2,3,4,5,6,7,10,11,12,13,14]:assert registers[i]==incoming[i],i
        assert runtime.prefix[17]==SSP and device.read(0xc0920,4)==A
        assert device.read(0x7000,4)==turns and device.read(0x15b53c,2)==1 and device.read(0x15b53a,2)==3
        assert device.read(A+26,4)==device.read(B+26,4)==0
        assert len(waits)==len(signals)==len(yields)==len(GPUs)==turns
        assert len(switches)==turns*2 and parked is None
        assert not changed or parked_resumes==turns
        assert final[SSP-256:SSP-192]==memory[SSP-256:SSP-192]
        for node in [A,B]:assert final[node+38:node+64]==memory[node+38:node+64]
        for index in range(102):
            at=b['arena_address']+index*256;assert final[at:at+16]==final[at+240:at+256]==bytes([0xa5])*16
        code_copy=bytearray(final[b['resident_address']:b['heap_start']])
        for slot in [slot_A,slot_B]:
            low=slot+16-b['resident_address'];high=slot+240-b['resident_address']
            code_copy[low:high]=memory[slot+16:slot+240]
        assert code_copy==memory[b['resident_address']:b['heap_start']]
        assert final[aux_base:aux_base+len(aux)]==aux and final[0x98000:0x98020]!=memory[0x98000:0x98020]
        stats=device.stats();assert stats['GPUExec1_calls']>0 and not stats['device_error'] and not stats['game_frames_executed']
        if changed:
            assert all(observer.fixture_stat(i)==0 for i in [0,1,2,3,4,7,8,9]),[observer.fixture_stat(i)for i in range(15)]
            assert observer.fixture_stat(5)==1 and observer.fixture_stat(6)==turns
        return dict(observer_calls=observer_calls,readonly_boundary_checks=readonly_boundary_checks,memory=final,initial=bytes(memory),registers=registers,SR=sr,USP=registers[15],SSP=runtime.prefix[17],waits=waits,signals=signals,yields=yields,GPUs=GPUs,switches=switches,parked_checks=parked_checks,parked_resumes=parked_resumes,guest_A=A+1024-minimum[A],guest_B=B+1024-minimum[B],arena_A=240-arena_min[A],arena_B=240-arena_min[B],supervisor_stack=SSP-ssp_low,steps=steps,covered=sorted(covered),GPU_stats=stats,A=A,B=B,slot_A=slot_A,slot_B=slot_B)

    symbols_for_observer=b['resource_arena_symbols']
    rows=[]
    try:
        state['status']='running_actual_wait_signal_task_GPU_interleavings';mark()
        for index_A in [0,100]:
            for turns in [1,2,3,7]:
                for flags in [0,31,0x700,0x71f]:
                    state['current_case']=dict(A_slot=index_A,turns=turns,flags=flags);mark()
                    left=execute(False,turns,flags,index_A);right=execute(True,turns,flags,index_A)
                    assert left['memory']==right['memory'],'Observer changes complete actual RAM'
                    assert left['GPU_stats']['GPUExec1_calls']==right['GPU_stats']['GPUExec1_calls']
                    assert left['registers']==right['registers'] and left['SR']==right['SR'] and left['SSP']==right['SSP']
                    for key in ['waits','signals','yields','GPUs','switches']:assert left[key]==right[key],key
                    assert left['memory'][right['B']:right['B']+1024]==right['memory'][right['B']:right['B']+1024]
                    assert left['memory'][right['slot_B']:right['slot_B']+256]==right['memory'][right['slot_B']:right['slot_B']+256]
                    comparable=bytearray(right['memory']);intervals=[(right['A']+64,right['A']+1024),(right['slot_A']+16,right['slot_A']+240),(SSP-192,SSP)]
                    intervals +=[(row['entry'],row['entry']+6)for row in b['resource_arena_entry_patches']]
                    for low,high in intervals:comparable[low:high]=left['memory'][low:high]
                    if comparable!=left['memory']:
                        save(out/'RAM-counterexample.json',dict(case=state['current_case'],differences=[dict(address=i,reference=x,candidate=y)for i,(x,y)in enumerate(zip(left['memory'],comparable))if x!=y][:64]));raise AssertionError('RAM-counterexample.json')
                    rows.append(dict(A_slot=index_A,turns=turns,flags=flags,observer_calls=right['observer_calls'],readonly_boundary_checks=right['readonly_boundary_checks'],all2MB_RAM_equal_without_exclusions=True,actual_waits=len(right['waits']),actual_signals=len(right['signals']),actual_switches=len(right['switches']),actual_GPU_submissions=len(right['GPUs']),parked_state_checks_after_instructions=right['parked_checks'],parked_state_resumes=right['parked_resumes'],old_guest_A_stack=left['guest_A'],new_guest_A_stack=right['guest_A'],guest_B_stack=right['guest_B'],private_A_bytes=right['arena_A'],private_B_bytes=right['arena_B'],supervisor_stack=right['supervisor_stack'],all_final_CPU_public_RAM_task_headers_and_complete_B_state_match=True,GPU_steps=right['GPU_stats']['GPUExec1_calls'],covered=right['covered']))
                    state['completed']=len(rows);mark()
        save(out/'cases.json',rows)
        paths=[Path(__file__),observer_path,Path(observer_proof['library']),ap,vp,bp,startup_path,Path(b['resource_arena_payload']),Path(b['component']),Path(v6['payload']),Path(b['component']),Path(b['derived_stage']),source,linker,out/'tasks.bin',out/'cases.json',Path(scheduler.__file__),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
        state.update(status='terminal_resource_input_observer_actual_wait_CPU_readonly_and_owner_commits_match',completed=len(rows),observer_calls=sum(r['observer_calls']for r in rows),whole_RAM_readonly_boundary_checks=sum(r['readonly_boundary_checks']for r in rows),complete_final_CPU_RAM_hardware_effects_equal_without_exclusions=True,actual_waits=sum(r['actual_waits']for r in rows),actual_signals=sum(r['actual_signals']for r in rows),actual_switches=sum(r['actual_switches']for r in rows),actual_GPU_submissions=sum(r['actual_GPU_submissions']for r in rows),maximum_new_guest_A_stack=max(r['new_guest_A_stack']for r in rows),maximum_old_guest_A_stack=max(r['old_guest_A_stack']for r in rows),maximum_guest_B_stack=max(r['guest_B_stack']for r in rows),maximum_private_A_bytes=max(r['private_A_bytes']for r in rows),maximum_private_B_bytes=max(r['private_B_bytes']for r in rows),maximum_supervisor_stack=max(r['supervisor_stack']for r in rows),parked_state_instruction_checks=sum(r['parked_state_checks_after_instructions']for r in rows),real_DF8C_TRAP4_DEF6_scheduler_RTE_DF96=True,real_DF9C_DF04_signal=True,real_task_B_DF60_TRAP0_scheduler_RTE=True,scheduler_provider='Actual v39 stage/resident scheduler dispatch/select/RTE; original semaphore/trap instructions',actual_v39_image_addresses=True,actual_disc_sha256=b['derived_disc_sha256'],GPU_provider='Original4320arithmetic synchronous through inherited native E220/E098',full_input_caller_executed=False,transport_and_loader_executed=False,same_task_alias_reentry_qualified=False,arbitrary_IRQ_qualified=False,gameplay_verified=False,default_promoted=False,source_sha256={str(p):sha(p)for p in paths},scope='32pairedactualv39direct-resourcewait/twoTaskGPUfixtureswithidenticalguestcode,observeroffvson. EveryobservercallchecksactualCPUunchanged;resource/helper/GPUboundarycallscheckall2MBRAMimmediatelyunchanged. Finalall2MBRAM/CPU/banks/GPUeffectsexactwithoutnormalization. Resourceobservercounts/commits/parkedstateanddifferent-taskownershipmatchactualexecution. Fullinputnotexecutedhere,scalarinputobserverrequiresseparateCPUcheck. No same-taskproductionreentryguard,arbitraryIRQ,freshgame or consoleproof.')
        mark();print({k:state[k]for k in ['status','completed','actual_switches','actual_GPU_submissions','maximum_private_A_bytes','maximum_private_B_bytes']},flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);state.update(status='terminal_actual_resource_wait_task_arena_failed',error=repr(error));mark();raise
    finally:runtime.close()


if __name__=='__main__':main()

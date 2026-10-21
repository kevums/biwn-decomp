"""Captured walking inputs plus connected original dispatcher/division cases.

Original 191F4 and E588 both execute; no RTS helper stub supplies division.
Nonmovement preamble globals are neutral fixture values. Live claims cover
the captured movement speed/remainder, not a full original runtime snapshot.
"""
import collections, ctypes as c, random, subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_SR, UC_M68K_REG_A7, UC_M68K_REG_D0, UC_M68K_REG_PC
import check_biwn_input_dispatch as dispatch
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    out=V/'input-timing-connected-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    deps={str(Path(__file__)):sha(__file__)};live=[];lanes={}
    for origin in ['candidate','control']:
        lanes[origin]={}
        for lane in ['native','original']:
            pointer=V/f'record-loop-input-timing-{origin}-{lane}-v3-current.json';job=read(pointer)
            assert job['status']=='terminal_saved_state_equal_origin_diagnostic_pending_review'
            for path,digest in job['source_sha256'].items():assert sha(path)==digest,path
            deps.update(job['source_sha256']);deps[str(pointer)]=sha(pointer)
            directory=Path(job['directory']);rows=read(directory/'frames.json')
            prior=read(V/f'record-loop-equal-state-motion-{origin}-{lane}-v2-current.json')
            assert rows==read(Path(prior['directory'])/'frames.json'),'Observer changes execution'
            data=read(directory/'world-events.json');assert data['overflow']==0
            events=data['events'];assert len(events)%3==0
            pairs=[]
            for index in range(0,len(events),3):
                a,b,w=events[index:index+3];assert [a['stage'],b['stage'],w['stage']]==[1,2,3]
                assert a['pc']==0x191f4 and b['pc']==0x1a26c and w['pc']==0x1a2c2
                assert b['speed']==w['speed'] and b['remainder']==w['remainder']
                pairs.append((a,b))
            walking=[(a,b)for a,b in pairs if a['state']==5 and a['held']==0x100000]
            assert all(b['state']==5 for a,b in walking)
            release=[(a,b)for a,b in pairs if a['state']==5 and a['held']==0]
            assert len(release)==1 and release[0][1]['state']==1 and release[0][1]['speed']==release[0][1]['remainder']==0
            total=sum(a['dt']for a,b in walking);ticks=sum(b['speed']for a,b in walking)
            stages=collections.Counter((a['state'],b['state'])for a,b in pairs)
            lanes[origin][lane]=dict(input_calls=len(pairs),walking_calls=len(walking),walking_clock_ticks=total,
                movement_steps=ticks,last_walking_frame=walking[-1][0]['frame'],
                last_walking_remainder=walking[-1][1]['remainder'],release_frame=release[0][0]['frame'],
                remainder_discarded_at_release=release[0][0]['remainder'],release_speed=release[0][1]['speed'],
                release_remainder=release[0][1]['remainder'],observer_all_prior_rows_equal=True,
                state_transitions={f'{a}->{b}':n for (a,b),n in stages.items()})
            for a,b in walking:
                live.append(dict(kind='captured_walking',origin=origin,lane=lane,frame=a['frame'],
                                 state=5,held=a['held'],dt=a['dt'],remainder=a['remainder'],
                                 expected_live_speed=b['speed'],expected_live_remainder=b['remainder']))
    assert len(live)==194
    assert [lanes['candidate'][k]['walking_clock_ticks']for k in ['native','original']]==[287,290]
    assert [lanes['candidate'][k]['movement_steps']for k in ['native','original']]==[22,23]
    assert [lanes['control'][k]['walking_clock_ticks']for k in ['native','original']]==[293,293]
    assert [lanes['control'][k]['movement_steps']for k in ['native','original']]==[23,23]
    restoration=ROOT/'projects/black-ice-white-noise/restoration';library=out/'input-and-division.dylib'
    q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',
                      str(restoration/'biwn_input_dispatch.c'),str(restoration/'biwn_signed_division.c'),'-o',str(library)],capture_output=True,text=True)
    (out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    lib=c.CDLL(str(library));fn=lib.biwn_input_dispatch
    fn.argtypes=[c.POINTER(dispatch.world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    divide=lib.biwn_signed_division;divide.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];divide.restype=c.c_int
    class Script(dispatch.Script):
        def call(self,address,args):
            assert address==0xe588 and len(args)==2 and args[1]==300,(hex(address),args)
            self.trace.append(['call',address,args]);quotient=c.c_uint32();remainder=c.c_uint32()
            assert divide(*args,c.byref(quotient),c.byref(remainder))==0
            return quotient.value
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert len(snapshot)==0x200000
    vectors=list(live)
    values=[0,1,2,7,8,30,0x1ffff,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    carries=[0,1,0x7fff,0xffff,0x10000,0x7fffffff,0xffffffff]
    for state,held in [(5,0x100000),(7,0x200000),(8,0x102000)]:
        for dt in values:
            for remainder in carries:vectors.append(dict(kind='connected_boundary',state=state,held=held,dt=dt,remainder=remainder))
    assert len(vectors)==425
    results=[];rng=random.Random(0x191f4);coverage=set()
    for i,vector in enumerate(vectors):
        case=dict(kind=vector['kind'],incoming=[rng.getrandbits(32)for _ in dispatch.world.REGS],
            initial=[[0x4624a,2,0],[0x49d62,2,0],[0x49c4e,2,0],[0x49cb8,2,vector['state']],
                     [0x49ba4,4,vector['held']],[0x4c24c,4,vector['dt']],[0x49cc8,4,vector['remainder']]],
            helper_returns={str(x):0 for x in dispatch.HELPERS},default_helper_return=0)
        original=Script(snapshot,case);translated=Script(snapshot,case)
        cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(original.memory));cpu.mem_write(dispatch.SP,dispatch.STOP.to_bytes(4,'big'))
        for reg,value in zip(dispatch.world.REGS,case['incoming']):cpu.reg_write(reg,value)
        cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,dispatch.SP)
        def code(e,address,width,user):
            assert 0x191f4<=address<0x19f2c or 0xe588<=address<0xe60a,hex(address)
            coverage.add(address)
            if address==0xe588:
                stack=e.reg_read(UC_M68K_REG_A7)
                args=[int.from_bytes(e.mem_read(stack+offset,4),'big')for offset in [4,8]]
                original.trace.append(['call',address,args])
        def memory_read(e,access,address,width,value,user):
            if dispatch.SP-0x1000<=address<dispatch.SP+8:return
            expected=original.read(address,width);assert int.from_bytes(e.mem_read(address,width),'big')==expected
        def memory_write(e,access,address,width,value,user):
            if dispatch.SP-0x1000<=address<dispatch.SP+8:return
            original.write(address,width,value&((1<<(width*8))-1))
        cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,memory_read);cpu.hook_add(UC_HOOK_MEM_WRITE,memory_write)
        cpu.emu_start(0x191f4,dispatch.STOP,count=5000,timeout=1000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==dispatch.STOP and cpu.reg_read(UC_M68K_REG_A7)==dispatch.SP+4
        status,d0=dispatch.translated(fn,translated,case)
        assert status==0 and d0==cpu.reg_read(UC_M68K_REG_D0),(i,vector,status,d0,cpu.reg_read(UC_M68K_REG_D0))
        assert original.trace==translated.trace,(i,'ordered global accesses/helpers differ')
        memory=bytes(cpu.mem_read(0,0x200000));expected=bytes(translated.memory)
        assert memory[:dispatch.SP-0x1000]==expected[:dispatch.SP-0x1000] and memory[dispatch.SP+8:]==expected[dispatch.SP+8:]
        speed=int.from_bytes(expected[0x49cc4:0x49cc8],'big');carry=int.from_bytes(expected[0x49cc8:0x49ccc],'big')
        if vector['kind']=='captured_walking':
            assert speed==vector['expected_live_speed'] and carry==vector['expected_live_remainder'],(i,vector,speed,carry)
        results.append(dict(vector=vector,original_and_C_speed=speed,original_and_C_remainder=carry,
                            ordered_global_accesses_and_helper_args_equal=True,original_division_executed=True))
    save(out/'cases.json',results);save(out/'lane-summary.json',lanes)
    for file in [Path(dispatch.__file__),Path(dispatch.boundary.__file__),ROOT/'render-assets/biwn-inventory-baseline.bin',
                 restoration/'biwn_input_dispatch.c',restoration/'biwn_input_dispatch.h',restoration/'biwn_signed_division.c',
                 restoration/'biwn_signed_division.h',library,out/'cases.json',out/'lane-summary.json']:
        deps[str(file)]=sha(file)
    facts=dict(status='terminal_readonly_input_trace_clock_threshold_explained_connected425_live194_pass',directory=str(out),
               lane_summary=lanes,new_diagnostic_lanes=4,observer_preserves_all_prior_rows=True,
               connected_original_dispatch_and_division_cases=425,captured_walking_cases=194,
               connected_boundary_cases=231,ordered_global_accesses_and_helper_arguments_match=True,
               whole_nonprivate_RAM_matches=True,source_game_code_changed=False,new_unique_original_functions=0,
               fresh_routes=0,fresh_matrix_gate_waived=False,full_game_fidelity_verified=False,
               host_pose_timer_or_input_normalization=False,new_predictions=0,new_training=False,
               scope='Four read-only motion replicas expose191F4entry/1A26Cexit and1A2C2world boundaries;all180priorCPU/RAM/GPU/DSP/video rows match. Original191F4andE588execute together in425connected fixtures;194use capturedwalkingdt/carry and matchlive speed/remainder. Otherpreamble globals heldneutral in fixtures;not completecaptured runtimeRAM/register equivalence. The controlled22/23step difference is explained by287/290admittedclockticks and release discarding a differentfraction. Specific earlierfreshroute mismatch remains unresolved;no gatewaived.',
               source_sha256=deps)
    save(out/'review.json',facts);save(V/'input-timing-connected-v1-current.json',facts)
    print(facts['status'],'425connected/194captured;287vs290ticks',flush=True)


if __name__=='__main__':main()

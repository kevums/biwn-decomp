"""Actual loaded actors through death flag, TRAP2 and task free-list removal."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_loaded_actor_runtime as actor
ROOT=actor.ROOT;CPU=actor.CPU;world=actor.world;save=actor.save;get=actor.get;sha=actor.sha


def main():
    proof=json.loads((ROOT/'verification/loaded-actor-runtime-current.json').read_text());folder=Path(proof['directory']);cases=json.loads((folder/'cases.json').read_text());source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,h in proof['source_sha256'].items():assert sha((source/name).read_bytes())==h
    out=ROOT/'verification/loaded-actor-removal'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    runtime=actor.Runtime(folder/'libloaded-actor-runtime.dylib');rows=[]
    try:
        for ordinal,case in enumerate(cases):
            ram=bytearray((folder/f'case-{ordinal}-C-RAM.bin').read_bytes());assert sha(ram)==case['rebuilt']['boundaries'][-1]['RAM_sha256']
            task=int(case['task'],16);pred=int(case['fixture']['predecessor'],16);slot=case['fixture']['actor_parameter'];obj=0x49d6c+slot*206
            ram[obj+2:obj+4]=(1).to_bytes(2,'big');ram[pred+26:pred+30]=bytes(4);initial=CPU()
            initial.registers[:]=case['final_CPU']['registers']
            for key in['pc','usp','ssp','sr']:setattr(initial,key,case['final_CPU'][key])
            ram=bytes(ram);assert initial.pc==0xf70c and get(ram,0x88)==0xdeb6
            save(out/'status.json',dict(status='running',case=ordinal,total=len(cases)))
            runtime.device.seed(ram,0);actor.lifecycle.seed_cpu(runtime,initial);boundary=None;steps=[]
            for _ in range(500):
                pc=runtime.core.m68k_get_reg(None,16)
                if pc==0x1ffe00:break
                assert any(lo<=pc<hi for lo,hi in[(0xf56e,0xf57e),(0xf70c,0xf712),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xde08,0xde5c),(0xdf66,0xdf6c)]),hex(pc)
                if pc==0xdf7a:boundary=runtime.snapshot(runtime.cpu())
                steps.append(pc);runtime.core.m68k_execute(1)
            else:raise AssertionError('Native removal did not return to predecessor caller')
            left=runtime.device.ram();expected=runtime.cpu();assert boundary
            runtime.device.seed(ram,1);actual=CPU.from_buffer_copy(bytes(initial))
            bus=world.Bus(runtime.device.r8,runtime.device.r16,runtime.device.r32,runtime.device.w16,runtime.device.w32,world.CALL(),None,0)
            status=runtime.pipeline(c.byref(bus),c.byref(actual),runtime.device.write8,4096,actor.OBSERVER(),None)
            assert status==0 and actual.pc==0xdf7a
            C_boundary=runtime.snapshot(actual)
            assert runtime.pipeline(c.byref(bus),c.byref(actual),runtime.device.write8,4096,actor.OBSERVER(),None)==0
            right=runtime.device.ram()
            if left!=right or bytes(expected)!=bytes(actual)or boundary!=C_boundary:
                save(out/'mismatch.json',dict(case=ordinal,native_CPU=actor.live.prior.scheduler.cpu_dict(expected),C_CPU=actor.live.prior.scheduler.cpu_dict(actual),native_boundary=boundary,C_boundary=C_boundary,RAM_differences=[hex(a)for a,(l,r)in enumerate(zip(left,right))if l!=r][:64]));raise AssertionError(str(out/'mismatch.json'))
            assert actual.pc==0x1ffe00 and get(right,0xc0920)==pred and get(right,0xc0924)==task and get(right,obj,2)==0
            assert task not in actor.ring(right)
            rows.append(dict(case=ordinal,task=case['task'],scene=case['scene'],actor_slot=slot,native_CPU_instructions=len(steps),pending_removal=boundary,final_CPU=actor.live.prior.scheduler.cpu_dict(actual),full_CPU_and_all_RAM_match=True,task_removed_from_actual_ring=True,free_list_head=hex(get(right,0xc0924))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error)));raise
    finally:runtime.close()
    save(out/'cases.json',rows)
    report=dict(status='loaded_actor_death_and_TRAP2_removal_match_native',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),actor_entries=proof['actor_entries'],source_sha256=proof['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),actor_update_proof=str(ROOT/'verification/loaded-actor-runtime-current.json'),source_directory=str(folder),new_actor_state_edits='Supplied death flag1 and unblocked predecessor context so source scheduler has a ready continuation after removal.',default_promoted=False,scope='Freshly loaded actors after verified1or8updates. OriginalF70C/actor exit writes and actualTRAP2/DEB6unlink/free-list/dispatch/RTE/resume compare fullCPU/all2MBRAM and pendingremoval checkpoints against linkedCpipeline. Actual task ring retained; supplied deathflag and predecessorreadiness, othercontextsblocked, no naturalcombatdeath/clock/interrupt/wholegame proof.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)));save(ROOT/'verification/loaded-actor-removal-current.json',report);print(json.dumps({k:report[k]for k in ['status','directory','cases','actor_entries']}),flush=True)


if __name__=='__main__':main()

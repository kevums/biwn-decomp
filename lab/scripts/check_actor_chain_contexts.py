"""Qualify final-address C-chain shared context, virtual ABI and task canaries.

Every native physical SP is observed. Native RAM task-header/lower guards are
checked after execution; full result and remaining physical helper ABI match the
original. Internal C collision boundaries compare decoded shadow state, not
physical C-ABI registers. Corruption controls alter decoded observations only.
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime,timezone
import check_native_actor_chain as fixtures
import actor_chain_native_replay as replay

ROOT=fixtures.ROOT


class ObservationMismatch(Exception):
    pass


class Observer:
    def __init__(self,negative=None):
        self.negative=negative

    def check(self,condition,kind):
        if not condition:
            raise ObservationMismatch(kind)

    def begin(self,native,case,compiled,symbols,base,payload):
        self.native=native;self.case=case;self.compiled=compiled;self.symbols=symbols;self.SP=fixtures.chain.SP
        self.context=self.SP-320-{0x13c9a:40,0x13b5a:8,0x13bb0:4}[case['entry']]
        self.pending=None;self.virtual=None;self.physical_checks=self.virtual_checks=0;self.injected=False
        self.returns={}
        targets={'biwn_native_actor_move_direction_capture':0x13440,'biwn_native_actor_move_submit_capture':0xe220,'biwn_native_actor_collision_outside_index_capture':0x1039c,'biwn_native_actor_collision_outside_scan_capture':0x102c4,'biwn_native_actor_collision_inside_outside_capture':0x1028e,'biwn_native_actor_collision_inside_index_capture':0x10652,'biwn_actor_chain_outside_index_capture':0x1039c,'biwn_actor_chain_outside_scan_capture':0x102c4,'biwn_actor_chain_inside_outside_capture':0x1028e,'biwn_actor_chain_inside_index_capture':0x10652}
        addresses=sorted(set(symbols.values())|{base+len(payload)})
        for name,target in targets.items():
            start=symbols[name];end=next(a for a in addresses if a>start)
            code=payload[start-base:end-base];pattern=b'\x4e\xb9'+target.to_bytes(4,'big')
            self.check(code.count(pattern)==1,'capture_decode')
            self.returns[start+code.index(pattern)+6]=target

    def ram(self):return self.native.device.ram()
    def reg(self,i):return self.native.lib.m68k_get_reg(None,i)
    def u32(self,ram,a):return int.from_bytes(ram[a:a+4],'big')

    def step(self,pc):
        sp=self.reg(15)
        if self.negative=='task_SP'and self.compiled and not self.injected and pc==self.symbols['biwn_native_actor_move']:
            sp=self.SP-920;self.injected=True
        self.check(self.SP-918<=sp<=self.SP,'task_stack_boundary')
        if not self.compiled:
            return
        if pc==self.symbols['biwn_actor_chain_collision_call']:
            ram=self.ram();context=self.u32(ram,sp+4)
            shadow=[self.u32(ram,context+4*i)for i in range(20)]
            if self.negative=='virtual_SP'and not self.injected:
                shadow[15]^=2;self.injected=True
            self.check(self.virtual is None and self.pending is None,'nested_virtual_state')
            self.check(context==self.context and shadow[15]==self.SP-54 and shadow[19]==0x13c9a and shadow[18]in[0x13b5a,0x13bb0],'virtual_collision_entry')
            self.virtual=dict(logical=shadow[15],D2=shadow[2],A2=shadow[10],params=ram[shadow[15]+4:shadow[15]+14],entry=shadow[18])
        if pc==self.symbols['biwn_actor_chain_collision_call_return']:
            self.check(self.virtual is not None and self.pending is None,'virtual_collision_pending')
            ram=self.ram();shadow=[self.u32(ram,self.context+4*i)for i in range(20)];v=self.virtual
            self.check(shadow[15]==v['logical']and shadow[2]==v['D2']and shadow[10]==v['A2']and shadow[19]==0x13c9a and ram[v['logical']+4:v['logical']+14]==v['params'],'virtual_collision_return')
            self.virtual_checks+=1;self.virtual=None
        if pc in[0x13440,0xe220,0x1039c,0x102c4,0x1028e,0x10652]:
            ram=self.ram();ret=self.u32(ram,sp)
            if ret in self.returns:
                self.check(self.pending is None and self.returns[ret]==pc,'physical_helper_pending')
                raw=ram[self.context:self.context+80];shadow=[self.u32(raw,4*i)for i in range(20)];sr=self.reg(17)
                if self.negative=='helper_X'and not self.injected:
                    sr^=16;self.injected=True
                self.check(shadow[:15]==[self.reg(i)for i in range(15)]and shadow[15]==sp+4 and(shadow[16]&0xffff)==sr and shadow[19]==self.case['entry'],'physical_helper_context')
                self.pending=dict(ret=ret,context=raw,SP=sp)
        if self.pending and pc==self.pending['ret']:
            ram=self.ram();raw=ram[self.context:self.context+80]
            if self.negative=='saved_context'and not self.injected:
                raw=bytes([raw[0]^1])+raw[1:];self.injected=True
            self.check(raw==self.pending['context']and sp==self.pending['SP']+4,'physical_helper_context_canary')
            self.physical_checks+=1;self.pending=None
        root_return=self.symbols[{0x13c9a:'biwn_native_actor_move_return',0x13b5a:'biwn_native_actor_collision_outdoor_return',0x13bb0:'biwn_native_actor_collision_indoor_return'}[self.case['entry']]]
        if pc==root_return:
            saved={0x13c9a:[2,3,4,5,6,7,10,11,12,13],0x13b5a:[2,10],0x13bb0:[10]}[self.case['entry']]
            observed=[self.reg(i)for i in range(15)]
            if self.negative=='callee_D2'and not self.injected:
                observed[2]^=1;self.injected=True
            self.check(all(observed[i]==self.case['incoming'][i]for i in saved)and sp==self.SP,'public_root_return')

    def finish(self):
        self.check(self.pending is None and self.virtual is None,'pending_at_completion')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    gate=fixtures.direct.g.read(ROOT/'verification/native-actor-chain-final-current.json')
    assert gate['status']=='terminal_source_owned_actor_chain_pass'and gate['code_address']==0x16489c
    for p,h in gate['source_sha256'].items():assert fixtures.direct.g.sha(p)==h,p
    snapshot,payload,symbols,build=fixtures.prepare(gate)
    out=ROOT/'verification/actor-chain-contexts'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    fixtures.direct.g.save(out/'component-gate.json',gate)
    groups=[('collision',fixtures.direct,fixtures.direct.vectors()),('movement',fixtures.chain,fixtures.chain.vectors())]
    if args.limit:
        groups=[(name,engine,cases[:args.limit]if name=='collision'else[cases[i]for i in[0,16,32,80,96,112,160,176]][:args.limit])for name,engine,cases in groups]
    state=dict(status='checking_final_actor_chain_contexts',directory=str(out),pid=os.getpid(),planned=2*sum(len(cases)for _,_,cases in groups),completed=0)
    def mark():fixtures.direct.g.save(out/'protocol.json',state);fixtures.direct.g.save(ROOT/'verification/actor-chain-contexts-active.json',state)
    mark();native=fixtures.chain.Native();rows=[]
    try:
        for name,engine,cases in groups:
            for i,case in enumerate(cases):
                outputs=[]
                for compiled in [False,True]:
                    expected=engine.execute(snapshot,case,payload,symbols,compiled)
                    observer=Observer();result,depth=replay.replay(engine,native,snapshot,case,payload,symbols,compiled,expected,observer)
                    outputs.append(result);rows.append(dict(group=name,index=i,compiled=compiled,native_private_depth=depth,headroom=918-depth,physical_context_checks=observer.physical_checks,virtual_collision_checks=observer.virtual_checks))
                assert outputs[0]==outputs[1]
                state['completed']=len(rows)
                if i%64==0:mark();print(name,i+1,'/',len(cases),flush=True)
        movements=fixtures.chain.vectors();results=fixtures.direct.g.read(Path(gate['directory'])/'results.json');witness=max((row for row in results if row['group']=='movement'),key=lambda row:row['candidate_depth']);case=movements[witness['index']];engine=fixtures.chain;expected=engine.execute(snapshot,case,payload,symbols,True);controls=[]
        for negative in ['task_SP','virtual_SP','helper_X','saved_context','callee_D2']:
            observer=Observer(negative);error=None
            try:replay.replay(engine,native,snapshot,case,payload,symbols,True,expected,observer)
            except ObservationMismatch as mismatch:error=str(mismatch)
            assert error and observer.injected,negative
            controls.append(dict(defect=negative,rejected=True,diagnostic=error,native_CPU_or_RAM_changed=False))
        fixtures.direct.g.save(out/'results.json',rows);fixtures.direct.g.save(out/'negative-controls.json',controls)
        inputs=[Path(__file__),Path(replay.__file__),Path(fixtures.__file__),out/'component-gate.json',out/'negative-controls.json',Path(gate['binary']),Path(gate['ELF']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
        state.update(status='terminal_actor_chain_contexts_preflight_pass'if args.limit else'terminal_final_actor_chain_contexts_pass',completed=len(rows),cases=len(rows)//2,max_native_private_depth=max(row['native_private_depth']for row in rows if row['compiled']),minimum_headroom=min(row['headroom']for row in rows if row['compiled']),physical_context_checks=sum(row['physical_context_checks']for row in rows),virtual_collision_checks=sum(row['virtual_collision_checks']for row in rows),negative_controls=controls,source_sha256={str(p):fixtures.direct.g.sha(p)for p in inputs},scope=__doc__)
        mark()
        if not args.limit:fixtures.direct.g.save(ROOT/'verification/actor-chain-contexts-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','cases','max_native_private_depth','minimum_headroom','physical_context_checks','virtual_collision_checks']}))
    except BaseException as error:
        state.update(status='terminal_actor_chain_contexts_failed',error=repr(error));mark();raise
    finally:native.close()


if __name__=='__main__':
    main()

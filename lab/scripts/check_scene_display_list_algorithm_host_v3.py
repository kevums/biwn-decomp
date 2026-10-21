"""Structured185B2 versus original pinned68000 and Unicorn, with full guest frames and ordered bus."""
import argparse,ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_display_list_cpu as base
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

class Runtime(base.Runtime):
    def native(self,ram,case,coverage):
        if not case['read_queues']:return super().native(ram,case,coverage)
        execute=self.core.m68k_execute
        def one(count):
            pc=self.core.m68k_get_reg(None,16)
            if pc in [0x186ca,0x186ce,0x187ba,0x187c4,0x1881e]:self.inject(self.core.m68k_get_reg(None,9),4)
            if pc in [0x1873e,0x1874a]:self.inject(self.core.m68k_get_reg(None,13),2)
            return execute(count)
        self.core.m68k_execute=one
        try:return super().native(ram,case,coverage)
        finally:self.core.m68k_execute=execute

def cases(snapshot):
    rows=base.cases(snapshot);count=len(rows);assert count==1025
    for full in [False,True]:
        for supervisor in [False,True]:
            for ccr in range(32):
                x=json.loads(json.dumps(rows[1+ccr%2]));x.update(id=len(rows),body=not full,SR=(0x2000 if supervisor else 0)|((ccr%8)<<8)|ccr,usp=0x170000 if supervisor else base.SP,ssp=base.SP if supervisor else 0x1d0000,kind='complete_CCR_bank_call_matrix');rows.append(x)
    for i in range(64):
        x=json.loads(json.dumps(rows[1+i%2]));x.update(id=len(rows),kind='declared_operand_reread_mutation',read_queues=[dict(address=0x120006,width=4,values=[1,2]),dict(address=0x120012,width=2,values=[0xffff,1])]);rows.append(x)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();source=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v3';out=V/'scene-display-list-algorithm-host-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False)
    def mark():save(out/'protocol.json',state);save(V/'scene-display-list-algorithm-host-v3-current.json',state)
    mark();runtime=None
    try:
        library=out/'display-list.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'host-wrapper.c'),'-o',str(library)];q=subprocess.run(cmd,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
        session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'display-list-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases(snapshot);vectors=vectors[:args.limit]if args.limit else vectors;runtime=Runtime(library,mapping['instructions_decoded']);coverage=set();rows=[]
        for case in vectors:
            ram=base.fixture(snapshot,case);left,expected,pinned=runtime.native(ram,case,coverage);independent,other,unicorn=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
            valid=not rebuilt['status'] and not rebuilt['errors'] and bytes(expected)==bytes(other)==bytes(actual) and left==independent==right and unicorn['trace']==rebuilt['trace']
            if not valid:
                save(out/'counterexample.json',dict(case=case,original_CPU=base.queue.cd.scheduler.cpu_dict(expected),Unicorn_CPU=base.queue.cd.scheduler.cpu_dict(other),rebuilt_CPU=base.queue.cd.scheduler.cpu_dict(actual),original=pinned,Unicorn=unicorn,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:32]))
                raise AssertionError(out/'counterexample.json')
            rows.append(dict(case=case['id'],kind=case.get('kind','legacy'),body=case['body'],CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),ordered_accesses=len(rebuilt['trace']),full_CPU_2MB_RAM_private_frames_and_order_match=True,source_instructions=len(pinned['steps'])))
            state.update(status='checking',completed=len(rows));mark()
            if len(rows)%64==0:print('display host',len(rows),'/',len(vectors),flush=True)
        save(out/'cases.json',rows);save(out/'vectors.json',vectors)
        if args.limit:state.update(status='terminal_display_list_structured_host_preflight',library=str(library));mark();print(state['status'],len(rows),flush=True);return
        missing={r['address']for r in mapping['instructions_decoded']}-coverage;assert missing=={0x185ec,0x18642},list(map(hex,missing));guards=[]
        case=vectors[1];ram=base.fixture(snapshot,case)
        for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
            _,_,d=runtime.translated(ram,case,**options);assert d['status']==1 and d['CPU_unchanged'] and not d['trace'];guards.append(dict(options=options,status=1))
        for options,status in [(dict(bad_pc=True),7),(dict(budget=1),4),(dict(fail=('read',4)),2),(dict(fail=('write',4)),2),(dict(fail=('read',2)),2),(dict(fail=('write',2)),2)]:
            _,_,d=runtime.translated(ram,case,**options);assert d['status']==status and d['CPU_unchanged'],(options,d);guards.append(dict(options=options,status=status))
        save(out/'guards.json',guards)
        state.update(status='terminal_structured_display_list_dual_CPU_full_RAM_order_pass',library=str(library),host_guards=len(guards),stable_cases=1025,complete_CCR_bank_body_call_cases=128,declared_operand_reread_cases=64,source_instruction_coverage=[252,254],unreachable_fixed_positive_literal_alternates=['0x185ec','0x18642'],original_nested_helpers=0,new_unique_original_functions=0,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(base.__file__),Path(base.queue.__file__),session/'display-list-fullCPU-generation.json',ROOT/'projects/black-ice-white-noise/restoration/biwn_display_list_cpu.c',*source.iterdir(),library,out/'cases.json',out/'vectors.json',out/'guards.json']},scope=__doc__+' 1217finite valid descriptor lists, stable captured real list, allCCR/bothbanks/body/fullcall and64declared handle/field-rereads. Native original operand mutations occur before the exact matching instruction; Unicorn/C use bus-read fixtures. Complete2MBRAM includes original LINK/MOVEM/local/dynamic private table and one-past unused read. No target code/game/IRQ/console proof. Original host work limits are separate from unbounded target loops; arbitrary invalid jump targets, stack/output aliases and concurrent mutation remain outside contract.')
        mark();print(state['status'],len(rows),len(guards),flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if runtime:runtime.close()
if __name__=='__main__':main()

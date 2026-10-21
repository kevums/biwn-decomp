"""Verify a callback-free coordinate continuation against original CPU cases.

The driver executes effects; the C state machine only emits requests. Delayed
requests, copied state and concurrent contexts must not repeat an operation.
Host-round-robin demonstrations are not Jaguar scheduling/live-frame proofs.
"""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_biwn_coordinate_entry as original

ROOT=original.ROOT
RESTORE=ROOT/'projects/black-ice-white-noise/restoration'
SENTINEL=0xa55aa55a
class Request(c.Structure):
    _fields_=[('context',c.c_uint64),('sequence',c.c_uint64)]+[(x,c.c_uint32) for x in ['kind','address','value','argument_count','argument','incoming_d0']]
class Completion(c.Structure):
    _fields_=[('context',c.c_uint64),('sequence',c.c_uint64),('value',c.c_uint32),('status',c.c_int)]
class Flow(c.Structure):
    _fields_=[('pending',Request)]+[(x,c.c_uint32) for x in ['magic','phase','terminal','d0','deadline']]+[(x,c.c_uint16) for x in ['cursor','x','z','digit']]+[(x,c.c_uint32) for x in ['initial_index','callback_status']]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')

def inspect_source(source,out):
    command=['clang','-std=c99','-I',str(RESTORE),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)]
    compiled=subprocess.run(command,capture_output=True,text=True)
    (out/'syntax.log').write_text(compiled.stderr);assert compiled.returncode==0,compiled.stderr
    tree=json.loads(compiled.stdout)
    functions={node['name']:node for node in tree['inner'] if node['kind']=='FunctionDecl' and any(x['kind']=='CompoundStmt' for x in node.get('inner',[]))}
    assert not any(x['kind'] in ['VarDecl','FileScopeAsmDecl'] for x in tree['inner'])
    graph={name:set() for name in functions}
    def visit(node,name):
        assert node['kind'] not in ['WhileStmt','DoStmt','ForStmt','GotoStmt','GCCAsmStmt','MSAsmStmt']
        assert node.get('castKind') not in ['IntegralToPointer','PointerToIntegral','BitCast']
        if node['kind']=='CallExpr':
            target=node['inner'][0]
            while target['kind'] in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
            assert target['kind']=='DeclRefExpr' and target['referencedDecl']['name'] in functions,target
            graph[name].add(target['referencedDecl']['name'])
        for child in node.get('inner',[]):visit(child,name)
    for name,node in functions.items():visit(node,name)
    def depth(name,path=()):
        assert name not in path,'Recursive continuation engine'
        return 1+max((depth(child,path+(name,)) for child in graph[name]),default=0)
    depths={name:depth(name) for name in graph}
    save(out/'bounded-call-graph.json',dict(no_loops_or_recursion=True,no_external_calls_or_callbacks=True,call_graph={k:sorted(v) for k,v in graph.items()},max_call_depth=max(depths.values())))

class Engine:
    def __init__(self,library):
        self.lib=c.CDLL(str(library))
        self.begin=self.lib.biwn_coordinate_flow_begin;self.begin.argtypes=[c.POINTER(Flow),c.c_uint64,c.c_uint32];self.begin.restype=c.c_int
        self.advance=self.lib.biwn_coordinate_flow_advance;self.advance.argtypes=[c.POINTER(Flow),c.POINTER(Completion),c.POINTER(Request)];self.advance.restype=c.c_int
        self.result=self.lib.biwn_coordinate_flow_result;self.result.argtypes=[c.POINTER(Flow),c.POINTER(c.c_uint32)];self.result.restype=c.c_int
        self.digit=self.lib.biwn_button_digit;self.digit.argtypes=[c.c_uint32,c.c_uint32];self.digit.restype=c.c_uint32
    def drive(self,script,context=1,fail_at=None,copy_each_step=True):
        script.digit_function=self.digit
        state=Flow();assert self.begin(c.byref(state),context,script.case['incoming'][0])==0
        status,request=0,Request();assert self.advance(c.byref(state),None,c.byref(request))==0
        events,polls=0,0
        while status==0 and events<20000:
            assert request.context==context and request.sequence==events+1
            before=bytes(state)
            for _ in range(3):
                repeated=Request();assert self.advance(c.byref(state),None,c.byref(repeated))==0
                assert bytes(state)==before and bytes(repeated)==bytes(request)
                polls+=1
            if copy_each_step:state=Flow.from_buffer_copy(bytes(state))
            if events==fail_at:
                reply=Completion(request.context,request.sequence,0,-17)
            else:
                value=effect(script,request)
                reply=Completion(request.context,request.sequence,value,0)
            status=self.advance(c.byref(state),c.byref(reply),c.byref(request));events+=1
        assert status in [1,2],status
        output=c.c_uint32(SENTINEL);assert self.result(c.byref(state),c.byref(output))==status
        return dict(status=status,D0=output.value,events=events,pending_polls=polls,state=state)

def effect(script,request):
    if request.kind in [1,2,3]:return script.read(request.address,{1:1,2:2,3:4}[request.kind])
    if request.kind in [4,5,6]:script.write(request.address,{4:1,5:2,6:4}[request.kind],request.value);return 0
    assert request.kind==7 and request.argument_count<=1
    script.incoming_call_d0=request.incoming_d0
    return script.call(request.address,[request.argument] if request.argument_count else [])

def protocol_guards(engine,snapshot,case,out):
    guards=[]
    state=Flow();request=Request();output=c.c_uint32(SENTINEL)
    for name,call in [
        ('begin_null_state',lambda:engine.begin(None,1,0)),('begin_zero_context',lambda:engine.begin(c.byref(state),0,0)),
        ('advance_uninitialized',lambda:engine.advance(c.byref(state),None,c.byref(request))),
        ('advance_null_state',lambda:engine.advance(None,None,c.byref(request))),
        ('result_null_state',lambda:engine.result(None,c.byref(output)))]:
        assert call()==3;guards.append(dict(case=name,status=3))
    assert engine.begin(c.byref(state),19,0)==0
    assert engine.advance(c.byref(state),None,None)==3 and engine.result(c.byref(state),None)==3
    assert engine.result(c.byref(state),c.byref(output))==0 and output.value==SENTINEL
    for context,sequence in [(20,1),(19,0),(19,2)]:
        before=bytes(state);request=Request(999,999,999,999,999,999,999,999);before_out=bytes(request)
        wrong=Completion(context,sequence,1,0)
        assert engine.advance(c.byref(state),c.byref(wrong),c.byref(request))==4 and bytes(state)==before and bytes(request)==before_out
        guards.append(dict(case='wrong_or_out_of_order_reply',context=context,sequence=sequence,no_state_or_output_change=True))
    correct=Completion(19,1,1,0)
    assert engine.advance(c.byref(state),c.byref(correct),c.byref(request))==0
    before=bytes(state);before_out=bytes(request)
    assert engine.advance(c.byref(state),c.byref(correct),c.byref(request))==4 and bytes(state)==before and bytes(request)==before_out
    guards.append(dict(case='duplicate_completion',no_state_or_output_change=True))
    baseline=original.Script(snapshot,case);baseline.digit_function=engine.digit
    completed=engine.drive(baseline)
    for index in range(completed['events']):
        script=original.Script(snapshot,case);result=engine.drive(script,fail_at=index)
        assert result['status']==2 and result['D0']==SENTINEL and script.trace==baseline.trace[:index]
        prefix=original.Script(snapshot,case);prefix.digit_function=engine.digit
        # Replay the already original-matched public trace independently of
        # the continuation engine. This lane uses supplied digit returns.
        assert not case.get('linked_digit')
        for event in baseline.trace[:index]:
            if event[0]=='r':assert prefix.read(event[1],event[2])==event[3]
            elif event[0]=='w':prefix.write(*event[1:])
            else:prefix.call(event[1],event[2])
        assert prefix.memory==script.memory and prefix.trace==script.trace
        terminal=result['state'];before=bytes(terminal);request=Request();out_before=bytes(request)
        assert engine.advance(c.byref(terminal),None,c.byref(request))==2 and bytes(terminal)==before and bytes(request)==out_before
        guards.append(dict(case='failed_completion',at=index,earlier_effects_retained=True,no_more_requests=True,out_D0_unchanged=True))
    # The counter cannot silently wrap and accidentally reuse request IDs.
    state=Flow();assert engine.begin(c.byref(state),23,0)==0;state.pending.sequence=0xffffffffffffffff
    reply=Completion(23,0xffffffffffffffff,1,0)
    assert engine.advance(c.byref(state),c.byref(reply),c.byref(request))==5
    assert engine.result(c.byref(state),c.byref(output))==5 and output.value==SENTINEL
    guards.append(dict(case='sequence_exhaustion',new_request_ID_not_reused=True))
    save(out/'protocol-guards.json',guards)
    return guards

def interleave(engine,snapshot,cases,out):
    selected=[next(x for x in cases if x['name']=='confirm_123_456'),next(x for x in cases if x['name']=='confirm_966_719')]
    jobs=[]
    for i,case in enumerate(selected):
        script=original.Script(snapshot,case);script.digit_function=engine.digit
        state=Flow();assert engine.begin(c.byref(state),100+i,case['incoming'][0])==0
        request=Request();assert engine.advance(c.byref(state),None,c.byref(request))==0
        jobs.append(dict(state=state,request=request,script=script,status=0,completed=0))
    delayed=0;other_progress=0;timeline=[]
    for quantum in range(10000):
        if all(job['status']==1 for job in jobs):break
        for index,job in enumerate(jobs):
            if job['status']==1:continue
            req=job['request']
            if index==0 and req.kind==7 and req.address==0xdf60 and delayed<50:
                before=bytes(job['state']);trace_count=len(job['script'].trace)
                assert engine.advance(c.byref(job['state']),None,c.byref(req))==0
                assert bytes(job['state'])==before and len(job['script'].trace)==trace_count
                delayed+=1;continue
            if index==1 and 0<delayed<50:other_progress+=1
            value=effect(job['script'],req);reply=Completion(req.context,req.sequence,value,0)
            job['status']=engine.advance(c.byref(job['state']),c.byref(reply),c.byref(req));job['completed']+=1
            assert job['status'] in [0,1]
            if job['status']==1:timeline.append(dict(context=100+index,done_at_host_quantum=quantum))
    else:raise AssertionError('Interleaved jobs did not finish')
    assert delayed==50 and other_progress>0 and timeline[0]['context']==101
    for index,job in enumerate(jobs):
        baseline=original.Script(snapshot,selected[index]);expected=original.original(baseline,selected[index],set())
        output=c.c_uint32(SENTINEL);assert engine.result(c.byref(job['state']),c.byref(output))==1
        assert output.value==expected and job['script'].trace==baseline.trace and job['script'].memory==baseline.memory
        assert sum(event[:2]==['call',0xdf60] for event in job['script'].trace)==1
    report=dict(delayed_context=100,delayed_target='0xdf60',pending_host_quanta=delayed,other_job_operations_while_pending=other_progress,
        completion_order=timeline,helper_executed_once=True,both_original_traces_and_RAM_and_D0_match=True,
        worlds_are_separate=True,actual_Jaguar_task_context_switch=False,
        scope='Two independent logical bus worlds, round-robin host driver. Request pending while another context advances; no game CPU/IRQ/device time claim.')
    save(out/'interleaved-contexts.json',report);return report

def frozen_clock(engine,snapshot,cases,out):
    case=json.loads(json.dumps(next(x for x in cases if x['name']=='cancel')));case['clock']=[1000]
    script=original.Script(snapshot,case);script.digit_function=engine.digit
    state=Flow();request=Request();engine.begin(c.byref(state),500,case['incoming'][0]);engine.advance(c.byref(state),None,c.byref(request))
    clock_reads=0
    for step in range(300):
        if request.kind==3 and request.address==0x778cc:clock_reads+=1
        value=effect(script,request);reply=Completion(request.context,request.sequence,value,0)
        assert engine.advance(c.byref(state),c.byref(reply),c.byref(request))==0
    assert clock_reads>250 and state.deadline==1075
    case['clock']=[1075]
    for step in range(100):
        value=effect(script,request);reply=Completion(request.context,request.sequence,value,0)
        status=engine.advance(c.byref(state),c.byref(reply),c.byref(request))
        if status==1:break
        assert status==0
    else:raise AssertionError('Clock completion did not resume')
    report=dict(nonadvancing_clock_requests=clock_reads,host_steps_before_clock_advance=300,resumed_after_clock_advance=True,
        original_timeout_added=False,one_effect_per_completion=True,scope='Supplied clock values; no physical frame/timer claim.')
    save(out/'frozen-clock.json',report);return report

def main():
    out=ROOT/'verification/coordinate-flow'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=RESTORE/'biwn_coordinate_flow.c';header=RESTORE/'biwn_coordinate_flow.h';inspect_source(source,out)
    library=out/'libcoordinate-flow.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(RESTORE),str(source),str(RESTORE/'biwn_inventory_select.c'),'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    engine=Engine(library);snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    prior=json.loads((ROOT/'verification/readable-coordinate-entry-current.json').read_text())
    coverage,results,lanes=set(),[],[]
    cases_by_lane={}
    for name,key in [('standalone','standalone_proof'),('digit_connected','connected_proof')]:
        proof_path=Path(prior[key]);proof=json.loads(proof_path.read_text());folder=Path(proof['directory'])
        cases=json.loads((folder/'fixtures.json').read_text());cached=json.loads((folder/'case-results.json').read_text());assert len(cases)==len(cached)
        cases_by_lane[name]=cases
        expected_RAM,expected_d0=[],[]
        for index,case in enumerate(cases):
            reference=original.Script(snapshot,case);expected=original.original(reference,case,coverage)
            assert expected==cached[index]['full_D0'] and hashlib.sha256(json.dumps(reference.trace).encode()).hexdigest()==cached[index]['trace_sha256'] and hashlib.sha256(reference.memory).hexdigest()==cached[index]['RAM_sha256']
            script=original.Script(snapshot,case);result=engine.drive(script,context=1000+index)
            assert result['status']==1 and result['D0']==expected and script.trace==reference.trace and script.memory==reference.memory,case['name']
            expected_RAM.append(script.memory);expected_d0.append(expected)
            results.append(dict(lane=name,name=case['name'],events=result['events'],pending_repolls=result['pending_polls'],full_D0=expected,
                trace_sha256=hashlib.sha256(json.dumps(script.trace).encode()).hexdigest(),RAM_sha256=hashlib.sha256(script.memory).hexdigest(),copied_state_before_every_completion=True))
        native_dir=out/name;native_dir.mkdir()
        native,core=original.native_cases(snapshot,cases,expected_RAM,expected_d0,native_dir)
        lanes.append(dict(name=name,cases=len(cases),native_cases=len(native),prior_fixture_hashes_revalidated=True,
            prior_proof=str(proof_path),prior_proof_sha256=sha(proof_path)))
        print(name,len(cases),'native',len(native),flush=True)
    assert len(coverage)==166
    base_cases=cases_by_lane['standalone']
    guards=protocol_guards(engine,snapshot,next(x for x in base_cases if x['name']=='confirm_123_456'),out)
    concurrent=interleave(engine,snapshot,base_cases,out);clock=frozen_clock(engine,snapshot,base_cases,out)
    save(out/'case-results.json',results)
    for path in [source,header]:shutil.copy2(path,out/path.name)
    report=dict(status='resumable_coordinate_flow_original_and_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),
        source=str(source),source_sha256=sha(source),header=str(header),header_sha256=sha(header),library=str(library),library_sha256=sha(library),compiler=command,
        cases=sum(x['cases'] for x in lanes),lanes=lanes,original_instruction_locations=[166,166],protocol_guards=len(guards),
        pending_request_repolls=sum(x['pending_repolls'] for x in results),serialized_before_every_completion=True,
        no_internal_polling_loop_or_callbacks=True,one_external_request_per_completion=True,
        interleaved_contexts=concurrent,frozen_clock=clock,code_authorship='Codex coordinator',local_model_source_added=False,new_training=False,
        CPU_private_state_and_cycle_timing_verified=False,high_level_API_live_frame_runtime_changed=False,whole_game_complete=False,
        remaining_services='Requests are emitted for all original bus/helper interfaces; this protocol checker supplies helper effects except real C digit decoding in the connected lane. Earlier task/cleanup-controls integration is separate.',
        scope='New nonblocking host interface for full logical coordinate caller. Ordered original bus/helper trace, RAM and fullD0 match77standalone and70real-digit-connected fixtures;23selected native cases per lane. Every external effect can stay pending, state copies preserve continuation, stale/cross-context replies are rejected and a nonadvancing clock yields finite host steps. Two separate logical worlds interleave, one defersDF60 while the other finishes; this is not actual Jaguar scheduling, live source-frame installation, instruction timing or whole-game/standalone proof.')
    save(out/'report.json',report);save(ROOT/'verification/coordinate-flow-current.json',report)
    print(json.dumps(dict(status=report['status'],cases=report['cases'],guards=len(guards),repolls=report['pending_request_repolls'])),flush=True)

if __name__=='__main__':main()

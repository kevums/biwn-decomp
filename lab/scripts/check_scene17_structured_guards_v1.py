"""Complete guard qualification against the unchanged compiled host body.
Reuse the completed1024matrix;do not rerun it for a corrected guard assertion.
"""
import json
from datetime import datetime,timezone
from pathlib import Path
import scene17_host_runtime_v1 as support
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base
def main():
 prior=V/'scene17-structured-host-v1/20261020T230553.352177Z';old=read(prior/'status.json');assert old['status']=='terminal_failed'and"'budget': 1"in old['error']
 matrix=read(prior/'fixtures.json');assert len(matrix)==1024 and all(x['full_CPU_RAM_privateframes_orderedbus_match']for x in matrix);coverage=read(prior/'coverage.json');assert not coverage['uncovered']
 # Inputs were frozen immediately after the failed guard. Assert each remains
 # byte-identical before reusing the library from that full matrix.
 src=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1'
 for name in ['host-wrapper.c','scene-context.h','coordinator-reference.inc']:assert (src/name).read_bytes()==(prior/name).read_bytes(),name
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=base.cases();runtime=support.Runtime(prior/'libscene-draw-cpu.dylib',mapping['instructions_decoded']);out=V/'scene17-structured-guards-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[]
 try:
  for entry in [0xe03a,0x17e0e]:
   case=next(x for x in vectors if x['entry']==entry and(entry!=0x17e0e or any(y==[0x49c60,2,1]for y in x['initial'])));ram=base.fixture(snapshot,case)
   options=[({'missing':i},1)for i in range(6)]+[({'null_bus':True},1),({'null_cpu':True},1),({'null_service':True},1),({'budget':0},1),({'stop_flag':2},1),({'bad_pc':True},7)]
   options+=[({'budget':1},3 if entry==0x17e0e else 4)]
   if entry==0x17e0e:options+=[({'budget':1,'nested_budget':10000},4),({'fail':('read',2)},2),({'fail':('read',4)},2),({'fail':('write',4)},2),({'fail':('helper',0xe03a)},3)]
   for kwargs,expected in options:
    _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==expected and result['CPU_unchanged']and not result['errors'],(entry,kwargs,result);rows.append(dict(entry=hex(entry),options=kwargs,status=expected,CPU_unchanged=True))
   if entry==0x17e0e:
    original=runtime.scripted
    try:
     for fault in ['stack','return']:
      def scripted(state,target,fault=fault):
       original(state,target)
       if target==0xe0a6:
        if fault=='stack':state.registers[15]+=4
        else:runtime.device.direct(state.registers[15],4,0)
      runtime.scripted=scripted;_,_,result=runtime.translated(ram,case);assert result['status']==5 and result['CPU_unchanged']and not result['errors'],(fault,result);rows.append(dict(entry=hex(entry),helper='0xe0a6',fault=fault,status=5,CPU_unchanged=True))
    finally:runtime.scripted=original
 finally:runtime.close()
 save(out/'guards.json',rows);paths=[Path(__file__),Path(support.__file__),Path(base.__file__),prior/'checker-source-as-run.py',prior/'fixtures.json',prior/'coverage.json',prior/'status.json',prior/'libscene-draw-cpu.dylib',*list(src.glob('*')),out/'guards.json'];proof=dict(status='terminal_scene17_1024_matrix_reused_and_separate_guard_checks_pass',directory=str(out),completed_matrix_cases=1024,new_matrix_reruns=0,guard_cases=len(rows),candidate_entry='0x17e0e',new_predictions=0,new_training=False,target_machine_code_executed=False,host_code_unchanged=True,initial_full_run_status='terminal_failed_at_added_guard_after_matrix',initial_guard_failure_preserved=True,scope=__doc__+'Nested worklimit maps toserviceerror3;isolated outerworklimit4uses successful nestedprovider. CPUerrors preserveinputCPU;RAM effects may remain. Oldclear/rotation/internalPC providers retained. No freshgame/nativeconsole/IRQ claim.',source_sha256={str(p):sha(p)for p in paths if p.is_file()});save(out/'review.json',proof);save(V/'scene17-structured-guards-v1-current.json',proof);print(proof['status'],len(rows))
if __name__=='__main__':main()

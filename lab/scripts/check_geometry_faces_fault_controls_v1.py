"""Reject compiled semantic mutations with the same1142ECPU/RAM/entry oracle."""
import json,os
from pathlib import Path
from datetime import datetime,timezone
import check_deck_geometry_faces_v1 as m
ROOT=m.ROOT;save=m.save;sha=m.sha
def main():
 gate=ROOT/'verification/deck-geometry-faces-v1-current.json';good=json.loads(gate.read_text());assert good['status']=='terminal_complete_geometry_faces_CPU_RAM_match'and good['completed']==640
 for p,h in good['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
 out=ROOT/'verification/geometry-faces-fault-controls-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);original=Path(good['source']).read_text();rows=[];e=m.Engine()
 try:
  variants=[('logical_average',[('uint32_t out=(v>>1)|(v&0x80000000u);','uint32_t out=v>>1;')]),
   ('stale_counter',[('uint32_t *r=s->cpu.registers,v;\n for(unsigned n=9;','uint32_t *r=s->cpu.registers,v,before_gpu_counter;\n for(unsigned n=9;'),('deck_push(s,r[10]+r[0]);deck_call(s,0xe26c','deck_push(s,r[10]+r[0]);before_gpu_counter=deck_read(s,0x49b88,4);deck_call(s,0xe26c'),('r[1]=deck_read(s,0x49b88,4);deck_nz','r[1]=before_gpu_counter;deck_nz')]),
   ('address_ADDQ_changes_X',[('r[12]++;faces_move_word','r[12]=scene_alu16(s,r[12],1,0,0);faces_move_word')]),
   ('wrong_stack_cleanup',[('deck_adjust(s,18);','deck_adjust(s,20);')])]
  for name,changes in variants:
   text=original
   for a,b in changes:assert text.count(a)==1,(name,a);text=text.replace(a,b)
   source=out/(name+'.c');source.write_text(text);fn,lib=m.compile_source(source,out,name);failure=None
   for ram,initial,case in m.fixtures():
    if case['count']==0:continue
    expected,cpu,entries,_,_=e.original(ram,initial,case);status,actual,got,observed,_,errors=e.translated(fn,ram,initial,case)
    if status or errors or expected!=actual or m.cpu_dict(cpu)!=m.cpu_dict(got)or entries!=observed:
     failure=dict(case=case,status=status,errors=errors,CPU_match=m.cpu_dict(cpu)==m.cpu_dict(got),RAM_match=expected==actual,entries_match=entries==observed);break
   assert failure,name;save(out/(name+'-counterexample.json'),failure);rows.append(dict(mutation=name,source=str(source),source_sha256=sha(source.read_bytes()),compiled_library=str(lib),rejected=True,counterexample=failure));print(name,'rejected',flush=True)
 finally:e.native.close()
 save(out/'cases.json',rows);proof=dict(status='terminal_four_geometry_faces_semantic_faults_rejected',directory=str(out),new_training=False,new_predictions=0,native_disc_changed=False,negative_controls=rows,source_sha256={str(p):sha(p.read_bytes())for p in [Path(__file__),Path(m.__file__),gate,out/'cases.json']},scope=__doc__+' Logical shift in signed average,stale postGPUcounter,address-register ADDQincorrectlychangingX,and wrong argument cleanup all compile and fail finite originalCPU/2MBRAM/entry comparisons. Not arbitrary mutation or hardware fidelity coverage.')
 save(out/'review.json',proof);save(ROOT/'verification/geometry-faces-fault-controls-v1-current.json',proof)
if __name__=='__main__':main()

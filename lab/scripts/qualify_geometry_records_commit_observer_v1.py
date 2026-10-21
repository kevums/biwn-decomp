"""Fault controls for exact read-only record-builder/provider witness source.

Synthetic host CPU/RAM fixtures;these do not execute a game or establish timing.
"""
import ctypes as c,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from geometry_records_observer_build_v1 import with_aliases

def main():
 bp=V/'native-geometry-records-disc-build-v1-current.json';b=with_aliases(read(bp));gp=V/'geometry-records-geometry-observer-qualified-v1-current.json';g=read(gp);text=Path(g['observer']).read_text();start=text.index('/* R33_RECORDS_WATCH_BEGIN:');end=text.index('/* R33_RECORDS_WATCH_END */',start)
 out=V/'geometry-records-commit-observer-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory;\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *o){*o=current;}\n'''
 hooks='''
void clear(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(r33_pending,0,sizeof(r33_pending));memset(r33_provider,0,sizeof(r33_provider));memset(r33_provider_entries,0,sizeof(r33_provider_entries));memset(r33_provider_returns,0,sizeof(r33_provider_returns));r33_entries=r33_returns=r33_errors=r33_original_steps=r33_protected=0;}
void put(uint32_t a,uint32_t v){ram[a]=v>>24;ram[a+1]=v>>16;ram[a+2]=v>>8;ram[a+3]=v;}
void word(uint32_t a,uint16_t v){ram[a]=v>>8;ram[a+1]=v;}
void reg(unsigned n,uint32_t v){current.r[n]=v;}
void pc(uint32_t a){current.pc=a;r33_watch(a);}
void snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}
uint64_t stat(unsigned n){switch(n){case 0:return r33_errors;case 1:return r33_pending_total();case 2:return r33_entries;case 3:return r33_returns;case 4:return r33_protected;case 5:return r33_provider_entries[0];case 6:return r33_provider_returns[0];case 7:return r33_provider_entries[1];case 8:return r33_provider_returns[1];default:return r33_original_steps;}}
'''
 source=out/'fixture.c';source.write_text(stub+text[start:end]+hooks);library=out/'fixture.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 f=c.CDLL(str(library));f.put.argtypes=[c.c_uint32,c.c_uint32];f.word.argtypes=[c.c_uint32,c.c_uint16];f.reg.argtypes=[c.c_uint,c.c_uint32];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64
 syms=b['shared_Deck_symbols'];variants=['legal_copy','legal_matrix','legal_both','bad_initial_PC','bad_initial_active','bad_initial_error','duplicate_begin','missing_begin','invalid_task','original_body_executed','bad_provider_CPU','bad_provider_bank','bad_provider_logical_PC','bad_provider_saved_SP','bad_provider_logical_SP','bad_provider_return_word','bad_provider_logical_return','duplicate_provider','missing_provider_entry','missing_provider_return','provider_frame_corruption','provider_stack_corruption','bad_provider_return_SP','bad_final_D2','bad_final_SP','bad_final_bank','bad_final_PC','bad_final_upper_SR','bad_final_active','bad_final_error','missing_end','duplicate_end'];rows=[]
 for name in variants:
  for flags in range(64):
   f.clear();slot_id=[0,1,6,100][flags%4];slot=b['deck_arena_address']+slot_id*1024;frame=slot+144;task=0xc0928+slot_id*1024;sp=task+[0x3c0,0x3be,0x200][flags%3];sr=(0x2000 if flags>=32 else 0)|(flags%32);usp=0x170000 if flags>=32 else sp;ssp=sp if flags>=32 else 0x1d0000
   f.put(0xc0920,task+1 if name=='invalid_task'else task)
   for n in range(16):f.put(frame+4+n*4,sp if n==15 else 0x12340000+n)
   f.put(frame+68,0 if name=='bad_initial_PC'else 0x170a0);f.put(frame+72,usp);f.put(frame+76,ssp);f.word(frame+80,sr);f.put(frame+114,0 if name=='bad_initial_active'else 1);f.put(frame+94,1 if name=='bad_initial_error'else 0)
   if name!='missing_begin':f.pc(syms['biwn_v33_records_begin'])
   if name=='duplicate_begin':f.pc(syms['biwn_v33_records_begin'])
   if name=='original_body_executed':f.pc(0x170a2)
   tags=[1,2]if name=='legal_both'else[2]if name=='legal_matrix'else[1]
   for tag in tags:
    hsp=sp-64;target=0xe3e0 if tag==1 else 0xe220;ret=0x17166 if tag==1 else 0x172c4
    f.put(frame+102,frame+6 if name=='bad_provider_CPU'else frame+4);f.put(frame+106,hsp+2 if name=='bad_provider_saved_SP'else hsp);f.put(frame+110,ret+2 if name=='bad_provider_logical_return'else ret)
    f.put(frame+(76 if flags>=32 else 72),hsp+2 if name=='bad_provider_bank'else hsp)
    f.put(frame+64,hsp+2 if name=='bad_provider_logical_SP'else hsp);f.put(frame+68,target+2 if name=='bad_provider_logical_PC'else target);f.put(hsp,2 if name=='bad_provider_return_word'else syms['biwn_v4_scene_helper_return']);f.reg(15,hsp)
    if name!='missing_provider_entry':f.pc(target)
    if name=='duplicate_provider':f.pc(target)
    if name=='provider_frame_corruption':f.put(frame+90,1)
    if name=='provider_stack_corruption':f.put(slot+650,1)
    f.reg(15,hsp+6 if name=='bad_provider_return_SP'else hsp+4)
    if name!='missing_provider_return':f.pc(syms['biwn_v4_scene_helper_return'])
   if name=='bad_final_upper_SR':f.word(frame+80,sr^0x400)
   f.put(frame+64,sp+2 if name=='bad_final_SP'else sp);f.put(frame+72,usp+2 if name=='bad_final_bank'else usp);f.put(frame+76,ssp);f.put(frame+68,0 if name=='bad_final_PC'else 0x17324)
   if name=='bad_final_D2':f.put(frame+12,0)
   if name=='bad_final_active':f.put(frame+114,0)
   if name=='bad_final_error':f.put(frame+94,1)
   if name!='missing_end':f.pc(syms['biwn_v33_records_end'])
   if name=='duplicate_end':f.pc(syms['biwn_v33_records_end'])
   values=[f.stat(n)for n in range(10)];accepted=values[0]==values[1]==values[9]==0 and values[2]==values[3]==1 and values[5]==values[6]and values[7]==values[8]and values[4]==len(tags)
   assert accepted==name.startswith('legal_'),(name,flags,values)
   rows.append(dict(fault=name,CCR=flags%32,supervisor=flags>=32,task_slot=slot_id,accepted=accepted,stats=values))
 save(out/'cases.json',rows);proof=dict(status='terminal_readonly_record_commit_provider_fault_controls_pass',directory=str(out),observer=g['observer'],fixture=str(source),fixture_library=str(library),controls=len(rows),legal_controls=sum(x['accepted']for x in rows),rejected_controls=sum(not x['accepted']for x in rows),all32CCR_both_banks=True,task_slots=[0,1,6,100],new_predictions=0,new_training=False,host_guest_RAM_writes=0,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,gp,Path(g['observer']),ROOT/'scripts/geometry_records_commit_observer_v1.inc.c',source,library,out/'cases.json']},scope=__doc__+'Includes missing/duplicate body boundaries,entry state,actual provider metadata and returnSP,suspended frame/stack corruption,originalbodyexecution,preservedD2/finalPC/SP/banks/active/error and unfinished provider. Actual CPU witness lanes still require separate qualification.');save(out/'review.json',proof);save(V/'geometry-records-commit-observer-qualified-v1-current.json',proof);print(proof['status'],len(rows),proof['legal_controls'],flush=True)
if __name__=='__main__':main()

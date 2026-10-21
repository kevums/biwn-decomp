"""Recover observed entry modes/IDs and original-table callback paths from traces."""
import ctypes as c,json,re,collections
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
class Event(c.Structure):_fields_=[('frame',c.c_uint32),('pc',c.c_uint32),('cpu',CPU),*[(n,c.c_uint32)for n in ['X','Z','mode','floor','scene','tile']]]
def read(p):return json.loads(Path(p).read_text())
def main():
 assert c.sizeof(Event)==112;v=ROOT/'verification';bp=v/'native-actor-initialize-disc-build-current.json';build=read(bp);stage=Path(build['derived_stage']).read_bytes();baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert stage[0x13620-0x4000:0x13706-0x4000]==baseline[0x13620:0x13706]
 src=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-initialize-reference.c';callbacks={int(a,16):int(b,16)for a,b in re.findall(r'case 0x([0-9a-f]+)u:r\[18\]=0x([0-9a-f]+)u',src.read_text())};assert len(callbacks)==15
 result={};paths=[Path(__file__),src,bp,Path(build['derived_stage']),ROOT/'scripts/native_gameplay_observer.c'];sequences=[]
 for kind in ['candidate','control']:
  pointer=v/f'native-actor-initialize-{kind}-current.json';run=read(pointer);f=Path(run['directory'])/'candidate/gameplay-events.bin';raw=f.read_bytes();assert len(raw)%112==0 and run['observations']['event_record_bytes']==112
  rows=[]
  for offset in range(0,len(raw),112):
   e=Event.from_buffer_copy(raw[offset:offset+112])
   if e.pc!=0x134dc:continue
   id=e.cpu.r[9]&65535;index=(id-4)&65535;table=None;target=None;callback=0
   if index<=114:
    table=int.from_bytes(baseline[0x13620+2*index:0x13622+2*index],'big');target=0x13620+(table if table<32768 else table-65536);callback=callbacks.get(target,0)
   rows.append(dict(frame=e.frame,id=id,slot=e.cpu.r[1]&65535,entry_mode=e.mode,table_target=hex(target)if target else None,task_callback=hex(callback)if callback else None))
  assert len(rows)==12 and all(x['slot']<40 for x in rows);modes=dict(collections.Counter(x['entry_mode']for x in rows));tasks=dict(collections.Counter(x['task_callback']for x in rows if x['task_callback']));assert modes=={1:3,2:9}and tasks=={'0xf4d8':2,'0x15140':1,'0xedc4':1}
  finished=sum(x['table_target']=='0x137da'for x in rows);assert finished==8 and sum(tasks.values())+sum(modes.values())==run['observations']['ai_helper_entries']==16
  result[kind]=dict(entries=rows,observed_entry_modes=modes,original_table_task_callbacks=tasks,finished_table_case=finished,invalid_ids_or_table_case=0,distinct_live_callback_targets=len(tasks),callback_targets_component_only=len(callbacks)-len(tasks),aggregate_helper_calls=16,helper_partition_derived_from_entry_modes_and_original_table=True,per_helper_type_counter_emitted=False)
  sequences.append([{k:value for k,value in row.items()if k!='frame'}for row in rows]);paths.extend([pointer,f])
 assert sequences[0]==sequences[1]
 out=v/'actor-initialize-live-paths'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='terminal_actual_initializer_entry_paths_extracted',directory=str(out),variants=result,entry_path_sequence_equal_ignoring_frames=True,scope=__doc__+' ID/slot are read from the observed13AE0child-entry register ABI, independently checked by the live monitor. Table bytes are identical to original. Helper-type partition is derived, not direct per-type instrumentation. Invalid/no-geometry/12othercallback branches remain component-only; no general gameplay coverage claim.',source_sha256={str(p):sha(p)for p in paths},new_predictions=0);save(out/'protocol.json',state);save(v/'actor-initialize-live-paths-current.json',state);print(json.dumps(dict(status=state['status'],modes={'1':3,'2':9},callbacks={'0xf4d8':2,'0x15140':1,'0xedc4':1},other_callbacks_component_only=12)))

if __name__=='__main__':main()

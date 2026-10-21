"""Compare read-only geometry timelines; distinguish temporal evidence from cause."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 tracep=V/'native-geometry-timing-trace-v1-current.json';trace=read(tracep);assert trace['status']=='terminal_read_only_geometry_timing_timelines_baseline_identical'
 for p,digest in trace['source_sha256'].items():assert sha(p)==digest,p
 bp=V/'native-Deck-debug-disc-build-v1-current.json';build=read(bp);stage=Path(build['derived_stage']);payload=Path(build['component']);assert sha(stage)==build['derived_stage_sha256']and sha(payload)==build['component_sha256'];base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();resident=payload.read_bytes();md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
 def decode(pc):
  if build['resident_address']<=pc<build['resident_address']+len(resident):raw=resident[pc-build['resident_address']:pc-build['resident_address']+16];origin='frozen resident image'
  else:raw=base[pc:pc+16];origin='original baseline code'
  ins=list(md.disasm(raw,pc,count=1));return dict(pc=hex(pc),instruction=(ins[0].mnemonic+' '+ins[0].op_str)if ins else None,source=origin)
 out=V/'native-geometry-timing-analysis-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);lanes={}
 columns=['frame','ordinal','pc','previous','reason','movie0','movie1','held','task','sp']
 for lane,proof in trace['lanes'].items():
  data=read(proof['timeline']);assert not data['overflow'];rows=[dict(zip(columns,row))for row in data['rows']];entries=[row for row in rows if row['pc']==0x11ad4];returns=[row for row in rows if row['pc']==(1499116 if lane=='candidate'else 0x11b4a)];assert len(entries)==len(returns)==18
  calls=[]
  for i,(a,b)in enumerate(zip(entries,returns),1):
   assert a['task']==b['task']and(a['frame'],a['ordinal'])<(b['frame'],b['ordinal']);calls.append(dict(call=i,task=hex(a['task']),entry_offset=a['frame']-24564,return_offset=b['frame']-24564,entry_ordinal=a['ordinal'],return_ordinal=b['ordinal'],frame_boundaries_crossed=b['frame']-a['frame']))
  transitions={key:[]for key in ['movie0','movie1','held']};last=rows[0]
  for row in rows[1:]:
   for key in transitions:
    if row[key]!=last[key]:transitions[key].append(dict(offset=row['frame']-24564,ordinal=row['ordinal'],old=last[key],value=row[key],observed_at=hex(row['pc']),preceding_observed_instruction=decode(row['previous']),task=hex(row['task'])))
   last=row
  lanes[lane]=dict(calls=calls,transitions=transitions)
 comparisons=[]
 for a,b in zip(lanes['candidate']['calls'],lanes['control']['calls']):
  comparisons.append(dict(call=a['call'],candidate_entry=a['entry_offset'],control_entry=b['entry_offset'],candidate_return=a['return_offset'],control_return=b['return_offset'],return_frame_shift=a['return_offset']-b['return_offset'],candidate_frame_boundaries=a['frame_boundaries_crossed'],control_frame_boundaries=b['frame_boundaries_crossed']))
 transition_comparisons={}
 for key in ['movie0','movie1','held']:
  a=lanes['candidate']['transitions'][key];b=lanes['control']['transitions'][key]
  same=[(x['old'],x['value'])for x in a]==[(x['old'],x['value'])for x in b]
  transition_comparisons[key]=dict(candidate_changes=len(a),control_changes=len(b),same_value_sequence=same,paired_offset_shifts=[x['offset']-y['offset']for x,y in zip(a,b)]if same else None)
 save(out/'lanes.json',lanes);save(out/'calls.json',comparisons);save(out/'transitions.json',transition_comparisons)
 result=dict(status='terminal_actual_geometry_timing_and_public_flag_transition_analysis',directory=str(out),trace=str(tracep),geometry_calls_each=18,calls=comparisons,transitions=transition_comparisons,new_predictions=0,new_training=False,discs_changed=False,inputs_changed=False,all_observed_frame_records_and_final_states_equal_baseline=True,fidelity_verified=False,scope=__doc__+' Trace observes CPU instruction boundaries. Frame ordinals are executed-instruction counts,not cycle counts. Preceding observed instruction disassembly is from frozen original/resident code and is a writer candidate;asynchronous effects and IRQ need separate attribution. Paired call ordinal is not assumed to establish identical input state. This experiment leaves the62video differences intact,including the unpaired candidate tail.')
 report=ROOT/'reports/Native Geometry Timing Trace Analysis.txt';report.write_text('NATIVE GEOMETRY — INSTRUCTION TIMELINE\n\n'+json.dumps(result,indent=2)+'\n\nDetailed event transitions:'+str(out/'lanes.json')+'\n');result['report']=str(report);paths=[Path(__file__),tracep,bp,stage,payload,ROOT/'render-assets/biwn-inventory-baseline.bin',out/'lanes.json',out/'calls.json',out/'transitions.json',report];result['source_sha256']={str(p):sha(p)for p in paths};save(out/'review.json',result);save(V/'native-geometry-timing-analysis-v1-current.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['source_sha256','scope']},indent=2))
if __name__=='__main__':main()

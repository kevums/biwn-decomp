"""Original movement+both collisions versus their coupled native C bodies.

Common parent compiled geometry plus original10652/direction/division execute.
Only E220GPU effects are prescribed. Compare full returned CPU/SR/banks, physical
helper-entry CPU/SR/SP/arguments, orderedpublicaccess and public2MBRAM. Private
frames/installedcode/returnPCs excluded. Finite validscene fixtures, not live
GPU/task scheduling or a general stack bound.
"""
import argparse,json,os
from pathlib import Path
from datetime import datetime,timezone
import native_movement_collision_joint_engine as e

def prepare(collision_proof):
 r=e.ROOT;bp=r/'verification/native-actor-move-disc-build-current.json';b=e.g.read(bp);g=e.g.read(collision_proof)
 for p,h in g['source_sha256'].items():assert e.g.sha(p)==h,p
 baseline=(r/'render-assets/biwn-inventory-baseline.bin').read_bytes();snapshot=bytearray(baseline);snapshot[0x4000:0x100000]=Path(b['derived_stage']).read_bytes();resident=b['resident_address'];full=Path(b['component']).read_bytes();snapshot[resident:resident+len(full)]=full
 for a,w in {e.ENTRY:8,**e.g.COLL_PATCH_WIDTHS}.items():snapshot[a:a+w]=baseline[a:a+w]
 e.BASE=b['actor_move_start'];e.PARENT_RANGE=(resident,resident+b['linked_component_bytes']);e.COLLBASE=g['code_address'];e.COLL_PAYLOAD=Path(g['binary']).read_bytes();e.COLL_SYMBOLS=g['symbols'];payload=full[e.BASE-resident:b['actor_move_end']-resident];assert len(payload)==2960 and e.COLLBASE+len(e.COLL_PAYLOAD)<=0x1ff000-8192
 return bytes(snapshot),payload,b['symbols'],b,g

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--collision-proof',type=Path,default=e.ROOT/'verification/native-actor-collision-prototype-current.json');args=ap.parse_args();snapshot,payload,symbols,build,gate=prepare(args.collision_proof);allcases=e.vectors();cases=[allcases[i]for i in[0,16,32,80,96,112,160,176]][:args.limit]if args.limit else allcases
 out=e.ROOT/'verification/native-movement-collision-joint'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);e.g.save(out/'parent-build.json',build);e.g.save(out/'collision-proof.json',gate);e.g.save(out/'fixtures.json',cases)
 inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),Path(e.g.motion.__file__),Path(e.g.direction.__file__),out/'parent-build.json',out/'collision-proof.json',Path(build['component']),Path(build['derived_stage']),Path(gate['binary']),Path(gate['ELF']),e.ROOT/'scripts/check_biwn_scheduler.py',e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];hashes={str(p):e.g.sha(p)for p in inputs};state=dict(status='checking_native_movement_collision_joint',directory=str(out),pid=os.getpid(),planned=len(cases),completed=0,source_sha256=hashes,collision_proof=str(out/'collision-proof.json'),new_predictions=0);rows=[];coverage=set();n=e.Native()
 def mark():e.g.save(out/'protocol.json',state);e.g.save(e.ROOT/'verification/native-movement-collision-joint-active.json',state)
 mark()
 try:
  for i,case in enumerate(cases):
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[k for k in ['ram','registers','trace']if a[k]!=b[k]]
   if diff:e.g.save(out/'mismatch.json',dict(index=i,case=case,differences=diff,original_trace=a['trace'],compiled_trace=b['trace'],original_regs=a['registers'],compiled_regs=b['registers']));raise AssertionError('Joint ordered comparison failed')
   an=e.replay(n,snapshot,case,payload,symbols,False,a);bn=e.replay(n,snapshot,case,payload,symbols,True,b)
   if an!=bn:e.g.save(out/'native-mismatch.json',dict(index=i,case=case,original=an,compiled=bn));raise AssertionError('Joint fullCPU/SR/helper comparison failed')
   coverage.update(a['coverage']);rows.append(dict(index=i,original_steps=len(a['machine']),compiled_steps=len(b['machine']),original_depth=a['private_depth'],compiled_depth=b['private_depth'],calls=len(an['events']),outdoor_entries=sum(s['pc']==0x13b5a for s in a['machine']),indoor_entries=sum(s['pc']==0x13bb0 for s in a['machine'])));state['completed']=len(rows)
   if i%64==0:mark();print('Joint movement/collision',i+1,'/',len(cases),flush=True)
  assert all(e.g.sha(p)==h for p,h in hashes.items());e.g.save(out/'results.json',rows);state.update(status='terminal_native_movement_collision_joint_preflight_pass'if args.limit else'terminal_native_movement_collision_joint_pass',cases=len(rows),completed=len(rows),max_private_depth=max(x['compiled_depth']for x in rows),max_original_depth=max(x['original_depth']for x in rows),outdoor_entries=sum(x['outdoor_entries']for x in rows),indoor_entries=sum(x['indoor_entries']for x in rows),original_sites=sorted(coverage),scope=__doc__);mark()
  if not args.limit:e.g.save(e.ROOT/'verification/native-movement-collision-joint-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','cases','max_private_depth','outdoor_entries','indoor_entries']}))
 except BaseException as error:state.update(status='terminal_native_movement_collision_joint_failed',error=repr(error));mark();raise
 finally:n.close()
if __name__=='__main__':main()

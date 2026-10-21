"""All three original-facing actor/sprite roots together at their final addresses.

The original reference restores13AE0/134DC/137E0. The candidate replaces all
three; both retain the same previously compiled10520/105DAand common parent.
Only four external services are prescribed. Original and native CPU lanes
compare complete returned CPU/SR/banks, helper-entry CPU/SP/SR/arguments,
ordered public memory accesses and public2MBRAM. This is a finite fixture proof,
not real resource decoding, task scheduling, timing or arbitrary faults.
"""
import copy,json,os
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_actor_triple_engine as e
import check_biwn_native_sprite_create_linked as sc

def main():
 r=e.ROOT;v=r/'verification';bp=v/'native-actor-initialize-disc-build-current.json';gp=v/'native-sprite-create-linked-current.json';build=e.g.read(bp);gate=e.g.read(gp)
 assert gate['status']=='terminal_original_ABI_sprite_create_pass'and gate['cases']==1228
 for p,h in gate['source_sha256'].items():assert e.g.sha(p)==h,p
 baseline=(r/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert e.g.sha(r/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
 assert e.g.sha(build['component'])==build['component_sha256']and e.g.sha(build['derived_stage'])==build['derived_stage_sha256']
 payload=Path(build['component']).read_bytes();snapshot=bytearray(baseline);snapshot[0x4000:0x100000]=Path(build['derived_stage']).read_bytes();resident=build['resident_address'];snapshot[resident:resident+len(payload)]=payload
 for a in [0x13ae0,0x134dc,0x137e0]:snapshot[a:a+8]=baseline[a:a+8]
 e.BASE=build['actor_dispatch_start'];e.INITBASE=build['actor_initialize_start'];e.SPRITEBASE=gate['code_address'];e.PARENT_RANGE=(resident,resident+len(payload))
 dispatch=payload[e.BASE-resident:build['actor_dispatch_end']-resident];e.INIT_PAYLOAD=payload[e.INITBASE-resident:build['actor_initialize_end']-resident];e.INIT_SYMBOLS=build['symbols'];e.SPRITE_PAYLOAD=Path(gate['binary']).read_bytes();e.SPRITE_SYMBOLS=gate['symbols'];symbols=build['symbols']
 assert len(dispatch)==572 and len(e.INIT_PAYLOAD)==1620 and len(e.SPRITE_PAYLOAD)==2180
 rows=e.vectors()
 for original in sc.vectors():
  c=copy.deepcopy(original);c['entry']=0x13ae0;c['sprite_joint_extra']=True
  id=c['params'][0];signed=id if id<32768 else id-65536
  flag=next(value for a,w,value in reversed(c['initial'])if a==0x4208c+id and w==1)
  c['initial'].append([0x4208c+signed,1,flag]);rows.append(c)
 out=v/'native-actor-triple'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 e.g.save(out/'parent-build.json',build);e.g.save(out/'sprite-component.json',gate);e.g.save(out/'fixtures.json',rows)
 inputs=[Path(__file__),Path(e.__file__),Path(sc.__file__),out/'parent-build.json',out/'sprite-component.json',Path(build['component']),Path(build['derived_stage']),Path(gate['binary']),Path(gate['ELF']),Path(e.g.__file__),Path(e.g.prior.__file__),r/'scripts/check_biwn_scheduler.py',r/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
 hashes={str(p):e.g.sha(p)for p in inputs};state=dict(status='checking_three_original_ABI_roots',pid=os.getpid(),directory=str(out),planned=len(rows),completed=0,source_sha256=hashes,component_proof=str(out/'sprite-component.json'),source=str(sc.ND/'sprite-create-reference.c'),new_predictions=0,disc_integrated=False)
 def mark():e.g.save(out/'protocol.json',state);e.g.save(v/'native-actor-triple-active.json',state)
 mark();results=[];coverage=set();native=e.Native()
 try:
  for i,c in enumerate(rows):
   a=e.execute(bytes(snapshot),c,dispatch,symbols,False);b=e.execute(bytes(snapshot),c,dispatch,symbols,True)
   diffs=[k for k in ['ram','registers','trace']if a[k]!=b[k]]
   if diffs:e.g.save(out/'mismatch.json',dict(index=i,case=c,differences=diffs,original_trace=a['trace'],compiled_trace=b['trace'],original_regs=a['registers'],compiled_regs=b['registers']));raise AssertionError('Triple ordered comparison failed')
   an=e.replay(native,bytes(snapshot),c,dispatch,symbols,False,a);bn=e.replay(native,bytes(snapshot),c,dispatch,symbols,True,b)
   if an!=bn:e.g.save(out/'native-mismatch.json',dict(index=i,case=c,original=an,compiled=bn));raise AssertionError('Triple full CPU/SR/bank/helper comparison failed')
   coverage.update(a['coverage']);results.append(dict(index=i,original_depth=a['private_depth'],compiled_depth=b['private_depth'],original_steps=len(a['machine']),compiled_steps=len(b['machine']),calls=len(an['events'])))
   if i%64==0:state['completed']=len(results);mark();print('Triple',len(results),'/',len(rows),flush=True)
  assert all(e.g.sha(p)==h for p,h in hashes.items());e.g.save(out/'results.json',results)
  state.update(status='terminal_three_original_ABI_roots_pass',completed=len(results),cases=len(results),original_sites=sorted(coverage),max_private_depth=max(x['compiled_depth']for x in results),max_original_depth=max(x['original_depth']for x in results),code_addresses=[hex(e.BASE),hex(e.INITBASE),hex(e.SPRITEBASE)],scope=__doc__);mark();e.g.save(v/'native-actor-triple-current.json',state);print(state['status'],len(rows),state['max_private_depth'],flush=True)
 except BaseException as error:state.update(status='terminal_three_original_ABI_roots_failed',completed=len(results),error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()

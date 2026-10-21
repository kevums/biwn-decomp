"""Cold fixed-pad controls retain native25 layout and selectively restore originals.
All derivative bytes are declared and checked; no runtime guest-state edits.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16

def main():
 fp=ROOT/'verification/native-free-fixed-route-current.json';fixed=json.loads(fp.read_text());fd=Path(fixed['directory']);template=fd/'fresh-fixed-free-route.py';assert sha(template)==fixed['source_sha256'][str(template)]
 rp=ROOT/'verification/native-free-route-current.json';route=json.loads(rp.read_text());assert sha(rp)==fixed['source_route_proof_sha256'];rd=Path(route['directory']);observer_source=rd/'free-observer.c';assert sha(observer_source)==route['source_sha256'][str(observer_source)]
 bp=ROOT/'verification/native-free-disc-build-current.json';build=json.loads(bp.read_text());assert sha(bp)==fixed['build_proofs'][str(bp)];disc=Path(build['derived_disc']);assert sha(disc)==build['derived_disc_sha256']
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset'];original=(session/'nextstage-68000-candidate.bin').read_bytes();native=Path(build['derived_stage']).read_bytes();assert sha(build['derived_stage'])==build['derived_stage_sha256'];LOAD=0x4000
 out=ROOT/'verification/native-free-timing-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);frames=6400
 recorded=json.loads((fd/'recorded-controller-input.json').read_text());inputs=out/'prefix-input.json';save(inputs,dict(windows=[{**w,'stop_frame':min(w['stop_frame'],frames+1)}for w in recorded['windows']if w['start_frame']<=frames]))
 variants={}
 for name,source_free,source_init in [('layout_only',False,False),('initializer_only',False,True),('free_only',True,False)]:
  stage=bytearray(native);changes=[]
  def replace(a,data):
   off=a-LOAD;old=bytes(stage[off:off+len(data)]);stage[off:off+len(data)]=data;changes.append(dict(address=a,original=old.hex(),replacement=data.hex()))
  if not source_free:replace(0x1545c,original[0x1545c-LOAD:0x15464-LOAD])
  if not source_init:
   replace(0x1557a,original[0x1557a-LOAD:0x15584-LOAD])
   for a,v in [(0x1557c,build['heap_start']),(0x1558c,build['heap_start']),(0x15592,build['heap_start']),(0x15598,build['heap_start']+4),(0x1559e,build['heap_start']+8)]:replace(a,v.to_bytes(4,'big'))
  target=out/(name+'.cdi');subprocess.run(['/bin/cp','-c',str(disc),str(target)],check=True)
  with target.open('r+b')as f:
   for change in changes:
    off=change['address']-LOAD;f.seek(offset+off);assert f.read(len(bytes.fromhex(change['original'])))==swap16(bytes.fromhex(change['original']));f.seek(offset+off);f.write(swap16(bytes.fromhex(change['replacement'])))
   f.flush();os.fsync(f.fileno())
  with target.open('rb')as f:f.seek(offset);assert swap16(f.read(len(stage)))==stage
  intervals=[(offset+x['address']-LOAD,offset+x['address']-LOAD+len(bytes.fromhex(x['original'])))for x in changes];position=0;different=0
  with disc.open('rb')as f,target.open('rb')as g:
   while True:
    a=f.read(1048576);b=g.read(1048576);assert len(a)==len(b)
    if not a:break
    if a!=b:
     for i,(x,y)in enumerate(zip(a,b)):
      if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);different+=1
    position+=len(a)
  assert position==disc.stat().st_size
  variants[name]=dict(disc=str(target),sha256=sha(target),source_free=source_free,source_initializer=source_init,changes=changes,changed_disc_bytes=different,all_other_disc_bytes_identical=True)
 host=observer_source.read_text().replace('free_native','new_layout')
 needle="    steps++;";assert host.count(needle)==1
 emitted=[0x1545c,0x1557a,build['symbols']['biwn_native_free_body'],build['symbols']['biwn_native_free_clear32'],build['symbols']['biwn_native_heap_initialize']]
 host=host.replace(needle,needle+'\n    if('+ '||'.join('pc=='+str(pc)for pc in emitted)+')emit(pc);')
 needle=f"if(pc==(new_layout?{build['symbols']['biwn_native_heap_initialize_return']}:0x155c0))";assert host.count(needle)==1
 host=host.replace(needle,f"if(pc==0x155c0||pc=={build['symbols']['biwn_native_heap_initialize_return']})")
 source=out/'timing-observer.c';source.write_text(host);library=out/'libtiming-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 lines=template.read_text().splitlines(keepends=True);changed=[]
 for i,line in enumerate(lines):
  if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changed.append('observer')
  elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+').read_bytes())\n';changed.append('payload')
  elif line.startswith('            (127 if disc==Path('):lines[i]='            127,observer_payload,len(observer_payload.raw)-1,\n';changed.append('address_profile')
 assert len(changed)==3;probe=out/'fresh-timing-controls.py';probe.write_text(''.join(lines));compile(probe.read_text(),str(probe),'exec')
 core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=frames,variants=variants,commands=[],source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer_source,source,library,probe,inputs,core,fp,rp,bp]},scope='Three cold fixed-pad6400frame controls retain native25resident payload/layout/6144reserve and selectively restore original free/initializer bytes. Original initializer uses same relocated heapfloor. New-layout observer flag selects symbol addresses, not which originals remain. Read-only call/SP events. No host game-state writes/checkpoint/source owner/physical proof.')
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-free-timing-controls-active.json',state)
 mark();children=[]
 try:
  for name,variant in variants.items():
   command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(frames),'--core',str(core),'--disc',variant['disc'],'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/name)]
   log=(out/(name+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((name,child,log));state['commands'].append(dict(name=name,pid=child.pid,command=command))
  state['status']='running_selective_original_restore_controls';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
  for name,child,log in children:codes[name]=child.wait();log.close()
  state['exit_codes']=codes;assert not any(codes.values()),codes;state.update(status='terminal_selective_restore_controls_pending_analysis',finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-free-timing-controls-current.json',state);print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

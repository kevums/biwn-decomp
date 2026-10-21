"""Full coordinator algorithm after two rejected local drafts; no independence claim."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys,re,fcntl,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 pp=ROOT/'verification/local-native-resource-release-current.json';previous=json.loads(pp.read_text());out=ROOT/'runs'/('local-native-resource-release-guided-'+lab.stamp());out.mkdir();print(out,flush=True);header=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/resource-release-native.h').read_text()
 system='You are local guided C translator. Return one complete C99 file in one c code fence. Include "resource-release-native.h"; implement only void biwn_native_resource_release_body(uint32_t *r). Follow the coordinator complete algorithm literally. No asm, libc, other functions, globals, guards, reinterpretation, tests or prose. This is fully guided translation, not autonomous decompilation.'
 user=header+'''\nCOMPLETE COORDINATOR ALGORITHM:
Read id=RR16(r[15]+4u) exactly once.
For uint32_t i=0u;i<50u;++i:
  r[0]=i*12u; uint32_t entry=0x15b534u+r[0].
  If RR16(entry)==id:
    uint16_t refs=RR16(entry+6u);refs=(uint16_t)(refs-1u);RW16(entry+6u,refs).
    If refs==0u:
      RW16(entry,0xffffu);uint32_t handle=RR32(entry+2u);
      biwn_native_release_free_capture(r,handle).
    End if.
  End if.
End loop.
Finally r[16] &= 0xffffffe0u; return.
No other frame cells are assigned directly. In particular do NOT write r[2], use local d0, overwrite r[0] after free capture, or set carry. The assembly wrapper handles exact public saves/restores. This includes original last-slot free D0 and final ADDQ/CMP X/N/Z/V/C=0.\n'''
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),previous=previous,reasoning='off',source_accepted=False,new_training=False,native_Chat=False,coordinator_supplied_complete_algorithm=True,independent_model_validation=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-resource-release-guided-active.json',state)
 mark();save(out/'prepared-author.json',dict(system=system,user=user,max_output_tokens=1200,reasoning='off'));(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\n')
 try:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');lab.CONFIG['models']['game']['reasoning']='off';state['status']='guided_author_running';mark();a=lab.generate('game',system,user,1200)
  save(out/'response.json',a)
  with(out/'prompts-and-responses.txt').open('a')as f:f.write('RESPONSE\n'+a['text'])
  blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1;p=out/'resource-release-native.c';p.write_text(blocks[0].strip()+'\n');state.update(status='terminal_guided_release_draft_pending_native_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reported_seconds=a['seconds'],usage=a['usage'],quality_flags=a['quality_flags'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-resource-release-current.json',state);print(state['status'],a['seconds'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()

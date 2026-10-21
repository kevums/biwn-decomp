"""Targeted local source replacements after compiler/coordinator review."""
import fcntl,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
p=ROOT/'verification/local-scene-select-author-current.json';protocol=json.loads(p.read_text());out=Path(protocol['directory']);source=out/'biwn_scene_select.c';before=source.read_text();(out/'pre-repair-biwn_scene_select.c').write_text(before)
feedback='''Actual compiler failed: D1 is set but unused. Clarification: effective recordbase=0x3D822+D1 where D1=unsignedid_word*146,so tagread/pointerpublication must use thatindexedbase. This is explicit in the original indexedinstruction; the prior prose was terse.
Other source review findings to repair:
1)Source must include "biwn_scene_select.h" and export nonstatic int biwn_scene_select; remove the sourceheaderguard and final#endif,not return a staticinline header.
2)After successful tagread,before branching,set D0=(D0&0xFFFF0000u)|tag. Normal tag0 must clear lowD0 beforefirsthelper.
3)Initialize uint32_t call_ret=D0 before1AE88; callbackpointer is in/out,neveruninitialized.
4)After computing shifted lowword fromval<<4,update D0=(D0&0xFFFF0000u)|shifted before secondhelper; this preserves highD0 fromfirsthelper.
5)Initialize uint32_t call_ret2=D0 before1AC68.
6)Everyloop iteration must assign D0=shift_idx after signed16index extension/unsignedshift3,so finaloutD0 is the finaloffset. Keep every repeatedread/store/branch otherwise unchanged.
Return JSON only with replacements array(old(string),new(string)) and reason. Exactly8 unique replacements: initialinclude/staticprefix,final#endifcontext,indexedbase,tagD0merge,call_retseed,shiftedD0merge,call_ret2seed,loopD0assignment. Use existing source snippets exactly. No unrun testclaim.'''
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',lab.COMMON+'\nProvide narrowly scoped exact C source replacements in JSON.',feedback+'\nSOURCE\n'+before,2200)
(out/'repair.json').write_text(json.dumps(result,indent=2)+'\n');patch=lab.parse_object(result['text']);assert len(patch['replacements'])==8;after=before
for row in patch['replacements']:
 old,new=row['old'],row['new'];assert after.count(old)==1,(old,after.count(old));after=after.replace(old,new,1)
assert '#ifndef'not in after and '#endif'not in after and 'static inline int biwn_scene_select'not in after
source.write_text(after);protocol.update(status='local_targeted_repair_pending_original_recheck',local_repair=patch,repair_seconds=result['seconds'],pre_repair_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False,contract_clarification='Effectivebase3D822+id*146,initializedcallbackD0seeds,publicCexport and fullregisterword/shift semantics.');p.write_text(json.dumps(protocol,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
with(out/'prompts-and-responses.txt').open('a')as f:f.write('REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('Local8replacementpatch applied',result['seconds'],flush=True)

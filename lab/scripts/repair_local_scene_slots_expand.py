"""One bounded local-model repair from concrete static/trace-contract findings."""
import fcntl,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
def main():
 pointer=ROOT/'verification/local-scene-slots-expand-author-current.json';p=json.loads(pointer.read_text());out=Path(p['directory']);source=out/'biwn_scene_slots_expand.c';old=source.read_text();(out/'before-repair.c').write_text(old);evidence=json.loads((out/'evidence.json').read_text())
 issues=['count is uint32_t but read16 gets (uint16_t*)&count twice: forbidden pointer alias and uninitialized upper bits. Make count uint16_t and pass &count both times.','uint32_t ret is uninitialized when passed to E26C callback. Initialize ret=D0_shifted2, the original current fullD0.','D0 is initialized from seed and never updated; assign D0=D0_shifted4 after its original final iteration calculation, before A4++ (out_D0 remains untouched until success).','The valid-face block preloads all6 source longs then3 globals. This violates the exact original callback order: per axis read ONLY its1or2 required source longs, compute wrap-sum/ASR if midpoint, immediately read that axis global and add; then nextaxis. Do not read unused source offsets. Derive perface first/second offsets from supplied contract. Table-driven loop allowed; 0second offset can mean unscaled direct read because all actual source offsets>=4. Afterall3axes assignD6,D5,D4 and readD3,D2,D1globals in originalorder.','Global offset words49B8C/49B8E/49B90 must be interleaved with their stores: readX/write12,readY/write14,readZ/write16. Currently all3reads precede all3stores.']
 system=lab.COMMON+'\nRepair the supplied C against the concrete findings, preserving interface and all other semantics. JSON only: patches(array),limitations(string). Small patch: {old,new,occurrences(optional default1)}. Large block replacement: {start,end,new}, where start/end are unique literal anchors and replacement covers FROM start UNTIL end (end anchor retained). No prose/codefences. Do not weaken tests or erase guards.'
 prompt=json.dumps(dict(source=old,evidence=evidence,issues=issues,block_patch_suggestions=[dict(start='        if (face <= 5) {',end='        uint32_t cur2'),dict(start='        uint16_t off_x, off_y, off_z;',end='        if (bus->write16(bus->context, slot + 0x20')]))
 (out/'repair-prompt.json').write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',system,prompt,2500)
 (out/'repair.json').write_text(json.dumps(result,indent=2)+'\n');parsed=lab.parse_object(result['text']);new=old
 for patch in parsed['patches']:
  if 'old'in patch:
   count=patch.get('occurrences',1);assert new.count(patch['old'])==count,(patch['old'],new.count(patch['old']),count);new=new.replace(patch['old'],patch['new'])
  else:
   assert new.count(patch['start'])==new.count(patch['end'])==1;a=new.index(patch['start']);b=new.index(patch['end'],a+len(patch['start']));new=new[:a]+patch['new']+new[b:]
 source.write_text(new);p['drafts'].append(dict(role='original_contract_repair',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));p.update(local_repair=True,coordinator_C_body_edits=False,status='local_repair_pending_original_checks');pointer.write_text(json.dumps(p,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
 with(out/'prompts-and-responses.txt').open('a')as f:f.write('LOCAL REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
 print('Applied bounded local repair',result['seconds'],flush=True)
if __name__=='__main__':main()

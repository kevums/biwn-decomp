"""One bounded compiler/contract repair by the local model; preserve failed draft."""
import fcntl,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab

def main():
 pointer=ROOT/'verification/local-face-coordinates-author-current.json';proposal=json.loads(pointer.read_text());out=Path(proposal['directory']);source=out/'biwn_face_coordinates.c';original=source.read_text();(out/'biwn_face_coordinates.before-repair.c').write_text(original);(out/'syntax-before-repair.log').write_text((out/'syntax.log').read_text())
 restoration=ROOT/'projects/black-ice-white-noise/restoration';evidence=json.loads((out/'evidence.json').read_text());evidence['referenced_header']=(restoration/'biwn_world_update.h').read_text()
 system=lab.COMMON+'\nRepair only the reported interface and hexadecimal-offset errors. Return JSON only with replacements(array of objects old,new),limitations(string). Each old string must occur exactly once; include enough context. Return literal C replacement strings. No prose or code fences.'
 prompt=json.dumps(dict(evidence=evidence,source=original,compiler=(out/'syntax.log').read_text(),issues=['biwn_bus_read16 and biwn_bus_write16 do not exist; call bus->read16(bus->context,address,&value) / write16 directly as shown in referenced struct. Every read and write site must use declared callbacks.','Guard bus->read16 and bus->write16 upfront with bus/out_D0.','Original destination displacement is hexadecimal 0x24, not decimal24; change starting offset to0x24u.'],required_scope='Keep existing face tables and logical read/write order; no coordinator C body edits.'))
 (out/'repair-prompt.json').write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',system,prompt,1400)
 (out/'repair.json').write_text(json.dumps(result,indent=2)+'\n');parsed=lab.parse_object(result['text']);changed=original
 for patch in parsed['replacements']:
  assert changed.count(patch['old'])==1,patch['old'];changed=changed.replace(patch['old'],patch['new'])
 source.write_text(changed);proposal['drafts'].append(dict(role='compiler_and_contract_repair',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));proposal.update(status='local_repair_pending_original_checks',local_repair=True,first_draft_failed_compilation=True,coordinator_C_body_edits=False)
 pointer.write_text(json.dumps(proposal,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(proposal,indent=2)+'\n')
 with(out/'prompts-and-responses.txt').open('a')as f:f.write('LOCAL REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
 print('Applied local repair',len(parsed['replacements']),result['seconds'],flush=True)
if __name__=='__main__':main()

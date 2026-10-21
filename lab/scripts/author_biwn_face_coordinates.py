"""Auditable local author/reviewer for a remaining scene dependency."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
 ensure_game_model(); restoration=ROOT/'projects/black-ice-white-noise/restoration'
 p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
 assembly='\n'.join(x for x in p.read_text().splitlines() if re.match(r'^[0-9a-fA-F]{8}:',x) and 0x110d4<=int(x[:8],16)<=0x11382)
 contract='''Recover complete110D4..11382 as readable portable C99, only suppliedheader. Function biwn_face_coordinates(bus,source,destination,face,out_D0). JSON source(string),limitations(string).
Require bus/read16/write16/out_D0 upfront; status1badargs,2buserror,0success. Priorwrites retained and output unchanged on error. No IO, allocation, assembly, rawguestpointers, otherexports or librarycalls. Use unsigned arithmetic and defined truncation for 16bitword operations.
Originalarguments source anddestination arelogical32bit addresses; face isword. READ16(source), zeroextend, shiftleft5 toD0, A0=400C4+D0 wrapping32bits. Face unsigned>5 returns thisD0 unchanged, no writes. Validface clearsD0 and dispatches immutable jump table: 0->11110,1->1117A,2->111E4,3->1124E,4->112B4,5->1131A. Originaltable bytes000c007600e0014a01b00216. Table is code constant, not a data callback. D0 cleared before dispatch means its upper16bits remainzero in eachvalidcase.
There are twelve sequential read16/write16 pairs per face into destination+24,+26,...+3A hex. Derive perface source offsets and whether to shiftwordleft3 from assembly. A directmemory-to-memory MOVE.W reads and writes but DOES NOT changeD0. A MOVE.W toD0 thenASL.W changes only itslow16bits. Return FULLlastD0, not lastwordwritten if itwasdirect. Sharedtail at111DC shiftsD0wordleft3 andwritesdest+3A for faces1/3/4. Build readable table-driven code ifuseful, trackingD0 only for scaledentries. Do not preloadallsource values: source anddestinationcanalias, so preserveeachread/writeorder. No script/stub helpers. No claimedtests. Logicaldataaccess scope excludesnativebusdummyreads,code/jumptablefetch,CCR,otherregisters,private stack,timing.'''
 out=ROOT/'runs'/(lab.stamp()+'-local-face-coordinates');out.mkdir();print(out,flush=True)
 evidence=dict(assembly=assembly,contract=contract,referenced_header=(restoration/'biwn_world_update.h').read_text(),header=(restoration/'biwn_face_coordinates.h').read_text());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
 protocol=dict(status='authoring',directory=str(out),same_weights_correlated=True,new_training=False,native_Chat_verified=False,coordinator_contribution='Disassembly, explicit register/data-order contract, header and original instruction validator.')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Recover this original function with the exact supplied interface.' if role=='author' else 'Audit every instruction against the C. Return corrected complete source and limitations in JSON. Pay attention to per-face offsets, word truncation, D0 preservation on direct moves and aliased reads.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
   result=lab.generate('game',system,prompt,1300);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_face_coordinates.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_checks',drafts=drafts)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-face-coordinates-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

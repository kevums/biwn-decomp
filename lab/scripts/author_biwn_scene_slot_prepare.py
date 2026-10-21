"""Auditable local author/reviewer for a remaining scene dependency."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
 ensure_game_model(); restoration=ROOT/'projects/black-ice-white-noise/restoration'
 p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
 assembly='\n'.join(x for x in p.read_text().splitlines() if re.match(r'^[0-9a-fA-F]{8}:',x) and 0x11384<=int(x[:8],16)<=0x1142c)
 contract='''Recover complete11384..1142C portable readable C99 only suppliedheader. Include exactly #include "biwn_scene_slot_prepare.h" in source. Function biwn_scene_slot_prepare(bus,incoming_D0,out_D0). JSON source(string),limitations(string). Require bus/read16/read32/write16/write32/call/out_D0 upfront, status1badargs,2buserror,3helpererror,0success. Priorwrites retained, output unchanged on hosterror. No rawguestpointers,IO,allocation,assembly,librarycalls,otherexports.
Exactlogical operations, use disassemblygroundtruth: read32(49B88),add1 wrapping32,write32(49B88); REREAD32(49B88),D0=value<<6 wrapping32. slot=47B88+D0. Sequentialwrite16 offsets0,2,4,6,8,A,C,E,10 values4000,0,0,0,4000,0,0,0,4000 hex. Then read16(49B8C),negateword modulo65536,write16(slot+12); likewise49B8E->slot+14,49B90->slot+16. Read16(403CE)faceFIRST, then read32(400E6)sourcepointer. Call110D4 with logicalargs[sourcepointer,slot,zeroextendedface],count3; currentD0 in/outcallback is current shiftedslot index. Actualcallee may changeRAM; preserve rereads.
Afterhelperread32(49B88),D0=value<<6; write16(47B88+D0+20,7); read32(400C4),write32(47B88+D0+3C,value). REREAD32(49B88),subtract1 wrapping32,shift6->D0. read16(49B8A),write16(47B88+D0+18,value). ReturnfullD0. Everyoffset/address/value abovehex; alladdressarithmeticuint32wrap, wordnegationdefined. Do not assume49B88stable: callbacks/helpers maymutateit. No flag/register exceptD0/stack/timing claims. CLRnativebusdummyreads excluded from thislogicaldata API.'''
 out=ROOT/'runs'/(lab.stamp()+'-local-scene-slot-prepare');out.mkdir();print(out,flush=True)
 evidence=dict(assembly=assembly,contract=contract,referenced_header=(restoration/'biwn_world_update.h').read_text(),header=(restoration/'biwn_scene_slot_prepare.h').read_text());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
 protocol=dict(status='authoring',directory=str(out),same_weights_correlated=True,new_training=False,native_Chat_verified=False,coordinator_contribution='Disassembly, reviewed callback/data-order contract, header and original instruction validator.')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Recover this original function with the exact supplied interface.' if role=='author' else 'Audit every instruction against the C. Return corrected complete source and limitations in JSON. Pay attention to rereads after helper, bus access order, word negation and fullD0.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
   result=lab.generate('game',system,prompt,2200);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_scene_slot_prepare.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_checks',drafts=drafts)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-scene-slot-prepare-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

"""Local API roles while locked; exact transcripts retained, not native Chat history."""
import fcntl,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
from run_local_portal_author_test import ensure_game_model
def main():
 ensure_game_model();restore=ROOT/'projects/black-ice-white-noise/restoration';mapping=json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text());manifest_path=Path(mapping['static_manifest']);m=json.loads(manifest_path.read_text());snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();instructions=[x for x in m['instructions']if 0x10990<=int(x['address'],16)<0x10a6a];assert len(instructions)==39
 for row in instructions:
  a=int(row['address'],16);assert snapshot[a:a+row['size']]==bytes.fromhex(row['bytes'])
 header='''#ifndef BIWN_SCENE_INITIAL_SETUP_H
#define BIWN_SCENE_INITIAL_SETUP_H
#include "biwn_world_update.h"
/* Analyst name for10990..10A68; privateCPU frames/CCR excluded. */
int biwn_scene_initial_setup(struct biwn_world_bus *,uint32_t,uint32_t *);
#endif
'''
 contract='''Translate COMPLETE10990..10A68 to readable C99. Include exactly "biwn_scene_initial_setup.h". Function int biwn_scene_initial_setup(struct biwn_world_bus *bus,uint32_t incoming_D0,uint32_t *out_D0). Require bus,outD0,read32,write16,write32,call upfront. Use0 rather than undefinedNULL. Status0success,1badargs,2busfailure,3helperfailure. Retain prior effects; outD0 unchanged on error. Address/data arithmetic unsigned32. No directguestpointers,IO,allocation,assembly,librarycalls or extraexports.
CurrentD0 starts incoming_D0. Everyhelper receives currentD0 through in/outvalue; update it after successfulcall. Callees will be linked/explicit at hostboundary,do notinline orinventtheir behavior.
CALL1AA40 logicalwordargs[3],count1; CALL18160 argsnone,count0.
WRITE32(403DC,0);WRITE16(403E0,0);WRITE16(403D8,FFFF);WRITE16(403D0,0);WRITE16(40400,0);WRITE32(4040A,0);WRITE32(40406,0);WRITE32(40402,0).
CALL10968 logicalwordargs[0,1],count2. Initialize slot0 identitymatrix with9sequentialWRITE16 at47B88+offsets0,2,4,6,8,A,C,E,10 values4000,0,0,0,4000,0,0,0,4000.
CALL10A6A logicalwordargs[1],count1.
READ32(400E6)->A0. READ32(A0+C)FIRST->z, thenREAD32(A0+8)->y, thenREAD32(A0+4)->x. CALL11762 logicalargs[1,x,y,z],count4 (firstwordkind,then3longs). Do not reorder coordinate loads or confuse push order withlogicalargumentorder.
WRITE16 at47B9A,47B9C,47B9E,49B8C,49B8E,49B90 inthatorder,all0. Return current fullD0 from lastsuccessfulhelper.
Private stackpushes,22bytecleanup,otherregisters,CCR,nativebusdummyreads,timing and physicalhardware are outside thisportableABI. No original callee implementation or test success claim.
Return JSON only:source(string),limitations(string).'''
 out=ROOT/'runs'/(lab.stamp()+'-local-scene-initial-setup');out.mkdir();(out/'biwn_scene_initial_setup.h').write_text(header);evidence=dict(assembly='\n'.join(x['address']+': '+x['assembly']for x in instructions),contract=contract,header=header,referenced_header=(restore/'biwn_world_update.h').read_text(),original_bytes_verified=True,source_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[];protocol=dict(status='authoring',directory=str(out),new_training=False,native_Chat_verified=False,same_weights_correlated=True,coordinator_contribution='Bytechecked original listing,reviewed ABI/access-order contract,header,prompts and original validators.');print(out,flush=True)
 def save():(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 save()
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Author the complete routine using the exact supplied contract.'if role=='author'else'Review all39instructions and allcallbackwidths/order/fullD0/errors. Return complete corrected source in JSON, no unrun test claim.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));result=lab.generate('game',system,prompt,2100);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with(out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));protocol['drafts']=drafts;save();print(role,result['seconds'],result['quality_flags'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_scene_initial_setup.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_original_checks',drafts=drafts);save();(ROOT/'verification/local-scene-initial-setup-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

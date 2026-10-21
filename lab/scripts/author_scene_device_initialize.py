"""Local author/reviewer for original18160 ordered device writes."""
import fcntl,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model


def main():
    ensure_game_model()
    manifest_path=Path(json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text())['static_manifest'])
    manifest=json.loads(manifest_path.read_text())
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    instructions=[row for row in manifest['instructions']if 0x18160<=int(row['address'],16)<=0x181d8]
    assert instructions[-1]['address']=='000181d8'
    for row in instructions:
        pc=int(row['address'],16);assert atlas[pc:pc+row['size']]==bytes.fromhex(row['bytes'])
    header='''#ifndef BIWN_SCENE_DEVICE_INITIALIZE_H
#define BIWN_SCENE_DEVICE_INITIALIZE_H
#include "biwn_world_update.h"
/* Analyst name18160..181D8. Ordered MMIO/RAM writes through the bus.
 * No emulated device implementation, private CPU frame or timing claim.
 * Status0success,1badargs,2bus error. Prior effects retained; output unchanged on error.
 */
int biwn_scene_device_initialize(struct biwn_world_bus *,uint32_t *);
#endif
'''
    evidence=dict(instructions=instructions,assembly='\n'.join(x['address']+': '+x['assembly']for x in instructions),
                  header=header,bus_header=(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.h').read_text(),contract='Implement complete18160..181D8 ordered writes exactly. D0 becomes0 at18166; finalD0=0. A0 is private CPU addressing only. Require bus,out_D0,write16,write32 before any effects. Every callback receives exact address,width,value in original order. On failed write return2 immediately, retain prior effects, leave out_D0 untouched. Success writes0 to out_D0 then returns0. No reads,helper calls,work limit or device emulation. MMIO callbacks provide actual hardware behavior; never treat MMIO as ordinary guest RAM. Include only provided header. ReturnJSON source,limitations. No unrun verification claim.',
                  atlas_sha256=hashlib.sha256(atlas).hexdigest(),manifest=str(manifest_path))
    out=ROOT/'runs'/(lab.stamp()+'-local-scene-device-initialize');out.mkdir();print(out,flush=True)
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');(out/'biwn_scene_device_initialize.h').write_text(header)
    drafts=[];receipt=dict(status='authoring',directory=str(out),coordinator_C_body_edits=False,
        same_weights_correlated=True,new_training=False,native_Chat_verified=False,
        coordinator_contribution='Bytechecked original listing, ABI/bus contract, header and native/ordered-write verifier.')
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['author','reviewer']:
            result=lab.generate('game',lab.COMMON+'\n'+('Author complete C99 source.'if role=='author'else'Audit each original instruction and bus write; return corrected complete C99 source.'),json.dumps(dict(evidence=evidence,prior=drafts)),1300)
            (out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
            drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']))
            print(role,result['seconds'],result['quality_flags'],flush=True)
    parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_scene_device_initialize.c').write_text(parsed['source']+'\n')
    receipt.update(status='proposed_source_pending_original_checks',drafts=drafts)
    (out/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (ROOT/'verification/local-scene-device-initialize-author-current.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()

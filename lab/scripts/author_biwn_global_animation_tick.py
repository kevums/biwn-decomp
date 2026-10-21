"""Local author/reviewer recover a complete previously absent game body."""
import fcntl,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model
def main():
    ensure_game_model();restoration=ROOT/'projects/black-ice-white-noise/restoration'
    p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
    assembly='\n'.join(s for s in p.read_text().splitlines()if re.match(r'^[0-9a-fA-F]{8}:',s)and 0x10ba4<=int(s[:8],16)<=0x10c16)
    contract='''Write the COMPLETE function in portable C99:
int biwn_global_animation_tick(struct biwn_world_bus *bus,uint32_t incoming_D0,uint32_t *out_D0).
Include ONLY "biwn_global_animation_tick.h". No other exported functions.
Use the supplied original assembly and precise reviewed contract below.
Require bus,out_D0,read16/read32/write16/write32 upfront. Status0success,
1badargument,2buserror. Leave out_D0 unchanged on errors, prior bus effects retained.
The observable contract includes FULL D0 and every external read/write width/order.
Private CPU stack,CCR,otherregisters,timing are intentionally excluded.
1)Read16 timer403D4. If signed16>0,READ16 timer AGAIN,write16value-1,
return incoming_D0. Signedpositive means !=0 and bit15clear.
2)Otherwise read32 pointer400E6,read16 pointer+90hex,write16timer403D4.
READ16phase403D0,write16(phase+1 wrapped16). READ16limit403D2,then READ16phase403D0.
If signed16(limit)<=signed16(phase),write16phase0. Signedcomparison mayxor0x8000.
3)READ16phase403D0 AGAIN; let table_index=(phase&1)+1;D0=table_index*4.
READ32 at23F84+table_index*4,WRITE32 thatvalue at23F84.
4)READ16phase403D0 AGAIN. Compute arithmetic-right-shift word by1 with
unsigned math: (word>>1)|(word&0x8000). READ16offset403DA; ADDwrapped16.
Signextend result to32 using (uint32_t)(word&0x7FFF)-(uint32_t)(word&0x8000).
Then D0=that32bitvalue<<3 (unsigned wrap). READ32 at4674C+D0 and WRITE32
thatvalue at23F7C. Return fullD0offset throughout_D0 on success.
No caches replacing specified rereads, no callbacks beyond those4busfunctions,
no directguestpointers/IO/asm/allocation/librarycalls. Static integer helpers allowed.
No implementation-defined signed casts or signedshifts. Do not claim tests ran.
Return JSON only with source(string),limitations(string).'''
    out=ROOT/'runs'/(lab.stamp()+'-local-global-animation-tick');out.mkdir();print(out,flush=True)
    evidence=dict(contract=contract,assembly=assembly,headers={n:(restoration/n).read_text()for n in ['biwn_global_animation_tick.h','biwn_world_update.h']})
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    protocol=dict(status='authoring',directory=str(out),coordinator_contribution='Original disassembly, reviewed bus/fullD0 contract, analyst header and deterministic validator. Local roles write/review the C body.',roles=['local Code Author','local Source Reviewer'],same_weights_correlated=True,new_training=False,native_Chat_verified=False,assembly_sha256=hashlib.sha256(assembly.encode()).hexdigest());drafts=[]
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['author','reviewer']:
            system=lab.COMMON+'\n'+('Translate the supplied complete game routine and reviewed semantics into readable C.'if role=='author'else'Audit every assembly instruction and contract clause, especially rereads, signed16comparisons, word wrapping and D0. Return corrected complete C source.')
            prompt=json.dumps(dict(evidence=evidence,prior_drafts=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
            result=lab.generate('game',system,prompt,1700);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
            drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],result['quality_flags'],flush=True)
    parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_global_animation_tick.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_original_checks',drafts=drafts)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-global-animation-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

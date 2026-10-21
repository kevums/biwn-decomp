"""Local roles recover the caller that integrates the checked animation body."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model
def main():
    ensure_game_model();restoration=ROOT/'projects/black-ice-white-noise/restoration'
    p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm';assembly='\n'.join(s for s in p.read_text().splitlines()if re.match(r'^[0-9a-fA-F]{8}:',s)and 0x11ad4<=int(s[:8],16)<=0x11b4a)
    contract='''Return readable portable C99 for COMPLETE11AD4..11B4A:
int biwn_global_scene_prepare(struct biwn_world_bus *bus,uint32_t incoming_D0,uint32_t *out_D0).
Include ONLY "biwn_global_scene_prepare.h". Require bus,out_D0,read16,
read32,write16,write32,call upfront. Status0success,1badargs,2failedbus,
3failedhelper. Preserve priorbus effects; never change out_D0 on host error.
FullD0 is the call callback in/out value. Preserve all memory widths/order.
No directguestpointers,allocation,IO,assembly,librarycalls,otherexports.
1)D0=incomingD0. CALL10968 with logical args[1,7],wordargs zeroextended;
callback receives currentD0 through outputpointer and replaces it.
2)WRITE32 at49B88 value0. READ32 at40100, add32 modulo32bits, mask255
toform A; READ32 at400F8, add32/mask255 toform B; READ32 at400FC,
add32/mask255 toform C. A=(A>>6)<<5; D0=(C>>6)<<3; B=(B>>6)*2;
READ16 at3D7A2+A+D0+B, WRITE16 thatword at403CE. Otherindex operations
do not modify D0. All arithmetic unsigned, wrapping defined at32bits.
3)CALL11384 with noargs, passing currentD0 in/out; CALL10BA4 likewise;
CALL1142E likewise; CALL10734 likewise. Do NOT inline or script these helpers;
the host will execute the alreadychecked10BA4body, otherdeps remain explicit.
4)Return finalD0 throughout_D0. Originalprivate stack,D2/D3save-restores,
otherCPUregisters,CCR,timing are deliberately outside this portable interface.
Use supplied disassembly as groundtruth; no claimed execution/validation.
Return JSON only: source(string),limitations(string).'''
    out=ROOT/'runs'/(lab.stamp()+'-local-global-scene-prepare');out.mkdir();print(out,flush=True)
    evidence=dict(contract=contract,assembly=assembly,headers={n:(restoration/n).read_text()for n in ['biwn_global_scene_prepare.h','biwn_world_update.h']});(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
    protocol=dict(status='authoring',directory=str(out),roles=['local Code Author','local Source Reviewer'],same_weights_correlated=True,coordinator_contribution='Disassembly, reviewed bus/fullD0 contract, host header, original-code integration validator.',new_training=False,native_Chat_verified=False);(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['author','reviewer']:
            system=lab.COMMON+'\n'+('Translate this complete game caller from the supplied reviewed semantics.'if role=='author'else'Audit the complete C caller against each assembly instruction and reviewed contract. Preserve callbackD0,inputorder,widths and errors. Return corrected complete C.')
            prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n');result=lab.generate('game',system,prompt,1300);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
            drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],result['quality_flags'],flush=True)
    parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_global_scene_prepare.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_integration_checks',drafts=drafts);(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-global-scene-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

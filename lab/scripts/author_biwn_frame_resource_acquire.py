"""Local complete1AC68 caller reconstruction; explicitloader and guestscratch ABI."""
import fcntl,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
from run_local_portal_author_test import ensure_game_model
def main():
 ensure_game_model();e0=json.loads((ROOT/'verification/frame-resource-acquire-evidence-current.json').read_text());evidence=json.loads((Path(e0['directory'])/'evidence.json').read_text());out=ROOT/'runs'/(lab.stamp()+'-local-frame-resource-acquire');out.mkdir();print(out,flush=True)
 header='''#ifndef BIWN_FRAME_RESOURCE_ACQUIRE_H
#define BIWN_FRAME_RESOURCE_ACQUIRE_H
#include "biwn_world_update.h"
/* Analyst name1AC68..1AE54. scratch is mapped guest A6-4,not hostmemory.
 * 0success,1badargs,2bus,3loader,4worklimit,5dividezero host guard.
 * Prior effects stay; out_D0 unchanged on any hosterror.
 */
int biwn_frame_resource_acquire(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
#endif
''';(out/'biwn_frame_resource_acquire.h').write_text(header)
 contract='''Complete173instruction1AC68..1AE54 readableC99 caller. Signature int biwn_frame_resource_acquire(bus,id_word,scratch_guest_address,out_D0). Include exactly "biwn_frame_resource_acquire.h",nonstaticexport. Requirebus/out/scratch/read16/read32/write16/write32/call upfront. Status0success,1badargs,2bus,3helper,4hostworklimit,5hostdividezero. Prior effects stay,outD0 changesonlysuccess. No directguestpointers,IO,allocation,asm,librarycalls,extraexports. Callbackcall is fullD0 in/out; initialize outputpointer beforeeverycall. Alladdresseshex; numericcounts noteddecimal. EveryWORDoperation wraps16bits,lowD0 changes preservehigh16 until EXT.L/fullmove. SX16 explicit(v<32768?v:v-65536); use uint32 arithmetic/shifts fordefinedaddresswrap. All Chelperboundaries preserve originalcallee-save values. Resource1B044 remains explicitdependency,not invented. Guest scratch modelsoriginal4bytes at A6-4; write it throughbus,pass its guestaddress toloader.
Mode: R16(15B530). Signedmode<1or>3returnsFFFFFFFF. Modevalid1..3: index2=mode*2; adjustedword=(id_word-R16(464C8+index2))&FFFF. countword=R16(464A0+index2). A2=R32(464A8+mode*4); A4=R32(464B8+mode*4). THESEpointerreads precede signedadjusted<0test; negativeadjusted returnsFFFFFFFF. Preserve readorder.
PHASE1existing: indexword=R16(15B532); limitword=(36decimal-countword)&FFFF. IfSX(limit)>SX(index),loop:addedSTEP consumesonebus.poll_limit iteration,0allowsnone. D0=SX(index)<<2. R16(15B4A0+D0); if equals id_word: jword=0; whileSX(count)>SX(j):STEP,D0=SX((index+j)&FFFF)<<2;SEPARATE read16(15B4A2+D0),write16(word+1wrapped);j++. Return (D0&FFFF0000)|indexword. Ifcount<=0 skipfill andstillreturnthatfullD0. Ifnotmatch:indexword+=countword wrapped;repeat whileSX(capturedlimit)>SX(index). Strict>,not>=.
DIVS1: dividend=SX(adjustedword),divisor=SX(countword). Ifzero status5withoutoutmutation(originalexceptionexecutionexcluded). Otherwise quotient truncatestowardzero; dividend0..32767ensures quotientfits16fornonzero16bitdivisor. A4+=signedquotient wrapped32. Packedremainderhigh is not used before later fullD0overwrites,but fullD0 bookkeeping mustmatch eachlaterreturn.
PHASE2empty: REREAD16(15B532)->index. limitword=36-count wrapped. IfSX(limit)>SX(index): frame_offset=SX(adjusted)<<13; size=SX(count)<<13 unsigned32; while strictlimit>index:STEP; index32=SX(index); D0=index32<<2;R16(15B4A0+D0). IfFFFF,LOAD+FILLbelow. Elseindexword+=countword;recompute limit36-count andcontinue strictcomparison.
PHASE3evict: REREAD16(15B532)->index; limit36-count. IfSX(limit)<=SX(index),returnFFFFFFFF. frame_offset/size sameasphase2. Loop:STEP; index32=SX(index);D0=index32<<2;R16(15B4A2+D0). IfZERO,LOAD+FILLbelow. Nonzero: index+=countwrapped,recompute limit; ifstrictlimit>indexcontinue;elsereturnFFFFFFFF.
LOAD+FILL shared phase2/3: quotient=SX(adjusted)/SX(count),samezero guard. scaledword=(quotient*64decimal)&FFFF; A1=frame_offset+SX(scaledword)wrapped. D0=index32<<3. R32(4674C+D0)->WRITE32(scratch_guest_address,value). CALL1B044 logical5longargs[A1+A2,A4,scratch_guest_address,size,0],count5,passingcurrentfullD0 in/out. Successfulloader maychange RAM,scratch,D0. jword=0; whileSX(count)>SX(j):STEP;D0=SX((index+j)&FFFF)<<2;W16(15B4A0+D0,(id_word+j)&FFFF);W16(15B4A2+D0,1);j++. Returnfull(D0&FFFF0000)|indexword; thispreservesloaderhighD0 if fill skipped. Do notrereadmode,count,adjusted,A2/A4 registers; preserveexplicitReservedIndex rereads and tableloads. Loaderprivateframe/CCR/otherregisters,physicaltiming and fulloriginalexceptions outsideABI. ReturnJSON only source(string),limitations(string).'''
 evidence.update(header=header,referenced_header=(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.h').read_text(),contract=contract);(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[];receipt=dict(status='authoring',directory=str(out),new_training=False,native_Chat_verified=False,same_weights_correlated=True,coordinator_contribution='Bytecheckedlisting,reviewedthreephase/fullD0/scratch/dividecontract,header,prompts and original/nativevalidators.')
 def save():(out/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
 save()
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Author thecomplete Ccaller fromexact originalassembly and reviewedcontract.'if role=='author'else'Audit all173instructions and contractagainstsource: threephases,strictbounds,wordwrap/signedcomparisons,loader fullD0 seed,guest scratch/readorder andfailedoutput preservation. Return correctedcomplete C inJSON,no unrun tests.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));result=lab.generate('game',system,prompt,4000);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with(out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));receipt['drafts']=drafts;save();print(role,result['seconds'],result['quality_flags'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_frame_resource_acquire.c').write_text(parsed['source']+'\n');receipt.update(status='proposed_source_pending_original_checks',drafts=drafts);save();(ROOT/'verification/local-frame-resource-acquire-author-current.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()

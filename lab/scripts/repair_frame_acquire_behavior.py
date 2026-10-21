"""Local complete-source repair after strictcompiler and originaldiagnostics."""
import fcntl,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
p=ROOT/'verification/local-frame-resource-acquire-author-current.json';d=json.loads(p.read_text());o=Path(d['directory']);source=o/'biwn_frame_resource_acquire.c';before=source.read_text();(o/'pre-behavior-repair-biwn_frame_resource_acquire.c').write_text(before)
feedback='''Actual diagnostics onUNCHANGEDunacceptedsource:
Strictcompiler rejects4unused outerframe_offset/size declarations; sharedload_fill computes these internally,removeonlytheunusedouterones.
Original case1 expectedfullD0=0,C=d60e0000; read/write/calltraceidentical. Afterpositivecountfill,originalD0 is lastidx_j signedoffset<<2,not loaderreturnhigh. Update d0_in=d0_j duringevery filliteration beforestores,thenfinal (d0_in&FFFF0000)|index_word. Fornegative/zero countfill skipped,keeploaderhighD0 asoriginal.
Case5 originalloaderCALL incomingD0=8,C=1,cacheindex1. Callbackseed MUSTbe d0_shift=SX(index_word)<<3,not (d0_idxhigh|indexword). InitializecurrentD0 accordingly beforeCALL.
Staticcontractreview: DO NOT mutate bus->poll_limit. Copy it to localremaining onceperinvocation; pass uint32_t*remaining tosharedload_fill. AtEVERY scan/filliteration test remaining==0 ->status4,then decrementlocalremaining; zeroallows noiteration. Thefirstcachedsearch iteration needsSTEP too; itcurrentlylacksit. Preserveall originaldata/callbackorder;addedsteps have no bus effects.
Require scratch_guest_address nonzero upfront. Callbackerrorsreturn3,directbus2,badargs1,dividezero5,outD0unchangedonerror. All existingcachedfill loops musttrack last d0_j forproper highD0 ifwordindiceswrap,not keepfirstd0_full/d0_loop. Recompute signedoffsets with unsigned32shifts; originalfirstphasecapturedlimit doesn'tchangeexceptequivalentconstant arithmetic. Do not cacheReservedIndex reads. Retain3phases,strict>,mode/adjusted/order,andexact scratch/loader5longargs.
ReturnJSON only COMPLETEcompactsource andlimitations. No longcomments/explanation,no unrun testclaim. You have6000outputtokens,do nottruncate. SOURCE:\n'''
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',lab.COMMON+'\nRepairthe entireCsource against exact compiler/originaldiagnosticfeedback. OutputcompletecompactJSON.',feedback+before,6000)
(o/'behavior-repair.json').write_text(json.dumps(result,indent=2)+'\n');parsed=lab.parse_object(result['text']);after=parsed['source']+'\n';source.write_text(after);d.update(status='local_behavior_repair_pending_original_recheck',behavior_repair_seconds=result['seconds'],behavior_repair_quality_flags=result['quality_flags'],pre_behavior_repair_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False);p.write_text(json.dumps(d,indent=2)+'\n');(o/'protocol.json').write_text(json.dumps(d,indent=2)+'\n')
with(o/'prompts-and-responses.txt').open('a')as f:f.write('BEHAVIORREPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('Complete local behaviorrepair saved',result['seconds'],result['quality_flags'],flush=True)

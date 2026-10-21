"""Auditable local author/reviewer for a remaining scene dependency."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
 ensure_game_model(); restoration=ROOT/'projects/black-ice-white-noise/restoration'
 p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
 assembly='\n'.join(x for x in p.read_text().splitlines() if re.match(r'^[0-9a-fA-F]{8}:',x) and 0x1142e<=int(x[:8],16)<=0x11760)
 contract='''Recover COMPLETE1142E..11760 portable readable C99. Include exactly "biwn_scene_slots_expand.h". Function biwn_scene_slots_expand(bus,seed,out_D0). Return JSON only:source(string),limitations(string). Read seed D0,D4,D5,D6. Require bus,seed,out_D0,read16/read32/write16/write32/call upfront; status1badargs,2bus,3helper,4iterationlimit,0success. Do not change output on errors; preserve prior effects. No rawguestpointers,assembly,IO,allocation,librarycalls,otherexports.
Use disassembly as groundtruth. Address/long arithmetic wraps uint32. All addresses/offsets belowhex unless explicitly decimal. Word arithmetic wraps16bits. ASR32(sum,1)=(sum>>1)|(sum&0x80000000u); sum wraps before shift. Signed16 multiply20decimal use explicit sign extension (x<32768?x:x-65536), converting to uint32 before address addition. Do not use signed shifts or implementation-defined casts.
A4 counter starts0. D0=seedD0,D4/D5/D6=seedvalues. Read32(400E6)->A1; read16(A1+88)->count. While count unsigned>low16(counter): first ensure completediterations<bus.poll_limit (0 allows noiteration; addedguard), then execute whole loop; incrementcounter32bits at end. Zero count returns incomingD0 unchanged.
Loop: read32(49B88),add1/write32; REREAD32(49B88),D0=value<<6; initialslot=47B88+D0. Write16 offsets0,2,4,6,8,A,C,E,10 values4000,0,0,0,4000,0,0,0,4000. Read16(A1)->index (zeroextend), sourcebase=400C4+(index<<5). D1=D2=D3=0. Read16(A1+10+sx16(counterlow)*20decimal)->face.
Validface0..5 computes D6=x,D5=y,D4=z sequentially; everyread repeated, no caching across coordinates or iterations. Sourcebase offsets4/8/C/10/14/18 are signed longs but use uint32 modular arithmetic. Face0: x=ASR(src4+src10),y=ASR(src8+src14),z=src18. Face1:x=src4,y=ASR(src8+src14),z=ASR(srcC+src18). Face2:x=ASR(src4+src10),y=ASR(src8+src14),z=srcC. Face3:x=src10,y=ASR(src8+src14),z=ASR(srcC+src18). Face4:x=ASR(src4+src10),y=src8,z=ASR(srcC+src18). Face5:x=ASR(src4+src10),y=src14,z=ASR(srcC+src18). Eachcoordinate immediately adds read32(constant): x at3D6CA+face*12decimal,y+4,z+8. Then read32 globals D3=3D712+face*12decimal,D2+4,D1+8 in thatorder. Invalidface retains PREVIOUS D4,D5,D6, D1/D2/D3remain0. Immutable jump table targets114CC,11510,11554,11598,115DC,1161E; code/table fetch excluded.
After face: REREAD32(49B88),D0=value<<6, callslot=47B88+D0. Clearwrite16 atcallslot+12,+14,+16. Call E26C logicalargs[callslot,D1,D2,D3,0] count5, with fifth a WORDzero as actually pushed, otherfour longs. Initialize fullD0 in/outcallback to current D0. E26C/GPU implementation excluded and assumed preserves otherregisters; prior callers physically push18bytes, not20. Do not invent GPU behavior or claim bus fidelity beyond logicalargs.
Afterhelper REREAD32(49B88),D1=value<<6, slot=47B88+D1. For i0..11 sequentialREAD16(3D75A+i*2),WRITE16(slot+24+i*2). Write16(slot+12,low16(D6)-READ16(49B8C)); thenslot+14 lowD5-read49B8E; thenslot+16 lowD4-read49B90; thenWRITE16(slot+20,7).
Read32(400E6)->A1 (reload); Read16(A1+14+sx16(counterlow)*20decimal)->texture; zeroextend texture,shiftleft3; Read32(3D772+offset),write32(slot+3C). REREAD32(49B88),D0=(value-1)<<6; READ16(49B8A),WRITE16(47B88+D0+18,value). counter++; READ16(A1+88)->count (same A1 capturedbefore texture read), repeatcomparison.
ReturnfullD0. Keep precise callbacks and repeated loads, no helper scripts in this C. No claim of tests or naturalgameplay. Originalstack,CCR,otherregisters/nativebusdummyreads and helperinternals excluded.'''
 out=ROOT/'runs'/(lab.stamp()+'-local-scene-slots-expand');out.mkdir();print(out,flush=True)
 evidence=dict(assembly=assembly,contract=contract,referenced_header=(restoration/'biwn_world_update.h').read_text(),header=(restoration/'biwn_scene_slots_expand.h').read_text());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
 protocol=dict(status='authoring',directory=str(out),same_weights_correlated=True,new_training=False,native_Chat_verified=False,coordinator_contribution='Disassembly, reviewed callback/data-order contract, header and original instruction validator.')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Recover this original function with the exact supplied interface.' if role=='author' else 'Audit every instruction against the C. Return corrected complete source and limitations in JSON. Pay attention to all six coordinate branches, wrapped ASR sums, retained seed registers on invalid faces, exact reads, counted loop, logical E26C args and fullD0.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
   result=lab.generate('game',system,prompt,4000);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_scene_slots_expand.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_checks',drafts=drafts)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-scene-slots-expand-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

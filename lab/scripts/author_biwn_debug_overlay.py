"""Auditable local author/reviewer for a remaining scene dependency."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
 ensure_game_model(); restoration=ROOT/'projects/black-ice-white-noise/restoration'
 p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
 assembly='\n'.join(x for x in p.read_text().splitlines() if re.match(r'^[0-9a-fA-F]{8}:',x) and 0x10734<=int(x[:8],16)<=0x10966)
 contract='''Recover COMPLETE10734..10966 portable readable C99. Include exactly "biwn_debug_overlay.h". Function biwn_debug_overlay(bus,scratch,incoming_D0,out_D0). JSONsource(string),limitations(string). Require bus/read16/read32/write32/call/out_D0 upfront. Status1badargs,2bus,3helper,0success. Prior effects persist; output changes only on success. No IO,allocation,rawguestpointers,assembly,librarycalls,otherexports. No claimedtools/tests.
Everyoffset/address/value belowhex unless stateddecimal. D0=incoming_D0. In exact order WRITE32(F02268,0),W32(F0226C,0),W32(F02200,B29D0),W32(F02204,1820),W32(F0220C,0),W32(F0223C,113B0),W32(F02238,10200). READ16(403CC); ifzero returnincomingD0 (nohelpercalls).
Nonzero draws8rows in order. Firstsix read32 from400EC,400F0,400F4,400FC,400F8,40100 respectively, immediatelybefore thatrow's formatter call. Formats106E0,106EB,106F6,10701,1070C,10717 respectively. Row6(zerobased) READ16(403D0),signextend32 without implementation-defined casts: v<32768?v:((uint32_t)v|0xffff0000u). Format10722. Row7 READ16(403CA),zeroextend, multiply24DECIMAL thenadd3FB0C wrappinguint32; assignthisvalue tofullD0 beforeformatter;format10730.
Foreachrow firstCALL1B45A logicalargs[scratch,format,value],3longs. Initialize/pass callback outputpointer as FULLcurrentD0 in/out (never uninitialized). Helper may change guestRAM andD0. NextCALL149AE args[xword,yword,scratch,B29D0,3E08,4C3E0,3,0],count8. CoordsX/Y byrow hex: [14,2],[14,C],[14,16],[78,2],[78,C],[78,16],[14,20],[14,2A]. Wordargs zeroextended. PassfullD0 in/out again. No memoryprefetch acrosshelpercalls; helpers mayalter later rowinput values. After lastrow returnfullD0 fromlasttextcall. Row6 signextension doesNOTchangeD0, row7computedpointer DOES. Do not inlineformatter/text—they are separately recovered dependencies supplied by host. Scratchaddress explicitguestRAM; originalprivate stacklayout/registersave,timing/CCR/nativebusdummyreads/devicepixelwork excluded. All8rows required, notonlydebugoff.'''
 out=ROOT/'runs'/(lab.stamp()+'-local-debug-overlay');out.mkdir();print(out,flush=True)
 evidence=dict(assembly=assembly,contract=contract,referenced_header=(restoration/'biwn_world_update.h').read_text(),header=(restoration/'biwn_debug_overlay.h').read_text());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
 protocol=dict(status='authoring',directory=str(out),same_weights_correlated=True,new_training=False,native_Chat_verified=False,coordinator_contribution='Disassembly, reviewed callback/data-order contract, header and original instruction validator.')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Recover this original function with the exact supplied interface.' if role=='author' else 'Audit every instruction against the C. Return corrected complete source and limitations in JSON. Pay attention to all8rows, argument widths/order, fullD0 helperseed, signed word row6, unsigned pointer row7 and no prefetch across calls.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
   result=lab.generate('game',system,prompt,2200);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_debug_overlay.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_checks',drafts=drafts)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-debug-overlay-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

"""Auditable local author/reviewer for a remaining scene dependency."""
import fcntl,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
 ensure_game_model(); restoration=ROOT/'projects/black-ice-white-noise/restoration'
 p=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm'
 assembly='\n'.join(x for x in p.read_text().splitlines() if re.match(r'^[0-9a-fA-F]{8}:',x) and 0x10968<=int(x[:8],16)<=0x1098e)
 contract='''Recover complete10968..1098E as readable portable C99 using ONLY supplied header. Return JSON source(string),limitations(string). Function biwn_slot_clear(bus,first_slot,count_words,out_D0).
Require bus,bus->write8,out_D0 up front; bad arguments1. Success0; callback error2, retain prior writes and leave out_D0 unchanged. No other exports, allocation, IO, assembly, guest pointer casts or library calls.
Derive exact semantics from assembly. Explicit sign extension of 16bit input without implementation-defined unsigned-to-signed casts: x<32768?x:x-65536, using int32_t. Use uint32_t before left shift6, so no negative signed shifts. Pointer base47B88 plus shifted signed first slot wraps32bits. D0=signextended count word shifted6 modulo32bits. Zero D0 means no writes. Otherwise do byte-zero write then increment address, increment16bit counter wrapping, signextend counter to32bits, loop while UNSIGNED D0>signextended counter. Do not replace this with ordinary count*64 memset: large positive and negative word counts have unusual termination. Output fullD0. CLR dummy reads/native bus cycles, other registers, CCR, stack and timing excluded from this logical-store API. No poll limit needed: all inputs terminate within65535 stores. Do not claim tests were run.'''
 out=ROOT/'runs'/(lab.stamp()+'-local-slot-clear');out.mkdir();print(out,flush=True)
 evidence=dict(assembly=assembly,contract=contract,header=(restoration/'biwn_slot_clear.h').read_text());(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[]
 protocol=dict(status='authoring',directory=str(out),same_weights_correlated=True,new_training=False,native_Chat_verified=False,coordinator_contribution='Disassembly, explicit reviewed arithmetic/loop contract, header and original instruction validator.')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Recover this original function with the exact supplied interface.' if role=='author' else 'Audit every instruction against the C. Return corrected complete source and limitations in JSON. Pay attention to unsigned compare of sign extended 16-bit counter.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));(out/(role+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
   result=lab.generate('game',system,prompt,1300);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));print(role,result['seconds'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_slot_clear.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_checks',drafts=drafts)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');(ROOT/'verification/local-slot-clear-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()

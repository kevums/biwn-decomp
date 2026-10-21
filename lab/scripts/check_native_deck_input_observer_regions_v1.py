"""Compile the exact live region checker and reject code/fence ownership faults."""
import ctypes as c
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';build=read(v/'native-Deck-input-disc-build-current.json');job=read(v/'native-Deck-input-candidate-current.json');live=Path(job['directory'])/'observer.c';text=live.read_text();lo=text.index('static unsigned native_deck_regions(');hi=text.index('static uint8_t deck_used',lo);body=text[lo:hi]
 out=v/'native-Deck-input-region-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=out/'checker.c';source.write_text('#include <stdint.h>\n#include <string.h>\n'+body+'\nunsigned check(const uint8_t *a,const uint8_t *b,const uint8_t *u){return native_deck_regions(a,b,u);}\n');lib=out/'checker.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(lib)).check;fn.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];fn.restype=c.c_uint
 payload=Path(build['component']).read_bytes();memory=bytearray(0x200000);base=build['resident_address'];memory[base:base+len(payload)]=payload
 def check(raw,used=bytes(101)):return fn(c.create_string_buffer(bytes(raw)),c.create_string_buffer(payload),c.create_string_buffer(bytes(used)))
 assert check(memory)==0;arena=build['deck_arena_address'];rows=[]
 points=[('prefix_code',base+512),('input_code',build['input_code_address']),('coordinate_code',build['deck_code_address']),('finalizer',build['deck_finalizer_address']),('immutable_gap',build['arena_end'])]
 points += [('fence_'+str(slot)+'_'+str(offset),arena+slot*1024+offset)for slot in [0,100]for offset in [0,128,256,704,1023]]
 points += [('unused_input_frame',arena+144),('unused_coordinate_frame',arena+16)]
 for name,address in points:
  altered=bytearray(memory);altered[address]^=1;assert check(altered)>0,name;rows.append(dict(name=name,address=hex(address),rejected=True))
 used=bytearray(101);used[6]=1;altered=bytearray(memory);altered[arena+6*1024+144]^=1;assert check(altered,used)==0
 altered[arena+6*1024+256]^=1;assert check(altered,used)>0;rows.append(dict(name='used_input_fence',rejected=True))
 proof=dict(status='terminal_exact_live_input_region_checker_positive_and_faults_pass',directory=str(out),synthetic_positive_cases=1,negative_controls=rows,used_private_context_change_allowed=True,game_RAM_modified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),live,source,lib,v/'native-Deck-input-disc-build-current.json']},scope='Exact function extracted from the actual running observer; code/gaps/outer and3internal fences/unused context ownership. Synthetic fault injections occur only in host test buffers. This does not qualify every live counter or game algorithm.')
 save(out/'review.json',proof);save(v/'native-Deck-input-region-check-current.json',proof);print(proof['status'],len(rows),flush=True)

if __name__=='__main__':main()

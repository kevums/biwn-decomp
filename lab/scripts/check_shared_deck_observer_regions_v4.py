"""Fault-check the exact candidate observer's immutable-code/arena function."""
import ctypes as c
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import check_native_deck_shared_v4 as kernel
def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-Deck-shared-disc-build-v4-current.json';build=read(bp);job=read(v/'native-Deck-five-caller-geometry-v1-candidate-current.json');live=Path(job['directory'])/'observer.c';text=live.read_text();lo=text.index('static unsigned native_deck_regions(');hi=text.index('static uint8_t deck_used',lo);body=text[lo:hi]
 out=v/'shared-Deck-region-check-v4'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=out/'checker.c';source.write_text('#include <stdint.h>\n#include <string.h>\n'+body+'\nunsigned check(const uint8_t *a,const uint8_t *b,const uint8_t *u){return native_deck_regions(a,b,u);}\n');lib=out/'checker.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(lib)).check;fn.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];fn.restype=c.c_uint
 payload=Path(build['component']).read_bytes();memory=bytearray(0x200000);base=build['resident_address'];memory[base:base+len(payload)]=payload;arena=build['deck_arena_address']
 def check(raw,used=bytes(101)):return fn(c.create_string_buffer(bytes(raw)),c.create_string_buffer(payload),c.create_string_buffer(bytes(used)))
 assert check(memory)==0;rows=[]
 points=[('prefix_code',base+512),('shared_code',build['shared_Deck_code_address']),('finalizer',build['deck_finalizer_address']),('immutable_gap',build['arena_end'])]
 points += [('fence_'+str(slot)+'_'+str(at),arena+slot*1024+at)for slot in [0,50,100]for lo,hi in kernel.FENCES for at in [lo,hi-1]]
 points += [('unused_'+name+'_frame',arena+values[1])for name,values in kernel.LAYOUT.items()]
 for name,address in points:
  altered=bytearray(memory);altered[address]^=1;assert check(altered)>0,name;rows.append(dict(name=name,address=hex(address),rejected=True))
 used=bytearray(101);used[6]=1
 for name,(_,offset,lower,top)in kernel.LAYOUT.items():
  altered=bytearray(memory);altered[arena+6*1024+offset]^=1;altered[arena+6*1024+lower]^=1;assert check(altered,used)==0,name
 for lo,hi in kernel.FENCES:
  altered=bytearray(memory);altered[arena+6*1024+lo]^=1;assert check(altered,used)>0;rows.append(dict(name='used_slot_fence_'+str(lo),address=hex(arena+6*1024+lo),rejected=True))
 proof=dict(status='terminal_exact_shared_observer_region_fault_controls_pass',directory=str(out),synthetic_positive_cases=1,negative_controls=rows,distinct_negative_addresses=len({x['address']for x in rows}),input_face_slot_is_aliased=True,coordinate_geometry_slot_is_aliased=True,used_private_context_and_stack_changes_allowed=True,game_RAM_modified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),live,source,lib,bp,Path(kernel.__file__)]},scope=__doc__+' Host buffers only. Checks code/gaps, all7fences including both endpoints at3slots, unused frames and used-private allowances. Does not independently validate other live counters or game algorithms.')
 save(out/'review.json',proof);save(v/'shared-Deck-region-check-v4-current.json',proof);print(proof['status'],len(rows),flush=True)
if __name__=='__main__':main()

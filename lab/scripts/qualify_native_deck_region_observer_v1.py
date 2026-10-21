"""Actual final RAM plus compiled code/guard/ownership negative controls."""
import ctypes as c,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import task_arena_observer_source_v2 as model
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 b=read(V/'native-Deck-coordinate-disc-build-current.json');out=V/'native-Deck-region-observer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=out/'checker.c';source.write_text('#include <stdint.h>\n#include <string.h>\n'+model.checker(b)+'\nunsigned check(const uint8_t*a,const uint8_t*b,const uint8_t*c){return native_deck_regions(a,b,c);}\n');library=out/'checker.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(library)).check;fn.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];fn.restype=c.c_uint
 payload=Path(b['component']).read_bytes();rows=[];snapshots={}
 def check(data,used=bytes(101)):
  return fn(c.create_string_buffer(data),c.create_string_buffer(payload),c.create_string_buffer(used))
 for lane in ['candidate','control']:
  job=read(V/('native-Deck-coordinate-quiescent-'+lane+'-current.json'));raw=Path(job['directory'])/'candidate/RAM-final.bin';data=raw.read_bytes();assert check(data)==0
  snapshots[lane]=data;rows.append(dict(lane=lane,source=str(raw),sha256=sha(raw),new_region_errors=0,legacy_contiguous_check_failed=data[b['resident_address']:b['resident_address']+b['linked_component_bytes']]!=payload[:b['linked_component_bytes']]))
 raw=snapshots['candidate'];mutations=[]
 points=[('prefix_code',b['resident_address']+512),('coordinate_code',b['deck_code_address']),('new_finalizer',b['deck_finalizer_address']),('new_guard_first',b['deck_arena_address']),('new_guard_last',b['deck_arena_address']+b['deck_arena_bytes']-1),('unused_Deck_context',b['deck_arena_address']+16),('immutable_gap_after_GPU',b['arena_end'])]
 for name,address in points:
  data=bytearray(raw);data[address]^=1;assert check(bytes(data))>0,name;mutations.append(dict(name=name,address=hex(address),rejected=True))
 data=bytearray(raw);data[b['deck_arena_address']+3*1024+64]^=1;used=bytearray(101);used[3]=1;assert check(bytes(data),bytes(used))==0
 data[b['deck_arena_address']+3*1024]^=1;assert check(bytes(data),bytes(used))>0;mutations.append(dict(name='used_Deck_slot_guard',rejected=True))
 state=dict(status='terminal_discontiguous_native_code_and_Deck_guard_observer_qualified',directory=str(out),actual_final_RAM_positive_cases=2,mutations=mutations,used_private_context_change_allowed=True,initial_false_alarm_diagnosis='Legacycodecount44430crossedmutableGPUarena. All403changedbytesofthatintervalareinsideGPUarenas;newDeckarenaisunchanged. NewcheckerchecksallimmutablecopybytesintwoexactrangesandallDeckguards/unusedslots.',source_sha256={str(p):sha(p)for p in[Path(__file__),Path(model.__file__),ROOT/'scripts/task_arena_observer_source_v1.py',source,library,V/'native-Deck-coordinate-disc-build-current.json']},snapshots=rows,scope='ExactsameCregionfunctionemittedintoliveobserver. Eightcompiledcode/gap/guard/unusedownershipfaultsrejected. LegacyGPUguard/ownershipchecksretainedseparately. NoCPU/RAMwrites or gamealgorithmchanges.')
 save(out/'report.json',state);save(V/'native-Deck-region-observer-current.json',state);print(state['status'],len(mutations),flush=True)
if __name__=='__main__':main()

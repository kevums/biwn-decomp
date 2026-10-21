"""Additional observable exact-boundary/wrap witnesses for readable Deck C."""
import ctypes as c,hashlib,json,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import check_deck_coordinate_source_v1 as m
ROOT=m.ROOT
def main():
 trial=json.loads((ROOT/'verification/Deck-coordinate-source-candidate-current.json').read_text());assert trial['status']=='terminal_component_source_selected_pending_pipeline'
 m.SRC=Path(trial['glue_directory'])
 source=Path(trial['candidate']);assert m.sha(source.read_bytes())==trial['candidate_sha256']
 out=ROOT/'verification/deck-coordinate-boundary-witnesses'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 libpath=out/'libdeck-coordinate.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(m.SRC),str(source),str(m.SRC/'deck-coordinate-adapter.c'),'-o',str(libpath)]
 compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
 fn=c.CDLL(str(libpath)).biwn_deck_coordinate_call;fn.argtypes=[c.POINTER(m.Bus),c.POINTER(m.CPU),m.SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
 vectors=[];baseline=m.fixtures()[0]
 # Proposed positions deliberately differ from old positions, so an incorrect
 # < versus <= or signed comparison produces observable public RAM changes.
 for gpu_word in [1,0x7fff,0x8000,0xffff]:
  for camera in [0,0x7fffffff,0x80000000,0xffffffff]:
   proposed=(camera+(gpu_word if gpu_word<0x8000 else gpu_word-0x10000))&0xffffffff
   distance=(proposed*proposed)&0xffffffff
   for threshold in sorted({distance,(distance+1)&0xffffffff,(distance-1)&0xffffffff,0x80000000}):
    for supervisor in [False,True]:
     ram=bytearray(baseline[0]);initial=m.CPU.from_buffer_copy(bytes(baseline[1]));initial.sr=0x271f if supervisor else 0x071f;initial.usp=0x1d8000 if supervisor else m.SP;initial.ssp=m.SP if supervisor else 0x1ff000
     def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
     put(0x400e6,4,0x80000);put(0x80000,2,0)
     for a in [0x400f0,0x400f4,0x80004,0x80008,0x8000c,0x40402,0x40406,0x4040a,0x40104]:put(a,4,0)
     put(0x400ec,4,camera);put(0x400e0,4,threshold)
     case=dict(gpu_effects=[[0x47b9a,2,gpu_word],[0x47b9c,2,0],[0x47b9e,2,0]],gpu_word=gpu_word,camera=camera,proposed=proposed,distance=distance,threshold=threshold,accept_expected=distance<threshold,supervisor=supervisor)
     vectors.append((bytes(ram),initial,case))
 engine=m.Engine();rows=[];accepts=rejects=0
 try:
  for i,(ram,initial,case)in enumerate(vectors):
   expected,cpu,entries,coverage,steps=engine.original(ram,initial,case)
   accepted=0x11e24 in coverage;assert accepted==case['accept_expected'],case
   status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
   assert not status and not errors and actual==expected and m.cpu_dict(got)==m.cpu_dict(cpu)and entries==observed,(i,case,status)
   assert int.from_bytes(actual[0x400ec:0x400f0],'big')==(case['proposed']if accepted else case['camera'])
   accepts+=accepted;rejects+=not accepted;rows.append(dict(**case,full_RAM_CPU_helper_entries_match=True))
 finally:engine.native.close()
 m.save(out/'cases.json',rows);report=dict(status='terminal_Deck_coordinate_exact_boundaries_and_wrap_pass',directory=str(out),cases=len(rows),accepted=accepts,rejected=rejects,equal_threshold_cases=sum(x['distance']==x['threshold']for x in rows),candidate=str(source),candidate_sha256=m.sha(source.read_bytes()),source_sha256={str(p):m.sha(p.read_bytes())for p in [Path(__file__),Path(m.__file__),m.SRC/'deck-coordinate-contract.h',m.SRC/'deck-coordinate-adapter.c']},scope='Additional component witnesses: real original caller/multiply,declaredGPUwordresults. Exactunsignedstrictboundary,signextendedGPUwords and32bitcamera/squarewrap,bothbanks/allincomingCCRbits1. Notlivegame/GPU/timingproof.')
 m.save(out/'report.json',report);m.save(ROOT/'verification/Deck-coordinate-boundaries-current.json',report);print(report['status'],report['cases'],flush=True)
if __name__=='__main__':main()

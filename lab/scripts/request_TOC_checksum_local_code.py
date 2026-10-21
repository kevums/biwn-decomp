"""Local Restorer authors a portable semantic checksum body; coordinator verifies."""
import fcntl,json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
out=ROOT/'verification/TOC-checksum-local-code'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
system='You are the local Restorer role. Return source code only, without fences or commentary. You have no tools and must not claim execution. Source comparison by the coordinator determines acceptance.'
prompt='''Write portable C99 implementing this verified firmware checksum semantics. Return only a complete C source file including stdint.h and stddef.h. Export int biwn_firmware_TOC_checksum(const uint8_t *toc, const uint32_t *round_constants, uint32_t *out). toc points to exactly1024bytes; round_constants has64uint32_t constants supplied by caller from original firmware; out has4uint32_t words. Return1 on any NULL pointer without modifying out; otherwise return0. No allocations, global mutation, library hashing, padding, byte reversal or sine computation.
Algorithm independently compared with original DSP: initialize A=0x67452301,B=0xefcdab89,C=0x98badcfe,D=0x10325476. For each of16blocks, decode16big-endian32-bit words X. Save AA/BB/CC/DD. For i0..63: rounds use F=(B&C)|(~B&D),g=i for i<16; F=(D&B)|(~D&C),g=(5*i+1)%16 for i<32; F=B^C^D,g=(3*i+5)%16 for i<48; F=C^(B|~D),g=(7*i)%16 otherwise. t=A+F+round_constants[i]+X[g] modulo2^32. Rotate t LEFT by S[i]. Assign A=oldD,D=oldC,C=oldB,B=oldB+rotated modulo2^32. S=[7,12,17,22]repeated4,then[5,9,14,20]repeated4,then[4,11,16,23]repeated4,then[6,10,15,21]repeated4. After eachblock add saved state wordwise modulo2^32. Output4state words directly, no byte serialization. MD5compression only: input has no padding appended; NOT the standard paddedMD5 API. Keep integer shifts defined and unsigned. Scope is only this1024byte semantic routine, not entire DSP register/IRQ/clock behavior.'''
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 state=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(state)==1 and state[0]['identifier']=='advertising-scholar'and state[0]['status']=='idle'
 result=lab.generate('game',system,prompt,2048,model='advertising-scholar')
 row=dict(role='Restorer',system=system,prompt=prompt,actual_model=state,result=result,status='generated_unverified',source_reference=str(ROOT/'verification/BIWN-TOC-compression-current.json'))
 (out/'request-and-response.json').write_text(json.dumps(row,indent=2)+'\n');(out/'candidate.c').write_text(result['text']);(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nRAW RESPONSE\n'+result['text']+'\n')
 (ROOT/'verification/TOC-checksum-local-code-current.json').write_text(json.dumps(dict(directory=str(out),status=row['status']),indent=2)+'\n')
 print(json.dumps(dict(directory=str(out),seconds=result['seconds'],flags=result['quality_flags'])),flush=True)

"""Guided local Restorer optimization; exact code awaits execution gates."""
import fcntl,json,os,sys,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
out=ROOT/'runs'/('local-native-math-optimization-repair-'+lab.stamp());out.mkdir()
source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/math-results.c'
system=lab.COMMON+'\n'+lab.ROLES['game']['restorer']+'\nOutput one complete C99 file in a single c code fence, without other role simulation. You have not compiled or tested your proposal.'
prompt='Your prior draft needs these exact repairs before acceptance: remove project-relative includes, leaving only stdint.h/stddef.h; add extern uint32_t __udivsi3(uint32_t,uint32_t); after computing unsigned quotient and raw remainder, negate quotient with unsigned0-q when numerator/denominator signs differ and negate remainder with unsigned0-r when numerator is negative. Keep the unsigned magnitudes for existing X-flag comparisons. Preserve the multiplication and ABI layout. Return a complete C99 file in one c fence. This is a coordinator-guided repair with supplied diagnosis, not unassisted authoring.\nPRIOR DRAFT\n'+Path('/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/runs/local-native-math-optimization-20261018T030837.270421Z/math-results-optimized.c').read_text()
state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Local Restorer',system=system,prompt=prompt,guided=True,coordinator_supplied_algorithm_plan=True,repair_of='/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/runs/local-native-math-optimization-20261018T030837.270421Z',native_Chat=False,new_training=False,source_accepted=False)
def save():
 (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/local-native-math-optimization-repair-current.json').write_text(json.dumps(state,indent=2)+'\n')
save();print(out,flush=True)
try:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);state['status']='generating';save();result=lab.generate('game',system,prompt,2200,model='advertising-scholar')
 state['result']=result;(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nRAW RESTORER\n'+result['text']+'\n');fences=re.findall(r'```(?:c|C)?\s*\n(.*?)```',result['text'],re.S);assert len(fences)==1,'Expected one complete fenced C file'
 candidate=out/'math-results-optimized.c';candidate.write_text(fences[0].rstrip()+'\n');prefix=ROOT/'tools/m68k-elf/bin/m68k-elf-';command=[str(prefix)+'gcc','-m68000','-msoft-float','-std=c99','-O2','-ffreestanding','-ffunction-sections','-fdata-sections','-fno-pic','-fno-pie','-fno-stack-protector','-Wall','-Wextra','-Werror','-c',str(candidate),'-o',str(out/'candidate.o')];p=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr)
 state.update(status='terminal_compiled_pending_native_validation'if p.returncode==0 else'terminal_compile_rejected',candidate=str(candidate),candidate_sha256=lab.sha(candidate),compile_command=command,compile_exit_code=p.returncode,coordinator_edited_model_source=False);save();print(json.dumps(dict(status=state['status'],seconds=result['seconds'],flags=result['quality_flags'],candidate=str(candidate))),flush=True)
except BaseException as error:state.update(status='terminal_failed',error=repr(error));save();raise

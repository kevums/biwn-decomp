import json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(json.loads((ROOT/'verification/actor6-local-follow-fragment-current.json').read_text())['directory']);results=[]
harness='\nint main(void){uint32_t s=0x1585c;volatile uint64_t sink=0;for(unsigned i=0;i<8192;i++){s^=s<<13;s^=s>>17;s^=s<<5;sink=biwn_actor6_follow_step(s,s^0x7fffffff);}return sink==0x123456789abcdefULL;}\n'
for role in ['author','reviewer','guided-repair']:
 p=out/(role+'-UBSan.c');p.write_text((out/(role+'.c')).read_text()+harness);exe=out/(role+'-UBSan');cmd=['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=undefined',str(p),'-o',str(exe)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});log=build.stdout+build.stderr;row=dict(role=role,compiler=cmd,compiled=not build.returncode)
 if not build.returncode:
  run=subprocess.run([str(exe)],capture_output=True,text=True);log+=run.stdout+run.stderr;row.update(exit_code=run.returncode,checked_8192_pairs=not run.returncode)
 (out/(role+'-UBSan.txt')).write_text(log);row['log']=str(out/(role+'-UBSan.txt'));results.append(row)
report=dict(status='completed_undefined_behavior_checks',results=results);(out/'undefined-behavior-check.json').write_text(json.dumps(report,indent=2)+'\n');print(results)

import json,fcntl,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
out=Path(json.loads((ROOT/'verification/actor7-local-distance-fragment-current.json').read_text())['directory']);protocol=json.loads((out/'protocol.json').read_text())
user='The following C function passed its declared output-only native checks. Return exactly the same C source without Markdown fences. Your response must start with #include and end with }. Output no introduction, no backticks, no commentary. This is a format correction, not new validation.\n\n'+(out/'author.c').read_text()
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);row=lab.generate('game','You are a source formatter. Return only plain C source. Do not use Markdown or code fences.',user,600)
row['role']='format-repair';protocol['results'].append(row);(out/'format-repair.c').write_text(row['text']);(out/'format-repair.json').write_text(json.dumps(row,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');p=out/'prompts-and-responses.txt';p.write_text(p.read_text()+'\n\nROLE format-repair\nREQUEST\n'+json.dumps(row['request'],indent=2)+'\nRAW RESPONSE\n'+row['text']);print(row['seconds'],row['quality_flags'],flush=True)

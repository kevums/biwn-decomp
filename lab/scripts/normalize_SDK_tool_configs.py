"""Use supported typed prediction configs; preserve callable-tool schema keys."""
import ast,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/SDK-typed-tool-configs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);changes=[]
for p in sorted((ROOT/'scripts').glob('*.py')):
 data=p.read_bytes()
 try:tree=ast.parse(data)
 except SyntaxError:continue
 aliases=[x.asname or x.name for n in tree.body if isinstance(n,ast.Import)for x in n.names if x.name=='lmstudio']
 if not aliases:continue
 module=aliases[0];lines=data.splitlines(keepends=True);starts=[0]
 for line in lines:starts.append(starts[-1]+len(line))
 edits=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call)or not isinstance(node.func,ast.Attribute)or node.func.attr!='act':continue
  for keyword in node.keywords:
   if keyword.arg!='config':continue
   value=keyword.value;begin=starts[value.lineno-1]+value.col_offset;end=starts[value.end_lineno-1]+value.end_col_offset;expr=data[begin:end]
   if b'LlmPredictionConfig'in expr or expr==b'None':continue
   edits.append((begin,end,module.encode()+b'.LlmPredictionConfig.from_dict('+expr+b')'))
 if not edits:continue
 shutil.copy2(p,out/p.name)
 revised=data
 for begin,end,expr in sorted(edits,reverse=True):revised=revised[:begin]+expr+revised[end:]
 ast.parse(revised);p.write_bytes(revised);changes.append(dict(path=str(p),sites=len(edits),before_sha256=hashlib.sha256(data).hexdigest(),after_sha256=hashlib.sha256(revised).hexdigest()))
report=dict(status='SDK_callers_use_typed_prediction_configs',directory=str(out),changes=changes,installed_SDK_modified=False,global_serializer_patch=False,reason='Dictionary config recursively changed JSON Schema property names while required names and callable parser stayed snake_case. Typed LlmPredictionConfig retains raw_tools schema verbatim.');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/SDK-typed-tool-configs-current.json').write_text(json.dumps(report,indent=2)+'\n');print(len(changes),'SDK callers updated')

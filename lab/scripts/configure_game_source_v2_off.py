"""Fix experimental package chat rendering to the trained reasoning-off format.

Only the newly generated pilot package's tokenizer metadata is changed. Base
weights/tokenizer and the existing everyday model definition stay unchanged.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from mlx_lm.tokenizer_utils import load
ROOT=Path(__file__).resolve().parent.parent
r=json.loads((ROOT/'verification/game-source-v2-hybrid-package.json').read_text());dest=Path(r['destination']);job=Path(r['selected_adapter']).parent
backup=job/'native-check/template-before';backup.mkdir(parents=True,exist_ok=True)
config=dest/'tokenizer_config.json';p=json.loads(config.read_text());original=p.get('chat_template') or (dest/'chat_template.jinja').read_text();assert isinstance(original,str)
prefix='{%- set enable_thinking = false -%}\n';assert not original.startswith(prefix)
for path in [config,dest/'chat_template.jinja']:
 if path.exists():shutil.copy2(path,backup/path.name)
p['chat_template']=prefix+original;config.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
if (dest/'chat_template.jinja').exists():
 q=dest/'chat_template.jinja';q.write_text(prefix+q.read_text())
t=load(dest);messages=[{'role':'system','content':'You are a game restoration assistant.'},{'role':'user','content':'Name the instruction architecture.'}]
rendered=t.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=True)
assert 'Reasoning effort is set to' not in rendered and rendered.endswith('<think>\n\n</think>\n\n')
report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'experimental_package_template_fixed_off','destination':str(dest),'reason':'Raw package exposed no reasoning configuration; API reasoning=off was rejected. Pin only this package chat template to training renderer before retry without reasoning parameter.','backup':str(backup),'prefix':prefix,'rendered_probe':rendered,'scope':'Text-only pilot; default everyday model untouched. Fixed off, no UI reasoning toggle promised.'}
(job/'native-check/template-off-review.json').write_text(json.dumps(report,indent=2)+'\n')
r.update(chat_template_reasoning='fixed off in experimental package only',metadata_override_report=str(job/'native-check/template-off-review.json'),model_files_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in dest.iterdir() if x.is_file()})
for path in [job/'hybrid-package.json',ROOT/'verification/game-source-v2-hybrid-package.json']:path.write_text(json.dumps(r,indent=2)+'\n')
print(report['status'])

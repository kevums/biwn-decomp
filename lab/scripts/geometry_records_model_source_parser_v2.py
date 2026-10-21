"""Classify incomplete generations before checking the exact C interface."""
import re
from run_local_geometry_records_source_v1 import ALLOWED
class SourceFormError(ValueError):
 def __init__(self,kind,**detail):self.detail=dict(kind=kind,**detail);super().__init__(str(self.detail))
def extract(raw,output_tokens=None,output_cap=None):
 text=raw.strip();normalization=[];missing_fence=False
 if text.startswith('```'):
  first,separator,text=text.partition('\n')
  if not separator:raise SourceFormError('incomplete_generation',reason='Opening fence has no source')
  if first not in ['```c','```c99','```']:raise SourceFormError('unsupported_fence',opening=first)
  if text.rstrip().endswith('```'):text=text.rstrip()[:-3].rstrip()
  else:missing_fence=True
  normalization.append('outer fence removed')
 clean=re.sub(r'/\*[\s\S]*?\*/|//[^\n]*','',text).strip()
 balance={key:0 for key in ['{','(','[']};pairs={'}':'{',')':'(',']':'['};bad_closer=False
 for char in clean:
  if char in balance:balance[char]+=1
  elif char in pairs:
   key=pairs[char];balance[key]-=1
   if balance[key]<0:bad_closer=True
 if any(v>0 for v in balance.values())or clean.count('/*')>clean.count('*/'):
  raise SourceFormError('incomplete_generation',opening_signature_valid=bool(re.match(r'^static\s+void\s+geometry_records_body\s*\(',clean)),closing_fence_missing=missing_fence,balance=balance,at_output_cap=output_tokens is not None and output_cap is not None and output_tokens>=output_cap-1,action='Use concise complete source or a bounded section; do not repeat the truncated response as a signature repair')
 if bad_closer:raise SourceFormError('unbalanced_source',balance=balance)
 if len(text.encode())>34000 or re.search(r'[#"\']|\b(?:asm|extern|volatile|switch|system|dlopen|syscall)\b|__|s\s*->\s*(?:bus|service|opaque)|\(\s*(?:u?int\d+_t|void|char)\s*\*',clean):raise SourceFormError('restricted_source_form')
 if not re.match(r'^static\s+void\s+geometry_records_body\s*\(\s*struct\s+biwn_deck_context\s*\*\s*s\s*\)\s*\{',clean):raise SourceFormError('wrong_function_signature')
 depth=0
 for index,char in enumerate(clean[clean.index('{'):],start=clean.index('{')):
  if char=='{':depth+=1
  if char=='}':depth-=1
  if depth==0 and clean[index+1:].strip():raise SourceFormError('trailing_source')
 invalid=set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',clean))-ALLOWED
 if invalid:raise SourceFormError('unsupported_calls',calls=sorted(invalid))
 for name in ['GEOMETRY_RECORDS_BEGIN','GEOMETRY_RECORDS_END']:
  if len(re.findall(r'\b'+name+r'\s*\(',clean))!=1:raise SourceFormError('wrong_marker_count',marker=name)
 if not re.search(r'uint32_t\s*\*\s*r\s*=\s*s\s*->\s*cpu\s*\.\s*registers\s*[,;]',clean)or re.search(r'uint32_t\s+r\s*\[',clean):raise SourceFormError('logical_register_alias_required',action='Use uint32_t *r=s->cpu.registers; helpers read and write that same array')
 if re.search(r'(?:^|[;{}])\s*scene_shift\s*\(',clean):raise SourceFormError('ignored_shift_return',action='Assign the returned value to the intended logical register')
 return text,'; '.join(normalization)or'none'

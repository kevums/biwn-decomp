"""Render read-only ownership checks; never alter guest CPU or RAM."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(build):
 path=ROOT/'scripts/native_task_arena_observer_v1.inc.c';text=path.read_text()
 values={'__ARENA__':build['arena_address'],'__CODE_BYTES__':build['linked_component_bytes'],'__POOL_ENTRY__':build['pool_symbols']['biwn_native_task_pool_initialize'],'__POOL_START__':build['pool_start'],'__POOL_END__':build['pool_end']}
 for k,v in values.items():assert k in text;text=text.replace(k,str(v)+'u')
 return text,path
def adapt_parent_stacks(text):
 counts={}
 for ceiling in ['0x1ffbc0u','0x1ffbfcu']:
  old=f'!task||task>{ceiling}||sp<task+38u||sp>task+0x404u'
  counts[ceiling]=text.count(old);text=text.replace(old,'!task_stack_valid(task,sp)')
 assert sum(counts.values())==13,counts
 # Headroom continues to describe the original task stack, independently of the arena.
 import re
 text,n=re.subn(r'else if\((sp-task-38u<[^)]+)\)',r'else if(task_original_stack_valid(task,sp)&&\1)',text)
 assert n>=10,n
 assert 'sp>task+0x404u' not in text
 return text,dict(predicate_replacements=counts,headroom_original_stack_only=n)
def render_mailbox(build):
 from gpu_mailbox_observer_source_v4 import render as old_render
 text,path=old_render(build)
 old='call->context=call->sp-124u;';assert text.count(old)==1
 text=text.replace(old,'call->context=task_arena_top(task)-124u;')
 old='call->native=1;mb_native[kind]++;';assert text.count(old)==1
 text=text.replace(old,'call->native=1;arena_active[task_arena_slot(task)]=1;arena_used[task_arena_slot(task)]=1;mb_native[kind]++;')
 old='!task||task>0x1ffbfcu||sp<task+38u||sp>task+0x404u';assert text.count(old)==1
 text=text.replace(old,'!task_stack_valid(task,sp)').replace('else if(sp-task-38u<mb_min_headroom)','else if(task_original_stack_valid(task,sp)&&sp-task-38u<mb_min_headroom)')
 old='if(current.r[15]<call->minimum)call->minimum=current.r[15];';assert text.count(old)==1
 text=text.replace(old,old+'\n if(call->native&&task_arena_stack_valid(task,current.r[15])){uint32_t depth=task_arena_top(task)-current.r[15];if(depth>arena_max_depth)arena_max_depth=depth;arena_stack_observations++;}')
 old='call->pending=0;mb_pending--;';assert text.count(old)==1
 text=text.replace(old,'if(call->native){arena_check_guards();arena_active[task_arena_slot(task)]=0;}\n  '+old)
 return text,path

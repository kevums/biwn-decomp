"""Render read-only CPU-return/helper/context monitor for the two GPU wrappers.
Full ordered mailbox semantics remain component-test coverage. This monitor
checks live CPU/SR/banks/arguments, two actual wait entries and task stacks.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(build):
 path=ROOT/'scripts/native_gpu_mailbox_observer.inc.c';source=path.read_text();symbols=build['mailbox_symbols']
 replacements={'__MB_START__':build['mailbox_start'],'__MB_END__':build['mailbox_end'],'__MB_4320__':symbols['biwn_native_gpu_submit_4320'],'__MB_4B00__':symbols['biwn_native_gpu_submit_4b00'],'__MB_RETURN_4320__':symbols['biwn_native_gpu_submit_4320_return'],'__MB_RETURN_4B00__':symbols['biwn_native_gpu_submit_4b00_return'],'__MB_BODY__':symbols['biwn_native_gpu_mailbox_body']}
 for key,value in replacements.items():assert key in source;source=source.replace(key,str(value)+'u')
 return source,path

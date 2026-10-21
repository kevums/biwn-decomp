"""Read-only six-root shared bridge monitor including global scene admission."""
from pathlib import Path
import re,subprocess
import task_arena_observer_source_v2 as regions
import check_native_deck_shared_v4 as kernel
ROOT=kernel.ROOT
LAYOUT={**kernel.LAYOUT,'scene':(0x17e0e,144,608,816)}
def observer_source(build,parent):
 source=ROOT/'verification/native-Deck-coordinate-v2-route/20261019T182433.767570Z-candidate-1851/frame-acquire-observer.c';text=source.read_text();old=regions.checker(parent);assert text.count(old)==1
 checker=regions.checker(build);anchor='  if(!used[i]&&memcmp';assert anchor in checker
 guard=''.join(f'  if(memcmp(memory+p+{lo}u,expected+p+{lo}u-{build["resident_address"]}u,{hi-lo}u))errors++;\n'for lo,hi in kernel.FENCES[1:-1]);text=text.replace(old,checker.replace(anchor,guard+anchor)).replace(str(parent['heap_start'])+'u',str(build['heap_start'])+'u')
 s=build['shared_Deck_symbols'];names=list(LAYOUT);elf=Path(build['directory'])/'five-build/native-shared.elf';table=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-readelf'),'-sW',str(elf)],text=True);functions=[int(row.split()[1],16)for row in table.splitlines()if len(row.split())>=8 and row.split()[3]=='FUNC'and row.split()[6]=='1'];floor=min(functions);assert floor==s['midpoint']==s['biwn_v4_scene_capture_end']+8
 def array(values):return '{'+','.join(str(v)+'u'for v in values)+'}'
 helpers=[[0xe26c,0xe540],[0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a],[0x10c6e,0x10cb6],[0x11b4c,0x1186a,0x11d1a],[0x10968,0x11384,0x10ba4,0x1142e,0x10734],[0x170a0]]
 replacements=dict(ROOTS=array([LAYOUT[n][0]for n in names]),ENDS=array([0x11e64,0x11d1a,0x11ad4,0x1186a,0x11b4c,0x17f14]),ENTRIES=array([s['biwn_v4_'+n]for n in names]),RETURNS=array([s['biwn_v4_'+n+'_return']for n in names]),HELPER_RETURNS=array([s['biwn_v4_'+n+'_helper_return']for n in names]),CAPTURE_ENDS=array([s['biwn_v4_'+n+'_capture_end']for n in names]),FALLBACKS=array([s['biwn_v4_'+n+'_original_fallback']for n in names]),OFFSETS=array([LAYOUT[n][1]for n in names]),LOWS=array([LAYOUT[n][2]for n in names]),TOPS=array([LAYOUT[n][3]for n in names]),HELPERS='{'+','.join(array(h+[0]*(9-len(h)))for h in helpers)+'}',CODE_LO=str(build['shared_Deck_code_address'])+'u',CODE_HI=str(build['shared_Deck_code_address']+build['shared_Deck_code_bytes'])+'u',ARENA=str(build['deck_arena_address'])+'u',C_FLOOR=str(floor)+'u')
 data=Path(__file__).with_name('scene17_shared_watch_v1.inc.c').read_text()
 for key,value in replacements.items():data=re.sub(r'\b'+key+r'\b',lambda _:value,data)
 # The retained source calls its raw RAM pointer ram; the watcher uses memory.
 data=data.replace('memory+','ram+')
 watch=f'''static void native_deck_watch(uint32_t pc){{
 shared_watch(pc);
 if(pc==0x11d1au)deck_entries++;
 if(pc>0x11d1au&&pc<0x11e64u)deck_source_steps++;
 if(pc=={s['biwn_v4_coordinate']}u){{deck_native_entries++;uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta<0x19400u&&!(delta&1023u))deck_valid_entries++;else deck_invalid_entries++;}}
 if(pc=={s['biwn_v4_coordinate_return']}u)deck_native_returns++;
}}\n'''
 text,n=re.subn(r'static void native_deck_watch\(uint32_t pc\)\{.*?\n\}',lambda _:data+watch,text,count=1,flags=re.S);assert n==1
 text=text.replace('int observer_quiescent(void){','static int retained_observer_quiescent(void){',1);text+='\nint observer_quiescent(void){return retained_observer_quiescent()&&!shared_pending_total();}\n';return text,source

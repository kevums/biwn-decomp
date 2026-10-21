"""Discontiguous immutable-code checks and separate Deck-arena ownership.

The old contiguous code-byte count crossed into the mutable GPU arena after
the Deck code append. All immutable bytes are now checked in two ranges.
"""
from pathlib import Path
import task_arena_observer_source_v1 as prior
adapt_parent_stacks=prior.adapt_parent_stacks
def checker(build):
 base=build['resident_address'];a=build['arena_address'];end=build['arena_end'];deck=build['deck_arena_address']
 assert base<a<end<deck and build['deck_arena_bytes']==101*1024
 return f'''
static unsigned native_deck_regions(const uint8_t *memory,const uint8_t *expected,const uint8_t *used){{
 unsigned errors=0;
 if(memcmp(memory+{base}u,expected,{a-base}u))errors++;
 if(memcmp(memory+{end}u,expected+{end-base}u,{deck-end}u))errors++;
 for(unsigned i=0;i<101;i++){{
  uint32_t p={deck}u+i*1024u;
  if(memcmp(memory+p,expected+p-{base}u,16)||memcmp(memory+p+1008u,expected+p+1008u-{base}u,16))errors++;
  if(!used[i]&&memcmp(memory+p,expected+p-{base}u,1024))errors++;
 }}
 return errors;
}}
'''
def render(build):
 text,_=prior.render(build);check=checker(build);entry=build['deck_symbols']['biwn_native_deck_coordinate'];ret=build['deck_symbols']['biwn_native_deck_coordinate_return']
 pre=f'''
static uint8_t deck_used[101];
static uint64_t deck_entries,deck_native_entries,deck_valid_entries,deck_native_returns,deck_source_steps,deck_invalid_entries;
static void native_deck_watch(uint32_t pc){{
 if(pc==0x11d1au)deck_entries++;
 if(pc>0x11d1au&&pc<0x11e64u)deck_source_steps++;
 if(pc=={entry}u){{
  deck_native_entries++;uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
  if(delta<0x19400u&&!(delta&1023u)){{deck_used[delta/1024u]=1;deck_valid_entries++;}}
  else deck_invalid_entries++;
 }}
 if(pc=={ret}u)deck_native_returns++;
}}
'''
 old=f'if(memcmp(ram+0x15edc0u,payload,{build["linked_component_bytes"]}u))arena_errors++;';assert text.count(old)==1
 text=text.replace(old,'arena_errors+=native_deck_regions(ram,payload,deck_used);\n if(deck_valid_entries!=deck_native_returns)arena_errors++;')
 text=text.replace('static void watch_pool_arena(uint32_t pc){','static void watch_pool_arena(uint32_t pc){\n native_deck_watch(pc);')
 anchor='static void arena_dump(FILE *file){';assert anchor in text
 text=text.replace(anchor,anchor+'''\n fprintf(file,",\\"deck_entries\\":%llu,\\"deck_native_entries\\":%llu,\\"deck_native_returns\\":%llu,\\"deck_source_steps\\":%llu,\\"deck_invalid_entries\\":%llu",(unsigned long long)deck_entries,(unsigned long long)deck_native_entries,(unsigned long long)deck_native_returns,(unsigned long long)deck_source_steps,(unsigned long long)deck_invalid_entries);
''')
 return check+pre+text,Path(__file__).resolve()

"""Resolve unique GCC LTO spellings without changing build addresses or code."""
def with_aliases(build):
 result=dict(build);symbols=dict(build['shared_Deck_symbols'])
 groups={}
 for name,value in symbols.items():
  if '.lto_priv.'in name:groups.setdefault(name.split('.lto_priv.')[0],[]).append(value)
 for name,values in groups.items():
  if name not in symbols:
   assert len(set(values))==1,(name,values);symbols[name]=values[0]
 result['shared_Deck_symbols']=symbols
 return result

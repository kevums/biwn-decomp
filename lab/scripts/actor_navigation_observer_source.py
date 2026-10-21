"""Render the four navigation observer entry/return constants from linked metadata."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(build):
 path=ROOT/'scripts/native_actor_navigation_observer.inc.c';source=path.read_text();s=build['navigation_symbols']
 def array(values):return '{'+','.join(str(v)+'u'for v in values)+'}'
 replacements={'__AN_COMPILED__':array(build['navigation_entries'][hex(k)]for k in [0xf368,0x13f12,0x13f7c,0x13fea]),'__AN_RETURN__':array(build['navigation_returns'][hex(k)]for k in [0xf368,0x13f12,0x13f7c,0x13fea]),'__AN_START__':str(build['navigation_start'])+'u','__AN_END__':str(build['navigation_end'])+'u','__AN_BODY__':str(s['biwn_native_actor_navigation_body'])+'u'}
 for k,v in replacements.items():assert k in source;source=source.replace(k,v)
 assert '__AN_'not in source;return source,path

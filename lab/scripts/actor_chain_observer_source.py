"""Materialize shared-context observer constants from the normalized linked image."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def render(build):
    path=ROOT/'scripts/native_actor_chain_observer.inc.c';text=path.read_text()
    def array(values):return '{'+','.join(str(v)+'u'for v in values)+'}'
    replacements={'__ACH_COMPILED__':array([build['actor_move_entry'],build['collision_entries']['outdoor'],build['collision_entries']['indoor']]),'__ACH_RETURN__':array([build['actor_move_return'],build['collision_returns']['outdoor'],build['collision_returns']['indoor']]),'__ACH_HELPER_RETURN__':array([row['return_PC']for row in build['actor_chain_helpers']]),'__ACH_HELPER_TARGET__':array([row['target']for row in build['actor_chain_helpers']]),'__ACH_START__':str(build['actor_chain_start'])+'u','__ACH_END__':str(build['actor_chain_end'])+'u','__ACH_VIRTUAL_ENTRY__':str(build['actor_chain_virtual_collision_entry'])+'u','__ACH_VIRTUAL_RETURN__':str(build['actor_chain_virtual_collision_return'])+'u'}
    for old,new in replacements.items():assert old in text;text=text.replace(old,new)
    assert '__ACH_'not in text
    return text,path

"""Movement fixtures with actual original direction/signed-division instructions."""
import native_actor_move_fixture_env as base
import check_biwn_actor_direction as direction
from types import SimpleNamespace
ROOT,sha,save,read,SP,STOP,cases=base.ROOT,base.sha,base.save,base.read,base.SP,base.STOP,base.cases
movement,creation=base.movement,base.creation
prior=SimpleNamespace(Script=base.Script,WIDTHS={**base.prior.WIDTHS,0xe588:[4,4]},CODE_RANGES=base.prior.CODE_RANGES+direction.RANGES,world=base.prior.world,__file__=__file__)
SERVICES=base.SERVICES-{0x13440};MEMBERS=base.MEMBERS|{0x13440,0xe588}

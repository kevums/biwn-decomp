"""Current checked stack-repair prototype; retain failed image distinctions."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args()
    p=load(ROOT);a=p['current_acquire_arena_stack_progress']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint. Complete source-only Jaguar rebuild remains unfinished.')
    print('Gameplay: reviewed v34; v37 video failure and v38 stack failure remain unpromoted.')
    print('New source prototype: 676-byte resource adapter shares per-task scratch; no additional RAM reserved.')
    print('Actual compiled resource/loader chain: 27 paired caller cases pass on each CPU core; six loads/copies per matrix.')
    print('Measured stack: guest 786 bytes, fallback 524; private scratch 180/224 bytes, with fences intact.')
    print('Input v6: provisional 768-byte reserve; 20,188 entry-route checks pass; copied SDK rebuild identical.')
    print('Adapter-only checks: 432 cases cover all 101 task slots and seven invalid IDs, with capture/restore intact.')
    print('Not installed in a new image. Real task switches, arena conflicts, IRQs and fresh gameplay remain open.')
    print('Models: no new predictions or weight updates; useful trained gain and LM Studio Chat visibility remain unverified.')
    print('Details and preserved failures: '+a['report'])
    if args.brief:return
    print('\nReducing the old private gap to448bytes was rejected: a nested loader overwrote parked acquire state after six completed comparisons. The new prototype moves the compiler stack instead of shrinking its separation from guest helpers.')
    print('Both lanes retain the compiled acquire/release/load/heap/copy/matrix providers. The input C algorithm is unchanged. Only its reserve immediate changes512to768, one byte at the same code address; all ELF symbol addresses match.')
    print('Primary CPU checks ordered accesses outside the current task224byte private scratch interior and detects writes into parked acquire state. Raw private differences are saved; actual runtime RAM is never normalized. The pinned core checks RAM/context and return snapshots; data-bus order is unobserved there.')
    print('Each matrix uses9native,9supervisor-fallback and9valid-headroom-fallback cases. The new headroom fixture starts at task+800. Original task+500cannot fit all compiled resource paths and is not called a passing fallback.')
    print('Six controlled loader yields and21parked-state checks execute per matrix. Transport/data/progress/cache wait/signal and boundary backends remain controlled; original GPU4320 completes synchronously.')
    print('The432identity cases use an explicit RTS C-body provider; they prove adapter selection/capture/restore only. They do not add432resource, scheduler or IRQ comparisons.')
    print('The prototype code is at fixture1F0000, with five explicit jump stubs in an in-memory resident copy. New image placement, scratch ownership across real task switches/IRQs/reentry, exact-image gates and fresh gameplay still require qualification.')
    print('The failed v38 CDI and installed preview are unchanged. No new model generation, optimizer update or weight training occurred.')


if __name__=='__main__':main()

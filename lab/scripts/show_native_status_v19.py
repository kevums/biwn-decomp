"""Show current image failure and checked component results without inference."""
import argparse
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brief', action='store_true')
    args = ap.parse_args()
    p = load(ROOT)
    s = p['current_input_stream_rebase_progress']
    b = p['unqualified_native_input_image']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint. Complete source-only Jaguar rebuild remains unfinished.')
    print('Gameplay: reviewed v34; v37 remains unpromoted after its matrix-video failure.')
    print(f"Input v5: {s['module_bytes']:,} bytes rebased; runtime source unchanged; copied SDK rebuild identical.")
    print('Controlled loader checks: 27 paired cases on each CPU core; actual payload copying passes.')
    print(f"Experimental v38: built; startup passes on both cores; 192 heap checks pass; initial heap {b['initial_heap_bytes']:,} bytes.")
    print('Image integration FAIL: native resource path reaches 958 stack bytes and changes protected task bytes; confirmed on both cores.')
    print('The 512-byte admission reserve is insufficient for this image path. v38 is unpromoted; preview unchanged.')
    print('Local models: structured Reader prepared, zero predictions because the inference lease was unavailable; default unchanged.')
    print('Training: useful gain on untouched tasks remains unproven; no new weight updates. LM Studio Chat visibility unverified.')
    print('Details and saved prompts: ' + b['report'])
    if args.brief:
        return
    print('\nThe 458-byte controlled-loader peak used original resource helpers. The image uses inherited compiled resource helpers; those provider sets have different stack requirements.')
    print('First image violation: PC 0x1603fe, SP 0x0c0966, task 0x0c0928. Bytes 62 and 63 of the protected 64-byte region changed. Execution stopped at that boundary; 958 is not a completed-path maximum.')
    print('Input runtime statements are unchanged from v4. The rebase changes 144 bytes at 48 checked ELF relocations; byte-prefix identity is not claimed.')
    print('Both startup cores match an independent full 2 MB RAM oracle, including saved stack bytes, both cleared/fenced arenas and input payload. These are startup checks, not gameplay or console qualification.')
    print('Transport/data/progress, cache wait/signal and boundary services remain controlled in the 27-case loader matrix. Pinned-core data-bus order is unobserved; the primary test separately checks ordered CPU accesses.')
    print('Next: repair private/guest stack separation and admission for the actual compiled resource chain, then repeat image-specific provider, nesting, IRQ, observer and fresh-game qualification. No gate is waived.')
    print('Exact prepared Reader prompt/schema and prior local Coder transcript: ' + s['prepared_Reader_directory'])


if __name__ == '__main__':
    main()

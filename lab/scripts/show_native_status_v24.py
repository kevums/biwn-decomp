"""Current v41 actor-phase route pass, retaining fidelity and model limits."""
import argparse
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brief', action='store_true')
    ap.parse_args()
    packet = load(ROOT)
    p = packet['current_actor_phased_image_progress']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; click the window, P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint; complete source-only Jaguar rebuild remains unfinished.')
    print('New v41 experimental image: phased actors pass the previously failing route; remains unpromoted.')
    print('Fresh route: candidate 25,024 frames, original-input control 25,011; both complete the Deck trial.')
    print('Each lane: actor dispatch 15/15, initializer 13/13, frame acquire 124/124; zero reported stack errors.')
    print('Fidelity open: 6,950 paired video differences; final video/selected fields agree; both audio captures silent.')
    print('Finite actors: 1,024 initializer + 856 joint cases, 232 task-layout pairs/101 slots, two copied builds pass.')
    print('Actor C-phase bounds 136/156 bytes exclude helpers/IRQs; no added arena; initial heap 122,560 bytes.')
    print('Next: fixed-input and broader indoor/device/audio checks, full source recovery and console validation.')
    print('Models: Reviewer prompt saved; lease unavailable, zero new predictions/weights; native Chat ease remains unverified.')
    print('Details and preserved failures: ' + p['report'])


if __name__ == '__main__':
    main()

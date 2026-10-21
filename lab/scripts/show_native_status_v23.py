"""Current v40 frame-acquire fix and newly exposed actor-init failure."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');ap.parse_args()
    packet=load(ROOT);p=packet['current_frame_phased_image_progress']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; click the window, P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint; complete source-only Jaguar rebuild remains unfinished.')
    print('New v40 experimental image: phased frame-acquire implementation built; remains unpromoted.')
    print('Frame acquire: candidate 75/75 calls returned with zero stack errors; the earlier frame-header defect is fixed.')
    print('New blocker: actor initialization at frame 8,978; argument/call/prologue overwrite 2/6/26 task-header bytes.')
    print('Fresh route: native-input candidate failed after 34,619 frames; original-input control completed 25,015.')
    print('Finite checks: 631 CPU/RAM cases, 192 DIVS/RTE cases, 634 image provider pairs and 31 preflight gates pass.')
    print('Frame C phases: 184-byte static bound excludes helpers/IRQs; nested fixtures use 448; initial heap 122,560 bytes.')
    print('Next: phase actor dispatch/initialization, qualify the nested chain, then rerun fresh routes and fidelity checks.')
    print('Models: Reviewer prompt saved; lease unavailable, zero new predictions/weights; native Chat ease remains unverified.')
    print('Details and preserved failures: '+p['report'])


if __name__=='__main__':main()

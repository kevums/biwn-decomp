"""Current v39 fresh failure, with baseline and preview preserved."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');ap.parse_args()
    packet=load(ROOT);p=packet['current_resource_arena_image_progress'];f=p['fresh_input_failure']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; click the window, P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint; complete source-only Jaguar rebuild remains unfinished.')
    print('Gameplay baseline: reviewed v34. Experimental v39 native input failed its fresh transition test and is unpromoted.')
    print(f"Fresh input: candidate {f['candidate_frames']:,} frames; original-input control completed {f['control_frames']:,} frames.")
    print('Candidate: one input and one lower-level asset acquire stayed pending; 878 acquire stack-outside observations.')
    print('Resource arena: four candidate and 11 control acquisitions returned; no reported owner conflicts in this route.')
    print('Finite final-address module, alias and read-only observer checks pass; they do not waive the fresh failure.')
    print('Next: fix the transition failure, then repeat changed-code routes and assess video/audio, IRQ and console behavior.')
    print('Models: current briefing prompt saved; inference lease unavailable, zero new predictions or weight updates.')
    print('Reader43 remains an earlier briefing; current native LM Studio Chat ease and useful trained gain remain unverified.')
    print('Details and preserved failures: '+p['report'])


if __name__=='__main__':main()

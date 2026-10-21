"""Current v39 partial image qualification, without inference or promotion."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args();p=load(ROOT);a=p['current_resource_arena_image_progress']
    print('BIWN local workbench — current checked status')
    print('Play: Desktop BIWN Test Preview.app; P starts, arrows move, Shift+Up runs.')
    print('Preview: earlier outdoor checkpoint. Complete source-only Jaguar rebuild remains unfinished.')
    print('Gameplay: reviewed v34. New v39 experimental image is built and remains unpromoted.')
    print('v39 startup: six cases per CPU core and 192 heap checks pass; initial heap 122,816 bytes.')
    print('Actual image caller: 27 paired comparisons per CPU; guest stack 786 bytes, fallback 524; reserved arenas intact.')
    print('Real resource wait: 32 paired cases, 208 task switches and 104 GPU submissions pass at image addresses.')
    print('Selected GPU interrupts: 16 paired cases at four phases preserve CPU, stack banks and all scratch slots through RTE.')
    print('Copied SDK: four newly linked pieces rebuild byte-identically; input v6 copied build retained.')
    print('Remaining: same-task reentry, firmware interrupt branch, wider IRQs, observers and fresh gameplay; preview unchanged.')
    print('Models: no new predictions or weights; useful trained gain and LM Studio Chat visibility remain unverified.')
    print('Details and preserved failures: '+a['report'])
    if args.brief:return
    print('\nResource adapter676bytes at0x17F078, input10580bytes with provisional768reserve. No extra per-task arena allocated; existingGPU224byte scratch is reused. The added code still occupies resident RAM.')
    print('v39 copy132864bytes, stagingclear132928at0xDDAC0, heap0x1A2040. Startup checks full2MBRAM including saved stack/arenas and stops before original400A; it is not a fresh game.')
    print('Real-wait and IRQ cases compare inherited512-gap adapter versus newarena on the pinnedCPU, with actual compiled scheduler and original semaphore/trap/RTE code. TaskBuses its own GPU slot and source4320math synchronously. Full input is not executed in that task fixture; the separate27-case input matrices use controlled transport/wait/signal/yield/boundary providers.')
    print('Only GPU-pending level2/vector64/sourceE7D4bit1 interrupts are checked at four logical phases. Firmware bit0/304E, all instruction boundaries, same-task GPU/resource nesting and arbitrary IRQs remain unqualified.')
    print('Actual-image input comparison excludes the selected224byte private scratch and records raw differences; all other resident code/Deck/outer/otherGPU slots remain exact. PrimaryCPUchecks ordered public accesses and parked-state writes; pinned-core data-bus order is unobserved.')
    print('The explicit component free-root was moved from180000outoftheDeckarena to1A2040/capacity122816. Other supplied owned/free-block fixtures remain component-domain inputs; this is not fresh global heap-ownership proof.')
    print('Copied rebuild covers shared54134/outer6060/resource676/finalizer248bytes. The inherited prefix was hash-checked, not recompiled into a full source-only game.')
    print('v37matrix-video failure and v38task-stack failure remain preserved and unpromoted. Same-console full CPU/GPU/DSP/audio/fidelity, useful training gain and native Chat ease remain unfinished.')


if __name__=='__main__':main()

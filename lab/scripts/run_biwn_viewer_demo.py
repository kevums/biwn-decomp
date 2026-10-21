"""Run the bounded reconstruction proof, then explain it with the local assistant."""
import json
import hashlib
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import assistant_chat
import lab


def publish_summary(proof_path):
    proof=json.loads(proof_path.read_text())
    assert proof['status']=='CPU_GPU_frame_comparison_pass' and all(proof['checks'].values())
    original=Path(proof['reference']);candidate=Path(proof['C_run'])
    native=json.loads((original/'report.json').read_text())
    before=(original/'warm-RAM.bin').read_bytes();after=(candidate/'final-RAM.bin').read_bytes()
    def read(data,address,width=4):return int.from_bytes(data[address:address+width],'big')
    def ring(data):
        context=read(data,0xc0920);seen=[]
        while context not in seen:
            assert 0<context<0x200000-64 and len(seen)<256
            seen.append(context);context=read(data,context)
        assert context==seen[0]
        return seen
    initial_ring=ring(before);final_ring=ring(after)
    assert len(initial_ring)==len(final_ring)==19 and set(initial_ring)==set(final_ring)
    slots=[]
    for index in range(36):
        address=0x15b4a0+index*4
        if not 0<read(before,address+2,2)<0x8000:continue
        assert before[address:address+4]==after[address:address+4]
        old=read(before,0x4674c+index*8);new=read(after,0x4674c+index*8)
        assert before[old:old+8192]==after[new:new+8192]
        slots.append(index)
    assert len(slots)==12 and read(after,0x15b530,2)==2
    pcs=native['PC_counts'];assert pcs.get('0x11e86',0)>0 and pcs.get('0x196f8',0)>0 and pcs.get('0x1a54a',0)>0
    summary=dict(status='recorded_19_task_viewer_enter_render_exit_world_continuation_CPU_GPU_match',
        proof=str(proof_path),proof_sha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        recorded_at=proof['recorded_at'],frames=proof['frames'],
        reconstructed_CPU_instructions=proof['owned_CPU_instructions'],GPU_counts=proof['GPU_counts'],
        viewer_render_iterations=pcs['0x11e86'],world_update_returns=pcs['0x1a54a'],
        mail_list_calls=pcs.get('0x16bf4',0),mail_message_calls=pcs.get('0x15e8e',0),
        original_task_contexts=19,task_ring_members_preserved=True,
        restored_active_texture_cache_slots=12,restored_texture_payload_bytes=98304,
        source_inventory_roundtrip_verified=True,recorded_machine_state_restored=True,
        initial_CPU_entry_supplied=False,initial_task_ring_supplied=False,
        initial_GPU_resident_context_supplied=False,external_disc_completion_injected=False,
        original_CPU_GPU_on_C_path=False,DSP_source_owned_in_this_test=False,
        experimental_selector_count13_and_word_scan_patches=True,default_promoted=False,
        source_CPU_authorship='Coordinator static instruction reconstruction, not new local-model code or training.',
        visual_quality_verified=False,
        function_identification='Deck/C-Space interface, previously mislabeled item viewer; supported by embedded game labels, deck equipment text and checked keypad subscene navigation.',
        identification_proof=str(ROOT/'verification/C-space-identification-current.json'),
        visual_review='Captured Deck/C-Space shows patterned yellow/red environments and green polygonal objects. Patterning alone does not establish texture corruption. Original revision23 hardware appearance and intended patched asset layout remain unverified.',
        new_training=False,native_Chat_verified=False,whole_game_complete=False,
        scope=str(proof['frames'])+'frames from the byte-exact original merchant machine checkpoint. Ordinary emulated input enters Deck/C-Space and exits toworld.'+(' Keypad4 opens mail list,A opens a message,C backs through message/list,and0 exits C-Space.'if pcs.get('0x15e8e',0)else' B+C enters and keypad0 exits.')+' Original19task ring,CPU registers/stack,devices and real frame scheduling/CD-HLE streaming retained; no host entry/ring/clock setup or disc-completion injection. Experimental inline selector/count13 and word-aligned marker search remain applied identically to originalCPU and reconstructedC. Every checked CPU state/cost,frame RAM/video/audio and final serialized machine/PCM match. GPU source ownership positive with zero original/rejected CPU/GPU. Original DSP, IRQ,firmwareHLE and device services remain. Finite repaired route,not untouched-original behavior,freshboot,physicalhardware,standalone or whole-game proof.')
    summary['checked_current_summary']=(str(proof['frames'])+'-frame repaired Deck/C-Space route matches originalCPU versus reconstructedCPU/GPU. '+
        ('Opens the Mail and Text Files list, opens and reads a message, backs out of message and list, then exits C-Space and resumes world. 'if pcs.get('0x15e8e',0)else'Enters, renders and exits C-Space, then resumes world. ')+
        'Uses the original19task recorded machine and firmwareCDstreaming. No suppliedCPUentry/taskring or externalcompletion injection. Experimental selector/count13 and word-scan patches; originalDSP/IRQ/HLE/devices remain. Whole-game and standalone completion unverified.')
    text=json.dumps(summary,indent=2)+'\n'
    (ROOT/'verification/natural-viewer-wordscan-summary-current.json').write_text(text)
    for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
        (root/'corpus/game/project-evidence/biwn-natural-viewer-wordscan.json').write_text(text)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mail',action='store_true');options=parser.parse_args()
    out = ROOT/'runs'/('viewer-demo-'+lab.stamp())
    out.mkdir()
    recipe=json.loads((ROOT/'verification'/('C-space-mail-demo-recipe.json'if options.mail else'natural-viewer-demo-recipe.json')).read_text())
    frames=recipe['frames'];capture_frames=recipe.get('capture_frames',[50,120])
    for filename,expected in recipe['hashes'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==expected, ('Recipe file changed',filename)
    record = dict(status='running', commands=[],
                  scope=recipe['scope'],
                  coordinator_runner=True, local_model_executes_comparison=False)
    receipt = out/'receipt.json'
    receipt.write_text(json.dumps(record, indent=2)+'\n')
    print(record['scope'], flush=True)
    print('1. Run original and reconstructed CPU/GPU for'+str(frames)+'frames: enter Deck/C-Space,'+('read mail,'if options.mail else'render,')+'exit,resume real19task world.', flush=True)
    print('Exact command and runner output: '+str(out), flush=True)
    try:
        for phase,key in [('reference','reference'),('C','candidate')]:
            command=list(recipe[key]);command[0]=sys.executable
            command[command.index('--output')+1]=str(out/phase)
            for frame in capture_frames:command+=['--capture-frame',str(frame)]
            record['commands'].append(command);receipt.write_text(json.dumps(record,indent=2)+'\n')
            print('Running '+phase+'…',flush=True)
            with (out/(phase+'.log')).open('w')as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
        pointer=out/'comparison.json'
        command=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),
            '--C-run',str(out/'C'),'--reference',str(out/'reference'),'--expected-frames',str(frames),
            '--original-checkpoint-report',recipe['reference'][recipe['reference'].index('--restore-original-report')+1],
            '--experimental-code-overlay',recipe['reference'][recipe['reference'].index('--experimental-code-overlay')+1],
            '--output',str(pointer)]
        record['commands'].append(command)
        with (out/'comparison.log').open('w')as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
        for frame in capture_frames:
            assert(out/'reference'/f'frame-{frame}.png').read_bytes()==(out/'C'/f'frame-{frame}.png').read_bytes()
        summary=publish_summary(pointer)
        record.update(status='comparison_pass_local_explanation_pending',proof=str(pointer),summary=summary,
                      matched_viewer_image=str(out/'C'/f'frame-{capture_frames[0]}.png'),matched_return_image=str(out/'C'/f'frame-{frames}.png'))
        if options.mail:record['matched_mail_image']=str(out/'C/frame-90.png')
        receipt.write_text(json.dumps(record, indent=2)+'\n')
        print('PASS:'+str(frames)+'frames; '+str(summary['viewer_render_iterations'])+'Deck/C-Space iterations; real19task world resumes. All captured frontend images match.',flush=True)
        print('2. Local Game Assistant: read the fresh evidence and explain its limits.', flush=True)
        session = assistant_chat.conversation('game',
            ('Can the reconstructed game open and read a mail message, back out, and return to the world? What was compared, and what remains provided by the emulator? Under130words.'if options.mail else
             'Read the latest Deck/C-Space world-loop evidence. In under120words explain what passed, what remains controlled, and whether this is playable.'))
        record.update(status='comparison_pass_explanation_saved_unreviewed', explanation_session=str(session))
    except Exception as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        receipt.write_text(json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    main()

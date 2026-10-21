"""Publish exact checked readable coordinate-entry source with honest authorship."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    standalone = ROOT / 'verification/coordinator-coordinate-entry-checks-current.json'
    connected = ROOT / 'verification/coordinator-coordinate-entry-linked-digit-checks-current.json'
    plain, linked = [json.loads(p.read_text()) for p in [standalone, connected]]
    source = Path(plain['source']).resolve()
    assert plain['source_authorship'] == linked['source_authorship'] == 'coordinator'
    assert plain['source_sha256'] == linked['source_sha256'] == sha(source)
    for proof in [plain, linked]:
        assert proof['status'] == 'local_coordinate_entry_original_CPU_match'
        assert proof['instruction_coverage'] == [166, 166]
        assert len(proof['native_cases']) == 23 and len(proof['guards']) == 123
        assert proof['full_D0_matches_original']
        assert not proof['full_CPU_state_verified'] and not proof['natural_gameplay_integration_verified']
    assert plain['cases'] == 77 and linked['cases'] == 70
    assert len(linked['digit_source_locations_reached']) == 41
    assert '0x1b718' not in linked['helper_bodies_external'] and len(linked['helper_bodies_external']) == 7
    out = ROOT / 'verification/readable-coordinate-entry' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    for p, name in [(standalone, 'standalone-proof.json'), (connected, 'connected-proof.json'),
                    (source, 'biwn_coordinate_entry.c'), (source.parent / 'biwn_coordinate_entry.h', 'biwn_coordinate_entry.h'),
                    (ROOT / 'scripts/check_biwn_coordinate_entry.py', 'check_biwn_coordinate_entry.py'),
                    (ROOT / 'verification/coordinate-backspace-exhaustive-current.json', 'backspace-proof.json')]:
        shutil.copy2(p, out / name)
    restore = ROOT / 'projects/black-ice-white-noise/restoration'
    prior = ROOT / 'verification/readable-coordinate-entry-current.json'
    if (restore / 'biwn_coordinate_entry.c').exists():
        previous = json.loads(prior.read_text())
        assert sha(restore / 'biwn_coordinate_entry.c') == previous['source_sha256']
        assert sha(restore / 'biwn_coordinate_entry.h') == previous['header_sha256']
        shutil.copy2(prior, out / 'previous-publication.json')
        for name in ['biwn_coordinate_entry.c', 'biwn_coordinate_entry.h']:
            shutil.copy2(restore / name, out / ('previous-' + name))
    for name in ['biwn_coordinate_entry.c', 'biwn_coordinate_entry.h']:
        shutil.copy2(out / name, restore / name)
    receipt = dict(status='readable_coordinate_entry_and_connected_digit_decoder_verified', recorded_at=datetime.now(timezone.utc).isoformat(),
        directory=str(out), source=str(restore / 'biwn_coordinate_entry.c'), source_sha256=sha(source),
        header=str(restore / 'biwn_coordinate_entry.h'), header_sha256=sha(restore / 'biwn_coordinate_entry.h'),
        source_authorship='Codex coordinator', local_model_source_accepted=False,
        original_function_range=['0x18e92', '0x190b8'], instruction_locations=[166, 166],
        standalone_cases=77, connected_digit_cases=70, native_cases_per_lane=23, host_guard_cases_per_lane=123,
        connected_digit_source_locations=41, connected_remaining_helper_bodies=linked['helper_bodies_external'],
        standalone_proof=str(out / 'standalone-proof.json'), connected_proof=str(out / 'connected-proof.json'),
        backspace_all_65536_words_match=True, default_frame_runtime_changed=False, source_repairs_applied=0,
        full_CPU_state_verified=False, natural_gameplay_integration_verified=False, native_Chat_verified=False,
        full_D0_matches_original=True, out_D0_unchanged_on_failure=True,
        new_training=False, whole_game_complete=False,
        scope='Complete semantic coordinate-entry caller: ordered global reads/writes/helper calls, fullD0 and external RAM against original Unicorn, selected pinned native final RAM/D0, all original caller instruction locations covered. Connected lane executes real original1B718versus existing readable C decoder. Callback failures/host operation limits retain exact earlier memory/trace effects and leave outD0 untouched. Clock/input/helper scheduling effects supplied; seven other helper bodies remain external. Excludes other caller-saved registers/CCR/private stack, live frame replacement, physical timing and whole-game/standalone-port completion.')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (ROOT / 'verification/readable-coordinate-entry-current.json').write_text(json.dumps(receipt, indent=2) + '\n')
    with (restore / 'READ ME.txt').open('a') as guide:
        guide.write('\nREADABLE COORDINATE ENTRY — ' + receipt['recorded_at'] + '\n'
                    'biwn_coordinate_entry.c/.h reconstruct the complete18E92..190B8semantic caller, now including full originalD0 via with_result. Coordinator authored; both local-model attempts failed and remain unaccepted.77original-CPU cases cover all166caller instruction locations;70connected cases run the real digit decoder (41locations), with23native cases and123host-error/budget checks per lane. Ordered public bus/helper effects,fullD0 and external RAM match. Backspace /10simplification checked for all65536word inputs. Seven other helper bodies/clock/input/scheduling remain supplied; other CPU registers/private stack/live frames/whole game remain unfinished. No repair, active-preview change or new weight training. Proof: ' + str(ROOT / 'verification/readable-coordinate-entry-current.json') + '\n')
    print(receipt['status'], receipt['source'], flush=True)


if __name__ == '__main__':
    main()

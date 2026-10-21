"""Compare saved divider-zero draw probes and map newly reached source overlays.

Read-only with respect to source image, original emulator and accepted C.
Linear disassembly is an analysis aid, not a code/data classification or C proof.
"""
import hashlib
import json
import struct
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text())
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')
def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    reports = [read(ROOT/'verification'/name) for name in [
        'biwn-gpu-draw-integer-original-probes.json',
        'biwn-gpu-draw-integer-slow-original-probes.json']]
    fast, slow = [Path(report['directory']) for report in reports]
    fast_rows, slow_rows = [read(folder/'cases.json') for folder in [fast, slow]]
    comparisons = []
    for a, b in zip(fast_rows, slow_rows, strict=True):
        assert a['case'] == b['case'] and a['before_GPU']['division_control'] == b['before_GPU']['division_control'] == 0
        stem = f"case-{a['case']:02d}"
        before = (fast/f'{stem}-before-RAM.bin').read_bytes()
        fb = int(a['framebuffer_address'], 16)
        fa = (fast/f'{stem}-after-RAM.bin').read_bytes()
        sb = (slow/f'{stem}-after-RAM.bin').read_bytes()
        differing = [i for i, (x, y) in enumerate(zip(fa, sb)) if x != y]
        comparisons.append(dict(case=a['case'],
            before_RAM_equal=before == (slow/f'{stem}-before-RAM.bin').read_bytes(),
            before_GPU_architecture_equal=a['before_GPU'] == b['before_GPU'],
            after_GPU_architecture_equal=a['after_GPU'] == b['after_GPU'],
            direct_PC_sequence_equal=read(fast/f'{stem}-PC-samples.json') == read(slow/f'{stem}-PC-samples.json'),
            queued_commands_equal=a['commands'] == b['commands'],
            framebuffer_changed_bytes_fast=a['framebuffer_changed_bytes'],
            framebuffer_changed_bytes_slow=b['framebuffer_changed_bytes'],
            framebuffer_difference_bytes=sum(fa[i] != sb[i] for i in range(fb, fb+224*180*2)),
            total_RAM_difference_bytes=len(differing),
            outside_framebuffer_difference_bytes=sum(not fb <= i < fb+224*180*2 for i in differing),
            readback_register_window_equal=(fast/f'{stem}-after-blitter-registers.bin').read_bytes() == (slow/f'{stem}-after-blitter-registers.bin').read_bytes()))
    comparison = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        status='completed_backend_comparison_pixels_disagree', GPU_division_control=0,
        fast_directory=str(fast), slow_directory=str(slow), cases=comparisons,
        scope='Same saved inputs, original GPU and pinned core; only fast-blitter selection differs. Pixel disagreement remains unresolved. Neither backend is selected as hardware truth from appearance. These are original-code diagnostics, not a C renderer or playable rebuild.')
    save(ROOT/'verification/biwn-integer-draw-backend-comparison.json', comparison)
    stage = (session/'nextstage-68000-candidate.bin').read_bytes()
    assert sha(stage) == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    decoder = ROOT/'tools/jaguar-disasm/jaguar-disasm'
    decoder_metadata = read(session/'gpu-render-6460-overlay/initial-linear-decode.json')['decoder']
    new_programs = []
    for header in [0x6720, 0x69a0]:
        destination, words = struct.unpack_from('>II', stage, header-0x4000)
        payload = stage[header-0x4000+8:header-0x4000+8+words*4]
        assert len(payload) == words*4 and destination == 0xf03240 and destination+len(payload) <= 0xf04000
        folder = session/f'gpu-render-{header:04x}-overlay'
        folder.mkdir(exist_ok=True)
        (folder/'original-overlay.bin').write_bytes(payload)
        listing = subprocess.check_output([str(decoder), 'gpu', hex(destination)], input=payload, text=False).decode()
        (folder/'initial-linear-decode.txt').write_text(listing)
        rows = []
        for line in listing.splitlines():
            pc, size, assembly = line.split('\t', 2)
            pc, size = int(pc, 16), int(size, 16)
            raw = payload[pc-destination:pc-destination+size]
            opcode = int.from_bytes(raw[:2], 'big')
            rows.append(dict(address=pc, size=size, bytes=raw.hex(), assembly=assembly,
                             opcode=opcode >> 10, M=(opcode >> 5) & 31, N=opcode & 31,
                             classification='linear_decode_code_data_boundary_unverified'))
        program = dict(status='linear_decode_only_code_data_boundaries_unverified',
            CPU_header=hex(header), GPU_load_address=hex(destination), payload_words=words,
            payload_bytes=len(payload), payload_SHA256=sha(payload), rows=rows,
            decoder=decoder_metadata, C_reconstructed=False,
            source_stage_SHA256=sha(stage), observed_in_integer_draw_chain=True,
            scope='Complete header-sized source payload preserved and linearly decoded. Dynamic command reach does not prove every instruction, code/data boundary, renderer completeness or original author intent.')
        save(folder/'initial-linear-decode.json', program)
        new_programs.append({k: v for k, v in program.items() if k not in ['rows', 'decoder']})
    workmap = read(session/'remaining-draw-GPU-workmap.json')
    for program in new_programs:
        workmap['programs'] = [p for p in workmap['programs'] if p['CPU_header'] != program['CPU_header']] + [program]
    workmap['draw_chain'].update(report=str(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json'),
        GPU_division_control=0, projection_list_head_values=[1],
        projection_completion_scope='Integer-mode projection leaves head1 in all four retained draw inputs. The later original draw chain consumes and clears it.',
        queued_commands=reports[0]['commands'],
        hybrid_report=str(ROOT/'verification/biwn-gpu-setup57-integer-hybrid-checks.json'),
        remaining_C_programs=['resident dispatcher F031BE', '0x58a0', '0x6380', '0x6460', '0x6720', '0x69a0'])
    workmap['scope'] = 'Current scene uses host-supplied integer divider mode0, consistent with GPU reset and explicit source4B00 return write0. Prior fractional-mode1 tests remain controlled historical fixtures. C57A0 setup matches four corrected-mode hybrid chains; remaining draw programs/dispatcher still execute original GPU. Two newly reached programs6720/69A0 are only mapped.117selected112CPU/5GPU is not a completion percentage.'
    save(session/'remaining-draw-GPU-workmap.json', workmap)
    resident = read(session/'gpu-draw-resident-workmap.json')
    observed = set()
    for row in fast_rows:
        observed.update(pc for pc in read(fast/f"case-{row['case']:02d}-PC-samples.json") if 0xf03440 <= pc < 0xf03440+2776)
    payload = (session/'gpu-render-58a0-overlay/original-overlay.bin').read_bytes()
    resident.update(source=str(fast), previous_fractional_observed_direct_PC_addresses=resident.get('previous_fractional_observed_direct_PC_addresses', resident['observed_direct_PC_addresses']),
        observed_direct_PC_addresses=len(observed), GPU_division_control=0,
        observed_opcode_counts=dict(Counter(str(int.from_bytes(payload[pc-0xf03440:pc-0xf03440+2], 'big') >> 10) for pc in observed)),
        observed_direct_PC_values=[hex(pc) for pc in sorted(observed)],
        observed_clusters_current=False,
        scope='Current integer-mode original-GPU direct PC samples only; taken delay slots are omitted. Historical clusters are retained separately. Source/control-flow classification and additional fixtures are required before declaring full resident coverage.')
    resident['historical_fractional_observed_clusters'] = resident.pop('observed_clusters', resident.get('historical_fractional_observed_clusters', []))
    save(session/'gpu-draw-resident-workmap.json', resident)
    print(json.dumps(dict(comparison_cases=comparisons, new_programs=new_programs, resident_direct_PC_addresses=len(observed))))

if __name__ == '__main__': main()

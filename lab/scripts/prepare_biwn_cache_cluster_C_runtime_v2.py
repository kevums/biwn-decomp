"""Compile an isolated static instruction provider for the exact cache disc.

The code atlas is compilation metadata, never a restored machine state.
Existing source libraries remain fallback providers; native opcode fallback
is still forbidden by the strict bridge at runtime.
"""
import json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone
import capstone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    bp = ROOT/'verification/native-cache-cluster-build-current.json'
    build = read(bp)
    for key in ['derived_disc', 'derived_stage', 'patch_manifest']:
        assert sha(build[key]) == build[key+'_sha256']
    baseproof = ROOT/'verification/bootstrap-CPU-build-current.json'
    bootstrap = read(baseproof)
    basep = Path(bootstrap['CPU_candidate'])
    assert sha(basep) == bootstrap['source_sha256'][str(basep)]
    base = read(basep)
    beforep = Path(base['instruction_RAM_source'])
    before = beforep.read_bytes()
    assert len(before) == 0x200000
    atlas = bytearray(before)
    atlas[0x4000:0x100000] = Path(build['derived_stage']).read_bytes()
    payload = Path(build['component']).read_bytes()
    resident = build['resident_address']
    atlas[resident:resident+len(payload)] = payload
    out = ROOT/'verification/cache-cluster-C-runtime-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    print(out, flush=True)
    atlasp = out/'instruction-atlas.bin'
    atlasp.write_bytes(atlas)
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)

    def instruction(memory, pc):
        ins = next(decoder.disasm(memory[pc:pc+24], pc, count=1))
        assert not ins.mnemonic.startswith('dc.'), (hex(pc), ins.mnemonic)
        return ins

    patches = read(build['patch_manifest'])['patches']
    jumps = {int(row['address'], 16) for row in patches if bytes.fromhex(row['replacement'])[:2] == b'\x4e\xf9'}
    stage = build['staging_address']
    new_start, new_end = build['frame_acquire_payload_start'], resident+build['linked_component_bytes']
    rows, affected, discarded = {}, [(new_start, new_end), (stage, stage+build['staging_bytes_cleared'])], []
    for key in base['selected_case_sources']:
        pc = int(key, 16)
        if pc in [0x303c, 0x3042, 0x304e, 0x4088]:
            continue
        if new_start <= pc < new_end or stage <= pc < stage+build['staging_bytes_cleared']:
            discarded.append(pc)
            continue
        if any(start < pc < start+6 for start in jumps):
            affected.append((pc, pc+2))
            discarded.append(pc)
            continue
        old = instruction(before, pc)
        if before[pc:pc+old.size] != atlas[pc:pc+old.size]:
            rows[pc] = instruction(atlas, pc)
            affected.append((pc, pc+old.size))
    position = stage
    while position < stage+40:
        ins = instruction(atlas, position)
        assert position+ins.size <= stage+40
        rows[position] = ins
        position += ins.size
    assert position == stage+40
    parent = read(build['parent_build'])
    acquire = read(parent['parent_build'])
    elfs = [Path(acquire['directory'])/'frame-acquire.elf', Path(parent['directory'])/'frame-single.elf']
    elfs += [Path(part['binary']).with_suffix('.elf') for part in build['components']]
    prefix = str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    for i, elf in enumerate(elfs):
        listing = subprocess.check_output([prefix+'objdump', '-d', str(elf)], text=True)
        (out/f'ELF-{i}-disassembly.txt').write_text(listing)
        for line in listing.splitlines():
            fields = line.split('\t')
            if len(fields) < 3 or not fields[0].strip().endswith(':') or not fields[2].strip():
                continue
            try:
                pc = int(fields[0].strip()[:-1], 16)
            except ValueError:
                continue
            assert new_start <= pc < new_end, hex(pc)
            rows[pc] = instruction(atlas, pc)
    for pc in jumps:
        if pc < stage:
            rows[pc] = instruction(atlas, pc)
            affected.append((pc, pc+6))
    listingp = out/'new-instructions.json'
    save(listingp, dict(instructions=[dict(address=hex(pc), size=ins.size, bytes=bytes(ins.bytes).hex(), assembly=ins.mnemonic+' '+ins.op_str) for pc, ins in sorted(rows.items())],
                       discarded_old_instruction_starts=[hex(x) for x in discarded], static_addresses_are_not_execution_coverage=True))
    candidate = out/'CPU-candidate.json'
    builder = ROOT/'scripts/build_biwn_cache_cluster_route_CPU.py'
    command = [str(ROOT/'.venv/bin/python'), '-u', str(builder), '--reference', str(Path(base['warm_RAM_source']).parent),
               '--base-candidate', str(basep), '--output-manifest', str(candidate), '--static-listing', str(listingp),
               '--instruction-RAM', str(atlasp), '--function', 'biwn_cache_cluster_translated_step', '--movie-privileged-events']
    for lo, hi in sorted(set(affected)):
        command += ['--replace-source-range', hex(lo), hex(hi)]
    paths = [ROOT/'scripts/biwn_cache_cluster_CPU_semantics.py', out/'runner-as-run.py', bp, baseproof, basep, beforep, Path(base['library']), Path(build['derived_stage']),
             Path(build['component']), Path(build['patch_manifest']), atlasp, listingp, builder, *elfs]
    state = dict(status='building_static_C_cache_cluster_provider', pid=os.getpid(), directory=str(out), command=command,
                 build_proof=str(bp), build_proof_sha256=sha(bp), CPU_candidate=str(candidate), base_CPU_candidate=str(basep),
                 static_instruction_starts=len(rows), discarded_stale_starts=len(discarded), atlas_is_metadata_only=True,
                 new_training=False, default_promoted=False, whole_game_complete=False,
                 source_sha256={str(p):sha(p) for p in paths})

    def mark():
        save(out/'protocol.json', state)
        save(ROOT/'verification/cache-cluster-C-runtime-build-active.json', state)
    mark()
    with (out/'build.log').open('w') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        state['child_pid'] = child.pid
        mark()
        code = child.wait()
    state.update(exit_code=code, status='terminal_cache_cluster_C_requires_additional_semantics' if code else 'terminal_cache_cluster_C_compiled_pending_checks')
    if not code:
        c = read(candidate)
        state.update(C_library=c['library'], selected_instruction_starts=len(c['selected_case_sources']))
    mark()
    save(ROOT/'verification/cache-cluster-C-runtime-build-current.json', state)
    print(state['status'], flush=True)
    if code:
        print((out/'build.log').read_text()[-3000:], flush=True)


if __name__ == '__main__':
    main()

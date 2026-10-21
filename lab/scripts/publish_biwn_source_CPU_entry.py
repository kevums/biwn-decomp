"""Publish distinct initial-entry, division-gameplay and earlier route scopes."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())

def main():
    pp=ROOT/'verification/native-formatter-C-processors-publication-current.json';parent=read(pp)
    dp=ROOT/'verification/CPU-division-gameplay-publication-current.json';division=read(dp)
    ep=ROOT/'verification/source-CPU-from-entry-current.json';entry=read(ep)
    assert entry['status']=='terminal_source_CPU_from_entry_equal' and entry['frames']==200 and entry['PCM_equal'] and not any(entry['comparisons'].values())
    CPU=entry['C_CPU_backend'];backends=entry['C_processor_backends']
    assert CPU['counts']==dict(Owned=3234720,Original=0,Rejected=0) and CPU['stats']['errors']==0 and CPU['entry_gate']['original_before_owner_install']==0
    assert backends['GPU']['C_source_instructions']>0 and backends['DSP']['owned']>0 and backends['IRQ']['core']['Owned']>0
    deps=dict(division['status_dependencies_sha256'])
    def add(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT),str(p);h=sha(p);assert expected is None or expected==h,str(p)
        if str(p)in deps:assert deps[str(p)]==h,str(p)
        deps[str(p)]=h
    for pub,p in [(parent,pp),(division,dp)]:
        frozen=Path(pub['directory'])/'publication.json';assert sha(frozen)==sha(p);add(frozen)
    for pointer in [ROOT/'verification/pre-mainstage-CPU-inventory-current.json',ROOT/'verification/bootstrap-CPU-build-current.json',ep]:
        data=read(pointer);directory=Path(data['directory']);add(directory/('build.json'if'CPU_candidate'in data else'protocol.json'))
        for p,h in data['source_sha256'].items():add(p,h)
        for p in directory.rglob('*'):
            if p.is_file():add(p)
    build=read(ROOT/'verification/bootstrap-CPU-build-current.json');candidate=read(build['CPU_candidate']);native=read(build['native_CPU_candidate'])
    for p in [Path(candidate['library']),Path(candidate['directory'])/'biwn_route_CPU.c',Path(native['library']),Path(native['directory'])/'fast_CPU_bridge.c']:add(p)
    add(Path(__file__))
    for p,h in deps.items():assert sha(p)==h,p
    now=datetime.now(timezone.utc);out=ROOT/'verification/source-CPU-entry-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    summary=('A separate repaired-disc candidate now owns CPU execution from the HLE-prepared initial entry for200freshframes, with0originalCPUopcodeexecution before or during that window. It performs2525630ordinaryCPUsteps inC plus709090HLE-return adapters; sourceGPU/DSP and interrupt selection/entry are also active. FullCPU,all2MBRAM,GPU/DSPstate,video and silentPCM match the immutable same-core/disc native control at every recorded frame; the control was reused,not rerun. '
        'This initial-entry candidate has not completed the longer gameplay routes. A separate division candidate passes1600freshnormal-gameplayframes after nativebootstrap, including7462normaldivisioncalls and0naturalzeroexceptions. Its localAuthor zero-entry C remains verified by34944nativefixtures and11264strict-owner fault/RTEroundtrips,not by a natural gameplay fault. '
        'Earlier combined-provider1600frame tests and CPU-only24975frame merchant/return equality retain their original scopes; do not attach the new initial-entry ownership to those runs. The separate combined merchant job is outside this terminal publication and must finish independently. '
        'FirmwareHLE,device/IRQline+ACK/vector resolution,hostcommit/prefetch/cost/clock,blitter/objectprocessor services remain. No authenticated firmware boot,standalone console game,general speedup,physical audio or new weights are proved. Existing preview/defaults remain unpromoted.')
    status='terminal_source_CPU_initial_entry_and_division_gameplay_published'
    current=dict(parent['current_status']);current.update(status=status,recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,
        source_CPU_from_initial_entry=dict(frames=200,CPU_owned=CPU['counts']['Owned'],ordinary_C_CPU_steps=CPU['stats']['steps'],HLE_return_adapters=CPU['stats']['HLE'],
            original_CPU_instructions_before_or_during_window=0,C_rejections=0,all_recorded_fields_equal=True,PCM_byte_identical=True,PCM_nonzero_samples=0,
            source_GPU_instructions=backends['GPU']['C_source_instructions'],source_DSP_instructions=backends['DSP']['owned'],source_IRQ_entries=backends['IRQ']['core']['Owned'],
            DSP_profiles=backends['DSP']['profiles'],reference_reused=True,proof=str(Path(entry['directory'])/'protocol.json'),proof_sha256=sha(Path(entry['directory'])/'protocol.json'),
            candidate_native_CPU=build['native_CPU_candidate'],observed_bootstrap_locations=77,observed_locations_already_in_prior_C_catalogue=77,
            new_static_unexecuted_branch_locations=11,new_original_game_functions_claimed=False,
            scope=entry['scope'],long_route_with_this_candidate_verified=False),
        division_backend_gameplay=division['current_status']['fresh_gameplay'],
        local_divzero_C_authorship=division['current_status']['local_Code_Author'],
        source_entry_authorship='Coordinator compiled/integrated existing77observedloaderC locations and11additionalstaticunexecutedbranchlocations. No new local-model code or original-game function recovery is attributed to this integration.',
        long_route_scope='Inherited24975frame C_runtime_comparison is CPU-only after4000; combined1600frame tests also retain nativeCPUbootstrap. New200frame initial-entry ownership is a separate candidate and proof.',
        whole_game_complete=False,physical_console_verified=False,new_training=False,default_promoted=False,goal_complete=False)
    report=ROOT/'reports/BIWN-source-CPU-entry-and-division.txt';current['report']=str(report)
    report.write_text(f'''BIWN — SOURCE CPU FROM INITIAL ENTRY
{now.isoformat()}

The repaired experimental disc now has a separately tested host C CPU candidate that starts at the HLE-prepared initial entry. In 200 fresh frames, it owns 3,234,720 CPU instructions: 2,525,630 ordinary C steps and 709,090 HLE-return adapters. The original CPU opcode count is zero before owner installation and throughout the tested window. C GPU/DSP and source interrupt selection/entry are also exercised.

At every recorded frame, full CPU, all 2 MB RAM, saved GPU/DSP state and video match the immutable native control; silent PCM bytes match too. The exact same-core/disc native 200-frame control was reused from the read-only observation run. No checkpoint was restored and no live guest RAM was patched.

WHAT CHANGED
Read-only observation identified 77 initial-loader instruction locations and 2,837,350 pre-mainstage native callbacks in the prior gated setup. All 77 locations were already in the C catalogue with identical instruction bytes. The coordinator compiled a separate fixed provider, added 11 statically decoded branch locations not exercised in this run, and removed the bootstrap-to-native gate for this candidate. This is new integration/ownership evidence, not 77 newly recovered functions or proof of those 11 unexecuted branches.

SEPARATE DIVISION GAMEPLAY RESULT
Another candidate passes a fresh 1,600-frame C gameplay run after the earlier native bootstrap. Its 7,462 normal division calls (7,443 unsigned, 19 signed) have zero errors, and all recorded CPU/RAM/GPU/DSP/video/control fields and captured silent PCM match native execution. No zero-divisor fault occurs in that normal gameplay run. The local model's unedited zero-entry function is validated by the separate 34,944 native fixtures, 11,264 strict-owner fault/RTE roundtrips and 22 host guards. It is not naturally invoked by those normal gameplay calls.

Keep these candidates and scopes separate from the earlier 24,975-frame CPU-only route and the older combined 1,600-frame tests. The new initial-entry candidate has only the 200-frame proof above. The existing preview and the separate long merchant comparison retain their previous backends. This publication does not poll that live long job or count it as passed.

RETAINED SERVICES
The HLE environment still prepares the initial image and supplies firmware/CD services. Devices, IRQ lines/ACK/vector resolution, host state commit/prefetch, emulator cost/clock, blitter and object-processor services remain supplied. This is not ordinary authenticated firmware boot or a standalone Jaguar source build. Silent PCM is not audible playback evidence, and no whole-game speedup or physical-console/audio result is proved.

Proofs:
{Path(entry['directory'])/'protocol.json'}
{Path(read(ROOT/'verification/CPU-division-fresh-gameplay-current.json')['directory'])/'protocol.json'}
Earlier division report and exact model prompts:
{division['report']}

No new weight training or default promotion occurred. Full game/source/platform reconstruction, more scene/exception/IRQ behavior, representative model training gains, native Chat usability and physical hardware/audio verification remain unfinished.
''')
    add(report)
    publication=dict(status=status,recorded_at=now.isoformat(),directory=str(out),current_status=current,report=str(report),status_dependencies_sha256=deps,integrity_mismatches=0,new_training=False,default_promoted=False,goal_complete=False)
    save(out/'publication.json',publication);save(ROOT/'verification/source-CPU-entry-publication-current.json',publication)
    print(json.dumps(dict(status=status,files=len(deps),original_CPU_opcodes_in_entry_run=0,integrity_mismatches=0,report=str(report))),flush=True)

if __name__=='__main__':main()

"""Publish four source-checked navigation bodies and their actual task integration."""
import collections
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
 now=datetime.now(timezone.utc).isoformat()
 unit=read(ROOT/'verification/biwn-actor-navigation-checks.json');linked=read(ROOT/'verification/biwn-actor-navigation-runtime-checks.json')
 assert unit['CPU_cases']==4096 and unit['CPU_instruction_coverage']==[209,209]and unit['host_guards']==15
 assert linked['cases']==128 and linked['task_handoffs']==3072 and len(linked['scripted_helpers'])==2
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
 validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==96
 backup=ROOT/'verification/actor-navigation-backup'/Path(linked['directory']).name;backup.mkdir(parents=True)
 filenames=['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt',
            'corpus/game/project-intake.json','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json']
 for name in filenames:
  target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(session/'boot-slice-validation.json',backup/'boot-slice-validation.json')
 for proof,checker in [(unit,'check_biwn_actor_navigation.py'),(linked,'check_biwn_actor_navigation_runtime.py')]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass'
  source=ROOT/'projects/black-ice-white-noise/restoration'
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
  snapshot=out/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  names=[checker,'check_biwn_actor_task_runtime.py','check_biwn_actor_task.py','check_biwn_actor_creation.py',
         'check_biwn_scene_loading.py','check_biwn_startup_services.py','check_biwn_boundary_handlers.py',
         'check_biwn_world_update.py','check_biwn_scheduler.py','check_biwn_render_display_runtime.py']
  files=[ROOT/'scripts'/n for n in set(names)]+[source/n for n in proof['source_sha256']]+[ROOT/n for n in ['animation_renderer.py','inventory_renderer.py']]
  for path in files:shutil.copy2(path,snapshot/path.name)
  save(snapshot/'manifest.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files})
 rows=read(Path(unit['directory'])/'fixtures.json');early=rows[4]['CPU'];masked=rows[8]['CPU']
 assert early['registers'][0]==0xaabb0001 and early['SR']==0x18 and early['registers'][2]==0x80000000
 assert masked['registers'][0]==0xaabb0fe0 and masked['registers'][1]==0x1234ffc0
 linked_rows=read(Path(linked['directory'])/'fixtures.json')
 linked['navigation_helper_return_comparisons']=dict(collections.Counter(hex(e['target'])for r in linked_rows for e in r['rebuilt']['navigation_returns']))
 linked['navigation_helper_return_comparisons_total']=sum(linked['navigation_helper_return_comparisons'].values())
 assert linked['navigation_helper_return_comparisons_total']==1279
 linked['matched']=['The original CPU and translated C execute the actor caller, four navigation helper bodies, two idle loops and actual DF60/TRAP0/DE08/RTE scheduling. All registers, full SR, USP/SSP and the complete 2 MB RAM including public headers/private frames match without masks.',
                    'Across 128 cases, eight actor iterations per case yield 3072 scheduler handoffs. All 1279 navigation-helper return CPU states also match, including 708 waypoint, 307 left, 132 right and 132 forward calls.']
 linked['limits']=['RNG1A77C and movement13C9A remain scripted in this integration. Movement field changes and geometry fixtures are explicit test inputs, not reconstructed physics or complete AI.',
                   'This separate actor/two-idle test does not execute actor bodies inside the 21-context startup. Removal TRAP2, real loading switches, remaining task bodies, rendering, full scenes/game/audio and hardware remain incomplete. The C path executes no original CPU/GPU/game frames.']
 save(ROOT/'verification/biwn-actor-navigation-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 scope=('100 checked components: 98 CPU and two GPU. Four navigation bodies F368/13F12/13F7C/13FEA pass 4096 original CPU comparisons, '
        'all 209 instructions and 15 host guards, including full registers, flags, ordered bus accesses and complete RAM/private save frames. '
        'A separate actor/two-idle integration passes 128 cases, 1024 actor iterations, 3072 real scheduler handoffs and 1279 complete navigation-helper return CPU comparisons. '
        'Only RNG and movement remain scripted in that actor test. Geometry and movement field changes are test fixtures. '
        'The 21-context startup still blocks actor bodies. Removal and real loading switches remain unfinished. The actor caller remains pending promotion; four navigation routines are newly counted. '
        'Full boot, complete AI/physics, remaining tasks, live world/render/assets, 3D drawing, scanout, main loop, scenes, audio, game and hardware remain unfinished. Counts are not completion percentages.')
 answers={'checked_waypoint_early_return':'With incoming D0=0xAABBCCDD, D2=0x80000000 and SR=0x0011, heading1 returns D0=0xAABB0001, D2=0x80000000 and SR=0x0018. CLR.W preserves upper D0 bits; MOVE.B writes heading1. The final MOVE.L restoring D2 sets N/Z from D2, not from D0; X remains set.',
          'checked_waypoint_word_arithmetic':'ANDI.W0xFC00 preserves the upper16 coordinate bits. ASL.W6 truncates the low word; the LEA D1.W index is sign-extended from16bits. With coordinate0xAABB1234 and extent0xFFFF, the OR32 path returns D0=0xAABB0FE0; D1=0x1234FFC0. These are original CPU/C checked cases, not local model predictions.',
          'checked_navigation_scope':scope,'checked_examples':[rows[4],rows[8]],
          'role_response_review':'Both ungrounded local source-reading responses were wrong and rejected. The original CPU/C evidence supplies the accepted results; same-model roles are not independent verification.'}
 save(ROOT/'verification/actor-navigation-checked-examples.json',answers)
 validation.update(portable_C_component_count=100,processor_component_counts={'CPU':98,'GPU':2},latest_aggregate_update=now,
                   actor_navigation_reconstruction=unit,actor_navigation_scheduler_integration=linked,
                   component_count_scope='100 checked components: 98 CPU and 2 GPU, across declared standalone/connected proofs. Four new navigation bodies; actor caller still pending real RNG/movement integration. Not a whole game completion percentage.')
 save(session/'boot-slice-validation.json',validation)
 path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
 block="""    navigation_path=root/'verification/biwn-actor-navigation-checks.json'
    navigation_runtime_path=root/'verification/biwn-actor-navigation-runtime-checks.json'
    if navigation_path.exists() and navigation_runtime_path.exists():
        navigation=json.loads(navigation_path.read_text());linked=json.loads(navigation_runtime_path.read_text())
        if navigation['CPU_cases']!=4096 or navigation['CPU_instruction_coverage']!=[209,209]or linked['navigation_helper_return_comparisons_total']!=1279:
            raise ValueError('Actor navigation evidence incomplete')
        runtime['CPU_actor_navigation_reconstruction']={**navigation,'report':str(navigation_path),**json.loads((root/'verification/actor-navigation-checked-examples.json').read_text())}
        runtime['actor_navigation_scheduler_integration']={**linked,'report':str(navigation_runtime_path)}
"""
 assert 'CPU_actor_navigation_reconstruction'not in text;path.write_text(text.replace(needle,block+needle))
 path=ROOT/'chat_tools.py';text=path.read_text().replace("'actor_task', 'actor_creation',","'actor_task', 'actor_navigation', 'actor_creation',").replace("'actor_task','actor_creation',","'actor_task','actor_navigation','actor_creation',")
 text=text.replace('Get checked Black Ice White Noise evidence. Use actor_task','Get checked Black Ice White Noise evidence. Use actor_navigation for F368 waypoint/13F12/13F7C/13FEA steering, full CPU effects, checked D0/SR examples, word masks/sign extension and current actor scheduler helper scope. Use actor_task',1)
 text=text.replace('Six helpers remain scripted; actor bodies are still blocked in the 21-context startup; removal remains pending.', 'Use actor_navigation for the latest four real helper bodies and two remaining RNG/movement scripts. Actor bodies are still blocked in the 21-context startup; removal remains pending.')
 needle="        return compact\n    if topic == 'actor_task':"
 insert="""        if 'actor_navigation_scheduler_integration' in observed:
            compact['separate_actor_navigation_runtime']={k:observed['actor_navigation_scheduler_integration'][k]for k in ['report','cases','actor_iterations','task_handoffs','scripted_helpers','navigation_helper_bodies_real','navigation_helper_return_comparisons_total','startup21context_fixture_linked','removal_TRAP2_executed']}
        return compact
    if topic == 'actor_navigation':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_actor_navigation_reconstruction']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact['CPU_actor_navigation']={key:proof[key]for key in ['report','CPU_cases','CPU_instruction_coverage','host_guards','new_components','entries','code_bytes','inline_jump_table_bytes','matched','limits']}
        compact.update({key:proof[key]for key in ['checked_waypoint_early_return','checked_waypoint_word_arithmetic','checked_navigation_scope','role_response_review']})
        compact['actor_navigation_scheduler_integration']=observed['actor_navigation_scheduler_integration']
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'actor_task':"""
 assert needle in text;text=text.replace(needle,insert)
 start=text.index("        compact['CPU_actor_task_scheduler_integration']=",text.index("    if topic == 'actor_task':"));end=text.index('        compact=latest_pipeline',start)
 text=text[:start]+"        compact['CPU_actor_task_scheduler_integration']=observed['actor_navigation_scheduler_integration']\n        compact['checked_actor_task_scope']="+repr(scope)+'\n'+text[end:]
 needle="            current=concise\n        return record('project_evidence',{'topic':topic},current)"
 replacement="""            if 'separate_actor_navigation_runtime' in current:
                concise['separate_actor_navigation_runtime']=current['separate_actor_navigation_runtime']
                concise['checked_current_summary']+=' Separately, four navigation helpers run in the 128-case actor/two-idle test with 3072 handoffs; RNG and movement remain scripted. This does not run actors in the 21-context startup.'
            current=concise
        return record('project_evidence',{'topic':topic},current)"""
 assert needle in text;text=text.replace(needle,replacement);path.write_text(text)
 path=ROOT/'presets/Game Assistant.system.txt';text=path.read_text().replace('- actor_task:', '- actor_navigation: F368 waypoint and steering helpers, exact checked D0/SR examples, word masks/sign extension, latest separate actor scheduler proof and two remaining scripts.\n- actor_task:',1);path.write_text(text)
 path=ROOT/'presets/Game Assistant.preset.json';preset=read(path)
 for field in preset['operation']['fields']:
  if field['key']=='llm.prediction.systemPrompt':field['value']=text.strip()
 save(path,preset);shutil.copy2(path,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  path=ROOT/name;value=read(path);value['actor_navigation_progress']=scope
  value['actor_navigation_evidence']=[str(ROOT/'verification/biwn-actor-navigation-checks.json'),str(ROOT/'verification/biwn-actor-navigation-runtime-checks.json')]
  if name=='config.json':value['chat_frontend']['game']['status']=scope
  if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
  if name=='verification/setup-status.json':value['game_work']=scope
  if name=='verification/current-runtime-state.json':value['decomp_progress']=scope
  for key in ['actor_task_boundary_progress','actor_task_scheduler_progress']:
   if key in value:value[key]='Historical checkpoint; latest helper scope is actor_navigation_progress. '+value[key]
  if name=='verification/requirements-audit.json':
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['state']=scope
  save(path,value)
 (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nLOCAL INFERENCE\nTwo sequential local source-reading responses were wrong and rejected. Accepted C was authored by Codex and checked against original CPU execution. Native Chat remains unverified while locked; API exchanges are separate from native Chat. Exact local prompts/responses: '+str(Path(read(ROOT/'verification/actor-navigation-local-review-current.json')['directory'])/'prompts-and-responses.txt')+'\n\nNEXT\nReplace the RNG and movement scripts with full callee CPU effects, then connect the actor caller to larger startup/world/render tests. Full goal active and incomplete.\n')
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LATEST GAME RESULT\n');end=text.index('LOCAL INFERENCE RESULT\n',start);path.write_text(text[:start]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[end:])
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':100,'CPU':98,'GPU':2,'navigation_CPU_cases':4096,'navigation_returns':1279,'handoffs':3072}))


if __name__=='__main__':main()

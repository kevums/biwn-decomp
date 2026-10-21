"""Compact checked current status,without model or game execution."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args();p=load(ROOT);c=p['latest_native_candidate'];debug=p['debug_overlay_recovery'];local=p.get('latest_local_source_generation_trial',{})
 print('BIWN — CURRENT CHECKED STATUS\nPlay: Desktop BIWN Test Preview.app,click window and press P. Arrows move;C+Up orShift+Up sends run input. LMStudio is not required for the game window.\n',flush=True)
 print('Latest fresh-reviewed candidate: '+c['variant'],flush=True)
 print(f"{len(c['native_internal_helpers'])} compiled geometry helpers;{c['native_geometry_cases']} native geometry cases,{c['native_retained_cases']:,} retained-caller and{c['native_fallback_cases']:,} fallback cases pass. Peak C stack{c['maximum_observed_C_stack_bytes']}/176bytes.",flush=True)
 if c['fresh_route_completed']:print(f"Fresh candidate/control:{c['candidate_frames']:,}/{c['control_frames']:,}frames;{c['differing_video_frames']}video differences;final video equal:{c['final_video_equal']}. Fidelity unapproved.",flush=True)
 else:print('Final-address/startup/heap/outer component checks pass. New alias,combined and fresh-gameplay checks remain pending.',flush=True)
 if debug.get('native_linked_module_executed'):print('10734 runs in the linked native geometry component with real original formatter/text and blitter. Its earlier standalone object remains compile-only.',flush=True)
 if local.get('shared_native_module_executed'):print('Local Repair: unedited10968function passes260shared-native CPU/RAM/order cases and42budget checks. This separate prototype remains unpromoted and outside the game disc.',flush=True)
 elif local.get('native_function_executed'):print('Local Repair: unedited10968function passes260standalone target68000CPU/RAM/order cases and35budgets. Not in the game disc. Desktop BIWN Code Test.command starts a new Author/check/Repair trial.',flush=True)
 elif local.get('accepted_complete_function'):print('Local Repair: one complete10968function passes260hostCPU/RAM cases,error checks and ordered-access checks. Its targetobject is compile-only;not in the game disc.',flush=True)
 if p.get('native_clear_casts_performance'):print('Coordinator cast optimization: sampled clear-loop cycles42,916 versus62,708 previously;whole geometry samples10–21% lower. Local model Reviewer was incomplete/unapproved. Gameplay fidelity remains open.',flush=True)
 if p.get('native_multiply_progress'):
  m=p['native_multiply_progress'];lo,hi=m['public_cost_ratio_range'];print(f"E540 multiply: prototype passes {m['public_entry_cases']:,} normal and {m['public_guard_cases']:,} guard cases. Public entry costs {lo:.1f}–{hi:.1f} times the original in eight samples; it remains outside the game image.",flush=True)
 if p.get('native_scene_reset_progress'):
  s=p['native_scene_reset_progress'];print(f"1102A reset: {s['body_cases']} standalone and {s['retained_caller_cases']:,} caller cases pass. Earlier raw Author/Repair failed; experimental disc uses hybrid with one coordinator flag-mask correction.",flush=True)
  if s.get('experimental_disc_internal_reset_installed'):print(f"Installed internally in the separate experimental input path; fresh reset entries/returns: {s['fresh_native_reset_entries']}/{s['fresh_native_reset_returns']}. Global original reset entry preserved. Reset-cost approval remains false.",flush=True)
  else:print('Component only; reset not installed in a game image.',flush=True)
  if s.get('cost_measured'):print(f"Reset work samples: {s['sampled_reset_service_cycles']} compiled-service versus {s['original_reset_body_cycles']} original-body emulator cycles; boundaries differ and include dispatch overhead.",flush=True)
 if c.get('native_input_internal_helpers')and not c.get('control_restores_only_scene'):print('Control restores the original input caller; both lanes retain compiled geometry. This does not demonstrate that older original-geometry differences were fixed. Both audio captures are silent.',flush=True)
 if p.get('native_input_optimization_progress'):
  i=p['native_input_optimization_progress'];lo,hi=i['native_input_cycle_reduction_percent_range'];print(f"New input prototype: {i['retained_caller_cases']:,} retained and {i['geometry_regression_cases']} geometry cases;{i['actual_public_bus_order_cases']} actual public-bus traces pass. Eight work samples {lo:.1f}–{hi:.1f}% lower than prior native input;still slower than original. Cost samples are from the prototype;see new-disc qualification below.",flush=True)
  print('Previously fresh-tested input failed case0 bus check: four CLR operand reads missing. New implementation uses seven explicit CLR sites.',flush=True)
 if p.get('native_input_disc_progress'):
  nd=p['native_input_disc_progress'];print(f"New separate input-CLR disc: all8final-address gates,384alias cases,128connected cases and {nd['final_input_public_bus_cases']} bus-order traces pass. Copied final module matches. Earlier input-only image fresh qualification completed;its8differences are separate from the current scene image. Preview unchanged.",flush=True)
 if p.get('native_scene_draw_progress'):
  s=p['native_scene_draw_progress'];print(f"Scene17: {s['shared_bridge_cases']} exact CPU cases; stack {s['shared_bridge_C_stack_bytes']}/208 bytes. Copied native build matches.",flush=True)
  if s.get('latest_fresh_result_is_passing_route'):
   print(f"Native scene: {s['fresh_scene_native_returns']:,} scene returns and {s['fresh_scene_helper_returns']:,} helper returns; all monitors clear. Earlier v22 failed its added work budget and is preserved separately.",flush=True)
   print(f"Fresh video differs on {s['fresh_differing_video_frames']:,} paired frames; feedback inputs differ on {s['held_input_differing_frames']} frames. Final video equal: {s['final_video_equal']}; selected game fields equal: {s['final_selected_game_fields_equal']}. Timing versus logic cause unproven; fidelity unapproved. Preview unchanged.",flush=True)
   if s.get('native_display_integrated'):
    current_prefix=s.get('current_fixed_input_video_comparison',s['fixed_input_comparison']['display-list']['video_sha256'])
    print(f"185B2 display-list, clear and rotation bodies run natively inside the scene caller: {s['native_display_returns']:,} returns each. Global original helper entries remain intact. Fixed-input prefix differs on {current_prefix['count']} video frames; control layout changes affect {s['fixed_input_control_layout_changes']['video_sha256']['count']} frames. No fidelity or speed approval.",flush=True)
    print(f"Minimum sampled free heap while outer active: {s['minimum_sampled_heap_while_outer_active']['candidate']:,} bytes in candidate. This is not a global heap minimum. Connected scene stack uses {s['shared_bridge_C_stack_bytes']}/208 bytes.",flush=True)
   elif s.get('native_clear_integrated'):
    print(f"E03A clear and 17F14 rotation run as structured native code: {s['native_clear_returns']:,} returns each; original 185B2 display-list builder retained. Fixed-input prefix differs on {s['fixed_input_comparison']['clear']['video_sha256']['count']} video frames. Its control differs on {s['fixed_input_control_layout_changes']['video_sha256']['count']} frames from the prior layout. Cross-build counts do not isolate helper timing or establish fidelity.",flush=True)
   elif s.get('native_rotation_integrated'):
    print(f"17F14 buffer rotation runs as structured native code: {s['native_rotation_returns']:,} returns; original185B2display-list builder retained. Fixed-input prefix differs on {s['fixed_input_comparison']['rotation']['video_sha256']['count']} frames. Its control also differs on {s['fixed_input_control_layout_changes']['video_sha256']['count']} frames from the prior layout, so cross-build comparison does not isolate rotation timing. No fidelity or speed approval.",flush=True)
   elif s.get('direct_poll_instructions_per_extra_busy_read'):
    print('Direct GPU polling adds two target instructions per extra busy read in the controlled samples. Fixed identical-input prefix still has194video differences versus189previously; whole-game speedup and fidelity improvement are not established.',flush=True)
  elif s.get('fresh_failure'):print('Fresh scene candidate failed its native work budget; correction still needs fresh validation.',flush=True)
  print('Local scene Author/Repair both rejected; coordinator source and target glue are separate. No new training.',flush=True)
 if p.get('local_scene_clear_development_progress'):
  l=p['local_scene_clear_development_progress']
  if l.get('target_native_cases',0):
   print(f"Local clear v2: one unchanged generated body passes {l['host_cases']} host and {l['target_native_cases']} native cases; Author took {l['author_seconds']} seconds with supplied primitive/addressing scaffolding. Initial native harness import failure was corrected without editing the body. Repair was identical. Separate prototype, outside the game image; no optimizer updates or copied-weight Native Chat verification.",flush=True)
  else:print(f"Local clear trial: {l['new_predictions']} actual predictions. Author failed compilation; Repair compiled but failed CPU/stack/RAM/order. Neither body was installed. Advisory Reviewer prose unapproved; exact prompts, responses and counterexample saved. No optimizer updates or copied-weight Native Chat verification.",flush=True)
 if p.get('native_display_list_progress'):
  d=p['native_display_list_progress']
  if d.get('disc_integrated'):
   print(f"185B2 is integrated in the separate experimental image. Exact final module passes {d['final_deployed_body_cases']} native body and {d['final_deployed_scene_cases']} scene cases, with original CLR dummy reads preserved. Shared module {d['module_bytes']:,} bytes; copied SDK matches. Finite fresh route passes; whole-game and IRQ/audio/console fidelity remain open. Preview unchanged.",flush=True)
  else:print(f"185B2 display-list prototype: compact C passes {d['host_cases']} host cases, {d['distinct_supplemental_reread_cases']} distinct reread fixtures, {d['native_body_cases']} actual native body cases and {d['connected_scene_cases']} connected scene cases. Two native CLR sites preserve the real 68000 dummy reads. Shared module {d['module_bytes']:,} bytes; connected stack {d['connected_C_stack_bytes']}/208 bytes. Copied SDK matches. Final image, alias/nesting and fresh gameplay qualification remain pending; current game disc and preview are unchanged.",flush=True)
 if p.get('local_scene_reset_flags_progress'):print('Local code test: supplied flag primitive lets two unedited Author bodies pass 768 cases each, including the copied launcher. Desktop BIWN Code Test.command and Portable Lab menu4 now run this workflow; menu5 shows saved prompts. These raw bodies are not in the game image.',flush=True)
 if p.get('native_scene_dispatch_headroom_progress'):
  h=p['native_scene_dispatch_headroom_progress']
  if h.get('fresh_gameplay_verified'):
   print(f"V29 direct internal dispatch: fresh route completed with {h['fresh_native_scene_returns']:,} scene returns. Exact connected scene stack is 168/208 bytes; shared module 48,410 bytes. Recorded heap/video limits remain separate from this component saving. Desktop preview unchanged.",flush=True)
  else:print('Separate v29 direct-dispatch component: scene stack 168/208 bytes versus 208/208; module 48,410 bytes, 84 smaller. Native body1153/scene772/retained4992/geometry256 and fallback/nesting/alias checks pass; copied SDK matches. '+('Separate disc built with 64 more initial heap bytes; final qualification is recorded in the current report. No fresh v29 gameplay yet.'if h.get('new_disc_built')else'No v29 disc or fresh gameplay yet.')+' V27 remains the latest gameplay-tested disc; Desktop preview unchanged.',flush=True)
 if p.get('copied_game_training_progress'):print('Copied training capability: two LoRA updates completed with full examples, unchanged base weights and restored model. Peak reported memory 50.4 GB. No adapter enabled or answer-quality improvement established. Desktop BIWN Training Check.command runs an explicit check.',flush=True)
 if p.get('current_copied_Reader_progress'):print('Copied-model Reader: saved briefings and exact prompts are available. Check the current-source verification below; Native Chat using copied weights and broader model quality remain pending.',flush=True)
 elif p.get('portable_copied_reader_progress'):print('Copied-model Reader inference verified after SDK launcher fix. Reader29 source-label failure retained;Reader30 scoped output passes. Native Chat using copied weights and broader model quality remain pending.',flush=True)
 if p.get('portable_native_Chat_progress'):print('Portable native Chat:3actualroles andprompt/response display verified. Firstfinalanswer113words versus95requested;lengthfailed. Desktop BIWN Visible Chat.command opens the prepared frontend.',flush=True)
 elif p.get('game_portable_progress'):print('Portable game snapshot: moved MCP v22,exact native build,SDK/model hashes and targetCPU smoke checks pass. New copied inference/training and nativeChat transport remain pending.',flush=True)
 if p.get('current_copied_Reader_progress',{}).get('status')=='terminal_two_copied_input_Readers_reviewed_unpromoted':print('Latest copied Reader output tests: 13.69/15.68 seconds. Both raw responses retained;neither approved as a complete scoped briefing. No training or broad quality gain.',flush=True)
 if p.get('current_copied_Reader_progress',{}).get('status')=='terminal_current_copied_Reader36_reviewed_word_limit_failed':print('Latest ordinary copied Reader: 11.58 seconds, current v27 factual claims reviewed; 156 words exceeds 150 requested. Earlier failed quality-pilot results omitted. Exact prompt and raw response saved; no training or broad quality gain.',flush=True)
 if p.get('current_copied_Reader_progress',{}).get('latest_source_changed_since_last_prediction'):print('Saved Reader response predates the latest source work. New briefing output has not yet been tested on these updated facts.',flush=True)
 print('Installed preview unchanged. Whole-game source rebuilding and broader fidelity remain incomplete. No new trained weights adopted.',flush=True)
 if not args.brief:print('\nReview:',c['report'],'\nNext:',c['next_action'],flush=True)
if __name__=='__main__':main()

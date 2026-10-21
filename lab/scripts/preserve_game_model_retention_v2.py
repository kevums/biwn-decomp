"""Preservation-only audit: unique trained exports stay; no deletion by recipe."""
from datetime import datetime, timezone
from pathlib import Path
import os
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha


def main():
    oldp = V / 'game-model-space-audit-v1-current.json'
    old = read(oldp)
    shared = Path('/Users/kevin/Documents/Codex/2026-10-20/che/outputs/model-storage-audit-20261021/model-and-checkpoint-inventory.json')
    inventory = read(shared)
    out = ROOT / 'audits/game-preservation-v2' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    state = dict(status='running_readonly_trained_export_preservation_hashes', directory=str(out), pid=os.getpid(),
        deletions=0, moves=0, training_started=False, inference_started=False, native_model_state_changed=False)
    def mark():
        save(out / 'protocol.json', state)
        save(V / 'game-preservation-v2-current.json', state)
    mark()
    rows = []
    deps = {str(p):sha(p) for p in [Path(__file__), oldp, shared]}
    for name in ['cpu-remediation-package.json', 'cpu-remediation-hybrid-package.json', 'game-source-v2-hybrid-package.json']:
        p = V / name
        receipt = read(p)
        folder = Path(receipt.get('destination', receipt.get('model_directory')))
        files = []
        for filename, expected in receipt['model_files_sha256'].items():
            f = folder / filename
            actual = sha(f)
            files.append(dict(path=str(f), bytes=f.stat().st_size, sha256=actual, recorded_sha256=expected, matches_recorded=actual==expected))
        matching_inventory = [x for x in inventory['weights'] if str(folder) + '/' in x['path']]
        other_copy_paths = [x['path'] for x in matching_inventory if not Path(x['path']).is_relative_to(folder)]
        assert not other_copy_paths
        rows.append(dict(model_directory=str(folder), receipt=str(p), files=files,
            all_recorded_files_match=all(x['matches_recorded'] for x in files),
            second_complete_copy_proven=False, native_shards_in_shared_inventory=len(matching_inventory),
            classification='KEEP_UNIQUE_TRAINED_EXPORT', recipe_alone_does_not_authorize_deletion=True))
        deps[str(p)] = sha(p)
        print(folder.name, 'hashed', len(files), 'files; recorded match', rows[-1]['all_recorded_files_match'], flush=True)
    state.update(status='terminal_preservation_only_game_models_and_resume_handoff_recorded',
        human_request=dict(thread_id='01a159fa-426f-73f3-bbfa-026d3fd27e99', message_id='01a15f04-b224-7402-b1f2-9195fc8b7ff4',
            request='Preserve all work between both chats and store it until dedicated local model machine is set up and work can begin again there.'),
        supersedes_cleanup_policy_of=str(oldp), unique_trained_exports=rows,
        older_candidates_reclassified='KEEP unless exact content/configuration is verified in a retained canonical copy or archive. Public re-download and theoretical fusion are insufficient.',
        trained_export_regeneration_run=False, public_models_to_preserve_including_CoderNext_both_formats=True,
        current_daily_target=str(P / 'lmstudio-home/models/lmstudio-community/Qwen3.8-27B-MLX-6bit'),
        native_game_bases_to_preserve=[str(Path.home()/'.lmstudio/models'/x) for x in ['lmstudio-community/Qwen3.8-27B-MLX-6bit','lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-MLX-4bit']],
        game_checkpoint_files=old['game_checkpoint_files'], game_checkpoint_bytes=old['game_checkpoint_logical_bytes'],
        required_game_proof_weight_files=old['current_published_game_status_required_weight_files'],
        preserve_whole_paths=[str(ROOT), str(P), '/Users/kevin/.lmstudio/local-ai-lab', '/Users/kevin/.lmstudio/models',
            '/Users/kevin/.lmstudio/hub/models/local', '/Users/kevin/.lmstudio/conversations'],
        copied_v41_status_and_MCP_verified=True, latest_game_report=str(ROOT/'reports/BIWN v41 Phased Actors and Fresh Route Pass.txt'),
        whole_game_complete=False, model_quality_complete=False, new_predictions=0, optimizer_updates=0,
        source_sha256=deps)
    save(out / 'trained-export-hashes.json', rows)
    handoff = out / 'BIWN preservation and resume handoff.txt'
    handoff.write_text(
        'BIWN — preserve now; resume on the dedicated model machine\n\n'
        'Human request verified in Advance local AI ad research, message01a15f04-b224-7402-b1f2-9195fc8b7ff4:preserve all work across both chats and store until the local model machine is ready. Advancement,training and inference stop. No files or models have been deleted,moved,loaded or unloaded by this audit.\n\n'
        'LATEST GAME CHECKPOINT\nV41nativeactor phases are built and copied; fresh candidate25024/control25011complete the previously failing outdoor/indoor/Deck route. AD15/15,AI13/13,Frame124/124in both lanes,all monitors clear. Final video/selected fields agree;6950paired video differences and both audio captures silent. Unpromoted. Reviewedv34and failedv37-v40and the earlier keyboard preview remain preserved.\n\n'
        'PRESERVE\nKeep the whole lab root,current portable workbench,allBIWNprojects/builds/analysis/assets/saves/verification,alltraining datasets/checkpoints/selected adapters/logs/evaluations/source snapshots,prompts and raw replies. Keep installed preview runtime and native LM Studio configurations,presets,model definitions and conversations. Do not delete an older restore-test workbench or results to remove redundant model payloads. Public models and trained fused exports stay unless another retained copy is byte-verified;recipe/re-download availability is insufficient.84game adapters total3.36GiB and the copied-training adapter directly hashed by current status must stay.\n\n'
        'MODEL DEPENDENCIES\nGame training used the exact27B/6bit base revision05f38c1f39e2f39619653616fe8e96a5d676358e and30B Coder/4bit revisionbbecedefd826819d2c6b6465e88ca7b9b8ad3407. Preserve native base paths. Current daily alias4f5658686590points to the current portable package,which must remain. Unique game-source-pilot-v2,restoration-cpu-remediation-v2andrestoration-cpu-remediation-hybrid-v2have no second complete copy proven in the shared515-path inventory. Current file hashes were checked against saved package receipts;see trained-export-hashes.json. Theoretical fusion does not qualify deletion.\n\n'
        'RESUME\nRead CURRENT DECOMPILATION.txt and verification/goal-continuation-current.json,then verify the current status manifest and the portable package on the new machine. Source actor-phased-fixed-v2and frame-acquire-phased-split-v2are authoritative;use actor_phased_symbols/frame_phased_symbols for internals rather than inherited old capture symbols. Run fixed physical-input and broader indoor/device/audio validation before promotion,then continue full readable CPU/GPU/DSP/firmware source-only console rebuilding. The latest source has no independent local-model review:Reviewer lease attempt0predictions;coordinator authored it. Reader43is historical and must receive a new current-source prompt before relying on generated status. Useful training gain,native Chat usability and actual256GBhardware qualification remain open.\n\n'
        'PREVIEW\nDesktop BIWN Test Preview.app opens the earlier keyboard checkpoint. Click window,Pstarts;arrowsmove;Shift+Up orC+Upruns;Zattack/read;1thenDDeck;Mmute;Escclose. LM Studio not needed. It is not the full rebuilt game.\n\n'
        'Latest detailed report: '+state['latest_game_report']+'\nCurrent package: '+str(P)+'\nRetention details: '+str(out/'protocol.json')+'\n')
    state['resume_handoff'] = str(handoff)
    state['source_sha256'].update({str(p):sha(p) for p in [handoff, out/'trained-export-hashes.json']})
    mark()
    print(state['status'], flush=True)


if __name__ == '__main__':
    main()

"""Read-only game model retention/deletion candidates for the shared audit."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT, V, P, save, sha


def model_inventory(path):
    weights = []
    for p in sorted(path.iterdir()):
        if p.is_file() and p.suffix in ['.safetensors', '.gguf', '.npz']:
            s = p.stat()
            weights.append(dict(path=str(p), resolved=str(p.resolve()), bytes=s.st_size, device=s.st_dev,
                inode=s.st_ino, links=s.st_nlink, allocated_stat_bytes=s.st_blocks*512, symlink=p.is_symlink()))
    return dict(path=str(path), resolved=str(path.resolve()), directory_symlink=path.is_symlink(), weights=weights,
        logical_weight_bytes=sum(x['bytes'] for x in weights))


def main():
    out = ROOT / 'audits/game-model-space-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    home = Path.home() / '.lmstudio/models'
    inventory = [model_inventory(p) for owner in sorted(home.iterdir()) if owner.is_dir() for p in sorted(owner.iterdir()) if p.is_dir()]
    catalog = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'), 'ps', '--json'], cwd='/', text=True, timeout=30))
    save(out / 'native-catalog-observed.json', catalog)
    training = []
    dependencies = [Path(__file__), ROOT / 'models.lock.json', ROOT / 'models.candidate.lock.json', P / 'portable-model-bindings.json']
    for p in sorted((ROOT / 'training/game').rglob('training-result.json')):
        d = json.loads(p.read_text())
        command = d.get('command', [])
        training.append(dict(receipt=str(p), status=d['status'], repo=d.get('base', {}).get('repo'),
            revision=d.get('base', {}).get('revision'), base_path=command[command.index('--model')+1] if '--model' in command else None))
        dependencies.append(p)
    adapters = [p for p in (ROOT / 'training/game').rglob('*.safetensors')]
    adapter_inventory = [dict(path=str(p), bytes=p.stat().st_size) for p in adapters]
    save(out / 'game-checkpoint-inventory.json', adapter_inventory)
    bindings = json.loads((P / 'portable-model-bindings.json').read_text())
    daily = bindings['models']['daily_base']
    keep = [dict(path=str(home / key), reason=reason) for key, reason in [
        ('lmstudio-community/Qwen3.8-27B-MLX-6bit', 'Base for eleven recorded game attempts, including latest geometry64 update pilot; also required by advertising owner.'),
        ('lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-MLX-4bit', 'Base for two recorded early game attempts and selected96 CPU remediation adapter.'),
        ('local/portable-ailab-4f5658686590-daily', 'Active native model alias; resolves to current self-contained portable package. Preserve target and configured definition.')]]
    keep += [dict(path=str(P / daily['relative_weights']), reason='Current active daily base target and portable test package; do not remove or retarget during audit.'),
             dict(path=str(ROOT / 'training'), reason='Preserve all datasets, intermediate/final/selected adapters, configs, source snapshots, optimizer/training/evaluation evidence.'),
             dict(path=str(ROOT / 'projects/black-ice-white-noise'), reason='Preserve all game source, assets, restoration, saves and analysis.'),
             dict(path=str(ROOT / 'builds'), reason='Preserve all tested/failed experimental discs and build inputs.'),
             dict(path=str(ROOT / 'verification'), reason='Preserve proof and runtime evidence, including copied-training adapter required by current published status.'),
             dict(path='/Users/kevin/.lmstudio/local-ai-lab', reason='Preserve installed runtime, preview and launchers.')]
    exports = []
    for name in ['cpu-remediation-package.json', 'cpu-remediation-hybrid-package.json', 'game-source-v2-hybrid-package.json']:
        p = V / name
        d = json.loads(p.read_text())
        selected = d.get('selected_adapter') or d.get('selected_checkpoint', {}).get('selected_adapter')
        exports.append(dict(receipt=str(p), destination=d.get('destination', d.get('model_directory')), selected_adapter=selected,
            adapter_sha256=d.get('adapter_sha256', d.get('selected_checkpoint', {}).get('adapter_sha256')),
            reconstruction_recipe_present='hybrid' in name, reconstruction_byte_identity_verified=False,
            classification='KEEP_PENDING_EXACT_RECONSTRUCTION_AUDIT', reason='Unique trained export is not a public re-download or proven byte-identical duplicate.'))
        dependencies.append(p)
        if selected:
            for f in ['adapter_config.json', 'adapters.safetensors']:
                q = Path(selected) / f
                assert q.is_file(), q
                dependencies.append(q)
    dependencies += [ROOT / 'scripts/package_hybrid_adapter.py', ROOT / 'scripts/configure_game_source_v2_off.py']
    candidates = []
    for key, qualification in [
        ('lmstudio-community/Qwen3-Coder-Next-MLX-4bit', 'Public candidate, not a base in any recorded game training job; preserve pinned revision03cba26036330b7553d252c1f3fb899f16cc5ea5 and historical results. Advertising owner must clear any separate dependency.'),
        ('unsloth/Qwen3-Coder-Next-GGUF', 'Public quantized comparison model, not a recorded game training base; save exact repo/revision/hash before removal and confirm no other user workflow needs it.'),
        ('mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit', 'No recorded game optimizer dependency; advertising owner must check earliest advertising pilot before clearing it.')]:
        row = next(x for x in inventory if x['path'] == str(home/key))
        candidates.append(dict(path=str(home/key), logical_weight_bytes=row['logical_weight_bytes'], classification='CONDITIONAL_PUBLIC_DOWNLOAD_CANDIDATE', qualification=qualification))
    aliases = [x for x in inventory if x['directory_symlink'] and 'portable-ailab-' in x['path']]
    old_aliases = [x for x in aliases if '4f5658686590' not in x['path']]
    for x in old_aliases:
        candidates.append(dict(path=x['resolved'], native_alias=x['path'], logical_weight_bytes=x['logical_weight_bytes'],
            classification='CONDITIONAL_RETIRED_RESTORE_TEST_WEIGHT_PAYLOAD_ONLY',
            qualification='Keep every workbench/runtime/verification/result file. Confirm no active model/definition/preset depends on this alias, retire its old registration, compare weight hashes against retained base/reviewer, and retain migration manifests. Do not delete whole restore package.'))
    wrapper = json.loads((V / 'native-Deck-current-status-v1-current.json').read_text())
    required_weights = [p for p in wrapper['dependencies_sha256'] if Path(p).suffix in ['.safetensors', '.gguf', '.npz']]
    save(out / 'native-model-weight-inventory.json', inventory)
    proof = dict(status='terminal_readonly_game_model_retention_audit_no_deletions', directory=str(out),
        source_human_request_verified=dict(thread_id='01a159fa-426f-73f3-bbfa-026d3fd27e99', user_message_id='01a15f00-27eb-7bc1-9663-f7181902d4c3'),
        scope='Native LM Studio inventory, actual game training bases/checkpoints, current portable binding and preservation constraints. Advertising-owned checkpoints/cache audit remains with originating chat.',
        keep=keep, trained_exports_hold=exports, conditional_candidates=candidates, game_training_receipts=training,
        game_checkpoint_files=len(adapters), game_checkpoint_logical_bytes=sum(x['bytes'] for x in adapter_inventory),
        current_published_game_status_required_weight_files=required_weights,
        active_model_identifier=catalog[0]['identifier'] if len(catalog)==1 else None, native_catalog=catalog,
        current_daily_identifier=daily['identifier'], current_daily_model_key=daily['model_key'],
        old_aliases=old_aliases, no_game_GPU_worker_started=True, deletions=0, moves=0, model_load_changes=0,
        sizes_are_logical_not_guaranteed_reclaimed_space=True,
        storage_note='Do not add symlink aliases to their targets or assume APFS clones/hardlinks reclaim their logical size. Removing only an alias saves negligible space; never remove current4f565target.',
        hybrid_recipe='Preserve selected adapter/config and exact base revision; package_hybrid_adapter.py fuses adapted modules only at dequantized precision, retaining other quantized modules. Reproduce in an isolated job copy/new destination; original script writes frozen job/global reports and requires unloaded native models. For game-source-v2 also reproduce configure_game_source_v2_off.py metadata override. No regeneration or unloading performed by this audit.',
        source_sha256={str(p):sha(p) for p in dependencies})
    save(out / 'audit.json', proof)
    save(V / 'game-model-space-audit-v1-current.json', proof)
    text = ('Game model space audit — read-only, no deletions\n\n'
        'Keep the native27B/6bit base,30B Coder/4bit base,current4f565portable daily target and registrations,all game training artifacts and all BIWN work. Three trained game exports remain on hold pending exact reconstruction audit; their retained adapters alone are not proof that deleting the exports preserves identical ready-to-load artifacts.\n\n'
        'Conditional public-download candidates\n' + '\n'.join(f"{x['path']} — {x['logical_weight_bytes']/1024**3:.2f}GiB logical: {x['qualification']}" for x in candidates if x['classification']=='CONDITIONAL_PUBLIC_DOWNLOAD_CANDIDATE') +
        '\n\nOlder portable aliases1ac245406ec5and4e102874883bpoint to separate restore-test targets. Retiring only their model payloads may save space after alias,definition,content-hash and current-dependency checks;keep every workbench/runtime/verification/result. Current4f565target is active and protected.\n\n'
        f"Game adapter checkpoints total{proof['game_checkpoint_logical_bytes']/1024**3:.2f}GiB across{len(adapters)}files;preserve all. Actual game training receipts use only the two protected base revisions. Current published game proof also directly hashes one copied-training adapter;deleting it breaks status/MCP verification.\n\n"
        'Native catalog was observed with the configured4f565daily model idle,queued0,32Kcontext/parallel1. This is a point-in-time observation;recheck before any approved cleanup. No weights loaded,unloaded,deleted or moved. Logical sizes do not establish physical reclaim for aliases/APFS clones/hardlinks.\n\n'
        'Exact details and paths: '+str(out/'audit.json')+'\n')
    (out / 'Game model retention and space candidates.txt').write_text(text)
    print(proof['status'], 'game checkpoints', len(adapters), 'public candidates logical GiB', round(sum(x['logical_weight_bytes'] for x in candidates if x['classification']=='CONDITIONAL_PUBLIC_DOWNLOAD_CANDIDATE')/1024**3,2), flush=True)


if __name__ == '__main__':
    main()

"""Qualify copied evidence corruption and explicit origin/escape rejection."""
import asyncio
import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def save(p, x):
    Path(p).write_text(json.dumps(x, indent=2) + '\n')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


async def main():
    state = json.loads((ROOT / 'verification/cold-runtime-move-active.json').read_text())
    assert state['status'] == 'terminal_relocated_MCP_calls_pass_pending_audit'
    base = Path(state['directory'])
    out = base / ('MCP-boundaries-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    runtime = Path(state['package']) / 'runtime'
    workbench = Path(state['package']) / 'workbench'
    entry = json.loads((Path(state['package']) / 'lmstudio-home' / 'mcp.json').read_text())['mcpServers']['local-ai-lab']
    env = {**os.environ, **entry['env']}
    pub = json.loads((workbench / 'verification/current-biwn-latest-publication-current.json').read_text())
    name, expected = next((n, h) for n, h in pub['dependencies_sha256'].items() if n.endswith('.py'))
    copied = workbench / Path(name).relative_to(ROOT)
    before = copied.read_bytes()
    assert sha(copied) == expected
    responses = []
    with (out / 'server-stderr.log').open('w') as errors:
        async with stdio_client(StdioServerParameters(command=entry['command'], args=entry['args'], env=env, cwd=str(runtime)), errlog=errors) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=180)) as client:
                await client.initialize()
                original = await client.call_tool('project_evidence', {'topic': 'status'})
                assert not original.isError
                responses.append(original.model_dump(mode='json'))
                try:
                    copied.write_bytes(before + b'\n# deliberate isolated integrity defect\n')
                    result = await client.call_tool('project_evidence', {'topic': 'status'})
                    responses.append(result.model_dump(mode='json'))
                    assert result.isError and any('Current status evidence changed' in getattr(block, 'text', '') for block in result.content)
                finally:
                    copied.write_bytes(before)
                restored = await client.call_tool('project_evidence', {'topic': 'status'})
                responses.append(restored.model_dump(mode='json'))
                assert not restored.isError and sha(copied) == expected
    save(out / 'corruption-tool-responses.json', responses)
    # Execute as a copied local module so its imports get the same explicit
    # Path/JSON views as the actual tools. Raw open intentionally bypasses Path.
    probe = runtime / ('boundary-probe-' + out.name + '.py')
    probe.write_text('''import json, pathlib, builtins
from pathlib import Path
original = ''' + repr(str(ROOT)) + '''
old_runtime = ''' + repr(str(Path.home() / '.lmstudio/local-ai-lab')) + '''
destination = ''' + repr(str(workbench)) + '''
mapped = Path(original + '/config.json')
assert str(mapped) == destination + '/config.json'
assert json.loads('{"''' + str(ROOT) + '''/key":"''' + str(ROOT) + '''/value"}') == {destination+'/key':destination+'/value'}
rows=[]
for label, name in [('old_workbench',original+'/config.json'),('old_runtime',old_runtime+'/config.json')]:
 try: builtins.open(name,'rb')
 except PermissionError as error: rows.append({'defect':label,'rejected':True,'error':str(error)})
 else: raise AssertionError('Origin read escaped relocation guard')
link=Path(destination)/'deliberate-origin-escape'
assert not link.exists()
link.symlink_to(original+'/config.json')
try:
 try: link.read_bytes()
 except PermissionError as error: rows.append({'defect':'symlink_to_origin','rejected':True,'error':str(error)})
 else: raise AssertionError('Symlink origin escape accepted')
finally: link.unlink()
print(json.dumps({'negative_controls':rows,'absolute_Path_and_JSON_keys_values_rebased':True}))
''')
    p = subprocess.run([entry['command'], str(probe)], env=env, cwd=runtime, capture_output=True, text=True, timeout=20)
    (out / 'boundary-probe.log').write_text(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr
    decoded = json.loads(p.stdout)
    save(out / 'boundary-probe.json', decoded)
    controls = decoded['negative_controls'] + [dict(defect='copied_hash_bound_evidence_corruption', rejected=True, restored_exact_bytes=True)]
    audits = []
    for path in Path(state['package']).glob('path-audit-*.json'):
        value = json.loads(path.read_text())
        if value['allowed_restore_root'] != state['package']: continue
        audits.append(dict(path=str(path), sha256=sha(path), pid=value['pid'], denied=len(value['denied']), restored_path_count=len(value['restored_paths']), counters=value['counters']))
    assert sum(row['denied'] for row in audits) == 3
    assert len(audits) >= 5, 'Expected parent and native fixture child audit receipts'
    save(out / 'path-audit-index.json', audits)
    inputs = [Path(__file__), probe, runtime / 'portable_runtime_paths_v3.py', runtime / 'sitecustomize.py', runtime / 'portable_chat_tools_v3.py', out / 'corruption-tool-responses.json', out / 'boundary-probe.json', out / 'path-audit-index.json']
    result = dict(status='terminal_cold_moved_runtime_boundaries_pass', directory=str(out), runtime=str(runtime), workbench=str(workbench), negative_controls=controls, original_tree_fallback=False, successful_tool_server_origin_accesses=0, historical_evidence_bytes_rewritten=False, scope=__doc__ + ' Same-host different-root only; audit hook is a test guard, not a security sandbox. Seven successful tool kinds out of eighteen registered; no model inference, all-tool behavior, native Chat UI, full workbench, off-machine or future hardware proof.', source_sha256={str(p): sha(p) for p in inputs})
    save(out / 'protocol.json', result)
    save(ROOT / 'verification/cold-runtime-boundaries-current.json', result)
    print(json.dumps({k: result[k] for k in ['status', 'original_tree_fallback', 'successful_tool_server_origin_accesses']}))


if __name__ == '__main__':
    asyncio.run(main())

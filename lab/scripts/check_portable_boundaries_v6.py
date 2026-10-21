"""Moved-package boundary and exact-certificate rejection checks.
The guard is a diagnostic mechanism, not a general security sandbox.
"""
import builtins, ctypes, hashlib, json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
PACKAGE=Path(__file__).resolve().parents[2]
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    out=PACKAGE/'test-results'/('boundaries-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True)
    origin=json.loads((PACKAGE/'origin.json').read_text());old=origin['original_workbench'];host=str(Path(origin['original_runtime']).parent)
    controls=[]
    def denied(name,operation):
        try:operation()
        except PermissionError as error:controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise AssertionError('Origin boundary did not reject '+name)
    denied('raw_origin_workbench_open',lambda:builtins.open(old+'/config.json','rb'))
    denied('raw_host_LM_Studio_open',lambda:builtins.open(host+'/mcp.json','rb'))
    denied('origin_dynamic_library_load',lambda:ctypes.CDLL(old+'/tools/libbiwn-movement-device.dylib'))
    alias=out/'origin-alias.json';alias.symlink_to(old+'/config.json')
    try:denied('symlink_origin_open',lambda:builtins.open(str(alias),'rb'))
    finally:alias.unlink()
    # An actual copied-module import sees rebased paths; third-party imports do
    # not get that view. Historical source bytes and external API JSON stay raw.
    code='import json\nresult=json.loads(payload)'
    payload=json.dumps({'path':old+'/config.json',old+'/key':'unchanged-value'})
    local={'__file__':str(PACKAGE/'workbench/probe.py'),'payload':payload};exec(code,local)
    thirdparty={'__file__':str(PACKAGE/'runtime/.venv/lib/python3.12/site-packages/probe.py'),'payload':payload};exec(code,thirdparty)
    assert local['result']['path']==str(PACKAGE/'workbench/config.json')
    assert str(PACKAGE/'workbench/key')in local['result']
    assert thirdparty['result']['path']==old+'/config.json' and old+'/key'in thirdparty['result']
    sys.path.insert(0,str(PACKAGE/'workbench'));import native_ccr_workbench
    proof,_,_,_=native_ccr_workbench.checked();source=Path(proof['source']);assert source.is_relative_to(PACKAGE)
    before=source.read_bytes();digest=sha(source);(out/'certificate-source-before.c').write_bytes(before)
    try:
        source.write_bytes(before+b'\n/* deliberate relocation certificate negative */\n')
        try:native_ccr_workbench.checked()
        except ValueError as error:controls.append(dict(name='copied_C_certificate_tamper',rejected=True,error=str(error)))
        else:raise AssertionError('Changed copied source incorrectly reused receipt')
    finally:source.write_bytes(before)
    assert sha(source)==digest;native_ccr_workbench.checked()
    training_command=[sys.executable,str(PACKAGE/'workbench/scripts/mlx_lora_reasoning_off.py'),'--help']
    result=subprocess.run(training_command,capture_output=True,text=True,timeout=60);(out/'training-CLI-help.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and '--adapter-path'in result.stdout and '--train'in result.stdout
    save(out/'training-command.json',training_command)
    state=dict(status='terminal_moved_boundaries_certificate_negative_and_training_CLI_help_pass',pid=os.getpid(),directory=str(out),package=str(PACKAGE),python=sys.executable,controls=controls,local_import_rebases_paths=True,third_party_JSON_unmodified=True,copied_certificate_restored_and_rechecked=True,training_CLI_help_pass=True,actual_training_updates=0,new_predictions=0,scope=__doc__)
    save(out/'protocol.json',state);save(PACKAGE/'portable-boundaries-current.json',state);print(json.dumps(state))
if __name__=='__main__':main()

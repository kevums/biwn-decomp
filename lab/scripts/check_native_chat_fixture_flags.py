"""Register/CCR matrix plus branch, legacy fallback and rejection contracts."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));from native_cpu_fixture import request_for,verify_native_subset
from native_cpu_fixture_worker import run
from check_biwn_scheduler import Native
from cpu_fixture import verify_fixture
out=ROOT/'verification/native-chat-fixture-flags'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);n=Native();cases=0;errors=[]
try:
 for register in range(8):
  for immediate in range(256):
   for X in [0,16]:
    code=(0x7000|(register<<9)|immediate).to_bytes(2,'big').hex()+'4e75';initial={f'D{i}':hex(0x12345678+i)for i in range(8)};request=request_for('hex:'+code,initial,15|X);result=run(request,n);signed=immediate if immediate<128 else immediate-256;expected=(8 if signed<0 else 4 if signed==0 else 0)|X
    assert result['status']=='bounded_fixture_completed'and result['stack_return_checked'];assert result['final_CCR']==expected and result['signed_final_registers'][f'D{register}']==signed,(register,immediate,X,result)
    for i in range(8):
     if i!=register:assert result['final_registers'][f'D{i}']==f'0x{0x12345678+i:08x}'
    cases+=1
 branch=[]
 for voice in [0,1,2,3,4,0xffff]:
  r=run(request_for('hex:53400c40000163047400600274014e75',{'D0':hex(voice)},31),n);assert int(r['final_registers']['D2'],16)==int(voice in [1,2]);branch.append(dict(voice=voice,branch_taken_D2=r['final_registers']['D2']))
finally:n.close()
# Actual parent/child path and backward-compatible non-native fixture path.
child=verify_fixture('hex:76f94e75',{},16);assert child['condition_codes']==dict(X=1,N=1,Z=0,V=0,C=0)and child['signed_final_registers']['D3']==-7
legacy=verify_fixture('hex:204f20104e75',{});assert legacy['status']=='bounded_fixture_completed'and not legacy['condition_codes_available']
loop=verify_fixture('hex:60fe4e75',{});assert loop['status']=='fixture_rejected_or_incomplete'and not loop['condition_codes_available']and loop['instructions_executed']==256
rejected=[]
for args in [('hex:70014e75',{},32),('hex:70014e75',{},True),('hex:70014e75',{'A7':'0x10800'},0),('hex:70014e75',{'D0':'-1'},0),('hex:204f20104e75',{},16),('hex:70',{},0)]:
 try:verify_fixture(*args)
 except ValueError as e:rejected.append(str(e))
 else:raise AssertionError(('guard accepted',args))
report=dict(status='native_chat_fixture_flags_verified',directory=str(out),MOVEQ_cases=cases,all_D_registers_all_immediates_both_X=True,initial_NZVC_set=True,branch_cases=branch,child_probe=child,legacy_flags_unavailable=True,loop_incomplete_flags_unavailable=True,rejection_guards=rejected,core_sha256=json.loads((ROOT/'native-fixture-backend.json').read_text())['core_sha256'],scope='Private CPU fixture tool; not generated C, complete game or hardware.',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [ROOT/'native_cpu_fixture.py',ROOT/'cpu_fixture.py',ROOT/'scripts/native_cpu_fixture_worker.py']});(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/native-chat-fixture-flags-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],cases)

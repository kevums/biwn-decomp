"""Verify the explicitly corrected local function and publish its pending integration phase."""
import copy,hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'navigation-hybrid-component-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if p.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);p=dest
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 provenance=read(V/'navigation-hybrid-source-provenance-current.json');prototype=read(V/'native-navigation-hybrid-current.json');final=read(V/'native-navigation-hybrid-final-current.json')
 for name,obj in [('navigation-hybrid-source-provenance-current.json',provenance),('native-navigation-hybrid-current.json',prototype),('native-navigation-hybrid-final-current.json',final)]:
  bind(V/name)
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 for gate in [prototype,final]:
  assert gate['cases']==6144 and gate['per_root_cases']['0x13f12']==1536 and gate['binary_bytes']==1588 and gate['max_private_depth']==180 and len(gate['original_sites'])==209
  assert subprocess.run(['ps','-p',str(gate['pid']),'-o','command='],capture_output=True).returncode!=0
 assert final['code_address']==0x165ce0
 raw=Path(provenance['raw_candidate']);hybrid=Path(provenance['hybrid_source']);assert sha(raw)==provenance['raw_candidate_sha256']and sha(hybrid)==provenance['hybrid_source_sha256']
 text=raw.read_text();text=text.replace('uint32_t d1 = 7;','r[1] = 7;');mask='r[16] = (r[16] & 0xffe0u) | 0x04u;';assert text.count(mask)==4;text=text.replace(mask,'r[16] = (r[16] & 0xfff0u) | 0x04u;',1);at=text.rindex(mask);text=text[:at]+text[at:].replace(mask,'r[16] = r[16] & 0xffe0u;',1);actual=hybrid.read_text();assert actual[actual.index('#include'):]==text
 for p in [raw,hybrid,Path(provenance['wrapper'])]:bind(p)
 report=out/'review.txt';report.write_text('''LOCAL NAVIGATION HYBRID — COMPONENT VERIFIED, NOT ON CURRENT DISC

The concise local27B draft is complete raw C but unchanged source is rejected:
its unusedD1variable fails strict compilation. It also omits originalD1writes,
clears incomingX at an early return and leavesZset on successfulD0=1returns.
The coordinator made exactly3source substitutions:writeD1,preserve earlyX,
clearZon successful return. Raw local output is unchanged and separately retained.
The new hybrid source has an attribution comment. No goldC was supplied to the
model; deterministic originalCPU/orderedaccess checks decide acceptance.

Prototype andfinal-address groups each pass6144cases(1536perroot),all209original
instruction sites. The model-derived hybrid function is13F12; the other3roots
remain coordinator code. FullreturnedCPU/SR/banks/public2MBRAM/ordereddataaccess
match original execution. No prescribed helpers; valid stored jump-table targets
only. Privateframes/installation/returnPCs excluded. Interrupt/concurrency/fault/
modifiedtargets/timing behavior remains unproved. Maxnativeprivate180bytes.

Group1588bytes at165CE0,160larger than current1428byte coordinatorgroup. Replacing
that group would make30036resident bytes inside existing30080reservation,free44.
No heap/staging growth needed if those bytes/sizes remain unchanged. It has NOT
been integrated: fresh observerqualification/fullpayloadstartup/newCDIpatchscope
and freshgameplay/control review remain required. Latest reviewed disc29876
still uses coordinator navigation. This is explicitly hybrid source,not accepted
unchanged local output or a training/weight-quality improvement. No independent
same-weight model review claim. Total newlocalpredictions thiscontinuation3.
''');bind(report);bind(Path(__file__))
 review=dict(status='terminal_hybrid_local13F12_prototype_and_final_component_pass_not_integrated',directory=str(out),report=str(report),prototype_group_cases=6144,final_group_cases=6144,hybrid_root_cases_each_matrix=1536,group_original_instruction_sites=209,group_bytes=1588,current_group_bytes=1428,max_private_depth=180,coordinator_corrections=provenance['coordinator_corrections'],new_predictions=0,new_training=False,unchanged_local_output_accepted=False,hybrid_source_component_verified=True,disc_integrated=False,projected_resident_bytes=30036,projected_reserved_free_bytes=44,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',review);save(V/'navigation-hybrid-component-reviewed-current.json',review)
 pp=V/'current-biwn-latest-publication-current.json';previous=read(pp);assert previous['facts']['experimental_build']['resident_bytes']==29876
 pubdir=V/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');pubdir.mkdir(parents=True);save(pubdir/'previous-publication.json',previous);facts=copy.deepcopy(previous['facts']);facts['recorded_at']=datetime.now(timezone.utc).isoformat();next=facts['next_component_development'];next.update(status=review['status'],final_address_verified=True,final_group_cases=6144,report=str(report),projected_resident_bytes=30036,proof=str(out/'protocol.json'));next['scope']='Prototype+final original-execution component comparison only. Fresh compiled observer/fullpayloadstartup/disc/live gates still required. No currentdisc/default/weightpromotion.'
 facts['checked_current_summary']=facts['checked_current_summary'].replace('a3correctionhybrid passesprototypeonly','a3correctionhybrid passesprototype+finalcomponentonly');facts['local_authorship']['navigation_trials']['hybrid_final_group_cases']=6144
 newdeps=dict(previous['dependencies_sha256'])
 for p,h in deps.items():assert p not in newdeps or newdeps[p]==h,p;newdeps[p]=h
 for p in [out/'protocol.json',pubdir/'previous-publication.json']:newdeps[str(p)]=sha(p)
 for p,h in newdeps.items():assert sha(p)==h,p
 result=dict(previous,directory=str(pubdir),recorded_at=facts['recorded_at'],facts=facts,dependencies_sha256=newdeps,scope=previous['scope']+' Hybrid final-address component pass,stillnotintegrated.');save(pubdir/'publication.json',result);save(pp,result)
 print(json.dumps(dict(status=review['status'],group_bytes=1588,projected_resident_bytes=30036,projected_free_bytes=44,published_gameplay_bytes=29876)))
if __name__=='__main__':main()

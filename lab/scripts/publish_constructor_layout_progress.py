"""Publish bounded constructor evidence without promoting a restoration candidate."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';RT=Path.home()/'.lmstudio/local-ai-lab'

def read(name):return json.loads((V/name).read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def compact(name):
 j=read(name);fields=['status','cases','source_loader_yields','source_scheduler_switches','constructor_return_verified','source_scene_descriptor_preserved','scene_descriptor_tag','scene_descriptor_asset','experimental_source_data_patch','experimental_argument_adapter','experimental_guest_code_overlay','saved_selector_ID_matches_acquired_cache_ID_verified','controlled_cache_reselection_and_release_verified','original_image_modified','runtime_default_promoted','scope']
 return {'proof':str(V/name),'proof_sha256':hashlib.sha256((V/name).read_bytes()).hexdigest(),'paired_checkpoints':len(j['phases']),**{k:j[k]for k in fields if k in j}}

def main():
 original=compact('scene-constructor-source-descriptor-scheduler-current.json')
 count=compact('scene-constructor-count13-experiment-current.json')
 request=compact('scene-constructor-request13-experiment-current.json')
 both=compact('scene-constructor-count13-request13-experiment-current.json')
 candidate=compact('scene-constructor-selector13-restoration-experiment-current.json')
 assert all(x['cases']==9 for x in [original,count,request,both,candidate])
 assert not any(x['constructor_return_verified']for x in [original,count,request])
 assert both['constructor_return_verified']and candidate['constructor_return_verified']
 assert candidate['paired_checkpoints']==99 and not candidate['experimental_argument_adapter']
 payload=read('scene-constructor-selector13-payload-current.json');assert len(payload['checks'])==18 and payload['payload_bytes']==106496
 review=read('mode3-constructor-local-review-current.json');assert review['status']=='terminal_local_review_complete'
 review['coordinator_review']={'status':'retained_with_corrections','analyst_correction':'ID16 is descriptor asset1 shiftedleft4,not a constantID or proven handshake. Missingmarker precedes retries under this provider; count-only failure doesnot establish countirrelevance.','reviewer_correction':'Failure after forcingID13 wouldnot by itself exclude an ID/addressing issue; factorial controls are needed. Actual count13/ID13 result establishes a bounded input combination,not intendedformat or universalrepair.','tested_follow_on':'Both single-factor controls retry; combinedinputs and separate guestcode/countoverlay return. SavedID/cacheID and controlled reselect/release agree in codecandidate; eighteen finalRAMpayloads match exact observed C001extent.','native_UI_attempt':'LM Studio computer-use call timedout. API messages retained; nativeChat not verified.'}
 save(V/'mode3-constructor-local-review-current.json',review)
 diagnosis=dict(status='mode3_constructor_retry_and_unpromoted_selector13_candidate_verified',recorded_at=read('scene-constructor-selector13-restoration-experiment-current.json')['recorded_at'],unchanged_descriptor=original,count13_only=count,request13_only=request,count13_request13=both,guest_code_candidate=candidate,exact_disc_payload={'proof':str(V/'scene-constructor-selector13-payload-current.json'),'checks':18,'bytes_per_payload':106496,'confirmed_image_schema':False},local_roles={'proof':str(V/'mode3-constructor-local-review-current.json'),'model':'advertising-scholar','roles':['analyst','reviewer'],'same_model_correlated':True,'transcript':str(Path(review['directory'])/'prompts-and-responses.txt'),'coordinator_review':review['coordinator_review']},original_image_modified=False,default_promoted=False,new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,whole_game_complete=False,remaining=['Recover intended mode3 schema and renderer use','Validate other source descriptors and lifetime branches','Integrate into actual source caller and uninterrupted gameplay','Validate provider phase/BIOS/device behavior beyond controlled fixtures'],scope='Original descriptor1: bounded sourceCPU/C retry equivalence. Explicit experimental source selector*13/count13 overlay: modified-program equivalence and controlled cache/payload proofs only. No original-image equivalence,author-intent,physical hardware or playable restoration claim.')
 save(V/'mode3-constructor-diagnosis-current.json',diagnosis)
 base=read('scene-constructor-scheduler-current.json');generation=read('scene-constructor-CPU-generation-current.json')
 visited=set(a for x in base['results']for a in x['original_visited_addresses']);generated={x['address']for x in generation['instructions_decoded']}
 summary=dict(status=base['status'],proof=str(V/'scene-constructor-scheduler-current.json'),cases=base['cases'],paired_phase_checkpoints=len(base['phases']),source_loader_yields=base['source_loader_yields'],source_scheduler_switches=base['source_scheduler_switches'],completion_switch_values=base['completion_switch_values'],observed_CPU_instruction_addresses=len(visited),constructor_generated_instruction_addresses=len(generated),constructor_observed_instruction_addresses=len(visited&generated),original_CPU_instructions_on_C_path=0,BIOS_adapters=base['BIOS_adapters'],completion_delivery=base['completion_delivery'],coordinator_authored=True,new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,scope=base['scope'],unchanged_descriptor_diagnosis=original,experimental_restoration=candidate,exact_experimental_payload=diagnosis['exact_disc_payload'],diagnosis_proof=str(V/'mode3-constructor-diagnosis-current.json'),default_promoted=False)
 summary={'status':diagnosis['status'],'checked_current_summary':'The unchanged source scene1 descriptor (asset1) repeatedly retries:9cases/153paired checkpoints,constructor return not verified. The older forcedasset0 control returns in9cases/81checkpoints. A separate selector*13/count13 guest-code candidate returns in9cases/99checkpoints,including controlledcache reuse/release, and18finalRAMpayloads match the observed106496byteC001extent. The candidate is unpromoted; intendedformat,rendering,naturalgameplay andwholegame remain unverified.','unchanged_descriptor_diagnosis':original,'experimental_restoration':candidate,'exact_experimental_payload':diagnosis['exact_disc_payload'],'earlier_controlled_asset0':{k:val for k,val in summary.items()if k not in ['unchanged_descriptor_diagnosis','experimental_restoration','exact_experimental_payload','diagnosis_proof']},'diagnosis_proof':str(V/'mode3-constructor-diagnosis-current.json'),'default_promoted':False,'native_Chat_verified':False,'new_training':False,'natural_gameplay_integration_verified':False}
 save(V/'scene-constructor-scheduler-summary-current.json',summary)
 for name,value in [('biwn-constructor-scheduler.json',summary),('biwn-mode3-constructor-diagnosis.json',diagnosis)]:save(ROOT/'corpus/game/project-evidence'/name,value)
 entry='MODE3 CONSTRUCTOR — '+diagnosis['recorded_at']+'\nUnchanged scene1descriptor asset1: originalCPU andC repeatedly retry,9cases/153pairedcheckpoints. Count13-only andrequest13-only controls also retry. Separate selector*13/count13 guest-codecandidate returns in9cases/99checkpoints,includingcontrolledcache reuse/release withoutanotherread;18finalRAMpayloads match exact106496byteC001disc extent. Originalimage/canonicalsource/defaults unchanged. This is experimental modified-program equivalence; intendedschema,rendering,naturalcaller andwholegame remain unverified.\nEvidence: '+str(V/'mode3-constructor-diagnosis-current.json')+'\nLocal analyst/reviewer prompts: '+str(Path(review['directory'])/'prompts-and-responses.txt')+'\nAsk Game Assistant: Use project_evidence with topic constructor_scheduler. What did the original descriptor do, and is the selector13 candidate a verified game fix?\n\n'
 for root in [ROOT,RT]:
  for name in ['START HERE.txt','CURRENT DECOMPILATION.txt']:
   path=root/name
   text=path.read_text()
   while text.startswith('MODE3 CONSTRUCTOR — '):text=text.split('\n\n',1)[1]
   path.write_text(entry+text)
 audit=ROOT/'runs/whole-function-training-who-does-what-current.txt'
 with audit.open('a')as f:f.write(('\n'+entry if entry not in audit.read_text() else '')+'Coordinator: extended scheduler harness,controlled factorialinputs,explicit codeoverlay generator,payloadcomparison andpublication. Two failed cacheassertion attempts were harnessplacement errors: assertion ran before loader completion; corrected controlflow and reran allnine candidatecases. Local27B: analyst14.19s/reviewer11.82s,APIonly,reviewedwithcorrections above. No model wrote the overlay Cbody, no newtraining/defaultpromotion.\n')
 print(diagnosis['status']);print('summary bytes',len(json.dumps(summary)))

if __name__=='__main__':main()

"""Keep current game status aligned with installed source retrieval and reviewed local outputs."""
import copy,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 p=V/'current-biwn-latest-publication-current.json';old=read(p);ad=read(V/'advertising-source-sections-reviewed-current.json');install=read(V/'reference-section-frontend-installed-current.json');index=read(V/'current-model-work-index-v4-current.json');assert old['facts']['experimental_build']['resident_bytes']==30036 and ad['new_predictions']==4 and index['saved_prompt_or_transcript_records']==68
 out=V/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();save(out/'previous-publication.json',old);f=copy.deepcopy(old['facts']);f['recorded_at']=datetime.now(timezone.utc).isoformat();f['prompts_and_responses']=index['report']
 f['advertising_workflow_progress']=dict(status=ad['status'],report=ad['report'],lesson=ad['friendly_lesson'],lesson_words=199,lesson_authorship='Coordinator edited after original-source/rubric review; raw local drafts and revised draft retained.',actual_local_predictions=4,role_seconds=ad['role_seconds'],roles=['baseResearcher','baseEducator','trainedSourceReviewer','baseEducator informedrevision'],trained_Reviewer_false_pass=True,quality_gain_demonstrated=False,new_training=False,source_is_heldout=False,source_scope='Schreiner2026Study2A/exposedreference; PDF9design/timing and20measurement accessed through newgeneral heading/study/page-based retrieval. One reviewed undergraduatelesson,not broad domainqualityproof.',daily_base_restored=True,native_Chat_verified=False)
 f['frontend_progress']=dict(status=install['status'],entrypoint=install['entrypoint'],tool_count=18,actual_configured_MCP_verified=True,general_section_retrieval=True,tested_positive_advertising_queries=4,tested_pdf_sources=1,out_of_range_page_rejected=True,page_ranges_supported=True,game_search_and_status_preserved=True,configuration_backup=install['configuration_backup'],native_Chat_display_verified=False,report=install['directory'])
 f['migration_progress'].update(live_frontend_entrypoint_version='v10',cold_package_frontend_entrypoint_version='v7',new_source_section_frontend_copied_to_cold_package=False)
 f['checked_current_summary']+=' Advertisingmethods/measurementsectionretrievalv10 installed;4localrolepredictions exposedbaseline/rubricerrors andtrainedReviewerfalsepass. Coordinatorcorrected199wordlesson saved;not broadqualitygain.68savedprompt/transcriptrecords. NativeChat/fullportableSDK/CLI/toolchain/training/futurehardware remainopen.'
 deps=dict(old['dependencies_sha256'])
 def bind(path,h=None):
  path=Path(path).resolve();actual=sha(path);assert h is None or actual==h,str(path)
  if(path.parent==V and path.name.endswith(('-current.json','-active.json')))or path==ROOT/'reports/Advertising Source Lesson.txt'or not path.is_relative_to(ROOT):
   target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name[-160:]);shutil.copy2(path,target);path=target
  assert str(path)not in deps or deps[str(path)]==actual,str(path);deps[str(path)]=actual
 for path,h in ad['dependencies_sha256'].items():bind(path,h)
 for path,h in install['source_sha256'].items():bind(path,h)
 for name in ['advertising-source-sections-reviewed-current.json','reference-section-frontend-installed-current.json','current-model-work-index-v4-current.json']:bind(V/name)
 for path in [Path(__file__),out/'previous-publication.json',Path(index['report']),Path(index['source_list_snapshot']),Path(index['directory'])/'manifest.json',Path.home()/'.lmstudio/mcp.json']:bind(path)
 for path,h in deps.items():assert sha(path)==h,path
 result=dict(old,directory=str(out),recorded_at=f['recorded_at'],facts=f,dependencies_sha256=deps,scope=old['scope']+' Installedsectionretrieval andactualfourroleoutputs/sourcecheckedcoordinatorlesson added;fullscopeactive.');save(out/'publication.json',result);save(p,result);print(json.dumps(dict(resident_bytes=30036,new_advertising_predictions=4,saved_records=68,trained_Reviewer_false_pass=True,bound_files=len(deps))))
if __name__=='__main__':main()

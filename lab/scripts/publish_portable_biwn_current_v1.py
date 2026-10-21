"""Publish the current moved offline game snapshot with explicit unfinished gates."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 build=read(V/'portable-biwn-current-v1-current.json');p=Path(build['package']);out=Path(build['directory']);runtime=read(V/'portable-biwn-runtime-v1-current.json');integrity=read(V/'portable-biwn-model-integrity-v1-current.json');profile=read(V/'portable-biwn-profile-v1-current.json');transcripts=read(V/'portable-biwn-transcripts-v2-current.json');differences=read(V/'native-debug-frame-differences-v1-current.json')
 for proof in [build,runtime,integrity,profile,differences]:
  for path,digest in proof.get('source_sha256',{}).items():assert sha(path)==digest,path
 assert runtime['exact_rebuilt_native_module_bytes']==40062 and runtime['actual_MCP_tools']==18 and runtime['origin_audit_denials']==0
 assert integrity['dependency_files_verified']==10009 and integrity['weight_shards_verified']==10 and transcripts['saved_records']==171
 assert profile['live_MCP_unchanged']and not profile['native_Chat_transport_migrated']
 # Verify this compiler discovers its tools/libraries under the moved prefix.
 tool=p/'workbench/tools/m68k-elf';cc=tool/'bin/m68k-elf-gcc';search=subprocess.check_output([str(cc),'-print-search-dirs'],text=True);(out/'compiler-search-dirs.txt').write_text(search)
 for line in search.splitlines():
  for value in line.split(':',1)[1].lstrip(' =').split(':'):
   if value:assert Path(value).resolve().is_relative_to(p),value
 links=[]
 for name in ['bin/m68k-elf-gcc','libexec/gcc/m68k-elf/15.2.0/cc1','libexec/gcc/m68k-elf/15.2.0/lto1','bin/m68k-elf-as','bin/m68k-elf-ld']:
  binary=tool/name;result=subprocess.check_output(['otool','-L',str(binary)],text=True);dependencies=[line.strip().split(' (',1)[0]for line in result.splitlines()[1:]];assert all(x.startswith(('/usr/lib/','/System/Library/'))for x in dependencies),dependencies;links.append(dict(relative=str(binary.relative_to(p)),sha256=sha(binary),system_libraries=dependencies))
 save(out/'compiler-runtime-dependencies.json',links)
 for title,action in [('status','2'),('exit','0')]:
  result=subprocess.run(['zsh',str(p/'Open BIWN Lab.command')],input=action+'\n',capture_output=True,text=True,cwd='/',timeout=30);(out/('menu-'+title+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
  if action=='2':assert '24,965/24,964'in result.stdout and '35budgets'in result.stdout
 # The snapshot is a game workflow. Historical extra resources remain archived;
 # native Chat transport and live model tests are deliberately not certified.
 readme=p/'CURRENT SETUP READ ME.txt';readme.write_text(readme.read_text()+'\nOFFLINE MOVED SNAPSHOT CHECKS\nActualMCPv22/18tools and checkedcurrentfacts pass. Copiednative source rebuilds the exact40,062byte module. FourtargetCPU/15budget smoke cases and preview artifact hashes pass.10,009SDKfiles,39modelresources/10weightshards(46.8GB)match their manifests.171savedprompt/transcriptrecords export from a frozen reviewed source list;new unrelated live jobs are not added to this copy. Compiler search paths are under this moved folder;sampled compiler executables depend only onmacOSsystemlibraries. XcodeCommandLineTools are needed for hostCcompilation tests.\n\nNativeChatplugin:the exact currently installedsource is archived underworkbench/native-chat-installed-reference. Its privateworkspace/socket transport is not yet migrated or installed here. The copied terminal Reader/Author/Repair launchers are separate. New moved-package inference and training remain untested while another task owns the sharedmodel lock. Do not treat offlinehash/build checks as model-output quality or futurehardware performance.\n')
 report=ROOT/'reports/Current BIWN Portable Snapshot Review.txt'
 summary='Current game snapshot moved and offline-verified: MCPv22/18tools,currentfacts,exact40062byte native rebuild,4targetCPU/15budget smoke cases,preview artifact hashes,10009SDKfiles and10modelweightshards pass.171savedprompt/transcriptrecords export. New model inference/training and nativeChattransport/rendering remain unverified;the installed playablepreview and liveMCP stay unchanged.'
 report.write_text('CURRENT BIWN PORTABLE SNAPSHOT\n\n'+summary+'\n\nFolder: '+str(p)+'\nOpen: '+str(p/'Open BIWN Lab.command')+'\nAfter moving: '+str(p/'Restore BIWN Setup.command')+'\n\nThe current experimental disc and saved source/model evidence are retained alongside the separately reviewed checkpoint preview. This is not a whole-game rebuild or verified256GBhardware configuration. Default32Kcontext/oneworker;local roles run sequentially. Future256GBcapacity candidates are unmeasured. The previous package is preserved. No new prediction,optimizer update,live model switch or profile installation occurred in this refresh.\n\nSaved-frame analysis:all62newcandidate/controlvideo differences occur at the same trialoffsets as the previous clear candidate. Intervals:56,59,61..104,201..214,225..226. Sampledplayerposition,equipment andother listedpublicfields match;movieflagandheldbuttonstate differ briefly.36video differences have a matchingcontrolhashwithin8frames;26do not. The extra candidate tailframe401is retained. This narrows evidence but does not prove fidelity.\n\nRemaining:adaptnativeChatprivateworkspace/socket transport,verifyactualChatdisplay andnewpackageinference/training;improvebroaderlocalcodingquality;resolvegameplaydifferences andcontinueoriginalsource/wholegamebuild.\n')
 facts=dict(status='terminal_current_biwn_moved_offline_snapshot_verified_live_workflows_pending',directory=str(out),package=str(p),launcher=str(p/'Open BIWN Lab.command'),restore=str(p/'Restore BIWN Setup.command'),report=str(report),frontend='v22',tools=18,SDK_files=10009,model_resource_files=39,weight_shards=10,model_bytes=integrity['model_bytes'],saved_prompt_transcript_records=171,exact_native_module_bytes=40062,target_CPU_smoke_cases=4,target_budget_smoke_cases=15,preview_artifacts_validated=True,new_inference_tested=False,new_training_tested=False,native_Chat_transport_migrated=False,native_Chat_rendering_verified=False,future256GBtested=False,live_MCP_unchanged=True,installed_preview_changed=False,whole_goal_complete=False,new_predictions=0,new_training=False,scope=summary)
 save(out/'facts.json',facts);names=['portable-biwn-current-v1-current.json','portable-biwn-runtime-v1-current.json','portable-biwn-model-integrity-v1-current.json','portable-biwn-profile-v1-current.json','portable-biwn-transcripts-v2-current.json','native-debug-frame-differences-v1-current.json']
 for name in names:shutil.copy2(V/name,out/('reviewed-'+name))
 dependencies=[Path(__file__),out/'facts.json',report,out/'compiler-search-dirs.txt',out/'compiler-runtime-dependencies.json',out/'menu-status.log',out/'menu-exit.log',*[out/('reviewed-'+name)for name in names]]
 pub=dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=0,new_training=False,whole_goal_complete=False,dependencies_sha256={str(path):sha(path)for path in dependencies});pubpath=V/'portable-biwn-current-reviewed-v1-current.json';save(pubpath,pub)
 # Add a new immutable packet instead of rewriting previous source evidence.
 wrapperpath=V/'native-Deck-current-status-v1-current.json';wrapper=read(wrapperpath);packet=read(wrapper['packet']);save(out/'before-status-wrapper.json',wrapper);save(out/'before-status-packet.json',packet)
 packet['game_portable_progress']=facts;packet['current_frame_difference_analysis']={key:differences[key]for key in ['report','previous_clear_difference_offsets_equal_new_debug','current_video_difference_intervals','current_semantic_difference_intervals','current_video_differences_with_nearby_control_hash','current_video_differences_without_nearby_hash','fidelity_verified']};packet['recorded_at']=datetime.now(timezone.utc).isoformat();packet['checked_current_summary']+=' Moved current game snapshot offlinechecks pass;new package inference/training and nativeChattransport remain pending.';packet['checked_answer']=packet['checked_current_summary'];newpacket=out/'current-status-packet.json';save(newpacket,packet);wrapper['packet']=str(newpacket);wrapper['dependencies_sha256'].update({str(path):sha(path)for path in [newpacket,pubpath,*dependencies]});save(wrapperpath,wrapper)
 # Keep this package's operational status view current without rewriting any
 # frozen game/model proof. Only the new packet and publication files are added.
 for path in [wrapperpath,newpacket,pubpath,*dependencies]:
  dest=p/'workbench'/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);assert sha(dest)==sha(path)
 shortcut=Path.home()/'Desktop/BIWN Portable Lab'
 if not(shortcut.exists()or shortcut.is_symlink()):shortcut.symlink_to(p,target_is_directory=True)
 else:assert shortcut.is_symlink()and shortcut.resolve()==p,'Preserve an existing unrelated Desktop item'
 print(summary);print(p)
if __name__=='__main__':main()

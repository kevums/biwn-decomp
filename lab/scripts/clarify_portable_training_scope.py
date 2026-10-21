"""Clarify that the unchanged game build predates the new migration-test adapter."""
import copy,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pointer=V/'current-biwn-latest-publication-current.json';prior=json.loads(pointer.read_text());package=Path(prior['facts']['migration_progress']['package']);out=V/'portable-sdk-scope-clarification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'previous-publication.json',prior)
 result=copy.deepcopy(prior);summary=result['facts']['checked_current_summary'];old='No newweights or unchangedlocaloutputadoption.';assert old in summary
 result['facts']['checked_current_summary']=summary.replace(old,'No unchangedlocaloutputadoption inthisgamebuild. A subsequentportable-pipelinetestcompletedoneunpromotedtrainingupdate;dailyweightsunchanged.')
 result.update(directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat());result['facts']['recorded_at']=result['recorded_at'];result['scope']+=' Clarifiedoldgamebuildno-newweightswordingafterthenewunpromotedmigrationtrainingupdate.'
 result['dependencies_sha256'].update({str(p):sha(p)for p in [Path(__file__),out/'previous-publication.json']});save(out/'publication.json',result);save(pointer,result)
 for source in [Path(__file__),out/'previous-publication.json',out/'publication.json']:
  target=package/'workbench'/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copy2(source,target)
 target=package/'workbench/verification/current-biwn-latest-publication-current.json';backup=package/'backups'/('scope-'+out.name+'.json');shutil.copy2(target,backup);shutil.copy2(pointer,target)
 save(out/'protocol.json',dict(status='terminal_scope_wording_clarified_pending_current_MCP_read',directory=str(out),package=str(package)));print(out)
if __name__=='__main__':main()

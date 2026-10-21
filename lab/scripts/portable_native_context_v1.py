"""Fixed game-only native Chat context lease for the moved package.
The base Python opens the shared machine lock before origin guards are installed.
No inference,training,model loads or model-chosen commands run in this helper.
"""
import fcntl,json,os,runpy,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent.parent

def main():
 if sys.argv[1:]:print(json.dumps(dict(status='failed',message='This portable Chat helper supports game evidence only.')),flush=True);return
 try:
  line=sys.stdin.readline();request=json.loads(line)
  if request.get('domain')!='game'or not isinstance(request.get('query'),str)or not request['query'].strip():raise ValueError('Choose the game restoration team and enter a text request.')
  origin=json.loads((PACKAGE/'origin.json').read_text());same_host=Path(origin['original_workbench'])/'runs/.inference.lock';lock_path=same_host if same_host.is_file()else PACKAGE/'.machine-inference.lock'
  with lock_path.open('a')as machine_lock:
   try:fcntl.flock(machine_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:print(json.dumps(dict(status='busy',message='Another local inference or training job is active. Use checked status or retry after it finishes.')),flush=True);return
   original=sys.stdin
   class Replay:
    first=True
    def readline(self,*args,**kwargs):
     if self.first:self.first=False;return line
     return original.readline(*args,**kwargs)
    def read(self,*args,**kwargs):return original.read(*args,**kwargs)
   sys.stdin=Replay();sys.path.insert(0,str(PACKAGE/'runtime'));import portable_runtime_paths_v8 as paths;paths.install();sys.path.insert(0,str(PACKAGE/'runtime/.venv/lib/python3.12/site-packages'));sys.path.insert(0,str(PACKAGE/'workbench'));sys.argv=[str(PACKAGE/'workbench/scripts/native_chat_team_context.py')];runpy.run_path(sys.argv[0],run_name='__main__')
 except Exception as error:print(json.dumps(dict(status='failed',message='Portable game evidence is unavailable: '+str(error))),flush=True)
if __name__=='__main__':main()

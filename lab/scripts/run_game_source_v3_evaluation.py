"""Generate evaluation outputs and restore daily model even after failure."""
import subprocess,sys,fcntl
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];lms=str(Path.home()/'.lmstudio/bin/lms')
try:result=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_game_source_v3.py')],cwd=ROOT)
finally:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True);subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',check=True,timeout=300)
raise SystemExit(result.returncode)

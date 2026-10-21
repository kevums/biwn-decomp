"""Run existing complete native gates while redirecting their publication pointers."""
import importlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 kind,source,receipt=sys.argv[1:];source=str(Path(source).resolve());receipt=Path(receipt).resolve();receipt.mkdir(parents=True,exist_ok=True)
 module=importlib.import_module('check_biwn_native_'+kind)
 original_save=module.save
 def isolated_save(path,value):
  path=Path(path)
  if path.parent==ROOT/'verification':path=receipt/path.name
  original_save(path,value)
 module.save=isolated_save
 sys.argv=[module.__file__,'--source',source]
 module.main()
if __name__=='__main__':main()

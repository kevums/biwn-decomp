"""Local complete-source callback ABI repair after actual compiler failure."""
import fcntl,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
p=ROOT/'verification/local-scene-device-initialize-author-current.json'
d=json.loads(p.read_text());out=Path(d['directory']);source=out/'biwn_scene_device_initialize.c';before=source.read_text()
header=(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.h').read_text()
user='Actualcompiler rejected all12 writes: callback takes THREE args (context,address,value), not four args (bus,address,width,value). Correct full source using bus->context and omit explicit width; write16/write32 already encode width. Preserve every store,address,value,order,all validation/status/output behavior. Return JSON source,limitations only. Coordinator initial evidence omitted transitive header; corrected actual ABI below. No test-success claim.\nBUS HEADER:\n'+header+'\nSOURCE:\n'+before
with (ROOT/'runs/.inference.lock').open('w')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',lab.COMMON+'\nRepair the complete source against actual callback declarations.',user,1300)
(out/'callback-ABI-repair.json').write_text(json.dumps(result,indent=2)+'\n')
after=lab.parse_object(result['text'])['source']+'\n';(out/'pre-ABI-repair.c').write_text(before);source.write_text(after)
d.update(status='local_ABI_repair_pending_recheck',ABI_repair_seconds=result['seconds'],
         pre_repair_sha256=hashlib.sha256(before.encode()).hexdigest(),
         repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False,
         coordinator_evidence_correction='Original author/reviewer evidence omitted transitive bus header; supplied actual header after compiler failure.')
p.write_text(json.dumps(d,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(d,indent=2)+'\n')
with (out/'prompts-and-responses.txt').open('a')as f:f.write('CALLBACK ABI REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('Local callback repair saved',result['seconds'],flush=True)

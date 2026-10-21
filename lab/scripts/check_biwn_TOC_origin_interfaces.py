"""Verify diagnostic coordinate algebra and raw-sector correspondence."""
import ctypes as c,json,hashlib
from pathlib import Path
import check_biwn_scheduler as scheduler
ROOT=scheduler.ROOT;b=json.loads((ROOT/'verification/BIWN-TOC-origin-build-current.json').read_text());run=scheduler.Native(diagnostic_core=Path(b['core_path']));core=run.lib
core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool
core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32]
core.CDIntfGetTrackInfo.argtypes=[c.c_uint32,c.c_uint32];core.CDIntfGetTrackInfo.restype=c.c_uint8
core.CDIntfGetSessionInfo.argtypes=[c.c_uint32,c.c_uint32];core.CDIntfGetSessionInfo.restype=c.c_uint8
core.CDIntfReadBlock.argtypes=[c.c_uint32,c.c_void_p];core.CDIntfReadBlock.restype=c.c_bool
layout=json.loads((ROOT/'projects/black-ice-white-noise/analysis/session-20261012T191624.705232Z/cdi-layout.json').read_text())
frames=lambda b:b[0]*4500+b[1]*75+b[2]
try:
 assert core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode())
 track_rows=[];raw_rows=[]
 for t in layout['tracks']:
  core.BIWNDiagnosticTOCOrigin(0);old=[core.CDIntfGetTrackInfo(t['track'],i)for i in range(3)]
  core.BIWNDiagnosticTOCOrigin(1);new=[core.CDIntfGetTrackInfo(t['track'],i)for i in range(3)];assert frames(old)-frames(new)==150
  track_rows.append(dict(track=t['track'],default_MSF=old,diagnostic_MSF=new))
  pregap=t.get('pregap_sectors',t.get('pregap'));dataLBA=t['declared_start_lba']+pregap
  for delta in [0,1,75]:
   physical=dataLBA+delta;logical=physical-150;assert logical>=0
   left=c.create_string_buffer(2352);right=c.create_string_buffer(2352)
   core.BIWNDiagnosticTOCOrigin(0);assert core.CDIntfReadBlock(physical,left)
   core.BIWNDiagnosticTOCOrigin(3);assert core.CDIntfReadBlock(logical,right);assert left.raw==right.raw
   raw_rows.append(dict(track=t['track'],physical_LBA=physical,logical_LBA=logical,raw_sector_sha256=hashlib.sha256(left.raw).hexdigest()))
 sessions=[]
 for n in [0,1]:
  core.BIWNDiagnosticTOCOrigin(0);old=[core.CDIntfGetSessionInfo(n,i)for i in range(5)]
  core.BIWNDiagnosticTOCOrigin(1);new=[core.CDIntfGetSessionInfo(n,i)for i in range(5)];sessions.append(dict(session=n,default=old,diagnostic=new))
 assert sessions[0]['diagnostic']==[1,1,0,16,29] and frames(sessions[1]['default'][2:])-frames(sessions[1]['diagnostic'][2:])==150
 match=json.loads((ROOT/'verification/BIWN-TOC-origin-match-current.json').read_text());expected=(Path(match['directory'])/'TOC.bin').read_bytes()
 p=Path(next(x for x in (ROOT/'runs/firmware-TOC-origin-read-long-source.log').read_text().splitlines()if x.startswith('/')and '/BIWN-relocated-'in x));actual=(p/'fourth-DSP-command/DSP-after-CPU.bin').read_bytes()[0x800:0xc00];assert expected==actual
 report=dict(status='coordinate_interfaces_and_live_TOC_match',core_sha256=b['core_sha256'],track_checks=track_rows,sessions=sessions,raw_sector_comparisons=raw_rows,count=15,live_source_TOC_matches_captured_hypothesis_all1024bytes=True,TOC_sha256=hashlib.sha256(actual).hexdigest(),scope='Diagnostic flag algebra and raw-sector equality in same CDI backend; no physical drive or global timing proof. Default-off tests separately passed.',whole_boot=False)
 (ROOT/'verification/TOC-origin-interface-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],track_checks=5,sector_checks=15,live_TOC_bytes=1024)))
finally:run.close()

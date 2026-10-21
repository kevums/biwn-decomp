"""Image-specific normalized-disc backend, completion delivered at an explicit tick.

This supplies file bytes, not BIOS instructions or physical drive timing.
The674-byte stream phase has a32768-byte original-capture witness.
"""
from pathlib import Path
import json,hashlib
import extract_biwn_stage as stage
ROOT=stage.ROOT
class Disc:
 def __init__(self):
  self.manifest=json.loads((ROOT/'verification/biwn-disc-resources.json').read_text());raw=Path(self.manifest['raw_track_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==self.manifest['source_raw_track_sha256'];self.data=stage.swap16(raw);assert hashlib.sha256(self.data).hexdigest()==self.manifest['normalized_track_sha256'];self.stream_phase=self.manifest['captured_CD_buffer_witness']['within_sector_phase'];self.prefix=b'';self.reset()
 def use_previous_track_prefix(self,sectors=6):
  """Explicit image-backed lookbehind for original seeks before track3.

  Require contiguous stored2352-byte tracks in both CDI byte and LBA space.
  This does not infer missing gaps, fabricate padding or prove drive timing.
  """
  assert isinstance(sectors,int)and 1<=sectors<=16
  track=self.manifest['track'];session=Path(self.manifest['raw_track_path']).parent.parent
  layout=json.loads((session/'cdi-layout.json').read_text());previous=next(t for t in layout['tracks']if t['track']==track['track']-1)
  assert previous['sector_bytes']==track['sector_bytes']==2352 and previous['session']==track['session']
  assert previous['raw_file_offset']+previous['raw_bytes']==track['raw_file_offset']
  assert previous['declared_start_lba']+previous['total_sectors']==track['declared_start_lba']
  count=sectors*2352;assert count<=previous['raw_bytes']
  image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
  with image.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==self.manifest['source_CDI_sha256']
  start=track['raw_file_offset']-count
  with image.open('rb')as f:f.seek(start);raw=f.read(count)
  prior_raw=(session/'raw-tracks'/('track-'+str(previous['track']).zfill(2)+'-raw.bin')).read_bytes()
  assert len(raw)==count and raw==prior_raw[-count:]
  self.prefix=stage.swap16(raw)
  return {'previous_track':previous['track'],'sectors':sectors,'bytes':count,'CDI_file_offset':start,'normalized_prefix_sha256':hashlib.sha256(self.prefix).hexdigest(),'source_CDI_sha256':self.manifest['source_CDI_sha256'],'byte_and_LBA_contiguity_verified':True,'physical_timing_verified':False}
 def use_captured_stream(self,normalized_offset,captured):
  """Select a fixed test phase only after matching a complete captured buffer.

  This is an explicit replay condition, not a prediction of other BIOS reads.
  reset() deliberately retains the selected phase across native/C comparisons.
  """
  assert isinstance(normalized_offset,int) and normalized_offset>=0 and len(captured)>=32768
  assert self.data[normalized_offset:normalized_offset+len(captured)]==captured
  self.stream_phase=normalized_offset%2352
  return {'normalized_offset':normalized_offset,'bytes':len(captured),'sha256':hashlib.sha256(captured).hexdigest(),'within_sector_phase':self.stream_phase}
 def reset(self):self.pending=None;self.requests=[];self.completions=[];self.stops=0
 def start(self,start,end,packed):
  minute,second,frame=(packed>>16)&255,(packed>>8)&255,packed&255;assert packed>>24==0 and second<60 and frame<75
  absolute=minute*4500+second*75+frame;track=self.manifest['track'];relative=absolute-(track['declared_start_lba']+150+track['pregap_sectors']);offset=relative*2352+self.stream_phase;count=end-start;assert start==0x1c0000 and 0<count<=0x40000 and -len(self.prefix)<=offset<=len(self.data)-count
  if offset<0:
   leading=min(-offset,count);data=self.prefix[len(self.prefix)+offset:len(self.prefix)+offset+leading]+self.data[:count-leading]
  else:data=self.data[offset:offset+count]
  assert len(data)==count
  self.pending=(start,end,data);self.requests.append({'destination_start':start,'destination_end':end,'packed_binary_MSF':packed,'normalized_track_offset':offset,'bytes':count,'sha256':hashlib.sha256(data).hexdigest()})
 def tick(self,write_bulk,write32):
  if self.pending:
   start,end,data=self.pending;write_bulk(start,data);write32(0xbd848,end);self.completions.append({'bytes':len(data),'progress_address':0xbd848,'progress_value':end});self.pending=None
 def stop(self):self.stops+=1

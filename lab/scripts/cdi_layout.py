# SPDX-License-Identifier: GPL-2.0-only
"""Bounded CDI metadata reader and lossless raw-track extraction.

Track-header layout adapted from CDIrip by DeXT/Lawrence Williams,
https://github.com/jozip/cdirip, revision 97dd0a9b1861638b39ea87a56fa0c8725db9d7c8.
Original source and GPL v2 license are retained in tools/cdirip-source/.
No disc-sector transformations, gap removal, audio swapping or game execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parent.parent
MARK=bytes.fromhex('000001000000ffffffff')
VERSIONS={0x80000004:'CDI_V2',0x80000005:'CDI_V3',0x80000006:'CDI_V35'}
SIZES={0:2048,1:2336,2:2352,4:2448}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

class Reader:
 def __init__(self,data):self.data=data;self.position=0
 def read(self,length):
  if length<0 or self.position+length>len(self.data):raise ValueError('Truncated CDI header')
  value=self.data[self.position:self.position+length];self.position+=length;return value
 def skip(self,length):self.read(length)
 def u8(self):return self.read(1)[0]
 def u16(self):return struct.unpack('<H',self.read(2))[0]
 def u32(self):return struct.unpack('<I',self.read(4))[0]

def parse(path):
 path=path.expanduser().resolve();length=path.stat().st_size
 if length<8:raise ValueError('Image too short')
 with path.open('rb') as stream:
  stream.seek(-8,2);version,offset=struct.unpack('<II',stream.read(8))
  if version not in VERSIONS or not offset:raise ValueError('Unsupported CDI footer')
  header_start=length-offset if version==0x80000006 else offset
  if not 0<=header_start<length-8 or length-8-header_start>16*1024*1024:raise ValueError('Invalid/oversized CDI header extent')
  stream.seek(header_start);header=stream.read(length-8-header_start)
 reader=Reader(header);session_count=reader.u16()
 if not 1<=session_count<=255:raise ValueError('Unsupported session count')
 sessions=[];tracks=[];data_end=0
 for session in range(1,session_count+1):
  track_count=reader.u16()
  if track_count>100:raise ValueError('Unsupported track count')
  sessions.append({'session':session,'tracks':track_count})
  for number in range(1,track_count+1):
   start=reader.position
   if reader.u32()!=0:reader.skip(8)
   if reader.read(10)!=MARK or reader.read(10)!=MARK:raise ValueError('Missing CDI track markers')
   reader.skip(4);name=reader.read(reader.u8());reader.skip(19)
   if reader.u32()==0x80000000:reader.skip(8)
   reader.skip(2);pregap=reader.u32();sectors=reader.u32();reader.skip(6);mode=reader.u32()
   reader.skip(12);lba=reader.u32();total=reader.u32();reader.skip(16);size_code=reader.u32()
   if mode>2 or size_code not in SIZES:raise ValueError('Unsupported track mode or sector size')
   if total<pregap+sectors:raise ValueError('Track is shorter than declared pregap plus program sectors')
   size=SIZES[size_code];extent=total*size
   if data_end+extent>header_start:raise ValueError('Track data overlaps CDI metadata')
   reader.skip(29)
   if version!=0x80000004:
    reader.skip(5)
    if reader.u32()==0xffffffff:reader.skip(78)
   tracks.append({'track':len(tracks)+1,'session':session,'session_track':number,
    'header_file_offset':header_start+start,'header_bytes':reader.position-start,
    'embedded_filename_hex':name.hex(),'mode':mode,'mode_label':{0:'AUDIO',1:'MODE1',2:'MODE2'}[mode],
    'sector_size_code':size_code,'sector_bytes':size,'pregap_sectors':pregap,'program_sectors':sectors,
    'total_sectors':total,'trailing_sectors':total-pregap-sectors,'declared_start_lba':lba,
    'raw_file_offset':data_end,'raw_bytes':extent,
    'program_file_offset':data_end+pregap*size,'program_bytes':sectors*size})
   data_end+=extent
  reader.skip(12 if version==0x80000004 else 13)
 if not tracks:raise ValueError('No tracks found')
 return {'schema':'local-ai-cdi-layout/v1','source':str(path),'source_bytes':length,'source_sha256':sha(path),
  'version':VERSIONS[version],'footer_version_hex':f'{version:08x}','footer_offset_value':offset,
  'header_start':header_start,'header_sha256':hashlib.sha256(header).hexdigest(),
  'sessions':sessions,'tracks':tracks,'mapped_data_end':data_end,
  'unmapped_preheader_bytes':header_start-data_end,'remaining_header_bytes':len(header)-reader.position,
  'remaining_header_hex':header[reader.position:].hex(),
  'implementation_sha256':sha(Path(__file__)),
  'reference_revision':'97dd0a9b1861638b39ea87a56fa0c8725db9d7c8',
  'scope':'CDI declarations and contiguous stored byte ranges only; no ISA, executable or Jaguar boot mapping proven.'}

def extract(report,destination):
 source=Path(report['source']);destination.mkdir(parents=True,exist_ok=True)
 if sha(source)!=report['source_sha256']:raise ValueError('Source changed after layout capture')
 outputs=[]
 with source.open('rb') as stream:
  for track in report['tracks']:
   target=destination/f'track-{track["track"]:02d}-raw.bin'
   if target.exists():raise ValueError(f'Output already exists: {target}')
   stream.seek(track['raw_file_offset']);remaining=track['raw_bytes'];digest=hashlib.sha256()
   with target.open('xb') as output:
    while remaining:
     data=stream.read(min(1024*1024,remaining))
     if not data:raise ValueError('Unexpected end of CDI track data')
     output.write(data);digest.update(data);remaining-=len(data)
   # Independent output readback, preserving every stored sector and gap.
   if sha(target)!=digest.hexdigest():raise ValueError('Track output readback mismatch')
   outputs.append({'track':track['track'],'path':str(target),'bytes':track['raw_bytes'],
    'source_offset':track['raw_file_offset'],'sha256':digest.hexdigest(),
    'transformations':'none; pregap and trailing sectors retained'})
 if sha(source)!=report['source_sha256']:raise ValueError('Source changed during extraction')
 return outputs

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('image',type=Path);parser.add_argument('--output',required=True,type=Path)
 parser.add_argument('--extract-to',type=Path)
 args=parser.parse_args();report=parse(args.image)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(report,indent=2)+'\n')
 if args.extract_to:
  report['extracted_tracks']=extract(report,args.extract_to)
  args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'report':str(args.output),'version':report['version'],'sessions':report['sessions'],
  'tracks':report['tracks'],'unmapped_preheader_bytes':report['unmapped_preheader_bytes']},indent=2))

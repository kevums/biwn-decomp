"""Fixed C for source6AE0/6DA0; standalone candidates, no live-scene claim."""
import hashlib,json
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
 stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert sha(stage)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
 for header,count in [(0x6ae0,276),(0x6da0,94)]:
  folder=session/f'gpu-render-{header:x}-overlay';mapping=json.loads((folder/'initial-linear-decode.json').read_text());payload=(folder/'original-overlay.bin').read_bytes();rows=mapping['rows'];assert len(rows)==count and sha(payload)==mapping['payload_sha256']
  original_header=stage[header-0x4000:header-0x4000+8];assert int.from_bytes(original_header[:4],'big')==0xf03240 and int.from_bytes(original_header[4:],'big')*4==len(payload)
  assert stage[header-0x4000+8:header-0x4000+8+len(payload)]==payload
  assert sha(payload)=={0x6ae0:'6c57d1c4bb60864668af932028b2cdb29c6e217adc0c715712633663973ff608',0x6da0:'244cddc6b648a29a953a26c583865d2c28e76b88e4159884584e17f4a27aaaa7'}[header]
  lower=f'gpu_interior{header:x}';upper=lower.upper()
  def rename(text):return text.replace('gpu_geometry',lower).replace('GPU_GEOMETRY',upper)
  prefix=rename(base.PREFIX).replace('GPU4D80',f'GPU{header:X}').replace('generate_biwn_gpu_geometry.py','generate_biwn_gpu_interior.py')
  if header==0x6ae0:
   prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int wr16('))+'\n'
  if header==0x6da0:
   prefix='\n'.join(line for line in prefix.splitlines()if not any(line.startswith('static '+signature)for signature in ['uint32_t sx16(', 'void divide(', 'int matrix(']))+'\n'
  image='static const uint8_t source_image[]={'+','.join(hex(x)for x in payload)+'};\n'
  arg0,arg4=(0x47b88,0x10d688)if header==0x6ae0 else(0x47bc8,0x49b88)
  prepare=f'''enum biwn_{lower}_status biwn_{lower}_prepare(struct biwn_{lower}_state *s,uint32_t scene,uint32_t sector){{if(!s||s->z>1||s->c>1||s->n>1)return 1;memcpy(s->local_RAM+0x240,source_image,sizeof(source_image));put32(s->local_RAM+0x204,{header}u);put32(s->local_RAM+0x20c,{arg0}u);put32(s->local_RAM+0x210,0x49b8c);put32(s->local_RAM+0x214,scene);put32(s->local_RAM+0x218,sector);put32(s->local_RAM+0x21c,{arg4}u);s->pc=0xf03240;s->instructions=0;return 0;}}
#define CHECK(e) do{{int status=(e);if(status)return(enum biwn_{lower}_status)status;}}while(0)
enum biwn_{lower}_status biwn_{lower}_run(struct biwn_{lower}_bus *bus,struct biwn_{lower}_state *state,uint32_t budget){{struct biwn_{lower}_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){{unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){{
'''
  suffix=rename('''default:return BIWN_GPU_GEOMETRY_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_GEOMETRY_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_GEOMETRY_OK;}}return BIWN_GPU_GEOMETRY_WORK_LIMIT;}
''')
  headertext=rename(base.HEADER[:base.HEADER.index('/* Source-specific')])+f'''/* Fixed{count}source instructions, source-specific reconstruction.
 * Bank0 active. prepare preserves incoming banks/flags/matrix/divider/RAM,
 * installs the original overlay and sourceE0F2/E148 arguments. Valid finite
 * relocated interior scene and in-range room sector are caller requirements.
 * run stops atF031BE after mandatory delay. No dispatcher/CPU wrapper,
 * boot/load integration, timing, interrupts, raster/scanout/fullgame claim.
 * Errors retain prior bus stores and leave caller state unchanged. */
enum biwn_{lower}_status biwn_{lower}_prepare(struct biwn_{lower}_state *,uint32_t,uint32_t);
enum biwn_{lower}_status biwn_{lower}_run(struct biwn_{lower}_bus *,struct biwn_{lower}_state *,uint32_t);
#endif
'''
  source=ROOT/'projects/black-ice-white-noise/restoration';cfile=source/f'biwn_{lower}.c';hfile=source/f'biwn_{lower}.h';cfile.write_text(prefix+image+prepare+'\n'.join(base.emit(row)for row in rows)+'\n'+suffix);hfile.write_text(headertext)
  manifest=dict(status='generated_unverified_not_counted',pinned_stage_sha256=sha(stage),instructions=count,payload_bytes=len(payload),payload_sha256=sha(payload),generator_sha256=sha(Path(__file__).read_bytes()),shared_generator_sha256=sha(Path(base.__file__).read_bytes()),source_sha256={p.name:sha(p.read_bytes())for p in [cfile,hfile]},instructions_decoded=rows,new_published_components=0,whole_game_complete=False)
  (folder/'C-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()

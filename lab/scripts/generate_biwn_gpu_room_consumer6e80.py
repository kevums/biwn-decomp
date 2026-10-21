"""Fixed source6E80 room mesh builder, returning to resident F03440."""
import hashlib,json
from pathlib import Path
import generate_biwn_gpu_geometry as base
import generate_biwn_gpu_projection as extended
ROOT=base.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert sha(stage)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';folder=session/'gpu-render-6e80-overlay';mapping=json.loads((folder/'initial-linear-decode.json').read_text());payload=(folder/'original-overlay.bin').read_bytes();assert stage[0x6e80-0x4000:0x6e88-0x4000]==bytes.fromhex('00f0324000000078')and stage[0x6e88-0x4000:0x7068-0x4000]==payload and sha(payload)==mapping['payload_sha256'];rows=mapping['rows'];assert len(rows)==222 and rows[-1]['address']==0xf0341e
 def rename(t):return t.replace('gpu_geometry','gpu_room_consumer6e80').replace('GPU_GEOMETRY','GPU_ROOM_CONSUMER6E80')
 prefix=rename(base.PREFIX).replace('GPU4D80','GPU6E80').replace('generate_biwn_gpu_geometry.py','generate_biwn_gpu_room_consumer6e80.py');prefix='\n'.join(line for line in prefix.splitlines()if not any(line.startswith('static '+signature)for signature in ['uint32_t sx16(', 'uint32_t sar(', 'void divide(', 'int matrix(']))+'\n'
 header=rename(base.HEADER[:base.HEADER.index('/* Source-specific')])+'''/* Fixed222sourceinstructions. Source57A0/dispatcher supplies the entry
 * registers and source overlay. Bank0active; preserve full incoming banks,
 * Z/C/N,matrix/divider and4KBlocalRAM. run returns at residentF03440;
 * mesh data/face records are written through the supplied bus. Mandatory
 * delay slots execute. No runtime decode or original GPU/core calls.
 * Does not run resident transforms/material/raster/dispatcher or fullgame.
 * Finite valid room/dimension/portal buffers required; no physical timing.
 * Errors retain prior stores and leave caller state unchanged. */
enum biwn_gpu_room_consumer6e80_status biwn_gpu_room_consumer6e80_run(struct biwn_gpu_room_consumer6e80_bus *,struct biwn_gpu_room_consumer6e80_state *,uint32_t);
#endif
'''
 functions=rename('''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_geometry_status)status;}while(0)
enum biwn_gpu_geometry_status biwn_gpu_geometry_run(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *state,uint32_t budget){struct biwn_gpu_geometry_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
''')
 suffix=rename('''default:return BIWN_GPU_GEOMETRY_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_GEOMETRY_BAD_DELAY;s.pc=resume;}if(s.pc==0xf03440u){*state=s;return BIWN_GPU_GEOMETRY_OK;}}return BIWN_GPU_GEOMETRY_WORK_LIMIT;}
''')
 source=ROOT/'projects/black-ice-white-noise/restoration';cfile=source/'biwn_gpu_room_consumer6e80.c';hfile=source/'biwn_gpu_room_consumer6e80.h';cfile.write_text(prefix+functions+'\n'.join(extended.emit(row)for row in rows)+'\n'+suffix);hfile.write_text(header);manifest=dict(status='generated_unverified_not_counted',instructions=222,payload_bytes=480,payload_sha256=sha(payload),stage_sha256=sha(stage),generator_sha256=sha(Path(__file__).read_bytes()),shared_generator_sha256=sha(Path(base.__file__).read_bytes()),source_sha256={p.name:sha(p.read_bytes())for p in [cfile,hfile]},instructions_decoded=rows,new_published_components=0,whole_game_complete=False);(folder/'C-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()

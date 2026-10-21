"""Static candidate for original GPU4720; boundaries still require native coverage."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT;sys.path.insert(0,str(ROOT));import binary_tools
rename=lambda text:text.replace('gpu_geometry','gpu_command4720').replace('GPU_GEOMETRY','GPU_COMMAND4720')
def main():
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();entry=int.from_bytes(snapshot[0x4720:0x4724],'big');length=int.from_bytes(snapshot[0x4724:0x4728],'big')*4;assert(entry,length)==(0xf03240,968);payload=snapshot[0x4728:0x4728+length];decoded,decoder=binary_tools.jaguar_instructions(payload,entry,'gpu');rows=[r for r in decoded if r['address']<0xf03502];assert len(rows)==333 and rows[-1]['address']==0xf03500
 out=ROOT/'verification/GPU4720-candidate-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 header=rename(base.HEADER).replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;');a=header.index('/* Source-specific');b=header.index('enum biwn_gpu_command4720_status biwn_gpu_command4720_run',a);header=header[:a]+'''/* Candidate fixed GPU4720 instructions; full inherited logical GPU state,
 * supplied source-loaded local RAM. Return at residentF031BE; mandatory
 * delay slots execute. No runtime decoder or originalGPU calls on C path.
 * Errors retain prior external writes and leave inputstate unchanged.
 * This generated artifact is unverified until native comparison passes.
 * Pipeline microstate, timing, dispatcher/CPU service and game integration
 * remain outside this module. */
'''+header[b:]
 prefix=rename(base.PREFIX);prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static void divide(','static int matrix(')))+'\n';prefix=prefix.replace('pinned GPU4D80 overlay','pinned GPU4720 command payload').replace('scripts/generate_biwn_gpu_geometry.py','scripts/generate_GPU4720_candidate.py')
 prefix+='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_command4720_status)status;}while(0)
enum biwn_gpu_command4720_status biwn_gpu_command4720_run(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *state,uint32_t budget){struct biwn_gpu_command4720_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
 cases=[]
 for row in rows:
  word=int(row['bytes'][:4],16);op,m,n=word>>10,(word>>5)&31,word&31
  if op==37:lines=[f's.registers[0][{n}]=s.registers[1][{m}];']
  elif op==41:
   M=f's.registers[0][{m}]';lines=[f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));s.registers[0][{n}]=v;']
  else:cases.append(rename(base.emit(row)));continue
  cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n '+'\n '.join(lines)+f'\n s.pc={hex(row["address"]+row["size"])}u;break;')
 suffix='''default:return BIWN_GPU_COMMAND4720_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_COMMAND4720_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_COMMAND4720_WORK_LIMIT;}
'''
 names=['biwn_gpu_command4720.c','biwn_gpu_command4720.h'];(out/names[0]).write_text(prefix+'\n'.join(cases)+'\n'+suffix);(out/names[1]).write_text(header)
 d=dict(status='generated_unverified',directory=str(out),source=str(out/names[0]),header=str(out/names[1]),source_sha256={n:hashlib.sha256((out/n).read_bytes()).hexdigest()for n in names},instructions_decoded=rows,payload_sha256=hashlib.sha256(payload).hexdigest(),payload_start=0x4728,payload_bytes=968,code_end=0xf03502,table_start=0xf03504,decoder=decoder,coordinator_authored=True,new_training=False,native_coverage_verified=False,whole_game_complete=False)
 (out/'generation.json').write_text(json.dumps(d,indent=2)+'\n');(ROOT/'verification/GPU4720-generation-current.json').write_text(json.dumps(d,indent=2)+'\n');print('Generated GPU4720 candidate',len(rows),'instructions; pending native coverage',out,flush=True)
if __name__=='__main__':main()

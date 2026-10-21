"""Fixed fifteen-instruction CPU copy and video-counter wait from live discovery."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_firmware_post_GPU_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_FIRMWARE_POST_GPU_CPU')

def main():
    origin=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T031716.035517Z'
    discovery=json.loads((origin/'CPU-after-GPU.json').read_text());rows=discovery['visited_instructions'];assert len(rows)==15
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static uint32_t sx16(','static uint32_t sx8(','static void pop(','static int push(','static int invoke(')))+'\n'
    guards='static int source_guard(struct dispatch *s){uint32_t value;switch(s->cpu.pc){\n'
    for row in rows:
        raw=bytes.fromhex(row['bytes']);guards+=f'case {hex(row["address"])}u:\n'
        for off in range(0,len(raw),2):guards+=f'if(read_value(s,{hex(row["address"]+off)}u,2,&value))return 2;if(value!={hex(int.from_bytes(raw[off:off+2],"big"))}u)return 7;\n'
        guards+='return 0;\n'
    guards+='default:return 7;}}\n'
    prefix=prefix.replace('#define CHECK',guards+'#define CHECK',1)
    prefix=prefix.replace('s.bus=bus;','(void)full_call;s.bus=bus;',1)
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.cpu.pc==0x1014u){*state=s.cpu;return BIWN_FIRMWARE_POST_GPU_CPU_READY;}CHECK(source_guard(&s));CHECK(s.service(s.context,s.bus,&s.cpu,s.cpu.pc));switch(s.cpu.pc){',1)
    suffix=rename(entry.rename(entry.loader.base.SUFFIX)).replace('}}return BIWN_FIRMWARE_POST_GPU_CPU_WORK_LIMIT;','}}*state=s.cpu;return BIWN_FIRMWARE_POST_GPU_CPU_WORK_LIMIT;')
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_FIRMWARE_POST_GPU_CPU_H').replace('BIWN_FIRMWARE_POST_GPU_CPU_BAD_PC=7','BIWN_FIRMWARE_POST_GPU_CPU_BAD_PC=7,BIWN_FIRMWARE_POST_GPU_CPU_READY=8')
    a=header.index('/* Static');b=header.index('enum biwn_firmware_post_GPU_cpu_status biwn_firmware_post_GPU_cpu_body',a)
    header=header[:a]+'''/* Observed 5028A..502AA GPU GO check, source 228-byte RAM copy to1000,
 * natural JMP1000, then 1000..1014 source video-counter delta-five wait.
 * Exact live instruction words guarded. READY8 stops before1014; work
 * limit4 commits CPU continuation. Service observes each instruction;
 * shared MMIO and external source video events remain providers.
 * No originalCPU execution/runtime instruction decoder. Other main
 * firmware, discboot, global timing and fullgame remain unverified. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_firmware_post_GPU_cpu.c','biwn_firmware_post_GPU_cpu.h']
    (source/names[0]).write_text(prefix+'\n'.join(rename(entry.emit(row))for row in rows)+'\n'+suffix);(source/names[1]).write_text(header)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    report=dict(status='generated_unverified',origin=str(origin),instructions=15,instructions_decoded=rows,stop_PC='0x1014',live_instruction_guards=True,source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),implementation_authorship='coordinator',whole_game_complete=False)
    (session/'firmware-post-GPU-CPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))

if __name__=='__main__':main()

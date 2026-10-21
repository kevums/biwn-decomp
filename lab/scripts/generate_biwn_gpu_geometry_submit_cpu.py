"""Fixed fullCPU E0A6 source wrapper; GPU and E098wait are providers."""
import hashlib,json,re
from pathlib import Path
import generate_biwn_resource_cpu as resource
ROOT=resource.ROOT
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    assert image[0xe0a6-0x4000:0xe0f2-0x4000]==snapshot[0xe0a6:0xe0f2]
    rows,_=resource.base.binary_tools.m68k_instructions(snapshot[0xe0a6:0xe0f2],0xe0a6);assert len(rows)==10
    prefix=resource.base.PREFIX.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_gpu_geometry_submit_cpu.py').replace('biwn_input_dispatch_cpu','biwn_gpu_geometry_submit_cpu').replace('biwn_dispatch_cpu_status','biwn_gpu_geometry_submit_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_GPU_GEOMETRY_SUBMIT_CPU').replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=re.sub(r'static uint32_t sx(?:16|8)[^\n]*\n','',prefix);prefix=re.sub(r'static void put[^\n]*\n','',prefix);prefix=re.sub(r'static void shift.*?(?=static int read_value)','',prefix,flags=re.S)
    suffix=resource.base.SUFFIX.replace('biwn_input_dispatch_cpu','biwn_gpu_geometry_submit_cpu').replace('biwn_dispatch_cpu_status','biwn_gpu_geometry_submit_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_GPU_GEOMETRY_SUBMIT_CPU')
    header=resource.HEADER.replace('BIWN_RESOURCE_CPU','BIWN_GPU_GEOMETRY_SUBMIT_CPU').replace('biwn_resource_cpu','biwn_gpu_geometry_submit_cpu');a=header.index('/*');b=header.index('*/',a)+2;header=header[:a]+'/* FullCPU10sourceinstructions E0A6submission. Bothstackbanks. E098wait andGPU4D80behavior are explicit providers; body stops beforeRTS/call consumesit. No runtimeCPUdecode or originalCPUcalls. */'+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';(source/'biwn_gpu_geometry_submit_cpu.c').write_text(prefix+'\n'.join(resource.emit(row).replace('BIWN_RESOURCE_CPU','BIWN_GPU_GEOMETRY_SUBMIT_CPU')for row in rows)+'\n'+suffix);(source/'biwn_gpu_geometry_submit_cpu.h').write_text(header)
    manifest=dict(status='generated_unverified',instructions=10,instructions_decoded=rows,stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_gpu_geometry_submit_cpu.c','biwn_gpu_geometry_submit_cpu.h']});(session/'gpu-geometry-submit-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()

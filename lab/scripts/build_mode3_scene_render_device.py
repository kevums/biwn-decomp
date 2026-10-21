"""Separate retained scene device adds source4720 before existing52E0/57A0."""
import argparse,json,hashlib,subprocess,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--movement',action='store_true');options=parser.parse_args()
 before=(ROOT/'scripts/biwn_retained_scene_render_device_bridge.c').read_text()
 function='''
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_command4720.h"
static int scene_C_cube4720(void)
{
 size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
 uint8_t raw[8192];size_t size;int status;
 struct biwn_gpu_command4720_state s;
 struct biwn_gpu_command4720_bus bus={consumer_read16,hybrid_read,material_write16,hybrid_write,hybrid_observe,NULL};
 save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
 load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");
 if(!save_state||!load_state)return 1;
 size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395])return 2;
 memset(&s,0,sizeof(s));memcpy(s.local_RAM,raw,4096);
 memcpy(&s.pc,raw+4096,4);memcpy(&s.accumulator,raw+4100,4);
 memcpy(&s.remainder,raw+4104,4);memcpy(&s.hidata,raw+4108,4);
 memcpy(&s.flags,raw+4112,4);memcpy(&s.matrix_control,raw+4116,4);
 memcpy(&s.matrix_pointer,raw+4120,4);memcpy(&s.data_organization,raw+4124,4);
 memcpy(&s.control,raw+4128,4);memcpy(&s.division_control,raw+4132,4);
 s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
 memcpy(s.registers,raw+4139,sizeof(s.registers));s.active_bank=raw[4395];
 component=3;status=biwn_gpu_command4720_run(&bus,&s,100000u);component=0;
 if(status)return status;
 if(save_state(raw)!=size)return 3;
 memcpy(raw,s.local_RAM,4096);memcpy(raw+4096,&s.pc,4);
 memcpy(raw+4100,&s.accumulator,4);memcpy(raw+4104,&s.remainder,4);
 memcpy(raw+4108,&s.hidata,4);memcpy(raw+4112,&s.flags,4);
 memcpy(raw+4116,&s.matrix_control,4);memcpy(raw+4120,&s.matrix_pointer,4);
 memcpy(raw+4124,&s.data_organization,4);memcpy(raw+4128,&s.control,4);
 memcpy(raw+4132,&s.division_control,4);raw[4136]=(uint8_t)s.z;
 raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;
 memcpy(raw+4139,s.registers,sizeof(s.registers));raw[4395]=(uint8_t)s.active_bank;
 return load_state(raw)==size?0:4;
}
'''
 needle='int lab_scene_render_submit(void *unused,uint32_t address,uint32_t value)';assert needle in before
 if options.movement:function+=function.replace('biwn_gpu_command4720','biwn_movement_fullGPU').replace('scene_C_cube4720','scene_C_movement4320')
 text=before.replace(needle,function+'\n'+needle)
 text=text.replace('(value!=0x4d80u&&value!=0x52e0u&&value!=0x57a0u)','(value!=0x4720u&&value!=0x4d80u&&value!=0x52e0u&&value!=0x57a0u)')
 text=text.replace('header!=0x4d80u&&header!=0x52e0u','header!=0x4720u&&header!=0x4d80u&&header!=0x52e0u')
 needle='else if(pc==0xf03240u&&header==0x4d80u)';assert needle in text
 text=text.replace(needle,'else if(pc==0xf03240u&&header==0x4720u){status=scene_C_cube4720();scene_render_stats[7]++;}\n        '+needle)
 if options.movement:
  text=text.replace('(value!=0x4720u&&','(value!=0x4320u&&value!=0x4720u&&').replace('header!=0x4720u&&','header!=0x4320u&&header!=0x4720u&&')
  text=text.replace(needle,'else if(pc==0xf03240u&&header==0x4320u){status=scene_C_movement4320();scene_render_stats[7]++;}\n        '+needle)
 bridge=ROOT/'scripts'/('biwn_mode3_world_render_device_bridge.c' if options.movement else 'biwn_mode3_scene_render_device_bridge.c');bridge.write_text(text)
 out=ROOT/'verification/mode3-scene-render-device'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 existing=json.loads((ROOT/'verification/retained-interior-render-device-build.json').read_text())['command']
 command=[str(bridge)if v.endswith('/biwn_retained_interior_render_device_bridge.c')else v for v in existing]
 output=out/'libmode3-scene-render-device.dylib';command[command.index('-o')+1]=str(output)
 command.insert(command.index('-lm'),str(ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_command4720.c'))
 if options.movement:command.insert(command.index('-lm'),str(ROOT/'projects/black-ice-white-noise/restoration/biwn_movement_fullGPU.c'))
 compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 (out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert not compiled.returncode,compiled.stderr
 report=dict(status='built_unverified_separate_mode3_renderer',directory=str(out),library=str(output),library_sha256=sha(output.read_bytes()),command=command,bridge=str(bridge),bridge_sha256=sha(text.encode()),source_sha256={v:sha(Path(v).read_bytes())for v in command if v.endswith('.c')},canonical_device_library_modified=False,default_promoted=False,scope='New retained bridge adds GPU4720 to existing source52E0/57A0/consumer/material/resident/dispatcher implementations. Build only; exact modified-program native/C pipeline comparison required. No default/library replacement or playable claim.')
 name='mode3-world-render-device-build-current.json' if options.movement else 'mode3-scene-render-device-build-current.json'
 (ROOT/'verification'/name).write_text(json.dumps(report,indent=2)+'\n');print(report['status'],output)
if __name__=='__main__':main()

"""Compile a native bridge over the accepted fixed GPU kernels; no core changes."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_GPU as GPU
from biwn_renderer_bundle import State,GeometryState
from biwn_material_bundle import PartialState
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--interior-candidate',type=Path);parser.add_argument('--candidate-output',type=Path);parser.add_argument('--capture-unknown',action='store_true');args=parser.parse_args()
    assert not args.interior_candidate or args.candidate_output, 'Additional kernels require isolated candidate output'
    assert not args.capture_unknown or args.candidate_output
    out=ROOT/'verification/fast-GPU-bridge-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    load=lambda name:json.loads((ROOT/'verification'/name).read_text())
    OP=load('OP-GPU-slice-current.json');render=load('renderer-bundle-candidate.json');mat=load('material-bundle-candidate.json');control=load('control-GPU-bundle-candidate.json');setup=load('setup-bundle-candidate.json')
    programs=[dict(name='OP',stem='biwn_gpu_OP_slice',function='biwn_gpu_OP_slice_run',library=OP['library'],instructions_decoded=OP['instructions_decoded'],type=GPU.State,kind='overlay')]
    programs.append(dict(name='resident',stem='biwn_gpu_resident',function='biwn_gpu_resident_bundle_run',library=render['library'],instructions_decoded=render['instructions_decoded'],type=State,kind='resident'))
    for row in render['overlays']:programs.append({**row,'stem':'biwn_gpu_'+row['name'],'function':'biwn_gpu_'+row['name']+'_bundle_run','type':GeometryState if row['name']=='geometry'else State,'kind':'overlay'})
    for row in mat['overlays']:programs.append({**row,'stem':'biwn_gpu_'+row['name'],'function':'biwn_gpu_'+row['name']+'_bundle_run','type':PartialState,'kind':'material'if row['name'].startswith('material')else'consumer'})
    for row in control['overlays']:programs.append({**row,'stem':'biwn_'+row['name']+'_fullGPU','type':GPU.State,'kind':'material'if row['name']=='sprite'else'overlay'})
    programs.append({**setup,'name':'setup57','stem':'biwn_gpu_setup57','function':'biwn_gpu_setup57_bundle_run','type':PartialState,'kind':'setup'})
    if args.interior_candidate:
        extra=json.loads(args.interior_candidate.read_text())
        programs.extend({**row,'type':GPU.State if row['kind']in ['movie','movie_exit','firstboot']else GeometryState}for row in extra['programs'])
    includes=[];libraries=[];wrappers=[];tables=[]
    for number,p in enumerate(programs):
        directory=Path(p['library']).parent;header=directory/(p['stem']+'.h');assert header.exists(),header
        includes.append('#include "'+str(header)+'"');libraries.append(p['library'])
        state='struct '+p['stem']+'_state';bus='struct '+p['stem']+'_bus';fn=p['function'];typ=p['type']
        assert fn in (directory/(p['stem']+'.c')).read_text()
        # Original headers retain run declarations; declare the isolated bundle ABI.
        wrappers.append('extern enum '+p['stem']+'_status '+fn+'('+bus+'*,'+state+'*,uint32_t);')
        if p['kind']=='resident':values='rd16,rd32,wr32,blit,NULL,NULL'
        elif p['kind']in ['overlay','interior','movie_exit']:values='rd16,rd32,wr16,wr32,NULL,NULL'
        elif p['kind']=='movie':values='rd8,rd16,rd32,wr32,NULL,NULL'
        elif p['kind']in ['material','firstboot']:values='rd8,rd16,rd32,wr16,wr32,NULL,NULL'
        elif p['kind']=='consumer':values='rd16,rd32,wr32,NULL,NULL'
        else:values='rd32,wr32,NULL,NULL'
        body='static int run_'+str(number)+'(struct full*s){'+state+' t;'+bus+' b={'+values+'};int status;'
        for field,_ in typ._fields_:
            if field in ['registers','local_RAM']:body+='memcpy(t.'+field+',s->'+field+',sizeof(t.'+field+'));'
            else:body+='t.'+field+'=s->'+field+';'
        body+='status='+fn+'(&b,&t,1);if(status)return status;'
        if typ is PartialState or p['kind']in ['interior','movie','movie_exit','firstboot']:
            body+='if(H.save(raw_after)!=4416)return 90;unpack(raw_after,s);memcpy(private_after,raw_after+4396,20);use_private_after=1;'
        for field,_ in typ._fields_:
            if field in ['registers','local_RAM']:body+='memcpy(s->'+field+',t.'+field+',sizeof(t.'+field+'));'
            else:body+='s->'+field+'=t.'+field+';'
        body+='return 0;}';wrappers.append(body)
        rows=[]
        for row in p['instructions_decoded']:
            data=bytes.fromhex(row['bytes']);assert len(data)in [2,6];slot=(row['address']-0xf03000)//2;assert 0<=slot<2048
            rows.append('['+str(slot)+']={'+str(len(data))+',{'+','.join(str(x)for x in data)+'}},')
        tables.append('static const struct identity map_'+str(number)+'[2048]={'+''.join(rows)+'};')
    prefix='''#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <CommonCrypto/CommonDigest.h>
struct host {size_t(*save)(void*);size_t(*load)(void*);uint16_t(*read16)(uint32_t,uint32_t);uint32_t(*read32)(uint32_t,uint32_t);void(*write16)(uint32_t,uint16_t,uint32_t);void(*write32)(uint32_t,uint32_t,uint32_t);uint8_t(*read8)(uint32_t,uint32_t);void*(*RAM)(void);uint32_t*counter;};
struct full {uint32_t registers[2][32],pc,z,c,n,matrix_control,matrix_pointer,division_control,remainder,instructions,accumulator,hidata,flags,data_organization,control,active_bank;uint8_t local_RAM[4096];};
struct stats {uint64_t callbacks,known,uncovered,instructions,errors;uint32_t error_PC,error_code;};
static struct host H;static struct stats S;static int mode;static FILE *before_file,*after_file,*PC_file;static uint8_t raw_after[4416],private_after[20];static int use_private_after;
static uint32_t get32(const uint8_t*p){uint32_t v;memcpy(&v,p,4);return v;}static void set32(uint8_t*p,uint32_t v){memcpy(p,&v,4);}
static void unpack(const uint8_t*p,struct full*s){memcpy(s->local_RAM,p,4096);s->pc=get32(p+4096);s->accumulator=get32(p+4100);s->remainder=get32(p+4104);s->hidata=get32(p+4108);s->flags=get32(p+4112);s->matrix_control=get32(p+4116);s->matrix_pointer=get32(p+4120);s->data_organization=get32(p+4124);s->control=get32(p+4128);s->division_control=get32(p+4132);s->z=p[4136];s->n=p[4137];s->c=p[4138];memcpy(s->registers,p+4139,256);s->active_bank=p[4395];s->instructions=0;}
static void pack(uint8_t*p,const struct full*s){memcpy(p,s->local_RAM,4096);set32(p+4096,s->pc);set32(p+4100,s->accumulator);set32(p+4104,s->remainder);set32(p+4108,s->hidata);set32(p+4112,s->flags);set32(p+4116,s->matrix_control);set32(p+4120,s->matrix_pointer);set32(p+4124,s->data_organization);set32(p+4128,s->control);set32(p+4132,s->division_control);p[4136]=(uint8_t)s->z;p[4137]=(uint8_t)s->n;p[4138]=(uint8_t)s->c;memcpy(p+4139,s->registers,256);p[4395]=(uint8_t)s->active_bank;}
static int rd8(void*x,uint32_t a,uint8_t*p){(void)x;*p=H.read8(a,6);return 0;}static int rd16(void*x,uint32_t a,uint16_t*p){(void)x;*p=H.read16(a,6);return 0;}static int rd32(void*x,uint32_t a,uint32_t*p){(void)x;*p=H.read32(a,6);return 0;}static int wr16(void*x,uint32_t a,uint16_t v){(void)x;H.write16(a,v,6);return 0;}static int wr32(void*x,uint32_t a,uint32_t v){(void)x;H.write32(a,v,6);return 0;}static int blit(void*x,uint32_t a,uint32_t v,uint8_t*p){(void)x;memcpy(H.RAM(),p,4096);H.write32(a,v,6);memcpy(p,H.RAM(),4096);return 0;}
struct identity {uint8_t size,bytes[6];};
'''
    suffix='static const struct identity*maps[]={'+','.join('map_'+str(i)for i in range(len(programs)))+'};\nstatic int(*runs[])(struct full*)={'+','.join('run_'+str(i)for i in range(len(programs)))+'};\n'
    suffix+='''static int matches(unsigned k,unsigned slot,const uint8_t*raw,uint16_t opcode){const struct identity*p=&maps[k][slot];if(!p->size||memcmp(raw+slot*2,p->bytes,p->size))return 0;if((opcode>>10)==52||(opcode>>10)==53){const struct identity*d;if(slot+1>=2048)return 0;d=&maps[k][slot+1];if(!d->size||memcmp(raw+slot*2+2,d->bytes,d->size))return 0;}return 1;}
static int fail(uint32_t pc,uint32_t code){S.errors++;S.error_PC=pc;S.error_code=code;return -1;}
int biwn_fast_GPU_owner(uint32_t pc,uint16_t opcode,uint32_t unsupported){uint8_t raw[4416],hash[32],p[4];struct full s;unsigned k,slot;uint32_t count,operand;int status;S.callbacks++;if(S.errors)return -1;if(pc<0xf03000u||pc>=0xf04000u||(pc&1)){S.uncovered++;return 0;}slot=(pc-0xf03000u)/2;if(H.save(raw)!=4416)return fail(pc,91);if(maps[0][slot].size){if(!matches(0,slot,raw,opcode))return fail(pc,92);k=0;}else{for(k=1;k<sizeof(maps)/sizeof(maps[0]);k++)if(matches(k,slot,raw,opcode))break;if(k==sizeof(maps)/sizeof(maps[0])){S.uncovered++;return 0;}}S.known++;if(before_file){CC_SHA256(raw,4396,hash);if(fwrite(hash,1,32,before_file)!=32)return fail(pc,93);p[0]=(uint8_t)(pc>>24);p[1]=(uint8_t)(pc>>16);p[2]=(uint8_t)(pc>>8);p[3]=(uint8_t)pc;if(fwrite(p,1,4,PC_file)!=4)return fail(pc,94);}if(mode==1)return 0;if(unsupported)return fail(pc,100+unsupported);unpack(raw,&s);if(s.active_bank)return fail(pc,95);count=*H.counter;use_private_after=0;status=runs[k](&s);if(status)return fail(pc,200+(uint32_t)status);if(s.instructions<1||s.instructions>2)return fail(pc,96);if(*H.counter!=count)return fail(pc,97);if(use_private_after)memcpy(raw+4396,private_after,20);operand=opcode;if(s.instructions==2){if((opcode>>10)!=52&&(opcode>>10)!=53)return fail(pc,98);operand=((uint32_t)raw[slot*2+2]<<8)|raw[slot*2+3];}set32(raw+4396,opcode);set32(raw+4400,(operand>>5)&31);set32(raw+4404,operand&31);pack(raw,&s);if(H.load(raw)!=4416)return fail(pc,99);S.instructions+=s.instructions;if(after_file){CC_SHA256(raw,4396,hash);if(fwrite(hash,1,32,after_file)!=32)return fail(pc,93);}return 1;}
int biwn_fast_GPU_begin(const struct host*h,int m,const char*before,const char*after,const char*PC){if(!h||!h->save||!h->load||!h->read16||!h->read32||!h->write16||!h->write32||!h->read8||!h->RAM||!h->counter||(m!=1&&m!=2))return 1;H=*h;mode=m;memset(&S,0,sizeof(S));before_file=before?fopen(before,"wb"):NULL;after_file=after?fopen(after,"wb"):NULL;PC_file=PC?fopen(PC,"wb"):NULL;if((before&&!before_file)||(after&&!after_file)||(PC&&!PC_file)||((before_file!=NULL)!=(PC_file!=NULL)))return 2;return 0;}
const struct stats*biwn_fast_GPU_end(void){if(before_file)fclose(before_file);if(after_file)fclose(after_file);if(PC_file)fclose(PC_file);before_file=after_file=PC_file=NULL;return &S;}
size_t biwn_fast_GPU_host_size(void){return sizeof(struct host);}size_t biwn_fast_GPU_stats_size(void){return sizeof(struct stats);}
'''
    if any(p['kind']=='movie'for p in programs):
        old='if(maps[0][slot].size){if(!matches(0,slot,raw,opcode))return fail(pc,92);k=0;}'
        assert old in suffix
        suffix=suffix.replace(old,'if(matches(0,slot,raw,opcode)){k=0;}')
    if args.capture_unknown:
        capture='''static FILE *unknown_file;static uint32_t seen_pc[256];static uint8_t seen_bytes[256][6];static unsigned seen_count;
int biwn_fast_GPU_capture_unknown(const char *path){seen_count=0;unknown_file=fopen(path,"wb");return unknown_file?0:1;}
uint64_t biwn_fast_GPU_unknown_count(void){return S.uncovered;}
static int uncovered(uint32_t pc,uint16_t opcode){uint8_t raw[4416],header[6],identity[6]={0};unsigned i;S.uncovered++;if(unknown_file&&seen_count<256){if(H.save(raw)!=4416){S.errors++;return -1;}if(pc>=0xf03000u&&pc<=0xf03ffau)memcpy(identity,raw+pc-0xf03000u,6);else{identity[0]=(uint8_t)(opcode>>8);identity[1]=(uint8_t)opcode;}for(i=0;i<seen_count;i++)if(seen_pc[i]==pc&&!memcmp(seen_bytes[i],identity,6))return 0;seen_pc[seen_count]=pc;memcpy(seen_bytes[seen_count],identity,6);seen_count++;header[0]=(uint8_t)(pc>>24);header[1]=(uint8_t)(pc>>16);header[2]=(uint8_t)(pc>>8);header[3]=(uint8_t)pc;header[4]=(uint8_t)(opcode>>8);header[5]=(uint8_t)opcode;if(fwrite(header,1,6,unknown_file)!=6||fwrite(raw,1,4416,unknown_file)!=4416){S.errors++;return -1;}fflush(unknown_file);}return 0;}
'''
        assert suffix.count('S.uncovered++;return 0;')==2
        suffix=suffix.replace('S.uncovered++;return 0;','return uncovered(pc,opcode);')
        suffix=capture+suffix
        suffix=suffix.replace('if(before_file)fclose(before_file);','if(unknown_file){fclose(unknown_file);unknown_file=NULL;}if(before_file)fclose(before_file);')
    body=prefix+'\n'.join(includes+tables+wrappers)+'\n'+suffix;source=out/'fast_GPU_bridge.c';source.write_text(body);library=out/'libfast-GPU-bridge.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),*libraries,'-o',str(library)]
    p=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    report=dict(status='compiled_unverified',directory=str(out),library=str(library),source_sha256=hashlib.sha256(body.encode()).hexdigest(),programs=[{k:v for k,v in p.items()if k not in ['type','instructions_decoded','ABI_checks']}for p in programs],whole_game_complete=False,new_training=False,coordinator_authored=True)
    report['capture_unknown']=args.capture_unknown
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(args.candidate_output or ROOT/'verification/fast-GPU-bridge-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(programs))
if __name__=='__main__':main()

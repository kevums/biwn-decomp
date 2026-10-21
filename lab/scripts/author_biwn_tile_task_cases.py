"""Fresh grounded local switch cases with coordinator checked ABI scaffolding."""
import fcntl,json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import lmstudio,sdk_thinking_override_probe
sdk_thinking_override_probe.install();out=ROOT/'verification/BIWN-tile-task-local-author'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
prefix='''#include "biwn_world_cpu.h"
#include <stddef.h>
struct task {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;};
static void bank(struct task*s){if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];}
static int rd16(struct task*s,uint32_t a,uint16_t*v){return s->bus->read16(s->bus->context,a,v)?2:0;}
static int rd32(struct task*s,uint32_t a,uint32_t*v){return s->bus->read32(s->bus->context,a,v)?2:0;}
static int push32(struct task*s,uint32_t v){s->cpu.registers[15]-=4;bank(s);return s->bus->write32(s->bus->context,s->cpu.registers[15],v)?2:0;}
static int pop32(struct task*s,uint32_t*v){int e=rd32(s,s->cpu.registers[15],v);if(e)return e;s->cpu.registers[15]+=4;bank(s);return 0;}
static void cmp16(struct task*s,uint16_t operand,uint16_t immediate){uint16_t r=(uint16_t)(operand-immediate);s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(r&0x8000u?8u:0u)|(r?0u:4u)|(((operand^immediate)&(operand^r)&0x8000u)?2u:0u)|(operand<immediate?1u:0u));}
#define CHECK(e) do{int error=(e);if(error)return error;}while(0)
int biwn_tile_task_cpu_run(struct biwn_world_bus*bus,struct biwn_task_cpu*state,uint32_t budget){struct task s;uint32_t value;uint16_t word;
 if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write32)return 1;s.bus=bus;s.cpu=*state;
 while(budget--){switch(s.cpu.pc){
'''
suffix='''default:return 7;}}return 4;}
'''
prompt='''Generate ONLY one fenced C code block containing13case labels for this supplied switch. No function/includes/helpers/default. Use only existing helpers and s.cpu fields. Avoid independent register caches. DO NOT reuse prior incorrect drafts.
Helpers: CHECK(rd16(&s,address,&word)); cmp16(&s,word,immediate) calculates word-minus-immediate and preservesX/upperSR. CHECK(push32(&s,value)) updates A7slot15 and activeUSP/SSP then writes long. CHECK(pop32(&s,&value)) reads long, updatesA7/bank. bank(&s) after directSPchange. Variables word(uint16_t),value(uint32_t) alreadydeclared. Allregisters/flags initiallycopied. CCR Z MASK4(bit2), X MASK16(bit4),N8,V2,C1. BNE when(s.cpu.sr&4)==0; BEQ when(s.cpu.sr&4)!=0. JSR transitions do not call host services.
Exact13 source cases:
21D1A read16(49C60),cmp16(word,1),PC21D22
21D22 BNE:PC21D2A ifZclear else21D24
21D24 push32(21D2A),PC212E8
21D2A push32(21D30),PCDF60,commit*state=s.cpu,return6
21D30 PC21D1A (BRA,flagsunchanged)
212E8 A7-=28u;bank;PC212EC (ADDA.W#FFE4,noCCRchange)
212EC MOVEM predecrement:forregisterindices14,13,12,11,10,7,6,5,4,3,2 push32(s.cpu.registers[index]);PC212F0
212F0 s.cpu.registers[8]=49C8C;PC212F6 (LEA,noCCRchange)
212F6 read16(s.cpu.registers[8]),cmp16(word,12),PC212FA
212FA ifZsetPC21D10; else return7 (other tilecode unported)
21D10 MOVEM postincrement:forindices2,3,4,5,6,7,10,11,12,13,14 pop32 into value then assignregister[index];PC21D14
21D14 A7+=28u;bank;PC21D18 (noCCRchange)
21D18 pop32 to value,PC=value (RTS,noCCRchange)
Allnonterminal cases endbreak. Keep sourceframes/effects, only commit atyield6. Guardeddisabledmode or tile12 paths; alternate tiles unported.
'''
record=dict(status='draft_pending',role='local Code Author',model='advertising-scholar',system='Write exact grounded C switch cases. Use supplied helpers verbatim. Do not invent instruction semantics, register mappings, helper names, or verification.',user=prompt,coordinator_prefix=prefix,coordinator_suffix=suffix,model_authorship='13switchcases only; coordinator verifiedABI/flag/stack helpers and loop scaffolding.',new_training=False,independent_model_verification=False)
(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n')
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['status']=='idle'
 chat=lmstudio.Chat(record['system']);chat.add_user_message(prompt);response=lmstudio.llm('advertising-scholar').respond(chat,config={'temperature':0.1,'maxTokens':2048,'raw':{'fields':[{'key':'llm.prediction.reasoning.enableThinking','value':False},{'key':'ext.virtualModel.customField.enableThinking','value':False},{'key':'ext.virtualModel.customField.preserveThinking','value':False}]}})
 raw=response.content;(out/'raw-response.txt').write_text(raw);assert raw.count('```')==2 and '```c'in raw;cases=raw.split('```c',1)[1].split('```',1)[0].strip()+'\n';(out/'model-cases.cfrag').write_text(cases);(out/'candidate.c').write_text(prefix+cases+suffix);record.update(status='grounded_cases_returned_unverified',raw_response=raw,directory=str(out));(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(ROOT/'verification/tile-task-local-author-current.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'],flush=True)

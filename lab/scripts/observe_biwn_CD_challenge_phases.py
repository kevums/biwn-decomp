"""Continue original CPU/DSP handshakes in the existing live firmware run.

No state restoration, header/payload injection, or physical timing claim.
Imported lazily by the firmware observer after the source reaches50BE2.
"""
import ctypes as c
import hashlib,struct,json
from collections import Counter
import capstone

def DSP_phase(host,runtime,out,label,args,mailbox,descriptor,CD_period_CPU,cycle_us,ack_requires_pc=None):
    out.mkdir();buffer=c.create_string_buffer(12000)
    assert runtime.savers['DSP'](buffer)==8729;initial=buffer.raw[:8729]
    (out/'DSP-before.bin').write_bytes(initial);CPU=bytes(runtime.cpu())
    counter=c.c_uint32.in_dll(runtime.core,'dsp_exec_opcode_count');start=counter.value
    costs=(c.c_uint8*64).in_dll(runtime.core,'dsp_opcode_cycles')
    counts=Counter();trace=hashlib.sha256();byte_trace=hashlib.sha256()
    blocks=delays=CD_ticks=SSI_events=cycles=0;CD_rem=SSI_rem=0.0;stop='budget';marker_comparisons=marker_matches=0;marker_samples=[]
    for i in range(args.third_DSP_budget):
        flag=runtime.core.DSPReadLong(mailbox,0)
        done=(not flag&0x80000000 and not runtime.core.DSPReadLong(0xf1a100,0)&8)if descriptor else bool(flag&0x80000000)
        witnessed=ack_requires_pc is None or any(key[0]==ack_requires_pc for key in counts)
        if done and blocks and witnessed:stop='source_descriptor_completed_after_IRQ_return'if descriptor else 'source_DSP_command_acknowledged';break
        if not runtime.core.DSPReadLong(0xf1a114,0)&1:stop='source_DSP_GO_cleared';break
        pc=runtime.core.DSPGetPC()
        if not 0xf1b000<=pc<0xf1d000:stop='outside_DSP_local_RAM';break
        if pc==0xf1b3f2:
            assert runtime.savers['DSP'](buffer)==8729;sample=buffer.raw[:8729];values=struct.unpack_from('=64I',sample,8239);bank=sample[8495];base=bank*32
            marker_comparisons+=1;equal=values[base+16]==values[base+25];marker_matches+=int(equal)
            if len(marker_samples)<24 or equal:
                if len(marker_samples)<96:marker_samples.append(dict(comparison=marker_comparisons,bank=bank,received_word=hex(values[base+16]),target_word=hex(values[base+25]),scan_counter=values[base+19],remaining_marker_words=values[base+23],equal=equal))
        pointer=runtime.core.DSPGetRAM()+pc-0xf1b000;raw=c.string_at(pointer,6);opcode=int.from_bytes(raw[:2],'big')>>10
        payload=raw[:6 if opcode==38 else 2];delay_raw=c.string_at(pointer+2,6)
        counts[(pc,payload)]+=1;trace.update(struct.pack('>I',pc));byte_trace.update(struct.pack('>I',pc)+payload)
        before=counter.value;runtime.core.DSPExec(1);blocks+=1;consumed=(counter.value-before)&0xffffffff
        if consumed>1 and opcode in [52,53]:
            payload=delay_raw[:6 if int.from_bytes(delay_raw[:2],'big')>>10==38 else 2]
            counts[(pc+2,payload)]+=1;trace.update(struct.pack('>I',pc+2));byte_trace.update(struct.pack('>I',pc+2)+payload);delays+=1
        elapsed=int(costs[opcode]);cycles+=elapsed;CD_rem+=elapsed;SSI_rem+=elapsed
        while CD_rem>=CD_period_CPU*2:runtime.core.BUTCHExec(0);CD_ticks+=1;CD_rem-=CD_period_CPU*2
        mode,divider=host.SSI_clock_registers(runtime)
        period=64*(divider+1)if mode&1 else 22.675737/(cycle_us/2)
        while SSI_rem>=period:
            host.deliver_SSI(runtime,args.SSI_receive_word_swap_diagnostic,args.SSI_previous_right_word_diagnostic);SSI_events+=1;SSI_rem-=period
        if i and i%500000==0:print(json.dumps(dict(phase=label,blocks=i,PC=hex(runtime.core.DSPGetPC()),flag=hex(flag),SSI=SSI_events)),flush=True)
    assert runtime.savers['DSP'](buffer)==8729;after=buffer.raw[:8729];RAM=runtime.device.ram()
    (out/'DSP-after.bin').write_bytes(after);(out/'RAM-after-DSP.bin').write_bytes(RAM)
    report=dict(label=label,status='original_DSP_discovery',stop_reason=stop,mailbox=hex(mailbox),initial_PC=hex(struct.unpack_from('=I',initial,8192)[0]),final_PC=hex(runtime.core.DSPGetPC()),final_mailbox=hex(runtime.core.DSPReadLong(mailbox,0)),instructions=(counter.value-start)&0xffffffff,execution_blocks=blocks,observed_branch_delays=delays,CD_clock_ticks=CD_ticks,SSI_events=SSI_events,pinned_outer_opcode_cycles=cycles,CPU_unchanged=bytes(runtime.cpu())==CPU,logical_DSP_sha256=host.sha(after[:8496]),RAM_sha256=host.sha(RAM),PC_trace_sha256=trace.hexdigest(),instruction_byte_trace_sha256=byte_trace.hexdigest(),visited_instructions=[{**host.generation.loader.base.binary_tools.jaguar_instructions(raw,pc,'dsp')[0][0],'count':count}for(pc,raw),count in sorted(counts.items())],marker_comparisons=marker_comparisons,marker_matches=marker_matches,marker_samples=marker_samples,source_C_verified=False,hardware_timing_verified=False,host_payload_copy=False,scope='Original DSPExec1 boundary PCs/detected branch delays with pinned partial CD/SSI clocks and selected explicit receive provider. CPU/GPU/video/PIT/bus stalls held; no global/physical timing proof.')
    host.save(out/'DSP-report.json',report);return report

def CPU_phase(host,runtime,out,args,CD_period_CPU,CD_remainder,stop_at=None,allow_CD_seek_wait=False):
    decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    initial=host.media.scheduler.cpu_dict(runtime.cpu());counts=Counter();seen=Counter();rows={};trace=hashlib.sha256();cycles=ticks=0;stop='budget'
    for i in range(args.CPU_continuation_budget):
        cpu=runtime.cpu();pc=cpu.pc
        if pc==stop_at:stop='source_fourth_DSP_GO_started_before_command';break
        seen[bytes(cpu)]+=1
        if seen[bytes(cpu)]>=64 and not (allow_CD_seek_wait and pc in [0x3544,0x354a,0x354e]):stop='repeated_exact_CPU_state_with_DSP_GPU_held';break
        if pc<0x200000:raw=c.string_at(runtime.device.pointer+pc,32)
        elif 0x800000<=pc<0x840000:raw=runtime.bios[pc-0x800000:pc-0x800000+32]
        else:stop='outside_mapped_RAM_userROM';break
        decoded=next(decoder.disasm(raw,pc,count=1),None)
        if decoded is None:stop='undecodable_instruction';break
        key=(pc,raw[:decoded.size].hex());rows[key]=dict(address=pc,size=decoded.size,bytes=key[1],assembly=decoded.mnemonic+' '+decoded.op_str)
        counts[key]+=1;trace.update(struct.pack('>I',pc));elapsed=runtime.core.m68k_execute(1);cycles+=elapsed;CD_remainder+=elapsed
        while CD_remainder>=CD_period_CPU:runtime.core.BUTCHExec(0);ticks+=1;CD_remainder-=CD_period_CPU
    RAM=runtime.device.ram();buffer=c.create_string_buffer(12000);assert runtime.savers['DSP'](buffer)==8729
    (out/'RAM-after-CPU.bin').write_bytes(RAM);(out/'DSP-after-CPU.bin').write_bytes(buffer.raw[:8729])
    report=dict(status='original_CPU_discovery',stop_reason=stop,steps=sum(counts.values()),initial_CPU=initial,final_CPU=host.media.scheduler.cpu_dict(runtime.cpu()),PC_trace_sha256=trace.hexdigest(),RAM_sha256=host.sha(RAM),returned_CPU_cycles=cycles,CD_clock_ticks=ticks,visited_instructions=[{**rows[key],'count':count}for key,count in sorted(counts.items())],CPU_reseeded=False,source_C_verified=False,host_payload_copy=False,hardware_timing_verified=False,known_CD_seek_wait_allowed=allow_CD_seek_wait)
    host.save(out/'CPU-report.json',report);return report,CD_remainder

def advance(host,runtime,out,args,CD_period_CPU,cycle_us,CD_remainder):
    phases=[];stop='phase_budget'
    for i in range(args.advance_CD_challenge_phases):
        command=runtime.core.DSPReadLong(0xf1b4c8,0);descriptor=runtime.core.DSPReadLong(0xf1b4a4,0)
        if not command&0x80000000:mailbox=0xf1b4c8;is_descriptor=False;kind='command'
        elif descriptor&0x80000000:mailbox=0xf1b4a4;is_descriptor=True;kind='descriptor'
        else:stop='no_pending_known_DSP_mailbox';break
        folder=out/f'challenge-phase-{i:02d}-{kind}'
        d=DSP_phase(host,runtime,folder,folder.name,args,mailbox,is_descriptor,CD_period_CPU,cycle_us)
        row=dict(directory=str(folder),DSP=d);phases.append(row)
        source_stop_completed=(not is_descriptor and command==0 and d['stop_reason']=='source_DSP_GO_cleared')
        if not source_stop_completed and not d['stop_reason'].startswith(('source_DSP_command_acknowledged','source_descriptor_completed')):stop=d['stop_reason'];break
        cpu,CD_remainder=CPU_phase(host,runtime,folder,args,CD_period_CPU,CD_remainder,0x50d98 if source_stop_completed and args.initialize_fourth_DSP_at_source_GO else None);row['CPU']=cpu
        print(json.dumps(dict(phase=i,DSP_instructions=d['instructions'],CPU_steps=cpu['steps'],CPU_PC=hex(cpu['final_CPU']['pc']))),flush=True)
        host.save(out/'challenge-phases.json',dict(phases=phases,stop_reason='running'))
        if source_stop_completed:stop='source_DSP_stopped_then_CPU_continued';break
    result=dict(status='bounded_original_CD_challenge_discovery',phases=phases,stop_reason=stop,final_CPU=host.media.scheduler.cpu_dict(runtime.cpu()),source_C_verified=False,full_boot_verified=False,host_payload_copy=False)
    host.save(out/'challenge-phases.json',result);return result,CD_remainder


def advance_fourth(host,runtime,out,args,CD_period_CPU,cycle_us,CD_remainder):
    if getattr(args,'fourth_DSP_budget',None):
        from argparse import Namespace
        args=Namespace(**vars(args));args.third_DSP_budget=args.fourth_DSP_budget
    phases=[];stop='phase_budget'
    for i in range(args.advance_fourth_DSP_phases):
        command=runtime.core.DSPReadLong(0xf1b020,0);reply=runtime.core.DSPReadLong(0xf1b3f8,0)
        if not command&0x80000000:mailbox=0xf1b020;is_reply=False;kind='command'
        elif reply&0x80000000 and runtime.core.DSPReadLong(0xf1a114,0)&0x40:mailbox=0xf1b3f8;is_reply=True;kind='CPU-IRQ'
        else:stop='no_pending_fourth_DSP_mailbox';break
        folder=out/f'fourth-phase-{i:02d}-{kind}'
        d=DSP_phase(host,runtime,folder,folder.name,args,mailbox,is_reply,CD_period_CPU,cycle_us)
        row=dict(directory=str(folder),DSP=d);phases.append(row)
        stopped=(not is_reply and d['stop_reason']=='source_DSP_GO_cleared')
        if not stopped and not d['stop_reason'].startswith(('source_DSP_command_acknowledged','source_descriptor_completed')):stop=d['stop_reason'];break
        cpu,CD_remainder=CPU_phase(host,runtime,folder,args,CD_period_CPU,CD_remainder);row['CPU']=cpu
        print(json.dumps(dict(fourth_phase=i,DSP_instructions=d['instructions'],CPU_steps=cpu['steps'],CPU_PC=hex(cpu['final_CPU']['pc']))),flush=True)
        host.save(out/'fourth-phases.json',dict(phases=phases,stop_reason='running'))
        if stopped:stop='fourth_DSP_stopped_then_CPU_continued';break
    result=dict(status='bounded_original_fourth_DSP_discovery',phases=phases,stop_reason=stop,final_CPU=host.media.scheduler.cpu_dict(runtime.cpu()),source_C_verified=False,full_boot_verified=False,host_payload_copy=False)
    host.save(out/'fourth-phases.json',result);return result,CD_remainder


def advance_after_auth_video(host,runtime,out,args,CD_period_CPU,CD_remainder):
    rows=[]
    runtime.core.TOMSetPendingVideoInt.argtypes=[]
    runtime.core.m68k_set_irq2.argtypes=[c.c_uint]
    for i in range(args.post_auth_video_events):
        before=host.media.scheduler.cpu_dict(runtime.cpu())
        counter_before=int.from_bytes(runtime.device.ram()[0x1ae4d2:0x1ae4d4],'big')
        runtime.core.TOMSetPendingVideoInt();runtime.core.m68k_set_irq2(2)
        entry=host.media.scheduler.cpu_dict(runtime.cpu())
        vector=int.from_bytes(runtime.device.ram()[0x100:0x104],'big');assert entry['pc']==vector
        folder=out/f'post-auth-video-{i:02d}';folder.mkdir()
        cpu,CD_remainder=CPU_phase(host,runtime,folder,args,CD_period_CPU,CD_remainder,allow_CD_seek_wait=True)
        row=dict(event=i+1,CPU_before=before,exception_entry=entry,CPU=cpu,video_counter_before=counter_before,video_counter_after=int.from_bytes(runtime.device.ram()[0x1ae4d2:0x1ae4d4],'big'),source_vector=hex(vector),host_counter_write=False,CPU_reseeded=False,physical_VBI_period_verified=False)
        rows.append(row);host.save(out/'post-auth-video.json',dict(events=rows,status='running'));print(json.dumps(dict(post_auth_video=i+1,steps=cpu['steps'],PC=hex(cpu['final_CPU']['pc']),counter=row['video_counter_after'])),flush=True)
        if cpu['final_CPU']['pc']!=0x50f40:break
    result=dict(status='bounded_original_CPU_after_explicit_VBI',events=rows,final_CPU=host.media.scheduler.cpu_dict(runtime.cpu()),host_counter_or_payload_write=False,whole_boot=False,source_C_verified=False,scope='Live source CPU/RAM state, supplied TOM VBI and real exception entry; native source handler/continuation. GPU/DSP held during handler; no physical/global clock proof.')
    host.save(out/'post-auth-video.json',result);return result,CD_remainder

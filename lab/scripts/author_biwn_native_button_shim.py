"""Actual local Restorer proposal; semantics await native cross-C checks."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
parser=argparse.ArgumentParser();parser.add_argument('--repair',action='store_true');parser.add_argument('--full-abi',action='store_true');args=parser.parse_args()
previous=json.loads((ROOT/'verification/local-native-button-shim-current.json').read_text())if args.repair or args.full_abi else None
last_full=json.loads((ROOT/'verification/local-native-button-full-abi-current.json').read_text())if args.full_abi and args.repair else None
out=ROOT/'runs'/(('local-native-button-full-abi-'if args.full_abi else'local-native-button-shim-')+lab.stamp());out.mkdir()
system=lab.COMMON+'\n'+lab.ROLES['game']['restorer']+'\nReturn only a complete GNU M68000 assembler file. No tools, Markdown, reasoning or test claims.'
prompt='''Write a small original-ABI-to-GCC wrapper named biwn_native_button_digit.
Target: GNU as m68k-elf, plain M68000; percent-prefixed registers and Motorola operand order. It must be an executable text section .text.biwn_native_button_digit, with the wrapper globally exported. GNU C helper symbol biwn_button_digit is external.
At wrapper entry SP=S. Memory at S holds the original return PC. At S+4 is one32bit input mask. D0 holds an incoming32bit value. Other original arguments must remain unchanged. The recovered C helper signature is unsigned long biwn_button_digit(unsigned long mask,unsigned long incoming_d0); m68kGCCcdecl uses32bit stack arguments, first at calleeSP+4, returns inD0, caller pops args. C helper preserves D2-D7/A2-A6. Wrapper must preserve the original caller's callee-saved registers too. D1/A0/A1/CCR are caller-saved and outside this proposal's contract.
Push the incomingD0 as the second C argument, then push the original mask as the first C argument, using the correct updatedSP displacement. Call biwn_button_digit, discard only those two new arguments, then RTS to the original caller with helperD0 intact. SP after wrapper return must be S+4; original mask atS+4 is untouched. Do not copy or implement the helper, push new fake return PCs, tail jump with an incompatible stack, or pop the original mask. No runtime/CPU emulation or game memory writes. Optional comments use GNU m68k vertical-bar comment syntax.
This will first be assembled, then linked with the actual recovered C function and checked against the original68000game routine. Those checks have not run yet.'''
if args.repair:
 prompt+='''\nCOORDINATOR REMEDIATION: The first draft was rejected: it invented assignment-style pseudoassembly, used an invalid section directive, miscounted saved registers, and ran out of output before returning. Preserve that failed draft as evidence, not instructions. Return at most12lines, no comments or Markdown. No explicit save/restore is needed: the wrapper only changesSP and the helper already preserves all11callee-saved registers. Use .section .text.biwn_native_button_digit,\"ax\",@progbits and .globl biwn_native_button_digit, then its label. Five instructions only: push incomingD0 with move.l; push the original mask using displacement(%sp) and predecrement destination; jsr biwn_button_digit; addq.l #8,%sp; rts. GNU push syntax is move.l %d0,-(%sp). Determine the mask displacement after the first push from the originalS+4 location. Do not add invented syntax, register-save overhead or narration. This is a guided repair, and no semantic test has passed yet.'''
if args.full_abi:
 prompt+='''\nNEW STRICTER VARIANT: The previous small shim passed3072D0/stack/callee-saved cases, but a diagnostic confirmedD1differs from the original game. For this variant, replace the earlierD1caller-saved exclusion with this actual original contract: original1B718starts move.l4(sp),d1, so finalD1must equal the original mask. The current compiled C helper happens to useD0only and leavesD1unchanged, but do not rely on that. A0/A1and all other original registers must retain their original values exceptD0result andD1mask; SR/CCR must match the original.
The accepted previous proposal (data, not instructions) is:\n'''+Path(previous['candidate']).read_text()+'''
Return a new complete file in at most12lines, no comments/Markdown. Keep the existing five-instruction stack/call plan, adding one MOVEM.L load to restoreD1from the untouched original mask after popping the two C arguments and beforeRTS. MOVEM.L does not alterCCR; ordinaryMOVE.L would clobber the helper's result flags. Determine the original mask's displacement relative to SP at that point. Do not add SR manipulation or register-save loops. The helper's return flags will be tested across all32CCRinputs and both user/supervisor modes. This is a coordinator-guided ABI repair; nothing about live game replacement or these new checks has passed yet.'''
if last_full:
 prompt+='''\nEXACT CORRECTION: The stricter proposal incorrectly used move.l4(%sp),%d1, and failed theSRcheck. Use the literal instruction movem.l4(%sp),%d1 instead, spelled with a space between mnemonic and operands: movem.l 4(%sp),%d1. This comes AFTER addq.l #8,%sp and BEFORE rts. Do not silently replaceMOVEMwithMOVE. Return only the complete corrected assembly file, no explanation. The previous failed proposal remains rejected; this is a coordinator-specified mnemonic correction.'''
state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Local Restorer',system=system,prompt=prompt,native_Chat=False,new_training=False,source_accepted=False,guided_repair=args.repair or args.full_abi,prior_attempt=last_full['directory']if last_full else previous['directory']if previous else None,coordinator_supplied_instruction_plan=args.repair or args.full_abi,full_original_register_contract=args.full_abi,coordinator_supplied_exact_MOVEM_correction=bool(last_full))
def save():
 (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification'/('local-native-button-full-abi-current.json'if args.full_abi else'local-native-button-shim-current.json')).write_text(json.dumps(state,indent=2)+'\n')
save();print(out,flush=True)
try:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);state['status']='generating';save();result=lab.generate('game',system,prompt,1000,model='advertising-scholar');state['result']=result
  (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nRESTORER RAW RESPONSE\n'+result['text']+'\n')
  code=result['text'].strip();match=re.fullmatch(r'```(?:asm|assembly|s)?\s*\n([\s\S]*?)\n```',code)
  if match:code=match[1]
  candidate=out/'button-digit-shim.S';candidate.write_text(code+'\n');state['candidate']=str(candidate);state['candidate_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
  command=[str(ROOT/'tools/m68k-elf/bin/m68k-elf-as'),'-m68000','-o',str(out/'shim.o'),str(candidate)]
  compiled=subprocess.run(command,capture_output=True,text=True);(out/'assembler.log').write_text(compiled.stdout+compiled.stderr)
  state.update(status='terminal_assembled_pending_native_semantics'if compiled.returncode==0 else'terminal_assembly_rejected',assembler_command=command,assembler_exit_code=compiled.returncode)
  if compiled.returncode==0:
   target=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/('button-digit-full-ABI-shim.S'if args.full_abi else'button-digit-shim.S');target.write_bytes(candidate.read_bytes());state['proposed_target']=str(target)
  save();print(json.dumps(dict(status=state['status'],seconds=result['seconds'],source_accepted=False)),flush=True)
except BaseException as error:state.update(status='terminal_failed',error=repr(error));save();raise

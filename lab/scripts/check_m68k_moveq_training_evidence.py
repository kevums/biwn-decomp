"""Synthetic native M68000 flags evidence for correcting prior model failure."""
import json
from pathlib import Path
import check_biwn_scheduler as scheduler
ROOT=scheduler.ROOT;run=scheduler.Native();core=run.lib;rows=[]
try:
 for immediate in [42,0,-1,-128]:
  for X in [0,1]:
   ram=bytearray(0x200000);code=bytes([0x70,immediate&255,0x4e,0x75]);ram[0x1000:0x1004]=code;ram[0x1ff000:0x1ff004]=(0x1ffff0).to_bytes(4,'big');run.device.seed(bytes(ram),0);core.m68k_pulse_reset();core.m68k_set_irq(0);core.m68k_set_reg(17,0x270f|(X<<4));core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(0,0x12345678);core.m68k_set_reg(16,0x1000)
   for i in range(16):
    if core.m68k_get_reg(None,16)==0x1ffff0:break
    core.m68k_execute(1)
   else:raise AssertionError('RTS did not return')
   value=core.m68k_get_reg(None,0);sr=core.m68k_get_reg(None,17);expected=(immediate&0xffffffff);CCR=(X<<4)|(8 if immediate<0 else 0)|(4 if immediate==0 else 0);assert value==expected and sr&31==CCR
   rows.append(dict(bytes_hex=code.hex(),immediate=immediate,initial_X=X,D0=hex(value),SR=hex(sr),N=bool(sr&8),Z=bool(sr&4),V=bool(sr&2),C=bool(sr&1),X=bool(sr&16),RTS_return_verified=True))
 report=dict(status='native_synthetic_MOVEQ_RTS_flags_checked',cases=rows,case_count=8,primary_reference='https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf',reference_PDF_page=238,scope='Synthetic private RAM/stack and CPU seed; no whole game or hardware proof. These native tests report flags; the public verify_68000_fixture tool does not.',new_model_training=False)
 (ROOT/'verification/MOVEQ-training-evidence.json').write_text(json.dumps(report,indent=2)+'\n');print('8 native MOVEQ/RTS cases passed, both X inputs preserved')
finally:run.close()

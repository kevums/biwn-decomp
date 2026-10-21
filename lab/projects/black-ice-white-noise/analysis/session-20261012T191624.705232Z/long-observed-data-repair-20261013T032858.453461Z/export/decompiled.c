/* Ghidra approximation. Not original source; validate against binary behavior. */
/* Language: 68000:BE:32:BIWN_DIVU_CANDIDATE */
/* Address 00004000 */

/* WARNING: This function may have set the stack pointer */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void operator_selected_entry(void)

{
  _DAT_00f0210c = &DAT_00070007;
  _DAT_00f02100 = 0;
  _DAT_00f02114 = 0;
  _DAT_00f1a10c = &DAT_00070007;
  _DAT_00f1a100 = 0;
  _DAT_00f1a114 = 0;
  _DAT_00f14000 = 0x100;
  _DAT_00f10000 = 0;
  _DAT_00f10002 = 0;
  DAT_000778cc = 0;
  _DAT_001ffffc = 0x4058;
  FUN_0000dff4();
  _DAT_001ffffc = 0x405e;
  FUN_0000d340();
  _DAT_001ffffc = 0x4064;
  FUN_0000e6a0();
  _DAT_001ffffc = 0x406a;
  FUN_0000e00a();
  _DAT_001ffffc = 0x4070;
  FUN_0001557a();
  _DAT_001ffffc = 0x4076;
  FUN_00017340();
  _DAT_001ffffc = 0x407c;
  FUN_0000e942();
  _DAT_001ffffc = 0x4082;
  FUN_0000e7aa();
  FUN_0000dd40();
  return;
}


/* Address 0000d1e0 */

/* WARNING: Unknown calling convention */
/* Analyst-assigned name and register signature. Original nonzero-divisor CPU routine checked
   against 296 fixtures. D2 preserved. Zero-divisor trap and full flags ABI excluded. Upstream DIVU
   semantics are unsuitable; use the separate candidate language or reviewed portable C. */

uint analyst_u32_div_u16(ushort divisor,uint numerator)

{
  uint uVar1;
  uint uVar2;
  
  if (0xffff < numerator / divisor) {
    uVar1 = numerator >> 0x10;
    uVar2 = uVar1 / divisor;
    if (uVar2 < 0x10000) {
      uVar1 = uVar1 % (uint)divisor << 0x10 | uVar2;
    }
    uVar2 = uVar1 & 0xffff0000 | numerator & 0xffff;
    if (uVar2 / divisor < 0x10000) {
      uVar2 = uVar2 / divisor & 0xffff;
    }
    return CONCAT22((short)uVar1,(short)uVar2);
  }
  return numerator / divisor & 0xffff;
}


/* Address 0000d206 */

/* WARNING: Unknown calling convention */
/* Analyst-assigned name and local signature from actual stack reads and CPU fixtures. Selector is
   adjusted while scanning zero-session entries; it is not an unconditional track number. 174
   supplied-TOC fixtures checked. Actual BIOS TOC and CD execution unverified. */

uint analyst_cd_offset_msf(uint selector,uint byte_offset)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  char cVar4;
  char cVar5;
  ushort *puVar6;
  ushort *puVar7;
  
  uVar2 = analyst_u32_div_u16(0x930,byte_offset);
  if (uVar2 / 0x4b < 0x10000) {
    uVar2 = uVar2 % 0x4b << 0x10 | uVar2 / 0x4b & 0xffff;
  }
  uVar3 = uVar2 & 0xffff;
  if (uVar3 / 0x3c < 0x10000) {
    uVar3 = uVar3 % 0x3c << 0x10 | uVar3 / 0x3c;
  }
  puVar6 = (ushort *)0x2c00;
  do {
    puVar7 = puVar6;
    puVar6 = puVar7 + 4;
    if (*(char *)(puVar7 + 6) == '\0') {
      selector = (uint)(ushort)((short)selector + 1);
    }
  } while (*(char *)puVar6 != (char)selector);
  uVar1 = *puVar6 & 0xff;
  cVar4 = (char)(puVar7[5] >> 8);
  cVar5 = (char)(uVar2 >> 0x10) + (char)puVar7[5];
  if (-1 < (char)(cVar5 + -0x4b)) {
    cVar5 = cVar5 + -0x4b;
    cVar4 = cVar4 + '\x01';
  }
  cVar4 = ((byte)(uVar3 >> 0x10) | (byte)(uVar2 >> 0x18)) + cVar4;
  if (-1 < (char)(cVar4 + -0x3c)) {
    cVar4 = cVar4 + -0x3c;
    uVar1 = uVar1 + 1;
  }
  uVar2 = CONCAT22(CONCAT11((char)(uVar1 >> 8),(char)uVar3 + (char)uVar1),CONCAT11(cVar4,cVar5)) - 6
  ;
  uVar3 = uVar2;
  if ((char)uVar2 < '\0') {
    uVar3 = CONCAT31((int3)(uVar2 >> 8),(char)uVar2 + 'K');
    if ((short)uVar3 < 0) {
      uVar3 = CONCAT22((short)(uVar2 >> 0x10),(short)uVar3 + 0x3c00);
    }
  }
  return uVar3;
}


/* Address 0000d2a0 */

/* WARNING: Control flow encountered bad instruction data */

void FUN_0000d2a0(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* Address 0000d2f0 */

void FUN_0000d2f0(void)

{
  func_0x0000303c();
  return;
}


/* Address 0000d306 */

/* WARNING: Control flow encountered bad instruction data */

void thunk_EXT_FUN_00003042(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* Address 0000d340 */

/* WARNING: Removing unreachable block (ram,0x0000d38c) */
/* WARNING: Removing unreachable block (ram,0x0000d3a2) */
/* WARNING: Removing unreachable block (ram,0x0000d3ac) */

void FUN_0000d340(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  puVar1 = (undefined4 *)&DAT_00f03258;
  puVar2 = &DAT_00021ec0;
  do {
    puVar3 = puVar2 + 1;
    *puVar1 = *puVar2;
    puVar1 = puVar1 + 1;
    puVar2 = puVar3;
  } while (puVar3 != (undefined4 *)0x22770);
  do {
  } while( true );
}


/* Address 0000d3c6 */

void FUN_0000d3c6(void)

{
  uint uVar1;
  short sVar2;
  
  FUN_0000e098();
  shared_word_00f03204_candidate = 0x21ea0;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x21ea0);
  sVar2 = 10000;
  do {
    sVar2 = sVar2 + -1;
  } while (sVar2 != -1);
  return;
}


/* Address 0000d3ec */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000d3ec(void)

{
  _DAT_00f02114 = 5;
  return;
}


/* Address 0000d3fc */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000d3fc(undefined4 param_1,undefined4 param_2,undefined2 param_3,undefined2 param_4,
                 undefined4 param_5,int param_6,undefined4 param_7)

{
  FUN_0000dc7c();
  _DAT_00047b82 = 1;
  while (_DAT_00047b80 != 0) {
    __m68k_trap(0);
  }
  DAT_000bd884 = 0x1c0000;
  DAT_000bd888 = 0x1ffc00;
  FUN_0000e840();
  FUN_0000d3c6();
  DAT_000c0904 = 0;
  DAT_000bd890 = param_1;
  DAT_000bd894 = param_2;
  DAT_000bd88c = DAT_000bd830;
  DAT_000bd8ac = param_5;
  DAT_000bd900 = param_6 << 1;
  DAT_000bd898 = param_7;
  DAT_000bd85c = 0;
  do {
    FUN_0000d4a8();
  } while (DAT_000bd85c != -1);
  FUN_0000d3ec();
  _DAT_00047b82 = 0;
  return;
}


/* Address 0000d4a8 */

undefined4 FUN_0000d4a8(void)

{
  undefined4 in_D0;
  
  if (-1 < DAT_000bd85c) {
    (*(code *)(&PTR_LAB_0000d4e0)[DAT_000bd85c])();
    if (DAT_000bd85c == -1) {
      FUN_0000e918();
    }
  }
  return in_D0;
}


/* Address 0000d5d6 */

undefined4 FUN_0000d5d6(void)

{
  undefined4 in_D0;
  int iVar1;
  undefined4 *in_A0;
  undefined4 *puVar2;
  
  iVar1 = in_A0[1];
  puVar2 = DAT_000bd884;
  if (*(short *)((int)in_A0 + *(int *)((int)in_A0 + in_A0[10] + 0x68) + in_A0[10] + 0x6c) == 1) {
    DAT_000bd8c4 = 0xd4;
  }
  else {
    DAT_000bd8c4 = 300;
  }
  do {
    do {
    } while (DAT_000bd848 <= (int)in_A0);
    *puVar2 = *in_A0;
    iVar1 = iVar1 + -4;
    in_A0 = in_A0 + 1;
    puVar2 = puVar2 + 1;
  } while (iVar1 != 0);
  DAT_000bd85c = 2;
  return in_D0;
}


/* Address 0000d63e */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0000d63e(void)

{
  undefined4 in_D0;
  uint uVar1;
  undefined4 in_D1;
  uint uVar2;
  int *piVar3;
  int extraout_A0;
  
  _DAT_000bd8b4 = 0;
  DAT_000bd89c = *(int *)(DAT_000bd884 + 4) + DAT_000bd89c;
  DAT_000bd8b0 = *(int *)(DAT_000bd884 + 4) + DAT_000bd884;
  _DAT_000bd8b8 = *(undefined4 *)(DAT_000bd884 + 0x20);
  _DAT_000bd8bc = *(undefined4 *)(DAT_000bd884 + 0x1c);
  piVar3 = (int *)(*(int *)(DAT_000bd884 + 0x14) + DAT_000bd884 + 0x10);
  if (*piVar3 == 0x41445343) {
    DAT_0003bcc0 = piVar3[3];
    DAT_0003bcc4 = piVar3[4];
  }
  else {
    DAT_0003bcc0 = 0x12;
    DAT_0003bcc4 = 0x481db08;
  }
  FUN_0000e8e2();
  DAT_000bd8c8 = *(undefined4 *)(extraout_A0 + 0xc);
  uVar1 = *(uint *)(extraout_A0 + 8);
  if (uVar1 / 300 < 0x10000) {
    uVar1 = uVar1 % 300 << 0x10 | uVar1 / 300 & 0xffff;
  }
  uVar2 = uVar1 & 0xffff0000;
  if (uVar2 / 300 < 0x10000) {
    uVar2 = uVar2 / 300 & 0xffff;
  }
  _DAT_000bd858 = CONCAT22((short)uVar1,(short)uVar2);
  DAT_000bd8c0 = (int)(short)((*(uint *)(extraout_A0 + 8) & 0xffff) * 0x1111 + 0x8000 >> 0x10);
  DAT_000bd8d0 = extraout_A0;
  DAT_000bd8dc = extraout_A0 + 0x10;
  DAT_000bd8ac = *(undefined4 *)(extraout_A0 + 0x1c);
  DAT_000bd8a8 = 0;
  DAT_000bd8a4 = DAT_000bd8b0;
  DAT_000bd8a0 = DAT_000bd8b0 + 0x10000;
  DAT_000bd85c = 3;
  return CONCAT44(in_D0,in_D1);
}


/* Address 0000d738 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000d738(void)

{
  undefined4 uVar1;
  undefined4 in_A0;
  int *extraout_A0;
  
  uVar1 = FUN_0000db8a();
  if (extraout_A0 == (int *)0x0) {
    return uVar1;
  }
  if (*extraout_A0 != 0x53544142) {
    _DAT_000bd85e = 0x3333;
    DAT_000bd85c = 0xffff;
    return uVar1;
  }
  DAT_000bd8e0 = extraout_A0 + -0x10;
  FUN_0000db54(uVar1);
  DAT_000bd8a0 = DAT_000bd8e0 + 0x4000;
  DAT_000bd85c = 4;
  return in_A0;
}


/* Address 0000d76e */

undefined4 FUN_0000d76e(void)

{
  int in_A0;
  undefined4 in_stack_00000000;
  
  DAT_000bd8e0 = in_A0 + -0x40;
  FUN_0000db54();
  DAT_000bd8a0 = DAT_000bd8e0 + 0x10000;
  DAT_000bd85c = 4;
  return in_stack_00000000;
}


/* Address 0000d7a4 */

/* WARNING: Removing unreachable block (ram,0x0000d7ca) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000d7a4(void)

{
  undefined4 in_D0;
  
  if (DAT_000bd848 <= DAT_000bd8a0) {
    return in_D0;
  }
  do {
  } while( true );
}


/* Address 0000d856 */

undefined4 FUN_0000d856(void)

{
  undefined4 in_D0;
  
  DAT_000bd8e4 = *(undefined4 *)(DAT_000bd8d4 + 0x4c);
  DAT_000bd8ec = *(int *)(DAT_000bd8d4 + 0x44) + DAT_000bd8d4 + 0x40;
  DAT_000bd8e8 = DAT_000bd8d4 + 0x50;
  DAT_000bd85c = 7;
  return in_D0;
}


/* Address 0000d896 */

/* WARNING: Removing unreachable block (ram,0x0000d934) */
/* WARNING: Removing unreachable block (ram,0x0000d97c) */
/* WARNING: Removing unreachable block (ram,0x0000d9aa) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0000d896(void)

{
  int iVar1;
  undefined4 in_D0;
  undefined4 in_D1;
  uint uVar2;
  int *extraout_A0;
  
  FUN_0000e4c0();
  if ((_DAT_00047b84 & _DAT_00049ba4) != 0) {
    _DAT_000bd85e = 0;
    DAT_000bd85c = 0xffff;
    return CONCAT44(in_D0,in_D1);
  }
  FUN_0000dca2();
  if (*(uint *)(DAT_000bd8e8 + 8) == 0xffffffff) {
    FUN_0000e902();
  }
  else {
    uVar2 = *(uint *)(DAT_000bd8e8 + 8) & 0x7fffffff;
    do {
    } while (DAT_000bd852 < (int)uVar2);
    if (_DAT_000bd8b4 == 0) {
      if ((int)((DAT_000bd852 - uVar2) - DAT_000bd8c0) < 0) {
        DAT_000c0904 = DAT_000c0904 + 1;
        FUN_000227a0(1,DAT_000bd8ec,&DAT_000bd904);
        _DAT_000bd85e = 0x4444;
        DAT_000bd85c = 0xffff;
        return CONCAT44(in_D0,in_D1);
      }
      _DAT_000bd8b4 = 1;
    }
    FUN_00022780(DAT_000bd8ec);
  }
  if (DAT_000bd8b6 == 0) {
    if (*(int *)(DAT_000bd8dc + 8) - DAT_000bd852 <= DAT_000bd8c4) {
      FUN_0000dc00();
      DAT_000bd8b6 = 1;
      DAT_000bd8ac = *(undefined4 *)(DAT_000bd8dc + 0xc);
      DAT_000bd8a8 = 0;
      DAT_000bd8a4 = DAT_000bd8b0;
      DAT_000bd8a0 = DAT_000bd8b0 + 0x10000;
    }
  }
  else if ((DAT_000bd8b6 == 1) && (FUN_0000db8a(), extraout_A0 != (int *)0x0)) {
    if (*extraout_A0 != 0x53544142) {
      _DAT_000bd85e = 0x3333;
      DAT_000bd85c = 0xffff;
      return CONCAT44(in_D0,in_D1);
    }
    DAT_000bd8e0 = extraout_A0 + -0x10;
    FUN_0000db54();
    DAT_000bd8b6 = 2;
  }
  iVar1 = DAT_000bd8e8;
  DAT_000bd8e8 = DAT_000bd8e8 + 0x10;
  DAT_000bd8ec = *(int *)(iVar1 + 4) + DAT_000bd8ec;
  DAT_000bd8e4 = DAT_000bd8e4 + -1;
  if (DAT_000bd8e4 != 0) {
    return CONCAT44(in_D0,in_D1);
  }
  while( true ) {
    iVar1 = DAT_000bd8d0;
    DAT_000bd8cc = DAT_000bd8cc + -1;
    if (DAT_000bd8cc == 0) break;
    DAT_000bd8d0 = DAT_000bd8d0 + 0x10;
    DAT_000bd8d4 = *(int *)(iVar1 + 4) + DAT_000bd8d4;
    if (*(int *)(DAT_000bd8d4 + 0x4c) != 0) {
      DAT_000bd85c = 6;
      return CONCAT44(in_D0,in_D1);
    }
  }
  if (DAT_000bd8b6 == 3) {
    if (DAT_000bd898 == 0) {
      _DAT_000bd85e = 0;
      DAT_000bd85c = 0xffff;
      return CONCAT44(in_D0,in_D1);
    }
    DAT_000bd898 = DAT_000bd898 + -1;
    DAT_000bd8d0 = DAT_000bd8f4;
    DAT_000bd8cc = DAT_000bd8f0;
    DAT_000bd8d4 = DAT_000bd8f8;
    DAT_000bd852 = DAT_000bd8fc;
    DAT_000bd85c = 6;
    return CONCAT44(in_D0,in_D1);
  }
  DAT_000bd85c = 5;
  return CONCAT44(in_D0,in_D1);
}


/* Address 0000db54 */

void FUN_0000db54(void)

{
  int in_A0;
  
  DAT_000bd8d8 = 0;
  do {
    in_A0 = *(int *)(DAT_000bd8dc + 4) + in_A0;
    if (DAT_000bd888 < in_A0) {
      return;
    }
    DAT_000bd8dc = DAT_000bd8dc + 0x10;
    DAT_000bd8d8 = DAT_000bd8d8 + 1;
    DAT_000bd8c8 = DAT_000bd8c8 + -1;
  } while (DAT_000bd8c8 != 0);
  return;
}


/* Address 0000db8a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0000db8a(void)

{
  undefined4 in_D0;
  undefined4 in_D1;
  int *piVar1;
  
  do {
    while( true ) {
      if (DAT_000bd848 < (int)DAT_000bd8a4) {
        if (DAT_000bd8a0 <= (int)DAT_000bd8a4) {
          _DAT_000bd85e = 0x1111;
          DAT_000bd85c = 0xffff;
        }
        return CONCAT44(in_D0,in_D1);
      }
      piVar1 = DAT_000bd8a4 + 1;
      if (DAT_000bd8ac == *DAT_000bd8a4) break;
      DAT_000bd8a8 = 0;
      DAT_000bd8a4 = piVar1;
    }
    DAT_000bd8a8 = DAT_000bd8a8 + 4;
    DAT_000bd8a4 = piVar1;
  } while (DAT_000bd8a8 != 0x40);
  return CONCAT44(in_D0,in_D1);
}


/* Address 0000dc00 */

void FUN_0000dc00(void)

{
  undefined4 extraout_A0;
  
  FUN_0000dc22();
  func_0x0000303c();
  func_0x0000304e();
  DAT_000bd848 = extraout_A0;
  return;
}


/* Address 0000dc22 */

undefined8 FUN_0000dc22(void)

{
  undefined4 in_D1;
  int extraout_D1;
  uint uVar1;
  uint uVar2;
  
  FUN_0000dc56();
  uVar1 = extraout_D1 - 6;
  if (uVar1 / 0x4b < 0x10000) {
    uVar1 = uVar1 % 0x4b << 0x10 | uVar1 / 0x4b & 0xffff;
  }
  uVar2 = uVar1 & 0xffff;
  if (uVar2 / 0x3c < 0x10000) {
    uVar2 = uVar2 % 0x3c << 0x10 | uVar2 / 0x3c;
  }
  return CONCAT44(CONCAT22((short)uVar2,(short)(uVar2 >> 0x10) << 8) | uVar1 >> 0x10,in_D1);
}


/* Address 0000dc56 */

void FUN_0000dc56(void)

{
  ushort in_D0w;
  uint in_D1;
  
  if (0xffff < in_D1 / in_D0w) {
    return;
  }
  return;
}


/* Address 0000dc62 */

void FUN_0000dc62(void)

{
  return;
}


/* Address 0000dc7c */

undefined4 FUN_0000dc7c(void)

{
  undefined4 in_D0;
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  DAT_000bd880 = &DAT_00802000;
  puVar1 = (undefined4 *)&DAT_00802000;
  do {
    puVar2 = puVar1 + 1;
    *puVar1 = 0;
    puVar1 = puVar2;
  } while (puVar2 != (undefined4 *)0x902000);
  return in_D0;
}


/* Address 0000dca2 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000dca2(void)

{
  undefined4 *puVar1;
  undefined4 in_D0;
  undefined4 *puVar2;
  undefined4 *extraout_A0;
  undefined4 unaff_A2;
  undefined4 unaff_A3;
  
  puVar1 = DAT_000bd880;
  puVar2 = DAT_000bd880 + 1;
  *DAT_000bd880 = 0xa0a4a3;
  *puVar2 = DAT_000bd8dc;
  puVar1[2] = DAT_000bd8e8;
  puVar1[3] = unaff_A3;
  puVar1[4] = 0xa2;
  puVar1[5] = unaff_A2;
  puVar1[6] = 0xd4;
  puVar1[7] = DAT_000bd8ec;
  puVar1[8] = 0xd5;
  puVar1[9] = DAT_000bd8e4;
  puVar1[10] = 0xd7;
  puVar1[0xb] = DAT_000bd8cc;
  puVar1[0xc] = _DAT_00f1b138;
  FUN_0000dd2c();
  *extraout_A0 = DAT_000bd848;
  extraout_A0[1] = *(undefined4 *)(DAT_000bd8e8 + 8);
  extraout_A0[2] = DAT_000bd852;
  extraout_A0[3] = 0xeeeeeeee;
  DAT_000bd880 = extraout_A0 + 3;
  return in_D0;
}


/* Address 0000dd2c */

void FUN_0000dd2c(void)

{
  undefined4 extraout_A0;
  
  func_0x0000304e();
  DAT_000bd848 = extraout_A0;
  return;
}


/* Address 0000dd40 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000dd40(void)

{
  undefined4 *puVar1;
  short sVar2;
  undefined4 *puVar3;
  
  _DAT_00000080 = 0xde08;
  _DAT_00000088 = 0xdeb6;
  _DAT_0000008c = 0xdee2;
  _DAT_00000090 = 0xdef6;
  _DAT_00000020 = 0xddfe;
  sVar2 = 0x62;
  puVar3 = &DAT_000c0d28;
  do {
    puVar1 = puVar3 + 0x100;
    *puVar3 = puVar1;
    sVar2 = sVar2 + -1;
    puVar3 = puVar1;
  } while (sVar2 != -1);
  *puVar1 = 0;
  DAT_000c0924 = &DAT_000c0d28;
  DAT_000c0920 = &DAT_000c0928;
  DAT_000c0928 = &DAT_000c0928;
  DAT_000c092c = &DAT_000c0928;
  DAT_000c0934 = &DAT_000c0d28;
  DAT_000c093c = 0;
  DAT_000c0942 = 0;
  DAT_000c093e = 0;
  DAT_000c094a = 0;
  DAT_000c0930 = 0xddcc;
  FUN_0000ddf2();
  do {
    do {
    } while (DAT_0000ddee == DAT_000778cc);
    DAT_0000ddee = DAT_000778cc;
    __m68k_trap(0);
  } while( true );
}


/* Address 0000ddf2 */

void FUN_0000ddf2(void)

{
  FUN_0000de5c();
  return;
}


/* Address 0000de1c */

void FUN_0000de1c(void)

{
  int *in_A0;
  
  while( true ) {
    do {
      do {
        in_A0 = (int *)*in_A0;
      } while (*(int *)((int)in_A0 + 0x1a) != 0);
    } while (*(int *)((int)in_A0 + 0x22) != 0);
    if (*(int *)((int)in_A0 + 0x16) == 0) break;
    if (*(uint *)((int)in_A0 + 0x16) <= DAT_000778cc) {
      *(undefined4 *)((int)in_A0 + 0x16) = 0;
      DAT_000c0920 = (int)in_A0;
      return;
    }
  }
  DAT_000c0920 = (int)in_A0;
  return;
}


/* Address 0000de5c */

/* WARNING: Control flow encountered unimplemented instructions */

int * FUN_0000de5c(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int in_D0;
  undefined4 in_D1;
  
  piVar2 = DAT_000c0924;
  piVar1 = DAT_000c0920;
  if (DAT_000c0924 != (int *)0x0) {
    iVar3 = *DAT_000c0924;
    *DAT_000c0924 = *DAT_000c0920;
    DAT_000c0924 = (int *)iVar3;
    piVar2[1] = (int)piVar1;
    *piVar1 = (int)piVar2;
    *(int **)(*piVar2 + 4) = piVar2;
    piVar2[2] = in_D0;
    piVar2[4] = in_D0;
    *(undefined4 *)((int)piVar2 + 0x1e) = in_D1;
    piVar2[3] = (int)(piVar2 + 0x100);
    *(undefined2 *)(piVar2 + 5) = 0;
    *(undefined4 *)((int)piVar2 + 0x1a) = 0;
    *(undefined4 *)((int)piVar2 + 0x16) = 0;
    *(undefined4 *)((int)piVar2 + 0x22) = 0;
    return piVar2;
  }
                    /* WARNING: Unimplemented instruction - Truncating control flow here */
  halt_unimplemented();
}


/* Address 0000df04 */

void FUN_0000df04(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  uint in_D0;
  
  puVar2 = DAT_000c0920;
  for (puVar1 = (undefined4 *)*DAT_000c0920; puVar2 != puVar1; puVar1 = (undefined4 *)*puVar1) {
    *(uint *)((int)puVar1 + 0x1a) = ~in_D0 & *(uint *)((int)puVar1 + 0x1a);
  }
  return;
}


/* Address 0000df22 */

void FUN_0000df22(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar2 = DAT_000c0920;
  for (puVar1 = (undefined4 *)*DAT_000c0920; puVar2 != puVar1; puVar1 = (undefined4 *)*puVar1) {
    *(int *)((int)puVar1 + 0x22) = *(int *)((int)puVar1 + 0x22) + 1;
  }
  return;
}


/* Address 0000df3e */

void FUN_0000df3e(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar2 = DAT_000c0920;
  for (puVar1 = (undefined4 *)*DAT_000c0920; puVar2 != puVar1; puVar1 = (undefined4 *)*puVar1) {
    if (*(int *)((int)puVar1 + 0x22) != 0) {
      *(int *)((int)puVar1 + 0x22) = *(int *)((int)puVar1 + 0x22) + -1;
    }
  }
  return;
}


/* Address 0000df60 */

void FUN_0000df60(void)

{
  __m68k_trap(0);
  return;
}


/* Address 0000df6c */

void FUN_0000df6c(void)

{
  FUN_0000de5c();
  return;
}


/* Address 0000df7a */

undefined4 FUN_0000df7a(undefined4 param_1)

{
  __m68k_trap(2);
  __m68k_trap(3);
  return param_1;
}


/* Address 0000df8c */

undefined4 FUN_0000df8c(undefined4 param_1)

{
  __m68k_trap(4);
  return param_1;
}


/* Address 0000df9c */

void FUN_0000df9c(void)

{
  FUN_0000df04();
  return;
}


/* Address 0000dfa6 */

undefined4 FUN_0000dfa6(void)

{
  return *(undefined4 *)(DAT_000c0920 + 0x1e);
}


/* Address 0000dff4 */

void FUN_0000dff4(void)

{
  func_0x00003048();
  func_0x00003006();
  func_0x0000305a();
  return;
}


/* Address 0000e00a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e00a(void)

{
  uint uVar1;
  undefined4 *puVar3;
  undefined4 *puVar4;
  ushort uVar2;
  
  puVar3 = &DAT_000040a4;
  uVar1 = DAT_000040a4;
  puVar4 = DAT_000040a0;
  do {
    puVar3 = puVar3 + 1;
    *puVar4 = *puVar3;
    uVar2 = (short)uVar1 - 1;
    uVar1 = (uint)uVar2;
    puVar4 = puVar4 + 1;
  } while (uVar2 != 0xffff);
  func_0x00003000();
  _DAT_00f02110 = 0xf03224;
  _DAT_00f02114 = 1;
  return;
}


/* Address 0000e03a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000e03a(undefined4 param_1,undefined4 param_2)

{
  undefined4 in_D0;
  
  do {
  } while ((_DAT_00f02238 & 1) == 0);
  _DAT_00f02268 = param_2;
  _DAT_00f0226c = param_2;
  _DAT_00f02200 = param_1;
  _DAT_00f02204 = 0x3e20;
  _DAT_00f0220c = 0;
  _DAT_00f02210 = 0x1ff20;
  _DAT_00f0223c = 0xb400e0;
  _DAT_00f02238 = 0x10200;
  return in_D0;
}


/* Address 0000e098 */

void FUN_0000e098(void)

{
  uint uVar1;
  
  do {
    uVar1 = shared_word_00f03200_candidate;
  } while (uVar1 != 0);
  return;
}


/* Address 0000e0a6 */

/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x17e3a","bytes":"4eb90000e0a6","assembly":"jsr
   $e0a6.l"}] */

void observed_call_candidate_0000e0a6(void)

{
  uint uVar1;
  
  FUN_0000e098();
  shared_word_00f0320c_candidate = 0x47b88;
  shared_word_00f03210_candidate = 0x49b8c;
  shared_word_00f03214_candidate = 0x49bb4;
  shared_word_00f03218_candidate = 0x49b88;
  shared_word_00f03204_candidate = 0x4d80;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x4d80);
  FUN_0000e098();
  return;
}


/* Address 0000e19e */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e19e(void)

{
  uint uVar1;
  
  FUN_0000e098();
  _DAT_0010a684 = 1;
  shared_word_00f0320c_candidate = 0x47b88;
  shared_word_00f03210_candidate = 0x47bc8;
  shared_word_00f03214_candidate = DAT_00049b88;
  shared_word_00f03218_candidate = 0x40;
  shared_word_00f0321c_candidate = 0x10a684;
  shared_word_00f03204_candidate = 0x52e0;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x52e0);
  FUN_0000e098();
  return;
}


/* Address 0000e202 */

void FUN_0000e202(void)

{
  uint uVar1;
  
  FUN_0000e098();
  shared_word_00f03204_candidate = 0x57a0;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x57a0);
  return;
}


/* Address 0000e220 */

void FUN_0000e220(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  uint uVar1;
  
  FUN_0000e098();
  shared_word_00f0320c_candidate = param_1;
  shared_word_00f03210_candidate = param_2;
  shared_word_00f03214_candidate = param_3;
  shared_word_00f03218_candidate = param_4;
  shared_word_00f0321c_candidate = param_5;
  shared_word_00f03204_candidate = 0x4320;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x4320);
  FUN_0000e098();
  return;
}


/* Address 0000e26c */

void FUN_0000e26c(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  uint uVar1;
  
  FUN_0000e098();
  shared_word_00f0320c_candidate = param_1;
  shared_word_00f03210_candidate = param_2;
  shared_word_00f03214_candidate = param_3;
  shared_word_00f03218_candidate = param_4;
  shared_word_00f0321c_candidate = param_5;
  shared_word_00f03204_candidate = 0x4720;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x4720);
  FUN_0000e098();
  return;
}


/* Address 0000e2b8 */

void FUN_0000e2b8(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  FUN_0000e098();
  shared_word_00f0320c_candidate = param_1;
  shared_word_00f03210_candidate = param_2;
  shared_word_00f03214_candidate = param_3;
  shared_word_00f03204_candidate = 0x4b00;
  do {
    uVar1 = shared_word_00f03204_candidate;
  } while (uVar1 == 0x4b00);
  FUN_0000e098();
  return;
}


/* Address 0000e3e0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e3e0(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  int iVar1;
  
  if (param_3 != 0) {
    if (param_3 + -0x80 < 0) {
      do {
        *param_2 = *param_1;
        param_3 = param_3 + -1;
        param_2 = param_2 + 1;
        param_1 = param_1 + 1;
      } while (param_3 != 0);
    }
    else {
      _DAT_00f02204 = 0x4020;
      _DAT_00f02228 = 0x4020;
      do {
        iVar1 = param_3;
        if (-1 < param_3 + -0x10000) {
          iVar1 = 0x10000;
        }
        param_3 = param_3 - iVar1;
        _DAT_00f0223c = iVar1 >> 1 | 0x10000;
        _DAT_00f02200 = (uint)param_2 & 0xfffffff8;
        _DAT_00f0220c = (int)((int)param_2 - _DAT_00f02200) >> 1;
        _DAT_00f02224 = (uint)param_1 & 0xfffffff8;
        _DAT_00f02230 = (int)((int)param_1 - _DAT_00f02224) >> 1;
        if (_DAT_00f0220c < _DAT_00f02230) {
          _DAT_00f02238 = 0x1800005;
        }
        else {
          _DAT_00f02238 = 0x1800001;
        }
        param_2 = param_2 + iVar1;
        param_1 = param_1 + iVar1;
      } while (param_3 != 0);
    }
  }
  return;
}


/* Address 0000e4c0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0000e4c0(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 in_D0;
  undefined4 in_D1;
  
  uVar4 = _DAT_00049ba4;
  _DAT_00f14000 = CONCAT22(0x810e,_DAT_00f14002);
  uVar1 = _DAT_00f14000 | 0xf0fffffc;
  _DAT_00f14000 = CONCAT22(0x810d,_DAT_00f14002);
  uVar2 = _DAT_00f14000 | 0xf0fffffc;
  _DAT_00f14000 = CONCAT22(0x810b,_DAT_00f14002);
  uVar3 = _DAT_00f14000 | 0xf0fffffc;
  _DAT_00f14000 = CONCAT22(0x8107,_DAT_00f14002);
  _DAT_00049ba4 =
       ~(((_DAT_00f14000 | 0xf0fffffc) << 8 | (_DAT_00f14000 | 0xf0fffffc) >> 0x18) &
        ((uVar3 << 6 | uVar3 >> 0x1a) << 6 | (uVar3 & 0x3ffffff) >> 0x14) &
        (uVar2 << 0x18 | uVar2 >> 8) & (uVar1 << 0x1c | uVar1 >> 4));
  DAT_00049bac = _DAT_00049ba4 & (_DAT_00049ba4 ^ uVar4);
  return CONCAT44(in_D0,in_D1);
}


/* Address 0000e540 */

int FUN_0000e540(ushort param_1,ushort param_2,short param_3,ushort param_4)

{
  ushort uVar3;
  uint uVar1;
  int iVar2;
  undefined2 local_2;
  
  local_2 = param_1;
  uVar3 = param_1;
  if ((short)param_1 < 0) {
    param_2 = -param_2;
    uVar3 = -(param_1 + (param_2 != 0));
  }
  if (param_3 < 0) {
    param_4 = -param_4;
    param_3 = -(param_3 + (ushort)(param_4 != 0));
    local_2 = ~param_1;
  }
  uVar1 = 0;
  if (uVar3 != 0) {
    uVar1 = (uint)uVar3 * (uint)param_4;
  }
  if (param_3 != 0) {
    uVar1 = (uint)(ushort)(param_3 * param_2 + (short)uVar1);
  }
  iVar2 = (uint)param_2 * (uint)param_4 + uVar1 * 0x10000;
  if ((short)local_2 < 0) {
    iVar2 = -iVar2;
  }
  return iVar2;
}


/* Address 0000e588 */

uint FUN_0000e588(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  short sVar4;
  bool bVar5;
  ushort local_2;
  
  local_2 = 0;
  uVar1 = 0;
  if (param_2 != 0) {
    uVar3 = param_2;
    if ((int)param_2 < 0) {
      uVar3 = -param_2;
      local_2 = 0xffff;
    }
    if ((int)param_1 < 0) {
      param_1 = -param_1;
      local_2 = ~local_2;
    }
    if (uVar3 <= param_1) {
      if (param_2._0_2_ == 0) {
        uVar1 = param_1 >> 0x10;
        if (uVar1 != 0) {
          uVar2 = uVar1 / (uVar3 & 0xffff);
          if (uVar2 < 0x10000) {
            uVar1 = uVar1 % (uVar3 & 0xffff) << 0x10 | uVar2;
          }
        }
        uVar2 = CONCAT22((short)(uVar1 >> 0x10),(short)param_1);
        uVar3 = uVar2 / (uVar3 & 0xffff);
        if (uVar3 < 0x10000) {
          uVar2 = uVar3 & 0xffff;
        }
        uVar1 = CONCAT22((short)uVar1,(short)uVar2);
      }
      else {
        sVar4 = 0x1f;
        uVar2 = uVar1;
        uVar1 = param_1;
        do {
          bVar5 = CARRY4(uVar1,uVar1);
          uVar1 = uVar1 * 2;
          uVar2 = uVar2 * 2 + (uint)bVar5;
          if (uVar3 <= uVar2) {
            uVar2 = uVar2 - uVar3;
            uVar1 = CONCAT22((short)(uVar1 >> 0x10),(short)uVar1 + 1);
          }
          sVar4 = sVar4 + -1;
        } while (sVar4 != -1);
      }
    }
  }
  if ((short)local_2 < 0) {
    uVar1 = -uVar1;
  }
  return uVar1;
}


/* Address 0000e60a */

undefined4 FUN_0000e60a(undefined4 param_1,undefined4 param_2)

{
  undefined4 extraout_D1;
  
  FUN_0000e588(param_1,param_2);
  return extraout_D1;
}


/* Address 0000e61c */

uint FUN_0000e61c(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  short sVar4;
  bool bVar5;
  
  uVar1 = 0;
  if ((param_2 != 0) && (param_2 <= param_1)) {
    if (param_2._0_2_ == 0) {
      uVar1 = param_1 >> 0x10;
      if (uVar1 != 0) {
        uVar2 = uVar1 / (param_2 & 0xffff);
        if (uVar2 < 0x10000) {
          uVar1 = uVar1 % (param_2 & 0xffff) << 0x10 | uVar2;
        }
      }
      uVar3 = CONCAT22((short)(uVar1 >> 0x10),(short)param_1);
      uVar2 = uVar3 / (param_2 & 0xffff);
      if (uVar2 < 0x10000) {
        uVar3 = uVar2 & 0xffff;
      }
      uVar1 = CONCAT22((short)uVar1,(short)uVar3);
    }
    else {
      sVar4 = 0x1f;
      uVar2 = uVar1;
      uVar1 = param_1;
      do {
        bVar5 = CARRY4(uVar1,uVar1);
        uVar1 = uVar1 * 2;
        uVar2 = uVar2 * 2 + (uint)bVar5;
        if (param_2 <= uVar2) {
          uVar2 = uVar2 - param_2;
          uVar1 = CONCAT22((short)(uVar1 >> 0x10),(short)uVar1 + 1);
        }
        sVar4 = sVar4 + -1;
      } while (sVar4 != -1);
    }
  }
  return uVar1;
}


/* Address 0000e67c */

undefined4 FUN_0000e67c(undefined4 param_1,undefined4 param_2)

{
  undefined4 extraout_D1;
  
  FUN_0000e61c(param_1,param_2);
  return extraout_D1;
}


/* Address 0000e6a0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e6a0(void)

{
  bool bVar1;
  
  bVar1 = (_DAT_00f14002 & 0x10) != 0;
  if (bVar1) {
    _DAT_000778c6 = 5;
    _DAT_00f00038 = 0xc0;
    _DAT_00f0003a = 0xc0;
    _DAT_000778c8 = 0x26;
    DAT_000778ca = 0x206;
  }
  else {
    _DAT_000778c6 = 6;
    _DAT_00f00038 = 0xaf;
    _DAT_00f0003a = 0xaf;
    _DAT_000778c8 = 0x23;
    DAT_000778ca = 0x263;
  }
  _DAT_00f0003c = 0x68c;
  _DAT_000778c4 = (ushort)!bVar1;
  _DAT_00f00046 = _DAT_000778c8;
  _DAT_00f00048 = 0xffff;
  _DAT_00f00058 = 0x4778;
  _DAT_00f0002a = 0;
  DAT_000776c8 = 0;
  DAT_000776cc = 2;
  DAT_000776d0 = 0;
  DAT_000776d4 = 4;
  DAT_000776d8 = 0xee;
  DAT_000776dc = CONCAT22(0xd900,DAT_000778ca << 3) & 0xffff3ff0 | 3;
  DAT_000776e0 = 0xee;
  DAT_000776e4 = CONCAT22(0xda00,DAT_000778ca << 3) | 0x8003;
  DAT_000776e8 = 0xee;
  DAT_000776ec = CONCAT22(0xda00,_DAT_000778c8 << 3) | 0x4003;
  DAT_000776f0 = 0;
  DAT_000776f4 = 4;
  _DAT_000778c0 = &DAT_000776f0;
  return;
}


/* Address 0000e7aa */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

char FUN_0000e7aa(void)

{
  char in_XF;
  
  _DAT_00000100 = FUN_0000e7d4;
  _DAT_00f0004e = DAT_000778ca | 1;
  _DAT_00f000e0 = 0x303;
  return in_XF << 4;
}


/* Address 0000e7d4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000e7d4(void)

{
  undefined4 in_D0;
  undefined4 extraout_A0;
  undefined4 extraout_A1;
  
  if ((_DAT_00f000e0 & 1) != 0) {
    _DAT_00f000e0 = func_0x0000304e();
    _DAT_00f000e0 = _DAT_00f000e0 | 0x100;
    DAT_000bd848 = extraout_A0;
    _DAT_001126a0 = extraout_A1;
  }
  if ((_DAT_00f000e0 & 2) != 0) {
    _DAT_000bd850 = 0xffff;
    _DAT_00f000e0 = _DAT_00f000e0 | 0x200;
  }
  _DAT_00f000e0 = _DAT_00f000e0 | 3;
  _DAT_00f000e2 = 0;
  return in_D0;
}


/* Address 0000e840 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000e840(void)

{
  undefined4 in_D0;
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  _DAT_00f1a100 = 0;
  puVar1 = (undefined4 *)&DAT_00f1b010;
  puVar2 = &DAT_00008460;
  do {
    puVar3 = puVar2 + 1;
    *puVar1 = *puVar2;
    puVar1 = puVar1 + 1;
    puVar2 = puVar3;
  } while (puVar3 != (undefined4 *)&DAT_000085e0);
  _DAT_00f1b140 = 0;
  _DAT_00f1a148 = 0;
  _DAT_00f1a14c = 0;
  _DAT_00f1a150 = 0x12;
  _DAT_00f1a154 = 0x15;
  _DAT_00f14000 = 0x100;
  _DAT_00f1b144 = 0x481db08;
  _DAT_00f1a110 = 0xf1b01c;
  _DAT_00f1a114 = 1;
  return in_D0;
}


/* Address 0000e8e2 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e8e2(void)

{
  _DAT_00f1a150 = DAT_0003bcc0;
  _DAT_00f1a154 = 0x15;
  _DAT_00f1b144 = DAT_0003bcc4;
  return;
}


/* Address 0000e902 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e902(void)

{
  undefined4 in_D0;
  undefined4 in_A1;
  
  _DAT_00f1b13c = in_A1;
  _DAT_00f1b138 = in_D0;
  return;
}


/* Address 0000e918 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0000e918(void)

{
  undefined4 in_D0;
  
  _DAT_00f1b140 = 1;
  do {
  } while ((_DAT_00f1a114 & 1) != 0);
  _DAT_00f1a100 = 0;
  return in_D0;
}


/* Address 0000e942 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e942(void)

{
  _DAT_00f1a10c = &DAT_00070007;
  _DAT_00f10000 = 0;
  _DAT_00f10002 = 0;
  _DAT_00f14000 = 0x100;
  FUN_0000e96c();
  return;
}


/* Address 0000e96c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000e96c(void)

{
  uint uVar1;
  undefined4 *puVar3;
  undefined4 *puVar4;
  ushort uVar2;
  
  puVar3 = &DAT_00007244;
  uVar1 = (DAT_00007244 >> 2) - 1;
  puVar4 = DAT_00007240;
  do {
    puVar3 = puVar3 + 1;
    *puVar4 = *puVar3;
    uVar2 = (short)uVar1 - 1;
    uVar1 = (uint)uVar2;
    puVar4 = puVar4 + 1;
  } while (uVar2 != 0xffff);
  _DAT_00f1bafc = 0x7fff;
  _DAT_00f1bb00 = 0x7fff;
  _DAT_00f1a110 = 0xf1b126;
  _DAT_00f1a150 = 0x1a;
  _DAT_00f1a154 = 0x15;
  _DAT_00f1badc = 2;
  _DAT_00f1bae0 = 0x3bce0;
  _DAT_00f1bae4 = 0;
  _DAT_00f1a114 = 5;
  FUN_0000ea08();
  return;
}


/* Address 0000ea08 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000ea08(void)

{
  do {
  } while (_DAT_00f1badc != 0);
  return;
}


/* Address 0000ea20 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000ea20(void)

{
  _DAT_00112940 = 0;
  return;
}


/* Address 0000ea28 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000ea28(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  byte *pbVar4;
  
  sVar3 = 0;
  if (0 < _DAT_00112940) {
    do {
      iVar2 = sVar3 * 0x10;
      iVar1 = **(int **)(&DAT_001126c8 + iVar2);
      pbVar4 = (byte *)(*(int *)(**(int **)(&DAT_001126c0 + iVar2) + 0xc +
                                *(int *)(&DAT_001126c4 + iVar2) * 4) +
                       **(int **)(&DAT_001126c0 + iVar2));
      *(uint *)(iVar1 + 8) = (uint)pbVar4[1] + (uint)*pbVar4 * 0x10000;
      if (*(int *)(&DAT_001126cc + iVar2) != 0) {
        *(byte *)(iVar1 + 8) = *(byte *)(iVar1 + 8) | 0x80;
      }
      *(undefined **)(iVar1 + 0xc) =
           (&PTR_s_hat_red_tape_encrusted_wad_of_bu_00030648_0x1d8_0003bd20)[*pbVar4];
      FUN_0000e2b8(**(undefined4 **)(&DAT_001126c0 + iVar2),*(undefined4 *)(&DAT_001126c4 + iVar2),
                   **(int **)(&DAT_001126c8 + iVar2) + 0x10);
      sVar3 = sVar3 + 1;
    } while (sVar3 < _DAT_00112940);
  }
  _DAT_00112940 = 0;
  return;
}


/* Address 0000eac4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_0000eac4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint in_D0;
  
  if (_DAT_00112940 < 0x28) {
    iVar1 = _DAT_00112940 * 0x10;
    *(undefined4 *)(&DAT_001126c4 + iVar1) = param_2;
    *(undefined4 *)(&DAT_001126c0 + iVar1) = param_1;
    *(undefined4 *)(&DAT_001126c8 + iVar1) = param_3;
    *(undefined4 *)(&DAT_001126cc + iVar1) = param_4;
    _DAT_00112940 = _DAT_00112940 + 1;
    return 1;
  }
  return in_D0 & 0xffff0000;
}


/* Address 0000eb04 */

void FUN_0000eb04(int param_1)

{
  int iVar1;
  short sVar2;
  char *pcVar3;
  
  if (*(int *)(param_1 + 0x68) == 0) {
    sVar2 = *(short *)(param_1 + 0x62) - DAT_0004c24c._2_2_;
    *(short *)(param_1 + 0x62) = sVar2;
    if (sVar2 < 1) {
      do {
        *(short *)(param_1 + 0x62) =
             (short)*(char *)(*(int *)(param_1 + 100) + 1 +
                             (short)*(char *)(*(int *)(param_1 + 100) + 3) * 4) +
             *(short *)(param_1 + 0x62);
        pcVar3 = *(char **)(param_1 + 100);
        iVar1 = (short)pcVar3[3] * 4;
        if ((*pcVar3 == pcVar3[iVar1]) && (*(short *)(param_1 + 0xcc) == 0)) {
          *(int *)(param_1 + 100) = iVar1 + *(int *)(param_1 + 100);
        }
        else {
          pcVar3 = (char *)(*(int *)(param_1 + 100) + iVar1);
          *(char **)(param_1 + 100) = pcVar3;
          sVar2 = FUN_0000eac4(*(undefined4 *)(param_1 + 0x58),(int)(short)*pcVar3,
                               *(undefined4 *)(param_1 + 0x5e),*(byte *)(param_1 + 0xca) >> 7);
          if (sVar2 != 0) {
            *(undefined2 *)(param_1 + 0xcc) = 0;
          }
        }
      } while (*(short *)(param_1 + 0x62) < 1);
      return;
    }
    if (*(short *)(param_1 + 0xcc) == 0) {
      return;
    }
  }
  else {
    sVar2 = *(short *)(param_1 + 0xca);
    if (sVar2 < 0) {
      sVar2 = -sVar2;
    }
    *(int *)(param_1 + 100) = *(int *)(param_1 + 0x68) + sVar2 * 4 + -4;
    *(undefined4 *)(param_1 + 0x68) = 0;
    *(short *)(param_1 + 0x62) = (short)*(char *)(*(int *)(param_1 + 100) + 1);
  }
  sVar2 = FUN_0000eac4(*(undefined4 *)(param_1 + 0x58),(int)(short)**(char **)(param_1 + 100),
                       *(undefined4 *)(param_1 + 0x5e),*(byte *)(param_1 + 0xca) >> 7);
  if (sVar2 != 0) {
    *(undefined2 *)(param_1 + 0xcc) = 0;
  }
  return;
}


/* Address 0000ed60 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

short FUN_0000ed60(void)

{
  uint uVar1;
  short sVar2;
  
  uVar1 = DAT_000778cc + 0x1194;
  FUN_00012620(0);
  while( true ) {
    if (uVar1 <= DAT_000778cc) {
      return 0;
    }
    FUN_0000e4c0();
    if ((_DAT_00049ba4 & 0xe00fe) != 0) break;
    if ((_DAT_00049ba4 & 0x22202000) != 0) {
      return -1;
    }
  }
  sVar2 = FUN_0001b718((short)(_DAT_00049ba4 >> 0x10),(short)_DAT_00049ba4);
  return sVar2 + 1;
}


/* Address 0000edc4 */

void FUN_0000edc4(void)

{
  int iVar1;
  int iVar2;
  short sVar4;
  int iVar3;
  short sVar5;
  undefined2 *puVar6;
  undefined1 *puVar7;
  
  puVar7 = &stack0xffffffec;
  sVar5 = 0;
  iVar2 = FUN_0000dfa6();
  iVar1 = iVar2 * 0xce;
  puVar6 = &DAT_00049d6c + iVar2 * 0x67;
  sVar4 = FUN_000101e0(puVar6,0x15,s_FR__Governor_Samantha_DuPree_Dea_0002cffc + 4,&DAT_0003c4a0);
  if (sVar4 == 0) {
    FUN_0000df7a();
  }
  (&DAT_00049dd8)[iVar2 * 0x67] = 1;
  (&DAT_00049e34)[iVar2 * 0x67] = 2;
  do {
    if ((&DAT_00049d6e)[iVar2 * 0x67] != 0) {
      *puVar6 = 0;
      *(undefined4 *)(puVar7 + -4) = *(undefined4 *)((int)&DAT_00049dca + iVar1);
      *(undefined4 *)(puVar7 + -8) = 0xee32;
      FUN_0001545c();
      *(undefined2 *)(puVar7 + -6) = 0x15;
      *(undefined4 *)(puVar7 + -10) = 0xee3c;
      FUN_0001b002();
      *(undefined4 *)(puVar7 + -10) = 0xee42;
      FUN_0000df7a();
      puVar7 = puVar7 + -6;
    }
    *(undefined4 *)((int)&DAT_00049de4 + iVar1) = 0;
    if (((short)(&DAT_00049e34)[iVar2 * 0x67] < 1) && ((&DAT_00049dd8)[iVar2 * 0x67] != 0)) {
      (&DAT_00049dd8)[iVar2 * 0x67] = 0;
      *(undefined **)((int)&DAT_00049dd4 + iVar1) = &DAT_0003c56c;
      *(undefined4 *)((int)&DAT_00049de4 + iVar1) = 0;
      *(undefined4 *)((int)&DAT_00049de8 + iVar1) = 0;
    }
    *(undefined2 **)(puVar7 + -4) = puVar6;
    *(undefined4 *)(puVar7 + -8) = 0xee6e;
    iVar3 = FUN_00010252();
    sVar4 = (&DAT_00049dd8)[iVar2 * 0x67];
    if (sVar4 == 1) {
      if (iVar3 < 0x100) {
        if (DAT_00049d1e < 3) {
          *(undefined2 *)(puVar7 + -2) = 0x3c;
          *(undefined4 *)(puVar7 + -6) = 0xeea8;
          FUN_000207cc();
          (&DAT_00049dd8)[iVar2 * 0x67] = 2;
        }
        else {
          if (sVar5 == 0) {
            *(undefined2 *)(puVar7 + -2) = 0x3a;
          }
          else {
            *(undefined2 *)(puVar7 + -2) = 0x3b;
          }
          *(undefined4 *)(puVar7 + -6) = 0xeec8;
          FUN_000207cc();
          do {
            *(undefined4 *)(puVar7 + -4) = 0xeed0;
            sVar4 = FUN_0000ed60();
            if (sVar4 < 1) break;
          } while (DAT_00049d1e < *(int *)(&DAT_0003c5d8 + sVar4 * 4));
          if (sVar4 == 0) {
            do {
              *(undefined2 *)(puVar7 + -2) = 0x3d;
              *(undefined4 *)(puVar7 + -6) = 0xeef2;
              FUN_000207cc();
              *(undefined4 *)(puVar7 + -6) = 0xeef8;
              sVar4 = FUN_0000ed60();
              if (sVar4 < 1) goto LAB_0000ef12;
            } while (DAT_00049d1e < *(int *)(&DAT_0003c5d8 + sVar4 * 4));
          }
          if (sVar4 < 1) {
LAB_0000ef12:
            *(undefined2 *)(puVar7 + -2) = 0x3e;
            *(undefined4 *)(puVar7 + -6) = 0xef1c;
            FUN_000207cc();
            if (0 < sVar4) goto LAB_0000ef22;
          }
          else {
LAB_0000ef22:
            *(undefined2 *)(puVar7 + -2) = 0x3f;
            *(undefined4 *)(puVar7 + -6) = 0xef2c;
            FUN_000207cc();
            DAT_00049d1e = DAT_00049d1e - *(int *)(&DAT_0003c5d8 + sVar4 * 4);
            *(undefined4 *)(puVar7 + -6) = 0xef42;
            FUN_0001b786();
            sVar5 = sVar5 + 1;
          }
          (&DAT_00049dd8)[iVar2 * 0x67] = 2;
        }
      }
    }
    else if (((1 < sVar4) && (sVar4 == 2)) && (0x1000 < iVar3)) {
      (&DAT_00049dd8)[iVar2 * 0x67] = 1;
    }
    if ((&DAT_00049dd8)[iVar2 * 0x67] != 0) {
      *(undefined2 **)(puVar7 + -4) = puVar6;
      *(undefined4 *)(puVar7 + -8) = 0xef6a;
      FUN_0001404c();
    }
    *(undefined2 **)(puVar7 + -4) = puVar6;
    *(undefined4 *)(puVar7 + -8) = 0xef74;
    FUN_0000eb04();
    *(undefined **)(puVar7 + -8) = &DAT_00042118;
    *(undefined2 **)(puVar7 + -0xc) = puVar6;
    *(undefined4 *)(puVar7 + -0x10) = 0xef82;
    FUN_00013c9a();
    *(undefined4 *)(puVar7 + -0x10) = 0xef88;
    FUN_0000df60();
  } while( true );
}


/* Address 0000f0c0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000f0c0(void)

{
  DAT_00049b8c = 0;
  DAT_00049b8e = 0;
  DAT_00049b90 = 0;
  _DAT_00049b92 = 0;
  _DAT_00049b94 = 0;
  _DAT_00049b96 = 0;
  DAT_00049b98 = 8;
  DAT_00049b9c = 8;
  DAT_00049ba0 = 0;
  return;
}


/* Address 0000f0fa */

undefined4 FUN_0000f0fa(void)

{
  int iVar1;
  int iVar2;
  char cVar4;
  ushort uVar3;
  short unaff_D2w;
  short unaff_D3w;
  int iVar5;
  int iVar6;
  
  if ((char)DAT_00049ba7 < '\0') {
    if (((DAT_00049ba5 & 0x10) != 0) && (DAT_00049b98 = DAT_00049b98 + 1, 0xff < DAT_00049b98)) {
      DAT_00049b98 = 0;
    }
    if (((DAT_00049ba5 & 0x20) != 0) && (DAT_00049b98 = DAT_00049b98 + -1, DAT_00049b98 < 0)) {
      DAT_00049b98 = 0xff;
    }
    if (((DAT_00049ba5 & 0x40) != 0) && (DAT_00049b9c = DAT_00049b9c + 1, 0xff < (int)DAT_00049b9c))
    {
      DAT_00049b9c = 0;
    }
    if (((char)DAT_00049ba5 < '\0') && (DAT_00049b9c = DAT_00049b9c + -1, (int)DAT_00049b9c < 0)) {
      DAT_00049b9c = 0xff;
    }
    if (((DAT_00049ba5 & 8) != 0) && (DAT_00049ba0 = DAT_00049ba0 + 1, 0xff < DAT_00049ba0)) {
      DAT_00049ba0 = 0;
    }
    if (((DAT_00049ba7 & 8) != 0) && (DAT_00049ba0 = DAT_00049ba0 + -1, DAT_00049ba0 < 0)) {
      DAT_00049ba0 = 0xff;
    }
    if ((DAT_00049ba5 & 1) != 0) {
      DAT_00049b8e = DAT_00049b8e + -8;
    }
    DAT_00047b9a = unaff_D3w;
    DAT_00047b9e = unaff_D2w;
    if ((DAT_00049ba7 & 1) != 0) {
      DAT_00049b8e = DAT_00049b8e + 8;
      DAT_00047b9a = unaff_D3w;
    }
  }
  else {
    if (DAT_0003c840 < 0x79) {
      DAT_0003c840 = DAT_0003c840 + 1;
    }
    else {
      DAT_0003c840 = 0;
    }
    DAT_0003c846 = 0x1b;
    iVar6 = (int)DAT_00049cdc;
    iVar1 = FUN_0000e540(iVar6,0x1b);
    iVar5 = (int)DAT_00049cd8;
    iVar2 = FUN_0000e540(iVar5,DAT_0003c842);
    iVar6 = FUN_0000e540(iVar6,DAT_0003c842);
    iVar5 = FUN_0000e540(iVar5,0x1b);
    DAT_00047b9e = (short)(-(iVar5 + iVar6) >> 0xe);
    DAT_00049b98 = DAT_00049cc0 + 8;
    DAT_00049ba0 = 0;
    DAT_00047b9a = (short)(iVar1 - iVar2 >> 0xe);
  }
  DAT_00047b9c = DAT_00049ce0;
  if ((byte)(DAT_00049cba - 0x40) < 0x81) {
    uVar3 = FUN_00013440(DAT_00049cde - DAT_00047b9a,DAT_00049ce2 - DAT_00047b9e);
    DAT_00049b9c = (uint)(byte)((ushort)((ushort)DAT_00049cba + (uVar3 & 0xff)) >> 1);
  }
  else {
    cVar4 = FUN_00013440(DAT_00049cde - DAT_00047b9a,DAT_00049ce2 - DAT_00047b9e);
    DAT_00049b9c = (uint)((short)((short)(char)DAT_00049cba + (short)cVar4) >> 1);
  }
  FUN_0000e220(&DAT_00047b88,DAT_00049b98,DAT_00049b9c,DAT_00049ba0,0);
  return DAT_0003c846;
}


/* Address 0000f368 */

uint FUN_0000f368(int param_1)

{
  ushort uVar1;
  byte bVar2;
  uint uVar3;
  short sVar4;
  int iVar5;
  
  bVar2 = *(byte *)(param_1 + 0x6f);
  if (bVar2 == 0x40) {
    iVar5 = *(int *)(param_1 + 0x44);
    uVar1 = *(ushort *)(iVar5 + 0x12);
    uVar3 = (uint)uVar1;
    if (uVar1 == 2) {
      uVar3 = *(uint *)(param_1 + 10);
      sVar4 = *(short *)(iVar5 + 0xe);
      goto LAB_0000f474;
    }
    if (2 < (short)uVar1) {
      if (uVar1 != 4) {
        return uVar3;
      }
      uVar3 = *(uint *)(param_1 + 10);
      sVar4 = *(short *)(iVar5 + 0xe);
LAB_0000f414:
      return (uVar3 & 0xfffffc00) + (int)(short)(sVar4 << 6) + 0xa0;
    }
LAB_0000f490:
    if ((short)uVar3 != 1) {
      return uVar3;
    }
LAB_0000f4a0:
    uVar3 = *(uint *)(param_1 + 10) & 0xfffffc00;
    sVar4 = *(short *)(iVar5 + 0xe);
LAB_0000f4ac:
    return uVar3 + (int)(short)(sVar4 << 6) | 0x20;
  }
  if (bVar2 < 0x41) {
    if (bVar2 != 0) {
      return (uint)bVar2;
    }
    iVar5 = *(int *)(param_1 + 0x44);
    uVar1 = *(ushort *)(iVar5 + 0x10);
    if (uVar1 != 2) {
      if (2 < (short)uVar1) {
        if (uVar1 != 4) {
          return (uint)uVar1;
        }
        uVar3 = *(uint *)(param_1 + 4);
        sVar4 = *(short *)(iVar5 + 10);
        goto LAB_0000f414;
      }
      if (uVar1 != 1) {
        return (uint)uVar1;
      }
      uVar3 = *(uint *)(param_1 + 4) & 0xfffffc00;
      sVar4 = *(short *)(iVar5 + 10);
      goto LAB_0000f4ac;
    }
  }
  else {
    if (bVar2 != 0x80) {
      if (bVar2 != 0xc0) {
        return (uint)bVar2;
      }
      iVar5 = *(int *)(param_1 + 0x44);
      uVar1 = *(ushort *)(iVar5 + 0x12);
      uVar3 = (uint)uVar1;
      if (uVar1 != 2) {
        if (2 < (short)uVar1) {
          if (uVar1 != 4) {
            return uVar3;
          }
          return (*(uint *)(param_1 + 10) & 0xfffffc00) + 0x60 +
                 (int)(short)(*(short *)(iVar5 + 0xe) << 6);
        }
        goto LAB_0000f490;
      }
      goto LAB_0000f4a0;
    }
    iVar5 = *(int *)(param_1 + 0x44);
    uVar1 = *(ushort *)(iVar5 + 0x10);
    if (uVar1 == 2) {
      uVar3 = *(uint *)(param_1 + 4) & 0xfffffc00;
      sVar4 = *(short *)(iVar5 + 10);
      goto LAB_0000f4ac;
    }
    if ((short)uVar1 < 3) {
      if (uVar1 != 1) {
        return (uint)uVar1;
      }
      uVar3 = *(uint *)(param_1 + 4) & 0xfffffc00;
      sVar4 = *(short *)(iVar5 + 10);
      goto LAB_0000f4ac;
    }
    if (uVar1 != 4) {
      return (uint)uVar1;
    }
  }
  uVar3 = *(uint *)(param_1 + 4);
  sVar4 = *(short *)(iVar5 + 10);
LAB_0000f474:
  return (uVar3 & 0xfffffc00) + 0x60 + (int)(short)(sVar4 << 6);
}


/* Address 0000f4d8 */

void FUN_0000f4d8(void)

{
  byte bVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  short sVar8;
  char cVar9;
  int unaff_D3;
  undefined2 *puVar10;
  undefined2 uVar11;
  
  bVar2 = false;
  iVar4 = FUN_0000dfa6();
  iVar3 = iVar4 * 0xce;
  puVar10 = &DAT_00049d6c + iVar4 * 0x67;
  *(undefined4 *)(&DAT_00049dc4 + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049dca + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049dd0 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049e0c + iVar3) = 7;
  uVar5 = FUN_0001a77c((short)iVar4);
  uVar5 = uVar5 & 3;
  if (uVar5 != 1) {
    if (1 < uVar5) {
      if (uVar5 == 2) {
        *(undefined **)(&DAT_00049e28 + iVar3) = &DAT_000085e0;
      }
      else if (uVar5 == 3) {
        *(undefined **)(&DAT_00049e28 + iVar3) = &DAT_00008858;
      }
      goto LAB_0000f554;
    }
    if (uVar5 != 0) goto LAB_0000f554;
  }
  *(undefined **)(&DAT_00049e28 + iVar3) = &DAT_000089ec;
LAB_0000f554:
  iVar6 = FUN_0000f368(puVar10);
  do {
    if ((&DAT_00049d6e)[iVar4 * 0x67] != 0) {
      *puVar10 = 0;
      FUN_0000df7a();
    }
    if (bVar2) {
      cVar9 = (&DAT_00049dda)[iVar3] - (&DAT_00049ddb)[iVar3];
      if (cVar9 == '\0') {
        bVar2 = false;
      }
      else {
        if (-(int)(short)cVar9 != DAT_0004c24c && (int)(short)cVar9 <= -DAT_0004c24c) {
          cVar9 = -(char)DAT_0004c24c;
        }
        if (DAT_0004c24c < (short)cVar9) {
          cVar9 = (char)DAT_0004c24c;
        }
        *(int *)((int)&DAT_00049de4 + iVar3) = (DAT_0004c24c >> 2) + 1;
        (&DAT_00049dda)[iVar3] = (&DAT_00049dda)[iVar3] - cVar9;
      }
      iVar6 = FUN_0000f368(puVar10);
    }
    else {
      *(int *)((int)&DAT_00049de4 + iVar3) = DAT_0004c24c;
      if ((*(short *)(&DAT_00049e30 + iVar3) != 0) && (**(short **)(&DAT_00049db0 + iVar3) < 0x51))
      {
        *(undefined2 *)(&DAT_00049e30 + iVar3) = 0;
        do {
          uVar7 = FUN_0001a77c((short)iVar4);
          uVar11 = (undefined2)((uint)uVar7 >> 0x10);
          sVar8 = FUN_00013f12(puVar10,uVar11,(short)uVar7);
          if (sVar8 != 0) {
            (&DAT_00049ddb)[iVar3] = (&DAT_00049ddb)[iVar3] + '@';
            bVar2 = true;
            goto LAB_0000f674;
          }
          sVar8 = FUN_00013f7c(puVar10,uVar11,(short)uVar7);
          if (sVar8 != 0) {
            (&DAT_00049ddb)[iVar3] = (&DAT_00049ddb)[iVar3] + -0x40;
            bVar2 = true;
            goto LAB_0000f674;
          }
          sVar8 = FUN_00013fea(puVar10);
          if (sVar8 == 0) goto LAB_0000f664;
          sVar8 = FUN_00013f12(puVar10,0,0);
        } while ((sVar8 != 0) || (sVar8 = FUN_00013f7c(puVar10,0,3), sVar8 != 0));
        (&DAT_00049ddb)[iVar3] = (&DAT_00049ddb)[iVar3] + -0x80;
        bVar2 = true;
LAB_0000f664:
        if (!bVar2) {
          iVar6 = FUN_0000f368(puVar10);
        }
      }
LAB_0000f674:
      *(undefined2 *)(&DAT_00049e30 + iVar3) = 0;
      bVar1 = (&DAT_00049ddb)[iVar3];
      if (bVar1 == 0x40) {
        unaff_D3 = *(int *)((int)&DAT_00049d76 + iVar3) - iVar6;
      }
      else if (bVar1 < 0x41) {
        if (bVar1 == 0) {
          unaff_D3 = *(int *)((int)&DAT_00049d70 + iVar3) - iVar6;
        }
      }
      else if (bVar1 == 0x80) {
        unaff_D3 = iVar6 - *(int *)((int)&DAT_00049d70 + iVar3);
      }
      else if (bVar1 == 0xc0) {
        unaff_D3 = iVar6 - *(int *)((int)&DAT_00049d76 + iVar3);
      }
      if (unaff_D3 < -8) {
        unaff_D3 = -8;
      }
      if (8 < unaff_D3) {
        unaff_D3 = 8;
      }
      (&DAT_00049dda)[iVar3] = (&DAT_00049ddb)[iVar3] + (char)unaff_D3;
    }
    sVar8 = *(short *)(&DAT_00049d74 + iVar3) + ((byte)(&DAT_00049ddb)[iVar3] >> 1) + 4;
    if (sVar8 < -8) {
      sVar8 = -8;
    }
    if (8 < sVar8) {
      sVar8 = 8;
    }
    *(int *)(&DAT_00049de0 + iVar3) = (int)-sVar8;
    FUN_00013c9a(puVar10,3,0xc860);
    FUN_0000df60();
  } while( true );
}


/* Address 000101e0 */

undefined4
FUN_000101e0(undefined2 *param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  
  piVar1 = (int *)FUN_0001af04(param_2);
  *(int **)(param_1 + 0x2c) = piVar1;
  if (piVar1 == (int *)0x0) {
    *param_1 = 0;
    uVar3 = 0;
  }
  else {
    puVar2 = (undefined4 *)FUN_000152a2(*(int *)(*piVar1 + 8) * 2 + 0x10);
    *(undefined4 **)(param_1 + 0x2f) = puVar2;
    if (puVar2 == (undefined4 *)0x0) {
      FUN_0001b002(param_2);
      *param_1 = 0;
      uVar3 = 0;
    }
    else {
      *(undefined4 *)*puVar2 = param_3;
      *(undefined4 *)(param_1 + 0x34) = param_4;
      *(undefined4 *)(param_1 + 0x32) = param_4;
      param_1[0x50] = 8;
      uVar3 = 1;
    }
  }
  return uVar3;
}


/* Address 00010252 */

int FUN_00010252(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_00049c50 - *(int *)(param_1 + 4);
  iVar2 = DAT_00049c56 - *(int *)(param_1 + 10);
  iVar1 = FUN_0000e540(iVar1,iVar1);
  iVar2 = FUN_0000e540(iVar2,iVar2);
  return iVar1 + iVar2;
}


/* Address 0001028e */

short FUN_0001028e(int param_1)

{
  if (((*(int *)(param_1 + 0x1e) <= *(int *)(param_1 + 4)) &&
      (*(int *)(param_1 + 4) < *(int *)(param_1 + 0x1a))) &&
     (*(int *)(param_1 + 0x26) <= *(int *)(param_1 + 10))) {
    return -(short)-(*(int *)(param_1 + 0x22) <= *(int *)(param_1 + 10));
  }
  return 1;
}


/* Address 000102c4 */

uint FUN_000102c4(int param_1)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  undefined2 uVar4;
  uint uVar5;
  short sVar6;
  int iVar7;
  
  uVar2 = (ushort)(*(int *)(param_1 + 4) >> 6) & 0xf;
  uVar5 = *(int *)(param_1 + 10) >> 6;
  uVar3 = (ushort)uVar5 & 0xf;
  sVar6 = *(short *)(&DAT_00049bb4)[*(short *)(param_1 + 0x40)] + -1;
  if (-1 < sVar6) {
    do {
      uVar5 = sVar6 * 0x14;
      iVar7 = *(int *)((short *)(&DAT_00049bb4)[*(short *)(param_1 + 0x40)] + 4) + uVar5;
      if (*(short *)(iVar7 + 10) <= (short)uVar2) {
        uVar4 = (undefined2)(uVar5 >> 0x10);
        sVar1 = *(short *)(iVar7 + 0x10) + *(short *)(iVar7 + 10);
        uVar5 = CONCAT22(uVar4,sVar1);
        if ((((short)uVar2 < sVar1) && (*(short *)(iVar7 + 0xe) <= (short)uVar3)) &&
           (sVar1 = *(short *)(iVar7 + 0x12) + *(short *)(iVar7 + 0xe),
           uVar5 = CONCAT22(uVar4,sVar1), (short)uVar3 < sVar1)) break;
      }
      sVar6 = sVar6 + -1;
    } while (sVar6 != -1);
    if (-1 < sVar6) {
      *(short *)(param_1 + 0x42) = sVar6;
      *(int *)(param_1 + 0x44) = iVar7;
      *(uint *)(param_1 + 0x4c) =
           (*(uint *)(param_1 + 4) & 0xfffffc00) + (int)(short)(*(short *)(iVar7 + 10) << 6);
      *(uint *)(param_1 + 0x54) =
           (*(uint *)(param_1 + 10) & 0xfffffc00) + (int)(short)(*(short *)(iVar7 + 0xe) << 6);
      *(int *)(param_1 + 0x48) =
           *(int *)(param_1 + 0x4c) + (int)(short)(*(short *)(iVar7 + 0x10) << 6);
      *(int *)(param_1 + 0x50) =
           *(int *)(param_1 + 0x54) + (int)(short)(*(short *)(iVar7 + 0x12) << 6);
      return 1;
    }
  }
  return uVar5 & 0xffff0000;
}


/* Address 0001039c */

int FUN_0001039c(int param_1,short param_2)

{
  int iVar1;
  
  if (param_2 < *(short *)(&DAT_00049bb4)[*(short *)(param_1 + 0x40)]) {
    iVar1 = *(int *)((short *)(&DAT_00049bb4)[*(short *)(param_1 + 0x40)] + 4) + param_2 * 0x14;
    *(short *)(param_1 + 0x42) = param_2;
    *(int *)(param_1 + 0x44) = iVar1;
    *(uint *)(param_1 + 0x4c) =
         (*(uint *)(param_1 + 4) & 0xfffffc00) + (int)(short)(*(short *)(iVar1 + 10) << 6);
    *(uint *)(param_1 + 0x54) =
         (*(uint *)(param_1 + 10) & 0xfffffc00) + (int)(short)(*(short *)(iVar1 + 0xe) << 6);
    *(int *)(param_1 + 0x48) =
         *(int *)(param_1 + 0x4c) + (int)(short)(*(short *)(iVar1 + 0x10) << 6);
    *(int *)(param_1 + 0x50) =
         *(int *)(param_1 + 0x54) + (int)(short)(*(short *)(iVar1 + 0x12) << 6);
    iVar1 = 1;
  }
  else {
    iVar1 = (((int)*(short *)(param_1 + 0x40) & 0x3fffffffU) >> 0xe) << 0x10;
  }
  return iVar1;
}


/* Address 00010430 */

uint FUN_00010430(int param_1,short param_2,short param_3)

{
  uint uVar1;
  uint uVar2;
  short in_D1w;
  ushort unaff_D3w;
  char cVar3;
  
  uVar2 = *(short *)(param_1 + 0x40) * 4;
  if ((*(short *)((&DAT_00049bb4)[*(short *)(param_1 + 0x40)] + 2) <= param_2) ||
     (uVar1 = *(int *)((&DAT_00049bb4)[*(short *)(param_1 + 0x40)] + 0xc) + param_2 * 0x1c,
     uVar2 = uVar1, *(short *)(uVar1 + 0x1a) == -1)) goto LAB_00010518;
  if (param_3 == 1) {
    in_D1w = *(short *)(param_1 + 0x4a) - *(short *)(param_1 + 6);
    cVar3 = *(char *)(uVar1 + 0xd);
LAB_000104c2:
    unaff_D3w = (ushort)cVar3;
  }
  else {
    if (1 < param_3) {
      if (param_3 == 2) {
        in_D1w = *(short *)(param_1 + 0x52) - *(short *)(param_1 + 0xc);
        cVar3 = *(char *)(uVar1 + 0xf);
      }
      else {
        if (param_3 != 3) goto LAB_000104c4;
        in_D1w = *(short *)(param_1 + 0xc) - *(short *)(param_1 + 0x56);
        cVar3 = *(char *)(uVar1 + 0x11);
      }
      goto LAB_000104c2;
    }
    if (param_3 == 0) {
      in_D1w = *(short *)(param_1 + 6) - *(short *)(param_1 + 0x4e);
      cVar3 = *(char *)(uVar1 + 0xb);
      goto LAB_000104c2;
    }
  }
LAB_000104c4:
  uVar2 = CONCAT22((short)(uVar1 >> 0x10),in_D1w >> 6);
  if (unaff_D3w == (in_D1w >> 6 & 0xfU)) {
    *(undefined2 *)(param_1 + 0x16) = 0;
    *(undefined2 *)(param_1 + 0x18) = *(undefined2 *)(uVar1 + 0x1a);
    *(int *)(param_1 + 0x1e) = (int)*(short *)(uVar1 + 0x12) << 6;
    *(int *)(param_1 + 0x26) = (int)*(short *)(uVar1 + 0x14) << 6;
    *(int *)(param_1 + 0x1a) = *(int *)(param_1 + 0x1e) + *(short *)(uVar1 + 0x16) * 0x40;
    *(int *)(param_1 + 0x22) = *(int *)(param_1 + 0x26) + *(short *)(uVar1 + 0x18) * 0x40;
    return 1;
  }
LAB_00010518:
  return uVar2 & 0xffff0000;
}


/* Address 00010520 */

uint FUN_00010520(int param_1)

{
  short sVar1;
  undefined2 uVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  short sVar6;
  int iVar7;
  
  uVar3 = *(int *)(param_1 + 10) - *(int *)(param_1 + 0x26);
  uVar5 = uVar3 >> 6;
  uVar4 = *DAT_00049c18 - 1;
  if (-1 < (int)((uint)uVar4 << 0x10)) {
    do {
      uVar3 = (short)uVar4 * 0x18;
      iVar7 = *(int *)(DAT_00049c18 + 2) + uVar3;
      sVar6 = (short)((uint)(*(int *)(param_1 + 4) - *(int *)(param_1 + 0x1e)) >> 6);
      if (*(short *)(iVar7 + 2) <= sVar6) {
        uVar2 = (undefined2)(uVar3 >> 0x10);
        sVar1 = *(short *)(iVar7 + 6) + *(short *)(iVar7 + 2);
        uVar3 = CONCAT22(uVar2,sVar1);
        if (((sVar6 < sVar1) && (sVar6 = (short)uVar5, *(short *)(iVar7 + 4) <= sVar6)) &&
           (sVar1 = *(short *)(iVar7 + 8) + *(short *)(iVar7 + 4), uVar3 = CONCAT22(uVar2,sVar1),
           sVar6 < sVar1)) break;
      }
      uVar4 = uVar4 - 1;
    } while (uVar4 != 0xffff);
    if (-1 < (short)uVar4) {
      *(ushort *)(param_1 + 0x2a) = uVar4;
      *(int *)(param_1 + 0x2c) = iVar7;
      *(int *)(param_1 + 0x34) = *(int *)(param_1 + 0x1e) + (int)(short)(*(short *)(iVar7 + 2) << 6)
      ;
      *(int *)(param_1 + 0x3c) = *(int *)(param_1 + 0x26) + (int)(short)(*(short *)(iVar7 + 4) << 6)
      ;
      *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x34) + (int)(short)(*(short *)(iVar7 + 6) << 6)
      ;
      *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x3c) + (int)(short)(*(short *)(iVar7 + 8) << 6)
      ;
      return 1;
    }
  }
  return uVar3 & 0xffff0000;
}


/* Address 000105da */

uint FUN_000105da(int param_1)

{
  short sVar1;
  undefined2 uVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  short sVar6;
  int iVar7;
  
  uVar3 = *(int *)(param_1 + 8) - DAT_00049c72;
  uVar5 = uVar3 >> 6;
  uVar4 = *DAT_00049c18 - 1;
  if (-1 < (int)((uint)uVar4 << 0x10)) {
    do {
      uVar3 = (short)uVar4 * 0x18;
      iVar7 = *(int *)(DAT_00049c18 + 2) + uVar3;
      sVar6 = (short)((uint)(*(int *)(param_1 + 2) - DAT_00049c6a) >> 6);
      if (*(short *)(iVar7 + 2) <= sVar6) {
        uVar2 = (undefined2)(uVar3 >> 0x10);
        sVar1 = *(short *)(iVar7 + 6) + *(short *)(iVar7 + 2);
        uVar3 = CONCAT22(uVar2,sVar1);
        if (((sVar6 < sVar1) && (sVar6 = (short)uVar5, *(short *)(iVar7 + 4) <= sVar6)) &&
           (sVar1 = *(short *)(iVar7 + 8) + *(short *)(iVar7 + 4), uVar3 = CONCAT22(uVar2,sVar1),
           sVar6 < sVar1)) break;
      }
      uVar4 = uVar4 - 1;
    } while (uVar4 != 0xffff);
    if (-1 < (short)uVar4) {
      *(ushort *)(param_1 + 0x10) = uVar4;
      return 1;
    }
  }
  return uVar3 & 0xffff0000;
}


/* Address 00010652 */

uint FUN_00010652(int param_1,short param_2)

{
  uint in_D0;
  uint uVar1;
  int iVar2;
  
  if (param_2 < *DAT_00049c18) {
    iVar2 = *(int *)(DAT_00049c18 + 2) + param_2 * 0x18;
    *(short *)(param_1 + 0x2a) = param_2;
    *(int *)(param_1 + 0x2c) = iVar2;
    *(int *)(param_1 + 0x34) = *(int *)(param_1 + 0x1e) + (int)(short)(*(short *)(iVar2 + 2) << 6);
    *(int *)(param_1 + 0x3c) = *(int *)(param_1 + 0x26) + (int)(short)(*(short *)(iVar2 + 4) << 6);
    *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x34) + (int)(short)(*(short *)(iVar2 + 6) << 6);
    *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x3c) + (int)(short)(*(short *)(iVar2 + 8) << 6);
    uVar1 = 1;
  }
  else {
    uVar1 = in_D0 & 0xffff0000;
  }
  return uVar1;
}


/* Address 00010734 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00010734(void)

{
  undefined1 auStack_36 [54];
  
  _DAT_00f02268 = 0;
  _DAT_00f0226c = 0;
  _DAT_00f02200 = &DAT_000b29d0;
  _DAT_00f02204 = 0x1820;
  _DAT_00f0220c = 0;
  _DAT_00f0223c = 0x113b0;
  _DAT_00f02238 = 0x10200;
  if (_DAT_000403cc != 0) {
    FUN_0001b45a(auStack_36,s_wx___8ld_000106e0,DAT_000400ec);
    FUN_000149ae(0x14,2,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_wy___8ld_000106eb,DAT_000400f0);
    FUN_000149ae(0x14,0xc,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_wz___8ld_000106f6,DAT_000400f4);
    FUN_000149ae(0x14,0x16,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_yaw___8ld_00010701,DAT_000400fc);
    FUN_000149ae(0x78,2,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_pitch__8ld_0001070c,DAT_000400f8);
    FUN_000149ae(0x78,0xc,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_roll___8ld_00010717,DAT_00040100);
    FUN_000149ae(0x78,0x16,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,s_turtles___8ld_00010722,(int)DAT_000403d0);
    FUN_000149ae(0x14,0x20,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
    FUN_0001b45a(auStack_36,&DAT_00010730,(uint)DAT_000403ca * 0x18 + 0x3fb0c);
    FUN_000149ae(0x14,0x2a,auStack_36,&DAT_000b29d0,0x3e08,&DAT_0004c3e0,3,0);
  }
  return;
}


/* Address 00010968 */

void FUN_00010968(short param_1,short param_2)

{
  short sVar1;
  undefined1 *puVar2;
  
  sVar1 = 0;
  puVar2 = &DAT_00047b88 + param_1 * 0x40;
  if ((int)param_2 << 6 != 0) {
    do {
      *puVar2 = 0;
      sVar1 = sVar1 + 1;
      puVar2 = puVar2 + 1;
    } while ((uint)(int)sVar1 < (uint)((int)param_2 << 6));
  }
  return;
}


/* Address 00010990 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00010990(void)

{
  FUN_0001aa40(3);
  FUN_00018160();
  DAT_000403dc = 0;
  _DAT_000403e0 = 0;
  DAT_000403d8 = 0xffff;
  DAT_000403d0 = 0;
  _DAT_00040400 = 0;
  DAT_0004040a = 0;
  DAT_00040406 = 0;
  DAT_00040402 = 0;
  FUN_00010968(0,1);
  _DAT_00047b88 = 0x4000;
  _DAT_00047b8a = 0;
  _DAT_00047b8c = 0;
  _DAT_00047b8e = 0;
  _DAT_00047b90 = 0x4000;
  _DAT_00047b92 = 0;
  _DAT_00047b94 = 0;
  _DAT_00047b96 = 0;
  _DAT_00047b98 = 0x4000;
  FUN_00010a6a(1);
  FUN_00011762(1,*(undefined4 *)(DAT_000400e6 + 4),*(undefined4 *)(DAT_000400e6 + 8),
               (short)((uint)*(undefined4 *)(DAT_000400e6 + 0xc) >> 0x10),
               (short)*(undefined4 *)(DAT_000400e6 + 0xc));
  DAT_00047b9a = 0;
  DAT_00047b9c = 0;
  DAT_00047b9e = 0;
  DAT_00049b8c = 0;
  DAT_00049b8e = 0;
  DAT_00049b90 = 0;
  return;
}


/* Address 00010a6a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00010a6a(ushort param_1)

{
  int iVar1;
  
  if (param_1 == 0xffff) {
    DAT_000403d6 = 2;
  }
  else {
    iVar1 = (uint)param_1 * 0x92;
    if (*(short *)(&DAT_0003d822 + iVar1) == 1) {
      DAT_000403d8 = -1;
      DAT_000403ca = param_1;
      DAT_000400e6 = &DAT_0003d822 + iVar1;
      DAT_000403d6 = 3;
    }
    else if (*(short *)(&DAT_0003d822 + iVar1) == 0) {
      DAT_000403ca = param_1;
      DAT_000400e6 = &DAT_0003d822 + iVar1;
      FUN_0001ae88(DAT_000403d8);
      DAT_000403d8 = *(short *)(DAT_000400e6 + 2) << 4;
      DAT_000403da = FUN_0001ac68(DAT_000403d8);
      if (DAT_000403da != -1) {
        DAT_000403d0 = 0;
        DAT_000403d4 = *(undefined2 *)(DAT_000400e6 + 0x90);
        DAT_000403d2 = *(undefined2 *)(DAT_000400e6 + 0x8e);
        DAT_00023f84 = PTR_DAT_00023f88;
        _DAT_00023f7c = (&DAT_0004674c)[DAT_000403da * 2];
        _DAT_00024068 = (&DAT_0004674c)[(short)(DAT_000403da + 4) * 2];
        _DAT_00024070 = (&DAT_0004674c)[(short)(DAT_000403da + 4) * 2];
        _DAT_00024078 = (&DAT_0004674c)[(short)(DAT_000403da + 8) * 2];
        _DAT_00024080 = (&DAT_0004674c)[(short)(DAT_000403da + 8) * 2];
        _DAT_00024088 = (&DAT_0004674c)[(short)(DAT_000403da + 0xc) * 2];
        _DAT_00024090 = (&DAT_0004674c)[(short)(DAT_000403da + 0xc) * 2];
        DAT_000403d6 = 0;
      }
    }
  }
  return;
}


/* Address 00010ba4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00010ba4(void)

{
  if (0 < DAT_000403d4) {
    DAT_000403d4 = DAT_000403d4 + -1;
    return;
  }
  DAT_000403d4 = *(undefined2 *)(DAT_000400e6 + 0x90);
  DAT_000403d0 = DAT_000403d0 + 1;
  if (DAT_000403d2 <= (short)DAT_000403d0) {
    DAT_000403d0 = 0;
  }
  DAT_00023f84 = (&DAT_00023f84)[(short)((DAT_000403d0 & 1) + 1)];
  _DAT_00023f7c = (&DAT_0004674c)[(short)(DAT_000403da + ((short)DAT_000403d0 >> 1)) * 2];
  return;
}


/* Address 00010c6e */

void FUN_00010c6e(short param_1)

{
  if (param_1 == 0) {
    if (0 < DAT_000403dc) {
      DAT_000403dc = DAT_000403dc + -1;
    }
  }
  else {
    *(short *)(&DAT_000403e0 + DAT_000403dc * 2) = param_1;
    DAT_000403dc = DAT_000403dc + 1;
  }
  FUN_00010a6a(*(undefined2 *)(DAT_000400e6 + 0x12 + param_1 * 0x14));
  return;
}


/* Address 00010cb6 */

void FUN_00010cb6(ushort param_1)

{
  int unaff_D2;
  int unaff_D3;
  int unaff_D4;
  
  FUN_0001102a();
  if (param_1 < *(ushort *)(DAT_000400e6 + 0x88)) {
    DAT_00040406 = 0;
    DAT_00040402 = 0;
    DAT_0004040a = 0;
    if (*(ushort *)(DAT_000400e6 + 0x10 + (short)param_1 * 0x14) < 6) {
                    /* WARNING: Could not recover jumptable at 0x00010d12. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)((int)&PTR_DAT_00010d16 +
                (int)*(short *)((int)&PTR_DAT_00010d16 +
                               (uint)*(ushort *)(DAT_000400e6 + 0x10 + (short)param_1 * 0x14) * 2)))
                ();
      return;
    }
    DAT_000400ec = *(int *)(DAT_000400e6 + 4) + unaff_D4;
    DAT_000400f0 = *(int *)(DAT_000400e6 + 8) + unaff_D3;
    DAT_000400f4 = *(int *)(DAT_000400e6 + 0xc) + unaff_D2;
    DAT_000400f8 = 0;
    DAT_00040100 = 0;
    DAT_000400fc = 0;
    DAT_00047b9a = (undefined2)unaff_D4;
    DAT_00047b9c = (undefined2)unaff_D3;
    DAT_00047b9e = (undefined2)unaff_D2;
  }
  return;
}


/* Address 00010e72 */

void FUN_00010e72(ushort param_1)

{
  int unaff_D2;
  int unaff_D3;
  int unaff_D4;
  
  FUN_0001102a();
  if (param_1 < *(ushort *)(DAT_000400e6 + 0x88)) {
    DAT_00040406 = 0;
    DAT_00040402 = 0;
    DAT_0004040a = 0;
    if (*(ushort *)(DAT_000400e6 + 0x10 + (short)param_1 * 0x14) < 6) {
                    /* WARNING: Could not recover jumptable at 0x00010ece. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)((int)&PTR_DAT_00010ed2 +
                (int)*(short *)((int)&PTR_DAT_00010ed2 +
                               (uint)*(ushort *)(DAT_000400e6 + 0x10 + (short)param_1 * 0x14) * 2)))
                ();
      return;
    }
    DAT_000400ec = *(int *)(DAT_000400e6 + 4) + unaff_D4;
    DAT_000400f0 = *(int *)(DAT_000400e6 + 8) + unaff_D3;
    DAT_000400f4 = *(int *)(DAT_000400e6 + 0xc) + unaff_D2;
    DAT_000400f8 = 0;
    DAT_00040100 = 0;
    DAT_000400fc = 0;
    DAT_00047b9a = (undefined2)unaff_D4;
    DAT_00047b9c = (undefined2)unaff_D3;
    DAT_00047b9e = (undefined2)unaff_D2;
  }
  return;
}


/* Address 0001102a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001102a(void)

{
  _DAT_00047b88 = 0x4000;
  _DAT_00047b8a = 0;
  _DAT_00047b8c = 0;
  _DAT_00047b8e = 0;
  _DAT_00047b90 = 0x4000;
  _DAT_00047b92 = 0;
  _DAT_00047b94 = 0;
  _DAT_00047b96 = 0;
  _DAT_00047b98 = 0x4000;
  DAT_00047b9a = 0;
  DAT_00047b9c = 0;
  DAT_00047b9e = 0;
  _DAT_00047bda = 0;
  _DAT_00047bdc = 0;
  _DAT_00047bde = 0;
  DAT_000400ec = *(undefined4 *)(DAT_000400e6 + 4);
  DAT_000400f0 = *(undefined4 *)(DAT_000400e6 + 8);
  DAT_000400f4 = *(undefined4 *)(DAT_000400e6 + 0xc);
  DAT_00040100 = 0;
  DAT_000400fc = 0;
  DAT_000400f8 = 0;
  DAT_00040104 = 0;
  DAT_00040406 = 0;
  DAT_0004040a = 0;
  DAT_00040402 = 0;
  return;
}


/* Address 000110d4 */

void FUN_000110d4(ushort *param_1,int param_2,undefined2 param_3)

{
  int iVar1;
  short sVar2;
  
  iVar1 = (uint)*param_1 * 0x20;
  switch(param_3) {
  case 0:
    *(short *)(param_2 + 0x24) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(short *)(param_2 + 0x26) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x28) = *(undefined2 *)(&DAT_000400de + iVar1);
    *(short *)(param_2 + 0x2a) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(short *)(param_2 + 0x2c) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2e) = *(undefined2 *)(&DAT_000400de + iVar1);
    *(short *)(param_2 + 0x30) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(short *)(param_2 + 0x32) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x34) = *(undefined2 *)(&DAT_000400de + iVar1);
    *(short *)(param_2 + 0x36) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(short *)(param_2 + 0x38) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x3a) = *(undefined2 *)(&DAT_000400de + iVar1);
    return;
  case 1:
    *(undefined2 *)(param_2 + 0x24) = *(undefined2 *)(&DAT_000400ca + iVar1);
    *(short *)(param_2 + 0x26) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(short *)(param_2 + 0x28) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2a) = *(undefined2 *)(&DAT_000400ca + iVar1);
    *(short *)(param_2 + 0x2c) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(short *)(param_2 + 0x2e) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x30) = *(undefined2 *)(&DAT_000400ca + iVar1);
    *(short *)(param_2 + 0x32) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(short *)(param_2 + 0x34) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x36) = *(undefined2 *)(&DAT_000400ca + iVar1);
    *(short *)(param_2 + 0x38) = *(short *)(&DAT_000400da + iVar1) << 3;
    sVar2 = *(short *)(&DAT_000400d2 + iVar1);
    break;
  case 2:
    *(short *)(param_2 + 0x24) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(short *)(param_2 + 0x26) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x28) = *(undefined2 *)(&DAT_000400d2 + iVar1);
    *(short *)(param_2 + 0x2a) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(short *)(param_2 + 0x2c) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2e) = *(undefined2 *)(&DAT_000400d2 + iVar1);
    *(short *)(param_2 + 0x30) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(short *)(param_2 + 0x32) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x34) = *(undefined2 *)(&DAT_000400d2 + iVar1);
    *(short *)(param_2 + 0x36) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(short *)(param_2 + 0x38) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x3a) = *(undefined2 *)(&DAT_000400d2 + iVar1);
    return;
  case 3:
    *(undefined2 *)(param_2 + 0x24) = *(undefined2 *)(&DAT_000400d6 + iVar1);
    *(short *)(param_2 + 0x26) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(short *)(param_2 + 0x28) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2a) = *(undefined2 *)(&DAT_000400d6 + iVar1);
    *(short *)(param_2 + 0x2c) = *(short *)(&DAT_000400ce + iVar1) << 3;
    *(short *)(param_2 + 0x2e) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x30) = *(undefined2 *)(&DAT_000400d6 + iVar1);
    *(short *)(param_2 + 0x32) = *(short *)(&DAT_000400da + iVar1) << 3;
    *(short *)(param_2 + 0x34) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x36) = *(undefined2 *)(&DAT_000400d6 + iVar1);
    *(short *)(param_2 + 0x38) = *(short *)(&DAT_000400da + iVar1) << 3;
    sVar2 = *(short *)(&DAT_000400de + iVar1);
    break;
  case 4:
    *(short *)(param_2 + 0x24) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x26) = *(undefined2 *)(&DAT_000400da + iVar1);
    *(short *)(param_2 + 0x28) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(short *)(param_2 + 0x2a) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2c) = *(undefined2 *)(&DAT_000400da + iVar1);
    *(short *)(param_2 + 0x2e) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(short *)(param_2 + 0x30) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x32) = *(undefined2 *)(&DAT_000400da + iVar1);
    *(short *)(param_2 + 0x34) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(short *)(param_2 + 0x36) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x38) = *(undefined2 *)(&DAT_000400da + iVar1);
    sVar2 = *(short *)(&DAT_000400de + iVar1);
    break;
  case 5:
    *(short *)(param_2 + 0x24) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x26) = *(undefined2 *)(&DAT_000400ce + iVar1);
    *(short *)(param_2 + 0x28) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(short *)(param_2 + 0x2a) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x2c) = *(undefined2 *)(&DAT_000400ce + iVar1);
    *(short *)(param_2 + 0x2e) = *(short *)(&DAT_000400de + iVar1) << 3;
    *(short *)(param_2 + 0x30) = *(short *)(&DAT_000400ca + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x32) = *(undefined2 *)(&DAT_000400ce + iVar1);
    *(short *)(param_2 + 0x34) = *(short *)(&DAT_000400d2 + iVar1) << 3;
    *(short *)(param_2 + 0x36) = *(short *)(&DAT_000400d6 + iVar1) << 3;
    *(undefined2 *)(param_2 + 0x38) = *(undefined2 *)(&DAT_000400ce + iVar1);
    *(short *)(param_2 + 0x3a) = *(short *)(&DAT_000400de + iVar1) << 3;
  default:
    return;
  }
  *(short *)(param_2 + 0x3a) = sVar2 << 3;
  return;
}


/* Address 00011384 */

void FUN_00011384(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_00049b88 + 1;
  iVar2 = iVar1 * 0x40;
  DAT_00049b88 = iVar1;
  *(undefined2 *)(&DAT_00047b88 + iVar2) = 0x4000;
  *(undefined2 *)(&DAT_00047b8a + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b8c + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b8e + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b90 + iVar2) = 0x4000;
  *(undefined2 *)(&DAT_00047b92 + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b94 + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b96 + iVar2) = 0;
  *(undefined2 *)(&DAT_00047b98 + iVar2) = 0x4000;
  (&DAT_00047b9a)[iVar1 * 0x20] = -DAT_00049b8c;
  (&DAT_00047b9c)[iVar1 * 0x20] = -DAT_00049b8e;
  (&DAT_00047b9e)[iVar1 * 0x20] = -DAT_00049b90;
  FUN_000110d4(DAT_000400e6,&DAT_00047b88 + iVar2,DAT_000403ce);
  iVar1 = DAT_00049b88 * 0x40;
  *(undefined2 *)(&DAT_00047ba8 + iVar1) = 7;
  *(undefined **)(&DAT_00047bc4 + iVar1) = PTR_DAT_000400c4;
  *(undefined2 *)(&DAT_00047ba0 + (DAT_00049b88 + -1) * 0x40) = DAT_00049b88._2_2_;
  return;
}


/* Address 0001142e */

void FUN_0001142e(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int unaff_D4;
  int unaff_D5;
  int unaff_D6;
  ushort *puVar6;
  ushort uVar7;
  
  uVar7 = 0;
  puVar6 = DAT_000400e6;
  if (DAT_000400e6[0x44] != 0) {
    do {
      DAT_00049b88 = DAT_00049b88 + 1;
      iVar1 = DAT_00049b88 * 0x40;
      *(undefined2 *)(&DAT_00047b88 + iVar1) = 0x4000;
      *(undefined2 *)(&DAT_00047b8a + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b8c + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b8e + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b90 + iVar1) = 0x4000;
      *(undefined2 *)(&DAT_00047b92 + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b94 + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b96 + iVar1) = 0;
      *(undefined2 *)(&DAT_00047b98 + iVar1) = 0x4000;
      iVar2 = DAT_00049b88;
      iVar1 = (uint)*puVar6 * 0x20;
      uVar3 = 0;
      uVar4 = 0;
      uVar5 = 0;
      switch(puVar6[(short)uVar7 * 10 + 8]) {
      case 0:
        unaff_D6 = DAT_0003d6ca +
                   (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        unaff_D5 = DAT_0003d6ce +
                   (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_D4 = DAT_0003d6d2 + *(int *)(&DAT_000400dc + iVar1);
        uVar3 = DAT_0003d71a;
        uVar4 = DAT_0003d716;
        uVar5 = DAT_0003d712;
        break;
      case 1:
        unaff_D6 = DAT_0003d6d6 + *(int *)(&DAT_000400c8 + iVar1);
        unaff_D5 = DAT_0003d6da +
                   (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_D4 = DAT_0003d6de +
                   (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        uVar3 = DAT_0003d726;
        uVar4 = DAT_0003d722;
        uVar5 = DAT_0003d71e;
        break;
      case 2:
        unaff_D6 = DAT_0003d6e2 +
                   (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        unaff_D5 = DAT_0003d6e6 +
                   (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_D4 = DAT_0003d6ea + *(int *)(&DAT_000400d0 + iVar1);
        uVar3 = DAT_0003d732;
        uVar4 = DAT_0003d72e;
        uVar5 = DAT_0003d72a;
        break;
      case 3:
        unaff_D6 = DAT_0003d6ee + *(int *)(&DAT_000400d4 + iVar1);
        unaff_D5 = DAT_0003d6f2 +
                   (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_D4 = DAT_0003d6f6 +
                   (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        uVar3 = DAT_0003d73e;
        uVar4 = DAT_0003d73a;
        uVar5 = DAT_0003d736;
        break;
      case 4:
        unaff_D6 = DAT_0003d6fa +
                   (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        unaff_D5 = DAT_0003d6fe + *(int *)(&DAT_000400cc + iVar1);
        unaff_D4 = DAT_0003d702 +
                   (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        uVar3 = DAT_0003d74a;
        uVar4 = DAT_0003d746;
        uVar5 = DAT_0003d742;
        break;
      case 5:
        unaff_D6 = DAT_0003d706 +
                   (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        unaff_D5 = DAT_0003d70a + *(int *)(&DAT_000400d8 + iVar1);
        unaff_D4 = DAT_0003d70e +
                   (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        uVar3 = DAT_0003d756;
        uVar4 = DAT_0003d752;
        uVar5 = DAT_0003d74e;
      }
      iVar1 = DAT_00049b88 * 0x40;
      (&DAT_00047b9a)[DAT_00049b88 * 0x20] = 0;
      (&DAT_00047b9c)[iVar2 * 0x20] = 0;
      (&DAT_00047b9e)[iVar2 * 0x20] = 0;
      FUN_0000e26c(&DAT_00047b88 + iVar1,uVar3,uVar4,uVar5,0);
      iVar2 = DAT_00049b88;
      iVar1 = DAT_00049b88 * 0x40;
      *(undefined2 *)(&DAT_00047bac + iVar1) = DAT_0003d75a;
      *(undefined2 *)(&DAT_00047bae + iVar1) = DAT_0003d75c;
      *(undefined2 *)(&DAT_00047bb0 + iVar1) = DAT_0003d75e;
      *(undefined2 *)(&DAT_00047bb2 + iVar1) = DAT_0003d760;
      *(undefined2 *)(&DAT_00047bb4 + iVar1) = DAT_0003d762;
      *(undefined2 *)(&DAT_00047bb6 + iVar1) = DAT_0003d764;
      *(undefined2 *)(&DAT_00047bb8 + iVar1) = DAT_0003d766;
      *(undefined2 *)(&DAT_00047bba + iVar1) = DAT_0003d768;
      *(undefined2 *)(&DAT_00047bbc + iVar1) = DAT_0003d76a;
      *(undefined2 *)(&DAT_00047bbe + iVar1) = DAT_0003d76c;
      *(undefined2 *)(&DAT_00047bc0 + iVar1) = DAT_0003d76e;
      *(undefined2 *)(&DAT_00047bc2 + iVar1) = DAT_0003d770;
      (&DAT_00047b9a)[iVar2 * 0x20] = (short)unaff_D6 - DAT_00049b8c;
      (&DAT_00047b9c)[iVar2 * 0x20] = (short)unaff_D5 - DAT_00049b8e;
      (&DAT_00047b9e)[iVar2 * 0x20] = (short)unaff_D4 - DAT_00049b90;
      *(undefined2 *)(&DAT_00047ba8 + iVar1) = 7;
      puVar6 = DAT_000400e6;
      *(undefined **)(&DAT_00047bc4 + iVar1) =
           (&PTR_PTR_0003d772)[(uint)DAT_000400e6[(short)uVar7 * 10 + 10] * 2];
      *(undefined2 *)(&DAT_00047ba0 + (DAT_00049b88 + -1) * 0x40) = DAT_00049b88._2_2_;
      uVar7 = uVar7 + 1;
    } while (uVar7 < puVar6[0x44]);
  }
  return;
}


/* Address 00011762 */

void FUN_00011762(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  int iVar2;
  
  if (DAT_000400e4 < 0x10) {
    iVar2 = DAT_000400e4 * 0x2e;
    (&DAT_000400ea)[DAT_000400e4 * 0x17] = param_1;
    *(undefined4 *)((int)&DAT_000400ec + iVar2) = param_2;
    *(undefined4 *)((int)&DAT_000400f0 + iVar2) = param_3;
    *(undefined4 *)((int)&DAT_000400f4 + iVar2) = param_4;
    *(undefined4 *)((int)&DAT_000400f8 + iVar2) = 0;
    *(undefined4 *)((int)&DAT_000400fc + iVar2) = 0;
    *(undefined4 *)((int)&DAT_00040100 + iVar2) = 0;
    *(undefined4 *)((int)&DAT_00040104 + iVar2) = 0;
    *(undefined4 *)(&DAT_00040108 + iVar2) = 0;
    *(undefined4 *)(&DAT_0004010c + iVar2) = 0;
    *(undefined4 *)(&DAT_00040110 + iVar2) = 0;
    *(undefined4 *)(&DAT_00040114 + iVar2) = 0;
    do {
      DAT_000400e4 = DAT_000400e4 + 1;
      if ((&DAT_000400ea)[DAT_000400e4 * 0x17] == 0) {
        if (DAT_000400e4 < 0x10) {
          return;
        }
        break;
      }
    } while (DAT_000400e4 < 0x10);
    DAT_000400e4 = 1;
    sVar1 = DAT_00040118;
    while ((sVar1 != 0 && (DAT_000400e4 < 0x10))) {
      DAT_000400e4 = DAT_000400e4 + 1;
      sVar1 = (&DAT_000400ea)[DAT_000400e4 * 0x17];
    }
  }
  return;
}


/* Address 00011828 */

void FUN_00011828(void)

{
  short sVar1;
  
  sVar1 = 0;
  do {
    if ((&DAT_000400ea)[sVar1 * 0x17] == 1) {
      FUN_00011b4c();
      if (0 < DAT_00040104) {
        FUN_0001186a();
      }
      FUN_00011d1a();
    }
    sVar1 = sVar1 + 1;
  } while (sVar1 < 0x10);
  return;
}


/* Address 0001186a */

void FUN_0001186a(void)

{
  int iVar1;
  undefined2 uVar2;
  int in_D1;
  ushort uVar3;
  int unaff_D4;
  int iVar4;
  int unaff_A3;
  int unaff_A4;
  int unaff_A5;
  int unaff_A6;
  
  iVar1 = (uint)*DAT_000400e6 * 0x20;
  uVar3 = 0;
  if (DAT_000400e6[0x44] != 0) {
    do {
      switch(DAT_000400e6[(short)uVar3 * 10 + 8]) {
      case 0:
        iVar4 = DAT_0003d6ca +
                (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        in_D1 = iVar4 + -0x20;
        unaff_A6 = iVar4 + 0x20;
        iVar4 = DAT_0003d6ce +
                (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_A5 = iVar4 + -0x20;
        unaff_A4 = iVar4 + 0x20;
        unaff_D4 = DAT_0003d6d2 + *(int *)(&DAT_000400dc + iVar1);
        unaff_A3 = unaff_D4 + -0x20;
        goto switchD_000118b0_default;
      case 1:
        in_D1 = DAT_0003d6d6 + *(int *)(&DAT_000400c8 + iVar1);
        unaff_A6 = in_D1 + 0x20;
        iVar4 = DAT_0003d6da +
                (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_A5 = iVar4 + -0x20;
        unaff_A4 = iVar4 + 0x20;
        iVar4 = DAT_0003d6de +
                (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        break;
      case 2:
        iVar4 = DAT_0003d6e2 +
                (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        in_D1 = iVar4 + -0x20;
        unaff_A6 = iVar4 + 0x20;
        iVar4 = DAT_0003d6e6 +
                (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_A5 = iVar4 + -0x20;
        unaff_A4 = iVar4 + 0x20;
        unaff_A3 = DAT_0003d6ea + *(int *)(&DAT_000400d0 + iVar1);
        unaff_D4 = unaff_A3 + 0x20;
        goto switchD_000118b0_default;
      case 3:
        unaff_A6 = DAT_0003d6ee + *(int *)(&DAT_000400d4 + iVar1);
        in_D1 = unaff_A6 + -0x20;
        iVar4 = DAT_0003d6f2 +
                (*(int *)(&DAT_000400d8 + iVar1) + *(int *)(&DAT_000400cc + iVar1) >> 1);
        unaff_A5 = iVar4 + -0x20;
        unaff_A4 = iVar4 + 0x20;
        iVar4 = DAT_0003d6f6 +
                (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        break;
      case 4:
        iVar4 = DAT_0003d6fa +
                (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        in_D1 = iVar4 + -0x20;
        unaff_A6 = iVar4 + 0x20;
        unaff_A5 = DAT_0003d6fe + *(int *)(&DAT_000400cc + iVar1);
        unaff_A4 = unaff_A5 + 0x20;
        iVar4 = DAT_0003d702 +
                (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        break;
      case 5:
        iVar4 = DAT_0003d706 +
                (*(int *)(&DAT_000400d4 + iVar1) + *(int *)(&DAT_000400c8 + iVar1) >> 1);
        in_D1 = iVar4 + -0x20;
        unaff_A6 = iVar4 + 0x20;
        unaff_A4 = DAT_0003d70a + *(int *)(&DAT_000400d8 + iVar1);
        unaff_A5 = unaff_A4 + -0x20;
        iVar4 = DAT_0003d70e +
                (*(int *)(&DAT_000400dc + iVar1) + *(int *)(&DAT_000400d0 + iVar1) >> 1);
        break;
      default:
        goto switchD_000118b0_default;
      }
      unaff_A3 = iVar4 + -0x20;
      unaff_D4 = iVar4 + 0x20;
switchD_000118b0_default:
      in_D1 = *(int *)(DAT_000400e6 + 2) + in_D1;
      unaff_A6 = *(int *)(DAT_000400e6 + 2) + unaff_A6;
      unaff_A5 = *(int *)(DAT_000400e6 + 4) + unaff_A5;
      unaff_A4 = *(int *)(DAT_000400e6 + 4) + unaff_A4;
      unaff_A3 = *(int *)(DAT_000400e6 + 6) + unaff_A3;
      unaff_D4 = *(int *)(DAT_000400e6 + 6) + unaff_D4;
      if ((((in_D1 <= DAT_000400ec) && (DAT_000400ec <= unaff_A6)) && (unaff_A5 <= DAT_000400f0)) &&
         (((DAT_000400f0 <= unaff_A4 && (unaff_A3 <= DAT_000400f4)) && (DAT_000400f4 <= unaff_D4))))
      {
        FUN_00010c6e(uVar3);
        if (uVar3 == 0) {
          uVar2 = *(undefined2 *)(&DAT_000403e0 + DAT_000403dc * 2);
        }
        else {
          uVar2 = 0;
        }
        FUN_00010cb6(uVar2);
        return;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < DAT_000400e6[0x44]);
  }
  return;
}


/* Address 00011ad4 */

void FUN_00011ad4(void)

{
  FUN_00010968(1,7);
  DAT_00049b88 = 0;
  DAT_000403ce = *(undefined2 *)
                  (((DAT_00040100 + 0x20U & 0xff) >> 6) * 0x20 + 0x3d7a2 +
                   ((DAT_000400fc + 0x20U & 0xff) >> 6) * 8 +
                  ((DAT_000400f8 + 0x20U & 0xff) >> 6) * 2);
  FUN_00011384();
  FUN_00010ba4();
  FUN_0001142e();
  FUN_00010734();
  return;
}


/* Address 00011b4c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00011b4c(void)

{
  uint uVar1;
  
  FUN_0000e4c0();
  uVar1 = DAT_00049bac;
  _DAT_000403cc = (ushort)(_DAT_00049ba4 >> 9) & 1;
  DAT_0004040a = 0;
  DAT_00040406 = 0;
  DAT_00040402 = 0;
  if ((_DAT_00049ba4 & 0x100000) == 0) {
    if ((_DAT_00049ba4 & 0x200000) == 0) {
      DAT_00040104 = 0;
    }
    else if ((_DAT_00049ba4 & 0x2000000) == 0) {
      if (-0x10 < DAT_00040104) {
        DAT_00040104 = DAT_00040104 + -1;
      }
    }
    else {
      DAT_00040402 = 0xfffffffe;
    }
  }
  else if ((_DAT_00049ba4 & 0x2000000) == 0) {
    if (DAT_00040104 < 0x10) {
      DAT_00040104 = DAT_00040104 + 1;
    }
  }
  else {
    DAT_00040402 = 2;
  }
  if ((DAT_00049bac & 0x2000) != 0) {
    _DAT_00040400 = 1;
  }
  if ((_DAT_00049ba4 & 0x400000) == 0) {
    if ((_DAT_00049ba4 & 0x800000) != 0) {
      DAT_0004040a = 0xfffffffe;
    }
  }
  else {
    DAT_0004040a = 2;
  }
  if (((DAT_00049bac & 0x10) != 0) && (*(short *)(DAT_000400e6 + 0x88) != 0)) {
    FUN_00010c6e(0);
    FUN_00010e72(*(undefined2 *)(&DAT_000403e0 + DAT_000403dc * 2));
  }
  if (((uVar1 & 0x80000) != 0) && (1 < *(ushort *)(DAT_000400e6 + 0x88))) {
    FUN_00010c6e(1);
    FUN_00010cb6(0);
  }
  if (((char)uVar1 < '\0') && (2 < *(ushort *)(DAT_000400e6 + 0x88))) {
    FUN_00010c6e(2);
    FUN_00010cb6(0);
  }
  if (((uVar1 & 8) != 0) && (3 < *(ushort *)(DAT_000400e6 + 0x88))) {
    FUN_00010c6e(3);
    FUN_00010cb6(0);
  }
  if (((uVar1 & 0x40000) != 0) && (4 < *(ushort *)(DAT_000400e6 + 0x88))) {
    FUN_00010c6e(4);
    FUN_00010cb6(0);
  }
  if (((uVar1 & 0x40) != 0) && (5 < *(ushort *)(DAT_000400e6 + 0x88))) {
    FUN_00010c6e(5);
    FUN_00010cb6(0);
  }
  if ((uVar1 & 0x10000) != 0) {
    DAT_0004040a = 0;
    DAT_00040406 = 0;
    DAT_00040402 = 0;
    FUN_0001102a();
  }
  return;
}


/* Address 00011d1a */

void FUN_00011d1a(void)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  DAT_000400f8 = DAT_00040402 + DAT_000400f8 & 0xff;
  DAT_000400fc = DAT_0004040a + DAT_000400fc & 0xff;
  DAT_00040100 = DAT_00040406 + DAT_00040100 & 0xff;
  FUN_0000e26c(&DAT_00047b88,DAT_00040402,DAT_0004040a,DAT_00040406,DAT_00040104);
  puVar1 = DAT_000400e6;
  DAT_00040406 = 0;
  DAT_0004040a = 0;
  DAT_00040402 = 0;
  iVar5 = (int)DAT_00047b9a;
  iVar6 = (int)DAT_00047b9c;
  iVar7 = (int)DAT_00047b9e;
  DAT_00047b9a = 0;
  DAT_00047b9c = 0;
  DAT_00047b9e = 0;
  iVar5 = DAT_000400ec + iVar5;
  iVar2 = iVar5 - *(int *)(DAT_000400e6 + 2);
  iVar6 = DAT_000400f0 + iVar6;
  iVar3 = iVar6 - *(int *)(DAT_000400e6 + 4);
  iVar7 = DAT_000400f4 + iVar7;
  iVar4 = iVar7 - *(int *)(DAT_000400e6 + 6);
  iVar2 = FUN_0000e540(iVar2,iVar2);
  iVar3 = FUN_0000e540(iVar3,iVar3);
  iVar4 = FUN_0000e540(iVar4,iVar4);
  if ((uint)(iVar4 + iVar3 + iVar2) < *(uint *)(&DAT_000400e0 + (uint)*puVar1 * 0x20)) {
    DAT_000400ec = iVar5;
    DAT_000400f0 = iVar6;
    DAT_000400f4 = iVar7;
  }
  DAT_00049b8c = DAT_000400ec._2_2_ - puVar1[3];
  DAT_00049b8e = DAT_000400f0._2_2_ - puVar1[5];
  DAT_00049b90 = DAT_000400f4._2_2_ - puVar1[7];
  return;
}


/* Address 00011e6c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00011e6c(void)

{
  undefined *puStack_c;
  undefined4 local_8;
  
  puStack_c = PTR_DAT_00011e64;
  local_8 = DAT_00011e68;
  FUN_00010990();
  do {
    FUN_00011828();
    if (DAT_000403d6 != 1) {
      if (DAT_000403d6 < 2) {
        if (DAT_000403d6 == 0) {
          FUN_0000e03a((short)((uint)DAT_000bd83c >> 0x10),(short)DAT_000bd83c,0,0);
          if (_DAT_00040400 != 0) {
            FUN_00010c6e(0);
            FUN_0001102a();
          }
          FUN_00011ad4();
        }
      }
      else {
        if (DAT_000403d6 == 2) {
          return;
        }
        if (DAT_000403d6 == 3) {
          FUN_00016bf4(*(undefined4 *)(DAT_000400e6 + 0x8e),&DAT_0004c3e0,DAT_000bd830,0x3e20,0xe0,
                       0xb4,&puStack_c);
          FUN_00010c6e(0);
          FUN_00010e72(*(undefined2 *)(&DAT_000403e0 + DAT_000403dc * 2));
          FUN_00011d1a();
        }
      }
    }
    if (0 < DAT_00049b88) {
      FUN_0000e19e();
      FUN_0000e202();
      do {
      } while (_DAT_0010a684 != 0);
    }
    FUN_0000e098();
    FUN_00017f14();
  } while( true );
}


/* Address 00012620 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00012620(short param_1)

{
  byte bVar1;
  int iVar2;
  short sVar3;
  byte *pbVar4;
  byte *pbVar5;
  
  iVar2 = param_1 * 0xe;
  sVar3 = *(short *)(&DAT_000410c6 + iVar2);
  _DAT_00f02200 = DAT_000bd830;
  _DAT_00f02204 = s_TO__Paul_Krantz__Recruitment_Ope_00033c1c + 0x204;
  _DAT_00f0220c =
       (int)(short)(*(short *)(&DAT_000410c6 + iVar2) + *(short *)(&DAT_000410be + iVar2)) |
       (uint)(ushort)(*(short *)(&DAT_000410c6 + iVar2) + *(short *)(&DAT_000410c0 + iVar2)) << 0x10
  ;
  _DAT_00f02210 =
       (int)(short)(0xe0 - (*(short *)(&DAT_000410c2 + iVar2) +
                           *(short *)(&DAT_000410c6 + iVar2) * -2));
  _DAT_00f02214 = 0;
  _DAT_00f02218 = 0;
  _DAT_00f02220 = 0;
  _DAT_00f0221c = 1;
  _DAT_00f02268 = 0x88808880;
  _DAT_00f0226c = 0x88808880;
  _DAT_00f0223c =
       (int)(short)(*(short *)(&DAT_000410c2 + iVar2) + *(short *)(&DAT_000410c6 + iVar2) * -2) |
       (uint)(ushort)(*(short *)(&DAT_000410c4 + iVar2) + *(short *)(&DAT_000410c6 + iVar2) * -2) <<
       0x10;
  while (sVar3 != 0) {
    sVar3 = sVar3 + -1;
    _DAT_00f0220c =
         (int)(short)(*(short *)(&DAT_000410be + iVar2) + sVar3) |
         (uint)(ushort)(*(short *)(&DAT_000410c0 + iVar2) + sVar3) << 0x10;
    _DAT_00f02210 = 0xdf;
    _DAT_00f02268 = 0x88a088a0;
    _DAT_00f0226c = 0x88a088a0;
    _DAT_00f0223c = (uint)(ushort)(*(short *)(&DAT_000410c4 + iVar2) + sVar3 * -2) << 0x10 | 1;
  }
  _DAT_00f02238 = 0x1810200;
  iVar2 = param_1 * 0xe;
  pbVar4 = *(byte **)((int)&PTR_DAT_000410c8 + iVar2);
  do {
    FUN_000149ae(*(short *)(&DAT_000410be + iVar2) + (ushort)*pbVar4,
                 *(short *)(&DAT_000410c0 + iVar2) + (ushort)pbVar4[1],pbVar4 + 2,DAT_000bd830,
                 0x3e20,&DAT_0004c3e0,0x88ff,0);
    pbVar5 = pbVar4 + 2;
    do {
      pbVar4 = pbVar5 + 1;
      bVar1 = *pbVar5;
      pbVar5 = pbVar4;
    } while (bVar1 != 0);
  } while (*pbVar4 != 0);
  return;
}


/* Address 00013440 */

uint FUN_00013440(short param_1,short param_2)

{
  undefined2 uVar1;
  undefined4 in_D0;
  int iVar3;
  byte bVar4;
  ushort uVar5;
  int iVar2;
  
  uVar1 = (undefined2)((uint)in_D0 >> 0x10);
  iVar2 = CONCAT22(uVar1,param_1);
  if (param_1 < 0) {
    iVar2 = CONCAT22(uVar1,-param_1);
    if (param_2 < 0) {
      param_2 = -param_2;
      uVar5 = 2;
    }
    else {
      uVar5 = 1;
    }
  }
  else if (param_2 < 0) {
    param_2 = -param_2;
    uVar5 = 3;
  }
  else {
    uVar5 = 4;
  }
  if (param_2 == 0) {
    bVar4 = 0x40;
  }
  else {
    iVar3 = FUN_0000e588(iVar2 << 0x10,(int)param_2);
    bVar4 = 0;
    do {
      iVar2 = (short)(ushort)bVar4 * 4;
      if (iVar3 <= *(int *)(&DAT_00041f00 + iVar2)) break;
      bVar4 = bVar4 + 1;
    } while (bVar4 < 0x40);
  }
  if (uVar5 == 2) {
    bVar4 = 0x80 - bVar4;
  }
  else if (2 < uVar5) {
    if (uVar5 == 3) {
      bVar4 = bVar4 + 0x80;
    }
    else if (uVar5 == 4) {
      bVar4 = -bVar4;
    }
  }
  return CONCAT31((int3)((uint)iVar2 >> 8),bVar4) & 0xffff00ff;
}


/* Address 000134dc */

void FUN_000134dc(undefined2 param_1,short param_2,uint param_3,undefined2 param_4,uint param_5,
                 undefined1 param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  code *pcVar4;
  
  iVar2 = (int)param_2;
  iVar3 = iVar2 * 0xce;
  (&DAT_00049d6c)[iVar2 * 0x67] = param_1;
  (&DAT_00049d6e)[iVar2 * 0x67] = 0;
  *(uint *)((int)&DAT_00049d70 + iVar3) = param_3;
  *(undefined2 *)(&DAT_00049d74 + iVar3) = param_4;
  *(uint *)((int)&DAT_00049d76 + iVar3) = param_5;
  *(undefined2 *)(&DAT_00049d7a + iVar3) = 0;
  *(undefined2 *)(&DAT_00049d7c + iVar3) = 0;
  *(undefined2 *)(&DAT_00049d7e + iVar3) = 0;
  (&DAT_00049d80)[iVar2 * 0x67] = DAT_00049c60;
  (&DAT_00049d82)[iVar2 * 0x67] = DAT_00049c62;
  (&DAT_00049d84)[iVar2 * 0x67] = DAT_00049c64;
  *(undefined4 *)((int)&DAT_00049d86 + iVar3) = DAT_00049c66;
  *(undefined4 *)((int)&DAT_00049d8a + iVar3) = DAT_00049c6a;
  *(undefined4 *)((int)&DAT_00049d8e + iVar3) = DAT_00049c6e;
  *(undefined4 *)((int)&DAT_00049d92 + iVar3) = DAT_00049c72;
  iVar1 = (int)((param_5 & 0xfffffc00) - (DAT_00049c56 & 0xfffffc00)) >> 10;
  (&DAT_00049dac)[iVar2 * 0x67] =
       (short)((int)((param_3 & 0xfffffc00) - (DAT_00049c50 & 0xfffffc00)) >> 10) +
       (short)(iVar1 << 2) + (short)iVar1 + 0xc;
  *(undefined4 *)(&DAT_00049dc4 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049dc8 + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049dca + iVar3) = 0;
  *(undefined2 *)(&DAT_00049dce + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049dd0 + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049dd4 + iVar3) = 0;
  (&DAT_00049dd8)[iVar2 * 0x67] = 0;
  (&DAT_00049dda)[iVar3] = param_6;
  (&DAT_00049ddb)[iVar3] = param_6;
  *(undefined4 *)(&DAT_00049ddc + iVar3) = 0;
  *(undefined4 *)(&DAT_00049de0 + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049de4 + iVar3) = 0;
  *(undefined4 *)((int)&DAT_00049de8 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049e02 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049e00 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049dfe + iVar3) = 0;
  *(undefined2 *)(&DAT_00049e30 + iVar3) = 0;
  *(undefined2 *)(&DAT_00049e36 + iVar3) = 1;
  if ((&DAT_00049d80)[iVar2 * 0x67] == 1) {
    FUN_000102c4(&DAT_00049d6c + iVar2 * 0x67);
  }
  else if ((&DAT_00049d80)[iVar2 * 0x67] == 2) {
    FUN_00010520(&DAT_00049d6c + iVar2 * 0x67);
  }
  switch(param_1) {
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 0xc:
  case 0xd:
  case 0xe:
  case 0xf:
  case 0x13:
  case 0x14:
    goto switchD_0001361c_caseD_4;
  case 9:
    pcVar4 = FUN_0000edc4;
    break;
  case 10:
    pcVar4 = (code *)&DAT_0000fcc2;
    break;
  case 0xb:
    pcVar4 = (code *)&LAB_00017f80;
    break;
  case 0x10:
    pcVar4 = (code *)&LAB_000178e0;
    break;
  case 0x11:
    pcVar4 = (code *)&LAB_0000f720;
    break;
  case 0x12:
    pcVar4 = (code *)&LAB_00021d40;
    break;
  case 0x15:
    pcVar4 = (code *)&LAB_00015080;
    break;
  case 0x16:
    pcVar4 = (code *)&LAB_00014fc0;
    break;
  case 0x17:
    pcVar4 = (code *)&LAB_0000f888;
    break;
  case 0x18:
    pcVar4 = (code *)&LAB_00015140;
    break;
  case 0x19:
  case 0x1a:
  case 0x1b:
    pcVar4 = (code *)&LAB_00014100;
    break;
  case 0x1c:
  case 0x1d:
  case 0x1e:
    pcVar4 = (code *)&LAB_00011f80;
    break;
  case 0x1f:
  case 0x20:
  case 0x21:
    pcVar4 = (code *)&LAB_000128a0;
    break;
  default:
    (&DAT_00049d6c)[param_2 * 0x67] = 0;
    return;
  case 0x40:
    pcVar4 = FUN_0000f4d8;
    break;
  case 0x76:
    pcVar4 = (code *)&LAB_00015a80;
  }
  FUN_0000df6c(pcVar4,(int)param_2);
switchD_0001361c_caseD_4:
  return;
}


/* Address 000137e0 */

void FUN_000137e0(ushort param_1,uint param_2,undefined2 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  short sVar5;
  int iVar6;
  
  sVar5 = 0;
  do {
    if ((&DAT_0004bd9c)[sVar5 * 0xf] == 0) break;
    sVar5 = sVar5 + 1;
  } while (sVar5 < 0x28);
  if (sVar5 < 0x28) {
    iVar2 = (int)sVar5;
    iVar6 = iVar2 * 0x1e;
    (&DAT_0004bd9c)[iVar2 * 0xf] = param_1;
    *(uint *)(iVar6 + 0x4bd9e) = param_2;
    *(undefined2 *)(iVar6 + 0x4bda2) = param_3;
    *(uint *)(iVar6 + 0x4bda4) = param_4;
    iVar1 = (int)((param_4 & 0xfffffc00) - (DAT_00049c56 & 0xfffffc00)) >> 10;
    *(short *)(iVar6 + 0x4bdaa) =
         (short)((int)((param_2 & 0xfffffc00) - (DAT_00049c50 & 0xfffffc00)) >> 10) +
         (short)(iVar1 << 2) + (short)iVar1 + 0xc;
    FUN_000105da(&DAT_0004bd9c + iVar2 * 0xf);
    uVar4 = (uint)param_1;
    if (((&DAT_0004208c)[uVar4] & 2) == 0) {
      puVar3 = (undefined4 *)FUN_000152a2(DAT_0006e6a8 * 2 + 0x10);
      *(undefined4 **)((int)&DAT_0004bdb0 + iVar6) = puVar3;
      *(undefined4 *)*puVar3 = 0x20000;
      iVar1 = **(int **)((int)&DAT_0004bdb0 + iVar6);
      iVar2 = *(int *)(&DAT_0006e6ac + (short)(char)(&DAT_00042000)[uVar4] * 4);
      *(uint *)(iVar1 + 8) =
           (uint)(byte)(&DAT_0006e6a1)[iVar2] | (uint)(byte)(&DAT_0006e6a0)[iVar2] << 0x10;
      *(undefined **)(iVar1 + 0xc) =
           (&PTR_s_hat_red_tape_encrusted_wad_of_bu_00030648_0x1d8_0003bd20)
           [(byte)(&DAT_0006e6a0)[iVar2]];
      FUN_0000e2b8(&DAT_0006e6a0,(int)(short)(char)(&DAT_00042000)[uVar4],
                   **(int **)((int)&DAT_0004bdb0 + iVar6) + 0x10);
    }
    else {
      *(undefined1 *)(iVar6 + 0x4bda8) = 0;
      switch(param_1) {
      case 0x68:
        *(undefined ***)(sVar5 * 0x1e + 0x4bdb4) = &PTR_DAT_00008f54;
        break;
      case 0x69:
        *(undefined ***)(sVar5 * 0x1e + 0x4bdb4) = &PTR_DAT_00009de0;
        break;
      case 0x6a:
      case 0x6c:
      case 0x6d:
        *(undefined ***)(sVar5 * 0x1e + 0x4bdb4) = &PTR_DAT_00009908;
        break;
      case 0x6b:
        *(undefined ***)(sVar5 * 0x1e + 0x4bdb4) = &PTR_DAT_0000a2b8;
        break;
      case 0x6e:
      case 0x77:
      case 0x78:
      case 0x79:
      case 0x7a:
      case 0x7b:
      case 0x7c:
      case 0x7d:
      case 0x7e:
      case 0x7f:
      case 0x80:
      case 0x81:
      case 0x82:
      case 0x89:
      case 0x8a:
        (&DAT_0004bd9c)[sVar5 * 0xf] = 0;
        break;
      case 0x6f:
        iVar1 = sVar5 * 0x1e;
        *(undefined **)(iVar1 + 0x4bdb4) = &DAT_00008b80;
        *(int *)(iVar1 + 0x4bd9e) = *(int *)(iVar1 + 0x4bd9e) + -0x20;
        sVar5 = 0;
        do {
          if ((&DAT_0004bd9c)[sVar5 * 0xf] == 0) break;
          sVar5 = sVar5 + 1;
        } while (sVar5 < 0x28);
        if (sVar5 < 0x28) {
          iVar2 = sVar5 * 0x1e;
          *(undefined2 *)(iVar2 + 0x4bdac) = *(undefined2 *)(iVar1 + 0x4bdac);
          (&DAT_0004bd9c)[sVar5 * 0xf] = param_1;
          *(uint *)(iVar2 + 0x4bd9e) = param_2;
          *(undefined2 *)(iVar2 + 0x4bda2) = param_3;
          *(uint *)(iVar2 + 0x4bda4) = param_4 + 0x20;
          *(undefined1 *)(iVar2 + 0x4bda8) = 0;
          *(undefined **)(iVar2 + 0x4bdb4) = &DAT_00008c98;
        }
        break;
      case 0x70:
        *(undefined **)(sVar5 * 0x1e + 0x4bdb4) = &DAT_00008db0;
        break;
      case 0x71:
        *(char **)(sVar5 * 0x1e + 0x4bdb4) = s_xXh2_eYOYSZTZVZVZTYSYSYSZTiTiTiT_0000cdde + 0x42;
        break;
      case 0x72:
        *(undefined ***)(sVar5 * 0x1e + 0x4bdb4) = &PTR_DAT_0000b390;
        break;
      case 0x74:
        *(undefined **)(sVar5 * 0x1e + 0x4bdb4) = &DAT_0000c648;
      }
    }
  }
  return;
}


/* Address 00013ae0 */

void FUN_00013ae0(short param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4,
                 undefined2 param_5)

{
  short sVar1;
  
  if (((&DAT_0004208c)[param_1] & 1) == 0) {
    FUN_000137e0(param_1,param_2,param_3,param_4,param_5);
  }
  else {
    sVar1 = 0;
    do {
      if ((&DAT_00049d6c)[sVar1 * 0x67] == 0) break;
      sVar1 = sVar1 + 1;
    } while (sVar1 < 0x28);
    if (sVar1 < 0x28) {
      FUN_000134dc(param_1,sVar1,param_2,param_3,param_4,param_5);
    }
  }
  return;
}


/* Address 00013b5a */

uint FUN_00013b5a(int param_1,ushort param_2,undefined2 param_3,short param_4)

{
  uint in_D0;
  uint uVar1;
  undefined2 uVar2;
  
  uVar2 = (undefined2)((uint)param_1 >> 0x10);
  if ((param_2 & 0xf000) == 0) {
    uVar1 = FUN_0001039c(uVar2,(short)param_1,param_2 & 0xfff);
  }
  else if (param_2 == 0xffff) {
    *(short *)(param_1 + 0x40) = param_4 + *(short *)(param_1 + 0x40);
    uVar1 = FUN_000102c4(uVar2,(short)param_1);
    if ((short)uVar1 == 0) {
      *(short *)(param_1 + 0x40) = *(short *)(param_1 + 0x40) - param_4;
      uVar1 = uVar1 & 0xffff0000;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = in_D0 & 0xffff0000;
  }
  return uVar1;
}


/* Address 00013bb0 */

uint FUN_00013bb0(int param_1,int param_2,short param_3)

{
  short *psVar1;
  short sVar2;
  undefined2 uVar3;
  ushort uVar4;
  undefined4 in_D0;
  uint uVar5;
  short in_D1w;
  short *psVar6;
  
  uVar3 = (undefined2)((uint)in_D0 >> 0x10);
  uVar5 = CONCAT22(uVar3,param_3);
  if (param_3 == 1) {
    sVar2 = *(short *)(param_2 + 6) + *(short *)(param_2 + 8) * 2;
    uVar5 = CONCAT22(uVar3,sVar2);
    in_D1w = sVar2 + ((short)(*(short *)(param_1 + 0x32) - *(short *)(param_1 + 6)) >> 6);
  }
  else if (param_3 < 2) {
    if (param_3 == 0) {
      sVar2 = (short)(*(short *)(param_1 + 6) - *(short *)(param_1 + 0x36)) >> 6;
      uVar5 = CONCAT22(uVar3,sVar2);
      in_D1w = *(short *)(param_2 + 8) + sVar2;
    }
  }
  else if (param_3 == 2) {
    sVar2 = (short)(*(short *)(param_1 + 0x3a) - *(short *)(param_1 + 0xc)) >> 6;
    uVar5 = CONCAT22(uVar3,sVar2);
    in_D1w = sVar2 + *(short *)(param_2 + 6) + *(short *)(param_2 + 8);
  }
  else if (param_3 == 3) {
    sVar2 = *(short *)(param_1 + 0xc) - *(short *)(param_1 + 0x3e);
    uVar5 = CONCAT22(uVar3,sVar2);
    in_D1w = sVar2 >> 6;
  }
  if (*(short *)(param_2 + 0x16) != -1) {
    psVar1 = (short *)(*(int *)(DAT_00049c18 + 8) + *(short *)(param_2 + 0x16) * 6);
    for (psVar6 = psVar1; uVar4 = (ushort)((uint)psVar1 >> 0x10), in_D1w != *psVar6;
        psVar6 = psVar6 + 3) {
      if (psVar6[1] < 0) {
        return (uint)uVar4 << 0x10;
      }
    }
    uVar5 = (uint)uVar4 << 0x10;
    if ((psVar6[1] & 0x7000U) != 0) {
      uVar3 = (undefined2)((uint)param_1 >> 0x10);
      if (psVar6[2] != -1) {
        uVar5 = FUN_00010652(uVar3,(short)param_1,psVar6[2]);
        return uVar5;
      }
      if ((*(short *)(param_1 + 0x16) == 0) &&
         (uVar5 = FUN_0001028e(uVar3,(short)param_1), (short)uVar5 != 0)) {
        *(undefined2 *)(param_1 + 0x14) = 1;
        return 2;
      }
    }
  }
  return uVar5 & 0xffff0000;
}


/* Address 00013c9a */

void FUN_00013c9a(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined2 uVar3;
  ushort uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  ushort uVar7;
  byte bVar8;
  char cVar10;
  short sVar9;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  
  *(undefined2 *)(param_1 + 0x96) = 0;
  *(undefined2 *)(param_1 + 0x94) = 0;
  *(undefined2 *)(param_1 + 0x92) = 0;
  cVar10 = FUN_00013440((&DAT_00047b9a)[*(short *)(param_1 + 0xc0) * 0x20],
                        (&DAT_00047b9e)[*(short *)(param_1 + 0xc0) * 0x20]);
  bVar8 = *(char *)(param_1 + 0x6e) - ((char)DAT_00049b9c + cVar10);
  if (bVar8 < 0x80) {
    if (bVar8 < 0x40) {
      *(undefined4 *)(param_1 + 0xa4) = param_2[0x12];
      *(undefined4 *)(param_1 + 0xa8) = param_2[0x13];
      *(undefined4 *)(param_1 + 0xac) = param_2[0x14];
      *(undefined4 *)(param_1 + 0xb0) = param_2[0x15];
      *(undefined4 *)(param_1 + 0xb4) = param_2[0x16];
      *(undefined4 *)(param_1 + 0xb8) = param_2[0x17];
    }
    else {
      *(undefined4 *)(param_1 + 0xa4) = param_2[0xc];
      *(undefined4 *)(param_1 + 0xa8) = param_2[0xd];
      *(undefined4 *)(param_1 + 0xac) = param_2[0xe];
      *(undefined4 *)(param_1 + 0xb0) = param_2[0xf];
      *(undefined4 *)(param_1 + 0xb4) = param_2[0x10];
      *(undefined4 *)(param_1 + 0xb8) = param_2[0x11];
    }
  }
  else if (bVar8 < 0xc0) {
    *(undefined4 *)(param_1 + 0xa4) = param_2[6];
    *(undefined4 *)(param_1 + 0xa8) = param_2[7];
    *(undefined4 *)(param_1 + 0xac) = param_2[8];
    *(undefined4 *)(param_1 + 0xb0) = param_2[9];
    *(undefined4 *)(param_1 + 0xb4) = param_2[10];
    *(undefined4 *)(param_1 + 0xb8) = param_2[0xb];
  }
  else {
    *(undefined4 *)(param_1 + 0xa4) = *param_2;
    *(undefined4 *)(param_1 + 0xa8) = param_2[1];
    *(undefined4 *)(param_1 + 0xac) = param_2[2];
    *(undefined4 *)(param_1 + 0xb0) = param_2[3];
    *(undefined4 *)(param_1 + 0xb4) = param_2[4];
    *(undefined4 *)(param_1 + 0xb8) = param_2[5];
  }
  FUN_0000e220(param_1 + 0x80,(short)((uint)*(undefined4 *)(param_1 + 0x74) >> 0x10),
               (short)*(undefined4 *)(param_1 + 0x74),0,*(undefined1 *)(param_1 + 0x6e),
               (short)((uint)*(undefined4 *)(param_1 + 0x70) >> 0x10),
               (short)*(undefined4 *)(param_1 + 0x70),
               (short)((uint)*(undefined4 *)(param_1 + 0x78) >> 0x10),
               (short)*(undefined4 *)(param_1 + 0x78));
  *(undefined2 *)(param_1 + 0xc4) = 0;
  uVar1 = *(undefined4 *)(param_1 + 4);
  uVar3 = *(undefined2 *)(param_1 + 8);
  uVar2 = *(undefined4 *)(param_1 + 10);
  uVar4 = *(ushort *)(param_1 + 0xe);
  uVar5 = *(undefined2 *)(param_1 + 0x10);
  uVar6 = *(undefined2 *)(param_1 + 0x12);
  uVar7 = (uVar4 & 0x3fff) + (*(ushort *)(param_1 + 0x9a) & 0x3fff);
  *(int *)(param_1 + 4) =
       (int)(short)(uVar7 >> 0xe) + (int)*(short *)(param_1 + 0x92) + *(int *)(param_1 + 4);
  *(ushort *)(param_1 + 0xe) = uVar7 & 0x3fff;
  uVar7 = (*(ushort *)(param_1 + 0x10) & 0x3fff) + (*(ushort *)(param_1 + 0x9c) & 0x3fff);
  *(short *)(param_1 + 8) = *(short *)(param_1 + 0x94) + (uVar7 >> 0xe) + *(short *)(param_1 + 8);
  *(ushort *)(param_1 + 0x10) = uVar7 & 0x3fff;
  uVar7 = (*(ushort *)(param_1 + 0x12) & 0x3fff) + (*(ushort *)(param_1 + 0x9e) & 0x3fff);
  *(int *)(param_1 + 10) =
       (int)(short)(uVar7 >> 0xe) + (int)*(short *)(param_1 + 0x96) + *(int *)(param_1 + 10);
  *(ushort *)(param_1 + 0x12) = uVar7 & 0x3fff;
  sVar9 = 1;
  uVar11 = (undefined2)((uint)param_1 >> 0x10);
  if (*(short *)(param_1 + 0x14) == 1) {
    *(undefined2 *)(param_1 + 0xc4) = 0;
    if (*(int *)(param_1 + 10) < *(int *)(param_1 + 0x50)) {
      if (*(int *)(param_1 + 10) < *(int *)(param_1 + 0x54)) {
        uVar13 = 0xfffb;
        uVar12 = 1;
        uVar14 = *(undefined2 *)(*(int *)(param_1 + 0x44) + 4);
      }
      else if (*(int *)(param_1 + 4) < *(int *)(param_1 + 0x48)) {
        if (*(int *)(param_1 + 0x4c) <= *(int *)(param_1 + 4)) goto LAB_00013ef0;
        uVar13 = 0xffff;
        uVar12 = 3;
        uVar14 = *(undefined2 *)(*(int *)(param_1 + 0x44) + 8);
      }
      else {
        uVar13 = 1;
        uVar12 = 2;
        uVar14 = *(undefined2 *)(*(int *)(param_1 + 0x44) + 6);
      }
    }
    else {
      uVar13 = 5;
      uVar12 = 0;
      uVar14 = *(undefined2 *)(*(int *)(param_1 + 0x44) + 2);
    }
    sVar9 = FUN_00013b5a(uVar11,(short)param_1,uVar14,uVar12,uVar13);
    *(undefined2 *)(param_1 + 0xc4) = 1;
  }
  else if (*(short *)(param_1 + 0x14) == 2) {
    if (*(int *)(param_1 + 10) < *(int *)(param_1 + 0x38)) {
      if (*(int *)(param_1 + 10) < *(int *)(param_1 + 0x3c)) {
        uVar14 = 1;
      }
      else if (*(int *)(param_1 + 4) < *(int *)(param_1 + 0x30)) {
        if (*(int *)(param_1 + 0x34) <= *(int *)(param_1 + 4)) goto LAB_00013ef0;
        uVar14 = 3;
      }
      else {
        uVar14 = 2;
      }
    }
    else {
      uVar14 = 0;
    }
    sVar9 = FUN_00013bb0(uVar11,(short)param_1,
                         (short)((uint)*(undefined4 *)(param_1 + 0x2c) >> 0x10),
                         (short)*(undefined4 *)(param_1 + 0x2c),uVar14);
  }
  else {
    sVar9 = 0;
  }
LAB_00013ef0:
  if (sVar9 == 0) {
    *(undefined4 *)(param_1 + 4) = uVar1;
    *(undefined2 *)(param_1 + 8) = uVar3;
    *(undefined4 *)(param_1 + 10) = uVar2;
    *(ushort *)(param_1 + 0xe) = uVar4;
    *(undefined2 *)(param_1 + 0x10) = uVar5;
    *(undefined2 *)(param_1 + 0x12) = uVar6;
  }
  return;
}


/* Address 00013f12 */

undefined4 FUN_00013f12(int param_1,uint param_2)

{
  ushort uVar1;
  
  if ((param_2 & 3) == 0) {
    switch((short)(*(byte *)(param_1 + 0x6e) + 0x20) >> 6) {
    case 0:
    case 4:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 8);
      break;
    case 1:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 4);
      break;
    case 2:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 6);
      break;
    case 3:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 2);
      break;
    default:
      goto switchD_00013f3a_default;
    }
    if ((uVar1 & 0xf000) == 0) {
      return 1;
    }
  }
switchD_00013f3a_default:
  return 0;
}


/* Address 00013f7c */

undefined4 FUN_00013f7c(int param_1,uint param_2)

{
  ushort uVar1;
  
  if ((param_2 & 3) == 3) {
    switch((short)(*(byte *)(param_1 + 0x6e) + 0x20) >> 6) {
    case 0:
    case 4:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 6);
      break;
    case 1:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 2);
      break;
    case 2:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 8);
      break;
    case 3:
      uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 4);
      break;
    default:
      goto switchD_00013fa8_default;
    }
    if ((uVar1 & 0xf000) == 0) {
      return 1;
    }
  }
switchD_00013fa8_default:
  return 0;
}


/* Address 00013fea */

undefined4 FUN_00013fea(int param_1)

{
  ushort uVar1;
  
  switch((short)(*(byte *)(param_1 + 0x6e) + 0x20) >> 6) {
  case 0:
  case 4:
    uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 2);
    break;
  case 1:
    uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 8);
    break;
  case 2:
    uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 4);
    break;
  case 3:
    uVar1 = *(ushort *)(*(int *)(param_1 + 0x44) + 6);
    break;
  default:
    goto switchD_0001400a_default;
  }
  if ((uVar1 & 0xf000) == 0) {
    return 0;
  }
switchD_0001400a_default:
  return 1;
}


/* Address 0001404c */

void FUN_0001404c(int param_1)

{
  byte bVar1;
  char cVar3;
  short sVar2;
  short sVar4;
  undefined2 uVar5;
  
  cVar3 = FUN_00013440((&DAT_00047b9a)[*(short *)(param_1 + 0xc0) * 0x20],
                       (&DAT_00047b9e)[*(short *)(param_1 + 0xc0) * 0x20]);
  bVar1 = *(char *)(param_1 + 0x6e) - ((char)DAT_00049b9c + cVar3);
  if (bVar1 < 0x80) {
    if (bVar1 < 0x39) {
      uVar5 = 0xffff;
      sVar2 = 1;
      goto LAB_000140ca;
    }
    if (bVar1 < 0x60) {
      uVar5 = 0xfffe;
      sVar2 = 2;
      goto LAB_000140ca;
    }
    uVar5 = 0xfffd;
  }
  else {
    if (199 < bVar1) {
      uVar5 = 1;
      sVar2 = 1;
      goto LAB_000140ca;
    }
    if (0xa0 < bVar1) {
      uVar5 = 2;
      sVar2 = 2;
      goto LAB_000140ca;
    }
    uVar5 = 3;
  }
  sVar2 = 3;
LAB_000140ca:
  sVar4 = *(short *)(param_1 + 0xca);
  if (sVar4 < 0) {
    sVar4 = -sVar4;
  }
  if (sVar2 != sVar4) {
    *(int *)(param_1 + 100) = (short)(sVar2 - sVar4) * 4 + *(int *)(param_1 + 100);
    *(undefined2 *)(param_1 + 0xcc) = 1;
  }
  *(undefined2 *)(param_1 + 0xca) = uVar5;
  return;
}


/* Address 000146e0 */

uint FUN_000146e0(byte *param_1,char *param_2)

{
  byte bVar1;
  int iVar2;
  ushort uVar3;
  short sVar4;
  short sVar5;
  
  sVar5 = 0;
  if (*param_2 == '\x02') {
    iVar2 = FUN_0000e540(param_2[1],param_2[3]);
    bVar1 = *param_1;
    while (bVar1 != 0) {
      param_1 = param_1 + 1;
      uVar3 = (ushort)bVar1;
      if ((uVar3 < (byte)param_2[4]) || ((byte)param_2[5] < uVar3)) {
        sVar4 = 0;
      }
      else {
        sVar4 = uVar3 - (byte)param_2[4];
      }
      sVar5 = (ushort)(byte)param_2[(int)sVar4 + iVar2 * 2 + 8] + sVar5;
      bVar1 = *param_1;
    }
  }
  else {
    bVar1 = *param_1;
    while (bVar1 != 0) {
      param_1 = param_1 + 1;
      sVar5 = (ushort)(byte)param_2[2] + sVar5;
      bVar1 = *param_1;
    }
  }
  return (uint)CONCAT12(param_2[3],sVar5);
}


/* Address 00014776 */

uint FUN_00014776(undefined2 param_1,short param_2,short param_3,ushort param_4)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar2 = -param_3;
  uVar1 = param_4 & param_2 + param_3;
  if (uVar1 != 0) {
    uVar2 = uVar2 - (param_4 - (uVar1 - 1));
  }
  return uVar2 | 0x10000;
}


/* Address 000147a6 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_000147a6(undefined2 param_1,undefined2 param_2,byte *param_3,undefined4 param_4,
                 uint param_5,int param_6)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  ushort uVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  
  bVar2 = *(byte *)(param_6 + 2);
  uVar10 = (ushort)bVar2;
  uVar11 = CONCAT22(param_2,param_1);
  _DAT_00f02224 = param_6 + 8;
  switch(param_5 & 0x38) {
  case 0:
  case 8:
  case 0x10:
    uVar7 = 0;
    _DAT_00f02228 = (int)*(short *)(param_6 + 6) & 0xfffcffffU | 0x10000;
    _DAT_00f02204 = param_5 & 0xfffcffff | 0x10000;
    goto LAB_0001489c;
  case 0x18:
    uVar7 = 7;
    break;
  case 0x20:
    uVar7 = 3;
    break;
  default:
    uVar7 = 1;
  }
  _DAT_00f02228 = (int)*(short *)(param_6 + 6) & 0xfffcffff;
  _DAT_00f02204 = param_5 & 0xfffcffff;
LAB_0001489c:
  _DAT_00f02268 = 0;
  _DAT_00f0226c = 0;
  uVar9 = (uint)*(byte *)(param_6 + 3) << 0x10;
  uVar3 = uVar9 | bVar2;
  bVar1 = *param_3;
  _DAT_00f02200 = param_4;
  while (bVar1 != 0) {
    param_3 = param_3 + 1;
    uVar6 = (ushort)bVar1;
    if ((uVar6 < *(byte *)(param_6 + 4)) || (*(byte *)(param_6 + 5) < uVar6)) {
      uVar5 = (uint)uVar10;
    }
    else {
      uVar6 = (uVar6 - *(byte *)(param_6 + 4)) * uVar10;
      uVar8 = (ushort)uVar7;
      iVar4 = FUN_00014776(uVar11,uVar10,uVar8);
      _DAT_00f02234 = FUN_00014776((int)(short)uVar6,uVar10,uVar8);
      if (iVar4 < _DAT_00f02234) {
        _DAT_00f02234 = _DAT_00f02234 - (uint)(ushort)(uVar8 + 1);
      }
      if (((uVar8 & uVar6) == 0) || ((uint)(uVar8 & uVar6) <= (uVar11 & uVar7))) {
        _DAT_00f02238 = 0x9800609;
      }
      else {
        _DAT_00f02238 = 0x980060d;
      }
      uVar5 = (uint)bVar2;
      _DAT_00f0220c = uVar11;
      _DAT_00f02210 = iVar4;
      _DAT_00f02230 = (int)(short)uVar6;
      _DAT_00f0223c = uVar3;
    }
    uVar9 = uVar5 + uVar9;
    uVar11 = uVar5 + uVar11;
    bVar1 = *param_3;
  }
  return uVar9;
}


/* Address 000149ae */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_000149ae(undefined2 param_1,undefined2 param_2,byte *param_3,undefined4 param_4,uint param_5
                ,char *param_6,ushort param_7,ushort param_8)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  ushort uVar6;
  ushort unaff_D4w;
  ushort uVar7;
  uint uVar8;
  ushort uVar9;
  int local_14;
  ushort local_10;
  char *local_e;
  uint local_a;
  short local_6;
  
  if (*param_6 == '\x02') {
    iVar4 = FUN_0000e540(param_6[1],param_6[3]);
    local_e = param_6 + iVar4 * 2 + 8;
  }
  else {
    if (*param_6 == '\x03') {
      iVar4 = FUN_000147a6(param_1,param_2,param_3,param_4,param_5,param_6);
      return iVar4;
    }
    local_e = (char *)0x0;
  }
  uVar9 = (byte)param_6[2] + 7 & 0xfff8;
  if (uVar9 == 0x18) {
LAB_00014a5e:
    local_6 = 2;
    uVar9 = 4;
  }
  else {
    if (uVar9 < 0x19) {
      if (uVar9 == 0x10) {
        local_6 = 1;
        uVar9 = 2;
        goto LAB_00014a68;
      }
    }
    else if (uVar9 == 0x20) goto LAB_00014a5e;
    local_6 = 0;
    uVar9 = 1;
  }
LAB_00014a68:
  if (local_e == (char *)0x0) {
    if ((byte)param_6[2] < 9) {
      unaff_D4w = (ushort)(byte)param_6[2];
    }
    else {
      unaff_D4w = ((byte)param_6[2] + 7 & 7) + 1;
    }
    local_a = (int)(short)unaff_D4w | (uint)(byte)param_6[3] << 0x10;
  }
  uVar8 = 0x14010604;
  uVar2 = param_5 & 0x38;
  if (uVar2 == 8) {
    param_7 = param_7 << 2 | param_7;
    param_8 = param_8 << 2 | param_8;
LAB_00014aee:
    param_7 = param_7 << 4 | param_7;
    param_8 = param_8 << 4 | param_8;
  }
  else {
    if (8 < uVar2) {
      if (uVar2 != 0x10) goto LAB_00014b00;
      goto LAB_00014aee;
    }
    if (uVar2 != 0) goto LAB_00014b00;
    if (param_7 != 0) {
      param_7 = 0xff;
    }
    if (param_8 != 0) {
      param_8 = 0xff;
    }
  }
  uVar8 = 0x1401060c;
LAB_00014b00:
  if (param_8 == 0) {
    uVar8 = uVar8 | 8;
  }
  else {
    _DAT_00f02248 = (uint)param_8;
  }
  local_14 = (uint)(byte)param_6[3] << 0x10;
  bVar1 = *param_3;
  iVar4 = CONCAT22(param_2,param_1);
  iVar3 = _DAT_00f0220c;
  while (_DAT_00f0220c = iVar4, bVar1 != 0) {
    param_3 = param_3 + 1;
    local_10 = (ushort)(byte)param_6[4];
    uVar6 = (ushort)bVar1;
    if ((uVar6 < local_10) || ((byte)param_6[5] < uVar6)) {
      sVar5 = 0;
    }
    else {
      sVar5 = uVar6 - local_10;
    }
    if (local_e == (char *)0x0) {
      sVar5 = sVar5 << local_6;
      uVar6 = uVar9;
    }
    else {
      unaff_D4w = (ushort)(byte)local_e[sVar5];
      uVar7 = (ushort)(byte)local_e[sVar5];
      uVar6 = (ushort)(uVar7 + 7) >> 3;
      if (8 < uVar7) {
        unaff_D4w = (uVar7 - 1 & 7) + 1;
      }
      local_a = (int)(short)unaff_D4w | (uint)(byte)param_6[3] << 0x10;
      sVar5 = sVar5 << local_6;
      if (uVar6 < uVar9) {
        sVar5 = (uVar9 - uVar6) + sVar5;
      }
    }
    _DAT_00f02230 = (int)sVar5;
    _DAT_00f0223c = local_a;
    _DAT_00f02210 = (ushort)-unaff_D4w | 0x10000;
    iVar4 = (short)unaff_D4w + _DAT_00f0220c;
    local_14 = (short)unaff_D4w + local_14;
    if (1 < uVar6) {
      _DAT_00f02210 = 0x1fff8;
      iVar3 = iVar4;
      while (iVar4 = iVar3, uVar6 = uVar6 - 1, 0 < (short)uVar6) {
        sVar5 = sVar5 + 1;
        _DAT_00f02230 = (int)sVar5;
        _DAT_00f0223c = (uint)(byte)param_6[3] << 0x10 | 8;
        local_14 = local_14 + 8;
        iVar3 = iVar4 + 8;
        _DAT_00f0220c = iVar4;
      }
    }
    iVar3 = _DAT_00f0220c;
    _DAT_00f02238 = uVar8;
    bVar1 = *param_3;
  }
  _DAT_00f02268 = (uint)param_7;
  _DAT_00f02234 = 0x1ffff;
  _DAT_00f02228 = (int)(short)((*(ushort *)(param_6 + 6) & 0x7e00) + 0xe800) | 0x10018;
  _DAT_00f02224 = param_6 + 8;
  _DAT_00f0220c = iVar3;
  _DAT_00f02204 = param_5 & 0xfffcffff | 0x10000;
  _DAT_00f02200 = param_4;
  return local_14;
}


/* Address 00015200 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00015200(void)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  piVar3 = (int *)(*_DAT_00112d60 + (int)_DAT_00112d60);
  piVar4 = _DAT_00112d60;
  if (piVar3 < &DAT_001c0000) {
    do {
      iVar1 = *piVar3;
      FUN_0000e3e0(piVar3,piVar4,iVar1);
      *(int **)piVar4[1] = piVar4 + 2;
      piVar3 = (int *)(*piVar4 + (int)piVar3);
      if (piVar3 < &DAT_001c0000) {
        if (0x15edbf < (uint)piVar3[1]) goto LAB_00015260;
        if ((piVar3[1] == 0) && (piVar3 = (int *)(*piVar3 + (int)piVar3), piVar3 < &DAT_001c0000)) {
          if (0x15edbf < (uint)piVar3[1]) goto LAB_00015260;
          iVar2 = piVar3[1];
          while (iVar2 == 0) {
LAB_00015260:
            do {
              piVar3 = (int *)(*piVar3 + (int)piVar3);
              if ((int *)0x1bffff < piVar3) goto LAB_0001527a;
            } while (0x15edbf < (uint)piVar3[1]);
            iVar2 = piVar3[1];
          }
        }
      }
LAB_0001527a:
      piVar4 = (int *)(iVar1 + (int)piVar4);
    } while (piVar3 < &DAT_001c0000);
  }
  *piVar4 = 0x1c0000 - (int)piVar4;
  piVar4[1] = 0;
  piVar4[2] = 0;
  _DAT_00112d60 = piVar4;
  return;
}


/* Address 000152a2 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_000152a2(int param_1)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  ushort uVar5;
  short sVar7;
  int iVar8;
  int *piVar9;
  uint *puVar10;
  int iVar6;
  
  puVar1 = _DAT_00112d60;
  uVar2 = param_1 + 0xfU & 0xfffffff8;
  if ((int)*_DAT_00112d60 < (int)uVar2) {
    puVar4 = (uint *)_DAT_00112d60[1];
    while (puVar10 = puVar4, puVar10 != (uint *)0x0) {
      if ((int)uVar2 <= (int)*puVar10) {
        uVar3 = *puVar10 - uVar2;
        if ((int)uVar3 < 0x10) {
          puVar1[1] = puVar10[1];
          iVar6 = 0xff;
          piVar9 = (int *)&DAT_00112d5c;
          while (iVar8 = iVar6 << 2, puVar4 = _DAT_00112d60, *piVar9 != 0) {
            piVar9 = piVar9 + -1;
            uVar5 = (ushort)((uint)iVar6 >> 0x10);
            sVar7 = (short)iVar6 + -1;
            iVar6 = CONCAT22(uVar5,sVar7);
            if ((sVar7 == -1) && (iVar6 = (uint)uVar5 * 0x10000 + -1, uVar5 == 0)) {
              return 0;
            }
          }
        }
        else {
          *puVar10 = uVar3;
          puVar10 = (uint *)(uVar3 + (int)puVar10);
          *puVar10 = uVar2;
          iVar6 = 0xff;
          piVar9 = (int *)&DAT_00112d5c;
          while (iVar8 = iVar6 << 2, puVar4 = _DAT_00112d60, *piVar9 != 0) {
            piVar9 = piVar9 + -1;
            uVar5 = (ushort)((uint)iVar6 >> 0x10);
            sVar7 = (short)iVar6 + -1;
            iVar6 = CONCAT22(uVar5,sVar7);
            if ((sVar7 == -1) && (iVar6 = (uint)uVar5 * 0x10000 + -1, uVar5 == 0)) {
              return 0;
            }
          }
        }
        goto LAB_000152f4;
      }
      puVar1 = puVar10;
      puVar4 = (uint *)puVar10[1];
    }
    FUN_00015200();
    puVar10 = _DAT_00112d60;
    puVar4 = _DAT_00112d60;
    if ((int)uVar2 <= (int)*_DAT_00112d60) {
      uVar3 = *_DAT_00112d60 - uVar2;
      if ((int)uVar3 < 0x10) {
        iVar6 = 0xff;
        piVar9 = (int *)&DAT_00112d5c;
        do {
          if (*piVar9 == 0) {
            puVar1 = _DAT_00112d60 + 2;
            _DAT_00112d60 = (uint *)_DAT_00112d60[1];
            *(uint **)(iVar6 * 4 + 0x112960) = puVar1;
            uVar2 = iVar6 * 4 + 0x112960;
            puVar10[1] = uVar2;
            _DAT_00112d64 = _DAT_00112d64 - *puVar10;
            return uVar2;
          }
          piVar9 = piVar9 + -1;
          uVar5 = (ushort)((uint)iVar6 >> 0x10);
          sVar7 = (short)iVar6 + -1;
          iVar6 = CONCAT22(uVar5,sVar7);
        } while ((sVar7 != -1) ||
                (iVar6 = (uint)uVar5 * 0x10000 + -1, puVar4 = (uint *)_DAT_00112d60[1], uVar5 != 0))
        ;
      }
      else {
        *_DAT_00112d60 = uVar3;
        puVar10 = (uint *)(uVar3 + (int)puVar10);
        *puVar10 = uVar2;
        iVar6 = 0xff;
        piVar9 = (int *)&DAT_00112d5c;
        do {
          iVar8 = iVar6 << 2;
          puVar4 = _DAT_00112d60;
          if (*piVar9 == 0) goto LAB_000152f4;
          piVar9 = piVar9 + -1;
          uVar5 = (ushort)((uint)iVar6 >> 0x10);
          sVar7 = (short)iVar6 + -1;
          iVar6 = CONCAT22(uVar5,sVar7);
        } while ((sVar7 != -1) || (iVar6 = (uint)uVar5 * 0x10000 + -1, uVar5 != 0));
      }
    }
  }
  else {
    uVar3 = *_DAT_00112d60 - uVar2;
    if ((int)uVar3 < 0x10) {
      iVar6 = 0xff;
      piVar9 = (int *)&DAT_00112d5c;
      do {
        iVar8 = iVar6 << 2;
        puVar10 = _DAT_00112d60;
        puVar4 = (uint *)_DAT_00112d60[1];
        if (*piVar9 == 0) goto LAB_000152f4;
        piVar9 = piVar9 + -1;
        uVar5 = (ushort)((uint)iVar6 >> 0x10);
        sVar7 = (short)iVar6 + -1;
        iVar6 = CONCAT22(uVar5,sVar7);
      } while ((sVar7 != -1) || (iVar6 = (uint)uVar5 * 0x10000 + -1, uVar5 != 0));
    }
    else {
      *_DAT_00112d60 = uVar3;
      *(uint *)(uVar3 + (int)puVar1) = uVar2;
      iVar6 = 0xff;
      piVar9 = (int *)&DAT_00112d5c;
      do {
        iVar8 = iVar6 << 2;
        puVar10 = (uint *)(uVar3 + (int)puVar1);
        puVar4 = _DAT_00112d60;
        if (*piVar9 == 0) {
LAB_000152f4:
          _DAT_00112d60 = puVar4;
          *(uint **)(iVar8 + 0x112960) = puVar10 + 2;
          puVar10[1] = iVar8 + 0x112960U;
          _DAT_00112d64 = _DAT_00112d64 - *puVar10;
          return iVar8 + 0x112960U;
        }
        piVar9 = piVar9 + -1;
        uVar5 = (ushort)((uint)iVar6 >> 0x10);
        sVar7 = (short)iVar6 + -1;
        iVar6 = CONCAT22(uVar5,sVar7);
      } while ((sVar7 != -1) || (iVar6 = (uint)uVar5 * 0x10000 + -1, uVar5 != 0));
    }
  }
  _DAT_00112d60 = puVar4;
  return 0;
}


/* Address 0001545c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001545c(int *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  if (param_1 == (int *)0x0) {
    return;
  }
  if (*param_1 == 0) {
    return;
  }
  puVar1 = (undefined4 *)*param_1;
  piVar4 = puVar1 + -2;
  _DAT_00112d64 = *piVar4 + _DAT_00112d64;
  if (_DAT_00112d60 == (int *)0x0) {
    _DAT_00112d60 = piVar4;
    puVar1[-1] = 0;
    *puVar1 = 0;
    goto LAB_00015572;
  }
  if (_DAT_00112d60 <= piVar4) {
    iVar2 = _DAT_00112d60[1];
    piVar3 = _DAT_00112d60;
    while (iVar2 != 0) {
      if (piVar4 < (int *)piVar3[1]) {
        if (*piVar4 + (int)piVar4 == piVar3[1]) {
          iVar2 = *(int *)(*piVar4 + (int)piVar4 + 4);
          puVar1[-1] = iVar2;
          if (iVar2 != 0) {
            *(int **)(puVar1[-1] + 8) = piVar4;
          }
          *piVar4 = *(int *)piVar3[1] + *piVar4;
        }
        else {
          puVar1[-1] = piVar3[1];
          *(int **)(piVar3[1] + 8) = piVar4;
        }
        *puVar1 = piVar3;
        if (piVar4 == (int *)(*piVar3 + (int)piVar3)) {
          *piVar3 = *piVar4 + *piVar3;
          iVar2 = puVar1[-1];
          piVar3[1] = iVar2;
          if (iVar2 != 0) {
            *(int **)(puVar1[-1] + 8) = piVar3;
          }
        }
        else {
          piVar3[1] = (int)piVar4;
        }
        goto LAB_00015572;
      }
      piVar3 = (int *)piVar3[1];
      iVar2 = piVar3[1];
    }
    if (piVar4 == (int *)(*piVar3 + (int)piVar3)) {
      *piVar3 = *piVar4 + *piVar3;
    }
    else {
      piVar3[1] = (int)piVar4;
      puVar1[-1] = 0;
      *puVar1 = piVar3;
    }
    goto LAB_00015572;
  }
  piVar3 = (int *)(*piVar4 + (int)piVar4);
  if (piVar3 == _DAT_00112d60) {
    puVar1[-1] = piVar3[1];
    *piVar4 = *piVar3 + *piVar4;
    if (piVar3[1] != 0) {
      _DAT_00112d60 = (int *)piVar3[1];
      goto LAB_000154d0;
    }
  }
  else {
    puVar1[-1] = _DAT_00112d60;
LAB_000154d0:
    _DAT_00112d60[2] = (int)piVar4;
  }
  *puVar1 = 0;
  _DAT_00112d60 = piVar4;
LAB_00015572:
  *param_1 = 0;
  return;
}


/* Address 0001557a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001557a(void)

{
  short sVar1;
  
  _DAT_00112d60 = &DAT_0015edc0;
  _DAT_0015edc0 = 0x61240;
  _DAT_0015edc4 = 0;
  _DAT_0015edc8 = 0;
  _DAT_00112d64 = 0x61240;
  sVar1 = 0xff;
  do {
    *(undefined4 *)(sVar1 * 4 + 0x112960) = 0;
    sVar1 = sVar1 + -1;
  } while (sVar1 != -1);
  return;
}


/* Address 00015bc0 */

undefined4 FUN_00015bc0(void)

{
  FUN_0000e4c0();
  return DAT_00049bac;
}


/* Address 00015bce */

void FUN_00015bce(short param_1)

{
  do {
  } while (DAT_000778cc < DAT_000778cc + (int)((short)(param_1 * 3) / 10));
  return;
}


/* Address 00015c1a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00015c1a(undefined4 param_1,uint param_2,short param_3,ushort param_4,short param_5,
                 ushort param_6,short param_7)

{
  _DAT_00f0220c = (int)param_3 | (uint)param_4 << 0x10;
  _DAT_00f02200 = param_1;
  _DAT_00f02204 = param_2 | 0x10000;
  _DAT_00f02210 = (ushort)-param_5 | 0x10000;
  _DAT_00f0223c = (int)param_5 | (uint)param_6 << 0x10;
  _DAT_00f02268 = (int)param_7;
  _DAT_00f02238 = 0x10200;
  return;
}


/* Address 00015ca0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00015ca0(undefined4 param_1,uint param_2,short param_3,short param_4,short param_5,
                 short param_6,ushort param_7,short param_8)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  ushort uVar5;
  ushort uVar7;
  uint uVar6;
  
  _DAT_00f02204 = param_2 | 0x30000;
  _DAT_00f02200 = param_1;
  _DAT_00f0220c = CONCAT22(param_4,param_3);
  _DAT_00f02218 = 0;
  uVar1 = param_5 - param_3;
  uVar2 = param_6 - param_4;
  uVar7 = uVar1;
  if ((short)uVar1 < 0) {
    uVar7 = -uVar1;
  }
  uVar5 = uVar2;
  if ((short)uVar2 < 0) {
    uVar5 = -uVar2;
  }
  uVar6 = (uint)(short)(uVar5 + uVar7);
  uVar3 = FUN_0000e588((uint)uVar1 << 0x10,uVar6);
  uVar4 = FUN_0000e588((uint)uVar2 << 0x10,uVar6);
  _DAT_00f0221c = uVar3 >> 0x10 | uVar4 & 0xffff0000;
  _DAT_00f02220 = uVar3 & 0xffff | uVar4 << 0x10;
  _DAT_00f0223c = uVar6 | 0x10000;
  _DAT_00f02240 = (uint)param_7;
  if (param_8 == 0) {
    _DAT_00f02238 = 0x1800000;
  }
  else {
    _DAT_00f02238 = 0xc00008;
  }
  return;
}


/* Address 00015d8e */

void FUN_00015d8e(undefined4 param_1,undefined4 param_2,short param_3,short param_4,short param_5,
                 short param_6,undefined2 param_7,undefined2 param_8)

{
  short sVar1;
  short sVar2;
  
  sVar1 = param_5 + param_3 + -1;
  sVar2 = param_6 + param_4 + -1;
  FUN_00015ca0(param_1,param_2,param_3,param_4,sVar1,param_4,param_7,param_8);
  FUN_00015ca0(param_1,param_2,param_3,param_4,param_3,sVar2,param_7,param_8);
  FUN_00015ca0(param_1,param_2,sVar1,sVar2,sVar1,param_4,param_7,param_8);
  FUN_00015ca0(param_1,param_2,sVar1,sVar2,param_3,sVar2,param_7,param_8);
  return;
}


/* Address 00015e16 */

char * FUN_00015e16(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  
  cVar1 = *param_1;
  while ((cVar1 != '\0' && (((*param_1 == ' ' || (*param_1 == '\r')) || (*param_1 == '\t'))))) {
    param_1 = param_1 + 1;
    cVar1 = *param_1;
  }
  if (*param_1 == '\n') {
    *param_2 = '\n';
    param_2[1] = '\0';
    return param_1 + 1;
  }
  pcVar2 = param_1;
  pcVar3 = param_2;
  if (((*param_1 != '\0') && (*param_1 != ' ')) && (*param_1 != '\r')) {
    while (pcVar2 = param_1, pcVar3 = param_2, 1 < (byte)(*param_1 - 9U)) {
      pcVar2 = param_1 + 1;
      pcVar3 = param_2 + 1;
      *param_2 = *param_1;
      if (((*pcVar2 == '\0') || (*pcVar2 == ' ')) ||
         (param_1 = pcVar2, param_2 = pcVar3, *pcVar2 == '\r')) break;
    }
  }
  *pcVar3 = '\0';
  return pcVar2;
}


/* Address 00015e8e */

uint FUN_00015e8e(undefined4 param_1,undefined4 param_2,char *param_3,undefined4 param_4,
                 undefined4 param_5,short param_6,short param_7,undefined2 param_8,
                 undefined2 param_9)

{
  uint in_D0;
  undefined4 uVar1;
  ushort uVar3;
  char *pcVar2;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  undefined4 auStackY_20084 [32728];
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  char local_d6 [82];
  undefined4 local_84 [32];
  
  if ((param_3 != (char *)0x0) && (*param_3 != '\0')) {
    uVar1 = FUN_000146e0(&DAT_00015e84,param_1);
    sVar6 = 0;
LAB_00015ed0:
    do {
      uVar11 = (undefined2)((uint)param_5 >> 0x10);
      uVar12 = (undefined2)param_5;
      uVar8 = (undefined2)((uint)param_4 >> 0x10);
      uVar9 = (undefined2)param_4;
      FUN_00015c1a(uVar8,uVar9,uVar11,uVar12,0,0,param_6,param_7,param_9);
      local_84[sVar6] = param_3;
      sVar4 = 0x14;
      sVar5 = 0x14;
      sVar7 = (short)((uint)uVar1 >> 0x10);
      uVar10 = (undefined2)((uint)param_1 >> 0x10);
      if (sVar6 == 0) {
        uVar3 = FUN_000146e0(param_2,param_1);
        FUN_000149ae((short)((int)((param_6 + -0x28) - (uint)uVar3) / 2) + 0x14,0x14,param_2,uVar8,
                     uVar9,uVar11,uVar12,uVar10,(short)param_1,param_8,0);
        sVar5 = sVar7 * 2 + 0x14;
      }
      if (*param_3 != '\0') {
        do {
          pcVar2 = (char *)FUN_00015e16(param_3,local_d6);
          if (local_d6[0] == '\n') {
            sVar4 = 0x14;
            sVar5 = sVar7 + sVar5 + 4;
            param_3 = pcVar2;
            if (param_7 < (short)(sVar5 + 0x14)) break;
          }
          else {
            uVar3 = FUN_000146e0(local_d6,param_1);
            if ((int)param_6 < (int)(uVar3 + 0x14 + (int)sVar4)) {
              sVar4 = 0x14;
              sVar5 = sVar7 + sVar5 + 1;
              if (param_7 < (short)(sVar5 + 0x14)) break;
            }
            FUN_000149ae(sVar4,sVar5,local_d6,uVar8,uVar9,uVar11,uVar12,param_1,param_8,0);
            sVar4 = uVar3 + (short)uVar1 + sVar4;
          }
          param_3 = pcVar2;
        } while (*pcVar2 != '\0');
      }
      for (; *param_3 == '\n'; param_3 = param_3 + 1) {
      }
      if (*param_3 != '\0') {
        sVar4 = FUN_000146e0(s__more__00015e86,param_1);
        FUN_000149ae((param_6 + -0x14) - sVar4,sVar5,s__more__00015e86,uVar8,uVar9,uVar11,uVar12,
                     uVar10,(short)param_1,param_8,0);
      }
      while( true ) {
        in_D0 = FUN_00015bc0();
        if (((in_D0 & 0x200000) != 0) && (*param_3 != '\0')) {
          sVar6 = sVar6 + 1;
          goto LAB_00015ed0;
        }
        if (((in_D0 & 0x100000) != 0) && (0 < sVar6)) break;
        if ((in_D0 & 0x2000) != 0) goto LAB_00016086;
      }
      sVar6 = sVar6 + -1;
      param_3 = (char *)local_84[sVar6];
    } while( true );
  }
LAB_00016086:
  return in_D0 & 0xffff0000;
}


/* Address 00016092 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00016092(int *param_1)

{
  int iVar1;
  ushort uVar3;
  undefined4 uVar2;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  
  if ((*param_1 == 0) || (param_1[2] == 0)) {
    _DAT_0011302a = 0;
    _DAT_00113028 = 0;
    _DAT_00113026 = 0;
    _DAT_00113024 = 0;
    sVar5 = _DAT_00113000;
  }
  else {
    sVar4 = 0x14;
    sVar6 = 0;
    iVar1 = *param_1;
    sVar5 = _DAT_00113000;
    while (iVar1 != 0) {
      iVar1 = param_1[sVar6 * 2];
      uVar3 = FUN_000146e0(iVar1,_DAT_00113004);
      if ((int)_DAT_00113020 < (int)(uVar3 + 0x14 + (int)sVar4)) {
        sVar4 = 0x14;
        sVar5 = _DAT_00113008 + sVar5 + 2;
      }
      if (sVar6 == _DAT_0011300c) {
        uVar2 = FUN_000149ae(sVar4,sVar5,iVar1,_DAT_00113018,_DAT_0011301c,_DAT_00113004,
                             _DAT_00113014,0);
        _DAT_00113024 = sVar4 + -1;
        _DAT_00113026 = sVar5 + -1;
        _DAT_00113028 = (short)uVar2 + 2;
        _DAT_0011302a = (short)((uint)uVar2 >> 0x10) + 2;
        sVar7 = _DAT_00113028;
        sVar8 = _DAT_0011302a;
        uVar3 = _DAT_00113014;
      }
      else {
        uVar2 = FUN_000149ae(sVar4,sVar5,iVar1,_DAT_00113018,_DAT_0011301c,_DAT_00113004,
                             _DAT_00113012,0);
        sVar8 = (short)((uint)uVar2 >> 0x10) + 2;
        sVar7 = (short)uVar2 + 2;
        uVar3 = _DAT_00113010;
      }
      FUN_00015d8e(_DAT_00113018,_DAT_0011301c,sVar4 + -1,sVar5 + -1,sVar7,sVar8,(uint)uVar3 << 0x10
                  );
      sVar4 = _DAT_0011300a + (short)uVar2 + sVar4;
      sVar6 = sVar6 + 1;
      iVar1 = param_1[sVar6 * 2];
    }
    sVar5 = _DAT_00113008 + sVar5;
  }
  _DAT_00113002 = sVar5 + 2;
  return;
}


/* Address 00016218 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00016218(short param_1,short param_2,short param_3,short param_4,short param_5,
                 short param_6,short param_7,short param_8,ushort param_9)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  
  param_9 = _DAT_00113010 ^ param_9;
  if ((param_3 != 0) && (param_7 != 0)) {
    sVar6 = 1;
    sVar8 = param_1 + param_3 + -1;
    do {
      iVar5 = (int)(short)(param_5 - param_1) * (int)sVar6;
      if (iVar5 < 0) {
        iVar5 = iVar5 + 0xf;
      }
      sVar1 = (short)(iVar5 >> 4) + param_1;
      iVar5 = (int)(short)(param_6 - param_2) * (int)sVar6;
      if (iVar5 < 0) {
        iVar5 = iVar5 + 0xf;
      }
      sVar7 = (short)(iVar5 >> 4) + param_2;
      iVar5 = (int)(short)(param_7 - param_3) * (int)sVar6;
      if (iVar5 < 0) {
        iVar5 = iVar5 + 0xf;
      }
      sVar2 = (short)(iVar5 >> 4) + param_3;
      iVar5 = (int)(short)(param_8 - param_4) * (int)sVar6;
      if (iVar5 < 0) {
        iVar5 = iVar5 + 0xf;
      }
      sVar3 = (short)(iVar5 >> 4) + param_4;
      FUN_00015d8e(_DAT_00113018,_DAT_0011301c,sVar1,sVar7,sVar2,sVar3,param_9,1);
      FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                   (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar1,sVar7,param_1,
                   param_2,param_9,1);
      sVar4 = sVar2 + sVar1 + -1;
      FUN_00015ca0(_DAT_00113018,_DAT_0011301c,sVar4,sVar7,sVar8,param_2,param_9,1);
      FUN_00015bce(10);
      FUN_00015d8e((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                   (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar1,sVar7,sVar2,sVar3
                   ,param_9,1);
      FUN_00015ca0(_DAT_00113018,_DAT_0011301c,sVar1,sVar7,param_1,param_2,param_9,1);
      FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                   (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar4,sVar7,sVar8,
                   param_2,param_9,1);
      sVar6 = sVar6 + 1;
    } while (sVar6 < 0x10);
    FUN_00015d8e(_DAT_00113018,_DAT_0011301c,param_5,param_6,param_7,param_8,param_9,1);
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,param_5,param_6,param_1,
                 param_2,param_9,1);
    FUN_00015ca0(_DAT_00113018,_DAT_0011301c,param_7 + param_5 + -1,param_6,param_3 + param_1 + -1,
                 param_2,param_9,1);
  }
  return;
}


/* Address 0001640c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001640c(short param_1,short param_2,short param_3,short param_4,short param_5,
                 short param_6,short param_7,short param_8,undefined2 param_9)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  
  if ((param_3 != 0) && (param_7 != 0)) {
    sVar3 = (short)(param_5 + param_1) / 2;
    sVar4 = (short)(param_6 + param_2) / 2;
    sVar5 = (short)(param_7 + param_3) / 2;
    sVar6 = (short)(param_8 + param_4) / 2;
    FUN_00015d8e((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,param_1,param_2,param_3,
                 param_4,_DAT_00113010,0);
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,param_5,param_6,param_1,
                 param_2,_DAT_00113010,0);
    sVar1 = param_3 + param_1 + -1;
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,param_7 + param_5 + -1,
                 param_6,sVar1,param_2,_DAT_00113010,0);
    FUN_00015d8e((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar3,sVar4,sVar5,sVar6,
                 param_9,0);
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar3,sVar4,param_1,
                 param_2,param_9,0);
    sVar2 = sVar5 + sVar3 + -1;
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar2,sVar4,sVar1,param_2
                 ,param_9,0);
    FUN_00015bce(0x3c);
    FUN_00015d8e((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar3,sVar4,sVar5,sVar6,
                 _DAT_00113010,0);
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar3,sVar4,param_1,
                 param_2,_DAT_00113010,0);
    FUN_00015ca0((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
                 (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,sVar2,sVar4,sVar1,param_2
                 ,_DAT_00113010,0);
  }
  return;
}


/* Address 000165c4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

char * FUN_000165c4(char *param_1,short param_2)

{
  char cVar1;
  short sVar2;
  char *pcVar3;
  
  sVar2 = FUN_000146e0(param_1,_DAT_00113004);
  if (param_2 < sVar2) {
    cVar1 = *param_1;
    pcVar3 = &DAT_00112d80;
    while (cVar1 != '\0') {
      *pcVar3 = *param_1;
      cVar1 = param_1[1];
      pcVar3 = pcVar3 + 1;
      param_1 = param_1 + 1;
    }
    *pcVar3 = '\0';
    do {
      if ((int)(pcVar3 + -0x112d80) < 5) break;
      builtin_strncpy(pcVar3 + -4,"...",4);
      sVar2 = FUN_000146e0(&DAT_00112d80,_DAT_00113004);
      pcVar3 = pcVar3 + -1;
    } while (param_2 < sVar2);
    param_1 = &DAT_00112d80;
  }
  return param_1;
}


/* Address 00016640 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00016640(int *param_1,short param_2)

{
  int iVar1;
  short sVar2;
  ushort uVar4;
  undefined4 uVar3;
  short sVar5;
  short sVar6;
  short sVar7;
  ushort uVar8;
  short sVar9;
  
  sVar7 = _DAT_00113002 + _DAT_00113008 * 2;
  _DAT_0011302c = 0x13;
  _DAT_0011302e = sVar7 + -1;
  uVar8 = 0;
  sVar5 = 0;
  iVar1 = *param_1;
  while (iVar1 != 0) {
    if ((*(char *)((int)param_1 + sVar5 * 10 + 9) == '\0') &&
       (uVar4 = FUN_000146e0(*(undefined4 *)((int)param_1 + sVar5 * 10),_DAT_00113004),
       (int)(short)uVar8 < (int)(uint)uVar4)) {
      uVar8 = uVar4;
    }
    sVar5 = sVar5 + 1;
    iVar1 = *(int *)((int)param_1 + sVar5 * 10);
  }
  sVar5 = 1;
  sVar9 = 0;
  sVar6 = 0;
  if (*param_1 != 0) {
    do {
      sVar2 = sVar7;
      if (*(char *)((int)param_1 + sVar6 * 10 + 9) == '\0') {
        if ((short)(_DAT_00113022 + -0x14) < sVar7) {
          sVar5 = sVar5 + 1;
          sVar2 = _DAT_0011302e + 1;
          sVar9 = sVar7;
        }
        else {
          sVar2 = _DAT_00113008 + sVar7 + 1;
        }
      }
      sVar7 = sVar2;
      sVar6 = sVar6 + 1;
    } while (*(int *)((int)param_1 + sVar6 * 10) != 0);
  }
  uVar4 = (short)(_DAT_00113020 + -0x28) / sVar5;
  if ((short)uVar4 < (short)uVar8) {
    uVar8 = uVar4;
  }
  if (sVar5 == 1) {
    _DAT_00113032 = (sVar7 - _DAT_0011302e) + 1;
    uVar4 = uVar8;
  }
  else {
    uVar4 = (sVar5 + -1) * _DAT_0011300a + uVar8 * sVar5;
    _DAT_00113032 = (sVar9 - _DAT_0011302e) + 2;
  }
  _DAT_00113030 = uVar4 + 2;
  if (param_2 != 0) {
    FUN_00016218(_DAT_00113024,_DAT_0011302a + _DAT_00113026 + -1,_DAT_00113028,3,_DAT_0011302c,
                 _DAT_0011302e,_DAT_00113030,_DAT_00113032,_DAT_00113014);
  }
  sVar5 = 0x14;
  sVar7 = _DAT_00113002 + _DAT_00113008 * 2;
  sVar6 = 0;
  iVar1 = *param_1;
  while (iVar1 != 0) {
    if (*(char *)((int)param_1 + sVar6 * 10 + 9) == '\0') {
      uVar4 = _DAT_00113012;
      if (sVar6 == _DAT_0011300e) {
        uVar4 = _DAT_00113016;
      }
      uVar3 = *(undefined4 *)((int)param_1 + sVar6 * 10);
      uVar3 = FUN_000165c4((short)((uint)uVar3 >> 0x10),(short)uVar3,uVar8,_DAT_00113018,
                           _DAT_0011301c,_DAT_00113004,(uint)uVar4 << 0x10);
      FUN_000149ae(sVar5,sVar7,(short)((uint)uVar3 >> 0x10),(short)uVar3);
      sVar7 = _DAT_00113008 + sVar7 + 1;
      if ((short)(_DAT_00113022 + -0x14) < sVar7) {
        sVar7 = _DAT_0011302e + 1;
        sVar5 = _DAT_0011300a + uVar8 + sVar5;
      }
    }
    sVar6 = sVar6 + 1;
    iVar1 = *(int *)((int)param_1 + sVar6 * 10);
  }
  return;
}


/* Address 00016876 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00016876(undefined4 *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = FUN_000146e0(*param_1,_DAT_00113004);
  FUN_000149ae((short)((int)((_DAT_00113020 + -0x28) - (uVar2 & 0xffff)) / 2) + 0x14,0x14,
               (short)((uint)*param_1 >> 0x10),(short)*param_1,(short)((uint)_DAT_00113018 >> 0x10),
               (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,
               (short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004,_DAT_00113012,0);
  FUN_00016092(param_1[1]);
  FUN_00015c1a((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
               (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,0x13,_DAT_00113002 + -1,
               _DAT_00113020 + -0x13,(_DAT_00113022 - _DAT_00113002) + 1,_DAT_00113010);
  uVar1 = *(undefined4 *)(param_1[1] + 4 + _DAT_0011300c * 8);
  FUN_00016640((short)((uint)uVar1 >> 0x10),(short)uVar1,1);
  return;
}


/* Address 0001694c */

undefined4 FUN_0001694c(int param_1,short param_2)

{
  int iVar1;
  
  if (*(int *)(param_1 + param_2 * 10) == 0) {
    return 0xffffffff;
  }
  do {
    param_2 = param_2 + 1;
    iVar1 = param_2 * 10;
    if (*(int *)(param_1 + iVar1) == 0) {
      return 0xffffffff;
    }
  } while (*(char *)(param_1 + 9 + iVar1) != '\0');
  return CONCAT22((short)((uint)iVar1 >> 0x10),param_2);
}


/* Address 0001698c */

short FUN_0001698c(int param_1,short param_2)

{
  do {
    param_2 = param_2 + -1;
    if (param_2 < 0) {
      return param_2;
    }
  } while (*(char *)(param_1 + 9 + param_2 * 10) != '\0');
  return param_2;
}


/* Address 000169b2 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined2 FUN_000169b2(undefined4 param_1)

{
  short sVar1;
  short sVar2;
  short sVar4;
  short sVar5;
  uint uVar3;
  undefined2 uVar6;
  
  FUN_00015c1a((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
               (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,0,0,_DAT_00113020,
               _DAT_00113022,_DAT_00113010);
  sVar2 = (short)(_DAT_00113022 - (_DAT_00113008 * 2 + 0x28)) / 2;
  sVar1 = sVar2 + 0x14;
  sVar4 = FUN_000146e0(4,0x3780,(short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004);
  sVar5 = FUN_000146e0((short)((uint)param_1 >> 0x10),(short)param_1,
                       (short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004);
  sVar4 = (short)(_DAT_00113020 - (sVar5 + sVar4 + 0x28)) / 2 + 0x14;
  sVar5 = FUN_000149ae(sVar4,sVar1,4,0x37a5,(short)((uint)_DAT_00113018 >> 0x10),
                       (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,_DAT_00113004,_DAT_00113012,0);
  sVar5 = sVar5 + sVar4;
  sVar4 = FUN_000149ae(sVar5,sVar1,&DAT_000437ac,(short)((uint)_DAT_00113018 >> 0x10),
                       (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,(short)((uint)_DAT_00113004 >> 0x10),
                       (short)_DAT_00113004,_DAT_00113014,0);
  sVar4 = sVar4 + sVar5;
  sVar5 = FUN_000149ae(sVar4,sVar1,4,0x37ae,(short)((uint)_DAT_00113018 >> 0x10),
                       (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,_DAT_00113004,_DAT_00113012,0);
  FUN_000149ae(sVar5 + sVar4,sVar1,param_1,(short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018
               ,(short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,
               (short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004,_DAT_00113016,0);
  sVar1 = _DAT_00113008 + sVar2 + 0x15;
  sVar4 = FUN_000146e0(s_PRESS_C_TO_CANCEL_00043793,_DAT_00113004);
  sVar4 = (short)(_DAT_00113020 - (sVar4 + 0x28)) / 2 + 0x14;
  sVar5 = FUN_000149ae(sVar4,sVar1,4,0x37ba,(short)((uint)_DAT_00113018 >> 0x10),
                       (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,(short)((uint)_DAT_00113004 >> 0x10),
                       (short)_DAT_00113004,_DAT_00113012,0);
  sVar5 = sVar5 + sVar4;
  sVar4 = FUN_000149ae(sVar5,sVar1,4,0x37c1,(short)((uint)_DAT_00113018 >> 0x10),
                       (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,_DAT_00113004,_DAT_00113014,0);
  FUN_000149ae(sVar4 + sVar5,sVar1,s_TO_CANCEL_000437c3,(short)((uint)_DAT_00113018 >> 0x10),
               (short)_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,
               (short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004,_DAT_00113012,0);
  do {
    uVar3 = FUN_00015bc0();
    if ((uVar3 & 0x20000000) != 0) {
      uVar6 = 1;
      goto LAB_00016bbc;
    }
  } while ((uVar3 & 0x2000) == 0);
  uVar6 = 0;
LAB_00016bbc:
  FUN_00015c1a((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
               (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,0,0,_DAT_00113020,
               _DAT_00113022,_DAT_00113010);
  return uVar6;
}


/* Address 00016bf4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

short FUN_00016bf4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                  undefined2 param_5,undefined2 param_6,undefined2 *param_7)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  
  _DAT_00113018 = param_3;
  _DAT_0011301c = param_4;
  _DAT_00113020 = param_5;
  _DAT_00113022 = param_6;
  _DAT_00113004 = param_2;
  _DAT_00113010 = *param_7;
  _DAT_00113012 = param_7[1];
  _DAT_00113016 = param_7[2];
  _DAT_00113014 = param_7[3];
  uVar3 = FUN_000146e0(1,0x6bf0,(short)((uint)param_2 >> 0x10),(short)param_2);
  _DAT_00113008 = (short)((uint)uVar3 >> 0x10);
  _DAT_0011300a = (undefined2)uVar3;
  _DAT_00113000 = _DAT_00113008 * 2 + 0x14;
  FUN_00015c1a((short)((uint)_DAT_00113018 >> 0x10),(short)_DAT_00113018,
               (short)((uint)_DAT_0011301c >> 0x10),(short)_DAT_0011301c,0,0,_DAT_00113020,
               _DAT_00113022,_DAT_00113010);
  _DAT_0011300c = 0;
  _DAT_0011300e = 0;
  uVar8 = (undefined2)((uint)param_1 >> 0x10);
  uVar9 = (undefined2)param_1;
  FUN_00016876(uVar8,uVar9);
  sVar7 = 0;
LAB_00016cb6:
  do {
    while (uVar4 = FUN_00015bc0(), (uVar4 & 0x400000) != 0) {
      if (0 < _DAT_0011300c) {
        _DAT_0011300c = _DAT_0011300c + -1;
LAB_00016cf4:
        _DAT_0011300e = 0;
        FUN_0001640c(_DAT_0011302c,_DAT_0011302e,_DAT_00113030,_DAT_00113032,_DAT_00113024,
                     _DAT_0011302a + _DAT_00113026 + -1,_DAT_00113028,3,_DAT_00113014);
        FUN_00016876(uVar8,uVar9);
      }
    }
    if ((uVar4 & 0x800000) == 0) {
      if ((uVar4 & 0x100000) == 0) {
        if ((uVar4 & 0x200000) != 0) {
          uVar3 = *(undefined4 *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
          sVar5 = FUN_0001694c((short)((uint)uVar3 >> 0x10),(short)uVar3,_DAT_0011300e);
          goto LAB_00016d98;
        }
        if ((uVar4 & 0x20000000) == 0) {
          if ((uVar4 & 0x2000000) == 0) {
            if ((uVar4 & 0x2000) != 0) {
              return sVar7;
            }
          }
          else {
            iVar1 = *(int *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
            if (*(char *)(iVar1 + 8 + _DAT_0011300e * 10) != '\0') {
              uVar3 = *(undefined4 *)(iVar1 + _DAT_0011300e * 10);
              sVar6 = FUN_000169b2((short)((uint)uVar3 >> 0x10),(short)uVar3);
              sVar5 = _DAT_0011300e;
              if (sVar6 != 0) {
                sVar7 = sVar7 + 1;
                *(undefined1 *)
                 (*(int *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8) + 9 + _DAT_0011300e * 10)
                     = 1;
                uVar3 = *(undefined4 *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
                sVar5 = FUN_0001694c((short)((uint)uVar3 >> 0x10),(short)uVar3,_DAT_0011300e);
                if ((sVar5 < 0) &&
                   (uVar3 = *(undefined4 *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8),
                   sVar5 = FUN_0001698c((short)((uint)uVar3 >> 0x10),(short)uVar3,_DAT_0011300e),
                   sVar5 < 0)) {
                  _DAT_0011300e = 0;
                  sVar5 = _DAT_0011300e;
                }
              }
              goto LAB_00016f1c;
            }
          }
        }
        else {
          iVar1 = *(int *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
          uVar3 = *(undefined4 *)(iVar1 + 4 + _DAT_0011300e * 10);
          uVar2 = *(undefined4 *)(iVar1 + _DAT_0011300e * 10);
          FUN_00015e8e((short)((uint)_DAT_00113004 >> 0x10),(short)_DAT_00113004,
                       (short)((uint)uVar2 >> 0x10),(short)uVar2,(short)((uint)uVar3 >> 0x10),
                       (short)uVar3,_DAT_00113018,(short)((uint)_DAT_0011301c >> 0x10),
                       (short)_DAT_0011301c,_DAT_00113020,_DAT_00113022,_DAT_00113012,_DAT_00113010)
          ;
          FUN_00015c1a(_DAT_00113018,_DAT_0011301c,0,0,_DAT_00113020,_DAT_00113022,_DAT_00113010);
          sVar5 = _DAT_0011300e;
LAB_00016f1c:
          _DAT_0011300e = sVar5;
          FUN_00016876(uVar8,uVar9);
        }
      }
      else {
        uVar3 = *(undefined4 *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
        sVar5 = FUN_0001698c((short)((uint)uVar3 >> 0x10),(short)uVar3,_DAT_0011300e);
LAB_00016d98:
        if (-1 < sVar5) {
          uVar3 = *(undefined4 *)(*(int *)(param_1 + 4) + 4 + _DAT_0011300c * 8);
          _DAT_0011300e = sVar5;
          FUN_00016640((short)((uint)uVar3 >> 0x10),(short)uVar3,0);
        }
      }
      goto LAB_00016cb6;
    }
    if (*(int *)(*(int *)(param_1 + 4) + _DAT_0011300c * 8 + 8) != 0) {
      _DAT_0011300c = _DAT_0011300c + 1;
      goto LAB_00016cf4;
    }
  } while( true );
}


/* Address 00016f3a */

void FUN_00016f3a(int *param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  
  *param_1 = (int)param_1 + *param_1;
  piVar2 = (int *)(param_1[1] + (int)param_1);
  param_1[1] = (int)piVar2;
  sVar5 = 0;
  iVar4 = *piVar2;
  while (iVar4 != 0) {
    iVar4 = (int)sVar5;
    piVar2[iVar4 * 2] = (int)param_1 + piVar2[iVar4 * 2];
    piVar3 = (int *)(piVar2[iVar4 * 2 + 1] + (int)param_1);
    piVar2[iVar4 * 2 + 1] = (int)piVar3;
    sVar6 = 0;
    iVar4 = *piVar3;
    while (iVar4 != 0) {
      piVar1 = (int *)((int)piVar3 + sVar6 * 10);
      *piVar1 = (int)param_1 + *piVar1;
      piVar1 = (int *)((int)piVar3 + sVar6 * 10 + 4);
      *piVar1 = (int)param_1 + *piVar1;
      sVar6 = sVar6 + 1;
      iVar4 = *(int *)((int)piVar3 + sVar6 * 10);
    }
    sVar5 = sVar5 + 1;
    iVar4 = piVar2[sVar5 * 2];
  }
  return;
}


/* Address 00016fb2 */

void FUN_00016fb2(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int *piVar2;
  short sVar3;
  
  piVar2 = *(int **)(*(int *)(param_1 + 4) + 4);
  sVar3 = 0;
  iVar1 = *piVar2;
  while (iVar1 != 0) {
    sVar3 = sVar3 + 1;
    iVar1 = *(int *)((int)piVar2 + sVar3 * 10);
  }
  iVar1 = sVar3 * 10;
  *(undefined4 *)((int)piVar2 + iVar1) = param_2;
  *(undefined4 *)((int)piVar2 + iVar1 + 4) = param_3;
  *(undefined1 *)((int)piVar2 + iVar1 + 8) = 1;
  *(undefined1 *)((int)piVar2 + iVar1 + 9) = 0;
  *(undefined4 *)((int)piVar2 + iVar1 + 10) = 0;
  return;
}


/* Address 00017002 */

void FUN_00017002(int param_1)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  
  piVar2 = *(int **)(param_1 + 4);
  sVar6 = 0;
  iVar1 = *piVar2;
  while (iVar1 != 0) {
    piVar3 = (int *)piVar2[sVar6 * 2 + 1];
    sVar5 = 0;
    sVar7 = 0;
    iVar1 = *piVar3;
    while (iVar1 != 0) {
      iVar1 = sVar7 * 10;
      if (*(char *)((int)piVar3 + iVar1 + 9) == '\0') {
        iVar4 = sVar5 * 10;
        *(undefined4 *)((int)piVar3 + iVar4) = *(undefined4 *)((int)piVar3 + iVar1);
        *(undefined4 *)((int)piVar3 + iVar4 + 4) = *(undefined4 *)((int)piVar3 + iVar1 + 4);
        *(undefined1 *)((int)piVar3 + iVar4 + 8) = *(undefined1 *)((int)piVar3 + iVar1 + 8);
        *(undefined1 *)((int)piVar3 + iVar4 + 9) = 0;
        sVar5 = sVar5 + 1;
      }
      sVar7 = sVar7 + 1;
      iVar1 = *(int *)((int)piVar3 + sVar7 * 10);
    }
    *(undefined4 *)((int)piVar3 + sVar5 * 10) = 0;
    sVar6 = sVar6 + 1;
    iVar1 = piVar2[sVar6 * 2];
  }
  return;
}


/* Address 000170a0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x17e40","bytes":"4eb9000170a0","assembly":"jsr
   $170a0.l"}] */

void observed_call_candidate_000170a0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  DAT_00049b88 = DAT_00049b88 + 1;
  _DAT_00049d0c = DAT_00049b88._2_2_;
  FUN_0000e3e0(&DAT_00049ccc,&DAT_00047b88 + DAT_00049b88 * 0x40,0x40);
  *(undefined2 *)(&DAT_00047ba0 + (DAT_00049b88 + -1) * 0x40) = DAT_00049b88._2_2_;
  iVar1 = DAT_00049b88 * 0x40;
  (&DAT_00047b9c)[DAT_00049b88 * 0x20] = (&DAT_00047b9c)[DAT_00049b88 * 0x20] - DAT_00049b8e;
  *(undefined4 *)(&DAT_00047bc4 + iVar1) = *DAT_00049caa;
  sVar5 = 0;
  do {
    iVar1 = (int)sVar5;
    iVar3 = iVar1 * 0xce;
    iVar4 = DAT_00049b88;
    if (((&DAT_00049d6c)[iVar1 * 0x67] != 0) &&
       ((DAT_00049c60 != 2 || ((short)(&DAT_00049d96)[iVar1 * 0x67] == iRam00049c1c)))) {
      DAT_00049b88 = DAT_00049b88 + 1;
      *(undefined2 *)(iVar3 + 0x49e2c) = DAT_00049b88._2_2_;
      FUN_0000e3e0(iVar3 + 0x49dec,&DAT_00047b88 + DAT_00049b88 * 0x40,0x40);
      iVar1 = DAT_00049b88 + -1;
      *(undefined2 *)(&DAT_00047ba0 + iVar1 * 0x40) = DAT_00049b88._2_2_;
      iVar4 = DAT_00049b88;
      iVar2 = DAT_00049b88 * 0x40;
      (&DAT_00047b9a)[DAT_00049b88 * 0x20] =
           *(short *)((int)&DAT_00049d70 + iVar3 + 2) - DAT_00049c50._2_2_;
      (&DAT_00047b9c)[iVar4 * 0x20] = *(undefined2 *)(&DAT_00049d74 + iVar3);
      (&DAT_00047b9e)[iVar4 * 0x20] =
           *(short *)((int)&DAT_00049d76 + iVar3 + 2) - DAT_00049c56._2_2_;
      (&DAT_00047b9c)[iVar4 * 0x20] = (&DAT_00047b9c)[iVar4 * 0x20] - DAT_00049b8e;
      iVar4 = DAT_00049b88;
      if ((*(short *)(&DAT_00049e0c + iVar3) == 8) &&
         (iVar4 = iVar1, *(int *)((int)&DAT_00049dca + iVar3) != 0)) {
        *(undefined4 *)(&DAT_00047bc4 + iVar2) = **(undefined4 **)((int)&DAT_00049dca + iVar3);
        iVar4 = DAT_00049b88;
      }
    }
    DAT_00049b88 = iVar4;
    sVar5 = sVar5 + 1;
  } while (sVar5 < 0x28);
  sVar5 = 0;
  do {
    iVar1 = (int)sVar5;
    iVar4 = iVar1 * 0x1e;
    if (((&DAT_0004bd9c)[iVar1 * 0xf] != 0) &&
       ((DAT_00049c60 != 2 || (*(short *)(iVar4 + 0x4bdac) == iRam00049c1c)))) {
      DAT_00049b88 = DAT_00049b88 + 1;
      iVar3 = DAT_00049b88 * 0x40;
      *(undefined4 *)(&DAT_00047bac + iVar3) = _DAT_000437e0;
      *(undefined4 *)(&DAT_00047bb0 + iVar3) = _DAT_000437e4;
      *(undefined4 *)(&DAT_00047bb4 + iVar3) = _DAT_000437e8;
      *(undefined **)(&DAT_00047bb8 + iVar3) = PTR_DAT_000437ec;
      *(undefined **)(&DAT_00047bbc + iVar3) = PTR_DAT_000437f0;
      *(undefined **)(&DAT_00047bc0 + iVar3) = PTR_DAT_000437f4;
      *(undefined2 *)(&DAT_00047ba0 + (DAT_00049b88 + -1) * 0x40) = DAT_00049b88._2_2_;
      iVar2 = DAT_00049b88;
      iVar3 = DAT_00049b88 * 0x40;
      (&DAT_00047b9a)[DAT_00049b88 * 0x20] = *(short *)(iVar4 + 0x4bda0) - DAT_00049c50._2_2_;
      (&DAT_00047b9c)[iVar2 * 0x20] = *(undefined2 *)(iVar4 + 0x4bda2);
      (&DAT_00047b9e)[iVar2 * 0x20] = *(short *)(iVar4 + 0x4bda6) - DAT_00049c56._2_2_;
      (&DAT_00047b9c)[iVar2 * 0x20] = (&DAT_00047b9c)[iVar2 * 0x20] - DAT_00049b8e;
      if (((&DAT_0004208c)[(ushort)(&DAT_0004bd9c)[iVar1 * 0xf]] & 2) == 0) {
        *(undefined2 *)(&DAT_00047b98 + iVar3) = 0x4000;
        *(undefined2 *)(&DAT_00047b90 + iVar3) = 0x4000;
        *(undefined2 *)(&DAT_00047b88 + iVar3) = 0x4000;
        *(undefined2 *)(&DAT_00047b8e + iVar3) = 0;
        *(undefined2 *)(&DAT_00047b8c + iVar3) = 0;
        *(undefined2 *)(&DAT_00047b8a + iVar3) = 0;
        *(undefined2 *)(&DAT_00047b96 + iVar3) = 0;
        *(undefined2 *)(&DAT_00047b94 + iVar3) = 0;
        *(undefined2 *)(&DAT_00047b92 + iVar3) = 0;
        *(undefined2 *)(&DAT_00047ba8 + iVar3) = 8;
        *(undefined4 *)(&DAT_00047bc4 + iVar3) = **(undefined4 **)((int)&DAT_0004bdb0 + iVar4);
      }
      else {
        *(undefined2 *)(&DAT_00047ba8 + iVar3) = 7;
        *(undefined4 *)(&DAT_00047bc4 + iVar3) = *(undefined4 *)(iVar4 + 0x4bdb4);
        FUN_0000e220(&DAT_00047b88 + iVar3,0,*(undefined1 *)(iVar4 + 0x4bda8),0,0);
      }
    }
    sVar5 = sVar5 + 1;
  } while (sVar5 < 0x28);
  *(undefined2 *)(&DAT_00047ba0 + DAT_00049b88 * 0x40) = 0;
  return;
}


/* Address 00017340 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00017340(void)

{
  _DAT_00043800 = &DAT_00113040;
  _DAT_00043804 = &DAT_0011304c;
  _DAT_00113040 = 0;
  _DAT_00113044 = 0;
  _DAT_0011304c = 0;
  _DAT_00113050 = 0;
  _DAT_00113048 = 0;
  _DAT_00113054 = 0;
  return;
}


/* Address 00017e0e */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x17dda","bytes":"4eb900017e0e","assembly":"jsr
   $17e0e.l"}] */

void observed_call_candidate_00017e0e(void)

{
  int iVar1;
  short sVar2;
  
  if (DAT_00049c60 != 0) {
    FUN_0000e03a(DAT_000bd83c,0);
    DAT_00049b88 = 0;
    if (DAT_00049c60 == 1) {
      observed_call_candidate_0000e0a6();
      observed_call_candidate_000170a0();
      if (DAT_00049b88 != 0) {
        FUN_0000e19e();
        FUN_0000e202();
        do {
        } while (_DAT_0010a684 != 0);
        FUN_0000e098();
      }
    }
    else if (DAT_00049c60 == 2) {
      iRam00049c1c = (int)DAT_00049c76;
      func_0x0000e0f2();
      sVar2 = 0;
      iVar1 = iRam0010d688;
      while ((iVar1 != 0xffff && (*(int *)((short)(sVar2 + 1) * 4 + 0x10d688) != 0))) {
        iRam00049c1c = *(int *)(sVar2 * 4 + 0x10d688);
        func_0x0000e148();
        observed_call_candidate_000170a0();
        if (DAT_00049b88 != 0) {
          FUN_0000e19e();
          FUN_0000e202();
          do {
          } while (_DAT_0010a684 != 0);
          FUN_0000e098();
        }
        sVar2 = sVar2 + 2;
        iVar1 = *(int *)(sVar2 * 4 + 0x10d688);
      }
    }
    else if (DAT_00049c60 == 3) {
      DAT_00049b88 = 0;
    }
    FUN_00017f14();
  }
  return;
}


/* Address 00017f14 */

void FUN_00017f14(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar2 = DAT_000bd83c;
  PTR_DAT_00043daa = DAT_000bd834;
  uVar1 = DAT_000bd830;
  DAT_000bd83c = DAT_000bd840;
  DAT_000bd840 = DAT_000bd844;
  DAT_000bd844 = uVar2;
  DAT_000bd830 = DAT_000bd834;
  DAT_000bd834 = (undefined *)DAT_000bd838;
  DAT_000bd838 = uVar1;
  FUN_000185b2(&DAT_00043da0,&DAT_000777c0);
  return;
}


/* Address 00018160 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00018160(void)

{
  _DAT_00f02268 = 0;
  _DAT_00f0226c = 0;
  _DAT_00f02200 = &DAT_000b29d0;
  _DAT_00f02204 = 0x2e20;
  _DAT_00f0220c = 0;
  _DAT_00f0223c = 0x113b0;
  _DAT_00f02238 = 0x10200;
  _DAT_00113060 = 0;
  _DAT_00f00400 = 0;
  _DAT_00f00402 = 0x77f;
  _DAT_00f00404 = 0x7040;
  _DAT_00f00406 = 0x707f;
  return;
}


/* Address 000181f8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x17de6","bytes":"4eb9000181f8","assembly":"jsr
   $181f8.l"}] */

void observed_call_candidate_000181f8(void)

{
  short sVar1;
  short sVar2;
  undefined2 uVar3;
  short sVar4;
  undefined1 auStack_36 [50];
  
  if (_DAT_0004451c != 0) {
    _DAT_00f02268 = 0;
    _DAT_00f0226c = 0;
  }
  _DAT_00044518 = _DAT_00049d6a;
  _DAT_0004451a = _DAT_00049d68;
  _DAT_0004451c = _DAT_00049d5c;
  if (_DAT_00113060 == 0) {
    _DAT_00113060 = 1;
  }
  _DAT_00f02200 = &DAT_000b29d0;
  _DAT_00f02204 = 0x14600;
  _DAT_00f0220c = (undefined *)0x90102;
  _DAT_00f02210 = 0x124;
  _DAT_00f02224 = 0x44168;
  _DAT_00f02228 = &switchD_000147fc::switchdataD_00014800;
  _DAT_00f02230 = (ushort)(-(ushort)DAT_00049cba - 0x50) & 0xfe;
  _DAT_00f02234 = 0x164;
  _DAT_00f0223c = 0xb009c;
  _DAT_00f02238 = 0x1800609;
  sVar1 = (short)(DAT_00049c50 >> 6);
  sVar2 = (short)(DAT_00049c56 >> 6);
  if (((sVar1 != _DAT_0004451e) || (sVar2 != _DAT_00044520)) || (DAT_00049c62 != _DAT_00044522)) {
    _DAT_00044522 = DAT_00049c62;
    if (DAT_00049c62 < 0) {
      sVar4 = -DAT_00049c62;
      uVar3 = 0x81da;
    }
    else {
      sVar4 = DAT_00049c62 + 1;
      uVar3 = 0x81e9;
    }
    _DAT_0004451e = sVar1;
    _DAT_00044520 = sVar2;
    FUN_0001b45a(auStack_36,1,uVar3,sVar1,sVar2,sVar4);
    _DAT_00f02268 = 0;
    _DAT_00f0226c = 0;
    _DAT_00f02200 = &DAT_000b29d0;
    _DAT_00f02204 = 0x2620;
    _DAT_00f02210 = 0x13;
    _DAT_00f0220c = &DAT_00040002;
    _DAT_00f0223c = 0x70009;
    _DAT_00f02238 = 0x10200;
    FUN_000149ae(0x16,2,auStack_36,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,2);
  }
  return;
}


/* Address 000185b2 */

/* WARNING: Removing unreachable block (ram,0x000185ec) */
/* WARNING: Removing unreachable block (ram,0x00018642) */

void FUN_000185b2(ushort *param_1,uint *param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  int iVar6;
  bool bVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  ushort *puVar13;
  uint *puVar14;
  ushort *puVar15;
  uint *puVar16;
  uint *puVar17;
  uint local_40;
  ushort *local_14;
  undefined1 *local_10;
  
  iVar9 = 1;
  uVar5 = *param_1;
  puVar15 = param_1;
  while (uVar5 != 4) {
    iVar9 = iVar9 + 1;
    puVar15 = puVar15 + 0x12;
    uVar5 = *puVar15;
  }
  iVar6 = iVar9 * -4;
  local_10 = &stack0xffffffc4 + iVar6;
  uVar12 = 0xeede;
  bVar7 = false;
  puVar15 = param_1;
  puVar17 = (uint *)(&stack0xffffffc4 + iVar6);
  do {
    uVar5 = *puVar15;
    if (uVar5 == 1) {
      uVar12 = uVar12 + 3 & 0xfffffffc;
      iVar10 = 3;
    }
    else if (uVar5 == 0) {
      uVar12 = uVar12 + 1 & 0xfffffffe;
      iVar10 = 2;
    }
    else {
      if (uVar5 == 4) {
        bVar7 = true;
      }
      iVar10 = 1;
    }
    *puVar17 = uVar12;
    uVar12 = iVar10 + uVar12;
    puVar15 = puVar15 + 0x12;
    puVar17 = puVar17 + 1;
  } while (!bVar7);
  bVar7 = false;
  uVar12 = 0xeede;
  puVar15 = param_1 + 2;
  puVar17 = (uint *)(param_1 + 5);
  puVar16 = (uint *)(param_1 + 3);
  puVar13 = param_1 + 1;
  local_14 = param_1 + 9;
  do {
    uVar8 = *(uint *)(local_10 + 4);
    puVar14 = param_2;
    switch(*param_1) {
    case 0:
      uVar11 = 1;
      goto LAB_000186c4;
    case 1:
      uVar11 = 3;
LAB_000186c4:
      while ((uVar11 & uVar12) != 0) {
        uVar12 = uVar12 + 1;
        *puVar14 = (int)(uVar12 & 0x7ff00) >> 8;
        puVar14[1] = (uint)(ushort)((short)uVar12 << 8) << 0x10 | 3;
        puVar14 = puVar14 + 2;
      }
      if (*puVar16 != 0) {
        uVar8 = (&local_40)[*puVar16 - iVar9];
      }
      uVar1 = param_1[7];
      uVar5 = *puVar15;
      uVar2 = *param_1;
      *puVar14 = (int)(uVar8 & 0x7ff00) >> 8 | (*puVar17 & 0xfffff8) << 8;
      puVar14[1] = (uint)uVar2 |
                   (uint)uVar5 << 3 | (uint)uVar1 << 0xe | (uint)(ushort)((short)uVar8 << 8) << 0x10
      ;
      uVar5 = *local_14;
      uVar1 = param_1[8];
      uVar3 = param_1[0xb];
      uVar4 = param_1[10];
      uVar2 = *puVar13;
      puVar14[2] = (uint)((*local_14 & 0x3f0) >> 4) |
                   (uint)param_1[0xc] << 6 |
                   (uint)param_1[0xd] << 0xd | (uint)(ushort)(param_1[0xe] << 1) << 0x10;
      param_2 = puVar14 + 4;
      puVar14[3] = (uint)uVar2 |
                   (uint)uVar4 << 0xc |
                   (uint)uVar3 << 0xf | (uint)(ushort)(uVar1 << 2) << 0x10 | (uint)uVar5 << 0x1c;
      uVar12 = uVar12 + 2;
      if (*param_1 == 1) {
        uVar8 = (uint)param_1[0x10] << 8 | (uint)param_1[0x11] << 0x10;
        uVar5 = param_1[0xf];
        puVar14 = puVar14 + 5;
        *param_2 = 0;
LAB_000187bc:
        param_2 = puVar14 + 1;
        *puVar14 = uVar5 | uVar8;
        uVar12 = uVar12 + 1;
      }
      break;
    case 2:
      uVar8 = (uint)*puVar15 << 3 | *puVar17 << 0xe;
      uVar5 = *param_1;
      puVar14 = param_2 + 1;
      *param_2 = *puVar16;
      goto LAB_000187bc;
    case 3:
      uVar8 = *(uint *)(&stack0xffffffc4 + *puVar16 * 4 + iVar6);
      uVar5 = *puVar13;
      uVar2 = *puVar15;
      uVar1 = *param_1;
      puVar14 = param_2 + 1;
      *param_2 = (int)(uVar8 & 0x7ff00) >> 8;
      param_2 = param_2 + 2;
      *puVar14 = (uint)uVar1 |
                 (uVar2 & 0x1fff) << 3 |
                 (uint)uVar5 << 0xe | (uint)(ushort)((short)uVar8 << 8) << 0x10;
      break;
    case 4:
      uVar8 = *puVar17;
      uVar5 = *puVar15;
      uVar2 = *param_1;
      puVar14 = param_2 + 1;
      *param_2 = *puVar16;
      param_2 = param_2 + 2;
      *puVar14 = (uint)uVar2 | (uVar5 & 1) << 3 | uVar8 << 4;
      uVar12 = uVar12 + 1;
      bVar7 = true;
    }
    puVar15 = puVar15 + 0x12;
    puVar17 = puVar17 + 9;
    puVar16 = puVar16 + 9;
    puVar13 = puVar13 + 0x12;
    local_14 = local_14 + 0x12;
    param_1 = param_1 + 0x12;
    local_10 = local_10 + 4;
    if (bVar7) {
      return;
    }
  } while( true );
}


/* Address 00018df2 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00018df2(void)

{
  short sVar1;
  ushort uVar2;
  
  if (((_DAT_00049d5e != 0) && (_DAT_00049d5c != 0)) && (DAT_00049d62 < 1)) {
    sVar1 = DAT_00049d12 + DAT_00049d66 * 2;
    uVar2 = FUN_0001a77c(100);
    if ((short)(uVar2 & 0x3ff) < (short)(sVar1 + 200)) {
      (&DAT_00049e34)[DAT_00049d60 * 0x67] =
           (&DAT_00049e34)[DAT_00049d60 * 0x67] - *(short *)(&DAT_000461b4 + DAT_00049d5a * 2);
    }
    DAT_00049d62 = 300;
  }
  if ((DAT_00049c50 >> 6 == 0xbf) && (DAT_00049c56 >> 6 == 0x22f)) {
    _DAT_00043d98 = 1;
  }
  return;
}


/* Address 00018e92 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00018e92(void)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  
  sVar2 = 1;
  sVar3 = 0;
  sVar4 = 0;
  if (DAT_00049c60 == 1) {
    *PTR_DAT_00040ffc = 0x20;
    PTR_DAT_00040ffc[1] = 0x5f;
    PTR_DAT_00040ffc[2] = 0x5f;
    PTR_DAT_00040ffc[3] = 0x5f;
    PTR_DAT_00040ffc[5] = 0x5f;
    PTR_DAT_00040ffc[6] = 0x5f;
    PTR_DAT_00040ffc[7] = 0x5f;
    do {
      while( true ) {
        FUN_00012620(1);
        while (_DAT_00049ba4 != 0) {
          FUN_0000e4c0();
        }
        do {
        } while (DAT_000778cc < DAT_000778cc + 0x4b);
        while (_DAT_00049ba4 == 0) {
          FUN_0000e4c0();
        }
        sVar1 = FUN_0001b718((short)(_DAT_00049ba4 >> 0x10),(short)_DAT_00049ba4);
        if (sVar1 < 0) break;
        if (sVar2 < 4) {
          PTR_DAT_00040ffc[sVar2] = (char)sVar1 + '0';
          sVar3 = sVar1 + sVar3 * 10;
          sVar2 = sVar2 + 1;
          if (sVar2 == 4) {
            sVar2 = 5;
          }
        }
        else if (sVar2 < 8) {
          PTR_DAT_00040ffc[sVar2] = (char)sVar1 + '0';
          sVar4 = sVar1 + sVar4 * 10;
          sVar2 = sVar2 + 1;
        }
      }
      if (((((_DAT_00049ba4 & 0x20000000) != 0) && (sVar2 == 8)) && (sVar3 < 0x3c7)) &&
         (((sVar4 < 0x2d0 && (0x1f < sVar3)) && (0x1f < sVar4)))) {
        DAT_00049c50 = (int)sVar3 << 6 | 0x20;
        DAT_00049c56 = (int)sVar4 << 6 | 0x20;
        _DAT_00045d98 = 1;
        FUN_00020e8c();
        FUN_0000df60();
        FUN_0000df22();
        FUN_00020f78(1);
        FUN_0000df3e();
        return;
      }
      if ((_DAT_00049ba4 & 0x2000000) != 0) {
        if (1 < sVar2) {
          sVar2 = sVar2 + -1;
        }
        if (sVar2 == 4) {
          sVar2 = 3;
        }
        PTR_DAT_00040ffc[sVar2] = 0x5f;
        if (sVar2 < 4) {
          sVar3 = sVar3 / 10;
        }
        else {
          sVar4 = sVar4 / 10;
        }
      }
    } while ((_DAT_00049ba4 & 0x2000) == 0);
  }
  return;
}


/* Address 000190bc */

void FUN_000190bc(void)

{
  char cVar1;
  short sVar2;
  char acStackY_800e [32752];
  char local_e [14];
  
  if ((*(byte *)(DAT_00049c18 + 0xc) & 0x40) == 0) {
    *PTR_DAT_000410ba = 0x20;
    PTR_DAT_000410ba[1] = 0x20;
    PTR_DAT_000410ba[2] = 0x20;
    PTR_DAT_000410ba[3] = 0x20;
  }
  else {
    *PTR_DAT_000410ba = 0x44;
    PTR_DAT_000410ba[1] = 0x4f;
    PTR_DAT_000410ba[2] = 0x57;
    PTR_DAT_000410ba[3] = 0x4e;
  }
  if (*(short *)(DAT_00049c18 + 0xc) < 0) {
    *PTR_DAT_000410b2 = 0x55;
    PTR_DAT_000410b2[1] = 0x50;
  }
  else {
    *PTR_DAT_000410b2 = 0x20;
    PTR_DAT_000410b2[1] = 0x20;
  }
  sVar2 = DAT_00049c62;
  if (-1 < DAT_00049c62) {
    sVar2 = DAT_00049c62 + 1;
  }
  FUN_0001b45a(local_e,&DAT_000190b8,sVar2);
  if (local_e[0] == '-') {
    local_e[0] = 'B';
  }
  *PTR_s__0004107f_9_000410b6 = 0x20;
  PTR_s__0004107f_9_000410b6[1] = 0x20;
  PTR_s__0004107f_9_000410b6[2] = 0x20;
  PTR_s__0004107f_9_000410b6[3] = 0x20;
  sVar2 = 0;
  cVar1 = local_e[0];
  while (cVar1 != '\0') {
    PTR_s__0004107f_9_000410b6[sVar2] = local_e[sVar2];
    sVar2 = sVar2 + 1;
    cVar1 = local_e[sVar2];
  }
  FUN_00012620(4);
  return;
}


/* Address 000191f4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000191f4(void)

{
  char cVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  short sVar8;
  int iVar6;
  uint uVar7;
  undefined **ppuVar9;
  undefined2 uVar10;
  
  if (_DAT_0004624a == 0) {
    DAT_0004624c = 0;
    DAT_0004624e = 0;
  }
  _DAT_0004624a = 0;
  if (0 < DAT_00049d62) {
    DAT_00049d62 = DAT_00049d62 - DAT_0004c24c._2_2_;
  }
  if (DAT_00049c4e != 0) {
    DAT_00049d14 = DAT_00049d14 - DAT_00049c4e;
    DAT_00049c4e = 0;
    _DAT_00049cb4 = (&PTR_DAT_0004613c)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
    DAT_00049cb8 = 0xc;
    DAT_00049cc4 = 0;
    DAT_00049cc8 = 0;
  }
  if (DAT_00049cb8 != 1) {
    DAT_00046250 = 300;
  }
  if (0xc < DAT_00049cb8) {
    _DAT_0004624a = 0;
    return;
  }
  switch(DAT_00049cb8) {
  case 0:
    goto switchD_0001929e_caseD_0;
  case 1:
    if ((DAT_00049c60 == 2) && (*DAT_00049c78 < 0)) {
      if (DAT_00046250 < 1) {
        do {
          FUN_000190bc();
          do {
            FUN_0000e4c0();
          } while (_DAT_00049ba4 == 0);
          FUN_0001a0f8();
        } while ((_DAT_00049ba4 & 0x300000) != 0);
        DAT_00046250 = 300;
      }
      else {
        DAT_00046250 = DAT_00046250 - DAT_0004c24c._2_2_;
      }
    }
    uVar4 = DAT_000778cc;
    uVar3 = DAT_00049b90;
    uVar2 = DAT_00049b8e;
    uVar10 = DAT_00049b8c;
    if ((_DAT_00049ba4 & 0x20000000) == 0) {
      if ((_DAT_00049ba4 & 0x2000000) == 0) {
        if ((_DAT_00049ba4 & 0x100000) != 0) {
          _DAT_00049cb4 = (&PTR_DAT_00045e6c)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
          DAT_00049cb8 = 5;
          return;
        }
        if ((_DAT_00049ba4 & 0x200000) != 0) {
          _DAT_00049cb4 = (&PTR_DAT_00045ea8)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
          DAT_00049cb8 = 7;
          return;
        }
        if ((_DAT_00049ba4 & 0x400000) == 0) {
          if (-1 < DAT_00049ba5) {
            return;
          }
          DAT_0004624c = DAT_0004624c + 1;
          cVar1 = -(char)DAT_0004624c;
          if (7 < DAT_0004624c) {
            DAT_0004624c = 7;
          }
          DAT_0004624e = 0;
        }
        else {
          DAT_0004624e = DAT_0004624e + 1;
          cVar1 = (char)DAT_0004624e;
          if (7 < DAT_0004624e) {
            DAT_0004624e = 7;
          }
          DAT_0004624c = 0;
        }
        DAT_00049cba = cVar1 + DAT_00049cba;
        _DAT_0004624a = 1;
        DAT_00046250 = 300;
        return;
      }
      if ((_DAT_00049ba4 & 0x400000) != 0) {
        _DAT_00049cb4 = (&PTR_DAT_00045f20)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
        DAT_00049cb8 = 3;
        return;
      }
      if (DAT_00049ba5 < '\0') {
        _DAT_00049cb4 = (&PTR_DAT_00045f5c)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
        DAT_00049cb8 = 4;
        return;
      }
      if ((_DAT_00049ba4 & 0x200000) != 0) {
        _DAT_00049cb4 = (&PTR_DAT_00045f98)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
        DAT_00049cb8 = 10;
        DAT_00049cc4 = 0;
        DAT_00049cc8 = 0;
        return;
      }
      if ((_DAT_00049ba4 & 0x100000) != 0) {
        _DAT_00049cb4 = (&PTR_DAT_000460c4)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
        DAT_00049cb8 = 0xb;
        return;
      }
      if ((_DAT_00049ba4 & 0x2000) == 0) {
        return;
      }
      if (DAT_00049d5a < 1) {
        iVar6 = (int)DAT_00049d54;
        if ((&DAT_000461be)[(short)(&DAT_00049d2c)[iVar6]] == '\0') {
          if (((((ushort)((&DAT_00049d2c)[iVar6] - 0x41) < 2) ||
               ((ushort)((&DAT_00049d2c)[iVar6] - 0x43) < 2)) || ((&DAT_00049d2c)[iVar6] == 0x45))
             || ((&DAT_00049d2c)[iVar6] == 0x66)) {
            uVar5 = FUN_0001aade();
            FUN_0000df22();
            FUN_00011e6c();
            DAT_00049b8c = uVar10;
            DAT_00049b8e = uVar2;
            DAT_00049b90 = uVar3;
            FUN_00018160();
            if (DAT_00049c60 == 1) {
              uVar10 = 1;
            }
            else {
              uVar10 = 2;
            }
            FUN_0001aa40(uVar10);
            FUN_0001ab2a((short)((uint)uVar5 >> 0x10),(short)uVar5);
            FUN_0000df3e();
          }
          DAT_000778cc = uVar4;
          if ((&DAT_00049d2c)[DAT_00049d54] == 0x46) {
            FUN_00018e92();
            return;
          }
        }
        else {
          FUN_0001b002(*(undefined2 *)(&DAT_00045d9a + DAT_00049d5a * 2 + DAT_00049c4c * 10));
          DAT_00049d5a = (short)(char)(&DAT_000461be)[(short)(&DAT_00049d2c)[DAT_00049d54]];
          DAT_00049ca4 = (int *)FUN_0001af04(*(undefined2 *)
                                              (&DAT_00045d9a + DAT_00049d5a * 2 + DAT_00049c4c * 10)
                                            );
          FUN_0001545c((short)((uint)DAT_00049caa >> 0x10),(short)DAT_00049caa);
          DAT_00049caa = (undefined4 *)FUN_000152a2(*(int *)(*DAT_00049ca4 + 8) * 2 + 0x10);
          *(char **)*DAT_00049caa = s_FR__ACCOLADY_Hello_and_goode_day_0002bfc8 + 0x38;
          _DAT_00049cb4 = *(undefined **)(DAT_00049c4c * 0x14 + 0x45df4 + DAT_00049d5a * 4);
          do {
            FUN_0000eb04(4,0x9c4c);
            FUN_0000df60();
          } while (*(char *)(DAT_00049cb0 + 2) == '\0');
        }
      }
      else {
        _DAT_00049cb4 = *(undefined **)(DAT_00049c4c * 0x14 + 0x45db8 + DAT_00049d5a * 4);
        do {
          FUN_0000eb04(4,0x9c4c);
          FUN_0000df60();
        } while (*(char *)(DAT_00049cb0 + 2) == '\0');
        FUN_0001b002(*(undefined2 *)(&DAT_00045d9a + DAT_00049d5a * 2 + DAT_00049c4c * 10));
        DAT_00049d5a = 0;
        DAT_00049ca4 = (int *)FUN_0001af04(*(undefined2 *)(&DAT_00045d9a + DAT_00049c4c * 10));
        FUN_0001545c((short)((uint)DAT_00049caa >> 0x10),(short)DAT_00049caa);
        DAT_00049caa = (undefined4 *)FUN_000152a2(*(int *)(*DAT_00049ca4 + 8) * 2 + 0x10);
        *(char **)*DAT_00049caa = s_FR__ACCOLADY_Hello_and_goode_day_0002bfc8 + 0x38;
      }
      _DAT_00049cb4 = (undefined *)DAT_00049cb0;
      return;
    }
    if ((_DAT_00049ba4 & 0x2000000) == 0) {
      ppuVar9 = &PTR_DAT_00046010 + DAT_00049c4c * 5;
      goto LAB_00019e6a;
    }
    if (((_DAT_00049ba4 & 0x100000) != 0) && (DAT_00049d5a == 0)) {
      _DAT_00049cb4 = (&PTR_DAT_00046088)[DAT_00049c4c * 5];
      DAT_00049cb8 = 2;
      return;
    }
    goto LAB_00019e48;
  case 2:
    if ((*(byte *)(DAT_00049cb0 + 2) & 2) != 0) {
      FUN_00018df2();
    }
    break;
  case 3:
    DAT_00049cde = DAT_00049cde - (DAT_00049ccc >> 0xe);
    DAT_00049ce0 = DAT_00049ce0 - (DAT_00049cce >> 0xe);
    DAT_00049ce2 = DAT_00049ce2 - (DAT_00049cd0 >> 0xe);
    break;
  case 4:
    DAT_00049cde = (DAT_00049ccc >> 0xe) + DAT_00049cde;
    DAT_00049ce0 = (DAT_00049cce >> 0xe) + DAT_00049ce0;
    DAT_00049ce2 = (DAT_00049cd0 >> 0xe) + DAT_00049ce2;
    break;
  case 5:
    if ((_DAT_00049ba4 & 0x2000) != 0) {
      _DAT_00049cb4 = (&PTR_DAT_00045ee4)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 8;
    }
    if ((_DAT_00049ba4 & 0x100000) != 0) {
      if ((_DAT_00049ba4 & 0x400000) == 0) {
        if (DAT_00049ba5 < '\0') {
          DAT_0004624c = DAT_0004624c + 1;
          DAT_00049cba = DAT_00049cba - (char)DAT_0004624c;
          if (7 < DAT_0004624c) {
            DAT_0004624c = 7;
          }
          DAT_0004624e = 0;
          _DAT_0004624a = 1;
          sVar8 = DAT_0004c24c._2_2_ * 2;
        }
        else {
          if ((_DAT_00049ba4 & 0x2000000) != 0) {
            _DAT_0004624a = 0;
            _DAT_00049cb4 = (&PTR_DAT_00046100)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
            DAT_00049cb8 = 6;
            return;
          }
          sVar8 = DAT_0004c24c._2_2_ * 2;
        }
      }
      else {
        DAT_0004624e = DAT_0004624e + 1;
        DAT_00049cba = (char)DAT_0004624e + DAT_00049cba;
        if (7 < DAT_0004624e) {
          DAT_0004624e = 7;
        }
        DAT_0004624c = 0;
        _DAT_0004624a = 1;
        sVar8 = DAT_0004c24c._2_2_ * 2;
      }
      goto LAB_00019d42;
    }
    goto LAB_00019e8e;
  case 6:
    if ((*(byte *)(DAT_00049cb0 + 2) & 1) != 0) {
      _DAT_00049cb4 = (&PTR_DAT_00045e6c)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 5;
    }
    sVar8 = DAT_0004c24c._2_2_ * 2;
    goto LAB_00019d42;
  case 7:
    if ((_DAT_00049ba4 & 0x200000) != 0) {
      if ((_DAT_00049ba4 & 0x2000000) != 0) {
        _DAT_0004624a = 0;
        _DAT_00049cb4 = (&PTR_DAT_00045f98)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
        DAT_00049cb8 = 10;
        DAT_00049cc4 = 0;
        return;
      }
      if ((_DAT_00049ba4 & 0x400000) == 0) {
        if (DAT_00049ba5 < '\0') {
          DAT_0004624c = DAT_0004624c + 1;
          DAT_00049cba = DAT_00049cba - (char)DAT_0004624c;
          if (7 < DAT_0004624c) {
            DAT_0004624c = 7;
          }
          DAT_0004624e = 0;
          _DAT_0004624a = 1;
          iVar6 = FUN_0000e588(DAT_0004c24c._2_2_ * -0x18,0,0,300);
          uVar7 = iVar6 - DAT_00049cc8;
          DAT_00049cc8 = -(uVar7 & 0xffff);
        }
        else {
          iVar6 = FUN_0000e588(DAT_0004c24c._2_2_ * -0x18,0,0,300);
          uVar7 = iVar6 - DAT_00049cc8;
          DAT_00049cc8 = -(uVar7 & 0xffff);
        }
      }
      else {
        DAT_0004624e = DAT_0004624e + 1;
        DAT_00049cba = (char)DAT_0004624e + DAT_00049cba;
        if (7 < DAT_0004624e) {
          DAT_0004624e = 7;
        }
        DAT_0004624c = 0;
        _DAT_0004624a = 1;
        iVar6 = FUN_0000e588(DAT_0004c24c._2_2_ * -0x18,0,0,300);
        uVar7 = iVar6 - DAT_00049cc8;
        DAT_00049cc8 = -(uVar7 & 0xffff);
      }
      goto LAB_00019d6c;
    }
    goto LAB_00019e8e;
  case 8:
    if ((_DAT_00049ba4 & 0x2000) == 0) {
      _DAT_00049cb4 = (&PTR_DAT_00045e6c)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 5;
    }
    if ((_DAT_00049ba4 & 0x100000) != 0) {
      if ((_DAT_00049ba4 & 0x400000) == 0) {
        if (DAT_00049ba5 < '\0') {
          DAT_0004624c = DAT_0004624c + 1;
          DAT_00049cba = DAT_00049cba - (char)DAT_0004624c;
          if (7 < DAT_0004624c) {
            DAT_0004624c = 7;
          }
          DAT_0004624e = 0;
          _DAT_0004624a = 1;
        }
        else if ((_DAT_00049ba4 & 0x2000000) != 0) {
          _DAT_0004624a = 0;
          _DAT_00049cb4 = (&PTR_DAT_00046100)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
          DAT_00049cb8 = 9;
          return;
        }
      }
      else {
        DAT_0004624e = DAT_0004624e + 1;
        DAT_00049cba = (char)DAT_0004624e + DAT_00049cba;
        if (7 < DAT_0004624e) {
          DAT_0004624e = 7;
        }
        DAT_0004624c = 0;
        _DAT_0004624a = 1;
      }
      goto LAB_00019d32;
    }
    goto LAB_00019e8e;
  case 9:
    if ((*(byte *)(DAT_00049cb0 + 2) & 1) != 0) {
      _DAT_00049cb4 = (&PTR_DAT_00045ee4)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 8;
    }
LAB_00019d32:
    sVar8 = (short)(DAT_0004c24c << 3);
LAB_00019d42:
    iVar6 = FUN_0000e588((DAT_0004c24c._2_2_ + sVar8) * 8,0,0,300);
    uVar7 = DAT_00049cc8 + iVar6;
    DAT_00049cc8 = uVar7 & 0xffff;
LAB_00019d6c:
    DAT_00049cc4 = (int)(short)(uVar7 >> 0x10);
    return;
  case 10:
    if ((_DAT_00049ba4 & 0x400000) == 0) {
      if (DAT_00049ba5 < '\0') {
        DAT_0004624c = DAT_0004624c + 1;
        cVar1 = -(char)DAT_0004624c;
        if (7 < DAT_0004624c) {
          DAT_0004624c = 7;
        }
        DAT_0004624e = 0;
        goto LAB_00019de2;
      }
    }
    else {
      DAT_0004624e = DAT_0004624e + 1;
      cVar1 = (char)DAT_0004624e;
      if (7 < DAT_0004624e) {
        DAT_0004624e = 7;
      }
      DAT_0004624c = 0;
LAB_00019de2:
      DAT_00049cba = cVar1 + DAT_00049cba;
      _DAT_0004624a = 1;
    }
    if ((_DAT_00049ba4 & 0x2200000) != 0x2200000) {
      _DAT_00049cb4 = (&PTR_DAT_00045fd4)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 1;
      return;
    }
    if ((_DAT_00049ba4 & 0x20000000) == 0) {
      return;
    }
    if (DAT_00049d5a == 0) {
      return;
    }
LAB_00019e48:
    ppuVar9 = &PTR_DAT_0004604c + DAT_00049c4c * 5;
LAB_00019e6a:
    _DAT_00049cb4 = ppuVar9[DAT_00049d5a];
    DAT_00049cb8 = 2;
    return;
  case 0xc:
    if ((*(byte *)(DAT_00049cb0 + 2) & 1) != 0) {
      _DAT_00049cb4 = (&PTR_DAT_00045e30)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
      DAT_00049cb8 = 1;
    }
    DAT_00049cc4 = 0;
    DAT_00049cc8 = 0;
    goto switchD_0001929e_caseD_0;
  }
  if ((*(byte *)(DAT_00049cb0 + 2) & 1) != 0) {
LAB_00019e8e:
    _DAT_00049cb4 = (&PTR_DAT_00045e30)[DAT_00049c4c * 5 + (int)DAT_00049d5a];
    DAT_00049cc4 = 0;
    DAT_00049cc8 = 0;
    DAT_00049cb8 = 1;
  }
switchD_0001929e_caseD_0:
  return;
}


/* Address 00019f2c */

undefined4 FUN_00019f2c(ushort param_1,undefined2 param_2,short param_3)

{
  undefined4 uVar1;
  short sVar2;
  
  if ((param_1 & 0xf000) == 0) {
    uVar1 = FUN_0001039c(4,0x9c4c,param_1 & 0xfff);
  }
  else if ((param_1 & 0xf000) == 0x1000) {
    sVar2 = FUN_00010430(4,0x9c4c,param_1 & 0xfff,param_2);
    if (sVar2 == 0) {
      uVar1 = 0;
    }
    else {
      DAT_00049c60 = 0;
      FUN_00020e8c();
      FUN_0000df60();
      FUN_0001aa40(2);
      FUN_00020f78(2);
      uVar1 = 2;
    }
  }
  else if (param_1 == 0xffff) {
    DAT_00049c8c = param_3 + DAT_00049c8c;
    sVar2 = FUN_000102c4(4,0x9c4c);
    if (sVar2 == 0) {
      DAT_00049c8c = DAT_00049c8c - param_3;
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}


/* Address 00019fda */

uint FUN_00019fda(int param_1,short param_2)

{
  short *psVar1;
  short sVar3;
  uint uVar2;
  short in_D1w;
  short *psVar4;
  
  if (param_2 == 1) {
    in_D1w = *(short *)(param_1 + 6) + *(short *)(param_1 + 8) * 2 +
             ((short)(DAT_00049c7c._2_2_ - DAT_00049c50._2_2_) >> 6);
  }
  else if (param_2 < 2) {
    if (param_2 == 0) {
      in_D1w = *(short *)(param_1 + 8) + ((short)(DAT_00049c50._2_2_ - DAT_00049c80._2_2_) >> 6);
    }
  }
  else if (param_2 == 2) {
    in_D1w = ((short)(DAT_00049c84._2_2_ - DAT_00049c56._2_2_) >> 6) +
             *(short *)(param_1 + 6) + *(short *)(param_1 + 8);
  }
  else if (param_2 == 3) {
    in_D1w = (short)(DAT_00049c56._2_2_ - DAT_00049c88._2_2_) >> 6;
  }
  if (*(short *)(param_1 + 0x16) != -1) {
    psVar1 = (short *)(*(int *)(DAT_00049c18 + 8) + *(short *)(param_1 + 0x16) * 6);
    for (psVar4 = psVar1; in_D1w != *psVar4; psVar4 = psVar4 + 3) {
      if (psVar4[1] < 0) {
        return (uint)psVar1 & 0xffff0000;
      }
    }
    if ((psVar4[1] & 0x7000U) != 0) {
      if (psVar4[2] != -1) {
        uVar2 = FUN_00010652(4,0x9c4c,psVar4[2]);
        return uVar2;
      }
      if ((DAT_00049c62 == 0) && (sVar3 = FUN_0001028e(4,0x9c4c), sVar3 != 0)) {
        DAT_00049c60 = 0;
        FUN_00020f0c();
        FUN_0000df60();
        FUN_0001aa40(1);
        FUN_00020f78(1);
        return 2;
      }
    }
  }
  return 0;
}


/* Address 0001a0f8 */

void FUN_0001a0f8(void)

{
  if ((DAT_00049c60 == 2) && (*DAT_00049c78 < 0)) {
    if ((DAT_00049ba5 & 0x10) == 0) {
      if (((DAT_00049ba5 & 0x20) != 0) && ((*(byte *)(DAT_00049c18 + 0xc) & 0x40) != 0)) {
        DAT_00049c60 = 0;
        FUN_00020f0c();
        DAT_00049c62 = DAT_00049c62 + -1;
        DAT_00049c64 = DAT_00049c64 + -1;
        FUN_00020f78(2);
      }
    }
    else if ((*(ushort *)(DAT_00049c18 + 0xc) & 0x8000) != 0) {
      DAT_00049c60 = 0;
      FUN_00020f0c();
      DAT_00049c62 = DAT_00049c62 + 1;
      DAT_00049c64 = DAT_00049c64 + 1;
      FUN_00020f78(2);
      return;
    }
  }
  return;
}


/* Address 0001a188 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x1a544","bytes":"4eb90001a188","assembly":"jsr
   $1a188.l"}] */

void observed_call_candidate_0001a188(void)

{
  short sVar1;
  short sVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  short sVar8;
  int iVar7;
  undefined2 uVar9;
  
  FUN_0000e4c0();
  if ((DAT_00049bac & 0x10000000) != 0) {
    do {
      FUN_0000e4c0();
    } while ((DAT_00049bac & 0x10000000) == 0);
    _DAT_00049ba4 = 0x10000000;
    DAT_00049bac = 0x10000000;
    _DAT_00046252 = DAT_000778cc;
  }
  DAT_0004c24c = DAT_000778cc - _DAT_00046252;
  if (0x1e < DAT_0004c24c) {
    DAT_0004c24c = 0x1e;
  }
  if ((DAT_00049bac & 0xe02fe) != 0) {
    if ((DAT_00049bac & 0x200) == 0) {
      DAT_00049d54 = FUN_0001b718((short)(DAT_00049bac >> 0x10),(short)DAT_00049bac);
      if (DAT_00049d54 == 0) {
        DAT_00049d54 = 10;
      }
      sVar2 = DAT_00049d54 + -1;
    }
    else {
      sVar2 = 0;
      if (DAT_00049d54 != 9) {
        sVar2 = DAT_00049d54 + 1;
      }
    }
    DAT_00049d54 = sVar2;
    DAT_00049d56 = DAT_00049d54;
    FUN_0001b786();
  }
  _DAT_00046252 = DAT_000778cc;
  if (-1 < DAT_00049ba7) {
    FUN_000191f4();
  }
  uVar6 = _DAT_00049c5e;
  uVar5 = _DAT_00049c5c;
  uVar4 = _DAT_00049c5a;
  iVar3 = DAT_00049c56;
  sVar2 = DAT_00049c54;
  iVar7 = DAT_00049c50;
  FUN_0000e220(&DAT_00049ccc,0,0,DAT_00049cba,0,0,(short)((uint)DAT_00049cc4 >> 0x10),
               (short)DAT_00049cc4);
  _DAT_00049c5a = (_DAT_00049c5a & 0x3fff) + (_DAT_00049ce6 & 0x3fff);
  DAT_00049c50 = (int)(short)(_DAT_00049c5a >> 0xe) + (int)DAT_00049cde + DAT_00049c50;
  _DAT_00049c5a = _DAT_00049c5a & 0x3fff;
  _DAT_00049c5c = (_DAT_00049c5c & 0x3fff) + (_DAT_00049ce8 & 0x3fff);
  DAT_00049c54 = DAT_00049ce0 + (_DAT_00049c5c >> 0xe) + DAT_00049c54;
  _DAT_00049c5c = _DAT_00049c5c & 0x3fff;
  _DAT_00049c5e = (_DAT_00049c5e & 0x3fff) + (_DAT_00049cea & 0x3fff);
  DAT_00049c56 = (int)(short)(_DAT_00049c5e >> 0xe) + (int)DAT_00049ce2 + DAT_00049c56;
  _DAT_00049c5e = _DAT_00049c5e & 0x3fff;
  sVar8 = 1;
  if (DAT_00049c60 == 1) {
    if (DAT_00049c56 < _DAT_00049c9c) {
      if (DAT_00049c56 < _DAT_00049ca0) {
        sVar8 = FUN_00019f2c(*(undefined2 *)(_DAT_00049c90 + 4),1,0xfffb);
      }
      else if (DAT_00049c50 < _DAT_00049c94) {
        if (DAT_00049c50 < _DAT_00049c98) {
          sVar8 = FUN_00019f2c(*(undefined2 *)(_DAT_00049c90 + 8),3,0xffff);
        }
      }
      else {
        sVar8 = FUN_00019f2c(*(undefined2 *)(_DAT_00049c90 + 6),2,1);
      }
    }
    else {
      sVar8 = FUN_00019f2c(*(undefined2 *)(_DAT_00049c90 + 2),0,5);
    }
  }
  else if (DAT_00049c60 == 2) {
    if (DAT_00049c56 < DAT_00049c84) {
      if (DAT_00049c56 < DAT_00049c88) {
        uVar9 = 1;
      }
      else if (DAT_00049c50 < DAT_00049c7c) {
        if (DAT_00049c80 <= DAT_00049c50) goto LAB_0001a42a;
        uVar9 = 3;
      }
      else {
        uVar9 = 2;
      }
    }
    else {
      uVar9 = 0;
    }
    sVar8 = FUN_00019fda((short)((uint)DAT_00049c78 >> 0x10),(short)DAT_00049c78,uVar9);
  }
  else {
    sVar8 = 0;
  }
LAB_0001a42a:
  sVar1 = _DAT_00049d16;
  if ((sVar8 != 0) &&
     (iVar7 = DAT_00049c50, sVar2 = DAT_00049c54, iVar3 = DAT_00049c56, uVar4 = _DAT_00049c5a,
     uVar5 = _DAT_00049c5c, uVar6 = _DAT_00049c5e, sVar8 == 1)) {
    _DAT_00049b92 = (_DAT_00049b92 & 0x3fff) + (_DAT_00049ce6 & 0x3fff);
    DAT_00049b8c = DAT_00049cde + (_DAT_00049b92 >> 0xe) + DAT_00049b8c;
    _DAT_00049b92 = _DAT_00049b92 & 0x3fff;
    _DAT_00049b94 = (_DAT_00049b94 & 0x3fff) + (_DAT_00049ce8 & 0x3fff);
    DAT_00049b8e = DAT_00049ce0 + (_DAT_00049b94 >> 0xe) + DAT_00049b8e;
    _DAT_00049b94 = _DAT_00049b94 & 0x3fff;
    _DAT_00049b96 = (_DAT_00049b96 & 0x3fff) + (_DAT_00049cea & 0x3fff);
    DAT_00049b90 = DAT_00049ce2 + (_DAT_00049b96 >> 0xe) + DAT_00049b90;
    _DAT_00049b96 = _DAT_00049b96 & 0x3fff;
  }
  _DAT_00049c5e = uVar6;
  _DAT_00049c5c = uVar5;
  _DAT_00049c5a = uVar4;
  DAT_00049c56 = iVar3;
  DAT_00049c54 = sVar2;
  DAT_00049c50 = iVar7;
  DAT_00049ce2 = 0;
  DAT_00049ce0 = 0;
  DAT_00049cde = 0;
  iVar7 = FUN_0000f0fa();
  if (iVar7 < 0) {
    _DAT_00049d16 = -1;
  }
  else {
    _DAT_00049d16 = 1;
  }
  if (sVar1 != _DAT_00049d16) {
    uRam00049d18 = 1;
  }
  FUN_0000eb04(4,0x9c4c);
  observed_call_candidate_00020820();
  return;
}


/* Address 0001a6f8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0001a6f8(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = _DAT_00113080 * 4;
  uVar3 = *(undefined4 *)(&DAT_00113082 + iVar1);
  iVar2 = FUN_0000e60a(uVar3,PTR_DAT_000462e0);
  uVar3 = FUN_0000e588(uVar3,PTR_DAT_000462e0);
  iVar4 = FUN_0000e540(uVar3,DAT_000462e4);
  iVar4 = iVar2 * 0xbc8f - iVar4;
  *(int *)(&DAT_00113082 + iVar1) = iVar4;
  if (iVar4 < 1) {
    *(int *)(&DAT_00113082 + iVar1) = *(int *)(&DAT_00113082 + iVar1) + 0x7fffffff;
  }
  return *(undefined4 *)(&DAT_00113082 + _DAT_00113080 * 4);
}


/* Address 0001a77c */

undefined4 FUN_0001a77c(short param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = param_1 * 4;
  uVar3 = *(undefined4 *)(&DAT_00113082 + iVar1);
  iVar2 = FUN_0000e60a(uVar3,PTR_DAT_000462e8);
  uVar3 = FUN_0000e588(uVar3,PTR_DAT_000462e8);
  iVar4 = FUN_0000e540(uVar3,DAT_000462ec);
  iVar4 = iVar2 * 0xbc8f - iVar4;
  *(int *)(&DAT_00113082 + iVar1) = iVar4;
  if (iVar4 < 1) {
    *(int *)(&DAT_00113082 + iVar1) = *(int *)(&DAT_00113082 + iVar1) + 0x7fffffff;
  }
  return *(undefined4 *)(&DAT_00113082 + iVar1);
}


/* Address 0001a7f4 */

void FUN_0001a7f4(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  short sVar4;
  
  sVar4 = 1;
  do {
    uVar2 = *(undefined4 *)(&DAT_00113082 + (short)(sVar4 + -1) * 4);
    iVar1 = FUN_0000e60a(uVar2,DAT_000462f0);
    uVar2 = FUN_0000e588(uVar2,DAT_000462f0);
    iVar3 = FUN_0000e540(uVar2,DAT_000462f4);
    iVar3 = iVar1 * 0x598d - iVar3;
    *(int *)(&DAT_00113082 + sVar4 * 4) = iVar3;
    if (iVar3 < 1) {
      *(int *)(&DAT_00113082 + sVar4 * 4) = *(int *)(&DAT_00113082 + sVar4 * 4) + 0x7fffffff;
    }
    sVar4 = sVar4 + 1;
  } while (sVar4 < 0x100);
  return;
}


/* Address 0001a87a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001a87a(undefined2 param_1)

{
  _DAT_00113080 = param_1;
  return;
}


/* Address 0001a8c6 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001a8c6(int param_1)

{
  if (param_1 == 0x7fffffff) {
    param_1 = 0;
  }
  _DAT_00113082 = param_1;
  FUN_0001a7f4();
  return;
}


/* Address 0001a8f8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001a8f8(int param_1)

{
  if (param_1 - 1U < 0x7ffffffe) {
    *(int *)(&DAT_00113082 + _DAT_00113080 * 4) = param_1;
  }
  return;
}


/* Address 0001a920 */

void FUN_0001a920(void)

{
  int iVar1;
  short sVar3;
  int iVar2;
  int iVar4;
  short *psVar5;
  undefined2 *puVar6;
  
LAB_0001a92a:
  do {
    iVar4 = 0;
    psVar5 = &DAT_00049d6c;
    do {
      if (*psVar5 == 0xf) {
        iVar1 = iVar4 * 0xce;
        puVar6 = &DAT_00049d6c + iVar4 * 0x67;
        sVar3 = FUN_000101e0(puVar6,0x1b,2,0xd000,4,0x6300);
        if (sVar3 != 0) {
          (&DAT_00049dd8)[iVar4 * 0x67] = 1;
          (&DAT_00049e34)[iVar4 * 0x67] = 2;
          while ((&DAT_00049d6e)[iVar4 * 0x67] == 0) {
            *(undefined4 *)((int)&DAT_00049de4 + iVar1) = 0;
            if (((short)(&DAT_00049e34)[iVar4 * 0x67] < 1) && ((&DAT_00049dd8)[iVar4 * 0x67] != 0))
            {
              (&DAT_00049dd8)[iVar4 * 0x67] = 0;
              *(undefined **)((int)&DAT_00049dd4 + iVar1) = &DAT_000463cc;
              *(undefined4 *)((int)&DAT_00049de4 + iVar1) = 0;
              *(undefined4 *)((int)&DAT_00049de8 + iVar1) = 0;
            }
            iVar2 = FUN_00010252(puVar6);
            sVar3 = (&DAT_00049dd8)[iVar4 * 0x67];
            if (sVar3 == 1) {
              if (iVar2 < 0x100) {
                FUN_0001c9e8(2);
                (&DAT_00049dd8)[iVar4 * 0x67] = 2;
              }
            }
            else if (((1 < sVar3) && (sVar3 == 2)) && (0x1000 < iVar2)) {
              (&DAT_00049dd8)[iVar4 * 0x67] = 1;
            }
            FUN_0000eb04(puVar6);
            FUN_00013c9a(puVar6,4,0x2118);
            FUN_0000df60();
          }
          *puVar6 = 0;
          FUN_0001545c((short)((uint)*(undefined4 *)((int)&DAT_00049dca + iVar1) >> 0x10),
                       (short)*(undefined4 *)((int)&DAT_00049dca + iVar1));
          FUN_0001b002(0x1b);
        }
        goto LAB_0001a92a;
      }
      psVar5 = psVar5 + 0x67;
      iVar4 = iVar4 + 1;
    } while (iVar4 < 0x28);
    FUN_0000df60();
  } while( true );
}


/* Address 0001aa40 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001aa40(short param_1)

{
  int iVar1;
  short sVar2;
  undefined4 local_8;
  
  _DAT_0015b532 = 0;
  sVar2 = 0;
  do {
    iVar1 = (int)sVar2;
    (&DAT_0004674c)[iVar1 * 2] = iVar1 * 0x2000 + 0x1134a0;
    (&DAT_00046750)[iVar1 * 2] = s_Laying_claim_to_the__discovery__o_00032e28 + 0x1f8;
    *(undefined2 *)(&DAT_0015b4a0 + iVar1 * 4) = 0xffff;
    *(undefined2 *)(&DAT_0015b4a2 + iVar1 * 4) = 0;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x24);
  _DAT_0015b530 = param_1;
  if (param_1 == 1) {
    local_8 = DAT_0004674c;
    FUN_0001b044(0xe3adc0,0x52545854,&local_8,0x1e000,0);
    _DAT_0015b532 = 0xf;
  }
  return;
}


/* Address 0001aade */

int * FUN_0001aade(void)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  short sVar4;
  
  piVar3 = (int *)FUN_000152a2(0x90);
  iVar1 = *piVar3;
  sVar4 = 0;
  do {
    iVar2 = sVar4 * 4;
    if (*(short *)(&DAT_0015b4a2 + iVar2) < 1) {
      *(undefined2 *)(iVar1 + iVar2) = 0xffff;
      *(undefined2 *)(iVar1 + 2 + iVar2) = 0;
    }
    else {
      *(undefined2 *)(iVar1 + iVar2) = *(undefined2 *)(&DAT_0015b4a0 + iVar2);
      *(undefined2 *)(iVar1 + 2 + iVar2) = *(undefined2 *)(&DAT_0015b4a2 + iVar2);
    }
    sVar4 = sVar4 + 1;
  } while (sVar4 < 0x24);
  return piVar3;
}


/* Address 0001ab2a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001ab2a(int *param_1)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  undefined4 local_8;
  
  iVar1 = *param_1;
  sVar4 = 0;
  do {
    iVar2 = sVar4 * 4;
    *(undefined2 *)(&DAT_0015b4a0 + iVar2) = *(undefined2 *)(iVar1 + iVar2);
    *(undefined2 *)(&DAT_0015b4a2 + iVar2) = *(undefined2 *)(iVar1 + 2 + iVar2);
    sVar4 = sVar4 + 1;
  } while (sVar4 < 0x24);
  if ((_DAT_0015b530 < 4) && (0 < _DAT_0015b530)) {
    sVar4 = *(short *)(&DAT_000464a0 + _DAT_0015b530 * 2);
    if (_DAT_0015b532 < (short)(0x24 - sVar4)) {
      sVar5 = _DAT_0015b532;
      do {
        iVar1 = sVar5 * 4;
        if (*(short *)(&DAT_0015b4a0 + iVar1) != -1) {
          iVar2 = _DAT_0015b530 * 4;
          sVar3 = (short)(*(short *)(&DAT_0015b4a0 + iVar1) -
                         *(short *)(&DAT_000464c8 + _DAT_0015b530 * 2)) / sVar4;
          local_8 = (&DAT_0004674c)[sVar5 * 2];
          FUN_0001b044(*(int *)(&DAT_000464a8 + iVar2) +
                       (short)(*(short *)(&DAT_0015b4a0 + iVar1) -
                              *(short *)(&DAT_000464c8 + _DAT_0015b530 * 2)) * 0x2000 +
                       (int)(short)(sVar3 << 6),*(int *)(&DAT_000464b8 + iVar2) + (int)sVar3,
                       &local_8,(int)sVar4 << 0xd,0);
        }
        sVar5 = sVar4 + sVar5;
      } while (sVar5 < (short)(0x24 - sVar4));
    }
    FUN_0001545c(param_1);
  }
  return;
}


/* Address 0001ac3c */

int FUN_0001ac3c(short param_1)

{
  ushort uVar1;
  short sVar2;
  
  sVar2 = 0;
  do {
    uVar1 = (ushort)((uint)(sVar2 * 4) >> 0x10);
    if (param_1 == *(short *)(&DAT_0015b4a0 + sVar2 * 4)) {
      return CONCAT22(uVar1,sVar2);
    }
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x24);
  return (uint)uVar1 << 0x10;
}


/* Address 0001ac68 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

short FUN_0001ac68(short param_1)

{
  int iVar1;
  short sVar2;
  int iVar3;
  short sVar4;
  short sVar5;
  undefined4 local_8;
  
  if ((_DAT_0015b530 < 4) && (0 < _DAT_0015b530)) {
    iVar3 = _DAT_0015b530 * 2;
    sVar4 = param_1 - *(short *)(&DAT_000464c8 + iVar3);
    sVar2 = *(short *)(&DAT_000464a0 + iVar3);
    iVar3 = _DAT_0015b530 * 4;
    if (-1 < sVar4) {
      for (sVar5 = _DAT_0015b532; sVar5 < (short)(0x24 - sVar2); sVar5 = sVar2 + sVar5) {
        if (param_1 == *(short *)(&DAT_0015b4a0 + sVar5 * 4)) {
          sVar4 = 0;
          if (sVar2 < 1) {
            return sVar5;
          }
          do {
            *(short *)(&DAT_0015b4a2 + (short)(sVar4 + sVar5) * 4) =
                 *(short *)(&DAT_0015b4a2 + (short)(sVar4 + sVar5) * 4) + 1;
            sVar4 = sVar4 + 1;
          } while (sVar4 < sVar2);
          return sVar5;
        }
      }
      iVar1 = *(int *)(&DAT_000464b8 + iVar3) + (int)(sVar4 / sVar2);
      if (_DAT_0015b532 < (short)(0x24 - sVar2)) {
        sVar5 = _DAT_0015b532;
        do {
          if (*(short *)(&DAT_0015b4a0 + sVar5 * 4) == -1) {
            local_8 = (&DAT_0004674c)[sVar5 * 2];
            FUN_0001b044(sVar4 * 0x2000 + (int)(short)(sVar4 / sVar2 << 6) +
                         *(int *)(&DAT_000464a8 + iVar3),iVar1,&local_8,(int)sVar2 << 0xd,0);
            sVar4 = 0;
            if (sVar2 < 1) {
              return sVar5;
            }
            do {
              iVar3 = (short)(sVar4 + sVar5) * 4;
              *(short *)(&DAT_0015b4a0 + iVar3) = sVar4 + param_1;
              *(undefined2 *)(&DAT_0015b4a2 + iVar3) = 1;
              sVar4 = sVar4 + 1;
            } while (sVar4 < sVar2);
            return sVar5;
          }
          sVar5 = sVar2 + sVar5;
        } while (sVar5 < (short)(0x24 - sVar2));
      }
      if (_DAT_0015b532 < (short)(0x24 - sVar2)) {
        sVar5 = _DAT_0015b532;
        do {
          if (*(short *)(&DAT_0015b4a2 + sVar5 * 4) == 0) {
            local_8 = (&DAT_0004674c)[sVar5 * 2];
            FUN_0001b044(sVar4 * 0x2000 + (int)(short)(sVar4 / sVar2 << 6) +
                         *(int *)(&DAT_000464a8 + iVar3),iVar1,&local_8,(int)sVar2 << 0xd,0);
            sVar4 = 0;
            if (sVar2 < 1) {
              return sVar5;
            }
            do {
              iVar3 = (short)(sVar4 + sVar5) * 4;
              *(short *)(&DAT_0015b4a0 + iVar3) = sVar4 + param_1;
              *(undefined2 *)(&DAT_0015b4a2 + iVar3) = 1;
              sVar4 = sVar4 + 1;
            } while (sVar4 < sVar2);
            return sVar5;
          }
          sVar5 = sVar2 + sVar5;
        } while (sVar5 < (short)(0x24 - sVar2));
      }
    }
  }
  return -1;
}


/* Address 0001ae56 */

void FUN_0001ae56(short param_1)

{
  int iVar1;
  short sVar2;
  
  sVar2 = 0;
  do {
    iVar1 = sVar2 * 4;
    if (param_1 == *(short *)(&DAT_0015b4a0 + iVar1)) {
      if (*(short *)(&DAT_0015b4a2 + iVar1) == 0) {
        return;
      }
      *(short *)(&DAT_0015b4a2 + iVar1) = *(short *)(&DAT_0015b4a2 + iVar1) + -1;
      return;
    }
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x24);
  return;
}


/* Address 0001ae88 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001ae88(short param_1)

{
  int iVar1;
  short sVar2;
  short sVar3;
  
  if (-1 < param_1) {
    sVar3 = *(short *)(&DAT_000464a0 + _DAT_0015b530 * 2);
    sVar2 = 0;
    do {
      if (sVar3 < 1) {
        return;
      }
      iVar1 = sVar2 * 4;
      if (param_1 == *(short *)(&DAT_0015b4a0 + iVar1)) {
        if (0 < *(short *)(&DAT_0015b4a2 + iVar1)) {
          *(short *)(&DAT_0015b4a2 + iVar1) = *(short *)(&DAT_0015b4a2 + iVar1) + -1;
        }
        sVar3 = sVar3 + -1;
        param_1 = param_1 + 1;
      }
      sVar2 = sVar2 + 1;
    } while (sVar2 < 0x24);
  }
  return;
}


/* Address 0001aeda */

void FUN_0001aeda(void)

{
  int iVar1;
  short sVar2;
  
  sVar2 = 0;
  do {
    iVar1 = sVar2 * 0xc;
    *(undefined2 *)(&DAT_0015b534 + iVar1) = 0xffff;
    *(undefined2 *)(&DAT_0015b53a + iVar1) = 0;
    *(undefined2 *)(&DAT_0015b53e + iVar1) = 0;
    *(undefined2 *)(&DAT_0015b53c + iVar1) = 0;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x32);
  return;
}


/* Address 0001af04 */

undefined4 FUN_0001af04(short param_1)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  if (*(int *)(&DAT_000464d0 + param_1 * 0xc) != 0) {
    sVar5 = 0;
    do {
      iVar2 = sVar5 * 0xc;
      if ((param_1 == *(short *)(&DAT_0015b534 + iVar2)) && (*(short *)(&DAT_0015b53a + iVar2) != 0)
         ) {
        *(short *)(&DAT_0015b53a + iVar2) = *(short *)(&DAT_0015b53a + iVar2) + 1;
        sVar1 = *(short *)(&DAT_0015b53c + iVar2);
        while (sVar1 == 0) {
          FUN_0000df8c(1);
          sVar1 = *(short *)(&DAT_0015b53c + iVar2);
        }
        return *(undefined4 *)(&DAT_0015b536 + sVar5 * 0xc);
      }
      sVar5 = sVar5 + 1;
    } while (sVar5 < 0x32);
    sVar5 = 0;
    iVar2 = (int)param_1;
    do {
      iVar4 = sVar5 * 0xc;
      if (*(short *)(&DAT_0015b53a + iVar4) == 0) {
        iVar3 = FUN_000152a2((&PTR_LAB_000464d8)[iVar2 * 3]);
        *(int *)(&DAT_0015b536 + iVar4) = iVar3;
        if (iVar3 == 0) {
          return 0;
        }
        *(undefined2 *)(&DAT_0015b53c + iVar4) = 0;
        *(short *)(&DAT_0015b534 + iVar4) = param_1;
        *(undefined2 *)(&DAT_0015b53a + iVar4) = 1;
        FUN_0001b044(*(undefined4 *)(&DAT_000464d0 + iVar2 * 0xc),
                     *(undefined4 *)(&DAT_000464d4 + iVar2 * 0xc),
                     *(undefined4 *)(&DAT_0015b536 + iVar4),(&PTR_LAB_000464d8)[iVar2 * 3],
                     &DAT_0015b53c + iVar4);
        if (*(short *)(&DAT_0015b53a + iVar4) != 1) {
          FUN_0000df9c(1);
        }
        return *(undefined4 *)(&DAT_0015b536 + iVar4);
      }
      sVar5 = sVar5 + 1;
    } while (sVar5 < 0x32);
  }
  return 0;
}


/* Address 0001b002 */

void FUN_0001b002(short param_1)

{
  short sVar1;
  int iVar2;
  short sVar3;
  
  sVar3 = 0;
  do {
    iVar2 = sVar3 * 0xc;
    if ((param_1 == *(short *)(&DAT_0015b534 + iVar2)) &&
       (sVar1 = *(short *)(&DAT_0015b53a + iVar2) + -1, *(short *)(&DAT_0015b53a + iVar2) = sVar1,
       sVar1 == 0)) {
      *(undefined2 *)(&DAT_0015b534 + iVar2) = 0xffff;
      FUN_0001545c(*(undefined4 *)(&DAT_0015b536 + iVar2));
    }
    sVar3 = sVar3 + 1;
  } while (sVar3 < 0x32);
  return;
}


/* Address 0001b044 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int * FUN_0001b044(uint param_1,int param_2,undefined4 *param_3,int param_4,undefined2 *param_5)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  while (_DAT_00047b82 != 0) {
    FUN_0000df60();
  }
  while (_DAT_00047b80 != 0) {
    FUN_0000df60();
  }
  _DAT_00047b80 = 1;
LAB_0001b08a:
  _DAT_001126a0 = 0;
  uVar1 = analyst_cd_offset_msf(2,param_1);
  FUN_0000d2f0(0x1c0000,param_4 + 0x1c8000,uVar1);
  _DAT_001126a0 = 0;
  DAT_000bd848 = 0;
  if (param_4 + 0x1c8000 != 0) {
    do {
      FUN_0000df60();
    } while (DAT_000bd848 < param_4 + 0x1c8000U);
  }
  piVar3 = (int *)&DAT_001c0000;
  thunk_EXT_FUN_00003042();
  do {
    iVar2 = *piVar3;
    while (piVar3 = piVar3 + 1, param_2 != iVar2) {
      if (0x1c7fff < (int)piVar3) {
        DAT_000bd848 = 0;
        goto LAB_0001b08a;
      }
      iVar2 = *piVar3;
    }
    iVar2 = 1;
    piVar4 = piVar3;
    while (piVar3 = piVar4 + 1, param_2 == *piVar4) {
      iVar2 = iVar2 + 1;
      piVar4 = piVar3;
      if (0xf < iVar2) {
        if ((int)piVar3 < 0x1c8001) {
          if (param_3 != (undefined4 *)0x0) {
            FUN_0000e3e0(piVar3,*param_3,param_4);
            _DAT_00047b80 = 0;
            if (param_5 != (undefined2 *)0x0) {
              *param_5 = 1;
            }
            piVar3 = (int *)0x0;
          }
          return piVar3;
        }
        goto LAB_0001b08a;
      }
    }
  } while( true );
}


/* Address 0001b160 */

short FUN_0001b160(undefined1 *param_1,undefined1 param_2,short *param_3,short param_4)

{
  short sVar1;
  short sVar2;
  
  sVar2 = 1;
  if (*param_3 < 1) {
    sVar2 = 0;
  }
  else {
    *param_1 = param_2;
    sVar1 = *param_3 + -1;
    *param_3 = sVar1;
    while (0 < sVar1) {
      param_1 = param_1 + 1;
      param_4 = param_4 + -1;
      if (param_4 < 1) {
        return sVar2;
      }
      *param_1 = 0x20;
      sVar1 = *param_3 + -1;
      *param_3 = sVar1;
      sVar2 = sVar2 + 1;
    }
  }
  return sVar2;
}


/* Address 0001b1a8 */

short FUN_0001b1a8(char *param_1,char *param_2,short *param_3,short param_4)

{
  short sVar1;
  short sVar2;
  
  sVar2 = 0;
  if (param_2 == (char *)0x0) {
    param_2 = &DAT_0001b1a0;
  }
  sVar1 = *param_3;
  for (; (0 < sVar1 && (*param_2 != '\0')); param_2 = param_2 + 1) {
    *param_1 = *param_2;
    sVar2 = sVar2 + 1;
    sVar1 = *param_3 + -1;
    *param_3 = sVar1;
    param_4 = param_4 + -1;
    param_1 = param_1 + 1;
  }
  while ((0 < param_4 && (0 < *param_3))) {
    *param_1 = ' ';
    sVar2 = sVar2 + 1;
    *param_3 = *param_3 + -1;
    param_4 = param_4 + -1;
    param_1 = param_1 + 1;
  }
  return sVar2;
}


/* Address 0001b212 */

short FUN_0001b212(char *param_1,int param_2,short param_3,short *param_4,short param_5,char param_6
                  )

{
  short sVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  char *pcVar5;
  char *pcVar6;
  
  sVar4 = 0;
  pcVar5 = &DAT_0015b7a0;
  do {
    sVar3 = param_5;
    iVar2 = FUN_0000e67c(param_2,(int)param_3);
    pcVar6 = pcVar5 + 1;
    *pcVar5 = s_0123456789ABCDEF_0001b200[iVar2];
    param_2 = FUN_0000e61c(param_2,(int)param_3);
    param_5 = sVar3 + -1;
    pcVar5 = pcVar6;
  } while (param_2 != 0);
  sVar3 = sVar3 + -2;
  while( true ) {
    sVar1 = sVar3;
    if (param_5 < 1) {
      sVar3 = *param_4;
      while ((0 < sVar3 && (pcVar6 != &DAT_0015b7a0))) {
        pcVar6 = pcVar6 + -1;
        *param_1 = *pcVar6;
        sVar4 = sVar4 + 1;
        sVar3 = *param_4 + -1;
        *param_4 = sVar3;
        param_1 = param_1 + 1;
      }
      return sVar4;
    }
    if (*param_4 < 1) break;
    *param_1 = param_6;
    sVar4 = sVar4 + 1;
    *param_4 = *param_4 + -1;
    sVar3 = sVar1 + -1;
    param_1 = param_1 + 1;
    param_5 = sVar1;
  }
  return sVar4;
}


/* Address 0001b29c */

short FUN_0001b29c(undefined1 *param_1,char *param_2,uint *param_3)

{
  bool bVar1;
  short sVar2;
  ushort uVar3;
  char cVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined1 *puVar7;
  uint *puVar8;
  char *pcVar9;
  char *pcVar10;
  undefined2 uVar11;
  short sVar12;
  undefined2 local_6;
  
  local_6 = 0xfe;
  cVar4 = *param_2;
  puVar7 = param_1;
  while (sVar2 = (short)puVar7, cVar4 != '\0') {
    pcVar9 = param_2 + 1;
    uVar11 = (undefined2)((uint)puVar7 >> 0x10);
    puVar8 = param_3;
    if (cVar4 != '%') {
      sVar12 = 1;
      uVar3 = (ushort)cVar4;
      goto LAB_0001b37e;
    }
    cVar4 = *pcVar9;
    sVar12 = 0;
    bVar1 = false;
    uVar6 = 0x20;
    pcVar10 = param_2 + 2;
    if (cVar4 == '0') {
      uVar6 = 0x30;
    }
    while ((cVar4 != '\0' && ((byte)(cVar4 - 0x30U) < 10))) {
      sVar12 = (short)cVar4 + sVar12 * 10 + -0x30;
      cVar4 = *pcVar10;
      pcVar10 = pcVar10 + 1;
    }
    if ((cVar4 == 'l') || (pcVar9 = pcVar10, cVar4 == 'L')) {
      bVar1 = true;
      pcVar9 = pcVar10 + 1;
      cVar4 = *pcVar10;
    }
    if (cVar4 == '\0') break;
    if (cVar4 == 'o') {
      if (bVar1) {
        puVar8 = param_3 + 1;
        uVar5 = *param_3;
      }
      else {
        puVar8 = (uint *)((int)param_3 + 2);
        uVar5 = (uint)*(ushort *)param_3;
      }
      uVar11 = 8;
LAB_0001b432:
      sVar2 = FUN_0001b212((short)((uint)puVar7 >> 0x10),(short)puVar7,(short)(uVar5 >> 0x10),
                           (short)uVar5,uVar11,&local_6,sVar12,uVar6);
      puVar7 = puVar7 + sVar2;
      param_3 = puVar8;
    }
    else {
      if ('o' < cVar4) {
        if (cVar4 != 'u') {
          if (cVar4 < 'v') {
            if (cVar4 == 's') {
              sVar2 = FUN_0001b1a8(uVar11,sVar2,(short)(*param_3 >> 0x10),(short)*param_3,&local_6,
                                   sVar12);
              puVar7 = puVar7 + sVar2;
              param_3 = param_3 + 1;
            }
          }
          else if (cVar4 == 'x') {
            if (bVar1) {
              puVar8 = param_3 + 1;
              uVar5 = *param_3;
            }
            else {
              puVar8 = (uint *)((int)param_3 + 2);
              uVar5 = (uint)*(ushort *)param_3;
            }
            uVar11 = 0x10;
            goto LAB_0001b432;
          }
          goto LAB_0001b444;
        }
        if (bVar1) {
          puVar8 = param_3 + 1;
          uVar5 = *param_3;
        }
        else {
          puVar8 = (uint *)((int)param_3 + 2);
          uVar5 = (uint)*(ushort *)param_3;
        }
LAB_0001b424:
        uVar11 = 10;
        goto LAB_0001b432;
      }
      if (cVar4 == 'c') {
        puVar8 = (uint *)((int)param_3 + 2);
        uVar3 = *(ushort *)param_3;
LAB_0001b37e:
        sVar2 = FUN_0001b160(uVar11,sVar2,uVar3,&local_6,sVar12);
        puVar7 = puVar7 + sVar2;
        param_3 = puVar8;
      }
      else if (cVar4 < 'd') {
        if (cVar4 == '%') {
          uVar3 = 0x25;
          goto LAB_0001b37e;
        }
      }
      else if (cVar4 == 'd') {
        if (bVar1) {
          puVar8 = param_3 + 1;
          uVar5 = *param_3;
        }
        else {
          puVar8 = (uint *)((int)param_3 + 2);
          uVar5 = (uint)(short)*(ushort *)param_3;
        }
        if ((int)uVar5 < 0) {
          sVar2 = FUN_0001b160(uVar11,sVar2,0x2d,&local_6,1);
          puVar7 = puVar7 + sVar2;
          sVar12 = sVar12 + -1;
          uVar5 = -uVar5;
        }
        goto LAB_0001b424;
      }
    }
LAB_0001b444:
    param_2 = pcVar9;
    cVar4 = *pcVar9;
  }
  *puVar7 = 0;
  return sVar2 - (short)param_1;
}


/* Address 0001b45a */

void FUN_0001b45a(undefined4 param_1,undefined4 param_2)

{
  FUN_0001b29c(param_1,param_2,&stack0x0000000c);
  return;
}


/* Address 0001b718 */

uint FUN_0001b718(uint param_1)

{
  uint in_D0;
  uint uVar1;
  
  if ((param_1 & 0x80000) != 0) {
    return 1;
  }
  if ((param_1 & 0x40000) != 0) {
    return 4;
  }
  if ((param_1 & 0x20000) != 0) {
    return 7;
  }
  if ((char)param_1 < '\0') {
    return 2;
  }
  if ((param_1 & 0x40) != 0) {
    return 5;
  }
  if ((param_1 & 0x20) != 0) {
    return 8;
  }
  if ((param_1 & 0x10) != 0) {
    return in_D0 & 0xffff0000;
  }
  if ((param_1 & 8) != 0) {
    return 3;
  }
  if ((param_1 & 4) != 0) {
    return 6;
  }
  uVar1 = 9;
  if ((param_1 & 2) == 0) {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}


/* Address 0001b786 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001b786(void)

{
  int iVar1;
  undefined *puVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  byte *pbVar6;
  undefined1 auStack_18 [24];
  
  _DAT_00f02200 = &DAT_000b5130;
  _DAT_00f02204 = s_Ultimately__everyone_at_Kelpin_c_00033200 + 0x220;
  _DAT_00f0220c = (undefined *)0x0;
  _DAT_00f02210 = 0;
  _DAT_00f02214 = 0;
  _DAT_00f02218 = 0;
  _DAT_00f02220 = 0;
  _DAT_00f0221c = 1;
  _DAT_00f02224 = &DAT_00069a60;
  _DAT_00f02228 = &LAB_00013420;
  _DAT_00f02230 = 0;
  _DAT_00f02234 = 0;
  _DAT_00f0223c = (undefined *)0x10780;
  _DAT_00f02238 = 0x1800601;
  FUN_0001b45a(auStack_18,&DAT_0001b780,DAT_00049d1e);
  FUN_000149ae(0x14,5,auStack_18,&DAT_000b5130,0x3420,&DAT_0004c3e0,0x7fc0,1);
  sVar5 = 0;
  sVar4 = 0x780;
  do {
    _DAT_00f02200 = &DAT_000b5130 + sVar4 * 2;
    _DAT_00f02204 = s_Ultimately__everyone_at_Kelpin_c_00033200 + 0x220;
    _DAT_00f0220c = (undefined *)0x0;
    if ((short)(DAT_00049d54 + sVar5) % 10 == DAT_00049d56) {
      _DAT_00f02224 = &DAT_00068260;
    }
    else {
      _DAT_00f02224 = &DAT_00066a60;
    }
    _DAT_00f02228 = &LAB_00013420;
    _DAT_00f02230 = 0;
    _DAT_00f02234 = 0;
    _DAT_00f0223c = (undefined *)0x10c00;
    _DAT_00f02238 = 0x9800609;
    _DAT_00f02268 = 0;
    _DAT_00f0226c = 0;
    sVar3 = (short)(DAT_00049d54 + sVar5) % 10;
    iVar1 = *(int *)(&DAT_0006e6ac + (short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[sVar3]] * 4
                    );
    pbVar6 = &DAT_0006e6a0 + iVar1;
    if ((&DAT_00049d2c)[sVar3] != 0) {
      FUN_0000e2b8(&DAT_0006e6a0,(int)(short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[sVar3]],
                   0x10a688);
      puVar2 = &DAT_000b5130 + sVar4 * 2;
      _DAT_00f02204 = s_Ultimately__everyone_at_Kelpin_c_00033200 + 0x220;
      _DAT_00f0220c =
           (undefined *)
           ((int)(short)(0x5e - (ushort)*pbVar6) |
           (uint)(ushort)(0x10 - ((byte)(&DAT_0006e6a1)[iVar1] >> 1)) << 0x10);
      _DAT_00f02210 = (int)(short)(0x60 - (ushort)*pbVar6);
      _DAT_00f02224 = (undefined *)0x10a688;
      _DAT_00f02228 =
           (undefined1 *)
           ((uint)(&PTR_s_hat_red_tape_encrusted_wad_of_bu_00030648_0x1d8_0003bd20)[*pbVar6] ^
           0x20000);
      _DAT_00f02230 = 0;
      _DAT_00f0223c = (undefined *)((uint)*pbVar6 | (uint)(byte)(&DAT_0006e6a1)[iVar1] << 0x10);
      _DAT_00f02238 = 0x9800609;
      _DAT_00f02200 = puVar2;
      FUN_000149ae(0x10,1,*(undefined4 *)
                           ((int)&PTR_s_My_First_00046a6a +
                           (short)(char)(&DAT_00042000)
                                        [(short)(&DAT_00049d2c)[(short)(DAT_00049d54 + sVar5) % 10]]
                           * 0x16),puVar2,0x3420,&DAT_0004cca0,2,0);
      FUN_000149ae(0x10,0xb,*(undefined4 *)
                             ((int)&PTR_DAT_00046a6e +
                             (short)(char)(&DAT_00042000)
                                          [(short)(&DAT_00049d2c)
                                                  [(short)(DAT_00049d54 + sVar5) % 10]] * 0x16),
                   puVar2,0x3420,&DAT_0004cca0,2,0);
      FUN_000149ae(0x10,0x15,
                   *(undefined4 *)
                    ((int)&PTR_DAT_00046a72 +
                    (short)(char)(&DAT_00042000)
                                 [(short)(&DAT_00049d2c)[(short)(DAT_00049d54 + sVar5) % 10]] * 0x16
                    ),puVar2,0x3420,&DAT_0004cca0,2,0);
    }
    _DAT_00f02200 = &DAT_000b5130 + sVar4 * 2;
    _DAT_00f02204 = s_Ultimately__everyone_at_Kelpin_c_00033200 + 0x220;
    _DAT_00f0220c = &DAT_000a0003;
    _DAT_00f02210 = 0x54;
    _DAT_00f02224 = (&PTR_DAT_000468a0)[(short)(DAT_00049d54 + sVar5) % 10];
    _DAT_00f02228 = (undefined1 *)0x11c20;
    _DAT_00f02230 = 0;
    _DAT_00f02234 = 0;
    _DAT_00f02268 = 0;
    _DAT_00f0226c = 0;
    _DAT_00f0223c = &DAT_000b000c;
    _DAT_00f02238 = 0x9800609;
    sVar4 = sVar4 + 0xc00;
    sVar5 = sVar5 + 1;
  } while (sVar5 < 5);
  return;
}


/* Address 0001bc78 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0001bc78(undefined2 param_1,int *param_2)

{
  int iVar1;
  short sVar2;
  undefined4 uVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  byte *pbVar7;
  
  sVar5 = 1;
  sVar4 = 0;
  iVar1 = *param_2;
  sVar2 = *(short *)(iVar1 + 2) + -1;
  while( true ) {
    if (sVar4 != sVar5) {
      pbVar7 = (byte *)(*(int *)(iVar1 + 0xc + sVar5 * 4) + *param_2);
      FUN_0000e2b8(*param_2,0,DAT_000bd830);
      FUN_0000e2b8(*param_2,(int)sVar5,DAT_000bd834);
      _DAT_00f02200 = DAT_000bd830;
      _DAT_00f02204 = s_TO__Paul_Krantz__Recruitment_Ope_00033c1c + 0x204;
      _DAT_00f0220c = (uint)(ushort)(0x5a - (pbVar7[1] >> 1)) << 0x10 | 0x14;
      _DAT_00f02210 = (int)(short)(0xe0 - (ushort)*pbVar7);
      _DAT_00f02214 = 0;
      _DAT_00f02218 = 0;
      _DAT_00f02220 = 0;
      _DAT_00f0221c = 1;
      _DAT_00f02224 = DAT_000bd834;
      _DAT_00f02228 =
           (uint)(&PTR_s_hat_red_tape_encrusted_wad_of_bu_00030648_0x1d8_0003bd20)[*pbVar7] ^
           0x20000;
      _DAT_00f02230 = 0;
      _DAT_00f02234 = 0;
      _DAT_00f0223c = (uint)*pbVar7 | (uint)pbVar7[1] << 0x10;
      _DAT_00f02268 = 0;
      _DAT_00f02238 = 0x9800609;
      sVar4 = sVar5;
    }
    FUN_0000e4c0();
    if ((DAT_00049bac & 0x20202000) != 0) break;
    sVar6 = sVar5;
    if (((DAT_00049bac & 0x400000) != 0) && (sVar6 = sVar2, 1 < sVar5)) {
      sVar6 = sVar5 + -1;
    }
    sVar5 = sVar6;
    if (DAT_00049bac._1_1_ < '\0') {
      if (sVar6 < sVar2) {
        sVar5 = sVar6 + 1;
      }
      else {
        sVar5 = 1;
      }
    }
    if ((DAT_00049bac & 0xe02fe) != 0) {
      if ((DAT_00049bac & 0x200) == 0) {
        DAT_00049d54 = FUN_0001b718(DAT_00049bac);
        if (DAT_00049d54 == 0) {
          DAT_00049d54 = 10;
        }
        sVar6 = DAT_00049d54 + -1;
      }
      else {
        sVar6 = 0;
        if (DAT_00049d54 != 9) {
          sVar6 = DAT_00049d54 + 1;
        }
      }
      DAT_00049d54 = sVar6;
      DAT_00049d56 = DAT_00049d54;
      FUN_0001b786();
    }
  }
  uVar3 = CONCAT22((short)((DAT_00049bac & 0x20202000) >> 0x10),sVar5);
  if ((DAT_00049bac & 0x20000000) == 0) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}


/* Address 0001be60 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001be60(short param_1,undefined4 param_2)

{
  int iVar1;
  short sVar2;
  short sVar3;
  ushort uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  
  _DAT_00047b84 = 0x22002000;
  FUN_00018160();
  _DAT_00049c48 = &DAT_0005e360;
  DAT_00043df2 = &DAT_0005e360;
  FUN_000185b2(4,0x3da0,7,0x77c0);
  iVar1 = param_1 * 0xcc;
  FUN_0000d3fc(*(undefined4 *)(&DAT_000468c8 + iVar1),*(undefined4 *)(&DAT_000468cc + iVar1),
               DAT_000bd830,*(undefined4 *)(&DAT_000468d0 + iVar1),0,0xe0,0,0);
  do {
    _DAT_00049c48 = &DAT_0005e360;
    DAT_00043df2 = &DAT_0005e360;
    FUN_000185b2(4,0x3da0,7,0x77c0);
    if ((_DAT_00049ba4 & 0x22002000) == 0) {
      _DAT_00049ba4 = 0;
      iVar1 = param_1 * 0xcc;
      FUN_0000d3fc(*(undefined4 *)(&DAT_000468d4 + iVar1),*(undefined4 *)(&DAT_000468d8 + iVar1),
                   (short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,
                   (short)((uint)*(undefined4 *)(&DAT_000468dc + iVar1) >> 0x10),
                   (short)*(undefined4 *)(&DAT_000468dc + iVar1),0,0xe0,0,0xf);
    }
    if ((_DAT_00049ba4 & 0x20000000) == 0) {
      if ((_DAT_00049ba4 & 0x2000000) != 0) goto LAB_0001c4b0;
      _DAT_00049c48 = &DAT_000b5130;
      DAT_00043df2 = &DAT_000b5130;
      FUN_000185b2(4,0x3da0,7,0x77c0);
      _DAT_00047b84 = 0x3e02fe;
      iVar1 = param_1 * 0xcc;
      FUN_0000d3fc(*(undefined4 *)(&DAT_00046934 + iVar1),*(undefined4 *)(&DAT_00046938 + iVar1),
                   DAT_000bd830,*(undefined4 *)(&DAT_0004693c + iVar1),0,0xe0,0,0);
LAB_0001c15c:
      while (_DAT_00047b84 = 0x3e02fe, (_DAT_00049ba4 & 0xe00fe) == 0) {
        iVar1 = param_1 * 0xcc;
        FUN_0000d3fc(*(undefined4 *)(&DAT_00046940 + iVar1),*(undefined4 *)(&DAT_00046944 + iVar1),
                     (short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046948 + iVar1) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046948 + iVar1),0,0xe0,0,0xf);
        if ((DAT_00049bac._2_1_ & 2) == 0) break;
        DAT_00049d56 = 0;
        if (DAT_00049d54 != 9) {
          DAT_00049d56 = DAT_00049d54 + 1;
        }
        DAT_00049d54 = DAT_00049d56;
        FUN_0001b786();
      }
      if ((_DAT_00049ba4 & 0x2200000) != 0) goto LAB_0001c4b0;
      if ((_DAT_00049ba4 & 0xe00fe) == 0) {
        iVar1 = param_1 * 0xcc;
        FUN_0000d3fc(*(undefined4 *)(&DAT_0004694c + iVar1),*(undefined4 *)(&DAT_00046950 + iVar1),
                     (short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046954 + iVar1) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046954 + iVar1),0,0xe0,0,0);
        goto LAB_0001c15c;
      }
      _DAT_00047b84 = 0;
      sVar2 = FUN_0001b718((short)(_DAT_00049ba4 >> 0x10),(short)_DAT_00049ba4);
      uVar4 = sVar2 - 1;
      if ((int)((uint)uVar4 << 0x10) < 0) {
        uVar4 = 9;
      }
      if ((&DAT_00049d2c)[(short)uVar4] == 0) {
        _DAT_00049ba4 = 0;
        goto LAB_0001c15c;
      }
      if (*(short *)(&DAT_00046a60 +
                    (short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[(short)uVar4]] * 0x16) < 200
         ) {
        iVar1 = param_1 * 0xcc;
        uVar7 = (undefined2)((uint)*(undefined4 *)(&DAT_00046960 + iVar1) >> 0x10);
        uVar8 = (undefined2)*(undefined4 *)(&DAT_00046960 + iVar1);
        uVar6 = *(undefined4 *)(&DAT_0004695c + iVar1);
        uVar5 = *(undefined4 *)(&DAT_00046958 + iVar1);
      }
      else {
        iVar1 = param_1 * 0xcc;
        uVar7 = (undefined2)((uint)*(undefined4 *)(&DAT_0004696c + iVar1) >> 0x10);
        uVar8 = (undefined2)*(undefined4 *)(&DAT_0004696c + iVar1);
        uVar6 = *(undefined4 *)(&DAT_00046968 + iVar1);
        uVar5 = *(undefined4 *)(&DAT_00046964 + iVar1);
      }
      FUN_0000d3fc(uVar5,uVar6,(short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,uVar7,uVar8,0
                   ,0xe0,0,0);
      FUN_0001b45a((short)((uint)PTR_s__00041030_0x12_00041074 >> 0x10),
                   (short)PTR_s__00041030_0x12_00041074,1,0xbe5c,
                   *(short *)(&DAT_00046a60 +
                             (short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[(short)uVar4]] *
                             0x16) >> 1);
      FUN_00012620(3);
      do {
        FUN_0000e4c0();
      } while ((_DAT_00049ba4 & 0x20002000) == 0);
      if ((_DAT_00049ba4 & 0x20000000) != 0) {
        DAT_00049d1e = (*(short *)(&DAT_00046a60 +
                                  (short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[(short)uVar4]]
                                  * 0x16) >> 1) + DAT_00049d1e;
        (&DAT_00049d2c)[(short)uVar4] = 0;
        DAT_00049d2a = DAT_00049d2a + 1;
        goto LAB_0001c3a2;
      }
    }
    else {
      _DAT_00049c48 = &DAT_000b5130;
      DAT_00043df2 = &DAT_000b5130;
      FUN_000185b2(4,0x3da0,7,0x77c0);
      uVar8 = (undefined2)DAT_000bd830;
      uVar7 = (undefined2)((uint)DAT_000bd830 >> 0x10);
      if (param_1 == 0) {
        if (DAT_00049d1e < 0x96) {
LAB_0001bf82:
          iVar1 = param_1 * 0xcc;
          uVar9 = (undefined2)((uint)*(undefined4 *)(&DAT_000468f4 + iVar1) >> 0x10);
          uVar10 = (undefined2)*(undefined4 *)(&DAT_000468f4 + iVar1);
          uVar6 = *(undefined4 *)(&DAT_000468f0 + iVar1);
          uVar5 = *(undefined4 *)(&DAT_000468ec + iVar1);
          goto LAB_0001c4a6;
        }
      }
      else if (DAT_00049d1e < 0xf) goto LAB_0001bf82;
      sVar2 = _DAT_00049d1c;
      if (param_1 == 0) {
        sVar2 = _DAT_00049d1a;
      }
      if (sVar2 != 0) {
        iVar1 = param_1 * 0xcc;
        FUN_0000d3fc(*(undefined4 *)(&DAT_000468f8 + iVar1),*(undefined4 *)(&DAT_000468fc + iVar1),
                     uVar7,uVar8,(short)((uint)*(undefined4 *)(&DAT_00046900 + iVar1) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046900 + iVar1),0,0xe0,0,0);
      }
      iVar1 = param_1 * 0xcc;
      uVar9 = (undefined2)((uint)*(undefined4 *)(&DAT_0004690c + iVar1) >> 0x10);
      uVar10 = (undefined2)*(undefined4 *)(&DAT_0004690c + iVar1);
      uVar7 = (undefined2)((uint)DAT_000bd830 >> 0x10);
      uVar8 = (undefined2)DAT_000bd830;
      uVar6 = *(undefined4 *)(&DAT_00046908 + iVar1);
      uVar5 = *(undefined4 *)(&DAT_00046904 + iVar1);
      while( true ) {
        while( true ) {
          FUN_0000d3fc(uVar5,uVar6,uVar7,uVar8,uVar9,uVar10,0,0xe0,0,0);
          sVar2 = FUN_0001bc78(param_1,(short)((uint)param_2 >> 0x10),(short)param_2);
          if (sVar2 == -1) goto LAB_0001c4b0;
          if (sVar2 == 0) goto LAB_0001c3a8;
          if (param_1 != 0) {
            sVar2 = sVar2 + 0x24;
          }
          uVar8 = (undefined2)DAT_000bd830;
          uVar7 = (undefined2)((uint)DAT_000bd830 >> 0x10);
          if (*(short *)(&DAT_00046a60 + sVar2 * 0x16) <= DAT_00049d1e) break;
          iVar1 = param_1 * 0xcc;
          uVar9 = (undefined2)((uint)*(undefined4 *)(&DAT_00046924 + iVar1) >> 0x10);
          uVar10 = (undefined2)*(undefined4 *)(&DAT_00046924 + iVar1);
          uVar6 = *(undefined4 *)(&DAT_00046920 + iVar1);
          uVar5 = *(undefined4 *)(&DAT_0004691c + iVar1);
        }
        if (DAT_00049d2a != 0) break;
        iVar1 = param_1 * 0xcc;
        uVar9 = (undefined2)((uint)*(undefined4 *)(&DAT_00046930 + iVar1) >> 0x10);
        uVar10 = (undefined2)*(undefined4 *)(&DAT_00046930 + iVar1);
        uVar6 = *(undefined4 *)(&DAT_0004692c + iVar1);
        uVar5 = *(undefined4 *)(&DAT_00046928 + iVar1);
      }
      DAT_00049d1e = DAT_00049d1e - *(short *)(&DAT_00046a60 + sVar2 * 0x16);
      sVar3 = 0;
      do {
        if ((&DAT_00049d2c)[sVar3] == 0) break;
        sVar3 = sVar3 + 1;
      } while (sVar3 < 10);
      (&DAT_00049d2c)[sVar3] = *(undefined2 *)(&DAT_00046a68 + sVar2 * 0x16);
      DAT_00049d2a = DAT_00049d2a + -1;
      *(undefined2 *)(&DAT_00049d40 + sVar3 * 2) = *(undefined2 *)(&DAT_00046a62 + sVar2 * 0x16);
LAB_0001c3a2:
      FUN_0001b786();
    }
LAB_0001c3a8:
    _DAT_00049c48 = &DAT_00055c60;
    DAT_00043df2 = &DAT_00055c60;
    FUN_000185b2(4,0x3da0,7,0x77c0);
    _DAT_00047b84 = 0x22002000;
    iVar1 = param_1 * 0xcc;
    FUN_0000d3fc(*(undefined4 *)(&DAT_00046970 + iVar1),*(undefined4 *)(&DAT_00046974 + iVar1),
                 DAT_000bd830,*(undefined4 *)(&DAT_00046978 + iVar1),0,0xe0,0,0);
    if (((_DAT_00049ba4 & 0x22002000) == 0) &&
       (FUN_0000d3fc(*(undefined4 *)(&DAT_0004697c + iVar1),*(undefined4 *)(&DAT_00046980 + iVar1),
                     (short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046984 + iVar1) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046984 + iVar1),0,0xe0,0,0xf),
       (_DAT_00049ba4 & 0x22002000) == 0)) {
      _DAT_00049ba4 = 0x2000000;
    }
    if ((_DAT_00049ba4 & 0x20000000) == 0) {
      iVar1 = param_1 * 0xcc;
      uVar9 = (undefined2)((uint)*(undefined4 *)(&DAT_00046990 + iVar1) >> 0x10);
      uVar10 = (undefined2)*(undefined4 *)(&DAT_00046990 + iVar1);
      uVar7 = (undefined2)((uint)DAT_000bd830 >> 0x10);
      uVar8 = (undefined2)DAT_000bd830;
      uVar6 = *(undefined4 *)(&DAT_0004698c + iVar1);
      uVar5 = *(undefined4 *)(&DAT_00046988 + iVar1);
LAB_0001c4a6:
      FUN_0000d3fc(uVar5,uVar6,uVar7,uVar8,uVar9,uVar10,0,0xe0,0,0);
LAB_0001c4b0:
      _DAT_00049c48 = &DAT_000b5130;
      DAT_00043df2 = &DAT_000b5130;
      FUN_000185b2(4,0x3da0,7,0x77c0);
      return;
    }
    _DAT_00049ba4 = 0;
    _DAT_00049c48 = &DAT_0005e360;
    DAT_00043df2 = &DAT_0005e360;
    FUN_000185b2(4,0x3da0,7,0x77c0);
  } while( true );
}


/* Address 0001c9e8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined2 FUN_0001c9e8(short param_1)

{
  uint uVar1;
  undefined4 uVar2;
  short sVar3;
  undefined2 uVar4;
  int iVar5;
  undefined2 unaff_D3w;
  undefined4 uVar6;
  undefined2 uVar7;
  
  DAT_00049d62 = 0x96;
  if ((_DAT_00049ba4 & 0x10001) != 0) {
    sVar3 = 0;
    uVar1 = _DAT_00049ba4 & 1;
    _DAT_00047b84 = 0x22002000;
switchD_0001ca64_default:
    do {
      if (uVar1 == 0) {
        sVar3 = sVar3 + 1;
        if (0xbb < sVar3) {
          sVar3 = 0;
        }
      }
      else {
        uVar2 = FUN_0001a77c(0);
        sVar3 = FUN_0000e60a((short)((uint)uVar2 >> 0x10),(short)uVar2,0,0xbc);
      }
      switch(sVar3) {
      case 0:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_1A_0001c4e0,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x7fffffff;
        uVar2 = 0x60;
        break;
      case 1:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_1B_0001c4e7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000000;
        uVar2 = 0x1591b0;
        break;
      case 2:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_1C_0001c4ee,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000001;
        uVar2 = 0x259350;
        break;
      case 3:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_2I_0001c4f5,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000002;
        uVar2 = 0x481080;
        break;
      case 4:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_2N_0001c4fc,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000003;
        uVar2 = 0x541f80;
        break;
      case 5:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_2Y_0001c503,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000004;
        uVar2 = 0x6c5910;
        break;
      case 6:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BAR_IDLE_0001c50a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000005;
        uVar2 = 0x8cef50;
        break;
      case 7:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BDK_IDLE_0001c513,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000006;
        uVar2 = 0x8fe0b0;
        break;
      case 8:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BS_IDLE_0001c51c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000007;
        uVar2 = 0x931260;
        break;
      case 9:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_1_0001c524,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000008;
        uVar2 = 0x953070;
        break;
      case 10:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_2I_0001c52a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000009;
        uVar2 = 0xc179d0;
        break;
      case 0xb:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_2N_0001c531,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000a;
        uVar2 = 0xe65560;
        break;
      case 0xc:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_3A_0001c538,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000b;
        uVar2 = 0x126c0f0;
        break;
      case 0xd:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_3B_0001c53f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000c;
        uVar2 = 0x1643b20;
        break;
      case 0xe:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_3C_0001c546,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000d;
        uVar2 = 0x1977ae0;
        break;
      case 0xf:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_3D_0001c54d,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000e;
        uVar2 = 0x1eb50e0;
        break;
      case 0x10:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_BUM_IDLE_0001c554,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000000f;
        uVar2 = 0x2870040;
        break;
      case 0x11:
        FUN_00018160();
        while (DAT_000bd830 != &DAT_000778d0) {
          FUN_00017f14();
        }
        FUN_000185b2(4,0x3e78,7,0x77c0);
        FUN_000149ae(0x14,2,s_C_LOSE_0001c55d,&DAT_000b29d0,0x3e08,4,0xc3e0,3,0);
        FUN_0000d3fc(3,0x39d35c0,(short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,0x8000,0x1e
                     ,0,0x140,0,0);
        uVar4 = FUN_000185b2(&DAT_00043da0,&DAT_000777c0);
        goto LAB_00020402;
      case 0x12:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_1A_0001c564,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000010;
        uVar2 = 0x289d610;
        break;
      case 0x13:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_1C_0001c56b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000011;
        uVar2 = 0x2968a70;
        break;
      case 0x14:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_2A_0001c572,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000012;
        uVar2 = 0x2ad94d0;
        break;
      case 0x15:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_2B_0001c579,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000013;
        uVar2 = 0x2d92fa0;
        break;
      case 0x16:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_2C_0001c580,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000014;
        uVar2 = 0x2f346f0;
        break;
      case 0x17:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_2I_0001c587,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000015;
        uVar2 = 0x3122430;
        break;
      case 0x18:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_2S_0001c58e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000016;
        uVar2 = 0x3260f40;
        break;
      case 0x19:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_3H_0001c595,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000017;
        uVar2 = 0x32f7f90;
        break;
      case 0x1a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_3L_0001c59c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000018;
        uVar2 = 0x33f12f0;
        break;
      case 0x1b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_4_0001c5a3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000019;
        uVar2 = 0x35aac20;
        break;
      case 0x1c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_4N_0001c5a9,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000001a;
        uVar2 = 0x36643b0;
        break;
      case 0x1d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_5A_0001c5b0,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000001b;
        uVar2 = 0x3736f80;
        break;
      case 0x1e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_5B_0001c5b7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000001c;
        uVar2 = 0x3841680;
        break;
      case 0x1f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_COM_IDLE_0001c5be,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000001d;
        uVar2 = 0x39aa040;
        break;
      case 0x20:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC1_1_0001c5c7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000001f;
        uVar2 = 0x3baacb0;
        break;
      case 0x21:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC1_2I_0001c5cd,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000020;
        uVar2 = 0x47c5da0;
        break;
      case 0x22:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC1_2N_0001c5d4,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000021;
        uVar2 = 0x49ab110;
        break;
      case 0x23:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC1_2Y_0001c5db,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000022;
        uVar2 = 0x4b93270;
        break;
      case 0x24:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC2_1_0001c5e2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000023;
        uVar2 = 0x4dadc50;
        break;
      case 0x25:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC3_1_0001c5e8,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000024;
        uVar2 = 0x4f2f120;
        break;
      case 0x26:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC3_2N_0001c5ee,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000025;
        uVar2 = 0x55b4530;
        break;
      case 0x27:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC3_2Y_0001c5f5,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000026;
        uVar2 = 0x57fc4e0;
        break;
      case 0x28:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC4_1A_0001c5fc,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000027;
        uVar2 = 0x5acaa70;
        break;
      case 0x29:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC4_1B_0001c603,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000028;
        uVar2 = 0x5e97f40;
        break;
      case 0x2a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC4_1C_0001c60a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000029;
        uVar2 = 0x6067590;
        break;
      case 0x2b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC5_1A_0001c611,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000002a;
        uVar2 = 0x656fe50;
        break;
      case 0x2c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC5_1B_0001c618,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000002b;
        uVar2 = 0x6818eb0;
        break;
      case 0x2d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DC6_1_0001c61f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000002c;
        uVar2 = 0x6b50ec0;
        break;
      case 0x2e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DCA_IDLE_0001c625,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000002d;
        uVar2 = 0x6f190e0;
        break;
      case 0x2f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_DCR_IDLE_0001c62e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000002e;
        uVar2 = 0x6f40ad0;
        break;
      case 0x30:
        FUN_00018160();
        while (DAT_000bd830 != &DAT_000778d0) {
          FUN_00017f14();
        }
        FUN_000185b2(4,0x3e78,7,0x77c0);
        FUN_000149ae(0x14,2,s_DEATH_0001c637,&DAT_000b29d0,0x3e08,4,0xc3e0,3,0);
        FUN_0000d3fc(3,0x6f63210,(short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,0x8000,0x2f
                     ,0,0x140,0,0);
        uVar4 = FUN_000185b2(&DAT_00043da0,&DAT_000777c0);
        goto LAB_00020402;
      case 0x31:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR1_1_0001c63d,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000030;
        uVar2 = 0x72a4520;
        break;
      case 0x32:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR1_2N_0001c643,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000031;
        uVar2 = 0x79ba470;
        break;
      case 0x33:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR1_2Y_0001c64a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000032;
        uVar2 = 0x7c2de60;
        break;
      case 0x34:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR1_3N_0001c651,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000033;
        uVar2 = 0x7e8dff0;
        break;
      case 0x35:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR2_1_0001c658,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000034;
        uVar2 = 0x8095170;
        break;
      case 0x36:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR3_1A_0001c65e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000035;
        uVar2 = 0x82cbd80;
        break;
      case 0x37:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR3_1B_0001c665,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000036;
        uVar2 = 0x8426ac0;
        break;
      case 0x38:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR4_1_0001c66c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000037;
        uVar2 = 0x857a090;
        break;
      case 0x39:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GR5_1_0001c672,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000038;
        uVar2 = 0x88473c0;
        break;
      case 0x3a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_1A_0001c678,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000039;
        uVar2 = 0x8f87af0;
        break;
      case 0x3b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_1C_0001c67f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003a;
        uVar2 = 0x9068c70;
        break;
      case 0x3c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_2A_0001c686,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003b;
        uVar2 = 0x91d7210;
        break;
      case 0x3d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_2B_0001c68d,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003c;
        uVar2 = 0x93d6c20;
        break;
      case 0x3e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_2C_0001c694,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003d;
        uVar2 = 0x9562f80;
        break;
      case 0x3f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_2I_0001c69b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003e;
        uVar2 = 0x96a7fa0;
        break;
      case 0x40:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_2S_0001c6a2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000003f;
        uVar2 = 0x982b930;
        break;
      case 0x41:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_3H_0001c6a9,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000040;
        uVar2 = 0x98e59f0;
        break;
      case 0x42:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_3L_0001c6b0,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000041;
        uVar2 = 0x9aa5830;
        break;
      case 0x43:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_4_0001c6b7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000042;
        uVar2 = 0x9c5ba40;
        break;
      case 0x44:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_4N_0001c6bd,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000043;
        uVar2 = 0x9d467f0;
        break;
      case 0x45:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_5A_0001c6c4,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000044;
        uVar2 = 0x9ec0550;
        break;
      case 0x46:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_5B_0001c6cb,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000045;
        uVar2 = 0x9fe9340;
        break;
      case 0x47:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_GUN_IDLE_0001c6d2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000046;
        uVar2 = 0xa141290;
        break;
      case 0x48:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_1_0001c6db,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000047;
        uVar2 = 0xa1703f0;
        break;
      case 0x49:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_2I_0001c6e1,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000048;
        uVar2 = 0xa24cbf0;
        break;
      case 0x4a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_2N_0001c6e8,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000049;
        uVar2 = 0xa2e4ea0;
        break;
      case 0x4b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_2Y_0001c6ef,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004a;
        uVar2 = 0xa3a7000;
        break;
      case 0x4c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_3_0001c6f6,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004b;
        uVar2 = 0xa82e590;
        break;
      case 0x4d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_4_0001c6fc,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004c;
        uVar2 = 0xa848c30;
        break;
      case 0x4e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_HKR_IDLE_0001c702,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004d;
        uVar2 = 0xa92c270;
        break;
      case 0x4f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_LX1_IDLE_0001c70b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004e;
        uVar2 = 0xa9484a0;
        break;
      case 0x50:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_LX2_IDLE_0001c714,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000004f;
        uVar2 = 0xa96d0a0;
        break;
      case 0x51:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_MORGUE_0001c71d,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000050;
        uVar2 = 0xa9953c0;
        break;
      case 0x52:
        FUN_00018160();
        while (DAT_000bd830 != &DAT_000778d0) {
          FUN_00017f14();
        }
        FUN_000185b2(4,0x3e78,7,0x77c0);
        FUN_000149ae(0x14,2,s_M_LOSE_0001c724,&DAT_000b29d0,0x3e08,4,0xc3e0,3,0);
        FUN_0000d3fc(3,0xaaea520,(short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,0x8000,0x51
                     ,0,0x140,0,0);
        uVar4 = FUN_000185b2(&DAT_00043da0,&DAT_000777c0);
        goto LAB_00020402;
      case 0x53:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG1_1_0001c72b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000052;
        uVar2 = 0xacbf750;
        break;
      case 0x54:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG1_2N_0001c731,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000053;
        uVar2 = 0xbac4e60;
        break;
      case 0x55:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG1_2Y_0001c738,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000054;
        uVar2 = 0xbd80df0;
        break;
      case 0x56:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG2_1_0001c73f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000055;
        uVar2 = 0xc10e6f0;
        break;
      case 0x57:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG2_2N_0001c745,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000056;
        uVar2 = 0xc554520;
        break;
      case 0x58:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG2_2Y_0001c74c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000057;
        uVar2 = 0xc7001d0;
        break;
      case 0x59:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG2_3_0001c753,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000058;
        uVar2 = 0xc9e1690;
        break;
      case 0x5a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG3_1A_0001c759,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000059;
        uVar2 = 0xca4ba40;
        break;
      case 0x5b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG3_1B_0001c760,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005a;
        uVar2 = 0xcea7590;
        break;
      case 0x5c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG3_1C_0001c767,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005b;
        uVar2 = 0xd11a650;
        break;
      case 0x5d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG4_1_0001c76e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005c;
        uVar2 = 0xd4566b0;
        break;
      case 0x5e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG5_1_0001c774,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005d;
        uVar2 = 0xd632720;
        break;
      case 0x5f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG5_2A_0001c77a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005e;
        uVar2 = 0xd842270;
        break;
      case 0x60:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PG5_2B_0001c781,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000005f;
        uVar2 = 0xdb718b0;
        break;
      case 0x61:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PGK_IDLE_0001c788,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000060;
        uVar2 = 0xddafc30;
        break;
      case 0x62:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_PGG_IDLE_0001c791,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000061;
        uVar2 = 0xddd2ca0;
        break;
      case 99:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RAZ_IDLE_0001c79a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000062;
        uVar2 = 0xdded340;
        break;
      case 100:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK2_1_0001c7a3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000063;
        uVar2 = 0xde168c0;
        break;
      case 0x65:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK4_2_0001c7a9,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000064;
        uVar2 = 0xe0b25d0;
        break;
      case 0x66:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK4_3_0001c7af,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000065;
        uVar2 = 0xee623f0;
        break;
      case 0x67:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK5_1_0001c7b5,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000066;
        uVar2 = 0xf0ab600;
        break;
      case 0x68:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK5_2I_0001c7bb,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000067;
        uVar2 = 0x101b4910;
        break;
      case 0x69:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RK5_2N_0001c7c2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000068;
        uVar2 = 0x10462c20;
        break;
      case 0x6a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_RKP_IDLE_0001c7c9,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000069;
        uVar2 = 0x1078f470;
        break;
      case 0x6b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC1_1_0001c7d2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006a;
        uVar2 = 0x107af6f0;
        break;
      case 0x6c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC1_2I_0001c7d8,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006b;
        uVar2 = 0x11626920;
        break;
      case 0x6d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC1_2N_0001c7df,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006c;
        uVar2 = 0x11ad98f0;
        break;
      case 0x6e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC1_2Y_0001c7e6,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006d;
        uVar2 = 0x11e045b0;
        break;
      case 0x6f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC2_1B_0001c7ed,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006e;
        uVar2 = 0x122131e0;
        break;
      case 0x70:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC2_2A_0001c7f4,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000006f;
        uVar2 = 0x12604980;
        break;
      case 0x71:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC3_1_0001c7fb,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000070;
        uVar2 = 0x12a1c8b0;
        break;
      case 0x72:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC3_2A1_0001c801,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000071;
        uVar2 = 0x12d7f9d0;
        break;
      case 0x73:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC3_2A2_0001c809,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000072;
        uVar2 = 0x1301a480;
        break;
      case 0x74:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC3_2B_0001c811,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000073;
        uVar2 = 0x13508fd0;
        break;
      case 0x75:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC3_2C_0001c818,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000074;
        uVar2 = 0x138f7050;
        break;
      case 0x76:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC4_1_0001c81f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000075;
        uVar2 = 0x13cad5a0;
        break;
      case 0x77:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC4_2_0001c825,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000076;
        uVar2 = 0x13e4aca0;
        break;
      case 0x78:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SC_IDLE_0001c82b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000077;
        uVar2 = 0x13e65340;
        break;
      case 0x79:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD1_1_0001c833,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000078;
        uVar2 = 0x13e89610;
        break;
      case 0x7a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD1_2I_0001c839,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000079;
        uVar2 = 0x14586120;
        break;
      case 0x7b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD1_2N_0001c840,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007a;
        uVar2 = 0x150a7580;
        break;
      case 0x7c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD1_2Y_0001c847,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007b;
        uVar2 = 0x15248cd0;
        break;
      case 0x7d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD2_1A_0001c84e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007c;
        uVar2 = 0x1577f490;
        break;
      case 0x7e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD2_1B_0001c855,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007d;
        uVar2 = 0x15e03640;
        break;
      case 0x7f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD3_1A_0001c85c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007e;
        uVar2 = 0x16297f20;
        break;
      case 0x80:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD3_1B_0001c863,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000007f;
        uVar2 = 0x1647ee20;
        break;
      case 0x81:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD3_3A_0001c86a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000080;
        uVar2 = 0x166f9650;
        break;
      case 0x82:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD3_3B_0001c871,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000081;
        uVar2 = 0x16a93040;
        break;
      case 0x83:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD3_3C_0001c878,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000082;
        uVar2 = 0x16f54ef0;
        break;
      case 0x84:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD4_1A_0001c87f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000083;
        uVar2 = 0x17290f50;
        break;
      case 0x85:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD4_1AB_0001c886,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000084;
        uVar2 = 0x17406330;
        break;
      case 0x86:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD4_1B_0001c88e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000085;
        uVar2 = 0x1758cab0;
        break;
      case 0x87:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD4_2_0001c895,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000086;
        uVar2 = 0x186d2ba0;
        break;
      case 0x88:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD5_1A_0001c89b,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000087;
        uVar2 = 0x18f3d320;
        break;
      case 0x89:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD5_1B_0001c8a2,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000088;
        uVar2 = 0x1942fec0;
        break;
      case 0x8a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD5_2A_0001c8a9,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000089;
        uVar2 = 0x19922a60;
        break;
      case 0x8b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SD5_3_0001c8b0,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008a;
        uVar2 = 0x1ae98c60;
        break;
      case 0x8c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SDP_IDLE_0001c8b6,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008b;
        uVar2 = 0x1b409d40;
        break;
      case 0x8d:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8bf,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008c;
        uVar2 = 0x1b429690;
        break;
      case 0x8e:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8c3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008d;
        uVar2 = 0x1b4d23b0;
        break;
      case 0x8f:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8c7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008e;
        uVar2 = 0x1b59f3a0;
        break;
      case 0x90:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8cb,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000008f;
        uVar2 = 0x1b658b30;
        break;
      case 0x91:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8cf,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000090;
        uVar2 = 0x1b72dbc0;
        break;
      case 0x92:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8d3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000091;
        uVar2 = 0x1b7d2890;
        break;
      case 0x93:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8d7,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000092;
        uVar2 = 0x1b90ca20;
        break;
      case 0x94:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8db,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000093;
        uVar2 = 0x1b9f77d0;
        break;
      case 0x95:
        FUN_00018160();
        FUN_000149ae(0x14,2,&DAT_0001c8df,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000094;
        uVar2 = 0x1bae2eb0;
        break;
      case 0x96:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SJ_IDLE_0001c8e3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000095;
        uVar2 = 0x1bc64380;
        break;
      case 0x97:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS1_1_0001c8eb,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000096;
        uVar2 = 0x1bc93e10;
        break;
      case 0x98:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS1_2N_0001c8f1,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000097;
        uVar2 = 0x1c311ab0;
        break;
      case 0x99:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS1_2Y_0001c8f8,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000098;
        uVar2 = 0x1c4ca180;
        break;
      case 0x9a:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS2_1A_0001c8ff,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x80000099;
        uVar2 = 0x1c882260;
        break;
      case 0x9b:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS2_1B_0001c906,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009a;
        uVar2 = 0x1ca84a60;
        break;
      case 0x9c:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS3_1_0001c90d,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009b;
        uVar2 = 0x1ce42720;
        break;
      case 0x9d:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS3_2I_0001c913,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009c;
        uVar2 = 0x1d5b6000;
        break;
      case 0x9e:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS3_2N_0001c91a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009d;
        uVar2 = 0x1d8857f0;
        break;
      case 0x9f:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS3_2Y_0001c921,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009e;
        uVar2 = 0x1da98130;
        break;
      case 0xa0:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS4_1A_0001c928,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x8000009f;
        uVar2 = 0x1dcbb4e0;
        break;
      case 0xa1:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SS4_1B_0001c92f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a0;
        uVar2 = 0x1dfd3270;
        break;
      case 0xa2:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SSD_IDLE_0001c936,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a1;
        uVar2 = 0x1e4729e0;
        break;
      case 0xa3:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_SSF_IDLE_0001c93f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a2;
        uVar2 = 0x1e48c750;
        break;
      case 0xa4:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TB2_2_0001c948,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a3;
        uVar2 = 0x1e4ae560;
        break;
      case 0xa5:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TB3_1B_0001c94e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a4;
        uVar2 = 0x1f7036d0;
        break;
      case 0xa6:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TB3_2I_0001c955,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a5;
        uVar2 = 0x1f71dd70;
        break;
      case 0xa7:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TB3_2N_0001c95c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a6;
        uVar2 = 0x1fcdf490;
        break;
      case 0xa8:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TB3_2Y_0001c963,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a7;
        uVar2 = 0x1ffdf970;
        break;
      case 0xa9:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI1_1_0001c96a,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a8;
        uVar2 = 0x208ba9b0;
        break;
      case 0xaa:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI1_2I_0001c970,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000a9;
        uVar2 = 0x21135ba0;
        break;
      case 0xab:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI1_2N_0001c977,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000aa;
        uVar2 = 0x214d63d0;
        break;
      case 0xac:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI1_2Y_0001c97e,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000ab;
        uVar2 = 0x217fe2a0;
        break;
      case 0xad:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI2_1A_0001c985,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000ac;
        uVar2 = 0x221a90c0;
        break;
      case 0xae:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI2_1B_0001c98c,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000ad;
        uVar2 = 0x224bbba0;
        break;
      case 0xaf:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_1_0001c993,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000ae;
        uVar2 = 0x228f6b40;
        break;
      case 0xb0:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_2_0001c999,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000af;
        uVar2 = 0x22d538f0;
        break;
      case 0xb1:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_3_0001c99f,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b0;
        uVar2 = 0x2340ac50;
        break;
      case 0xb2:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_4_0001c9a5,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b1;
        uVar2 = 0x23684220;
        break;
      case 0xb3:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_5_0001c9ab,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b2;
        uVar2 = 0x240f3f90;
        break;
      case 0xb4:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_6I_0001c9b1,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b3;
        uVar2 = 0x2481e9a0;
        break;
      case 0xb5:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_6N_0001c9b8,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b4;
        uVar2 = 0x24c7d2e0;
        break;
      case 0xb6:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI3_6Y_0001c9bf,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b5;
        uVar2 = 0x24e56e90;
        break;
      case 0xb7:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI4_1_0001c9c6,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b6;
        uVar2 = 0x255d8d20;
        break;
      case 0xb8:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI4_2N_0001c9cc,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b7;
        uVar2 = 0x25936260;
        break;
      case 0xb9:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI4_2Y_0001c9d3,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        uVar6 = 0x800000b8;
        uVar2 = 0x259cadf0;
        break;
      case 0xba:
        FUN_00018160();
        FUN_000149ae(0x14,2,s_TI5_1_0001c9da,0xb,0x29d0,0,0x3e08,4,0xc3e0,3,0);
        FUN_0000d3fc(3,0x25b02190,DAT_000bd830,0x800000b9,0xe0,0);
        goto switchD_0001ca64_default;
      case 0xbb:
        FUN_00018160();
        while (DAT_000bd830 != &DAT_000778d0) {
          FUN_00017f14();
        }
        FUN_000185b2(4,0x3e78,7,0x77c0);
        FUN_000149ae(0x14,2,s_T_LOSE_0001c9e0,&DAT_000b29d0,0x3e08,4,0xc3e0,3,0);
        FUN_0000d3fc(3,0x2613c210,(short)((uint)DAT_000bd830 >> 0x10),(short)DAT_000bd830,0x8000,
                     0xba,0,0x140,0,0);
        FUN_000185b2(&DAT_00043da0,&DAT_000777c0);
      default:
        goto switchD_0001ca64_default;
      }
      uVar4 = FUN_0000d3fc(3,uVar2,DAT_000bd830,uVar6,0xe0,0);
LAB_00020402:
      if ((_DAT_00049ba4 & 0x2000) != 0) {
        return uVar4;
      }
    } while( true );
  }
  _DAT_00047b84 = 0x22002000;
  FUN_00018160();
  _DAT_00049c48 = &DAT_00055c60;
  DAT_00043df2 = &DAT_00055c60;
  FUN_000185b2(4,0x3da0,7,0x77c0);
  iVar5 = param_1 * 0x84;
  FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fa4 + iVar5),DAT_000bd830,
               *(undefined4 *)(&DAT_00046fa8 + iVar5),0,0xe0,0,0);
  if ((_DAT_00049ba4 & 0x22002000) == 0) {
    if (*(int *)(&DAT_00046fb0 + iVar5) == 0) goto LAB_0002079c;
    FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fb0 + iVar5),(short)((uint)DAT_000bd830 >> 0x10),
                 (short)DAT_000bd830,(short)((uint)*(undefined4 *)(&DAT_00046fb4 + iVar5) >> 0x10),
                 (short)*(undefined4 *)(&DAT_00046fb4 + iVar5),0,0xe0,0,0xf);
    if (_DAT_00049ba4 == 0) {
      _DAT_00049ba4 = 0x2000000;
    }
  }
  uVar7 = SUB42(DAT_000bd830,0);
  uVar4 = (undefined2)((uint)DAT_000bd830 >> 0x10);
  if ((_DAT_00049ba4 & 0x20000000) == 0) {
    if ((_DAT_00049ba4 & 0x2000000) == 0) {
      iVar5 = param_1 * 0x84;
      FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fd4 + iVar5),uVar4,uVar7,
                   (short)((uint)*(undefined4 *)(&DAT_00046fd8 + iVar5) >> 0x10),
                   (short)*(undefined4 *)(&DAT_00046fd8 + iVar5),0,0xe0,0,0);
      if ((_DAT_00049ba4 & 0x22002000) == 0) {
        unaff_D3w = 5;
        if (*(int *)(&DAT_00046fec + iVar5) == 0) goto LAB_0002079c;
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fec + iVar5),(short)((uint)DAT_000bd830 >> 0x10),
                     (short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046ff0 + iVar5) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046ff0 + iVar5),0,0xe0,0,0xf);
        if (_DAT_00049ba4 == 0) {
          _DAT_00049ba4 = 0x2000000;
        }
      }
      uVar4 = (undefined2)((uint)DAT_000bd830 >> 0x10);
      if ((_DAT_00049ba4 & 0x20000000) == 0) {
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_0004701c + param_1 * 0x84),uVar4,(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00047020 + param_1 * 0x84) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00047020 + param_1 * 0x84),0,0xe0,0,0);
        unaff_D3w = 5;
      }
      else {
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_00047010 + param_1 * 0x84),uVar4,(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00047014 + param_1 * 0x84) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00047014 + param_1 * 0x84),0,0xe0,0,0);
        unaff_D3w = 4;
      }
    }
    else {
      iVar5 = param_1 * 0x84;
      FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fc8 + iVar5),uVar4,uVar7,
                   (short)((uint)*(undefined4 *)(&DAT_00046fcc + iVar5) >> 0x10),
                   (short)*(undefined4 *)(&DAT_00046fcc + iVar5),0,0xe0,0,0);
      if ((_DAT_00049ba4 & 0x22002000) == 0) {
        unaff_D3w = 2;
        if (*(int *)(&DAT_00046fe0 + iVar5) == 0) goto LAB_0002079c;
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fe0 + iVar5),(short)((uint)DAT_000bd830 >> 0x10),
                     (short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046fe4 + iVar5) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046fe4 + iVar5),0,0xe0,0,0xf);
        if (_DAT_00049ba4 == 0) {
          _DAT_00049ba4 = 0x2000000;
        }
      }
      uVar4 = (undefined2)((uint)DAT_000bd830 >> 0x10);
      if ((_DAT_00049ba4 & 0x20000000) == 0) {
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_00047004 + param_1 * 0x84),uVar4,(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00047008 + param_1 * 0x84) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00047008 + param_1 * 0x84),0,0xe0,0,0);
        unaff_D3w = 3;
      }
      else {
        FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046ff8 + param_1 * 0x84),uVar4,(short)DAT_000bd830,
                     (short)((uint)*(undefined4 *)(&DAT_00046ffc + param_1 * 0x84) >> 0x10),
                     (short)*(undefined4 *)(&DAT_00046ffc + param_1 * 0x84),0,0xe0,0,0);
        unaff_D3w = 2;
      }
    }
  }
  else {
    FUN_0000d3fc(3,*(undefined4 *)(&DAT_00046fbc + param_1 * 0x84),uVar4,uVar7,
                 (short)((uint)*(undefined4 *)(&DAT_00046fc0 + param_1 * 0x84) >> 0x10),
                 (short)*(undefined4 *)(&DAT_00046fc0 + param_1 * 0x84),0,0xe0,0,0);
    unaff_D3w = 1;
  }
LAB_0002079c:
  _DAT_00049c48 = &DAT_000b5130;
  DAT_00043df2 = &DAT_000b5130;
  FUN_000185b2(4,0x3da0,7,0x77c0);
  return unaff_D3w;
}


/* Address 000207cc */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000207cc(short param_1)

{
  int iVar1;
  
  _DAT_00047b84 = 0x22002000;
  FUN_00018160();
  iVar1 = param_1 * 0xc;
  FUN_0000d3fc(*(undefined4 *)(&DAT_00047864 + iVar1),*(undefined4 *)(&DAT_00047868 + iVar1),
               DAT_000bd830,*(undefined4 *)(&DAT_0004786c + iVar1),0xe0,0);
  return;
}


/* Address 00020820 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x1a532","bytes":"4eb900020820","assembly":"jsr
   $20820.l"}] */

void observed_call_candidate_00020820(void)

{
  short sVar1;
  char cVar6;
  int iVar2;
  int iVar3;
  short sVar4;
  short sVar5;
  int iVar7;
  int iVar8;
  short sVar9;
  int unaff_D6;
  int iVar10;
  
  sVar1 = _DAT_00049d5c;
  iVar8 = 0xfffff;
  sVar9 = -1;
  _DAT_00049d5c = 0;
  sVar5 = 0;
  do {
    iVar10 = (int)sVar5;
    iVar7 = iVar10 * 0xce;
    if (((((&DAT_00049d6c)[iVar10 * 0x67] != 0) && ((&DAT_00049dd8)[iVar10 * 0x67] != 0)) &&
        (0xf < (short)(&DAT_00047b9e)[*(short *)(iVar7 + 0x49e2c) * 0x20])) &&
       ((short)(&DAT_00047b9e)[*(short *)(iVar7 + 0x49e2c) * 0x20] < 0x401)) {
      iVar10 = DAT_00049c50 - *(int *)((int)&DAT_00049d70 + iVar7);
      iVar7 = DAT_00049c56 - *(int *)((int)&DAT_00049d76 + iVar7);
      cVar6 = FUN_00013440(-(short)iVar10,-(short)iVar7);
      cVar6 = cVar6 - DAT_00049cba;
      if ((cVar6 < '\x06') && (-6 < cVar6)) {
        iVar2 = FUN_0000e540((int)(short)cVar6,(short)cVar6 * 0x14);
        iVar3 = FUN_0000e540(iVar10,iVar10);
        iVar7 = FUN_0000e540(iVar7,iVar7);
        iVar10 = iVar7 + iVar3 + iVar2;
        if (iVar10 < iVar8) {
          unaff_D6 = iVar7 + iVar3;
          iVar8 = iVar10;
          sVar9 = sVar5;
        }
      }
    }
    sVar5 = sVar5 + 1;
  } while (sVar5 < 0x28);
  if ((sVar9 != -1) && (unaff_D6 < *(int *)(DAT_00049d5a * 4 + 0x4c280))) {
    iVar8 = (int)*(short *)(sVar9 * 0xce + 0x49e2c);
    sVar5 = (&DAT_00047b9e)[iVar8 * 0x20];
    sVar4 = FUN_0000e588((short)(&DAT_00047b9a)[iVar8 * 0x20] * 0xad,(int)sVar5);
    sVar4 = sVar4 + 0x70;
    sVar5 = FUN_0000e588((short)((&DAT_00047b9c)[iVar8 * 0x20] + -0x14) * 0xad,(int)sVar5);
    sVar5 = sVar5 + 0x5a;
    if (sVar4 < _DAT_00049d68) {
      _DAT_00049d68 = (_DAT_00049d68 + -1) - ((short)(_DAT_00049d68 - sVar4) >> 3);
    }
    if (_DAT_00049d68 < sVar4) {
      _DAT_00049d68 = ((short)(sVar4 - _DAT_00049d68) >> 3) + _DAT_00049d68 + 1;
    }
    if (sVar5 < _DAT_00049d6a) {
      _DAT_00049d6a = (_DAT_00049d6a + -1) - ((short)(_DAT_00049d6a - sVar5) >> 3);
    }
    if (_DAT_00049d6a < sVar5) {
      _DAT_00049d6a = ((short)(sVar5 - _DAT_00049d6a) >> 3) + _DAT_00049d6a + 1;
    }
    if ((sVar4 == _DAT_00049d68) && (sVar5 == _DAT_00049d6a)) {
      _DAT_00049d5e = 1;
    }
    else {
      _DAT_00049d5e = 0;
    }
    if (((ushort)(_DAT_00049d68 - 1U) < 0xdf) && ((ushort)(_DAT_00049d6a - 9U) < 0xa3)) {
      if (sVar1 == 0) {
        _DAT_00049d68 = 0x70;
        _DAT_00049d6a = 0x5a;
      }
      _DAT_00049d5c = 1;
    }
    sRam00049d64 = (short)unaff_D6;
    iVar8 = 1;
    DAT_00049d60 = sVar9;
    do {
      iVar7 = (int)sRam00049d64;
      iVar10 = FUN_0000e540(iVar8,iVar8);
      if (iVar7 < iVar10) {
        DAT_00049d66 = 0x100 - (short)iVar8;
        return;
      }
      iVar8 = iVar8 + 1;
    } while (iVar8 < 0x100);
  }
  return;
}


/* Address 00020aa0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020aa0(void)

{
  short sVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short *psVar7;
  short *psVar8;
  
  sVar5 = 0;
  if (0 < _DAT_0015ed46) {
    do {
      psVar8 = *(short **)(&DAT_0015ece2 + sVar5 * 4) + 1;
      for (sVar1 = **(short **)(&DAT_0015ece2 + sVar5 * 4); 0 < sVar1; sVar1 = sVar1 + -1) {
        if (DAT_00049c60 == 1) {
          sVar4 = *psVar8;
          iVar3 = *(int *)(psVar8 + 1);
          sVar6 = psVar8[3];
          psVar7 = psVar8 + 6;
          iVar2 = *(int *)(psVar8 + 4);
LAB_00020af8:
          psVar8 = psVar7 + 1;
          FUN_00013ae0(sVar4,iVar3,sVar6,iVar2,*psVar7);
        }
        else if (DAT_00049c60 == 2) {
          sVar4 = *psVar8;
          iVar3 = DAT_00049c6a + psVar8[1];
          sVar6 = 0;
          psVar7 = psVar8 + 3;
          iVar2 = DAT_00049c72 + psVar8[2];
          goto LAB_00020af8;
        }
      }
      sVar5 = sVar5 + 1;
    } while (sVar5 < _DAT_0015ed46);
  }
  _DAT_0015ed46 = 0;
  return;
}


/* Address 00020b2a */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020b2a(undefined2 *param_1,undefined2 *param_2,short param_3)

{
  short sVar1;
  
  *param_2 = *param_1;
  param_2[1] = param_1[1];
  param_2[2] = param_1[2];
  param_2[3] = param_1[3];
  *(int *)(param_2 + 4) = (int)param_2 + (short)param_1[4] + 8;
  *(int *)(param_2 + 6) = (int)param_2 + (short)param_1[5] + 8;
  *(int *)(param_2 + 8) = (int)param_2 + (short)param_1[6] + 8;
  *(int *)(param_2 + 10) = (int)param_2 + (short)param_1[7] + 8;
  FUN_0000e3e0(param_1 + 8,param_2 + 0xc,(int)(short)(param_3 + -0x10));
  sVar1 = 0;
  if (0 < (short)param_2[3]) {
    do {
      *(undefined2 *)(&DAT_0015ec7c + _DAT_0015ece0 * 2) =
           *(undefined2 *)(*(int *)(param_2 + 10) + sVar1 * 2 + 4);
      _DAT_0015ece0 = _DAT_0015ece0 + 1;
      sVar1 = sVar1 + 3;
    } while (sVar1 < (short)param_2[3]);
  }
  *(int *)(&DAT_0015ece2 + _DAT_0015ed46 * 4) = *(int *)(param_2 + 10) + (short)param_2[3] * 2;
  _DAT_0015ed46 = _DAT_0015ed46 + 1;
  *(undefined2 **)(_DAT_0015edac * 4 + 0x15ed48) = param_2;
  _DAT_0015edac = _DAT_0015edac + 1;
  return;
}


/* Address 00020c16 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020c16(void)

{
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  short sVar4;
  short sVar5;
  undefined2 *puVar6;
  undefined2 *puVar7;
  undefined2 *puVar8;
  
  sVar4 = 0;
  if (0 < _DAT_0015ece0) {
    do {
      FUN_0001ac68(*(undefined2 *)(&DAT_0015ec7c + sVar4 * 2));
      sVar4 = sVar4 + 1;
    } while (sVar4 < _DAT_0015ece0);
  }
  _DAT_0015ece0 = 0;
  sVar4 = 0;
  if (0 < _DAT_0015edac) {
    do {
      iVar2 = *(int *)(sVar4 * 4 + 0x15ed48);
      sVar5 = 0;
      iVar1 = *(int *)(iVar2 + 0xc);
      if (0 < *(short *)(iVar2 + 2)) {
        puVar8 = (undefined2 *)(iVar1 + 6);
        puVar7 = (undefined2 *)(iVar1 + 4);
        puVar6 = (undefined2 *)(iVar1 + 2);
        do {
          uVar3 = FUN_0001ac3c(*puVar6);
          *puVar6 = uVar3;
          uVar3 = FUN_0001ac3c(*puVar7);
          *puVar7 = uVar3;
          uVar3 = FUN_0001ac3c(*puVar8);
          *puVar8 = uVar3;
          puVar8 = puVar8 + 0xe;
          puVar7 = puVar7 + 0xe;
          puVar6 = puVar6 + 0xe;
          sVar5 = sVar5 + 1;
        } while (sVar5 < *(short *)(iVar2 + 2));
      }
      sVar4 = sVar4 + 1;
    } while (sVar4 < _DAT_0015edac);
  }
  _DAT_0015edac = 0;
  return;
}


/* Address 00020cc4 */

void FUN_00020cc4(int param_1)

{
  short sVar1;
  
  sVar1 = 0;
  if (0 < *(short *)(param_1 + 6)) {
    do {
      FUN_0001ae56(*(undefined2 *)(*(int *)(param_1 + 0x14) + sVar1 * 2));
      sVar1 = sVar1 + 1;
    } while (sVar1 < *(short *)(param_1 + 6));
  }
  return;
}


/* Address 00020cf8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020cf8(int param_1,int param_2,short param_3)

{
  short sVar1;
  short *psVar2;
  int iVar3;
  
  FUN_0000e3e0(param_1,param_2,(int)param_3);
  *(int *)(param_2 + 4) = *(int *)(param_1 + 4) + param_2;
  iVar3 = *(int *)(param_1 + 8) + param_2;
  *(int *)(param_2 + 8) = iVar3;
  psVar2 = (short *)(iVar3 + *(short *)(param_2 + 2) * 6);
  for (sVar1 = *psVar2; psVar2 = psVar2 + 1, 0 < sVar1; sVar1 = sVar1 + -1) {
    *(short *)(&DAT_0015ec7c + _DAT_0015ece0 * 2) = *psVar2;
    _DAT_0015ece0 = _DAT_0015ece0 + 1;
  }
  *(short **)(&DAT_0015ece2 + _DAT_0015ed46 * 4) = psVar2;
  _DAT_0015ed46 = _DAT_0015ed46 + 1;
  return;
}


/* Address 00020d7c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020d7c(void)

{
  int iVar1;
  short *psVar2;
  undefined2 uVar3;
  short sVar4;
  undefined2 *puVar5;
  undefined2 *puVar6;
  undefined2 *puVar7;
  undefined2 *puVar8;
  undefined2 *puVar9;
  undefined2 *puVar10;
  
  sVar4 = 0;
  if (0 < _DAT_0015ece0) {
    do {
      FUN_0001ac68(*(undefined2 *)(&DAT_0015ec7c + sVar4 * 2));
      sVar4 = sVar4 + 1;
    } while (sVar4 < _DAT_0015ece0);
  }
  psVar2 = DAT_00049c18;
  _DAT_0015ece0 = 0;
  sVar4 = 0;
  iVar1 = *(int *)(DAT_00049c18 + 2);
  if (0 < *DAT_00049c18) {
    puVar5 = (undefined2 *)(iVar1 + 0x14);
    puVar10 = (undefined2 *)(iVar1 + 0x12);
    puVar9 = (undefined2 *)(iVar1 + 0x10);
    puVar8 = (undefined2 *)(iVar1 + 0xe);
    puVar7 = (undefined2 *)(iVar1 + 0xc);
    puVar6 = (undefined2 *)(iVar1 + 10);
    do {
      uVar3 = FUN_0001ac3c(*puVar6);
      *puVar6 = uVar3;
      uVar3 = FUN_0001ac3c(*puVar7);
      *puVar7 = uVar3;
      uVar3 = FUN_0001ac3c(*puVar8);
      *puVar8 = uVar3;
      uVar3 = FUN_0001ac3c(*puVar9);
      *puVar9 = uVar3;
      uVar3 = FUN_0001ac3c(*puVar10);
      *puVar10 = uVar3;
      uVar3 = FUN_0001ac3c(*puVar5);
      *puVar5 = uVar3;
      puVar5 = puVar5 + 0xc;
      puVar10 = puVar10 + 0xc;
      puVar9 = puVar9 + 0xc;
      puVar8 = puVar8 + 0xc;
      puVar7 = puVar7 + 0xc;
      puVar6 = puVar6 + 0xc;
      sVar4 = sVar4 + 1;
    } while (sVar4 < *psVar2);
  }
  return;
}


/* Address 00020e40 */

void FUN_00020e40(int param_1)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short *psVar4;
  
  psVar4 = (short *)(*(int *)(param_1 + 8) + *(short *)(param_1 + 2) * 6);
  sVar1 = *psVar4;
  sVar3 = 0;
  if (0 < sVar1) {
    do {
      sVar2 = 0;
      do {
        FUN_0001ae56(psVar4[sVar3 + 1] + sVar2);
        sVar2 = sVar2 + 1;
      } while (sVar2 < 6);
      sVar3 = sVar3 + 1;
    } while (sVar3 < sVar1);
  }
  return;
}


/* Address 00020e8c */

void FUN_00020e8c(void)

{
  int iVar1;
  short sVar2;
  
  sVar2 = 0;
  do {
    FUN_00020cc4((&DAT_00049bb4)[sVar2]);
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x19);
  sVar2 = 0;
  do {
    (&DAT_00049d6e)[sVar2 * 0x67] = 1;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x28);
  sVar2 = 0;
  do {
    iVar1 = sVar2 * 0x1e;
    if (((&DAT_0004bd9c)[sVar2 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar1) != 0)) {
      FUN_0001545c(*(undefined4 *)((int)&DAT_0004bdb0 + iVar1));
    }
    (&DAT_0004bd9c)[sVar2 * 0xf] = 0;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x28);
  return;
}


/* Address 00020f0c */

void FUN_00020f0c(void)

{
  int iVar1;
  short sVar2;
  
  FUN_00020e40(DAT_00049c18);
  sVar2 = 0;
  do {
    (&DAT_00049d6e)[sVar2 * 0x67] = 1;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x28);
  sVar2 = 0;
  do {
    iVar1 = sVar2 * 0x1e;
    if (((&DAT_0004bd9c)[sVar2 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar1) != 0)) {
      FUN_0001545c(*(undefined4 *)((int)&DAT_0004bdb0 + iVar1));
    }
    (&DAT_0004bd9c)[sVar2 * 0xf] = 0;
    sVar2 = sVar2 + 1;
  } while (sVar2 < 0x28);
  return;
}


/* Address 00020f78 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00020f78(short param_1)

{
  short *psVar1;
  short *psVar2;
  short *psVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  short sVar8;
  int iVar9;
  
  if (param_1 == 1) {
    iVar9 = 0xbc01 - DAT_00049c56;
    iVar5 = (DAT_00049c50 + -1 >> 10) + -2;
    iVar4 = FUN_0000e60a(iVar5,0,5);
    iVar5 = FUN_0000e588(iVar5,0,5);
    iVar5 = iVar5 + ((iVar9 >> 10) + 2) * 0xd;
    sVar8 = 0;
    iVar9 = iVar5 * 0x1260 + 0x930;
    iVar5 = iVar5 + 0x2000;
    do {
      iVar6 = FUN_0001b044(iVar9,(short)((uint)iVar5 >> 0x10),(short)iVar5,0,0,0,0x1260,0,0);
      psVar1 = (short *)(iVar6 + iVar4 * 2);
      psVar2 = psVar1 + 1;
      FUN_00020b2a(*psVar1 + iVar6,(short)((uint)(&DAT_00049bb4)[sVar8] >> 0x10),
                   (short)(&DAT_00049bb4)[sVar8],*psVar2 - *psVar1);
      psVar3 = psVar1 + 2;
      FUN_00020b2a(*psVar2 + iVar6,(short)((uint)(&DAT_00049bb4)[(short)(sVar8 + 1)] >> 0x10),
                   (short)(&DAT_00049bb4)[(short)(sVar8 + 1)],*psVar3 - *psVar2);
      psVar2 = psVar1 + 3;
      FUN_00020b2a(*psVar3 + iVar6,(short)((uint)(&DAT_00049bb4)[(short)(sVar8 + 2)] >> 0x10),
                   (short)(&DAT_00049bb4)[(short)(sVar8 + 2)],*psVar2 - *psVar3);
      psVar3 = psVar1 + 4;
      FUN_00020b2a(*psVar2 + iVar6,(short)((uint)(&DAT_00049bb4)[(short)(sVar8 + 3)] >> 0x10),
                   (short)(&DAT_00049bb4)[(short)(sVar8 + 3)],*psVar3 - *psVar2);
      FUN_00020b2a(*psVar3 + iVar6,(short)((uint)(&DAT_00049bb4)[(short)(sVar8 + 4)] >> 0x10),
                   (short)(&DAT_00049bb4)[(short)(sVar8 + 4)],psVar1[5] - *psVar3);
      _DAT_00047b80 = 0;
      iVar9 = iVar9 + -0xeee0;
      iVar5 = iVar5 + -0xd;
      sVar8 = sVar8 + 5;
    } while (sVar8 < 0x19);
    DAT_00049c8c = 0xc;
    DAT_00049b8c = (short)DAT_00049c50 % 0x400 + 0x800;
    DAT_00049b8e = DAT_00049c54 + -0x20;
    DAT_00049b90 = (short)DAT_00049c56 % 0x400 + 0x800;
    _DAT_00049b92 = 0;
    _DAT_00049b94 = 0;
    _DAT_00049b96 = 0;
    FUN_00020c16();
    FUN_000102c4(4,0x9c4c);
    DAT_00049c60 = 1;
    FUN_00020aa0();
  }
  else if (param_1 == 2) {
    uVar7 = FUN_0001b044(DAT_00049c64 * 0x1260 + 0x591c90,DAT_00049c64 + 0x6000,0,0,0,0x1260,0,0);
    FUN_00020cf8(uVar7,(short)((uint)DAT_00049c18 >> 0x10),(short)DAT_00049c18,0x1260);
    _DAT_00047b80 = 0;
    DAT_00049b8c = DAT_00049c50._2_2_ - DAT_00049c6a._2_2_;
    DAT_00049b8e = DAT_00049c54 + -0x20;
    DAT_00049b90 = DAT_00049c56._2_2_ - DAT_00049c72._2_2_;
    _DAT_00049b92 = 0;
    _DAT_00049b94 = 0;
    _DAT_00049b96 = 0;
    FUN_00020d7c();
    FUN_00010520(4,0x9c4c);
    DAT_00049c60 = param_1;
    FUN_00020aa0();
  }
  return;
}


/* Address 00021242 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00021242(void)

{
  short sVar1;
  
  _DAT_0015ece0 = 0;
  _DAT_0015ed46 = 0;
  _DAT_0015edac = 0;
  sVar1 = 0;
  do {
    (&DAT_00049bb4)[sVar1] = sVar1 * 0x21c + 0x15b7c0;
    sVar1 = sVar1 + 1;
  } while (sVar1 < 0x19);
  DAT_00049c18 = 0x15b7c0;
  sVar1 = 0;
  do {
    (&DAT_00049d6c)[sVar1 * 0x67] = 0;
    sVar1 = sVar1 + 1;
  } while (sVar1 < 0x28);
  sVar1 = 0;
  do {
    (&DAT_0004bd9c)[sVar1 * 0xf] = 0;
    sVar1 = sVar1 + 1;
  } while (sVar1 < 0x28);
  _DAT_00047b80 = 0;
  _DAT_00047b82 = 0;
  FUN_0001aa40(0);
  FUN_0001aeda();
  FUN_0000ea20();
  FUN_0000f0c0();
  return;
}


/* Address 000212e8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first
   post-frame bytes match candidate. Body inferred from existing decoded flow; original
   boundary/name/ABI unverified. Evidence: [{"from":"0x21d24","bytes":"4eb9000212e8","assembly":"jsr
   $212e8.l"}] */

void observed_call_candidate_000212e8(void)

{
  short *psVar1;
  short *psVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  short *psVar17;
  short sVar18;
  undefined2 uVar19;
  undefined2 uVar20;
  undefined4 auStack_18 [6];
  
  auStack_18[4] = uRam00049c14;
  uVar3 = uRam00049c10;
  uVar4 = uRam00049c0c;
  uVar5 = uRam00049c08;
  uVar6 = uRam00049c04;
  uVar7 = uRam00049c00;
  uVar8 = uRam00049bf0;
  uVar9 = uRam00049bec;
  uVar10 = uRam00049bdc;
  uVar11 = uRam00049bd8;
  uVar12 = uRam00049bc8;
  auStack_18[0] = DAT_00049bc4;
  auStack_18[1] = DAT_00049bc0;
  auStack_18[2] = DAT_00049bbc;
  auStack_18[3] = DAT_00049bb8;
  uVar13 = DAT_00049bb4;
  do {
    if (DAT_00049c8c == 0xc) {
      DAT_00049bb4 = uVar13;
      DAT_00049bb8 = auStack_18[3];
      DAT_00049bbc = auStack_18[2];
      DAT_00049bc0 = auStack_18[1];
      DAT_00049bc4 = auStack_18[0];
      uRam00049bc8 = uVar12;
      uRam00049bd8 = uVar11;
      uRam00049bdc = uVar10;
      uRam00049bec = uVar9;
      uRam00049bf0 = uVar8;
      uRam00049c00 = uVar7;
      uRam00049c04 = uVar6;
      uRam00049c08 = uVar5;
      uRam00049c0c = uVar4;
      uRam00049c10 = uVar3;
      uRam00049c14 = auStack_18[4];
      return;
    }
    DAT_00049bb4 = uVar13;
    DAT_00049bb8 = auStack_18[3];
    DAT_00049bbc = auStack_18[2];
    DAT_00049bc0 = auStack_18[1];
    DAT_00049bc4 = auStack_18[0];
    uRam00049bc8 = uVar12;
    uRam00049bd8 = uVar11;
    uRam00049bdc = uVar10;
    uRam00049bec = uVar9;
    uRam00049bf0 = uVar8;
    uRam00049c00 = uVar7;
    uRam00049c04 = uVar6;
    uRam00049c08 = uVar5;
    uRam00049c0c = uVar4;
    uRam00049c10 = uVar3;
    uRam00049c14 = auStack_18[4];
    switch(DAT_00049c8c) {
    case 0:
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
      DAT_00049c8c = DAT_00049c8c + 5;
      auStack_18[0] = uVar6;
      auStack_18[1] = uVar5;
      auStack_18[2] = uVar4;
      auStack_18[3] = uVar3;
      sVar18 = 0x18;
      do {
        (&DAT_00049bb4)[sVar18] = (&DAT_00049bb4)[(short)(sVar18 + -5)];
        sVar18 = sVar18 + -1;
      } while (4 < sVar18);
      sVar18 = 0;
      DAT_00049bb4 = uVar6;
      DAT_00049bb8 = uVar5;
      DAT_00049bbc = uVar4;
      DAT_00049bc0 = uVar3;
      DAT_00049bc4 = auStack_18[4];
      do {
        FUN_00020cc4((short)((uint)auStack_18[sVar18] >> 0x10),(short)auStack_18[sVar18]);
        sVar18 = sVar18 + 1;
      } while (sVar18 < 5);
      sVar18 = 0;
      do {
        iVar15 = (int)sVar18;
        if ((short)(&DAT_00049dac)[iVar15 * 0x67] < 0x14) {
          (&DAT_00049dac)[iVar15 * 0x67] = (&DAT_00049dac)[iVar15 * 0x67] + 5;
        }
        else {
          (&DAT_00049d6e)[iVar15 * 0x67] = 1;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      sVar18 = 0;
      do {
        iVar15 = sVar18 * 0x1e;
        if (*(short *)(iVar15 + 0x4bdaa) < 0x14) {
          *(short *)(iVar15 + 0x4bdaa) = *(short *)(iVar15 + 0x4bdaa) + 5;
        }
        else {
          if (((&DAT_0004bd9c)[sVar18 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar15) != 0))
          {
            FUN_0001545c((short)((uint)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15) >> 0x10),
                         (short)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15));
          }
          (&DAT_0004bd9c)[sVar18 * 0xf] = 0;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      DAT_00049b90 = DAT_00049b90 + 0x400;
      iVar15 = 0xbc01 - DAT_00049c56;
      iVar14 = (DAT_00049c50 >> 10) + -2;
      if (-1 < iVar14) {
        iVar16 = FUN_0000e60a(iVar14,0,5);
        iVar14 = FUN_0000e588(iVar14,0,5);
        iVar14 = iVar14 + ((iVar15 >> 10) + 2) * 0xd;
        iVar15 = FUN_0001b044(iVar14 * 0x1260 + 0x930,iVar14 + 0x2000,0,0,0,0x1260,0,0);
        psVar1 = (short *)(iVar15 + iVar16 * 2);
        psVar2 = psVar1 + 1;
        FUN_00020b2a(*psVar1 + iVar15,(short)((uint)DAT_00049bb4 >> 0x10),(short)DAT_00049bb4,
                     *psVar2 - *psVar1);
        psVar17 = psVar1 + 2;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)DAT_00049bb8 >> 0x10),(short)DAT_00049bb8,
                     *psVar17 - *psVar2);
        psVar2 = psVar1 + 3;
        FUN_00020b2a(*psVar17 + iVar15,(short)((uint)DAT_00049bbc >> 0x10),(short)DAT_00049bbc,
                     *psVar2 - *psVar17);
        psVar17 = psVar1 + 4;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)DAT_00049bc0 >> 0x10),(short)DAT_00049bc0,
                     *psVar17 - *psVar2);
        sVar18 = psVar1[5] - *psVar17;
        uVar19 = (undefined2)((uint)DAT_00049bc4 >> 0x10);
        uVar20 = (undefined2)DAT_00049bc4;
code_r0x00021ce0:
        FUN_00020b2a(*psVar17 + iVar15,uVar19,uVar20,sVar18);
        _DAT_00047b80 = 0;
        FUN_00020c16();
        FUN_00020aa0();
      }
      break;
    case 10:
    case 0xb:
      DAT_00049c8c = DAT_00049c8c + 1;
      auStack_18[1] = uVar11;
      auStack_18[2] = uVar9;
      auStack_18[3] = uVar7;
      sVar18 = 0x18;
      do {
        iVar15 = (int)sVar18;
        sVar18 = sVar18 + -1;
        (&DAT_00049bb4)[iVar15] = (&DAT_00049bb4)[sVar18];
      } while (0 < sVar18);
      sVar18 = 0;
      DAT_00049bb4 = auStack_18[0];
      uRam00049bc8 = uVar11;
      uRam00049bdc = uVar9;
      uRam00049bf0 = uVar7;
      uRam00049c04 = auStack_18[4];
      do {
        FUN_00020cc4((short)((uint)auStack_18[sVar18] >> 0x10),(short)auStack_18[sVar18]);
        sVar18 = sVar18 + 1;
      } while (sVar18 < 5);
      sVar18 = 0;
      do {
        iVar15 = (int)sVar18;
        if ((short)(&DAT_00049dac)[iVar15 * 0x67] % 5 == 4) {
          (&DAT_00049d6e)[iVar15 * 0x67] = 1;
        }
        else {
          (&DAT_00049dac)[iVar15 * 0x67] = (&DAT_00049dac)[iVar15 * 0x67] + 1;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      sVar18 = 0;
      do {
        iVar15 = sVar18 * 0x1e;
        if (*(short *)(iVar15 + 0x4bdaa) % 5 == 4) {
          if (((&DAT_0004bd9c)[sVar18 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar15) != 0))
          {
            FUN_0001545c((short)((uint)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15) >> 0x10),
                         (short)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15));
          }
          (&DAT_0004bd9c)[sVar18 * 0xf] = 0;
        }
        else {
          *(short *)(iVar15 + 0x4bdaa) = *(short *)(iVar15 + 0x4bdaa) + 1;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      DAT_00049b8c = DAT_00049b8c + 0x400;
      iVar15 = (DAT_00049c50 + -1 >> 10) + -2;
      if ((-1 < iVar15) && (iVar14 = (0xbc00 - DAT_00049c56 >> 10) + -2, -1 < iVar14)) {
        iVar16 = FUN_0000e60a(iVar14,0,5);
        iVar14 = FUN_0000e588(iVar14,0,5);
        iVar14 = iVar14 + iVar15 * 10;
        iVar15 = FUN_0001b044(iVar14 * 0x1260 + 0x2be450,iVar14 + 0x4000,0,0,0,0x1260,0,0);
        psVar1 = (short *)(iVar15 + iVar16 * 2);
        psVar2 = psVar1 + 1;
        FUN_00020b2a(*psVar1 + iVar15,(short)((uint)uRam00049c04 >> 0x10),(short)uRam00049c04,
                     *psVar2 - *psVar1);
        psVar17 = psVar1 + 2;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049bf0 >> 0x10),(short)uRam00049bf0,
                     *psVar17 - *psVar2);
        psVar2 = psVar1 + 3;
        FUN_00020b2a(*psVar17 + iVar15,(short)((uint)uRam00049bdc >> 0x10),(short)uRam00049bdc,
                     *psVar2 - *psVar17);
        psVar17 = psVar1 + 4;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049bc8 >> 0x10),(short)uRam00049bc8,
                     *psVar17 - *psVar2);
        sVar18 = psVar1[5] - *psVar17;
        uVar19 = (undefined2)((uint)DAT_00049bb4 >> 0x10);
        uVar20 = (undefined2)DAT_00049bb4;
        goto code_r0x00021ce0;
      }
      break;
    case 0xd:
    case 0xe:
      DAT_00049c8c = DAT_00049c8c + -1;
      auStack_18[0] = uVar13;
      auStack_18[1] = uVar12;
      auStack_18[2] = uVar10;
      auStack_18[3] = uVar8;
      auStack_18[4] = uVar6;
      sVar18 = 0;
      do {
        iVar15 = (int)sVar18;
        sVar18 = sVar18 + 1;
        (&DAT_00049bb4)[iVar15] = (&DAT_00049bb4)[sVar18];
      } while (sVar18 < 0x18);
      sVar18 = 0;
      DAT_00049bc4 = uVar13;
      uRam00049bd8 = uVar12;
      uRam00049bec = uVar10;
      uRam00049c00 = uVar8;
      uRam00049c14 = uVar6;
      do {
        FUN_00020cc4((short)((uint)auStack_18[sVar18] >> 0x10),(short)auStack_18[sVar18]);
        sVar18 = sVar18 + 1;
      } while (sVar18 < 5);
      sVar18 = 0;
      do {
        iVar15 = (int)sVar18;
        if ((short)(((short)(&DAT_00049dac)[iVar15 * 0x67] / 5) * 5) ==
            (&DAT_00049dac)[iVar15 * 0x67]) {
          (&DAT_00049d6e)[iVar15 * 0x67] = 1;
        }
        else {
          (&DAT_00049dac)[iVar15 * 0x67] = (&DAT_00049dac)[iVar15 * 0x67] + -1;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      sVar18 = 0;
      do {
        iVar15 = sVar18 * 0x1e;
        if ((short)((*(short *)(iVar15 + 0x4bdaa) / 5) * 5) == *(short *)(iVar15 + 0x4bdaa)) {
          if (((&DAT_0004bd9c)[sVar18 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar15) != 0))
          {
            FUN_0001545c((short)((uint)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15) >> 0x10),
                         (short)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15));
          }
          (&DAT_0004bd9c)[sVar18 * 0xf] = 0;
        }
        else {
          *(short *)(iVar15 + 0x4bdaa) = *(short *)(iVar15 + 0x4bdaa) + -1;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      DAT_00049b8c = DAT_00049b8c + -0x400;
      iVar15 = DAT_00049c50 + 1;
      iVar14 = (0xbc00 - DAT_00049c56 >> 10) + -2;
      if (-1 < iVar14) {
        iVar16 = FUN_0000e60a(iVar14,0,5);
        iVar14 = FUN_0000e588(iVar14,0,5);
        iVar14 = iVar14 + ((iVar15 >> 10) + 2) * 10;
        iVar15 = FUN_0001b044(iVar14 * 0x1260 + 0x2be450,iVar14 + 0x4000,0,0,0,0x1260,0,0);
        psVar1 = (short *)(iVar15 + iVar16 * 2);
        psVar2 = psVar1 + 1;
        FUN_00020b2a(*psVar1 + iVar15,(short)((uint)uRam00049c14 >> 0x10),(short)uRam00049c14,
                     *psVar2 - *psVar1);
        psVar17 = psVar1 + 2;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049c00 >> 0x10),(short)uRam00049c00,
                     *psVar17 - *psVar2);
        psVar2 = psVar1 + 3;
        FUN_00020b2a(*psVar17 + iVar15,(short)((uint)uRam00049bec >> 0x10),(short)uRam00049bec,
                     *psVar2 - *psVar17);
        psVar17 = psVar1 + 4;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049bd8 >> 0x10),(short)uRam00049bd8,
                     *psVar17 - *psVar2);
        sVar18 = psVar1[5] - *psVar17;
        uVar19 = (undefined2)((uint)DAT_00049bc4 >> 0x10);
        uVar20 = (undefined2)DAT_00049bc4;
        goto code_r0x00021ce0;
      }
      break;
    case 0xf:
    case 0x10:
    case 0x11:
    case 0x12:
    case 0x13:
    case 0x14:
    case 0x15:
    case 0x16:
    case 0x17:
    case 0x18:
      DAT_00049c8c = DAT_00049c8c + -5;
      auStack_18[4] = uVar13;
      sVar18 = 0;
      do {
        (&DAT_00049bb4)[sVar18] = (&DAT_00049bb4)[(short)(sVar18 + 5)];
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x14);
      sVar18 = 0;
      uRam00049c04 = uVar13;
      uRam00049c08 = auStack_18[3];
      uRam00049c0c = auStack_18[2];
      uRam00049c10 = auStack_18[1];
      uRam00049c14 = auStack_18[0];
      do {
        FUN_00020cc4((short)((uint)auStack_18[sVar18] >> 0x10),(short)auStack_18[sVar18]);
        sVar18 = sVar18 + 1;
      } while (sVar18 < 5);
      sVar18 = 0;
      do {
        iVar15 = (int)sVar18;
        if ((short)(&DAT_00049dac)[iVar15 * 0x67] < 5) {
          (&DAT_00049d6e)[iVar15 * 0x67] = 1;
        }
        else {
          (&DAT_00049dac)[iVar15 * 0x67] = (&DAT_00049dac)[iVar15 * 0x67] + -5;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      sVar18 = 0;
      do {
        iVar15 = sVar18 * 0x1e;
        if (*(short *)(iVar15 + 0x4bdaa) < 5) {
          if (((&DAT_0004bd9c)[sVar18 * 0xf] != 0) && (*(int *)((int)&DAT_0004bdb0 + iVar15) != 0))
          {
            FUN_0001545c((short)((uint)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15) >> 0x10),
                         (short)*(undefined4 *)((int)&DAT_0004bdb0 + iVar15));
          }
          (&DAT_0004bd9c)[sVar18 * 0xf] = 0;
        }
        else {
          *(short *)(iVar15 + 0x4bdaa) = *(short *)(iVar15 + 0x4bdaa) + -5;
        }
        sVar18 = sVar18 + 1;
      } while (sVar18 < 0x28);
      DAT_00049b90 = DAT_00049b90 + -0x400;
      iVar15 = (DAT_00049c50 >> 10) + -2;
      if ((-1 < iVar15) && (iVar14 = (0xbbff - DAT_00049c56 >> 10) + -2, -1 < iVar14)) {
        iVar16 = FUN_0000e60a(iVar15,0,5);
        iVar15 = FUN_0000e588(iVar15,0,5);
        iVar15 = iVar15 + iVar14 * 0xd;
        iVar15 = FUN_0001b044(iVar15 * 0x1260 + 0x930,iVar15 + 0x2000,0,0,0,0x1260,0,0);
        psVar1 = (short *)(iVar15 + iVar16 * 2);
        psVar2 = psVar1 + 1;
        FUN_00020b2a(*psVar1 + iVar15,(short)((uint)uRam00049c04 >> 0x10),(short)uRam00049c04,
                     *psVar2 - *psVar1);
        psVar17 = psVar1 + 2;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049c08 >> 0x10),(short)uRam00049c08,
                     *psVar17 - *psVar2);
        psVar2 = psVar1 + 3;
        FUN_00020b2a(*psVar17 + iVar15,(short)((uint)uRam00049c0c >> 0x10),(short)uRam00049c0c,
                     *psVar2 - *psVar17);
        psVar17 = psVar1 + 4;
        FUN_00020b2a(*psVar2 + iVar15,(short)((uint)uRam00049c10 >> 0x10),(short)uRam00049c10,
                     *psVar17 - *psVar2);
        sVar18 = psVar1[5] - *psVar17;
        uVar19 = (undefined2)((uint)uRam00049c14 >> 0x10);
        uVar20 = (undefined2)uRam00049c14;
        goto code_r0x00021ce0;
      }
    }
    auStack_18[4] = uRam00049c14;
    uVar3 = uRam00049c10;
    uVar4 = uRam00049c0c;
    uVar5 = uRam00049c08;
    uVar6 = uRam00049c04;
    uVar7 = uRam00049c00;
    uVar8 = uRam00049bf0;
    uVar9 = uRam00049bec;
    uVar10 = uRam00049bdc;
    uVar11 = uRam00049bd8;
    uVar12 = uRam00049bc8;
    auStack_18[0] = DAT_00049bc4;
    auStack_18[1] = DAT_00049bc0;
    auStack_18[2] = DAT_00049bbc;
    auStack_18[3] = DAT_00049bb8;
    uVar13 = DAT_00049bb4;
  } while( true );
}


/* Address 00022780 */

undefined4 FUN_00022780(void)

{
  undefined4 in_D0;
  
  return in_D0;
}


/* Address 000227a0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_000227a0(short param_1,uint *param_2,int param_3)

{
  uint uVar1;
  short sVar2;
  char cVar3;
  char cVar4;
  uint *puVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  undefined4 in_D0;
  short sVar9;
  undefined4 in_D1;
  byte bVar11;
  int iVar10;
  uint uVar12;
  undefined4 *puVar13;
  undefined4 *puVar14;
  uint *puVar15;
  
  cVar3 = *(char *)param_2;
  if ((cVar3 == '\0') || (cVar3 == '\x01')) {
    uVar1 = *param_2;
    sVar2 = *(short *)(param_2 + 2);
    puVar15 = (uint *)((int)param_2 + 10);
    for (uVar12 = 0; (int)uVar12 < (int)sVar2; uVar12 = uVar12 + 1) {
      while ((cVar4 = *(char *)puVar15, cVar4 != '\x10' && (cVar4 != '\x11'))) {
        puVar15 = (uint *)((*puVar15 & 0xffffff) + (int)puVar15);
        if ((uint *)((int)param_2 + (uVar1 & 0xffffff)) <= puVar15) goto LAB_000228cc;
      }
      puVar5 = (uint *)((int)puVar15 + (*puVar15 & 0xffffff));
      puVar15 = puVar15 + 3;
      if (((uVar12 != 0) && (cVar3 == '\0')) && (cVar4 == '\x11')) {
        puVar14 = (undefined4 *)(param_3 + (uVar12 & 0xffff) * 0x1800);
        sVar9 = 0x5ff;
        puVar13 = puVar14 + -0x600;
        do {
          *puVar14 = *puVar13;
          sVar9 = sVar9 + -1;
          puVar13 = puVar13 + 1;
          puVar14 = puVar14 + 1;
        } while (sVar9 != -1);
      }
      for (; iVar8 = _DAT_000bd84c, puVar15 < puVar5;
          puVar15 = (uint *)((*puVar15 & 0xffffff) + (int)puVar15)) {
        cVar4 = *(char *)puVar15;
        bVar6 = cVar4 - 0x20;
        if (((-1 < (int)((uint)bVar6 << 0x18)) && ((char)bVar6 < '\x04')) &&
           (iVar7 = (*puVar15 & 0xffffff) - 4, iVar7 != 0)) {
          bVar11 = cVar4 - 0x1d;
          if (param_1 != 0) {
            bVar11 = cVar4 - 0x19;
          }
          puVar14 = (undefined4 *)(_DAT_000bd84c + 0xf037a0);
          *(uint *)(_DAT_000bd84c + 0xf0379c) = (uint)bVar11;
          *puVar14 = puVar15 + 1;
          iVar10 = (uVar12 & 0xffff) * 0x1800;
          if ((bVar6 & 2) != 0) {
            iVar10 = iVar10 + 0x800;
          }
          *(int *)(iVar8 + 0xf037a4) = param_3 + iVar10;
          *(int *)(iVar8 + 0xf037a8) = iVar7;
          FUN_000229f4();
        }
      }
    }
  }
LAB_000228cc:
  return CONCAT44(in_D0,in_D1);
}


/* Address 000228d4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000228d4(uint param_1,int param_2,uint *param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  uint *puVar8;
  byte bVar9;
  int iVar10;
  undefined4 in_D0;
  uint uVar11;
  int *piVar12;
  uint *puVar13;
  
  if ((*(char *)param_3 == '\0') || (*(char *)param_3 == '\x01')) {
    uVar2 = *param_3;
    sVar3 = *(short *)(param_3 + 2);
    puVar13 = (uint *)((int)param_3 + 10);
    for (uVar11 = 0; (int)uVar11 < (int)sVar3; uVar11 = uVar11 + 1) {
      while ((*(char *)puVar13 != '\x10' && (*(char *)puVar13 != '\x11'))) {
        puVar13 = (uint *)((*puVar13 & 0xffffff) + (int)puVar13);
        if ((uint *)((int)param_3 + (uVar2 & 0xffffff)) <= puVar13) {
          return in_D0;
        }
      }
      sVar4 = *(short *)((int)puVar13 + 10);
      sVar5 = *(short *)((int)puVar13 + 6);
      sVar6 = *(short *)(puVar13 + 2);
      sVar7 = *(short *)(puVar13 + 1);
      puVar8 = (uint *)((int)puVar13 + (*puVar13 & 0xffffff));
      for (puVar13 = puVar13 + 3; iVar10 = _DAT_000bd84c, puVar13 < puVar8;
          puVar13 = (uint *)((*puVar13 & 0xffffff) + (int)puVar13)) {
        bVar9 = *(char *)puVar13 - 0x30;
        if ((-1 < (short)((ushort)bVar9 << 8)) && ((char)bVar9 < '\x03')) {
          piVar12 = (int *)(_DAT_000bd84c + 0xf037a0);
          *(uint *)(_DAT_000bd84c + 0xf0379c) = (uint)bVar9;
          *piVar12 = param_2;
          *(uint *)(iVar10 + 0xf037a4) = param_1;
          *(uint *)(iVar10 + 0xf037a8) = (uint)(ushort)(sVar4 - sVar5);
          *(uint *)(iVar10 + 0xf037ac) = (uint)(ushort)(sVar6 - sVar7);
          iVar1 = param_4 + (uVar11 & 0xffff) * 0x1800;
          *(int *)(iVar10 + 0xf037b0) = iVar1;
          *(int *)(iVar10 + 0xf037b4) = iVar1 + 0x800;
          *(uint **)(iVar10 + 0xf037b8) = puVar13 + 1;
          FUN_000229f4();
          param_2 = (uint)(ushort)(sVar6 - sVar7) * (param_1 & 0xffff) + param_2;
        }
      }
    }
  }
  return in_D0;
}


/* Address 000229f4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000229f4(void)

{
  _DAT_000bd850 = 0;
  *(undefined4 *)(_DAT_000bd84c + 0xf03798) = 1;
  do {
    stop();
  } while (DAT_000bd850 == '\0');
  return;
}



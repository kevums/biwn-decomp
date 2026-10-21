/* Ghidra approximation. Not original source; validate against binary behavior. */
/* Language: 68000:BE:32:default */
/* Address 00180000 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: This function may have set the stack pointer */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void operator_selected_entry(void)

{
  char *pcVar1;
  short sVar2;
  char cVar3;
  char cVar4;
  undefined4 *puVar5;
  char *pcVar6;
  char *pcVar7;
  int extraout_A0;
  undefined4 *puVar8;
  
  _DAT_00f0210c = 0x70007;
  if ((_DAT_00f14002 & 0x10) == 0) {
    _DAT_00f00038 = 0xaf;
    _DAT_00f0003a = 0xaf;
    _DAT_00f00046 = 0x23;
  }
  else {
    _DAT_00f00038 = 0xc0;
    _DAT_00f0003a = 0xc0;
    _DAT_00f00046 = 0x26;
  }
  _DAT_00f0003c = 0x68c;
  _DAT_00f00048 = 0xffff;
  _DAT_00f00058 = 0;
  _DAT_00f0002a = 0;
  sVar2 = 500;
  puVar5 = &DAT_00180188;
  puVar8 = (undefined4 *)&DAT_00f03200;
  do {
    *puVar8 = *puVar5;
    sVar2 = sVar2 + -1;
    puVar5 = puVar5 + 1;
    puVar8 = puVar8 + 1;
  } while (sVar2 != -1);
  _DAT_00f03800 = 0;
  _DAT_001ffffc = 0x1800a2;
  func_0x00003048();
  _DAT_001ffffc = 0x1800aa;
  func_0x00003006();
  _DAT_001ffffc = 0x1800b4;
  func_0x00003060();
  _DAT_00f02110 = &DAT_00f03200;
  _DAT_00f02114 = 1;
  cVar3 = DAT_00002c03 + -1;
  pcVar7 = (char *)0x2c00;
  cVar4 = 'd';
  while (cVar3 = cVar3 + -1, cVar3 != '\0') {
    pcVar6 = pcVar7 + 8;
    pcVar1 = pcVar7 + 0xc;
    pcVar7 = pcVar6;
    if ((*pcVar1 == '\x01') && (*pcVar6 <= cVar4)) {
      cVar4 = *pcVar6;
    }
  }
  pcVar7 = (char *)0x2c00;
  do {
    do {
      pcVar6 = pcVar7 + 8;
      pcVar1 = pcVar7 + 0xc;
      pcVar7 = pcVar6;
    } while (*pcVar1 != '\x01');
  } while (*pcVar6 != cVar4);
  _DAT_001ffffc = 0x18015e;
  func_0x0000303c();
  do {
    _DAT_001ffffc = 0x180162;
    func_0x0000304e();
  } while (extraout_A0 < 0x100001);
  _DAT_001ffffc = 0x18016e;
  func_0x00003042();
  _DAT_00f03800 = 1;
  do {
  } while ((_DAT_00f02114 & 1) != 0);
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



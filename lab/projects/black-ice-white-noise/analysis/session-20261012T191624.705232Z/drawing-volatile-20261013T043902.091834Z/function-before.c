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



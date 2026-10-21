/* Address 0001b786 */

void FUN_0001b786(void)

{
  int iVar1;
  undefined *puVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  byte *pbVar6;
  undefined1 auStack_18 [24];
  
  drawing_word_00f02200_candidate = 0xb5130;
  drawing_word_00f02204_candidate = 0x33420;
  drawing_word_00f0220c_candidate = 0;
  drawing_word_00f02210_candidate = 0;
  drawing_word_00f02214_candidate = 0;
  drawing_word_00f02218_candidate = 0;
  drawing_word_00f02220_candidate = 0;
  drawing_word_00f0221c_candidate = 1;
  drawing_word_00f02224_candidate = 0x69a60;
  drawing_word_00f02228_candidate = 0x13420;
  drawing_word_00f02230_candidate = 0;
  drawing_word_00f02234_candidate = 0;
  drawing_word_00f0223c_candidate = 0x10780;
  drawing_word_00f02238_candidate = 0x1800601;
  FUN_0001b45a(auStack_18,&DAT_0001b780,DAT_00049d1e);
  FUN_000149ae(0x14,5,auStack_18,&DAT_000b5130,0x3420,&DAT_0004c3e0,0x7fc0,1);
  sVar5 = 0;
  sVar4 = 0x780;
  do {
    drawing_word_00f02200_candidate = (uint)(&DAT_000b5130 + sVar4 * 2);
    drawing_word_00f02204_candidate = 0x33420;
    drawing_word_00f0220c_candidate = 0;
    if ((short)(DAT_00049d54 + sVar5) % 10 == DAT_00049d56) {
      drawing_word_00f02224_candidate = 0x68260;
    }
    else {
      drawing_word_00f02224_candidate = 0x66a60;
    }
    drawing_word_00f02228_candidate = 0x13420;
    drawing_word_00f02230_candidate = 0;
    drawing_word_00f02234_candidate = 0;
    drawing_word_00f0223c_candidate = 0x10c00;
    drawing_word_00f02238_candidate = 0x9800609;
    drawing_word_00f02268_candidate = 0;
    drawing_word_00f0226c_candidate = 0;
    sVar3 = (short)(DAT_00049d54 + sVar5) % 10;
    iVar1 = *(int *)(&DAT_0006e6ac + (short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[sVar3]] * 4
                    );
    pbVar6 = &DAT_0006e6a0 + iVar1;
    if ((&DAT_00049d2c)[sVar3] != 0) {
      FUN_0000e2b8(&DAT_0006e6a0,(int)(short)(char)(&DAT_00042000)[(short)(&DAT_00049d2c)[sVar3]],
                   0x10a688);
      puVar2 = &DAT_000b5130 + sVar4 * 2;
      drawing_word_00f02200_candidate = (uint)puVar2;
      drawing_word_00f02204_candidate = 0x33420;
      drawing_word_00f0220c_candidate =
           (int)(short)(0x5e - (ushort)*pbVar6) |
           (uint)(ushort)(0x10 - ((byte)(&DAT_0006e6a1)[iVar1] >> 1)) << 0x10;
      drawing_word_00f02210_candidate = (int)(short)(0x60 - (ushort)*pbVar6);
      drawing_word_00f02224_candidate = 0x10a688;
      drawing_word_00f02228_candidate =
           (uint)(&PTR_s_hat_red_tape_encrusted_wad_of_bu_00030648_0x1d8_0003bd20)[*pbVar6] ^
           0x20000;
      drawing_word_00f02230_candidate = 0;
      drawing_word_00f0223c_candidate = (uint)*pbVar6 | (uint)(byte)(&DAT_0006e6a1)[iVar1] << 0x10;
      drawing_word_00f02238_candidate = 0x9800609;
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
    drawing_word_00f02200_candidate = (uint)(&DAT_000b5130 + sVar4 * 2);
    drawing_word_00f02204_candidate = 0x33420;
    drawing_word_00f0220c_candidate = 0xa0003;
    drawing_word_00f02210_candidate = 0x54;
    drawing_word_00f02224_candidate = (uint)(&PTR_DAT_000468a0)[(short)(DAT_00049d54 + sVar5) % 10];
    drawing_word_00f02228_candidate = 0x11c20;
    drawing_word_00f02230_candidate = 0;
    drawing_word_00f02234_candidate = 0;
    drawing_word_00f02268_candidate = 0;
    drawing_word_00f0226c_candidate = 0;
    drawing_word_00f0223c_candidate = 0xb000c;
    drawing_word_00f02238_candidate = 0x9800609;
    sVar4 = sVar4 + 0xc00;
    sVar5 = sVar5 + 1;
  } while (sVar5 < 5);
  return;
}



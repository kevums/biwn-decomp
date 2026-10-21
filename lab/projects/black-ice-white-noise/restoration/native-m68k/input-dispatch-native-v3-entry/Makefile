LAB_ROOT := $(abspath ../../../../..)
CROSS ?= $(LAB_ROOT)/tools/m68k-elf/bin/m68k-elf-
LIBGCC ?= $(LAB_ROOT)/tools/m68k-elf/m68000-soft/libgcc.a
BUILD ?= build
CFLAGS := -m68000 -msoft-float -std=c99 -Os -ffreestanding -ffunction-sections -fdata-sections -fno-common -fno-pie -fno-pic -fno-stack-protector -Wall -Wextra -Werror -I../..
.PHONY: all
all: $(BUILD)/native-input.bin
$(BUILD):
	mkdir -p $@
$(BUILD)/adapter.o: native-input.c | $(BUILD)
	$(CROSS)gcc $(CFLAGS) -c $< -o $@
$(BUILD)/dispatch.o: input-source.c ../../biwn_input_dispatch.h | $(BUILD)
	$(CROSS)gcc $(CFLAGS) -c $< -o $@
$(BUILD)/division.o: ../../biwn_signed_division.c ../../biwn_signed_division.h | $(BUILD)
	$(CROSS)gcc $(CFLAGS) -c $< -o $@
$(BUILD)/physical-call.o: physical-call.S | $(BUILD)
	$(CROSS)as -m68000 $< -o $@
$(BUILD)/entry.o: native-entry.S | $(BUILD)
	$(CROSS)as -m68000 $< -o $@
$(BUILD)/native-input.elf: $(BUILD)/adapter.o $(BUILD)/dispatch.o $(BUILD)/division.o $(BUILD)/physical-call.o $(BUILD)/entry.o native.ld Makefile $(LIBGCC)
	$(CROSS)ld --gc-sections -T native.ld -Map $(BUILD)/native-input.map -o $@ $(filter %.o,$^) $(LIBGCC)
$(BUILD)/native-input.bin: $(BUILD)/native-input.elf
	$(CROSS)objcopy -O binary $< $@

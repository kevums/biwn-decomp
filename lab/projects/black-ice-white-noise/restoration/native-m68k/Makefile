LAB_ROOT := $(abspath ../../../..)
CROSS ?= $(LAB_ROOT)/tools/m68k-elf/bin/m68k-elf-
BUILD ?= build
CFLAGS := -m68000 -msoft-float -std=c99 -O2 -ffreestanding -ffunction-sections -fdata-sections -fno-common -fno-pie -fno-pic -fno-stack-protector

.PHONY: all
all: $(BUILD)/button-digit.elf $(BUILD)/button-digit.bin

$(BUILD):
	mkdir -p $@

$(BUILD)/button-digit-shim.o: button-digit-shim.S | $(BUILD)
	$(CROSS)as -m68000 -o $@ $<

$(BUILD)/inventory-select.o: ../biwn_inventory_select.c ../biwn_inventory_select.h | $(BUILD)
	$(CROSS)gcc $(CFLAGS) -I.. -c $< -o $@

$(BUILD)/button-digit.elf: $(BUILD)/button-digit-shim.o $(BUILD)/inventory-select.o native.ld
	$(CROSS)ld --gc-sections -T native.ld -Map $(BUILD)/button-digit.map -o $@ $(BUILD)/button-digit-shim.o $(BUILD)/inventory-select.o

$(BUILD)/button-digit.bin: $(BUILD)/button-digit.elf
	$(CROSS)objcopy -O binary $< $@

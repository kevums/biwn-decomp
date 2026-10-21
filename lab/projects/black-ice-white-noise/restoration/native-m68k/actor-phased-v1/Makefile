LAB := $(abspath ../../../../..)
PREFIX := $(LAB)/tools/m68k-elf/bin/m68k-elf-
BUILD ?= build
MODULE ?= dispatch
ADDRESS ?= 0x190000
FLAGS := -m68000 -msoft-float -std=c11 -Os -ffreestanding -fno-builtin -fno-pie -fno-common -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -Wall -Wextra -Werror
.PHONY: all
all:
	mkdir -p "$(BUILD)"
	"$(PREFIX)gcc" $(FLAGS) -c $(MODULE).c -o "$(BUILD)/native.o"
	"$(PREFIX)gcc" -m68000 -c $(MODULE).S -o "$(BUILD)/shim.o"
	"$(PREFIX)gcc" $(FLAGS) -nostdlib -Wl,--gc-sections,--defsym,NATIVE_ADDRESS=$(ADDRESS),-T,$(MODULE).ld "$(BUILD)/shim.o" "$(BUILD)/native.o" -o "$(BUILD)/native.elf"
	"$(PREFIX)objcopy" -O binary "$(BUILD)/native.elf" "$(BUILD)/native.bin"
	"$(PREFIX)nm" -n "$(BUILD)/native.elf" > "$(BUILD)/symbols.txt"
	"$(PREFIX)objdump" -dr "$(BUILD)/native.elf" > "$(BUILD)/disassembly.txt"

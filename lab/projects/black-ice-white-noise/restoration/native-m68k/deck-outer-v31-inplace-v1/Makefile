LAB := $(abspath ../../../../..)
PREFIX := $(LAB)/tools/m68k-elf/bin/m68k-elf-
BUILD ?= build
ADDRESS ?= 0x180000
ARENA_ADDRESS ?= 0x130000
DECK_ADDRESS ?= 0x160000
FLAGS := -m68000 -msoft-float -std=c11 -Os -flto -ffreestanding -fno-builtin -fno-pie -fno-common -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -Wall -Wextra -Werror -D'inline=inline __attribute__((always_inline))'
.PHONY: all
all:
	mkdir -p "$(BUILD)"
	"$(PREFIX)gcc" $(FLAGS) -c native-outer.c -o "$(BUILD)/bridge.o"
	"$(PREFIX)gcc" -m68000 -c native-outer.S -o "$(BUILD)/shim.o"
	"$(PREFIX)gcc" $(FLAGS) -nostdlib -Wl,--gc-sections,--defsym,NATIVE_ADDRESS=$(ADDRESS),--defsym,OUTER_ARENA_BASE=$(ARENA_ADDRESS),--defsym,DECK_ARENA_BASE=$(DECK_ADDRESS),-T,native-outer.ld "$(BUILD)/shim.o" "$(BUILD)/bridge.o" -o "$(BUILD)/native-outer.elf"
	"$(PREFIX)objcopy" -O binary "$(BUILD)/native-outer.elf" "$(BUILD)/native-outer.bin"
	"$(PREFIX)nm" -n "$(BUILD)/native-outer.elf" > "$(BUILD)/symbols.txt"
	"$(PREFIX)objdump" -dr "$(BUILD)/native-outer.elf" > "$(BUILD)/disassembly.txt"

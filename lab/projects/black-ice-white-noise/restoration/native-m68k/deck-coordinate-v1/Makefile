LAB := $(abspath ../../../../..)
PREFIX := $(LAB)/tools/m68k-elf/bin/m68k-elf-
BUILD ?= build
ADDRESS ?= 0x180000
ARENA_ADDRESS ?= 0x160000
BODY := ../../experimental/deck-coordinate-local-v6-hybrid/deck-coordinate-hybrid.c
FLAGS := -m68000 -msoft-float -std=c11 -Os -flto -ffreestanding -fno-builtin -fno-pie -fno-common -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -Wall -Wextra -Werror -D'inline=inline __attribute__((always_inline))'
.PHONY: all
all:
	mkdir -p "$(BUILD)"
	"$(PREFIX)gcc" $(FLAGS) -I../../experimental/deck-coordinate-update-v2 -c "$(BODY)" -o "$(BUILD)/body.o"
	"$(PREFIX)gcc" $(FLAGS) -c native-deck.c -o "$(BUILD)/bridge.o"
	"$(PREFIX)gcc" -m68000 -c native-deck.S -o "$(BUILD)/shim.o"
	"$(PREFIX)gcc" $(FLAGS) -nostdlib -Wl,--gc-sections,--defsym,NATIVE_ADDRESS=$(ADDRESS),--defsym,DECK_ARENA_BASE=$(ARENA_ADDRESS),-T,native-deck.ld "$(BUILD)/shim.o" "$(BUILD)/bridge.o" "$(BUILD)/body.o" -o "$(BUILD)/native-deck.elf"
	"$(PREFIX)objcopy" -O binary "$(BUILD)/native-deck.elf" "$(BUILD)/native-deck.bin"
	"$(PREFIX)nm" -n "$(BUILD)/native-deck.elf" > "$(BUILD)/symbols.txt"
	"$(PREFIX)objdump" -dr "$(BUILD)/native-deck.elf" > "$(BUILD)/disassembly.txt"

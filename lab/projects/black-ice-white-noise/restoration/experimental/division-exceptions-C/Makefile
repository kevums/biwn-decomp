CC = clang
CFLAGS = -std=c99 -O2 -Wall -Wextra -Werror

all: build/libdivzero-entry.dylib

build/libdivzero-entry.dylib: biwn_divzero_entry.c ../../biwn_scheduler.h ../../biwn_world_update.h
	mkdir -p build
	$(CC) $(CFLAGS) -dynamiclib -I../.. biwn_divzero_entry.c -o $@

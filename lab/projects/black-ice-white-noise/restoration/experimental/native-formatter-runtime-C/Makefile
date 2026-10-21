CC := clang
CFLAGS := -std=c99 -O2 -Wall -Wextra -Werror -I../..
.PHONY: wait
wait: build/libGPU-wait-repair.dylib
build/libGPU-wait-repair.dylib: biwn_GPU_wait_repair.c
	mkdir -p build
	$(CC) $(CFLAGS) -dynamiclib $< -o $@

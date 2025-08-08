# Compiler and tools
CC = clang
F2C = f2c
TARGET = wasm32-wasip1

# Flags
CFLAGS = --target=$(TARGET) -D_WASI_EMULATED_SIGNAL -I$(SYSROOT)/include
LDFLAGS = -lf2c -lwasi-emulated-signal

# Source file (default to sine if SRC not specified)
SRC ?= sine 
FORTRAN_SRC = $(SRC).f 
C_SRC = $(SRC).c main.c
OUTPUT = $(SRC).wasm

# Default target
all: $(OUTPUT)

# Rule to convert Fortran to C
$(SRC).c: $(FORTRAN_SRC)
	$(F2C) $(FORTRAN_SRC)</dev/null
    
# Rule to compile C to WASM
$(OUTPUT): $(C_SRC)
	$(CC) $(CFLAGS) $(C_SRC) $(LDFLAGS) -o $(OUTPUT)

# Clean up generated files
clean:
	rm -f $(SRC).c $(OUTPUT)

# Run the WASM binary
run: $(OUTPUT)
	wasm $(OUTPUT)

.PHONY: all clean run
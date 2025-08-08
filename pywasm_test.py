import sys
import pywasm
import os
import types
import typing_extensions as typing

# Enable minimal logging
pywasm.log.lvl = 0  # Set to 1 for debugging

# Fix Pythonista3's sys.stdin/stdout/stderr
for sysstdstream, i, name in [(sys.stdin, 0, "<stdin>"), (sys.stdout, 1, "<stdout>"), (sys.stderr, 2, "<stderr>")]:
    if not hasattr(sysstdstream, 'errors'):
        sysstdstream.errors = 'strict'
    if not hasattr(sysstdstream, 'fileno'):
        sysstdstream._fileno = i
        sysstdstream.fileno = types.MethodType(lambda self: self._fileno, sysstdstream)
    if not hasattr(sysstdstream, 'name'):
        sysstdstream.name = name

# Custom Preview1 to debug fd_write
class CustomPreview1(pywasm.wasi.Preview1):
    def fd_write(self, m: pywasm.core.Machine, args: typing.List[int]) -> typing.List[int]:
        fd, iovs_ptr, iovs_len, nwritten_ptr = args
        print(f"fd_write called with fd={fd}, iovs_ptr={iovs_ptr}, iovs_len={iovs_len}, nwritten_ptr={nwritten_ptr}")
        if fd in (1, 2):  # stdout, stderr
            if not m.store.mems:
                print("Error: No memory instances available")
                return [28]  # EINVAL
            memory = m.store.mems[0].data
            total_written = 0
            for i in range(iovs_len):
                iov_ptr = iovs_ptr + i * 8
                buf_ptr = int.from_bytes(memory[iov_ptr:iov_ptr + 4], byteorder='little')
                buf_len = int.from_bytes(memory[iov_ptr + 4:iov_ptr + 8], byteorder='little')
                data = memory[buf_ptr:buf_ptr + buf_len]
                print(data.decode('utf-8', errors='ignore'), end='')
                total_written += buf_len
            memory[nwritten_ptr:nwritten_ptr + 4] = total_written.to_bytes(4, byteorder='little')
            sys.stdout.flush()  # Ensure output is displayed
            return [0]
        return [28]  # EINVAL

# Path to your .wasm file (update for sine.wasm as needed)
wasm_file = '/private/var/mobile/Containers/Data/Application/7FF24350-641A-41A9-8B89-82C94A80B7AD/Documents/sine.wasm'
# For sine.wasm: wasm_file = '/private/var/mobile/Containers/Data/Application/7FF24350-641A-41A9-8B89-82C94A80B7AD/Documents/sine.wasm'

# Configure WASI Preview1
wasi_args = ["sine.wasm"]  # For sine.wasm: ["sine.wasm"] or ["sine.wasm", "1.0"]
wasi_dirs = {}  # Disable file system
wasi_envs = {"PATH": "/usr/bin", "TERM": "xterm"}

# Create runtime and bind custom WASI Preview1
runtime = pywasm.core.Runtime()
wasi = CustomPreview1(args=wasi_args, dirs=wasi_dirs, envs=wasi_envs)
wasi.bind(runtime)

try:
    m = runtime.instance_from_file(wasm_file)
    if not hasattr(m, 'exps'):
        raise AttributeError("ModuleInst has no 'exps' attribute")
    exports = m.exps
    export_names = [e.name for e in exports if hasattr(e, 'name')]
    print("Available exports:", export_names)
    entry_point = '_start'
    if entry_point not in export_names:
        raise ValueError(f"Entry point '{entry_point}' not found in exports: {export_names}")
    r = runtime.invocate(m, entry_point, [])
    print(f"Return value: {r}")
except Exception as e:
    print(f"Error during execution: {type(e)} {e}", file=sys.stderr)
    raise e  # Re-raise for full traceback

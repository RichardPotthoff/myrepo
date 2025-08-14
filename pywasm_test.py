import sys,os
import platform_darwin
import pywasm

# Enable minimal logging
pywasm.log.lvl = 0  # Set to 1 for debugging
root_dir='/private/var/mobile/Containers/Data/Application/7FF24350-641A-41A9-8B89-82C94A80B7AD/Documents'
# Path to your .wasm file (update for sine.wasm as needed)
#wasm_file_name='file_open_example'
wasm_file_name='sine'
wasm_file = root_dir+f'/{wasm_file_name}.wasm'

#if os.path.exists(root_dir+'/mydata.txt'):
#  os.remove(root_dir+'/mydata.txt')

# Configure WASI Preview1
wasi_args = [f"{wasm_file_name}.wasm"]
wasi_dirs = {'/':root_dir}  # Disable file system
wasi_envs = {"PATH": "/bin", "TERM": "xterm"}

# Create runtime and bind WASI Preview1
runtime = pywasm.core.Runtime()
print()
wasi = pywasm.wasi.Preview1(args=wasi_args, dirs=wasi_dirs, envs=wasi_envs)
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


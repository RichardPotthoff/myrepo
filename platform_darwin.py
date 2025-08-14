import sys,os,io
import types

# Fix Pythonista3's sys.stdin/stdout/stderr
for sysstdstream, i, name in [(sys.stdin, 0, "stdin"), (sys.stdout, 1, "stdout"), (sys.stderr, 2, "stderr")]:
    try:
      _ = sysstdstream.errors
    except (io.UnsupportedOperation, AttributeError):
      sysstdstream.errors='strict'
    try:
      _ = sysstdstream.fileno()
    except (io.UnsupportedOperation, AttributeError):
        sysstdstream._fileno = i
        sysstdstream.fileno = types.MethodType(lambda self: self._fileno, sysstdstream)
    try:
      _ = sysstdstream.name
    except  (io.UnsupportedOperation, AttributeError):
      sysstdstream.name = name
      
_os_write=os.write
def os_write(fd,data):
  file = {1:sys.stdout,2:sys.stderr}.get(fd,None)
  if file:
    print(data.decode('utf-8', errors='ignore'), end='',file=file)
    file.flush()
    return len(data)
  else:
    return _os_write(fd,data)
   
os.write=os_write

import platform
platform.system=lambda:'Darwin'


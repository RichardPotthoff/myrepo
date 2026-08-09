# ppdb.py: applies a monkey-patch to the pdb module (command line debugger) for use with Pythonista
# This allows to use the "exit" command to exit (Pdb)'s *interactive* mode.
# This solves a problem with consoles that cannot enter EOF (ctrl D) 
# Just import this module before running the debugger. 

import pdb
import sys

_original_readline = sys.stdin.readline

def ipad_safe_readline(*args, **kwargs):
    line = _original_readline(*args, **kwargs)
    if line.strip() == "exit":
        return ""  # Send clean EOF signal to exit 'interact'
    return line

# 1. Store the original Pdb command loop methods
_original_cmdloop = pdb.Pdb.cmdloop
_original_postloop = pdb.Pdb.postloop

def custom_cmdloop(self, *args, **kwargs):
    # Enforce our iPad-safe stream right as the Pdb prompt starts
    sys.stdin.readline = ipad_safe_readline
    return _original_cmdloop(self, *args, **kwargs)

def custom_postloop(self, *args, **kwargs):
    # Restore the original Pythonista stream the exact moment Pdb exits
    sys.stdin.readline = _original_readline
    return _original_postloop(self, *args, **kwargs)

# 2. Apply the persistent Pdb life-cycle patches
pdb.Pdb.cmdloop = custom_cmdloop
pdb.Pdb.postloop = custom_postloop

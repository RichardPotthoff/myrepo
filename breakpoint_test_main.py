if '_debug_main' in locals():
    #print source code of Pythonista's debugger
    import inspect, pythonista_debug 
    print('-'*5,'Source code in ',pythonista_debug.__file__,':\n')
    print(inspect.getsource(pythonista_debug))
    print('-'*80)
    print()
    
    #set additional, breakpoints in other files
    from debugger import debugger as d
    breakpoints=[('./breakpoint_test_module.py', [3,]  ),
                 ('./breakpoint_test_module.py', 4 ),
                 (__file__,34),
                ]
    for filename,breaklines in breakpoints:
      filepath=d.canonic(filename)
      if not hasattr(breaklines,'__iter__'):
          breaklines=[breaklines]
      for breakline in breaklines:
          d.set_break(filepath,breakline) 
    
    print('List of breakpoints:')
    for filepath,breaklines in d.breaks.items():
      print(filepath, breaklines)
    print()

import sys,os,pathlib,inspect
import breakpoint_test_module
print('List of command line arguments:')
for i, arg in enumerate(sys.argv):
    print(f'arg{i:2}={arg}')
print()
print('Test start:')
print(f'Line {inspect.currentframe().f_lineno} in "{pathlib.Path(__file__).relative_to(os.getcwd())}"')
breakpoint_test_module.f1(12)
print(f'Line {inspect.currentframe().f_lineno} in "{pathlib.Path(__file__).relative_to(os.getcwd())}"')
print('Test complete!')


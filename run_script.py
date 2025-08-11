import sys, runpy
saved_argv=sys.argv
try:
  script_path=sys.argv[1]
  sys.argv=sys.argv[1:]
  print("'run_script.py': Executing " '"' f"runpy.run_path('{script_path }',run_name='__main__')" '".')
  runpy.run_path(script_path,run_name='__main__')
  print( "'run_script.py': Finished!")
except Exception as e: print(e,file=sys.stderr)
finally: sys.argv=saved_argv

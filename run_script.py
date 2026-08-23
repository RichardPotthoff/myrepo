import os, sys, runpy
saved_argv=sys.argv
saved_path=sys.path
saved_cwd=os.getcwd()
try:
  script_path=sys.argv[1]
  script_home=os.path.dirname(script_path)
  #print(f'run_script(original): {sys.argv=}')
  sys.argv=sys.argv[1:]#there seems to be an extra argument appended at the end when called from pythonista tools
  sys.path=[script_home]+saved_path
  #print(f'run_script(shifted): {sys.argv=}')
  os.chdir(script_home)
  print("'run_script.py': Executing " '"' f"runpy.run_path('{script_path }',run_name='__main__')" '".')
  runpy.run_path(script_path,run_name='__main__')
  print( "'run_script.py': Finished!")
except Exception as e: print(e,file=sys.stderr)
finally: 
  sys.argv=saved_argv
  sys.path=saved_path
  if saved_cwd: os.chdir(saved_cwd)
  

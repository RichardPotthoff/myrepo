import sys, os, shutil, pathlib, shlex

try:
  import PIP_TARGET
except ImportError:
  print('Module "PIP_TARGET.py" missing in "site-packages(user)"!\n\n'
        'Add an empty file named "PIP_TARGET.py" to "site-packages(user)". \n'
        'This file acts as a tag that marks the target directory for the\n'
        'commands "pip" and "clone".',file=sys.stderr)
  sys.exit(1)
pip_packages_path=os.path.dirname(PIP_TARGET.__file__)
os.environ['PIP_TARGET']=pip_packages_path

cloned_packages_path=pip_packages_path
try:
  import CLONE_TARGET
  cloned_packages_path=os.path.dirname(CLONE_TARGET.__file__)
except ImportError: pass

def clone_selected(src, dst, selected, logging=False):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    if logging: print(f'\nCopying {len(selected)} items:') 
    for i,item in enumerate(selected):
      if logging: print(f'{i+1:5d}: {item:30}',end='')
      try:
        src_path = src / item
        dst_path = dst / item
        if os.path.exists(dst_path):
          if logging: print("can't overwrite existing item",file=sys.stderr)
        elif src_path.is_dir():
          shutil.copytree(src_path, dst_path,copy_function=shutil.copy)
          if logging: print("O.K.")
        elif src_path.is_file():
          shutil.copy(src_path, dst_path)
          if logging: print("O.K.")
        else:
          if logging: print("source item invalid",file=sys.stderr)
      except Exception as e:
        if logging:
          print()
          print(e,file=sys.stderr)

def sh_cmd(cmdln):
  if not cmdln:
    return
  saved_argv=sys.argv
  sys.argv=shlex.split(cmdln)
  cmd,*args=sys.argv
  try:
    if   'pip'  ==cmd:
                       from pip._internal.cli.main import main as _main
                       try:
                         return(_main())
                       except BaseException: 
                         return -1
    elif 'clone'==cmd: clone_selected(src=os.getcwd(),dst=cloned_packages_path,selected=args,logging=True);return 0
    elif 'ls'   ==cmd: print('\n',' \n '.join(map(shlex.quote,sorted(os.listdir(*args)))),' ');  return 0
    elif 'cd'   ==cmd: os.chdir(*args); return 0
    elif 'quit' ==cmd: sys.exit()
    elif 'exit' ==cmd: sys.exit()
    else:
      print(f"sh_cmd: {cmd}: command not found",file=sys.stderr)
      return -1 
  finally:
    sys.argv=saved_argv

def sh():
  print(
  'Command List:\n'
  '  pip: This is the standard Python pip command.\n'
  '       If "pip" is not yet installed, copy "pip_sh.py" to a remote share that\n'
  '       contains an installed "pip" module (e.g. on a shared remote drive) to\n'
  '       bootstrap the installation of "pip" (using the command: "pip install pip").\n'
  '       Running "pip" from a remote shared drive may be slow (~30s to install pip),\n'
  '       so it should be avoided once "pip" is installed locally.\n'
  'clone: This command copies a list of files/directories from the "cwd" (current\n'
  '       working directory) to "site-packages(user)" (PIP_TARGET), or to a directory\n'
  '       with a file "CLONE_TARGET.py" (the directories have to be on the "sys.path"\n'
  '       search path so Python can find them).\n'
  '       Tip 1: Copy/paste the filenames from the "ls" output to the input line.\n'
  '              (Line breaks in the pasted text are not a problem.)\n'
  '       Tip 2: Copy "pip_sh.py" to a remote shared drive, and run it from there.\n'
  '              (The initial "cwd" is the parent directory of the script being run.)\n'
  '   ls: List an alphabetically sorted list of files/directories of the "cwd".\n' 
  '   cd: Change the "cwd".\n'
  ' exit: exit "pip_sh".\n'
  )
  
  while True:
    try:
      cwd=os.path.basename(os.getcwd())
      cmdln=input(f'\npip_sh:{cwd} $ ')
      sh_cmd(cmdln)
    except Exception as e:
      print(e)
    except BaseException:
      break 
      
if __name__=='__main__':
  sh()


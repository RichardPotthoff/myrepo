import sys, os, pathlib, shutil, shlex, runpy, types, pprint
pprint, pp = [pprint.pprint] * 2

try:
  import platform_darwin, ppdb #patches required only for some commands
except:
  pass 
  
sh_name=os.path.splitext(os.path.basename(__file__))[0] if '__file__' in locals() else 'pip_sh'

def help_text(): return ('\n'
  'List of Commands:\n\n'
  '  pip: This is the standard Python pip command.\n'
  '       If "pip" is not yet installed, copy "pip_sh.py" to a remote share that\n'
  '       contains an installed "pip" module (e.g. on a shared remote drive) to\n'
  '       bootstrap the installation of "pip", using the command: "pip install pip".\n'
  '       Running "pip" from a remote shared drive may be slow (~30s to install pip),\n'
  '       so it should be avoided once "pip" is installed locally.\n'
  '       Tip 1: It may be easier to just create a new empty script in Pythonista on the, \n'
  '              remote drive and hit "run" in Pythonista. Here is an example path of a file\n'
  '              that has been created in this way:\n'
  '              "/private/var/mobile/Library/LiveFiles/com.apple.filesystems.smbclientd/\n'
  '               oRJK7QPythonista/lib/python3.10/site-packages/remotePC_sh.py"\n'      
  '\n'
  'clone: This command copies a list of files/directories from the "cwd" (current\n'
  '       working directory) to "site-packages(user)" (PIP_TARGET), or to a directory\n'
  '       with a file "CLONE_TARGET.py" (the directories have to be on the "sys.path"\n'
  '       search path so Python can find them).\n'
  '       Tip 2: Copy/paste the filenames from the "ls" output to the input line.\n'
  '              (Line breaks in the pasted text are not a problem.)\n'
  '       Tip 3: Copy "pip_sh.py" to a remote shared drive, and run it from there.\n'
  '              (The initial "cwd" is the parent directory of the script being run.)\n'
  '\n'
  '   ls: List an alphabetically sorted list of files/directories of the "cwd".\n' 
  '\n'
  '   cd: Change the "cwd".\n'
  '\n'
  '    !: execute a Python statement. E.g. "!pp(sys.path)" will print the current Python path.\n'
  '\n'
 f" exit: Exit '{sh_name}'.\n"
 '\n'
  ' help: This help text.\n'
  '\n'
  ) 
  
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

def sh_engine(cloned_packages_path):
    """
    The Core Shell State Machine. 
    It yields the current prompt token and receives the next command via .send()
    """
    quit_shell = False
    while not quit_shell:
        try:
            cwd = os.path.basename(os.getcwd())
            prompt_token = f"{sh_name}:{cwd} $ "
            
            # --- THE TWO-WAY STREET ---
            # 1. We yield the prompt out to the runner
            # 2. We pause and wait for the runner to .send(cmdln) back in
            cmdln = yield prompt_token
            
            if not cmdln:
                continue
                
            shell_main = sys.modules.get("__main__") 
            saved_argv = sys.argv
            sys.argv = shlex.split(cmdln)
            cmd, *args = sys.argv
            
            try:
                if cmd.startswith('!'): 
                    exec((cmdln[1:]).lstrip())
                elif 'clone' == cmd: 
                    clone_selected(src=os.getcwd(), dst=cloned_packages_path, selected=args, logging=True)
                elif 'ls' == cmd: 
                    print('\n', ' \n '.join(map(shlex.quote, sorted(os.listdir(*args)))), '\n')
                elif 'cd' == cmd: 
                    os.chdir(*args)
                elif 'help' == cmd: 
                    print(help_text(), end='\n\n')
                elif 'quit' == cmd or 'exit' == cmd: 
                    quit_shell = True
                else:
                    try:
                        import importlib.util
                        from types import ModuleType
                        
                        # 1. Look up the command module profile via sys.path specs
                        spec = importlib.util.find_spec(cmd)
                        
                        if spec and spec.origin:
                            origin_path = spec.origin
                            module_name = spec.name
                            
                            # 💡 THE PACKAGE DISCOVERY STEP:
                            # If the spec points to an __init__.py file, this is an executable package folder!
                            if os.path.basename(origin_path) == '__init__.py':
                                package_dir = os.path.dirname(origin_path)
                                main_script_path = os.path.join(package_dir, '__main__.py')
                                
                                # Verify the package actually contains a runnable entry script
                                if os.path.exists(main_script_path):
                                    origin_path = main_script_path
                                    # Update name to accurately simulate running via 'python -m package'
                                    module_name = f"{spec.name}.__main__"
                                else:
                                    print(f"sh: package '{cmd}' is not an executable module (missing __main__.py)")
                                    origin_path = None
                                    
                            if origin_path:
                                with open(origin_path, 'r', encoding='utf-8') as f:
                                    script_code = f.read()
                                
                                parent_package = spec.name # Map parent package path context
                                
                                # Create our safe virtual isolated sys configuration object
                                isolated_sys = ModuleType('sys')
                                isolated_sys.__dict__.update(sys.__dict__) 
                                isolated_sys.argv = [origin_path] + args
                                
                                # Build the virtual environment sandbox namespace
                                sandbox_globals = {
                                    '__name__': '__main__',        # Triggers standard executable hooks
                                    '__file__': origin_path,       # Injects runtime path mapping
                                    '__package__': parent_package, # Preserves cross-module package relationships
                                    '__spec__': spec,              
                                    'sys': isolated_sys,           # Safe local command argument virtualization
                                    '__builtins__': __builtins__,
                                }
                                
                                # Execute the script safely inside our thread-insulated framework
                                exec(script_code, sandbox_globals)
                        else:
                            print(f"sh: command not found: {cmd}")
                            
                    except Exception as script_err:
                        print(f"Error running script:\n{script_err}")
                            
            except Exception as e: 
                print(e, file=sys.stderr)
            except BaseException: 
                pass
            finally: 
                if shell_main:
                    sys.modules["__main__"] = shell_main 
                sys.argv = saved_argv
                
        except Exception as e: 
            print(e, file=sys.stderr)
        except BaseException:  
            break
            
    if quit_shell: 
        raise KeyboardInterrupt

def run_shell():
    """
    The Drive Loop / Interface Layer.
    Responsible ONLY for capturing real-world I/O and stepping the generator.
    """
    saved_cwd = os.getcwd() 
    try:
        os.chdir(os.path.dirname(__file__))
    except Exception as e:
        print(e, file=sys.stderr)
        
    print(help_text())
    
    # Initialize the generator coroutine
    engine = sh_engine(cloned_packages_path)
    
    # Prime the generator (advances execution to the first yield statement)
    prompt = next(engine) 
    
    while True:
        try:
            cmdln = input(prompt)
            # Send the text input straight back into the waiting yield expression
            prompt = engine.send(cmdln)
        except StopIteration:
            break
        except KeyboardInterrupt:
            break

    os.chdir(saved_cwd) 
    print(f"\nKeyboard interrupt received, exiting '{sh_name}'. ")

if __name__ == '__main__':
    if len(sys.argv) > 1: 
        sh_name = sys.argv[1]
    run_shell()


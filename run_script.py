import importlib.util
import sys
import os
modulefilepath=sys.argv[1]
print(modulefilepath)
moduledir,modulefile=os.path.split(modulefilepath)
modulename='__main__'
spec = importlib.util.spec_from_file_location(modulename, modulefilepath)
module = importlib.util.module_from_spec(spec)
sys.modules[modulename] = module
os.chdir(moduledir)
sys.argv=sys.argv[1:]
spec.loader.exec_module(module)


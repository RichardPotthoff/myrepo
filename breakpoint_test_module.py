import os, pathlib, inspect
def f1(x):
  print(f'Line {inspect.currentframe().f_lineno} in "{pathlib.Path(__file__).relative_to(os.getcwd())}"')
  print(f'Line {inspect.currentframe().f_lineno} in "{pathlib.Path(__file__).relative_to(os.getcwd())}"')
  print(x)

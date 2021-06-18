from typing import Iterator
class arrayfunction(object):
  def __init__(self,y):
    object.__init__(self)
    self.y=y
  def __call__(self,*args,**kwargs):
    return self.y(*args,**kwargs)
  def __getitem__(self,*args,**kwargs):
    return self.__call__(*args,**kwargs)
    
@arrayfunction  
def y(i):
  return i**2
  
def fib(n: int) -> Iterator[int]:
    a, b = 0, 1
    while a < n:
        yield a
        a, b = b, a+b  
        
for i in range(10):print(i,y(i),y[i])


import inspect
class BaseModel:
  def __init__(self, **data):
      self.__dict__.update( (k, type(v)(v)) for k,v in inspect.getmembers(self) if type(v) is list)
      self.__dict__.update(data)  
def root_validator(*args,**kwargs):
  return lambda f:f


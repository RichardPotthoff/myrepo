from matplotlib import pyplot as plt
import numpy as np
class Figure:
    def __init__(self,*args,**kwargs):
      plt.clf()
      self.fig=plt.figure()
      self.ax=self.fig.add_subplot(projection='3d')
      self.tracecount=0

    def show(self,*args,**kwargs):
      limits = np.array([getattr(self.ax, f'get_{axis}lim')() for axis in 'xyz'])
      self.ax.set_box_aspect(np.ptp(limits, axis = 1))
      #self.fig.show()
      #print(f'"plotly" is not installed!\n Skipping plotly.Figure.show().')
      #print(f'{self.tracecount=}')
      pass
    def add_trace(self,trace,*args,**kwargs):
      def rgb(r,g,b):
        return r/255,g/255,b/255
      scope=locals()
      if type(trace) is Scatter3d:
        if trace.data['mode']=='lines':
          self.tracecount+=1
          x,y,z,line=(trace.data[c] for c in ('x','y','z','line'))
          n=len(x)
          dn=100
          for i in range(0,n-1,dn):
            i2=min(n,i+dn+1)
            self.ax.plot3D(x[i:i2],y[i:i2],z[i:i2],c=eval(line['color'][i],scope))
      pass
    def update_layout(self,*args,**kwargs):
      pass
class Mesh3d:
  def __init__(self,*args,**kwargs):
    pass
class Scatter3d:
  def __init__(self,*args,**kwargs):
    self.data=kwargs
     

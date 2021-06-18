import numpy as np
from pylab import *
class AffineTransform(np.matrix):
  def __new__(cls,a=1.0,b=0.0,c=0.0,d=1.0,e=0.0,f=0.0):
    return np.matrix.__new__(cls,[[a,b,e],[c,d,f],[0.0,0.0,1.0]]).transpose()
  def rotate(self,angle=0):
    sincos=np.exp(1j*angle)
    self[:2,:2]*=[[sincos.real,sincos.imag],[-sincos.imag,sincos.real]]
    return self
  def scale(self,s):
    if hasattr(s,'__len__'):
      self[:2,:2]*=np.diag(s)
    else:
      self[:2,:2]*=s
    return self
  def shift(self,p):
    self[2,:2]+=matrix(p)
    return self
    
M=[AffineTransform().scale([0.003,-0.17]).shift([0,1.7]),
   AffineTransform().scale(0.85).rotate(-2.7*pi/180).shift([0,1.6]),
   AffineTransform().scale([0.30,0.34]).rotate(50*pi/180).shift([0,1.6]),
   AffineTransform().scale([-0.27,0.34]).rotate(-55*pi/180).scale([1.0,1.15]).shift([0,0.44])]         
p = np.cumsum([0.02, 0.78, 0.1, 0.1])    #probabilities for each affine transformation        
#p = np.cumsum([0.25, 0.25, 0.25, 0.25])    #probabilities for each affine transformation        

n=100000
points=np.zeros((n,3))
x=[0.0,0.0,1.0]
for i in range(1,n):
  x=x*M[np.searchsorted(p,np.random.rand())]
  points[i]=x
print("BarnsleyFern, %d points"%n) 
plot(points[:,1],-points[:,0],marker='.',linestyle='none',color='green',markersize=1)

axis('off')
axes().set_aspect('equal', 'datalim')	
subplots_adjust(left=0, right=1, top=1, bottom=0)
show()
xmax,ymax,_=np.max(points,0)
xmin,ymin,_=np.min(points,0)
for MM in M+[AffineTransform(1,0,0,1,0,0)]:
  box=([[xmin,ymin,1],[xmin,ymax,1],[xmax,ymax,1],[xmax,ymin,1],[xmin,ymin,1]]*MM)
  plot(box[:2,1],-box[:2,0],color='blue',linestyle='solid',linewidth=1)    
  plot(box[1:,1],-box[1:,0],color='red',linestyle='solid',linewidth=1)         
show()


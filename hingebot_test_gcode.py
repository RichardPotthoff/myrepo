import numpy as np
from matplotlib import pyplot as plt
from cmath import pi,acos,exp,sqrt
def Arc(P0,n0,l,da,*args,tol=0.001,**kwargs):
  if l==0:
    return
  x=np.linspace(0,l,max(2,int(abs(6*(da/(2*pi)))),int(l//(2*abs(2*l/da*tol)**0.5)+1))if (da!=0) and (l!=0) else 2)
  phi2=x/l*da/2
  p=P0+x*np.sinc(phi2/pi)*n0*np.exp(1j*phi2)
  return p.real,p.imag
r=100.0
n=100
phi=2*pi*n
X,Y=Arc(r+0j,1j,r*phi,phi,tol=0.01)
x0,y0=100,100
X+=x0
Y=Y+y0
plt.plot(X,Y,'.')
plt.gca().set_aspect('equal')
plt.show()
f=60*60
gcodefile='hingebot_test.gcode'
fo=open(gcodefile,'w')
for x,y in zip(X,Y):
    s=f'G1 X{x:.3f} Y{y:.3f} F{f:.3f}\n'
    fo.write(s)
fo.close()

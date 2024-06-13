import numpy as np
from matplotlib import pyplot as plt
import math
from math import pi,sin,cos,sqrt
from cmath import exp
deg=pi/180

def plotArc(ax,P0,n0,l,da,*args,tol=0.001,**kwargs):
  if l==0:
    return
  x=np.linspace(0,l,max(2,int(abs(6*(da/(2*pi)))),int(l//(2*abs(2*l/da*tol)**0.5)+1))if (da!=0) and (l!=0) else 2)
  phi2=x/l*da/2
  p=P0+x*np.sinc(phi2/pi)*n0*np.exp(1j*phi2)
  ax.plot(p.real,p.imag,*args,**kwargs)
class HingebotKinematics:
    def __init__(self,anchors):
      self.anchors=anchors
    def calc_position(self, stepper_positions):
        def sss(c,a,b):#triangle with 3 sides: return angle opposite first side 'c'
            cosgamma=(a*a+b*b-c*c)/(2*a*b)
            return cosgamma 
        def intersect_circles(c1x,c1y,r1,c2x,c2y,r2):# intersection point of 2 circles
            dx,dy=c1x-c2x,c1y-c2y
            dl=sqrt(dx*dx+dy*dy)
            ex,ey=dx/dl,dy/dl 
            cos1=sss(r1,dl,r2)
            sin1=sqrt(1.0-cos1*cos1)
            p1x,p1y=c2x+r2*(ex*cos1+ey*sin1),c2y+r2*(-ex*sin1+ey*cos1)
            p2x,p2y=c2x+r2*(ex*cos1-ey*sin1),c2y+r2*(ex*sin1+ey*cos1)
            if (p1x*p1x+p1y*p1y)<(p2x*p2x+p2y*p2y):#point closest to the origin
                return p1x,p1y
            else:
                return p2x,p2y
        r1=stepper_positions['stepper_x']
        r2=stepper_positions['stepper_y']
        z=stepper_positions['stepper_z']
        c1x,c1y=self.anchors[0][:2]
        c2x,c2y=self.anchors[1][:2]
        x,y=intersect_circles(c1x,c1y,r1,c2x,c2y,r2)
        return x,y,z
        
def plotArcchain(ax,P0,n0,arcs,*args,**kwargs):
    p=P0
    n=n0
    for l,da in arcs:
        plotArc(ax,p,n,l,da,*args,**kwargs)
        p+=l*np.sinc(da/(2*pi))*n*exp(1j*da/2)
        n*=exp(1j*da)
        
def evolvent(t,t0=0.0,r=1):
  from numpy import exp,sin,cos
  tt0=t+t0
  return r*(cos(tt0)+t*sin(tt0)+1j*(sin(tt0)-t*cos(tt0)))

def sss(c,a,b):          #triangle with 3 sides: return angle opposite first side 'c'
  cosgamma=(a*a+b*b-c*c)/(2*a*b)
  return cosgamma 
  
def calc_ictersect(c1x,c1y,r1,c2x,c2y,r2):
  dx,dy=c1x-c2x,c1y-c2y
  dl=sqrt(dx*dx+dy*dy)
  ex,ey=dx/dl,dy/dl 
  cos1=sss(r1,dl,r2)
  sin1=sqrt(1-cos1*cos1)
  p1x,p1y=c2x+r2*(ex*cos1+ey*sin1),c2y+r2*(-ex*sin1+ey*cos1)
  p2x,p2y=c2x+r2*(ex*cos1-ey*sin1),c2y+r2*(ex*sin1+ey*cos1)
  if (p1x*p1x+p1y*p1y)<(p2x*p2x+p2y*p2y):# return the point closest to the origin
    return p1x,p1y
  else:
    return p2x,p2y
  
def test(a,b):
  return *a,b
C1=-350+0j 
C2=0+360j
l1=350
l2=360
t=np.linspace(0,2*pi,361)
plotArc(plt.gca(),C1+l1,1j,l1*2*pi,2*pi)
plotArc(plt.gca(),C2+l2,1j,l2*2*pi,2*pi)
p=calc_ictersect(C1.real,C1.imag,l1,C2.real,C2.imag,l2)
plt.plot(*p,'ko',fillstyle='none'  )
plt.gca().set_aspect('equal')
plt.show()
hbk=HingebotKinematics(anchors=[[C1.real,C1.imag,0],[C2.real,C2.imag,0]])
stepper_pos={'stepper_x':l1,'stepper_y':l2-10,'stepper_z':0.0}
pos=hbk.calc_position(stepper_pos)
print(stepper_pos, pos)

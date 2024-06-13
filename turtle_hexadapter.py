#!/usr/bin/env python
# coding: utf-8

# ## 3D-Printing using Turtle Graphics
# - A "Turtle Graphics" approach is used to define the extrusion paths:  A series of `(segment length, change of heading angle)` - tuples defines a path segment. e.g. the tuple `(2*pi ,2*pi)` defines a unit circle, the tuple `(1,0)` a straight line of unit length, and `(0,-30*deg)` turns on the spot `30deg` to the right.
# - Complex numbers are used for the 2D coordinates:  2D translations and rotations are simple additions and multiplications of complex numbers. E.g. the complex expression `(3+5j)*1j**(30/90)` rotates the point `(x=3,y=5)` counter-clockwise by `30deg` around the origin.

# In[1]:


import numpy as np
from matplotlib import pyplot as plt
from numpy import pi,exp,sign

def polygonArea(p):
  def crossprod(v1,v2):
    return v1.real*v2.imag-v2.real*v1.imag
  return 0.5*np.sum(crossprod(p[range(-1,len(p)-1)],p))

def SegmentsLengthArea(Segs):
  nSegs=len(Segs)
  dl,dang=np.array(Segs).transpose()
  l=sum(dl)
  ang=np.cumsum(dang)
  ang=exp(1j*np.insert( ang,0,0))
  dang_2=np.exp(1j*dang/2)
  viSeg=np.sinc(dang/(2*pi))*dl*dang_2*ang[:-1]
  pSeg=np.cumsum(viSeg)
  olderr=np.geterr()
  np.seterr(divide='ignore',invalid='ignore')#suppress the warnings from 0/0 = nan. nansum assumes nan=0, which is the correct value in this case
  area=polygonArea(pSeg) +  np.nansum((dl/dang)**2*(dang/2.0-dang_2.real*dang_2.imag))
  np.seterr(**olderr)
  return l,area

def InterpSegments(Segs,t,p0=0+0j,a0=0+1j,scale=1.0,return_headings=False,eps=1e-6):
  """
  Segment points are calculated for values of 't', where 't' is the normalized
  length of the path. t is in the range of [0..1[
  """
  dl,dang=np.array(Segs).transpose()
  l,ang_=np.cumsum([(0,0)]+Segs,axis=0).transpose()
  ang=exp(1j*ang_)
  viSeg=np.sinc(dang/(2*pi))*dl*scale*np.exp(1j*dang/2)*ang[:-1]
  pSeg=np.cumsum(np.insert(viSeg,0,0+0j))
  T=t.astype(int)
  if ((abs(pSeg[-1])<eps) and (abs(ang[-1]-(1+0j))<eps)):
    pr,ar=np.zeros((len(t),),dtype=complex), np.ones((len(t),),dtype=complex) # closed loop. No translation/rotation necessary for t>1
  else: #endpoint of path != startpoint => repeat path for t>1 by translating and rotating it
    def rotateSecant(v,beta,T):
      beta2=beta/2
      rot2=exp(1j*beta2)
      uniqueT,inverseIndex=np.unique(T,return_inverse=True) #don't re-calculate for identical values of T
      p=(v*rot2**(uniqueT-1)/np.sinc(beta2/np.pi) * uniqueT * np.sinc(uniqueT*beta2/np.pi))[inverseIndex]
      a=(rot2**(2*uniqueT))[inverseIndex]
      return p,a
    pr,ar=rotateSecant(pSeg[-1],ang_[-1],T)
  pr+=p0
  ar*=a0
  l=l/l[-1]
  Xx=np.interp(np.array(t)%1,l,range(len(l)))
  X=Xx.astype(int) #segment index
  x=Xx%1 #within seggment
  p=pSeg[X] + np.sinc( dang[X]*x /(2*pi))* dl[X]*x *scale*np.exp(1j* dang[X]*x /2)*ang[X]
  p=p*ar+pr
  if not return_headings:
    return p
  else:
    a=ang[X]*np.exp(1j*dang[X]*x)*ar
    return p,a

def Segments2Complex(Segs,p0=0+0j,scale=1.0,a0=0+1j,tol=0.05,offs=0,loops=1,return_heading=False,return_start=False):
  """
  The parameter "tol defines the resolution. It is the maximum allowable
  difference between circular arc segment, and the secant between the
  calculated points on the arc. Smaller values for tol will result in
  more points per segment.
  """
  a=a0
  p=p0
  p-=1j*a*offs
  if return_start:
      yield p
  for _ in range(loops):
      for l,da in Segs:
        l=l*scale
        if da!=0:
          r=l/da
          r+=offs
          if r!=0:
            l=r*da
            dl=2*abs(2*r*tol)**0.5
            n=max(int(abs(6*(da/(2*pi)))),int(l//dl)+1)
          else:
            n=1
          dda=exp(1j*da/n)
          dda2=dda**0.5
          v=(2*r*dda2.imag)*dda2*a
        else:
          n=1
          dda=1
          v=l*a
        for _ in range(n):
          p+=v
          if return_heading:
            yield p,a
          else:
            yield p
          v*=dda
          a*=dda


# In[30]:


from math import pi
deg=pi/180
def mirror(a): return a+a[::-1]
def rackSegment(l=1,w1=0.5,w2=0.5,r1=0.1,r2=0.1,a=60*deg,c=0*deg,da=0,daw=0):return mirror([(w1/2,daw/2),(r1*a,a+da/4-daw/2-c/4),(l,c/2),(r2*a,-a+da/4-daw/2-c/4),(w2/2,daw/2)])
hex=mirror([(0.5,0),(0.1,30*deg)])*6
#ns,nc=13,2
ns,nc=21,4 
#rs=rackSegment(w1=0.575,w2=0.3,r1=0.2,r2=0.2,da=2*pi/(ns/nc),daw=0.8* 2*pi/ns)
#ns,nc=10,3 
ns,nc=24,5   
rs=rackSegment(w1=0.43,w2=0.12,r1=0.2,r2=0.2,da=2*pi/(ns/nc),c=0*deg,daw=0.7* 2*pi/ns)
#rs=rackSegment(w1=1.2,w2=0.6,r1=0.2,r2=0.2,a=55*deg,da=2*pi/(ns/nc),c=45*deg,daw=0.8* 2*pi/ns)

pr1=np.array(list(Segments2Complex(rs,scale=5,tol=0.01,loops=ns,return_start=True))).transpose()
pr1max=max(pr1.real)
pr1min=min(pr1.real)
pr1_r=(pr1max-pr1min)/2
pr1+=pr1_r
pr1_ri=np.min(abs(pr1))
phex=np.array(list(Segments2Complex(hex,scale=1,tol=0.02,loops=1,return_start=True))).transpose()
hexh=(max(phex.imag)-min(phex.imag))
hexw=(max(phex.real)-min(phex.real))
hex_r_eq=(hexh+hexw)/4
hexscale=pr1_r/hex_r_eq
phex=(phex+hexw/2)*hexscale
t=((np.log(pr1).imag)/(2*pi))%1#phase angle [0..1[
amp=abs(pr1)/pr1_r*hexscale#amplitude
ampmax=max(amp)
ampmin=min(amp)
ampmid=(max(amp)+min(amp))/2
vhex=InterpSegments(hex,t,p0=hexw/2)*amp
vhexmix=pr1.copy()
vhexmix[amp>ampmid]=vhex[amp>ampmid]

thread=mirror([(0.1,60*deg),(1,0),(0.14,-60*deg)])
pthread=np.array(list(Segments2Complex(thread,return_start=True,tol=0.001)))
pthread/=pthread[-1].imag
Dflatcp=-(2.5-0.5)+1j*(2.5**2-2**2)**0.5 #corner point of D-shaft 5mm diameter
Dflatang=np.log(Dflatcp).imag
Dshaft=mirror([(2.5*Dflatang,Dflatang),(0,pi-Dflatang),(Dflatcp.imag,0)])
pDshaft=(np.array(list(Segments2Complex(Dshaft,p0=2.5,return_start=True,tol=0.01)))/2.5)*pr1_ri
vDshaft=0.7*InterpSegments(Dshaft,t,p0=2.5)/2.5*amp
vDshaftmix=pr1.copy()
vDshaftmix[amp<ampmid]=vDshaft[amp<ampmid]

t=np.linspace(0,2*pi,301)
r=8
pc=r*np.exp(1j*t)
pt=pc*(r+np.interp(t/(2*pi),pthread.imag,pthread.real))/r
fig,((ax1,ax2),(ax3,ax4))=plt.subplots(2,2,figsize=(12,12))
ax4.plot(vhexmix.real,vhexmix.imag,'b.-')
ax1.plot(pDshaft.real,pDshaft.imag,'.-',c='orange',zorder=6)
ax3.plot(vDshaftmix.real,vDshaftmix.imag,'b.-',zorder=6)
ax2.plot(vhex.real,vhex.imag,'b.-',zorder=5)
ax1.plot(pr1.real,pr1.imag,'b.-')
ax1.plot(phex.real,phex.imag,'r.-',zorder=4)
for ax in(ax1,ax2,ax3,ax4):
  ax.set_aspect('equal')
  ax.set_xlim(-12.5,12.5)
  ax.set_ylim(-12.5,12.5)
plt.show()


# In[26]:


if 'google.colab' in str(get_ipython()):
 try:
   import fullcontrol as fc
 except Exception as e:
   print(e)
   print('Attempting to install missing packages. Please wait ...')
   get_ipython().system('pip install git+https://github.com/FullControlXYZ/fullcontrol --quiet')
   import fullcontrol as fc
 from google.colab import files
import fullcontrol as fc
from math import cos, tau


# In[12]:


steps=[]
hl=0.2
FilamentDiameter=1.75
tol=0.03
nwipe=5
nskip=5
jt=0
nskirt=0
skirtoffs=1.5
ehmin=hl/4
p0=25+0j
a0=1j**(90/90)
#Segments=rs
offs=0.0
scale=8
a0=1
p0=0
#path=list(Segments2Complex(Segments,p0=p0,a0=a0,tol=tol,scale=scale,offs=offs,loops=ns))
path=vhex*2
r=max(path.real)
rskirt=r+skirtoffs
p=-1j*rskirt
steps.extend(fc.travel_to(fc.Point(x=p.real,y=p.imag,z=hl)))
steps.append(fc.Extruder(on=True))
n=200
dang=1j**(4/n)
for i in range(n):
  p*=dang
  steps.append(fc.Point(x=p.real,y=p.imag))
steps.append(fc.Extruder(on=False))
n=len(path)
zb=0
zt=zb+10
dzdj=hl/n
w=0.75
#print(w)
dwdj=0
old_eh=-1
old_w=-1
jt=0
p=path[-1]
z=zb+ehmin
steps.extend(fc.travel_to(fc.Point(x=p.real,y=p.imag)))
steps.extend(fc.travel_to(fc.Point(z=z)))
steps.append(fc.Extruder(on=True))
#while False:
while  z<(zt+hl):
  jt=(jt+1)%n
  z+=dzdj
  w-=dwdj
  eh=min(z-zb if z<(zb+hl+ehmin) else hl ,zt-(z-hl))
  p=path[jt]
  if (abs(eh-old_eh)/hl)>0.01 or abs(w-old_w)>0.005:
   # print(f'{zb=}{z=}{zt=}{eh=}{w=}')
    steps.append(fc.ExtrusionGeometry(area_model='rectangle',height=eh,width=w))
    old_eh=eh
    old_w=w
  steps.append(fc.Point(x=p.real,y=p.imag,z=min(z,zt)))
steps.append(fc.Extruder(on=False))
steps.extend(fc.travel_to(fc.Point(x=0,y=0)))
# offset the whole procedure. z dictates the gap between the nozzle and the bed for the first layer, assuming the model was designed with a first layer z-position of 0
model_offset = fc.Vector(x=100, y=100, z=0.0*hl)
#print(f'{w=} {eh=}')
steps = fc.move(steps, model_offset)


# In[13]:


# add annotations and plot
EW=1.0
EH=0.2
fc.transform(steps, 'plot', fc.PlotControls(style='line',color_type='print_sequence', initialization_data={'extrusion_width': EW, 'extrusion_height': EH}))


# In[7]:


#design parameters

design_name = 'hexadapter'
nozzle_temp = 220
bed_temp = 120
print_speed = 30*60
fan_percent = 0
EH = 0.2    # extrusion heigth
EW = 0.5    # extrusion width
printer_name = 'generic'
#printer_name = 'Prusa_Mendel'
gcode_controls = fc.GcodeControls(
    printer_name=printer_name,
    save_as=design_name,
    initialization_data={
        'primer': 'no_primer',
        'print_speed': print_speed,
        'nozzle_temp': nozzle_temp,
        'bed_temp': bed_temp,
        'fan_speed':fan_percent,
         })
gcode = fc.transform(steps, 'gcode', gcode_controls)


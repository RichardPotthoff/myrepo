import os
import socket
from math import acos,pi,sin,cos,sqrt
import cmath
import numpy as np
on_ipad=socket.gethostname()=="iPad"
if on_ipad:
  from matplotlib import pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D

import operator
from collections import namedtuple

class Angle(complex):
   def __new__(cls,cos_phi=None,sin=None,phi=None,cos=None):
     if sin==None:
       if hasattr(cos_phi,'__getitem__'):
         return super(Angle,cls).__new__(cls,*cos_phi)
       elif issubclass(cos_phi.__class__,complex):
           return super(Angle,cls).__new__(cls,cos_phi)
       else: 
           return super(Angle,cls).__new__(cls,cmath.rect(1,cos_phi if cos_phi!=None else phi))
     return super(Angle,cls).__new__(cls,cos_phi if cos_phi!=None else cos,sin)
   @property
   def cos(self):
     return self.real
   @property
   def sin(self):
     return self.imag
   @property
   def cossin(self):
     return (self.real,self.imag)
   @property
   def phi(self):
     return cmath.phase(self)

class Point(complex):
   def __new__(cls,x_p,y=None,x=None):
     if y==None:
       if hasattr(x_p,'__getitem__'):
         return super(Point,cls).__new__(cls,*x_p)
       elif issubclass(x_p.__class__,complex):
           return super(Point,cls).__new__(cls,x_p)
     return super(Point,cls).__new__(cls,(x_p if x_p != None else x),y)
   @property
   def x(self):
     return self.real
   @property
   def y(self):
     return self.imag
   @property
   def xy(self):
     return (self.real,self.imag)
   @property
   def rphi(self):
     return cmath.polar(self)

#def cossin(x):
#  return Angle(cos(x),sin(x))

class Segment(namedtuple('Segment','l, ang')):
  def __new__ (cls, l, ang=0):
    return super(Segment, cls).__new__(cls, l,ang)
  def __init__(self,l,ang=0):
    self._csang=Angle(ang)
    self._endpoint=rotate(Point(l,0),self._csang)
    self._A=0
  @property
  def csang(self):
    return self._csang
  @property
  def endpoint(self):
    return self._endpoint
  @property
  def A(self):
    return self._A
    
class ArcSegment(Segment):
  def __init__(self,l,ang):
    super().__init__(l,ang)
    if ang!=0:
      secang=halfangle(self._csang)
      lsec=2*secang.sin*l/ang
      self._endpoint=Point(lsec*secang.cos,lsec*secang.sin)
      self._A=0.5*(l*l/ang-lsec*l/ang*secang.cos)

def firstNotNone(*args):
  for x in args:
    if x!=None:
      return x
  return None
    
def findIndex(x,xi):
  i0=0
  i2=len(xi)
  while True:
    if (i2-i0)<=1:
      return i2 if x>xi[i0] else i0
    i=(i0+i2)//2
    if x>xi[i]:
      i0=i
    else:
      i2=i
      
def interp(x,xi,fi,extrapolate=False):
  i=findIndex(x,xi)
  if i<=0:
    if extrapolate:
      i=1
    else:
      return fi[0]
  elif i>=len(xi):
    if extrapolate:
      i=len(xi)-1
    else:
      return fi[len(xi)-1]
  return fi[i-1]+(fi[i]-fi[i-1])/(xi[i]-xi[i-1])*(x-xi[i-1])
    

class Position(list):
  def __init__(self,x,y,z):
    super().__init__([x,y,z])
  def __getattr__(self,attr):
    return self[{'x':0,'y':1,'z':2}[attr]]
  def __setattr__(self,attr,value):
    self[{'x':0,'y':1,'z':2}[attr]]=value
    
Position=namedtuple('Position','x, y, z')    

def shiftPoint(p,offset):
  return Point(p+offset)

def addAngles(a,b):
  return Angle(a*b)

  
class SegmentList_(Segment):
  def __new__ (cls, list):
    len=sum(s.l for s in list)
    ang=sum(s.ang for s in list)
    return super(SegmentList_, cls).__new__(cls, len,ang)
  def __init__(self,list):
    self._list=list
    self._ls=[None]*len(list)
    self._angs=[None]*len(list)
    self._endpoints=[None]*len(list)
    self._csangs=[None]*len(list)
    A=0
    l=0
    ang=0
    endpoint=Point(0,0)
    csang=Angle(1,0)
    for i,s in enumerate(list):
      super().__init__(self.l,self.ang)
      l+=s.l
      ang+=s.ang
      startpoint=endpoint
      endpoint=shiftPoint(startpoint,rotate(s.endpoint,csang))
      A+=s.A+crossProduct(startpoint,endpoint)/2
      csang=addAngles(csang,s.csang)
      self._ls[i]=l
      self._angs[i]=ang
      self._endpoints[i]=endpoint
      self._csangs[i]=csang
    self._endpoint=endpoint
    self._A=A
    
    

class SegmentList(list):
  def __init__(self):
    self._l=[0]
    self._csang=[Angle(1,0)]
    self._ang=[0]
    self._p=[(0,0)]
  def addArc(self,l=None,ang=None,r=None):
    if ang==None:
      ang=l/r
    if l==None:
      l=r*ang
    self._l.append(self._l[-1]+l)
    csang=Angle(ang)
    cshalfang=halfangle(csang)
    lsec=l if ang==0 else 2*cshalfang.sin*l/ang
    secang=addAngles(cshalfang,self._csang[-1])
    self._p.append((self._p[-1][0]+lsec*secang.cos,self._p[-1][1]+lsec*secang.sin))
    self._csang.append(sumangles(csang,self._csang[-1]))
    self._ang.append(self._ang[-1]+ang)
    

  def addLine(self,l):
    self.addArc(l,ang=0)   
  @property
  def length(self):
    return self._l[-1]
  def coord(self,l,offset=0):
    i=findIndex(l,self._l)
    i=max(i,1)
    i=min(i,len(self._l)-1)
    dl=l-self._l[i-1]
    dang=(self._ang[i]-self._ang[i-1])/(self._l[i]-self._l[i-1])*dl
    csdang=Angle(dang)
    cspang=addAngles(csdang,self._csang[i-1])
    cshalfdang=halfangle(csdang)
    if dang==0:
      lsec=dl
      secang=self._csang[i]
    else:
      lsec=2*cshalfdang.sin*dl/dang
      secang=sumangles(cshalfdang,self._csang[i-1])
    return (self._p[i-1][0]+lsec*secang.cos-offset*cspang.sin,self._p[i-1][1]+lsec*secang.sin+offset*cspang.cos)

    
    
class Position_h_w(list):
  _attrindex={'x':0,'y':1,'z':2,'h':3,'w':4}
  def __init__(self,p,h,w):
    super().__init__([*p,h,w])
  def __getattr__(self,attr):
    try:
      return self[self._attrindex[attr]]
    except KeyError:
      if attr=='p':
        return self[:3]
  def __setattr__(self,attr,value):
    try:
      self[self._attrindex[attr]]=value
    except KeyError:
      if attr=='p':
        self[:3]=value
      
  def flatten(self):
    return [*self[0],*self[1:]]
Position_h_w=namedtuple('Position_h_w','x, y, z, h, w')    
class Printer():
  def __init__(self,origin=Position(x=0,y=0,z=0),defaultExtrusionHeight=None,defaultExtrusionWidth=None):   
    self.defaultExtrusionHeight=defaultExtrusionHeight
    self.defaultExtrusionWidth=defaultExtrusionWidth
    self.currentExtrusionHeight=None
    self.currentExtrusionWidth=None
    self.currentPosition=origin
    
  def moveto(self,p,extrusionHeight=None,extrusionWidth=None):
    self.currentExtrusionHeight=extrusionHeight
    self.currentExtrusionwidth=extrusionWidth
    self.currentPosition=p
    
  def extrudeto(self,p,extrusionHeight,extrusionWidth):
    self.currentExtrusionHeight=extrusionHeight
    self.currentExtrusionWidth=extrusionWidth
    self.currentPosition=p
    
  def extrudePolygon(self,polygon,extrusionHeight=None,extrusionWidth=None):
    self.moveto(polygon[0])
    for p in polygon[1:]:
#      print('extrudePolygon',p)
      self.extrudeto(p,extrusionHeight,extrusionWidth)
      
class LogPrinter(Printer):
  def __init__(self,*args,**kwargs):
    self.paths=[]
    self.currentPath=None
    super().__init__(*args, **kwargs)
    
  def moveto(self,*args, **kwargs):
    self.currentPath=None
    super().moveto(*args, **kwargs)
    
  def extrudeto(self,p,extrusionHeight=None,extrusionWidth=None):
    if not self.currentPath:
      self.currentPath=[Position_h_w(*self.currentPosition,firstNotNone(self.currentExtrusionHeight, extrusionHeight, self.defaultExtrusionHeight), firstNotNone(self.currentExtrusionWidth , extrusionWidth, self.defaultExtrusionWidth))]
      self.paths.append(self.currentPath)
#      print('start new path',self.currentPath)
#    print('extrudeto',p)
    self.currentPath.append(Position_h_w(*p,firstNotNone(extrusionHeight, self.currentExtrusionHeight,  self.defaultExtrusionHeight),firstNotNone(extrusionWidth, self.currentExtrusionWidth, self.defaultExtrusionWidth)) )
    self.currentExtrusionHeight=extrusionHeight
    self.currentExtrusionwidth=extrusionWidth
    self.currentPosition=p
   
class PreviewPrinter(Printer):
  def __init__(self,axis3D,*args,**kwargs):
    self.pltAxis=axis3D
    super().__init__(*args,**kwargs)
  def moveto(self,p):
    self.currentPosition=p
  def extrudeto(self,p,extrusionheight,extrusionwidth):
    self.currentPosition=p


cookiecutterindex=5
#'Tanne':tSegments,'Dasy':dSegments,'Ente':eSegments,'Stern':sSegments,'Heart':hSegments,'Circle':cSegments
crosssectionindex=1

def show_plot():
  plt.axis('off')
  plt.axes().set_aspect('equal', 'datalim')
  plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
  plt.show()
  plt.close()
  
#class Segment(object):
#  def __init__(self,l,ang):
#    self.l=l
#    self.ang=ang

Brick=namedtuple('Brick','offset, width')
 
class Bricklayer(list):
  def __init__(self,*args):
    super().__init__(args)
    
class ExtrusionCrosssection(list):
  def __init__(self,*args):
    super().__init__(args)
    
def sumangles(a,b):
  return Angle(a*b)
  
def rotate(v,a):
  return Point(a*v)

def doubleangle(a):
  return sumangles(a,a)
  
def halfangle(a):
  return Angle(cmath.sqrt(a))
#def halfangle(a):
#  return Angle(sqrt(0.5+a.cos/2.0),(1.0 if(a.sin>0) else -1.0)* sqrt(0.5-a.cos/2.0))  
  
  
def angle(cs):
  return atan2(cs.sin,cs.cos)
  
n=50
pi2=pi*2
t_=[float(i)/n for i in range(n+1)]
t1=[(sin(t*pi2),cos(t*pi2)) for t in t_]

hSegments=[Segment(0.45,45.0/180*pi),
          Segment(10.0,-180.0/180*pi),
          Segment(6.91,10.0/180*pi),
          Segment(1.1,-110.0/180*pi),
          Segment(6.91,10.0/180*pi),
          Segment(10.0,-180.0/180*pi),
          Segment(0.45,45.0/180*pi)]
          
dSegments=[]
n=9
a=150.0
b=a-360.0/n
for i in range(n):
  dSegments+=[Segment(1.0,b/180*pi),
          Segment(2.0,-a/180*pi)]
      
#Tanne
tSegments=[Segment(0.75,-40.0/180*pi)]
n=4
a=140.0
b=a
for i in range(n):
  tSegments+=[Segment(3,0.0),
              Segment(1.5,-b/180*pi),
             Segment(0.6,0.0),

          Segment(1.0,a/180*pi)]
tSegments=tSegments[:-3]
tSegments+=[Segment(1.5,-140.0/180*pi),Segment(12.4-0.969,0)]
for i in range(len(tSegments)-2,-1,-1):
  tSegments.append(tSegments[i])

eSegments=[Segment(5,125.0/180*pi),
          Segment(15,-220.0/180*pi),
          Segment(3,90.0/180*pi),
          Segment(2,20.0/180*pi),
          Segment(3,-170.0/180*pi),
          Segment(5,-20.0/180*pi),
          Segment(5,90.0/180*pi),
          Segment(15,-90.0/180*pi),
          Segment(22.913,-90.0/180*pi),
          Segment(4,-160.0/180*pi),
          Segment(3,80.0/180*pi),
          Segment(13.297,-25.0/180*pi),
          Segment(0.4,10.0/180*pi),
          ]
cSegments=[Segment(1.0,2*pi),]


sSegments=[]
n=5
a=130.0
b=a-360.0/n
for i in range(n):
  sSegments+=[Segment(0.5,b/180*pi),
              Segment(2.0,0.0),
          Segment(0.8,-a/180*pi),
          Segment(2.0,0.0)]

def SegmentsToPolyline(Segments, a=Angle(0), p=Point(0.0,0.0), o=0.0, damax=pi/4, maxdev=0.01, lstart=0.0,lend=None):
  p+=rotate(Point(0.0,o),a)
  t2=[]
  vn=[]
  ltot=pathLength(Segments)
  reverse=False
  if lend!=None:
    if lstart>lend:
      reverse=True
      temp=lend
      lend=lstart
      lstart=temp
  fullloops=ltot*int(float(lstart)/ltot)
  while fullloops>lstart:
    fullloops-=ltot
  lstart=lstart-fullloops
  if lend:
    lend=lend-fullloops
  else:
    lend=lstart+ltot
  l=0.0
  iSegment=0
  nSegments=len(Segments)
#    print lstart,lend,ltot
  startfound=False
  while l<lend:
    s=Segments[iSegment]
    if s.ang!=0:
      r=abs(float(s.l)/s.ang)
      if maxdev<r:
        maxang=(2.0*acos(1.0-maxdev/r)).real
        n=int(round(abs(s.ang)/maxang+0.5))
      else:
        n=1
      da=s.ang/n
      if abs(da)>damax:
        n=int(round(abs(s.ang)/damax+0.5))
        da=s.ang/n
      da1=Angle(da)
      da2=halfangle(da1)
      dl=rotate(Point((float(s.l)-o*s.ang)/n*da2.sin/(da/2.0),0),da2)
    else:
      n=1
      da=0
      da1=Angle(1.0,0.0)
      dl=Point(float(s.l),0.0)
    true_dl=float(s.l)/n
#        print "n=",n
    vnormal=Angle(0,1)
    dl=rotate(dl,a)
    vnormal=rotate(vnormal,a)
    for i in range(n):
      l+=true_dl
      if not startfound:
        if l>lstart:
          startfound=True
          dlfraction=1.0-(l-lstart)/true_dl
          t2.append((Point(p+dlfraction*dl),0.0))
          vn.append(vnormal)
      p+=dl
      ll=l-lstart
      if startfound:
        if l>lend:
          dlfraction=-(l-lend)/true_dl
          t2.append((Point(p+dlfraction*dl),lend-lstart))
          vn.append(vnormal)
          break
        else:
          t2.append((Point(p),ll))
          vn.append(vnormal)
      dl=rotate(dl,da1)
      vnormal=rotate(vnormal,da1)
      
    a=rotate(a,Angle(s.ang))
    iSegment+=1
    if iSegment>=nSegments:
      iSegment-=nSegments
#   print angle(a)*180/pi,p
#    print l
  if reverse:
    return reversed(t2),([-p for p in reversed(vn)])
  else:
    return t2,vn
    
def pathLength(Segments):
  result=0
  for Segment in Segments:
    result+=Segment.l
  return result
  
def minmaxxy(t):
  p,l=t[0]
  maxx=p.x
  minx=maxx
  maxy=p.y
  miny=maxy
  for p,l in t[1:]:
    maxx=max(maxx,p.x)
    minx=min(minx,p.x)
    maxy=max(maxy,p.y)
    miny=min(miny,p.y)
  return (minx,maxx,miny,maxy)
  
def fill(minx,maxx,n):
  w=maxx-minx
  dx=float(w)/n
  x=minx+dx/2
  result=[Brick(x,dx)]
  for i in range(n-1):
    x+=dx
    result.append(Brick(x,dx))
  if n>3:
    result=[result[1]]+[result[0]]+result[n-2:]+result[2:n-2]
  return Bricklayer(*result)
  
def skirt(polyline,r=3,d=3):
  xmin,xmax,ymin,ymax=minmaxxy(polyline)
  dx,dy=xmax-xmin,ymax-ymin
  return(Point(xmin-d,ymin-d-r),(Segment(dx+d*2,0),Segment(r*pi/2,pi/2),\
                      Segment(dy+d*2,0),Segment(r*pi/2,pi/2),\
                      Segment(dx+d*2,0),Segment(r*pi/2,pi/2),\
                      Segment(dy+d*2,0),Segment(r*pi/2,pi/2)))
                      
def scalePath(path,scale=1.0):
  return [Segment(s.l*scale,s.ang) for s in path]
  
def mirrorPath(path):
  return[Segment(s.l,-s.ang)for s in path]
  
def crossProduct(v1,v2):
  return(v1.x*v2.y-v2.x*v1.y)
  
def vectorSum(v1,v2):
  return Point(v1+v2)
  
def pathArea(path):
  areaSum=0.0
  currentAngle=Angle(0)
  currentCoordinate=Point(0.0,0.0)
  for Segment in path:
    deltaAngle=Angle(Segment.ang)
    halfDeltaAngle=halfangle(deltaAngle)
    if Segment.ang!=0.0:
      secantLength=Segment.l*halfDeltaAngle.sin/(0.5*Segment.ang)
      circleSectionArea=(float(Segment.l)/Segment.ang)**2*(Segment.ang/2.0-halfDeltaAngle.cos*halfDeltaAngle.sin)
    else:
      secantLength=Segment.l
      circleSectionArea=0.0
    deltaCoordinate=rotate(Point(secantLength,0.0),sumangles(currentAngle,halfDeltaAngle))
    triangleArea=0.5*crossProduct(currentCoordinate,deltaCoordinate)
    areaSum+=triangleArea+circleSectionArea
#    print "circleSection",circleSectionArea
    currentCoordinate=vectorSum(currentCoordinate,deltaCoordinate)
    currentAngle=sumangles(currentAngle,deltaAngle)
  return areaSum

def normalizePath(path,p0,area):
  actualarea=pathArea(path)
  rotang=Angle(1.0,0.0)
  if actualarea<0:
    path=mirrorPath(reversed(path))
    actualarea*=-1
    rotang=addAngles(rotang,Angle(-1.0,0.0))
  scale=sqrt(area/actualarea)
  xmin,xmax,ymin,ymax=minmaxxy(SegmentsToPolyline(path)[0])
  dx=xmax-xmin
  dy=ymax-ymin
  if dx>dy:
    rotang=addAngles(rotang,Angle(0.0,1.0))
  path=scalePath(path,scale)
  xmin,xmax,ymin,ymax=minmaxxy(SegmentsToPolyline(path,a=rotang)[0])
  dx=xmax-xmin
  dy=ymax-ymin
  return vectorSum(p0,Point(-(xmin+dx/2.0),-(ymin+dy/2.0))),rotang,path

p0,a,Segments=normalizePath((tSegments,dSegments,eSegments,sSegments,hSegments,cSegments)[cookiecutterindex],p0=Point(100,100),area=2000.0)

t2=[]#SegmentsToPolyline(Segments,p=p0,a=a)
for o in range(1):
  t2+=SegmentsToPolyline(Segments,p=p0,a=a,o=-o,lstart=10*o-20)[0]
pskirt0,skirtSegments=skirt(t2,r=5,d=0)
t2=SegmentsToPolyline(skirtSegments,p=pskirt0,o=0,lstart=-30)[0]+t2
area=minmaxxy(t2)
#print t2[-1],area

crosssection1= [fill(-w2,w2,n) for w2,n in ((3.6/2,4),(4.0/2,5),(4.4/2,6),(4.6/2,5))]+ \
      [Bricklayer(Brick(0.0,cw),Brick(-w2+ww/2,ww),Brick(w2-ww/2,ww)) for w2,ww,cw in[ \
        (4.8/2,1.0,1.0),\
        (5.0/2,1.0,0.8),\
        (5.0/2,0.9,0.6)]+\
        [(5.0/2,0.9,0.5)]*2+[\
        (4.8/2,0.9,0.5),\
        (4.6/2,0.9,0.5),\
        (4.4/2,1.0,0.5)]+\
        [(w2,1.0,0.5)for w2 in(4.0/2,3.6/2,3.2/2,2.8/2)]+\
        [(2.4/2,0.9,0.6)]
        ]+\
      [fill(-w2,w2,n) for w2,n in ((2.0/2,2),(1.6/2,3),(1.2/2,2))]+\
      [Bricklayer(Brick(0.0,1.0-0.5*i/50.0)) for i in range(50+1)]

crosssection2= ExtrusionCrosssection(fill(-2.0,-0.2,2),
      *[fill(-w2,0,n) for w2,n in ((4.4/2,3),(4.6/2,4))],
      *[Bricklayer(Brick(-cw/2,cw),Brick(-w2+ww/2,ww)) for w2,ww,cw in[ \
        (4.8/2,1.0,1.0),\
        (5.0/2,1.0,0.8),\
        (5.0/2,0.9,0.6)]+\
        [(5.0/2,0.9,0.5)]*2+[\
        (4.8/2,0.9,0.5),\
        (4.6/2,0.9,0.5),\
        (4.4/2,1.0,0.5),\
        (2.0,1.0,0.7)]\
        ]+\
        [fill(-1.8,0,2),\
         fill(-1.6,0,3),\
        fill(-1.4,0,2),\
        fill(-1.2,0,2)],
      *[Bricklayer(Brick(-(1.0-0.5*i/50.0)/2.0,1.0-0.5*i/50.0)) for i in range(50+1)])
      
crosssection=(crosssection1,crosssection2)[crosssectionindex]
#for layer in crosssection:print layer
#print "forward",pathArea(Segments)
#print "mirrored",pathArea(mirrorPath(eSegments))
#print "reversed",pathArea(reversed(eSegments))
from time import strftime,gmtime
program_name="Cookiecutter"
program_version="0.1"
layer_height = 0.2
perimeter_speed = 30
travel_speed = 130
nozzle_diameter = 0.35
filament_diameter = 1.75
extrusion_multiplier = 1.07
first_layer_bed_temperature = 120.0
first_layer_hotend_temperature = 220.0
bed_temperature=115.0
hotend_temperature=220.0
retraction = 1.0
first_layer_speed_ratio=0.7
retract_perimeter_length=10.0
filament_crossection=filament_diameter**2*pi/4.0
min_layer_time=15.0
eps=1.0e-5
lastx=1e10
lasty=1e10
lastz=1e10
laste=1e10
lastspeed=1e10

def extrudePolyline(output,t,speed=None,extrusion_ratio=None,z=None):
  global lastx,lasty,lastz,laste,lastspeed
  p,l=t[0]
  x,y=p.xy
  if (abs(x-lastx)>eps) or (abs(y-lasty)>eps) or (abs(z-lastz)>eps):
#       print "xyz,lastxyz",x,y,z,lastx,lasty,lastz,lastx==x,lasty==y,lastz==z
    output.write("G1 X%(X)0.3f Y%(Y)0.3f Z%(Z)0.3f F%(F)0.3f\n"%{"X":x,"Y":y,"Z":z,"F":travel_speed*60})
    lastx,lasty,lastz,lastspeed=x,y,z,travel_speed
  for p,l in t[1:]:
    x,y=p.xy
    output.write("G1 X%(X)0.3f Y%(Y)0.3f E%(E)0.5f"%{"X":x,"Y":y,"E":laste+l*extrusion_ratio})
    if speed!=lastspeed:
      output.write(" F%(F)0.3f\n"%{"F":speed*60})
      lastspeed=speed
    else:
      output.write("\n")
    lastx,lasty=x,y
  laste+=t[-1][1]*extrusion_ratio
  return

def extrudePath(output,path,p0,o,a,lstart,speed,\
                layer_height,extrusion_width,z):
  global laste
  output.write("G92 E0\n")
  laste=0.0
  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart,\
                       lend=lstart+retract_perimeter_length)[0]
  extrudePolyline(output,t,speed=speed,extrusion_ratio=retraction/retract_perimeter_length,z=z)

  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length)[0]
  extrusion_crossection=layer_height*extrusion_width
  extrudePolyline(output,t,speed=speed,\
       extrusion_ratio=extrusion_crossection/filament_crossection*extrusion_multiplier,z=z)

  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length,\
                       lend=lstart+2*retract_perimeter_length)[0]
  extrudePolyline(output,t,speed=speed,extrusion_ratio=-retraction/retract_perimeter_length,z=z)
  return

def extrudeSpiralPath(output,path,p0,o,a,lstart,speed,\
                layer_height,extrusion_width,z):
  global laste
  output.write("G92 E0\n")
  laste=0.0
  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart,\
                       lend=lstart+retract_perimeter_length)[0]
  extrudePolyline(output,t,speed=speed,extrusion_ratio=retraction/retract_perimeter_length,z=z)

  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length)[0]
  extrusion_crossection=layer_height*extrusion_width
  extrudePolyline(output,t,speed=speed,\
       extrusion_ratio=extrusion_crossection/filament_crossection*extrusion_multiplier,z=z)

  t=SegmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length,\
                       lend=lstart+2*retract_perimeter_length)[0]
  extrudePolyline(output,t,speed=speed,extrusion_ratio=-retraction/retract_perimeter_length,z=z)
  return

preamble=f'''; generated by {program_name:s} v{program_version:s} {strftime("on %Y/%m/%d at %H:%M:%S",gmtime()):s}
; layer_height = {layer_height:0.3f}
; perimeter_speed = {perimeter_speed:f}
; travel_speed = {travel_speed:f}
; nozzle_diameter = {nozzle_diameter:f}
; filament_diameter = {filament_diameter:f}
; extrusion_multiplier = {extrusion_multiplier:f}

G21 ; set units to millimeters
M107
M190 S{first_layer_bed_temperature:0.0f} ; wait for bed temperature to be reached
M104 S{first_layer_hotend_temperature:0.0f} ; set temperature

M109 S{first_layer_hotend_temperature:0.0f} ; wait for temperature to be reached
G90 ; use absolute coordinates
G92 E0
M82 ; use absolute distances for extrusion
'''


for n_flange,brickLayer in enumerate(crosssection):
  if len(brickLayer)==1:
    break
    
#n_flange=(20,16)[crosssectionindex]
    
filelocation="/dev/null" if on_ipad else "/home/pi/.octoprint/uploads/spiral_duck.gcode"
z=0.0
z+=layer_height
output=open(filelocation,"w")
output.write(preamble)
output.write("G1 Z%(Z)0.3f F%(F)0.3f\n"%{"F":travel_speed*60.0,"Z":z})
lastz=z
lstart=0.0
dlstart=2.5*retract_perimeter_length

for i in range(-1,2,1):
  extrudePath(output,skirtSegments,speed=perimeter_speed*first_layer_speed_ratio,\
                    p0=pskirt0,a=Angle(1.0,0.0),o=i*0.75,lstart=lstart,
                    extrusion_width=0.75,layer_height=layer_height,z=z)
  lstart+=dlstart
speed_ratio=first_layer_speed_ratio
for layer in crosssection[:n_flange]:
  totalextrusionlength=len(layer)*pathLength(Segments)
  speed=min(totalextrusionlength/min_layer_time,perimeter_speed)*speed_ratio
  for o,w in layer:
    extrudePath(output,Segments,speed=speed,\
                    p0=p0,a=a,o=o,lstart=lstart,
                    extrusion_width=w,layer_height=layer_height,z=z)
    lstart+=dlstart
  speed_ratio=1.0
  z+=layer_height
for layer in crosssection[n_flange:]:
  totalextrusionlength=len(layer)*pathLength(Segments)
  speed=min(totalextrusionlength/min_layer_time,perimeter_speed)*speed_ratio
  for o,w in layer:
    extrudePath(output,Segments,speed=speed,\
                    p0=p0,a=a,o=o,lstart=lstart,
                    extrusion_width=w,layer_height=layer_height,z=z)
    lstart+=dlstart
  speed_ratio=1.0
  z+=layer_height

output.write("G1 Z%(Z)0.3f\n"%{"Z":z})
output.write("G28 X0\n")
output.close()

def plot_box(x,z,w,h,style="r"):
  l=x-0.5*w
  r=x+0.5*w
  b=z-h
  t=z
  plt.plot([r,l,l,r,r],[t,t,b,b,t],style)

def plot_layers(extrusionCrosssection,x0=0,z0=0.0,dz=0.2,style="r"):
  z=z0+dz
  for brickLayer in extrusionCrosssection:
    for brick in brickLayer:
      plot_box(x0+brick.offset,z,brick.width,dz,style)
    z+=dz
    
def fminExtrusionWidth(nozzleDiameter,layerHeight):
  minExtrusionWidth=nozzleDiameter+layerHeight*pi/4.0#Nozzle width + area of two semicircles of layer height diameter to either side of nozzle
  return(minExtrusionWidth)
  
def  plot_():
  plt.plot([p.x for p,l in t2],[p.y for p,l in t2])
  show_plot()
  dz=0.2
  h_blade=(len(crosssection)-n_flange)*dz
  w_blade_top=crosssection[-1][0].width
  w_blade_bottom=crosssection[n_flange][0].width
  offset_blade_bottom=crosssection[n_flange][0].offset
  offset_blade_top=crosssection[-1][0].offset
  n_blade=int(h_blade/dz+1.5)
  plot_layers(crosssection[:n_flange],x0=-5.5,z0=0,dz=dz,style="r")
  plot_layers(crosssection[n_flange:],x0=-5.5,z0=n_flange*dz,dz=dz,style="b")
  for i in range(4):
    plot_layers(crosssection[:n_flange],x0=5.5*i,z0=0,dz=dz,style="r")
    for j in range(n_blade):
      z=(j+i/4.0)*dz
      o=-offset_blade_bottom+(j+i/4.0)/n_blade*(offset_blade_bottom-offset_blade_top)
      h_layer=min(z,dz)if z<h_blade else max(dz-(z-h_blade),0.0)
      if dz-(z-h_blade)<0:print("negative layer height at z=%f"%(z))
      z=min(z,h_blade)
      w_layer=w_blade_bottom+(w_blade_top-w_blade_bottom)*(z-0.5*h_layer)/h_blade
      plot_box(5.5*i-o,z+n_flange*dz,w_layer,h_layer,"g")
  show_plot()
  
def test_path():
  plt.close()
  p=SegmentList()
  n=11
  pent=[ArcSegment(1,1.11*pi/2+0.1), ArcSegment(1.75,4*pi/n-0.2), ArcSegment(1,1.11*pi/2+0.1), Segment(1.3),ArcSegment(1,-1.11*pi),Segment(1.3)]*n
  for s in pent:
    p.addArc(*s)
  ltot=p.length
  n=800
  for o in (-0.05,0,0.05):
    p1=[p.coord(l,o) for i in range(n+1) for l in (ltot/n*i,)]
    plt.plot(*zip(*p1))
  x=SegmentList_([ArcSegment(*s) for s in pent])
  plt.plot(*zip(*(p.xy for p in x._endpoints)))
  show_plot()
  
if on_ipad:
  printer=LogPrinter()
  p2d,vn=SegmentsToPolyline(Segments,lstart=-40)
  vn=np.array([p.xy for p in vn])
  p2d=np.array([(*p.xy,l) for p,l in p2d])
  dz=0.2
  z=0
  p2d0=np.concatenate((p2d[:,:2],np.zeros((p2d.shape[0],1))),axis=1)
  vn0=np.concatenate((vn,np.zeros((p2d.shape[0],1))),axis=1)
  for i,bricklayer in enumerate(crosssection):
    z+=dz
    if len(bricklayer)>1:
      for brick in bricklayer:
        printer.extrudePolygon(p2d0+[[0,0,z]]+brick.offset*vn0, extrusionWidth=brick.width,extrusionHeight=dz)
    else:
      n_flange=i
      break
  l=p2d[-1,2]
  p3d=np.concatenate((p2d[:,:2],p2d[:,2:]*dz/l),axis=1)
  n3d=np.concatenate((vn,np.zeros((vn.shape[0],1))),axis=1)
  n_top=len(crosssection)
  zmax=dz*n_top
  z_flange=dz*n_flange
  ptot=np.concatenate(list(p3d+[0,0,dz*i] for i in range(n_flange,n_top+1)),axis=0)
  ntot=np.concatenate(list(n3d for i in range(n_flange,n_top+1)),axis=0)
  dztot=np.minimum(ptot[:,2:],zmax)-np.maximum(ptot[:,2:]-dz,0)
  ptot[ptot[:,2] > zmax ,2]=zmax  
#  ptot_bottom=ptot-[0,0,1]*dztot
  dp2d=np.sum((p2d[:,:-1]-np.roll(p2d[:,:-1],-1,axis=0))**2,1)**0.5
  def f_o_w(z):
    o=np.interp(z,dz*np.arange(n_flange+1,len(crosssection)+0.5),[b.offset for [b]in crosssection[n_flange:]])
    w=np.interp(z,dz*np.arange(n_flange+1,len(crosssection)+0.5),[b.width for [b] in crosssection[n_flange:]])
    return o,w  
  otot,wtot=f_o_w(ptot[:,2:])
  ptot_offset=ptot+ntot*otot
  printer.extrudePolygon(ptot_offset,extrusionWidth=0.5,extrusionHeight=0.2)
#  printer.extrudePolygon(ptot_offset,extrusionWidth=0.5,extrusionHeight=0.2)
  t=np.array([p for path in printer.paths for *p,w,h in path ]) 
#  fig = plt.figure()
#  ax = plt.axes(projection='3d')p
  plt.close()
  fig = plt.figure()
  ax = fig.gca(projection='3d')
  for path in printer.paths:
    ax.plot3D(*np.array(path)[:,:3].transpose(), 'gray')
  plt.show()
#  plot_()
  pass

import os
import socket
from math import acos,pi,sin,cos,sqrt
on_ipad=socket.gethostname()=="iPad"
if on_ipad:
  from pylab import *
import operator
cookiecutterindex=5
crosssectionindex=1
def show_plot():
  axis('off')
  axes().set_aspect('equal', 'datalim')	
  subplots_adjust(left=0, right=1, top=1, bottom=0)
  show()
  close()
class segment(object):
    def __init__(self,l,ang):
        self.l=l
        self.ang=ang
def sumangles(a,b):
    return rotate(a,b)
def rotate(v,a):
    return(a[0]*v[0]-a[1]*v[1],a[1]*v[0]+a[0]*v[1])
     
def doubleangle(a):
    return sumangles(a,a)
def halfangle(a):
    return (sqrt(0.5+a[0]/2.0),(1.0 if(a[1]>0) else -1.0)* sqrt(0.5-a[0]/2.0))
def cossin(x):
    return (cos(x),sin(x))
def angle(cs):
    return atan2(cs[1],cs[0])
n=50
pi2=pi*2
t_=map(lambda i:float(i)/n,range(n+1))
t1=map(lambda t:(sin(t*pi2),cos(t*pi2)),t_)
hsegments=[segment(0.45,45.0/180*pi),
          segment(10.0,-180.0/180*pi),
          segment(6.91,10.0/180*pi),
          segment(1.1,-110.0/180*pi),
          segment(6.91,10.0/180*pi),
          segment(10.0,-180.0/180*pi),
          segment(0.45,45.0/180*pi)]
dsegments=[]
n=9
a=150.0
b=a-360.0/n
for i in range(n):
  dsegments+=[segment(1.0,b/180*pi),
          segment(2.0,-a/180*pi)]      
tsegments=[segment(0.75,-40.0/180*pi)]
n=4
a=140.0
b=a
for i in range(n):
  tsegments+=[segment(3,0.0),
              segment(1.5,-b/180*pi),
             segment(0.6,0.0),
               
          segment(1.0,a/180*pi)]    
tsegments=tsegments[:-3]
tsegments+=[segment(1.5,-140.0/180*pi),segment(12.4-0.969,0)]
for i in range(len(tsegments)-2,-1,-1):
    tsegments.append(tsegments[i])
            
esegments=[segment(5,125.0/180*pi),
          segment(15,-220.0/180*pi),
          segment(3,90.0/180*pi),
          segment(2,20.0/180*pi),
          segment(3,-170.0/180*pi),
          segment(5,-20.0/180*pi),
          segment(5,90.0/180*pi),
          segment(15,-90.0/180*pi),
          segment(22.913,-90.0/180*pi),
          segment(4,-160.0/180*pi),
          segment(3,80.0/180*pi),
          segment(13.297,-25.0/180*pi),
          segment(0.4,10.0/180*pi),
          ]
csegments=[segment(1.0,2*pi),]
 
   
ssegments=[]
n=5
a=130.0
b=a-360.0/n
for i in range(n):
  ssegments+=[segment(0.5,b/180*pi),
              segment(2.0,0.0),
          segment(0.8,-a/180*pi),
          segment(2.0,0.0)]          
     
def segmentsToPolyline(segments,a=(1.0,0.0),p=(0.0,0.0),o=0.0,damax=pi/4,maxdev=0.01,lstart=0.0,lend=None):
    p=map(operator.add,p,rotate((0.0,o),a))
    t2=[]
    ltot=pathLength(segments)
    reverse=False
    if lend<>None:
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
    nSegments=len(segments)
#    print lstart,lend,ltot
    startfound=False
    while l<lend:
        s=segments[iSegment]
        if s.ang<>0:
          r=abs(float(s.l)/s.ang)
          if maxdev<r:
            maxang=2.0*acos(1.0-maxdev/r)
            n=int(round(abs(s.ang)/maxang+0.5))
#            print "ndev=%d,r=%f,maxdev=%f,s.ang=%f,maxang=%f"%(n,r,maxdev,s.ang,maxang)
          else:
          	n=1
          da=s.ang/n
          if abs(da)>damax:
            n=int(round(abs(s.ang)/damax+0.5))
            da=s.ang/n
          da1=cossin(da)
          da2=halfangle(da1)
          dl=rotate(((float(s.l)-o*s.ang)/n*da2[1]/(da/2.0),0),da2)
        else:
            n=1
            da=0
            da1=(1.0,0.0)
            dl=(float(s.l),0.0)
        true_dl=float(s.l)/n
#        print "n=",n
        dl=rotate(dl,a)
        for i in range(n):
            l+=true_dl
            if not startfound:
            	if l>lstart:
            	  startfound=True
            	  dlfraction=1.0-(l-lstart)/true_dl
            	  t2.append((p[0]+dlfraction*dl[0],p[1]+dlfraction*dl[1],0.0))
            p=(p[0]+dl[0],p[1]+dl[1],l-lstart)
            if startfound:
            	if l>lend:
            		dlfraction=-(l-lend)/true_dl
            		t2.append((p[0]+dlfraction*dl[0],p[1]+dlfraction*dl[1],lend-lstart))
            		break
            	else:
            		t2.append(p)  
            dl=rotate(dl,da1) 
        a=rotate(a,cossin(s.ang))
        iSegment+=1
        if iSegment>=nSegments:
        	iSegment-=nSegments
#   print angle(a)*180/pi,p 
#    print l
    if reverse:
    	return reversed(t2)
    else:
    	return t2
def pathLength(segments):
	result=0
	for segment in segments:
		result+=segment.l
	return result
def minmaxxy(t):
    p=t[0]
    maxx=p[0]
    minx=maxx
    maxy=p[1]
    miny=maxy
    for p in t[1:]:
        maxx=max(maxx,p[0])
        minx=min(minx,p[0])
        maxy=max(maxy,p[1])
        miny=min(miny,p[1])
    return (minx,maxx,miny,maxy)
def fill(minx,maxx,n):
	w=maxx-minx
	dx=float(w)/n
	x=minx+dx/2
	result=[(x,dx)]
	for i in range(n-1):
		x+=dx
		result.append((x,dx))
	if n>3:
	  result=[result[1]]+[result[0]]+result[n-2:]+result[2:n-2]
	return result	
def skirt(polyline,r=3,d=3):
	xmin,xmax,ymin,ymax=minmaxxy(polyline)
	dx,dy=xmax-xmin,ymax-ymin
	return((xmin-d,ymin-d-r),(segment(dx+d*2,0),segment(r*pi/2,pi/2),\
	                    segment(dy+d*2,0),segment(r*pi/2,pi/2),\
	                    segment(dx+d*2,0),segment(r*pi/2,pi/2),\
	                    segment(dy+d*2,0),segment(r*pi/2,pi/2)))
def scalePath(path,scale=1.0):
	return [segment(s.l*scale,s.ang) for s in path]
def mirrorPath(path):
	return[segment(s.l,-s.ang)for s in path]
def crossProduct(v1,v2):
	return(v1[0]*v2[1]-v2[0]*v1[1])
def vectorSum(v1,v2):
	return(map(operator.add,v1,v2))
def pathArea(path):
  areaSum=0.0
  currentAngle=[1.0,0.0]
  currentCoordinate=[0.0,0.0]
  for segment in path:
    deltaAngle=cossin(segment.ang)
    halfDeltaAngle=halfangle(deltaAngle)
    if segment.ang<>0.0:
      secantLength=segment.l*halfDeltaAngle[1]/(0.5*segment.ang)
      circleSectionArea=(float(segment.l)/segment.ang)**2*(segment.ang/2.0-halfDeltaAngle[0]*halfDeltaAngle[1])
    else:
      secantLength=segment.l
      circleSectionArea=0.0
    deltaCoordinate=rotate((secantLength,0.0),sumangles(currentAngle,halfDeltaAngle))
    triangleArea=0.5*crossProduct(currentCoordinate,deltaCoordinate)
    areaSum+=triangleArea+circleSectionArea
#    print "circleSection",circleSectionArea
    currentCoordinate=vectorSum(currentCoordinate,deltaCoordinate)
    currentAngle=sumangles(currentAngle,deltaAngle)
  return areaSum
	
def normalizePath(path,p0,area):
	actualarea=pathArea(path)
	rotang=(1.0,0.0)
	if actualarea<0:
		path=mirrorPath(reversed(path))
		actualarea*=-1
		rotang=rotate(rotang,(-1.0,0.0))
	scale=sqrt(area/actualarea)
	xmin,xmax,ymin,ymax=minmaxxy(segmentsToPolyline(path))
	dx=xmax-xmin
	dy=ymax-ymin
	if dx>dy:
		rotang=rotate(rotang,(0.0,1.0))
	path=scalePath(path,scale)
	xmin,xmax,ymin,ymax=minmaxxy(segmentsToPolyline(path,a=rotang))
	dx=xmax-xmin
	dy=ymax-ymin
	return vectorSum(p0,(-(xmin+dx/2.0),-(ymin+dy/2.0))),rotang,path     
	        
p0,a,segments=normalizePath((tsegments,dsegments,esegments,ssegments,hsegments,csegments)[cookiecutterindex],p0=(100,100),area=2000.0)
t2=[]#segmentsToPolyline(segments,p=p0,a=a)
for o in range(1):
  t2+=segmentsToPolyline(segments,p=p0,a=a,o=-o,lstart=10*o-20)
pskirt0,skirtsegments=skirt(t2,r=5,d=0)
t2=segmentsToPolyline(skirtsegments,p=pskirt0,o=0,lstart=-30)+t2
area=minmaxxy(t2)
#print t2[-1],area

crosssection1= [fill(-w2,w2,n) for w2,n in ((3.6/2,4),(4.0/2,5),(4.4/2,6),(4.6/2,5))]+ \
      [((0.0,cw),(-w2+ww/2,ww),(w2-ww/2,ww)) for w2,ww,cw in[ \
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
      [[(0.0,1.0-0.5*i/50.0)]for i in range(50+1)]
      
crosssection2= [fill(-2.0,-0.2,2)]+\
      [fill(-w2,0,n) for w2,n in ((4.4/2,3),(4.6/2,4))]+ \
      [((-cw/2,cw),(-w2+ww/2,ww)) for w2,ww,cw in[ \
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
        fill(-1.2,0,2)]+\
      [[(-(1.0-0.5*i/50.0)/2.0,1.0-0.5*i/50.0)]for i in range(50+1)]
crosssection=(crosssection1,crosssection2)[crosssectionindex]
#for layer in crosssection:print layer
#print "forward",pathArea(segments)
#print "mirrored",pathArea(mirrorPath(esegments))
#print "reversed",pathArea(reversed(esegments))
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
  x,y,l=t[0]
  if (abs(x-lastx)>eps) or (abs(y-lasty)>eps) or (abs(z-lastz)>eps):
#  	print "xyz,lastxyz",x,y,z,lastx,lasty,lastz,lastx==x,lasty==y,lastz==z
  	output.write("G1 X%(X)0.3f Y%(Y)0.3f Z%(Z)0.3f F%(F)0.3f\n"%{"X":x,"Y":y,"Z":z,"F":travel_speed*60})
  	lastx,lasty,lastz,lastspeed=x,y,z,travel_speed
  for x,y,l in t[1:]:
    output.write("G1 X%(X)0.3f Y%(Y)0.3f E%(E)0.5f"%{"X":x,"Y":y,"E":laste+l*extrusion_ratio})
    if speed<>lastspeed:
  	  output.write(" F%(F)0.3f\n"%{"F":speed*60})
  	  lastspeed=speed
    else:
  		output.write("\n")
    lastx,lasty=x,y
  laste+=t[-1][2]*extrusion_ratio
  return

def extrudePath(output,path,p0,o,a,lstart,speed,\
                layer_height,extrusion_width,z):
  global laste
  output.write("G92 E0\n")
  laste=0.0
  t=segmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart,\
                       lend=lstart+retract_perimeter_length)
  extrudePolyline(output,t,speed=speed,extrusion_ratio=retraction/retract_perimeter_length,z=z)

  t=segmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length)
  extrusion_crossection=layer_height*extrusion_width
  extrudePolyline(output,t,speed=speed,\
       extrusion_ratio=extrusion_crossection/filament_crossection*extrusion_multiplier,z=z)

  t=segmentsToPolyline(path,p=p0,o=o,a=a,lstart=lstart+retract_perimeter_length,\
                       lend=lstart+2*retract_perimeter_length)
  extrudePolyline(output,t,speed=speed,extrusion_ratio=-retraction/retract_perimeter_length,z=z)
  return

preamble="""; generated by %(program_name)s v%(version)s %(datetime)s
; layer_height = %(layer_height)0.3f
; perimeter_speed = %(perimeter_speed)f
; travel_speed = %(travel_speed)f
; nozzle_diameter = %(nozzle_diameter)f
; filament_diameter = %(filament_diameter)f
; extrusion_multiplier = %(extrusion_multiplier)f

G21 ; set units to millimeters
M107
M190 S%(bed_temperature)0.0f ; wait for bed temperature to be reached
M104 S%(hotend_temperature)0.0f ; set temperature

M109 S%(hotend_temperature)0.0f ; wait for temperature to be reached
G90 ; use absolute coordinates
G92 E0
M82 ; use absolute distances for extrusion
"""%{
"program_name":program_name,
"version":program_version,
"datetime":strftime("on %Y/%m/%d at %H:%M:%S",gmtime()),
"layer_height":layer_height,
"perimeter_speed":perimeter_speed,
"travel_speed":travel_speed,
"nozzle_diameter":nozzle_diameter,
"filament_diameter":filament_diameter,
"extrusion_multiplier":extrusion_multiplier,
"bed_temperature":first_layer_bed_temperature,
"hotend_temperature":first_layer_hotend_temperature        
 }
n_flange=(20,16)[crosssectionindex]
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
  extrudePath(output,skirtsegments,speed=perimeter_speed*first_layer_speed_ratio,\
	            p0=pskirt0,a=(1.0,0.0),o=i*0.75,lstart=lstart,
	            extrusion_width=0.75,layer_height=layer_height,z=z)
  lstart+=dlstart
speed_ratio=first_layer_speed_ratio
for layer in crosssection[:n_flange]:
  totalextrusionlength=len(layer)*pathLength(segments)
  speed=min(totalextrusionlength/min_layer_time,perimeter_speed)*speed_ratio
  for o,w in layer: 
    extrudePath(output,segments,speed=speed,\
	            p0=p0,a=a,o=o,lstart=lstart,
	            extrusion_width=w,layer_height=layer_height,z=z)
    lstart+=dlstart
  speed_ratio=1.0
  z+=layer_height
for layer in crosssection[n_flange:]:
  totalextrusionlength=len(layer)*pathLength(segments)
  speed=min(totalextrusionlength/min_layer_time,perimeter_speed)*speed_ratio
  for o,w in layer: 
    extrudePath(output,segments,speed=speed,\
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
			plot([r,l,l,r,r],[t,t,b,b,t],style)

def plot_layers(crosssection,x0=0,z0=0.0,dz=0.2,style="r"):
	z=z0+dz
	for layer in crosssection:
		for x,w in layer:
			plot_box(x0+x,z,w,dz,style)
		z+=dz
def fz(n,b1=50.0/8,w0=0.2,w1=0.1):
	a=w0
	b=(w0-w1)/b1**2
	c=2.0*sqrt(a*b)
	ecn=exp(-c*n)
	z=(c*(1-ecn))/(2*b*(ecn+1))
	return z
	
def fn(z=50.0/8,b1=None,w0=0.2,w1=0.1):
	if b1==None :b1=z
	a=w0
	b=(w0-w1)/b1**2
	c=2.0*sqrt(a*b)
	n=-log((c-2.0*b*z)/(c+2.0*b*z))/c
	return n
def fminExtrusionWidth(nozzleDiameter,layerHeight):
	minExtrusionWidth=nozzleDiameter+layerHeight*pi/4.0#Nozzle width + area of two semicircles of layer height diameter to either side of nozzle
	return(minExtrusionWidth)
def  plot_():
	plot([p[0] for p in t2],[p[1] for p in t2])
	show_plot()
	dz=0.2
	h_blade=(len(crosssection)-n_flange)*dz
	w_blade_top=crosssection[-1][0][1]
	w_blade_bottom=crosssection[n_flange][0][1]
	n_blade=int(h_blade/dz+1.5)
	plot_layers(crosssection[:n_flange],x0=-5.5,z0=0,dz=dz,style="r")	
	plot_layers(crosssection[n_flange:],x0=-5.5,z0=n_flange*dz,dz=dz,style="b")
	for i in range(4):
	  plot_layers(crosssection[:n_flange],x0=5.5*i,z0=0,dz=dz,style="r")	
	  for j in range(n_blade):
	  	z=(j+0.25*i)*dz
	  	h_layer=min(z,dz)if z<h_blade else max(dz-(z-h_blade),0.0)
	  	if dz-(z-h_blade)<0:print "negative layer height at z=%f"%(z)
	  	z=min(z,h_blade)
	  	w_layer=w_blade_bottom+(w_blade_top-w_blade_bottom)*(z-0.5*h_layer)/h_blade
	  	plot_box(5.5*i-0.5*(w_layer),z+n_flange*dz,w_layer,h_layer,"g")
	show_plot()
if on_ipad:
	plot_()
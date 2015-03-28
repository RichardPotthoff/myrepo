# Function Plotter
import canvas
import console
import operator
from math import sin, cos, pi,sqrt,atan2,acos,exp,log
class segment(object):
    def __init__(self,l,ang):
        self.l=l
        self.ang=ang
         
def draw_grid(min_x, max_x, min_y, max_y):
    w, h = canvas.get_size()
    scale_x = w / (max_x - min_x)
    scale_y = h / (max_y - min_y)
    scale_x = min(scale_x,scale_y)
    scale_y=scale_x
    min_x, max_x = round(min_x), round(max_x)
    min_y, max_y = round(min_y), round(max_y)
    canvas.begin_updates()
    canvas.set_line_width(1)
    canvas.set_stroke_color(0.7, 0.7, 0.7)
    #Draw vertical grid lines:
    x = min_x
    while x <= max_x:
        if x != 0:
            draw_x = round(w / 2 + x * scale_x) + 0.5
            canvas.draw_line(draw_x, 0, draw_x, h)
        x += 0.5
    #Draw horizontal grid lines:
    y = min_y
    while y <= max_y:
        if y != 0:
            draw_y = round(h/2 + y * scale_y) + 0.5
            canvas.draw_line(0, draw_y, w, draw_y)
        y += 0.5
    #Draw x and y axis:
    canvas.set_stroke_color(0, 0, 0)
    canvas.draw_line(0, h/2, w, h/2)
    canvas.draw_line(w/2, 0, w/2, h)
    canvas.end_updates()
 
def plot_function(t_, color, min_x,max_x,min_y,max_y):
    #Calculate scale, set line width and color:
    w, h = canvas.get_size()
    scale_x = w / (max_x - min_x)
    scale_y = h / (max_y - min_y)
    scale_x = min(scale_x,scale_y)
    scale_y=scale_x
    origin_x, origin_y = -scale_x*min_x,-scale_y*min_y
    canvas.set_stroke_color(*color)
    canvas.set_line_width(2)
    #Draw the graph line:
    x = t_[0][0]
    y = t_[0][1]
    canvas.move_to(origin_x + scale_x * x, 
                   origin_y + scale_y * y)
    for p in t_[1:]:
        x=p[0]
        y=p[1]
        draw_x = origin_x + scale_x * x
        draw_y = origin_y + scale_y * y
        canvas.add_line(*(draw_x, draw_y))
    canvas.set_fill_color(*color)
    canvas.draw_path()
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
#Set     up the canvas size and clear any text output:
console.clear()
canvas.set_size(688, 688)
#Draw the grid:v
area = (-10, 10, -10, 10)
draw_grid(*area)
#Draw 4 different graphs (sin(x), cos(x), x^2, x^3):
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
def plot_box(center,size,color,area):
	xmin,xmax=center[0]-size[0]/2.0,center[0]+size[0]/2.0
	ymin,ymax=center[1]-size[1]/2.0,center[1]+size[1]/2.0
	plot_function(((xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)),color,*area)
def plot_brick(center,size,color,area):
	xmin,xmax=center[0]-size[0]/2.0,center[0]+size[0]/2.0
	ymin,ymax=center[1]-size[1],center[1]
	d=size[0]/4.0
	plot_function(((xmin-size[1]+d,ymin+d),(xmax-size[1]-d,ymin-d),(xmax,ymax),(xmin,ymax),(xmin-size[1]+d,ymin+d)),color,*area)
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
	        
p0,a,segments=normalizePath(esegments,p0=(100,100),area=2000.0)
t2=[]#segmentsToPolyline(segments,p=p0,a=a)
for o in range(1):
  t2+=segmentsToPolyline(segments,p=p0,a=a,o=-o,lstart=10*o-20)
pskirt0,skirtsegments=skirt(t2,r=5,d=0)
t2=segmentsToPolyline(skirtsegments,p=pskirt0,o=0,lstart=-30)+t2
area=minmaxxy(t2)
#print t2[-1],area

crosssection= [fill(-w2,w2,n) for w2,n in ((3.6/2,4),(4.0/2,5),(4.4/2,6),(4.6/2,5))]+ \
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

filelocation="cookie.txt"
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
for layer in crosssection:
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
def plot_layers(crosssection):
	z=0.0
	dz=0.2
	for layer in crosssection:
		for x,w in layer:
			plot_box((x,z),(w,dz),(1,0,0),(-3,3,-0.3,14.4))
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
a1=(45.0-4)/2
b1=(55.0-14.0)/2
a1*=1.0
b1*=1.0
d=0.7
a2=a1-d
b2=b1-d
t3=[[a1*cos(pi/2/100*i),b1*sin(pi/2/100*i)]for i in range(0,101)]
t4=[[a2*cos(pi/2/100*i),b2*sin(pi/2/100*i)]for i in range(0,101)]
zoom=0.8
area=(0,40*zoom,0,40*zoom)
#plot_function(t2,(0,0,1), *(0,200,0,200))
plot_function(t3,(0,0,1), *area)
plot_function(t4,(0,1,0), *area)
#plot_layers(crosssection)	

#print segmentslength(esegments)
def fyEllipse(x,a,b):
	if x>a:return 0.0
	return b*sqrt(1-(x/a)**2)
def fxyEllipse(m_,c_,a_,b_):
	A=b_**2+(a_*m_)**2
	B=2.0*a_**2*m_*c_
	C=-B/(2*A)
	D=((a_*b_)**2-(a_*c_)**2)/A+C**2
	if D<0.0:return None 
	D=sqrt(D)
	x1=C-D
	x2=C+D
	return[(x1,m_*x1+c_),(x2,m_*x2+c_)]
class DummyClass:pass
db1=0.15
layers=[DummyClass()]
layers[0].x1=0
layers[0].x2=a1
layers[0].z=0
layers[0].dz=0.2
layers[0].bricks=[]
layers[0].blocks=[]
for i in range(1,int(fn(b1))+1):
	thisLayer=DummyClass()
	z=fz(i-0.5,b1=b1+db1)
	x1=fyEllipse(z,b2,a2)
	x2=fyEllipse(z,b1,a1)
	dx=x2-x1
	dz=fz(i,b1=b1+db1)-fz(i-1,b1=b1+db1)
	thisLayer.x1=x1
	thisLayer.x2=x2
	thisLayer.z=fz(i,b1=b1+db1)
	thisLayer.dz=dz
	thisLayer.blocks=[]
	thisLayer.bricks=[]
	layers.append(thisLayer)
	
for layer in layers:
	plot_box(((layer.x1+layer.x2)/2.0,layer.z-layer.dz/2),(layer.x2-layer.x1,layer.dz),(1,0,0), area)	
	
for c_ in range(int(b2/nozzle_diameter)):
	x,z=fxyEllipse(1.0,b2-0.05-c_*nozzle_diameter,a2+0.1,b2+0.1)[1]
	slope=x/z*((b2+0.2)/(a2+0.2))**2
	if slope>1:break 
	n=int(fn(z,b1=b1+db1))+1
	dz=fz(n,b1=b1+db1)-z
	for i in range(n,n-3,-1):
		zl=fz(i,b1=b1+db1)
		layer=layers[i]
#		print n,i,z,zl,x,layer.x1,layer.x2
		layer.x1=max(layer.x1,x+zl-z+nozzle_diameter/2-layer.dz/2)
	layer=layers[n]
	brick=DummyClass()
	brick.x=x+dz
	brick.A=(nozzle_diameter*1.14)**2*pi/4.0
	layer.bricks.append(brick)
for layer in layers:
	minWidth=fminExtrusionWidth(nozzle_diameter,layer.dz)
	maxWith=2.0*minWidth
	nPaths=int((layer.x2-layer.x1)/(minWidth*4.0/3.0)+0.5)
	extrusionWidth=(layer.x2-layer.x1)/nPaths
	x=layer.x2-0.5*extrusionWidth
	while x>layer.x1:
		block=DummyClass()
		block.x=x
		block.extrusionWidth=extrusionWidth
		block.A=extrusionWidth*layer.dz
		layer.blocks.append(block)
		x-=extrusionWidth
for layer in layers:
	for brick in layer.bricks:
		plot_brick((brick.x,layer.z),(nozzle_diameter,nozzle_diameter),(0,0,1), area)
	for block in layer.blocks:
		plot_box((block.x,layer.z-layer.dz/2),(block.extrusionWidth,layer.dz),(0,1,0), area)		
filelocation="egg.txt"
z=0.0
z+=layer_height
output=open(filelocation,"w")
output.write(preamble)
output.write("G1 Z%(Z)0.3f F%(F)0.3f\n"%{"F":travel_speed*60.0,"Z":z})
lastz=z
lstart=0.0
dlstart=0.1
xSkirt=a2-5.0
skirtsegments=[segment(xSkirt*2.0*pi,2.0*pi)]
pskirt0=[0.0,xSkirt]
partOffsets=[[100.0,100.0-a1-2.5],[100.0,100.0+a1+2.5]]
for i in range(-1,2,1):
  extrudePath(output,skirtsegments,speed=perimeter_speed*first_layer_speed_ratio,\
	            p0=vectorSum(pskirt0,partOffsets[0]),a=(1.0,0.0),o=i*0.75,lstart=lstart*a1*pi*2,
	            extrusion_width=0.75,layer_height=layer_height,z=z)
  lstart+=dlstart
speed_ratio=first_layer_speed_ratio
for layer in layers[:5]:
	blocks=layer.blocks
	bricks=layer.bricks
	x=(layer.x1+layer.x2)/2.0
	segments=[segment(x*2.0*pi,2.0*pi)]
	lPath=pathLength(segments)
	totalextrusionlength=(len(bricks)+len(blocks))*len(partOffsets)*lPath
	speed=min(totalextrusionlength/min_layer_time,perimeter_speed)*speed_ratio
	p0=(0.0,x)
	for partOffset in partOffsets:
		lstart_=lstart
		for block in blocks: 
			extrudePath(output,segments,speed=speed,\
			  p0=vectorSum(partOffset,p0),a=a,o=block.x-x,lstart=lstart_*lPath,
			  extrusion_width=block.extrusionWidth,layer_height=layer.dz,z=layer.z)
			lstart_+=dlstart
		for brick in bricks[:1]:
			extrudePath(output,segments,speed=speed,\
			  p0=vectorSum(partOffset,p0),a=a,o=brick.x-x,lstart=lstart_*lPath,
			  extrusion_width=brick.A/layer.dz,layer_height=layer.dz,z=layer.z)
	for brick in bricks[1:]:
		lstart_+=dlstart
		for partOffset in partOffsets:
			extrudePath(output,segments,speed=speed,\
			  p0=vectorSum(partOffset,p0),a=a,o=brick.x-x,lstart=lstart_*lPath,
			  extrusion_width=brick.A/layer.dz,layer_height=layer.dz,z=layer.z)
	speed_ratio=1.0
	lstart+=dlstart
	z+=layer_height
output.write("G1 Z%(Z)0.3f\n"%{"Z":z})
output.write("G28 X0\n")
	
output.close()

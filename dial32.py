import Image, ImageDraw
from math import pi,sin,cos

scale=1600/93
r=800

im = Image.new('L',(2*r+int(18*scale),2*r+int(18*scale)),'white')

draw = ImageDraw.Draw(im)
center=(im.size[0]/2,im.size[1]/2)
draw.arc((center[0]-r,center[1]-r,center[0]+r,center[1]+r),0,360,fill=0)
r0=scale*22/2
draw.arc((center[0]-r0,center[1]-r0,center[0]+r0,center[1]+r0),0,360,fill=0)
draw.line((center[0]-r0,center[1],center[0]+r0,center[1]),fill=0)
draw.line((center[0],center[1]-r0,center[0],center[1]+r0),fill=0)
for i in range(32):
  ang=i/32*2*pi
  s=sin(ang)
  c=cos(ang)
  r1=r-[10,6,8,6][i%4]*scale
  r2=r+[0,8,0,8][i%4]*scale
  draw.line((center[0]+c*r1,center[1]+s*r1,center[0]+c*r2,center[1]+s*r2), fill=0,width=5)
  if (i%4)==3:
    draw.arc((center[0]-r2,center[1]-r2,center[0]+r2,center[1]+r2),int(ang*180/pi),int((ang+pi/8)*180/pi),fill=0)

#  draw.text((center[0]+c*r1,center[1]+s*r1),'{:d}'.format(i))
del draw

# write to stdout
im.save('test.png', "PNG",dpi=(96*4,96*4))

#!/usr/bin/env python3


from pylab import *
import matplotlib
from six.moves import range
def show_plot():
  axis('off')
  axes().set_aspect('equal', 'datalim')	
  subplots_adjust(left=0, right=1, top=1, bottom=0)
  show()
  close()
def  hilbert(n):
  a=1+1j
  b=conj(a)
  z=array([0])
  for k in range(n):
    w=1j*conj(z)
    z=concatenate([w-a,z-b,z+a,b-w])/2.0
  return z
def moore(n):
  z=-conj(hilbert(n))
  w=concatenate([z+1+1j,z-1+1j])
  return concatenate([w,-1.0*w])/2.0
def curvature(x):
  deltax=roll(x,-1)-x
  length=abs(deltax)
  curvature=2*(conj(roll(deltax,1))*deltax).imag/(length*roll(length,1)*abs(deltax+roll(deltax,1)))
  return curvature
def area_length(x):
  deltax=roll(x,-1)-x
  area=sum(conj(x)*deltax).imag/2.0#the cross product
  length=sum(abs(deltax))
  return (area,length)
def blend(x,y,alpha):
  return alpha*y+(1.0-alpha)*x
z4=moore(3)
a4,l4=area_length(z4)
r4=(a4/pi)**0.5
z6=moore(6)
n=8
zu=concatenate([[z4[i-1]*(n-k)+z4[i]*k for k in range(1,n+1)] for i in range(len(z4))])/n
zu=roll(zu,-n//2+1)
#zu=z6
zuf=fft(zu)
z1f=copy(zuf)
nf=len(z1f)//8
z1f[nf:len(z1f)-1-nf]=0
z1i=ifft(z1f)
plot(z4.real,z4.imag)
show_plot()
print("area=%f, length=%f"%(area_length(z4)))
plot(z1i.real,z1i.imag)
show_plot()
print("area=%f, length=%f"%(area_length(z1i)))
plot(z1i[7:128].real,z1i[7:128].imag,label='z1i')
plot(z4[:16].real,z4[:16].imag,label='z4')
zj=z1i
#zj=zu
for i in range(3):
  zj=0.5*(roll(zj,-1)+roll(zj,1))
plot(zj[7:128].real,zj[7:128].imag,label='zj')
#zk=ifft([zuf[i]*(0.5*(1+cos(pi*i*2/len(zu))))**(exp(2)) for i in range(len(zu))])
rcos=(0.5*(1+cos(pi*2*array(list(range(len(zu))))/len(zu))))
zk=ifft(zuf*rcos**exp(2))
plot(zk[7:128].real,zk[7:128].imag,label='zk')
plt.legend()
show_plot()
plot(zj.real,zj.imag)
plot(zk.real,zk.imag)
show_plot()

print("area=%f, length=%f"%(area_length(zj)))
zjf=fft(zj)
hj=array([zjf[i]/zuf[i] if zuf[i]!=(0.0+0.0j) else 0.0+0.0j for i in range(len(zu))])
zc=exp(1j*2*pi*arange(len(zu))/len(zu))*sqrt(1.9/pi)
zcf=fft(zc)
print("circle fourier=",zcf[:5],zcf[-5:])
plot (abs(hj))
#plot (angle(hj))
for x in (-2,0,1.85,4,8):
  plot(rcos**exp(x))
show()
close()
zuabs=abs(zu)
k=argmax(zuabs)
#print "max=%f,index=%d,max(zuabs)=%f"%(zuabs[k],k,max(zuabs))
scale=4.0
z=arange(0,13.5*scale,scale)
nz=0.5
#z[-1]=79
#z[-1]=9.4*scale
print(z[-1])
xa=array([sqrt(2.0/area_length(ifft(zuf*rcos**exp(10*(y1/(10*scale)+0.1)**nz+2)))[0] )for y1 in z])
#plot(xa,z)
rzu=r4*len(zuf)
zuf[1]-=rzu
rzu_=zeros(zuf.shape)
rzu_[1]=rzu
x=array([(ifft(zuf*rcos**exp(10*(y1/(10*scale)+0.1)**nz+2)+rzu_))[[k,len(zu)//4,0]] for y1 in z])
#x=array([blend(ifft(zuf*rcos**exp(10*(y1/(10*scale)+0.1)**nz+2)),zc,(0.5*(1+cos(pi*(1-y1/z[-1]))))**6)[[k,len(zu)//4,0]] for y1 in z])
plot(abs(x)*20.0,z)
axes().set_aspect('equal', 'datalim')	
show()
close()

for y1 in z:  
  xf=zuf*rcos**exp(10*(y1/(10*scale+0.1))**nz+2)
  xf[1]+=rzu
#  if y1==z[-1]:xf=zcf
  
  x=ifft(xf)
#  x=blend(ifft(xf),zc,(0.5*(1+cos(pi*(1-y1/z[-1]))))**6)
#  x=x*sqrt(2.0/area_length(x)[0])
  plot(x.real,x.imag)
zuf[1]+=rzu
show_plot()
test=fft(x)
print("last fft:",test[:5],test[-5:])
print("nzu=%d, nz=%d, nz6=%d"%(len(zu),len(z4),len(z6)))
plot(abs(roll(x,-1)-x))
show()



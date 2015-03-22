from pylab import *
import matplotlib
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
z=moore(4)
n=8
zu=concatenate([[z[i-1]*(n-k)+z[i]*k for k in range(1,n+1)] for i in range(len(z))])/n
zuf=fft(zu)
z1f=copy(zuf)
nf=len(z1f)/8
z1f[nf:len(z1f)-1-nf]=0
z1i=ifft(z1f)
plot(z.real,z.imag)
show_plot()
plot(z1i.real,z1i.imag)
show_plot()
plot(z1i[7:128].real,z1i[7:128].imag)
plot(z[:16].real,z[:16].imag)
zj=z1i
#zj=zu
for i in range(3):
  zj=0.5*(concatenate([zj[1:],zj[:1]])+concatenate([zj[-1:],zj[:-1]]))
plot(zj[7:128].real,zj[7:128].imag)
#zk=ifft([zuf[i]*(0.5*(1+cos(pi*i*2/len(zu))))**(exp(2)) for i in range(len(zu))])
rcos=(0.5*(1+cos(pi*2*array(range(len(zu)))/len(zu))))
zk=ifft(zuf*rcos**exp(2))
plot(zk[7:128].real,zk[7:128].imag)
show_plot()
plot(zj.real,zj.imag)
plot(zk.real,zk.imag)
show_plot()
print sum(abs(concatenate([zj[1:],zj[:1]])-zj))
print sum(abs(concatenate([z1i[1:],z1i[:1]])-z1i))
zjf=fft(zj)
hj=array([zjf[i]/zuf[i] if zuf[i]<>(0.0+0.0j) else 0.0+0.0j for i in range(len(zu))])
plot (abs(hj))
#plot (angle(hj))
plot([(0.5*(1+cos(pi*i*2/len(zu))))**exp(-2) for i in range(len(zu))])
plot([(0.5*(1+cos(pi*i*2/len(zu))))**exp(0) for i in range(len(zu))])
plot([(0.5*(1+cos(pi*i*2/len(zu))))**exp(1.85) for i in range(len(zu))])
plot([(0.5*(1+cos(pi*i*2/len(zu))))**exp(4) for i in range(len(zu))])
plot([(0.5*(1+cos(pi*i*2/len(zu))))**exp(8) for i in range(len(zu))])
show()
close()
zuabs=abs(zu)
k=argmax(zuabs)
print "max=%f,index=%d,max(zuabs)=%f"%(zuabs[k],k,max(zuabs))
z=arange(0,100.0,6.5)
x=array([ifft(zuf*rcos**exp(y1/6.5+2))[k] for y1 in z])
plot(abs(x)*40.0,z)
k=len(zu)/4
x=array([ifft(zuf*rcos**exp(y1/6.5+2))[k] for y1 in z])
plot(abs(x)*40.0,z)
axes().set_aspect('equal', 'datalim')	
show()
close()
for y1 in z:
  x=ifft(zuf*rcos**exp(y1/6.5+2))
  plot(x.real,x.imag)
show_plot()

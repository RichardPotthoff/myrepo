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
z1f=fft(zu)
nf=len(z1f)/8
z1f[nf:len(z1f)-1-nf]=0
z1i=ifft(z1f)
plot(z.real,z.imag)
show_plot()
plot(z1i.real,z1i.imag)
show_plot()
plot(z1i[7:128].real,z1i[7:128].imag)
plot(z[:16].real,z[:16].imag)
show_plot()


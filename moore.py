from pylab import *
import matplotlib
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
matplotlib.pyplot.a
plot(z.real,z.imag)
show()
close()
plot(z1i.real,z1i.imag)
show()
close()
plot(z1i[7:72].real,z1i[7:72].imag)
plot(z[:9].real,z[:9].imag)
show()
close()


import wave
import random
import struct
import datetime
import os
import sndhdr
import sound
#from math import pi,sin,cos
from pylab import *
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

m=400
noise_output = wave.open('noise2.wav', 'wb')
#noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))#for wave
noise_output.setparams((2, 2, 44100, 4096*m,'NONE', 'not compressed'))
d1 = datetime.datetime.now()
values = []
maxint=2**15-1
f=pi*2.0/44100*880
pi4=pi/4
z4=moore(3)
n=4
zu=concatenate([[z4[i-1]*(n-k)+z4[i]*k for k in range(1,n+1)] for i in range(len(z4))])/n
zu=roll(zu,-n//2+1)
print (len(zu))
zuf=fft(zu)
rcos=(0.5*(1+cos(pi*2*array(list(range(len(zu))))/len(zu))))
yf=zuf*rcos**exp(1)
y=ifft(yf)
value_str=b''.join([struct.pack('h',int(maxint*x)) for z in y for x in (real(z),imag(z))])
print(len(value_str))
noise_output.writeframes(value_str*m)
print(noise_output.getparams())

d2 = datetime.datetime.now()
print ((d2 - d1), "(time for writing frames)")

noise_output.close()

d3 = datetime.datetime.now()
print( (d3 - d2), "(time for closing the file)")
# Simple demo of playing a looping sound using the (currently undocumented) sound.Player class
noise_input = sound.Player('noise2.wav')
#noise_input = open((os.path.expanduser(os.path.join(os.path.dirname(os.__file__), "../Media/Sounds/game/Beep.caf"))),'rb')
print(noise_input.duration)
noise_input.number_of_loops=0
noise_input.play()
import photos
#img=photos.capture_image()
#img.save('osci.jpg')

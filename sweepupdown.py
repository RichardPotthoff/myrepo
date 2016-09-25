import wave
import random
import struct
import datetime
import os
import sndhdr
import sound
from math import pi,sin,cos,log,exp
from itertools import accumulate
from pydsm import iso226
def f2note(f):
	return log(f/440)/log(2)*12+49
def note2f(note):
	return 440.0*2.0**((note-49)/12)
f_40=iso226.iso226_spl_itpl()
def f_amp(note):
	return 10**(0.1*(f_40(note)-50))
f_table=iso226.tabled_f()
y_table=iso226.tabled_L_p(40)
y_f=list(map(f_40,map(f2note,f_table)))
print(f_table,y_f,y_table,list(map(f2note,f_table)))
for i in range(116):
	print ('key#%4d:%10.3f, amp:%7.3f, f_40(i):%7.3f'%(i,note2f(i),f_amp(i),f_40(i)))
maxint=2**15-1
noise_output = wave.open('updown.wav', 'wb')
samplerate=44100
sampleintervall=1/samplerate
noise_output.setparams((2, 2,samplerate , 0,'NONE', 'not compressed'))
d1 = datetime.datetime.now()
tmax=20
dt1=2
def omega(t):return 2*pi*440/16*2**(t/dt1)
def amplitude(t):return 0.25*exp(-((t-8)/(2.0*dt1))**2)
#def amplitude(t):return min(0.5,f_amp(t/dt1*12+1))
def sampletimes(tmax,dt):
	t=0
	while t<tmax:
		t+=dt
		yield t
	return
value_str=b''.join(struct.pack('hh',y,y) for x,t in zip(accumulate([sampleintervall*omega(t) for t in sampletimes(tmax,sampleintervall)]),sampletimes(tmax,sampleintervall)) for y in (int(amplitude(t)*sin(x)*maxint),))

print(len(value_str))
noise_output.writeframes(value_str)
print(noise_output.getparams())

d2 = datetime.datetime.now()
print ((d2 - d1), "(time for writing frames)")

noise_output.close()

d3 = datetime.datetime.now()
print( (d3 - d2), "(time for closing the file)")
# Simple demo of playing a looping sound using the (currently undocumented) sound.Player class
noise_input = sound.Player('updown.wav')
#noise_input = open((os.path.expanduser(os.path.join(os.path.dirname(os.__file__), "../Media/Sounds/game/Beep.caf"))),'rb')
print(noise_input.duration)
noise_input.number_of_loops=0
noise_input.play()
import photos
#img=photos.capture_image()
#img.save('osci.jpg')

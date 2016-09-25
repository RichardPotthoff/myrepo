import wave
import random
import struct
import datetime
import os
import sndhdr
import sound
from math import pi,sin,cos,log,exp
from itertools import accumulate
maxint=2**15-1
for note in range(13):
	noise_output = wave.open('weier%d.wav'%(note), 'wb')
	samplerate=44100
	sampleintervall=1/samplerate
	noise_output.setparams((1, 2,samplerate , 0,'NONE', 'not compressed'))
	d1 = datetime.datetime.now()
	enote=note/12.0
	f_min=440.0/16*2.**enote
	n=int(samplerate/f_min+0.5)
#	print(n)
	dphi=2.0*pi/n
	yA=[sin(i*dphi) for i in range(n)]
#	ab=[(0.6666**(i+enote),1<<i) for i in range(11)]
	ab=[(0.25*exp(-((i+enote-4)/2)**2),1<<i) for i in range(11)]	
	yB=[sum([a*yA[(i*f)%n]for (a,f)in ab]) for i in range(n)]
	ymax1=1.0/max(max(yB),abs(min(yB)))
	print ('ymax=',ymax1)
	ymax1=0.5625
	ymax1=2.0
	value_str=b''.join(struct.pack('h',y) for yWeier in yB for y in (int(yWeier*ymax1*maxint),))
	
#	print(len(value_str))
	noise_output.writeframes(value_str*int(0.25*f_min+0.5))
#	noise_output.writeframes(struct.pack('h',0)*200*n)
#	print(noise_output.getparams())
	
	d2 = datetime.datetime.now()
#	print ((d2 - d1), "(time for writing frames)")
	
	noise_output.close()
	
	d3 = datetime.datetime.now()
#	print( (d3 - d2), "(time for closing the file)")
# Simple demo of playing a looping sound using the (currently undocumented) sound.Player class
for note in range(12):
	noise_input = sound.Player('weier%d.wav'%note)
	#noise_input = open((os.path.expanduser(os.path.join(os.path.dirname(os.__file__), "../Media/Sounds/game/Beep.caf"))),'rb')
	print(noise_input.duration)
	noise_input.number_of_loops=0
	noise_input.play()
import photos
#img=photos.capture_image()
#img.save('osci.jpg')

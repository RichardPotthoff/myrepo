import wave
import random
import struct
import datetime
import os
import sndhdr
import sound
def fiter(format,f):
	n=struct.calcsize(format)
	while True:
		x=f.read(n)
		if x:
			yield struct.unpack(format,x)
		else:
			return
d1 = datetime.datetime.now()
noise_output=wave.open('ripoff.wav','wb')
noise_output.setparams((2, 2, 44100, 0,'NONE', 'not compressed'))
f=open('ripoff.log','rb')
n=4
n1=1/n
delay=1
#for l in fiter('hhhh',f):
#for l in struct.iter_unpack('hhhh',f):
noise_output.writeframes(b''.join([struct.pack('h',int((x1*(n-k)+x2*k)*n1)) for l in fiter('hhhh',f) for k in range(0,n+1) for _ in range(delay) for (x1,x2) in ((l[0],l[2]),(l[1],l[3])) ]))
print(noise_output.getparams())

d2 = datetime.datetime.now()
print ((d2 - d1), "(time for writing frames)")

noise_output.close()

d3 = datetime.datetime.now()
print( (d3 - d2), "(time for closing the file)")
# Simple demo of playing a looping sound using the (currently undocumented) sound.Player class
noise_input = sound.Player('ripoff.wav')
#noise_input = open((os.path.expanduser(os.path.join(os.path.dirname(os.__file__), "../Media/Sounds/game/Beep.caf"))),'rb')
print(noise_input.duration)
noise_input.number_of_loops=0
noise_input.play()
import photos
#img=photos.capture_image()
#img.save('osci.jpg')

import time
import wave
import sndhdr
import sound
for i in range(12):
  for note in range(12):
	  noise_input = sound.Player('weier%d.wav'%note)
	  print(noise_input.duration)
#	  noise_input.number_of_loops=0
	  noise_input.play()
	  time.

Sections=[(0x7000,'3752904.bin'),
          (0x6e00,'lock_L3R1L31R8L18R16.bin'),
          (0x6c00,'counter128.bin'),
          (0x6a00,'oscs_a.bin'),
          (0x5000,'7Segment.bin')]
o_buffer=[0xff]*0x8000
for offset,filename in Sections:
  f=open(filename,'rb')
  i_buffer=f.read()
  f.close()
  o_buffer[offset:offset+len(i_buffer)]=bytearray(i_buffer)
import time
#with open(time.strftime('%Y%m%d')+'.bin','wb') as f: f.write(bytes(o_buffer))
base=0b0110101100000000
x=255
for i in range(256):
  print('{0:08b}'.format(x))
  x=o_buffer[base|x]

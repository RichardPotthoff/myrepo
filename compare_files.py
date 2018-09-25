with open('IR_Remote.bin','rb') as a:
  x=a.read()
with open('IR_Remote_a.bin','rb') as b:
  y=b.read()
for i,xi in enumerate(x):
  j=(i & ~(0b11<<8))| ((i & (1<<8))<<1) | ((i & (1<<9))>>1)
  if xi!=y[j]: raise Exception('xi != y[j]')
#  print('i={:d}, j={:d}, xi={:d}, y[j]={:d}'.format(i,j,xi,y[j]))
print ('xi=y[j]')

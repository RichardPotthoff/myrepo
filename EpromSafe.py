# 3 Eprom State Machines for Eprom 27c256:
#
# 1. A rotary dial combination lock:
#  A0 - A6: feedback from D0 - D6
#  A7, A8: input from encoder disk
#  D0 - D6: feedback to A0 - A6
#  D7: output, low if correct number is dialed in.
#  The generated example is for the combination L3R1L31R8L18R16. L: increasing, R: decreasing
#  
#
# 2. A 128 step up-down counter. Same as the combination lock, except that the output is low 
#  at position 0, and there is no combination. The counter wraps around from 127 to 0, and vice versa.
#
# 3. A set of oscillators with cycles of 2,4,8,16,32,64,128,256 steps. The oscillators 
#  require 1,2,3,4,5,6,7, and 8 feedback lines, e.g. the 64 step oscillator requires D0 - D5 to be 
#  connected to A0 - A5. 
#  There are no other inputs or outputs.
#  The start address of each oscillator is the same as the step number: e.g. the offset for the 64 step 
#  oscillator is 64. The program for the 64 step oscillator is 64 bytes long, and ends at 127.
#  
#


def grayToInt(gray):
  mask=gray>>1
  result=gray
  while mask!=0:
    result^=mask
    mask>>=1
  return result

def intToGray(i):
  return i^(i>>1)

def rotate_left(x,p,n=4):
  result=[None]*n
  for i,x1 in enumerate(x):
    result[(i-p)%n]=x1
  return result
  
def simulateEprom(address,actions,addressInversionMask=0x0000,dataInversionMask=0x00):
  address^=addressInversionMask
  state=grayToInt(address&0x7F)
  phase=grayToInt((address>>7)&0x3)
  newstate=actions[state][phase]
  return (intToGray(newstate&0x7F)|(newstate&0x80))^dataInversionMask
  
def extractAction(eprom,state,phase,addressInversionMask=0x0000,dataInversionMask=0x00):
  address=intToGray(state)|(intToGray(phase)<<7)
  address^=addressInversionMask
  action=eprom[address]^dataInversionMask
  return (grayToInt(action&0x7F)|(action&0x80))
if __name__=='__main__':
  addressInversionMask=(1<<9)-1 
  dataInversionMask=(1<<8)-1
  combination=[-2,30,-23,10,-2]
  i=0
  p=0
  actions=[None]*128
  for j in combination:
    for k in range(abs(j)-1):
      actions[i]=rotate_left([[127-i,i,i,i+1],[i+1,i,i,127-i]][j>0],p%4)
      p+=1 if j>0 else -1
      i+=1
  for j in range(i,64):
    actions[j]=rotate_left([127-j,j+0x80,j+0x80,127-j],p%4)
  for i in range(64,128):
    actions[i]=rotate_left([(i+1)&127,i,i,i if i==127 else i+3 if i==64 else i-1],i%4)
  for i,a in enumerate(actions): print(i,a)  
  Eprom=[simulateEprom(address,actions,addressInversionMask,dataInversionMask) for address in range(1<<9)]
  def add_statusbits(i):
    i%=0x80
    return 0x80 if i==0 else i
  actions=[rotate_left(map(add_statusbits,[i+1, i,i,i-1]),(i+1)%4) for i in range(0x80)]
  CounterEprom=[simulateEprom(address,actions,addressInversionMask,dataInversionMask) for address in range(1<<9)]
  actions_=[[extractAction(CounterEprom,state,phase,addressInversionMask,dataInversionMask) for phase in range(4)]for state in range(128)]
  def makeOscEprom(nbits):
    inc=nbits//abs(nbits) if nbits!=0 else 0
    nbits=max(1,abs(nbits))
    n=1<<nbits
    return [intToGray((i+inc)%n)|((1<<(i//4+4)) if ((nbits==4) and (((i+inc)%4)!=0)) else 0) for j in range(n) for i in (grayToInt(j),)]  
  oscs=[makeOscEprom(i) for i in [0,1,2,3,4,5,6,7,8,0,-1,-2,-3,-4,-5,-6,-7,-8]]
  alloscs=[y for x in oscs for y in x] 
  phase=1
  oldphase=phase
  state=126
  state=intToGray(state)
  for k in [2]+combination+[12]:
    for j in range(abs(k)):
      phase+=1 if k>0 else -1
      for i in range(2):
  #      newstate=actions[state&0x7F][phase%4]
        newstate=Eprom[(state&0x7F|(intToGray((-phase)%4)<<7))^addressInversionMask]^dataInversionMask
  #      print('Old State: %3d, direction %s, phase: %3d, New State:%3d'%(state,'L'if k>0 else 'R',phase,newstate))
        print('Old State: %3d, direction %s, phase: %3d, New State:%3d'%(grayToInt(state&0x7F)|(state&0x80),'L'if k>0 else 'R',(phase+64)%32,grayToInt(newstate&0x7f)|(newstate&0x80)))
        oldphase=phase
        state=newstate
  
  #for i in range(64):
  #  print('{0:3d} {1:07b} {2:07b} {3:3d}'.format(i,intToGray(i),intToGray(127-i), 127-i))
  state=0
  for i in range(100):
    state=alloscs[(state & 0x0f)+16]
    print('{1:1x}{0:1x}'.format(grayToInt((state&0xf)>>2),state>>4))
  
  
  with open('oscs_up_down.bin','wb') as f: f.write(bytes(alloscs));f.close()
  #with open('lock_L3R1L31R8L18R16.bin','wb') as f: f.write(bytes(Eprom));f.close()
  #with open('counter128a.bin','wb') as f: f.write(bytes(CounterEprom));f.close()
  #print(('{:05d} {:04x} {:04x} {:016b} {:05d}\n'*65).format(*[j for i in range(65) for j in (i*512,i*512,0x8000-512*i,0x8000-512*i,0x8000-512*i)]))

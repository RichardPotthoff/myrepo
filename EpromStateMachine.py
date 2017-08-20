#-----------------------------------------------------------------------
# Simulation of a State Machine using a memory chip with feedback:
#
# The example is a implementation of a combination lock using
# an Eprom with at least 12 Address input lines, and 8bit parallel
# data output (e.g. 27c512)
#
# The Address lines A0 - A4 are connected to the data output lines D0-D4,
# The Address lines A5 - A7 are connected to the columns of a 3 columns x
# 4 rows numeric keypad. The Address lines A8 - A11 are connected to the
# 4 rows of the keypad:
#
#     D0 -------------> A 0 -+
#     D1 -------------> A 1  |
#     D2 -------------> A 2   > A0 - A4 = 32 Internal States (2**5)
#     D3 -------------> A 3  |
#     D4 -------------> A 4 -+
#     D5 --> blue  (Unlock) -+
#     D6 --> green (O.K.)    | D5 - D7 = Status Output bits
#     D7 --> red   (Error)  -+           (red+green = key pressed)
#        +------------> A 5 -+
#        |   +--------> A 6  |
#        |   |   +----> A 7  |
#        |   |   |           |
#        1 - 2 - 3 ---> A 8  |
#        |   |   |            > A5 - A11 = 7 bit External Input
#        4 - 5 - 6 ---> A 9  |
#        |   |   |           |
#        7 - 8 - 9 ---> A10  |
#        |   |   |           |
#        A - B - C ---> A11 -+
#  (A=Reset B=0 C=Unlock)
#
# This Python Program uses the 'scene' module of "Pythonista".
# "Pythonista" is a Python development system for Apple's iPad
# and iPhone: http://omz-software.com/pythonista/
#-----------------------------------------------------------------------

from scene import *
import sys


class Keypad (object):
  def __init__(self,ncols=3,nrows=4):
    self.nrows=nrows
    self.ncols=ncols
    self.bits=ncols+nrows
    self.mask=(1<<self.bits)-1
  def encode(self,n):
    if n==0:
      result=0
    elif n>self.nrows*self.ncols:
      result=1
    else:
      col=(n-1) % self.ncols
      row=(n-1)//self.ncols
      result=(1<<col)|(1<<(row+self.ncols))
    return result
  def decode(self,m):
    if m==0:
      return 0
    colbits=m&((1<<self.ncols)-1)
    rowbits=m>>self.ncols
    col=colbits.bit_length()
    row=rowbits.bit_length()
    if col==0 or colbits^(1<<(col-1)) != 0:
      return self.ncols*self.nrows+1
    if row==0 or row>(self.nrows) or rowbits^(1<<(row-1)) != 0:
      return self.ncols*self.nrows+1
    return (row-1)*self.ncols+col

class DigiLock (object):
  def __init__(self,keypad=Keypad(),combination=(1,2,3,4,5,6,7)):
    self.keypad=keypad
    self.combination=[0xB if i==0 else i for i in combination]#replace '0' with 0xB
    self.statebitcount=(len(combination)*2+1).bit_length()+1
    self.nstates=1<<self.statebitcount
    self.statemask=self.nstates-1
    self.invalidmask=1<<(self.statebitcount-1)
  def nextstate(self,s_in):
    resetkey=0xA
    releasekey=0xC
    invalidkey=0xD
    key=self.keypad.decode(s_in>>self.statebitcount)
    state=s_in&self.statemask
    data=0
    combination_invalid_flag=state&self.invalidmask!=0
    state&=~self.invalidmask
    n=grayToInt(state)
    if combination_invalid_flag:
      n=n+1
    if n<len(self.combination)*2:
      if n&1 and key!=resetkey:
        if key==0 or key==resetkey:
          n=n+1
        else:
          data=0b110
      elif combination_invalid_flag:
        if (key!=0 and key!=invalidkey and key!=resetkey):
          n=n+1
        elif key==resetkey:
          n=fastforward(n-1,self.nstates//2-1)+1
      else:
        if key==self.combination[n//2]:
          n=n+1
        else:
          if key!=0 and key!=invalidkey and  not (key==resetkey and n==0):
            n=n+1
            combination_invalid_flag=True
    else:
      if combination_invalid_flag:
        if n==len(self.combination)*2:
          if key==resetkey:
            n=fastforward(n-1,self.nstates//2-1)+1
#                                               n=n+1
          else:
            data=0b100
        else:
          if n<self.nstates//2:
            n=fastforward(n-1,self.nstates//2-1)+1
#                                               n=n+1
          else:
            n=n-1
            combination_invalid_flag=False
      else:
        if n==len(self.combination)*2:
          if key==resetkey:
            n=fastforward(n,self.nstates//2-1)
#                                               n=n+1
          else:
            if key==releasekey:
              data=0b011
            else:
              data=0b010
        elif n<self.nstates//2-1:
          n=fastforward(n,self.nstates//2-1)
#                                       n=n+1
        else:
          n=0
    if combination_invalid_flag:
      n=n-1
    newstate=intToGray(n)
    if combination_invalid_flag:
      newstate|=self.invalidmask
    return newstate|data<<self.statebitcount
  def eprom(self,addressinvertmask=0x0000,datainvertmask=0x00):
    n_bits=self.statebitcount+self.keypad.ncols+self.keypad.nrows
    result=[0xFF]*(1<<n_bits)
    addressinvertmask&=(1<<n_bits)-1
    datainvertmask&=0xFF
    for i in range(1<<n_bits):
      result[i^addressinvertmask]=self.nextstate(i)^datainvertmask
    return result


def mirror_bits(i,n):
  result=0
  for k in range(n):
    result<<=1
    result|=i&1
    i>>=1
  return result

def fastforward(i,j):
  ig=intToGray(i)
  jg=intToGray(j)
  xij=ig^jg
  msb=xij.bit_length()-1
  return grayToInt(ig^1<<msb if msb>0 else jg)

#-----------------------------------------------------------------------
def distance(shape,p):
  if shape.size.h>shape.size.w:
    return max(shape.position.x-p.x,p.x-(shape.position.x+shape.size.w))
  else:
    return max(shape.position.y-p.y,p.y-(shape.position.y+shape.size.h))

class LaserNode(ShapeNode):
  def __init__(self,position=Point(0,0),angle=0,length=100,width=5,color='red',**kwargs):
    self.max_length=length
    ShapeNode.__init__(self,position=position,size=(length,width),anchor_point=Point(0,(width+1)//2),color=color,**kwargs)
    self.rotation=angle*math.pi/180
    self.cr=math.cos(self.rotation)
    self.sr=math.sin(self.rotation)
  def blockLaser(self,ps,r=40):
    new_length=self.max_length
    result=False
    for p in ps:
      if p:
        p1x=p.location.x-self.position.x
        p1y=p.location.y-self.position.y
        p2x=p1x*self.cr+p1y*self.sr#length
        p2y=-p1x*self.sr+p1y*self.cr#distance
        if (abs(p2y)<r) and (p2x>0) and (p2x<self.max_length):
          new_length=min(new_length,max(0,p2x-r))
          result=True
    self.size=(new_length,self.size.h)
    return result

class Game(Scene):
  def __init__(self,combination=(1,2,3,4,5,6,7),*args,**kwargs):
    Scene.__init__(self,*args,**kwargs)
    self.combination=combination
  def setup(self):
    self.keypad=Keypad()
    self.digiLock=DigiLock(combination=self.combination)
    self.Eprom=self.digiLock.eprom()
    self.location=None
    self.locations=[]
    self.score_label = LabelNode('0', font=('Avenir Next', 0.052*min(self.size)), position=(self.size.w/2, self.size.h-0.065*min(self.size)),alpha=1.0, parent=self)
    self.state=0b00000
    w=self.size.w
    h=self.size.h
    nh=4
    dh=0.2*min(self.size)
    nv=3
    dv=dh
    for i in range(nh):
      for j in range(nv):
        n=i*nv+j+1
        LabelNode('%X'%(n), font=('Avenir Next', 0.078*min(self.size)), position=(w/2.0+dv*(j-nv/2+0.5), h/2.0-dh*(i-nh/2+0.5)),alpha=0.7, parent=self)
    hLasers=[(Point(w,h/2.0-dh*(i-nh/2+0.5)),w,0.0065*min(self.size),180,'red') for i in range(nh)]
    vLasers=[(Point(w/2.0+dv*(i-nv/2+0.5),0),h,0.0065*min(self.size),90.0,'lightgreen') for i in range(nv)]
    self.Lasers = [LaserNode(position=p,length=ll,width=lw,angle=a,color=c,alpha=0.7,parent=self) for p,ll,lw,a,c in vLasers+hLasers]
    self.LED=ShapeNode(color=(0,0,0),position=(0.325*min(self.size), self.size.h-0.025*min(self.size)),size=(0.025*min(self.size),0.025*min(self.size)),parent=self)
    self.background_color = 'black'

  def update(self):
    n=0
    for i,Laser in enumerate(self.Lasers):
      if Laser.blockLaser(self.locations):
        n|=1<<i
#               nextstate=self.digiLock.nextstate(n<<5|(self.state&0b11111))
    nextstate=self.Eprom[n<<5|(self.state&0b11111)]
    self.score_label.text='{2:08b} {1:07b} ={0:2X}\n{3:08b}'.format(self.keypad.decode(n),mirror_bits(n,7),self.state,nextstate)
    self.LED.color=((self.state>>7)&1,(self.state>>6)&1,(self.state>>5)&1)
    if (self.state^nextstate)&0b11111:
      print('{3:03b} {1:0{0}b}{2:3d} '.format(self.digiLock.statebitcount,self.state&self.digiLock.statemask,grayToInt(self.state&self.digiLock.statemask), self.state>>self.digiLock.statebitcount))
#      print('{0:08b}{1:3d}'.format(self.state,grayToInt(self.state&0b11111)))
#                       print('{0:08b}\n'.format(nextstate))

    self.state=nextstate



  def touch_began(self, touch):
    self.location= touch.location
    self.locations.append(touch)

  def touch_ended(self,touch):
    self.location= None
    self.locations.remove(touch)

  def touch_moved(self, touch):
    self.location = touch.location
    self.locations.remove(touch)
    self.locations.append(touch)

def grayToInt(gray):
  mask=gray>>1
  result=gray
  while mask!=0:
    result^=mask
    mask>>=1
  return result

def intToGray(i):
  return i^(i>>1)
#-----------------------------------------------------------------------

def main():
  if len(sys.argv)==1:
    run(Game(), PORTRAIT, show_fps=True)
  elif len(sys.argv)>1:
    combination=[int(c) for c in sys.argv[1]]
    if len(sys.argv)==2:
      run(Game(combination=combination), PORTRAIT, show_fps=True)
    else:
      input=[0xB if c=='0' else 0xA if c in ('r','R') else 0xC if c in ('u','U') else int(c) for c in sys.argv[2]]
      keypad=Keypad(ncols=3,nrows=4)
      digiLock=DigiLock(keypad=keypad,combination=combination)
      Eprom=digiLock.eprom()
      state=0
      k=0
      for i in input+[0]*5:
        for j in (i,i,0):
          print('{3:03b} {1:0{0}b}{2:3d} '.format(digiLock.statebitcount,state&digiLock.statemask,grayToInt(state&digiLock.statemask), state>>digiLock.statebitcount))
          state=Eprom[keypad.encode(j)<<digiLock.statebitcount|(state&digiLock.statemask)]
          if state==0: 
            k=k+1
          if k>2:break
        if k>2: break
  

if __name__ == '__main__':
  main()


# Piano
#
# A simple multi-touch piano.
import scene
from scene import *
import sound
import os
from itertools import chain
from math import radians,pi,sin,cos,atan2
class StateTable(scene.ShapeNode):
  def __init__(self,x,y,w,h,data,**args):
    scene.Node.__init__(self,**args)
    self.data=data
    self.size=(w,h)
    self.position=(x,y)
    self.anchor_point=(0,0)
    self.statebox=ShapeNode(ui.Path.rect(0,0,20,10),stroke_color='#000000',fill_color='#2bff3d')
    self.add_child(self.statebox)
    self.phase_=0
    self.state_=0
    self.cells=[None]*512
    for i in range(512):
      c=((i>>6&1)<<2)|(i>>7)
      r=i&((1<<6)-1)
      if c>3:r=63-r
      if c>3:c+=1
      cell=LabelNode("%4d"%(self.data[i]),scale=0.5)
      cell.position=(c*18+self.size.w-200,self.size.h-36-11*r)
      cell.color=(0,0,0)
      if self.data[i]&0x7f>63:cell.color='#ff0000'
      if ((self.data[i] & 0x7f+128)-(i & 0x7f))%128==1 and i&0x7f != 63:cell.color='#00c010'
      if ((self.data[i] & 0x7f)-(i & 0x7f))==0:cell.color='#000000'
      self.cells[i]=cell
      self.add_child(cell)
    self.updateState()
    p=ui.Path()
    p.move_to(0,0)
    p.line_to(0,self.size.h)
    p.move_to(18*5,0)
    p.line_to(18*5,self.size.h)
    self.cursor=ShapeNode(p)
    self.cursor.anchor_point=(0,0)
    self.cursor.position=(self.size.w-200,0)
    self.cursor.stroke_color=(0,0,0)
    self.add_child(self.cursor)
    self.phase=0.75
    self.state=0
  @property
  def phase(self):
    return self.phase_
  @phase.setter
  def phase(self,phi):
    self.phase_=4*frac(1/8+phi)
    self.cursor.position=(self.size.w-200-9+18*self.phase_,0)
    self.updateState()
  @property
  def state(self):
    return self.state_
  @state.setter
  def state(self,state):
    self.state_=state
    self.updateState()
  def updateState(self):
    while self.state_ != self.data[(int(self.phase_)<<7)|self.state_]&0x7f:
      self.state_=self.data[(int(self.phase)<<7)|self.state_]&0x7f
    self.statebox.position=self.cells[(int(self.phase_)<<7)|self.state_].position
    

class dial(scene.Node):
  def __init__(self,x,y,r1,r2,n,**args):
    scene.Node.__init__(self,**args)
    self.all_flags = []
    self.angle_=0.0
    self.r1=r1
    self.r2=r2
    self.position=(x,y)
    self.n=n

    p=ui.Path()
    p.move_to(r1,0)
    ang1=2*2*pi/self.n
    p.add_arc(0,0,r1,0,-ang1/2,False)
    p.add_arc(0,0,r2,-ang1/2,ang1/2,True)
    p.add_arc(0,0,r1,ang1/2,0,False)
    p.close()   
    rcorr=(cos(ang1/2)*r1+r2)/2
    for i in range(self.n//4):
      ang=(4*i+3)*(2*pi/n)
      flag=ShapeNode(p)
      flag.fill_color=(0,0,0)
      flag.stroke_color=(0,0,0)
      flag.alpha=0.8
      flag.position=(cos(ang)*rcorr,sin(ang)*rcorr)
      flag.rotation=ang
      self.add_child(flag)
      self.all_flags.append(flag)
    circ=scene.ShapeNode(ui.Path.oval(0,0,2*r1,2*r1))
    circ.fill_color=(1,1,1)
    circ.stroke_color=(0,0,0)
    self.add_child(circ)
    for i in range(self.n):
      ang=-i*2*pi/self.n
      text=LabelNode("%3d – "%(i),color=(0,0,0),scale=1.0)
      text.rotation=ang
      text.position=(cos(ang)*(self.r1-text.size.w/2),sin(ang)*(self.r1-text.size.w/2))
      self.add_child(text)
    text=LabelNode("+",color=(0,0,0),scale=1.0)
    self.add_child(text)
    
def frac(x):
  return x-int(x)
class dial_lock (Scene):
  def __init__(self,data,**args):
    Scene.__init__(self,**args)
    self.data=data
  def setup(self):
    self.background_color=(1,1,1)
    n=32
    r=0.49*min(self.size.w, self.size.h)
    rled=r*0.025
    for pos in ((self.size.h/2+0.95*r,self.size.h/2+sin(pi/32)*r),(self.size.h/2+0.95*r,self.size.h/2-sin(pi/32)*r)):
      circ=scene.ShapeNode(ui.Path.oval(0,0,2*rled,2*rled),stroke_color=(0.5,0.5,1),fill_color=(0.5,0.5,1),position=pos)
      self.add_child(circ)
    self.dial=dial(self.size.h/2,self.size.h/2,0.9*r,r,n,scale=1.0)
    self.add_child(self.dial)
    text=LabelNode("——",color=(0,0,0))
    text.position=(self.size.h/2+0.9*r,self.size.h/2)
    self.add_child(text)
    self.dial.angle=pi/16
    self.stateTable=StateTable(self.size.h,0,self.size.w-self.size.h,self.size.h,self.data)
    self.add_child(self.stateTable)
    
  def touch_began(self, touch):
    self.last_angle=atan2(touch.location.y-self.dial.position.y,touch.location.x-self.dial.position.x)
    pass

  def touch_moved(self, touch):
    angle=atan2(touch.location.y-self.dial.position.y,touch.location.x-self.dial.position.x)
    self.dial.rotation+=angle-self.last_angle
    self.stateTable.phase=(-self.dial.rotation+2*pi)/(2*pi/(self.dial.n/4))+0.75
    self.last_angle=angle
    pass

  def touch_ended(self, touch):
    pass
addressInversionMask=(1<<9)-1 
dataInversionMask=(1<<8)-1
#f= open('counter128.bin','rb')
f=open('lock_L3R1L31R8L18R16.bin','rb')
eprom=f.read()
f.close
from EpromSafe import extractAction
actions=[extractAction(eprom,address,phase,addressInversionMask,dataInversionMask)for phase in range(4) for address in range(128) ]
p=dial_lock(actions)
run(p, LANDSCAPE,show_fps=True)


# A State machine that decodes IR remote control signals, and changes an output bit 
# if the correct code is received.
# This example is for a controller that sends a NEC IR transmission frame (start bit, address(8 bit),~address,command(8 bit),~command). The 'address' value is always 0. Other values for 'address' may not synchronize properly, and a separate R/C circuit may be required to generate a reset signal from the start bit. In the current implementation, the start bit is detected as a regular '1', and the 8 following '0' bits from the 'address' guarantee synchronization. 
#
#Hardware implementation:
#IC1: Eprom 27c256
#IC2: 1838 Ir receiver
#C1: 0.1uF*
#R1: 6.8kOhm*, R2: 220kOhm, R3:22kOhm
#Q1: pnp transistor (e.g. 2N3906)
#LED1: green LED
#
# *: R1*C1 should be around 0.630ms, but anything between 0.4ms and 1.0ms worked for me
#
#Circuit Nodes:
#GND: IC1[GND,~CE,~OE], R1[1], C1[1], IC2[GND], LED1[C]
#VCC: IC1[Vcc,Vpp], IC2[Vcc], Q1[E]
#RX: Q1[C], IC1[A8], R1[2], C1[2]
#CLK: IC2[Sig],IC1[A9],R2[1]
#Q1[B]: R2[2]
#StatusOut: IC1[D7], R3[1], IC1[A7|A10|..A14]
#LED: LED1[A],R3[2]
#Feedbacks: IC1[D0..D6]->IC1[A0..A6]
#Configuration: IC1[A7,A10..A14]->(Vcc|GND|IC1[D7]) **
# **: The number of '1' bits in the Address bits (7,10..14) must be odd if D7 is '1', and must be even if D7 is '0'. This means that the number of these Adress lines tied to 'Vcc' must be even (otherwise the locic would be reversed: the number of '1' bits would be odd for D7='0'). Only one of the address lines can be connected to D7, otherwise the parity of the Address bits is undefined during the transition.

import scene
from itertools import accumulate
from operator import __add__
def grayToInt(gray):
  mask=gray>>1
  result=gray
  while mask!=0:
    result^=mask
    mask>>=1
  return result

def intToGray(i):
  return i^(i>>1)
def lsbitpos(m):
  lsb=0
  if  m!=0:
    while m&(1<<lsb)==0:
      lsb=lsb+1
  else:
    lsb=-1
  return lsb
def fastforward(i,j):
  ig=intToGray(i)
  jg=intToGray(j)
  xij=ig^jg
#  msb=xij.bit_length()-1
#  return grayToInt(ig^1<<msb if msb>=0 else jg)
  lsb=lsbitpos(xij)
  return grayToInt(ig^1<<lsb if lsb>=0 else jg)
  
def CountBits(n):
  n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
  n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
  n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
  n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
  n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
  n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
  return n

def reverseByte(b):
  b_=0
  for i in range(8):
    b_<<=1
    b_|=b&1
    b>>=1
  return b_
 
f=open("lircd.conf")
a=f.read()
b=[x.split() for x in a.split("begin raw_codes")[1].split("end raw_codes")[0].split("name")[1:]]
d={x[0].strip():[int(y)for y in x[1:]] for x in b}
f.close()

def gen_pwl(pw=[0]+d['BTN_0']):
  t=accumulate(pw)
  return [((t+y)/1e6,y^(i & 1)) for i,t in enumerate(t) for y in (0,1)]
  
def rc_filter(pwl,dt=0.000580/5,tmax=0.08,t0=0,y0=0):
  y=y0
  t=t0
  c1=1.5/5
  c2=0.5/5
  yield(t,y)
  for t1,y1 in pwl:
    if t>tmax:
      break
    while t<t1:
      t=t+dt
      if t>tmax:
        break
      if y1>y:
        y=min(y1,y+c1)
      else:
        y=c2*y1+(1-c2)*y
      yield (t,y)
  
    
def write_pwl_Files():
  for bn in d.keys():
    with open(bn+".txt","w") as of:
      of.write("\n".join(["{:8f} {:d}".format(*x) for x in gen_pwl([0]+d[bn])]))
      
def gen_bits(ButtonName,blank_even=True,blank_character=''):
  return ''.join([blank_character if (((i%2)==0)and blank_even)else '1' if dt>1000 else '0' for i,dt in enumerate(d[ButtonName])])
  
e='\n'.join([gen_bits(bn,be,' ')+' '+bn for bn in d.keys() for be in (False,True)])
d1={bn:int(gen_bits(bn)[1:33],base=2) for bn in d.keys()}
#print('d2={{\n{:s}}}'.format(',\n'.join(["{:>17s}:0x{:08x}".format("'"+bn+"'",code)for bn,code in d1.items()])))
d2={
'KEY_CHANNELDOWN':0x00ffa25d,  'KEY_CHANNEL':0x00ff629d,  'KEY_CHANNELUP':0x00ffe21d,
   'KEY_PREVIOUS':0x00ff22dd,     'KEY_NEXT':0x00ff02fd,  'KEY_PLAYPAUSE':0x00ffc23d,
 'KEY_VOLUMEDOWN':0x00ffe01f, 'KEY_VOLUMEUP':0x00ffa857,      'KEY_EQUAL':0x00ff906f,      
  'KEY_NUMERIC_0':0x00ff6897,        'BTN_0':0x00ff9867,          'BTN_1':0x00ffb04f,
  'KEY_NUMERIC_1':0x00ff30cf,'KEY_NUMERIC_2':0x00ff18e7,  'KEY_NUMERIC_3':0x00ff7a85,
  'KEY_NUMERIC_4':0x00ff10ef,'KEY_NUMERIC_5':0x00ff38c7,  'KEY_NUMERIC_6':0x00ff5aa5,
  'KEY_NUMERIC_7':0x00ff42bd,'KEY_NUMERIC_8':0x00ff4ab5,  'KEY_NUMERIC_9':0x00ff52ad}
d3={k:reverseByte(c>>8&0xff) for k,c in d2.items()}
d3={'KEY_CHANNELDOWN': 69,   'KEY_CHANNEL': 70, 'KEY_CHANNELUP': 71,
       'KEY_PREVIOUS': 68,      'KEY_NEXT': 64, 'KEY_PLAYPAUSE': 67, 
     'KEY_VOLUMEDOWN':  7,  'KEY_VOLUMEUP': 21,     'KEY_EQUAL':  9, 
      'KEY_NUMERIC_0': 22,         'BTN_0': 25,         'BTN_1': 13, 
      'KEY_NUMERIC_1': 12, 'KEY_NUMERIC_2': 24, 'KEY_NUMERIC_3': 94, 
      'KEY_NUMERIC_4':  8, 'KEY_NUMERIC_5': 28, 'KEY_NUMERIC_6': 90, 
      'KEY_NUMERIC_7': 66, 'KEY_NUMERIC_8': 82, 'KEY_NUMERIC_9': 74}

f='\n'.join(['{:4x}'.format(int(gen_bits(bn,be,'')[1:33],base=2))+' '+bn for bn in d.keys() for be in (True,)])

def byteToCode(b):
  if hasattr(b,'__len__'):
    a,p=b[0],b[1]
  else:
    a,p=b,0
  ah=reverseByte(a>>8 & 0xff)
  al=reverseByte(a & 0xff)
  ph=reverseByte(p>>8 & 0xff)
  pl=reverseByte(p & 0xff)
  return ((ah<<24)|((ah^0xff)<<16)|(al<<8)|(al^0xff),(ph<<24)|(ph<<16)|(pl<<8)|pl)

def generate_pw(bytecode=d3['BTN_0']):
  yield(0)
  yield(8900)
  yield(4600)
  code= byteToCode(bytecode)[0]
  for i in range(32):
    yield(580)
    yield(580*[1,3][code>>(31-i)&1])
  yield(580)
  yield(40000)
  yield(8900)
  yield(2300)
  yield(580)


assert sum([x^byteToCode(y)[0] for k in d2 for x,y in ((d2[k],d3[k]),)])==0
  
def bitAtPos(x,i):
  return(x>>i&1 if i>=0 else 0)

def newState(address,code=d2['BTN_0'],dontCare=0):#Example codes for BTN_0 and BTN_1
  msbBitPos=31
  state = address & 0xff #bits 2 - 9
#  outputIsOn = state&0x80 != 0
  outputIsOn = CountBits(address & ~(1<<9|1<<8|0x7f))&1#parity of address, excluding bits 0-6,8,and 9
  state = state & 0x7f | outputIsOn << 7 #bits 0 - 6, plus address parity
  oldstate=state
  if outputIsOn:
    state=state^0x40#flip bit 6 if output bit is on
  step = grayToInt(state&0x7f)
  if step>63:step=step-128
  clock = (address>>9)&1
  serialIn  = (address>>8)&1
  clockTriggered = step%2 == clock
  currentBitPos=msbBitPos-(step+1)//2 if step>=0 else msbBitPos #msb is transmitted first
  newstep=step
  newOutputIsOn=outputIsOn
  if step<0:
    if step==-1 and clockTriggered and clock==1:
      if (bitAtPos(code,currentBitPos)==serialIn) or bitAtPos(dontCare,currentBitPos):
        newstep=step+1 #go to 0 and start 
      else:
        newstep=step-1 #go to -2 and wait
    else:
      newstep=fastforward(step+128,127-clock)-128#endstate should be -1, or -2, depending on clock signal
  elif clockTriggered:
    if clock==1:#rising edge of clock signal 
      if (bitAtPos(code,currentBitPos)==serialIn) or bitAtPos(dontCare,currentBitPos): 
        if step==61: #transmission complete, perfect match: switch output signal
          newOutputIsOn=not outputIsOn
          newstep=-(step+1)#prepare to receive new transmission
        else:
          newstep=step+1
      else:
        newstep=-(step+1)#no match, wait for next transmission
    else: newstep=step+1 #falling edge of clock signal: go to next 
  else: pass #nothing has changed, return the original state
  #now re-assemble the new state, and return it:
  if newstep<0:newstep=newstep+128
  newstate=intToGray(newstep)|(1<<7 if newOutputIsOn else 0)
  if newOutputIsOn:
    newstate=newstate^0x40#flip bit 6 if output bit is on
    
  assert CountBits(newstate^oldstate)<=1 #make sure no more than one bit of the state changes at the same time
#  if CountBits(newstate^oldstate)>1:
#    print("error")
  return newstate
  
g=[None]*1024*6
for j,code_dontCare_bytes in enumerate([(c1,c1^c2) for k1,k2 in (('KEY_NEXT','KEY_NEXT'),('KEY_NEXT','KEY_NEXT'),('KEY_PLAYPAUSE','KEY_PLAYPAUSE'),('KEY_PLAYPAUSE','KEY_PLAYPAUSE'),('KEY_VOLUMEUP','KEY_VOLUMEUP'),('KEY_VOLUMEUP','KEY_VOLUMEUP'),('KEY_EQUAL','KEY_EQUAL'),('KEY_EQUAL','KEY_EQUAL'),('KEY_CHANNELDOWN','KEY_CHANNELUP'),('KEY_CHANNELDOWN','KEY_CHANNELUP'),('KEY_CHANNEL','KEY_CHANNELUP'),('KEY_CHANNEL','KEY_CHANNELUP')) for c1,c2 in ((d3[k1],d3[k2]),)]):
#  print('{:3d} {:08x} {:032b}'.format(j,code,dontCare))
  for i in range(512):
    address=i^0x000+j*512
    parity=CountBits(address&~(0x3ff))%2
    code,dontCare=byteToCode(code_dontCare_bytes)
    g[address^((1<<8)|(1<<9))]=newState(address,code,dontCare)^0x00

def generate_signal(bytecode=d3['BTN_0']):
  yield((0,1))
  yield((0,1))
  yield((1,1))
  code= byteToCode(bytecode)[0]
  for i in range(32):
    d=code>>(31-i)&1
    yield((0,d))
    yield((1,d))
  yield((0,1))
  yield((1,1))
  yield((0,1))
  yield((1,1))
  yield((0,1))

class IR_Receiver():
  def __init__(self,Eprom=(0xFF,)*6*1024,state=0,clkBitPos=9,rxBitPos=8,feedbackBitPos=10,baseAddress=0):
    self.Eprom=Eprom
    self.clkBitPos=clkBitPos
    self.rxBitPos=rxBitPos
    self.feedbackBitPos=feedbackBitPos
    self.baseAddress=baseAddress 
    self.address_=0
    self.clk_=0
    self.rx_=1
    self.state_=state
    self.updateState()
  @property
  def D7(self):
    return (self.state_>>7)&1
  @property
  def clk(self):
    return self.clk_
  @clk.setter
  def clk(self,clk):
    if self.clk_!=clk:
      self.clk_=clk
      self.updateState()
  @property
  def rx(self):
    return self.rx_
  @rx.setter
  def rx(self,rx):
    if self.rx_!=rx:
      self.rx_=rx
      self.updateState()
      
  def updateState(self,max_iterations=7):
    for i in range(max_iterations):
      newAddress=self.baseAddress&~((1<<self.clkBitPos)|(1<<self.rxBitPos)|(1<<self.feedbackBitPos)|0x7f) | (self.clk_<<self.clkBitPos)|(self.rx_<<self.rxBitPos)|(self.state_ & 0x80)<<(self.feedbackBitPos-7)|(self.state_ & 0x7f)
      if self.address_!=newAddress:
        newState=self.Eprom[newAddress]
        #          print('{:015b} {:08b}'.format(newAddress,newState))
#        if self.state_&0x80!=newState&0x80: 
#          print('B state changed from {:08b} to {:08b}'.format(self.state_,newState))
        self.address_=newAddress
        if newState==self.state_: break
        self.state_=newState
        
        
    
  @property
  def state(self):
    return self.state_
  @state.setter
  def state(self,state):
    self.state_=state
    self.updateState()

    
def testStateMachine(codes= (0,1,2,4,5,7,8,0,1,2,4,5,7,8), fbp=7,ba=0):
  codes=[(i,list(d3.items())[i][1])for i in codes] 
  state=255
  IR2=IR_Receiver(Eprom=g,baseAddress=ba,feedbackBitPos=fbp)
  IR2.state_=state^0x00
  for key_number,code in (codes):
    print("key#={:2d} code={:032b}".format(key_number,code))
    errorcount=0
    errorcount2=0
    for x in generate_signal(code):
      i=0
      while True:
        address=(state&0x7f)|0x00|(x[0]<<9)|(x[1]<<8)|(state&0x80)<<(fbp-7)|ba
        newstate=g[address^((1<<8)|(1<<9))]^0x00
#        print('A ', x[0],x[1],'{:016b} {:08b} {:3d}'.format(address,state,grayToInt(state&0x7f)))
        if state&0x80!=newstate&0x80: 
          print('A state changed from {:08b} to {:08b}'.format(state,newstate))
        if newstate==state or i>5: break
        i=i+1
        state= newstate
      IR2.clk,IR2.rx=(x[0]^1,x[1]^1)
#      print('B ', x[0],x[1],'{:016b} {:08b} {:3d}'.format(IR2.address_^0x3ff,IR2.state^0xff,grayToInt((IR2.state^0xff)&0x7f)))
#      if IR2.state^0xff!=newstate:
#        errorcount2=errorcount2+1
#    print ("errorcount={:d} errorcount2={:d}".format(errorcount,errorcount2))
    
def runTests():
  testStateMachine()
  p=[[CountBits(x^y)for x in d2.values()]for y in d2.values()]
  print('\n'.join([' '.join(['{:3d}'.format(x) for x in y]) for y in p]))
  
class  Button(scene.ShapeNode):
    def __init__(self,shape,text='',response='',**args):
      scene.ShapeNode.__init__(self,shape,**args)
      self.add_child(scene.LabelNode(text,scale=2))
      self.response=response
    

class IrRemote(scene.Scene):
  def __init__(self,**args):
    scene.Scene.__init__(self,**args)
  def setup(self):
    self.background_color=(1,1,1)
    n=32
    rled=min(self.size)*0.02
    self.IR_Receivers=[None]*8
    for i,(text,ba,fbp) in enumerate((('IO on, Mode off, Mute toggle',0b100001<<7,10),('|<< toggle',0b000000<<7,7),(' +  toggle',0b011000<<7,7),('|<< on, >>| off',0b000000<<7,10),('- on, + off',0b010001<<7,10),('|<< on, - off',0b000000<<9,11),('>>| on, + off',0b001001<<7,11), ('Mode toggle, Mute toggle',0b101000<<7,7))):
      s='{:016b}'.format(ba)
      s=s[:16-9-1]+'rc'+s[16-8:]
      s=s[:16-fbp-1]+'^'+s[16-fbp:16-7]+'ddddddd'
 #     print(s+'  '+text)
      circ=scene.ShapeNode(scene.ui.Path.oval(0,0,2*rled, 2*rled),fill_color='darkgreen',stroke_color='#000000',position=(0.67*self.size.w,(0.48-(i-(16-1)/2)/17)*self.size.h))
      if i==0:
         circ.add_child(scene.LabelNode('Configuration:', scale=1, color='black', anchor_point=(1,0),position=(-25,25)))
         circ.add_child(scene.LabelNode('Description:', scale=1, color='black', anchor_point=(0,0),position=(25,25)))
      circ.add_child(scene.LabelNode(s,scale=1,color='black',anchor_point=(1,0.5),position=(-25,0)))
      circ.add_child(scene.LabelNode(text,scale=1,color='black',anchor_point=(0,0.5),position=(25,0)))
      self.IR_Receivers[i]=(IR_Receiver(Eprom=g,feedbackBitPos=fbp,baseAddress=ba,state=0),circ)
      if self.IR_Receivers[i][0].D7==1:
        circ.fill_color='lightgreen'
      self.add_child(circ)
    self.statustext=scene.LabelNode('Code:',scale=1,color='black',anchor_point=(0,0),position=(self.size.width*0.475,self.size.height*0.08))
    self.add_child(self.statustext)
    self.dy=min(self.size)/7
    self.dx=min(min(self.size)/4,self.dy*1.5)
    buttonheight=0.9*self.dy
    buttonwidth=buttonheight
    self.colors=[['red','black','green'], ['green','black','black'], ['magenta','blue','blue'], ['black','red','red'],['black','black','black'],['black','black','black'],['black','black','black'] ]
    self.texts=[['OI','Mod','Mute'],['>||','|<<','>>|'],['EQ','-','+'],['0','$','U/SD'],['1','2','3'],['4','5','6'],['7','8','9']]
    for i in range(3):
      for j in range(7):
        button=Button(scene.ui.Path.oval(0,0, buttonwidth, buttonheight), color=self.colors[j][i], position=(1.5*self.dx+(i-(3-1)/2)*self.dx,self.size.h/2-(j-(7-1)/2)*self.dy), text=self.texts[j][i], response='{:>17s} {:02x}'.format(*list(d3.items())[j*3+i]))
#        button.add_child(scene.LabelNode(texts[j][i],scale=2))
        self.add_child(button)
    self.chart_clk=scene.ShapeNode(scene.ui.Path(),fill_color='red',stroke_color='black',position=(self.size.width*0.5,self.size.h*0.05),anchor_point=(0,0))
    self.add_child(self.chart_clk)
    self.add_child(scene.LabelNode('clk',scale=1,color='black',anchor_point=(1.0,0),position=(self.size.width*0.5,self.size.h*0.05)))
    self.chart_dat=scene.ShapeNode(scene.ui.Path(),fill_color='blue',stroke_color='black',position=(self.size.width*0.5,self.size.h*0.02),anchor_point=(0,0))
    self.add_child(self.chart_dat)
    self.add_child(scene.LabelNode('dat',scale=1,color='black',anchor_point=(1.0,0),position=(self.size.width*0.5,self.size.h*0.02)))

  def touch_began(self,touch):
    i=round(touch.location[0]/self.dx-(0.5))
    j=round(-(touch.location[1]-self.size.h/2)/self.dy+3)
    if i>=0 and i<3 and j>=0 and j<7:
#       print('{:>17s} {:2d}'.format(*list(d3.items())[j*3+i]))
       self.statustext.text='Code: {1:02d} ( {2:s} )'.format(*(list(d3.items())[j*3+i]+(self.texts[j][i],)))
       p=scene.ui.Path()
       p.move_to(0,20)
       for a in [(t*6000,(1-y)*20) for t,y in gen_pwl(generate_pw((list(d3.items())[j*3+i][1]))) if t<0.08]:
         p.line_to(*a)
       p.line_to(0.08*6000,20)
       self.chart_clk.path=p
       p=scene.ui.Path()
       p.move_to(0,20)
       for a in [(t*6000,(1-y)*20) for t,y in rc_filter(gen_pwl(generate_pw((list(d3.items())[j*3+i][1]))))]:
         p.line_to(*a)
       p.line_to(0.08*6000,20)
       self.chart_dat.path=p
       for x in generate_signal((list(d3.items())[j*3+i][1])):
#         print(x)
         for IR,led in self.IR_Receivers:
           IR.clk,IR.rx=(x[0]^1,x[1]^1)
       for IR,led in self.IR_Receivers:
         led.fill_color=('darkgreen','lightgreen')[IR.D7]
       
IR1=IrRemote()
scene.run(IR1,scene.LANDSCAPE,show_fps=True)
#runTests()
#testStateMachine(codes= ( d2['KEY_NEXT'],d2['KEY_PLAYPAUSE'],d2['KEY_NEXT'],d2['KEY_PLAYPAUSE']) )
#testStateMachine(fbp=10,ba=0b100001<<7)#+
#testStateMachine(fbp=10,ba=0b010001<<7)#+
#testStateMachine(fbp=10,ba=0b000000<<7)#+
#testStateMachine(fbp= 7,ba=0b101000<<7)#+
#testStateMachine(fbp= 7,ba=0b011000<<7)#+
#testStateMachine(fbp= 7,ba=0b000000<<7)#+
#testStateMachine(fbp=11,ba=0b001001<<7)#+
#testStateMachine(fbp=11,ba=0b000000<<7)#+
#with open('IR_Remote_a.bin','wb') as f: f.write(bytes(g));f.close()

  

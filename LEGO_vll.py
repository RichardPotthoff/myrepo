import scene
class  Button(scene.ShapeNode):
    def __init__(self,shape,text='',response='',**args):
      scene.ShapeNode.__init__(self,shape,**args)
      self.add_child(scene.LabelNode(text,scale=2))
      self.response=response

class vllRemote(scene.Scene):
  def __init__(self,**args):
    scene.Scene.__init__(self,**args)
  def setup(self):
    self.background_color=(1,1,1)
    self.dy=min(self.size)/7
    self.dx=min(min(self.size)/4,self.dy*1.5)
    buttonheight=0.9*self.dy
    buttonwidth=buttonheight
    self.colors=[['red','black','green'], ['green','black','black'], ['magenta','blue','blue'], ['black','red','red'],['black','black','black'],['black','black','black'],['black','black','black'] ]
    self.texts=[['OI','Mod','Mute'],['>||','|<<','>>|'],['EQ','-','+'],['0','$','U/SD'],['1','2','3'],['4','5','6'],['7','8','9']]
    for i in range(3):
      for j in range(7):
        button=Button(scene.ui.Path.oval(0,0, buttonwidth, buttonheight), color=self.colors[j][i], position=(1.5*self.dx+(i-(3-1)/2)*self.dx,self.size.h/2-(j-(7-1)/2)*self.dy), text=self.texts[j][i], response=j*3+i)
#        button.add_child(scene.LabelNode(texts[j][i],scale=2))
        self.add_child(button)
  def update(self):
    print (self.dt)
    self.background_color=tuple(1-i for i in self.background_color)
vll1=vllRemote()
scene.run(vll1,scene.LANDSCAPE,show_fps=True,frame_interval=1)

  

# Piano
# 
# A simple multi-touch piano.

from scene import *
import sound
from itertools import chain
from math import radians,pi,sin,cos
		
class Key (object):
	cos_pi_12=cos(pi/12)
	def __init__(self, node):
		self.node = node
		self.name = None
		self._touch = None
		self.texture = None
		self.highlight_texture = None
	@property 
	def touch(self):
		return self._touch
	@touch.setter
	def touch(self,value):
		if self._touch != value:
			self._touch=value
			self.node.texture= self.texture if value==None else self.highlight_texture
				
	def hit_test(self, touch):
		p0=self.node.parent.bounds.center()
		pt=touch.location-p0
		pk=self.node.position-p0
		abs_pt=abs(pt)
		abs_pk=abs(pk)
		rr=abs_pt/abs_pk
		cos_ang=sum(pt*pk)/(abs_pt*abs_pk)
		return (cos_ang>Key.cos_pi_12) and  rr>0.6 and rr<1.4
		
def make_key_images(r1,r2,scale=1.0):
	r1=r1*scale
	r2=r2*scale
	ang=pi/12.0
	key_img=[]
	s=sin(ang)
	c=cos(ang)
	h=2.0*r2*s
	w=r2-r1*c
	with ui.ImageContext(w,h) as ctx:
		p=ui.Path()
		x0=-c*r1
		y0=h/2
		p.move_to(x0+c*r1,y0+s*r1)
		p.add_arc(x0,y0,r1,ang,-ang,False)
		p.add_arc(x0,y0,r2,-ang,ang,True)
		p.close()
		for fill_color in [(1,1,1),(0.8,0.8,0.8),(0,0,0),(0.3, 0.3,0.3)]:
			ui.set_color(fill_color)
			p.fill()
			ui.set_color((0.5,0.5,0.5))
			p.stroke()
			key_img.append(ctx.get_image())
	return key_img
	
class Piano (Scene):
	def setup(self):
		self.white_keys = []
		self.black_keys = []
		self.all_keys = []
		r=0.49*min(self.size.w, self.size.h)
		key_textures = [Texture(img) for img in make_key_images(0.5*r,r,scale=1.0)]
		key_names = ['weier%d.wav'%i for i in range(12)]
		for key_name in key_names:
			sound.load_effect(key_name)
		white_positions = [3,5,7,8,10,0,2]#0=A
		black_positions = [ 4,6,  9,11,1]
		for i in range(12):
			ang=pi/6*(6+i)
			texture_index=0 if i in white_positions else 2
			key=Key(SpriteNode(key_textures[texture_index],scale=1.0,position=(self.size.w/2+cos(ang)*0.75*r,self.size.h/2+sin(ang)*0.75*r)))
			key.node.rotation=ang
			[key.texture, key.highlight_texture] = key_textures[texture_index:texture_index+2]
			key.name=key_names[i]
			self.all_keys.append(key)
		for i in chain(white_positions,black_positions):
			key=self.all_keys[i]
			self.add_child(key.node)
			self.white_keys.append(key)
		
	def touch_began(self, touch):
		for key in chain(self.black_keys, self.white_keys):
			if key.hit_test(touch):
				key.touch = touch
				sound.play_effect(key.name)
				return
	
	def touch_moved(self, touch):
		hit_key = None
		for key in chain(self.black_keys, self.white_keys):
			hit = key.hit_test(touch)
			if hit and hit_key is None:
				hit_key = key
				if key.touch is None:
					key.touch = touch
					sound.play_effect(key.name)
			if key.touch == touch and key is not hit_key:
				key.touch = None
				
	def touch_ended(self, touch):
		for key in chain(self.black_keys, self.white_keys):
			if key.touch == touch:
				key.touch = None
				
run(Piano(), LANDSCAPE)

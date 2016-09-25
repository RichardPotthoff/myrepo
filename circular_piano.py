# Piano
# 
# A simple multi-touch piano.

from scene import *
import sound
from itertools import chain
from math import radians,pi,sin,cos,sqrt,asin,acos
def v_sub(v1,v2):
	return [x-y for x,y in zip(v1,v2)]
def v_dot(v1,v2):
	return sum([x*y for x,y in zip(v1,v2)])
def v_len(v):
	return sqrt(sum([x*x for x in v]))
def distance(v1,v2):
	return v_len(v_sub(v1,v2))
def v_cross(v1,v2):
	return v1[0]*v2[1]-v2[0]*v1[1]
class Key (object):
	def __init__(self, node):
		self.node = node
		self.name = None
		self.touch = None
		self.texture = None
		self.highlight_Texture = None
		
	def hit_test(self, touch):
		p0=self.node.parent.bounds.center()
		pt=v_sub(touch.location,p0)
		pk=v_sub(self.node.position,p0)
		rt=v_len(pt)
		rk=v_len(pk)
		rr=rt/rk
		ang=acos(v_dot(pt,pk)/(rt*rk))
		return (abs(ang)<pi/12) and  rr>2/3 and rr<4/3
		
def pi_segment(r1,r2,ang1,ang2):
	p=ui.Path()
	s1=sin(ang1)
	c1=cos(ang1)
	s2=sin(ang2)
	c2=cos(ang2)
	x0=-0.5*(r1+r2)
	y0=0.0
	p.move_to(x0+c2*r1,y0+s2*r1)
	p.add_arc(x0,y0,r1,ang2,ang1,False)
#	p.line_to(r2+r2*c1,r2+r2*s1)
	p.add_arc(x0,y0,r2,ang1,ang2,True)
	p.close()
#	p.line_to(r2+r1*c2,r2+r1*s2)
	return p
def make_key_images(r1,r2):
	ang1=-pi/12.0
	ang2=pi/12.0
	key_img=[]
	s1=sin(ang1)
	c1=cos(ang1)
	s2=sin(ang2)
	c2=cos(ang2)
	h=2.0*r2*s2
	w=r2-r1*c1
#	print(w,h)
	with ui.ImageContext(w,h) as ctx:
		p=ui.Path()
		x0=-c1*r1
		y0=h/2
		p.move_to(x0+c2*r1,y0+s2*r1)
		p.add_arc(x0,y0,r1,ang2,ang1,False)
		p.add_arc(x0,y0,r2,ang1,ang2,True)
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
#		self.root_node=Node(self)
#		self.add_child(ShapeNode(position=(self.size.w/2.0,self.size.h/2.0),path=ui.Path.oval(self.size.w/2.0,self.size.h/2.0,self.size.w,self.size.h)))
		self.white_keys = []
		self.black_keys = []
		self.all_keys = []
		r2=0.49*min(self.size.w, self.size.h)
		r1=0.5*r2
		key_textures = [Texture(img) for img in make_key_images(r1,r2)]
		key_names = ['weier%d.wav'%i for i in range(12)]
		for key_name in key_names:
			sound.load_effect(key_name)
		white_positions = [3,5,7,8,10,0,2]
		black_positions = [ 4,6,  9,11,1]
		for i in range(12):
			a1=pi/6*(6+i)
			s=sin(a1)
			c=cos(a1)
#			key=Key(ShapeNode(position=(self.size.w/2+c*0.75*r2,self.size.h/2+s*0.75*r2), fill_color=(1,1,1), stroke_color=(0.5,0.5,0.5), path=pi_segment(r1,r2,-1*pi/12,1*pi/12)))
			key=Key(SpriteNode(key_textures[0],position=(self.size.w/2+c*0.75*r2,self.size.h/2+s*0.75*r2)))
			key.node.rotation=a1
			key.name=key_names[i]
			self.all_keys.append(key)
		for i in white_positions:
			key=self.all_keys[i]
			key.texture = key_textures[0]
			key.highlight_texture = key_textures[1]
			self.add_child(key.node)
			self.white_keys.append(key)
		for i in black_positions:
			key=self.all_keys[i]
			self.add_child(key.node)
			key.texture = key_textures[2]
			key.highlight_texture = key_textures[3]
			key.node.texture=key.texture
			self.black_keys.append(key)
		
	def draw(self):
		for key in chain(self.white_keys, self.black_keys):
			if key.touch is not None:
				key.node.texture=key.highlight_texture
			else:
				key.node.texture=key.texture
	
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

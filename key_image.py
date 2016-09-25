import ui
from math import sin,cos,pi,radians

def make_key_images():
	r1=100
	r2=200
	ang1=-pi/12
	ang2=pi/12
	key_img=[]
	with ui.ImageContext(110,110) as ctx:
		p=ui.Path()
		s1=sin(ang1)
		c1=cos(ang1)
		s2=sin(ang2)
		c2=cos(ang2)
		x0=55-0.5*(r1+r2)
		y0=55+0.0
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
key_images=make_key_images()
for img in key_images:
	img.show()
#pie_img = draw_pie(0.1, 200)
#pie_img.show()

import matplotlib.pyplot as plt
from math import sin,cos, pi

def show_plot():
  plt.axis('off')
  plt.axes().set_aspect('equal')	
  plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
  plt.show()
scale=0.8/128*96
r=0.9*scale
for i in range(32):
  rotation_deg=-360/32*i
  rotation_rad=rotation_deg/360*2*pi
  c=cos(rotation_rad)
  s=sin(rotation_rad)
  plt.text(c*r, s*r, '{:2d} $-$'.format(i), {'ha': 'center', 'va': 'center'}, size=20*scale,rotation=rotation_deg)
plt.plot(0,0,marker='+',color='black')
plt.axes().set_xlim(-1,1)
plt.axes().set_ylim(-1,1)
show_plot()
plt.savefig('dial32.png',dpi=300)
#Keywords: python, matplotlib, pylab, example, codex (see Search examples)

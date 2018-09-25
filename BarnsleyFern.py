import numpy as np
from pylab import *

M=[np.matrix([[ 0.  ,  0.  ,  0.  ], 
              [ 0.  ,  0.16,  0.  ],
              [ 0.  ,  0.  ,  1.  ]]).transpose(), 
   np.matrix([[ 0.85,  0.04,  0.  ],
              [-0.04,  0.85,  1.6 ],
              [ 0.  ,  0.  ,  1.  ]]).transpose(), 
   np.matrix([[ 0.2 ,-0.26,  0.  ],
              [ 0.23,  0.22,  1.6 ],
              [ 0.  ,  0.  ,  1.  ]]).transpose(), 
   np.matrix([[-0.15,  0.28,  0.  ],
              [ 0.26,  0.24,  0.44],
              [ 0.  ,  0.  ,  1.  ]]).transpose()]             
p = np.cumsum([0.01, 0.85, 0.07, 0.07])    #probabilities for each affine transformation
points=np.array([[0.0]*3]*100000)        
   
x=np.matrix([[0.0,0.0,1.0]])
for i in range(100000):
  x=x*M[np.searchsorted(p,np.random.rand())]
  points[i]=x
  
plot(points.transpose()[1],-points.transpose()[0],marker='.',linestyle='none',color='green',markersize=1)

axis('off')
axes().set_aspect('equal', 'datalim')	
subplots_adjust(left=0, right=1, top=1, bottom=0)
show()
xmax,ymax,_=np.max(points,0)
xmin,ymin,_=np.min(points,0)
ymin=0.0
for MM in M+[np.matrix(np.eye(3))]:
  box=asarray([[xmin,ymin,1],[xmin,ymax,1],[xmax,ymax,1],[xmax,ymin,1],[xmin,ymin,1]]*MM).transpose()
  plot(box[1][1:],-box[0][1:],color='red',linestyle='solid',linewidth=1)   
  plot(box[1][:2],-box[0][:2],color='blue',linestyle='solid',linewidth=1)           
show()


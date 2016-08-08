from numpy import *

def show_plot():
  axis('off')
  axes().set_aspect('equal', 'datalim')	
  subplots_adjust(left=0, right=1, top=1, bottom=0)
  show()
  close()
  
def mandel(n, m, itermax, xmin, xmax, ymin, ymax):
    ix, iy = mgrid[0:n, 0:m]
    x = linspace(xmin, xmax, n)[ix]
    y = linspace(ymin, ymax, m)[iy]
    c = x+complex(0,1)*y
    del x, y # save a bit of memory, we only need z
    img = zeros(c.shape, dtype=int)
    ix.shape = n*m
    iy.shape = n*m
    c.shape = n*m
    z = copy(c)
    for i in xrange(itermax):
        if not len(z): break # all points have escaped
        multiply(z, z, z)
        add(z, c, z)
        rem = abs(z)>2.0
        img[ix[rem], iy[rem]] = i+1
        rem = -rem
        z = z[rem]
        ix, iy = ix[rem], iy[rem]
        c = c[rem]
    return img
 
if __name__=='__main__':
    from pylab import *
    import time
    n=600
    x0=0.001643721971153
    y0=0.822467633298876
#    x0=-0.74688-1e-4-1.25e-6+1.75e-8-0.075e-10
#    y0=0.1+0.3e-8-0.1e-10
#    x0=-0.75
#    x0=-2.0
#    y0=0.0
    for zoom in(1.0,1e2,1e4,1e6,1e8,5e10):
      start = time.time()
      dx=1.25/zoom
      dy=1.25/zoom
      I = mandel(400, 400,n,x0-dx, x0+dx, y0-dy,y0+dy)
      print 'Time taken:', time.time()-start, "zoom=",zoom
      I[I==0] = n+1
      I[198:201,198:201]=3*n/4+1
      I[199,199]=n+1
      img = imshow(I.T, origin='lower left')
#      img.write_png('mandel.png', noscale=True)
      show_plot()
import numpy as np
import matplotlib.pyplot as plt
def fswell(r,dr,a):
  return a*2.718281828459**(-(r**2/(2*dr**2)))
def fdisp(r,dr,a):
  return r*(1+fswell(r,dr,a))
def fdisp_(r,dr,a):
  return (1-(r/dr)**2)*fswell(r,dr,a)+1
def fdisp_inv(r_,dr,a):
  def fy(x):
    return fdisp(x,dr,a)
  def fy_(x):
    return fdisp_(x,dr,a)
  x=r_
  i=0
  while True:
    dx=(fy(x)-r_)/fy_(x)
    if abs(dx)<abs(x*1e-8):break
    i+=1
    x-=dx
#  print (i)
  return x
def f1(x,y,dr=.4,a=1):
  r=(x**2+y**2)**0.5
  disp=fdisp_inv(r,dr,a)/r
  return [x*disp,y*disp]
x=np.arange(-2,2,0.1)
y=x
a=1
dr=0.4
p1=np.array([f1(x_,y_,dr=dr,a=a) for y_ in y for x_ in x])
plt.plot([x for x,y in p1],[y for x,y in p1],linestyle='none',marker='+')
plt.show()
plt.close()
plt.plot(x,[fdisp(x_,dr,a) for x_ in x])
plt.plot(x,[fdisp_(x_,dr,a) for x_ in x])
plt.plot(x,x)
plt.show()
plt.close()


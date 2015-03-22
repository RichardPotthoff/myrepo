#Examples from: http://nbviewer.ipython.org/github/empet/Math/blob/master/DomainColoring.ipynb

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import hsv_to_rgb
rcdef = plt.rcParams.copy()
plt.rcParams['figure.figsize'] = 10,10
plt.rcParams['figure.figsize'] = 10, 6
sat=[1.0, 0.85, 0.5, 0.25]
svals=['S=1', 'S=0.85', 'S=0.5', 'S=0.25']
for k, s in zip(range(4),sat):
    V,H = np.mgrid[0:1:200j, 0:1:200j]
    S = s*np.ones_like(H)  
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
    plt.subplot(2,2,k+1)
    plt.imshow(RGB, origin="lower", extent=[0, 1, 0, 1])
    plt.xticks([0, 1.0/6, 1.0/3, 1.0/2,  2.0/3, 5.0/6, 1],
    ['$0$', r'$\frac{1}{6}$', r'$\frac{1}{3}$', r'$\frac{1}{2}$', r'$\frac{2}{3}$',
     r'$\frac{5}{6}$', '$1$'])
    plt.xlabel("$H$")
    plt.ylabel("$V$")
    plt.title(svals[k])
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.tight_layout(1)    
plt.show()
plt.close()

def Hcomplex(z):# computes the hue corresponding to the complex number z
    H=np.angle(z)/(2*np.pi)+1
    return np.mod(H,1)

def func_vals(f, re, im,  N): #evaluates the complex function at the nodes of the grid
   #re and im are  tuples, re=(a,b) and im=(c,d), defining the rectangular region
   #N is the number of nodes per unit interval 
    
   l=re[1]-re[0]
   h=im[1]-im[0]
#   resL=N*l #horizontal resolution
#   resH=N*h#vertical resolution
   resL=N #horizontal resolution
   resH=N #vertical resolution
   x=np.linspace(re[0], re[1],resL)
   y=np.linspace(im[0], im[1], resH)
   x,y=np.meshgrid(x,y)
   z=x+1j*y
   w=f(z)
   return w 
   
def domaincol_c(w, s):#Classical domain coloring
    #w is the complex array of values f(z)
    #s is the constant saturation
    indi=np.where(np.isinf(w))#detects the values w=a+ib, with a or b or both =infinity
    indn=np.where(np.isnan(w))#detects nans
    H=Hcomplex(w)
    S = s*np.ones_like(H)
    modul=np.absolute(w)
    V= (1.0-1.0/(1+modul**2))**0.2
    # the points mapped to infinity are colored with white; hsv_to_rgb(0,0,1)=(1,1,1)=white
    H[indi]=0.0 
    S[indi]=0.0  
    V[indi]=1.0
    #hsv_to_rgb(0,0,0.5)=(0.5,0.5, 0.5)=gray  
    H[indn]=0
    S[indn]=0
    V[indn]=0.5
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
    return RGB     
        
def domaincol_m(w,  s): #domain coloring with modulus track
   
   # w the array of values
   #s is the constant Saturation
   
   H=Hcomplex(w) 
   modulus=np.absolute(w)
   c= np.log(2)
   Logm=np.log(modulus)/c#log base 2
   Logm=np.nan_to_num(Logm)
   
   V=Logm-np.floor(Logm)
   S = s*np.ones_like(H, float)
   
   HSV = np.dstack((H,S,V**0.2))# V**0.2>V for V in[0,1];this choice  avoids too dark colors
   RGB=hsv_to_rgb(HSV) 
   return RGB
   
def perfract(x, t, m, M):
    x=x/t
    return m+(M-m)*(x-np.floor(x))

def domaincol_co(w,s):
    H=Hcomplex(w) 
    m=0.7 # brightness is restricted to [0.7,1]; interval suggested by E Wegert
    M=1
    n=15 # n=number of isochromatic lines per cycle 
    isol=perfract(H, 1.0/n, m, M) # isochromatic lines
    modul=np.absolute(w)
    Logm=np.log(modul)
    Logm=np.nan_to_num(Logm) 
    modc=perfract(Logm, 2*np.pi/n, m, M)# lines of constant log-modulus
   
    V=modc*isol 
    S = 0.9*np.ones_like(H, float) 
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
   
    return RGB
    
   
def plot_domain(color_func, f,   re=[-1,1], im= [-1,1], Title='',
                s=0.9, N=600, daxis=None):
    w=func_vals(f, re, im, N)
    domc=color_func(w, s)
    plt.xlabel("$\Re(z)$")
    plt.ylabel("$\Im(z)$")
    plt.title(Title)
    if(daxis):
         plt.imshow(domc, origin="lower", extent=[re[0], re[1], im[0], im[1]])
       
    else:
        plt.imshow(domc, origin="lower")
        plt.axis('off')
        
plt.rcParams['figure.figsize'] = 8, 5
ab=[-2,2]
cd=[-2,2]
plt.subplot(1,2,1)
f=lambda z: (z**3-1)/z
plot_domain(domaincol_c, f, re=ab, im= cd, Title='$f(z)=(z^3-1)/z$', daxis=True)
plt.subplot(1,2,2)
plot_domain(domaincol_c, lambda z:z, re=[-7, 7], im=[-7, 7], Title='$z$', daxis=True)
plt.tight_layout(2)  
plt.show()
plt.close()
ab=(-1,3)
cd=(-2,2)
f=lambda z: np.sin(z)/(z-1j)**2
plt.subplot(1,2,1)
plot_domain(domaincol_c,  f,   re=ab, im=cd, Title='$f(z)=\sin z/(z-i)^2$', daxis=True)
plt.subplot(1,2,2)
plot_domain(domaincol_m,  f,   re=ab, im=cd, Title='$f(z)=\sin z/(z-i)^2$', daxis=True)
plt.tight_layout(1)
plt.show()
plt.close()
plt.subplot(1,2,1)
plot_domain(domaincol_co,  f,   re=ab, im=cd, Title='$f(z)=\sin z/(z-i)^2$', daxis=True)
plt.tight_layout(1)
plt.show()
plt.close()
plt.subplot(1,2,1)
ab=(-2,2)
cd=(-2,2)
f=lambda z: (z**6-1)/(z**12+1)
plot_domain(domaincol_m,  f,   re=ab, im=cd, Title='$f(z)=(z^6-1)/(z^{12}+1)$', daxis=True)
plt.subplot(1,2,2)
ab=(-1.3,1.3)
cd=(-1.3,1.3)
plot_domain(domaincol_m,  f,   re=ab, im=cd, Title='$f(z)=(z^6-1)/(z^{12}+1)$', daxis=True)
plt.tight_layout(2)
plt.show();plt.close()

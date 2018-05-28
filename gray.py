from pylab import *
import matplotlib
def show_plot():
  axis('off')
  axes().set_aspect('equal', 'datalim')	
  subplots_adjust(left=0, right=1, top=1, bottom=0)
  show()
  close()
def ror(x,p,n):
  x&=(1<<n)-1
  p%=n
  return ((x>>p)|(x<<(n-p)))&((1<<n)-1)
for b in range(256):
  y=[0]*16
  p=0
  d={}
  d[0]=0
  for i in range(2,16):
    x=y[i-1]
    p=(p+((b>>(ror(x,p-1,4)&0b111))&0b1)*2-1)%4
    y[i]=x^(1<<p)
    if y[i] in d: 
      break
    else:
      d[y[i]]=i
#  print(b,len(d),y[len(d)-1],y[8],d[15]if 15 in d else 0)
def gen_rl_gray(n):
  if n==0:
    return[0b0]
  else:
    gray_n_1=gen_rl_gray(n-1)
    gray_n_1=[gray_n_1[-1]]+gray_n_1[:-1]
    return [(x<<1)|0b1 for x in gray_n_1]+[(x<<1)|0b0 for x in reversed(gray_n_1)]
def bits(x,n):
  return [(x>>j)&1 for j in range(n)]
arr=[[bit for _ in range(2) for bit in bits(x,4) ]+[0]*2 for x in y*2]

#plt.imshow(arr,cmap=plt.cm.binary,interpolation="nearest")
#plt.show()
#show_plot()
#quit()
def bit_count(n):
    """Return the number of bits set to 1 in the integer number 'n'.
       This is called the Hamming weight or the population count of 'n'.
       The algorithm performs as many iterations as there are set bits.
       References:
         The C Programming Language 2nd Ed., Kernighan & Ritchie, 1988.
         Peter Wegner in CACM 3 (1960), 322.
    """
    assert n >= 0, 'Argument of bit_count() must be non-negative'
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
    
def gen_graycodes(nbit=4):
#  for i in (0b11111111111111,0b0000000000000):
  bmax=1<<(nbit-1)
  ncodes=2**nbit
#  print(bmax)
  for i in range(2**(ncodes-2)):
#    if (((bit_count(i)+2)*2)%nbit)!=0:continue
    bm=bmax
    i1=i<<2|0b11
    code=0
    gray={}
    gray[0]=0
    for j in range(2**nbit):
      if i1 & 1<<j:
        bm=bm<<1 if bm<bmax else 1
      else:
        bm=bm>>1 if bm>1 else bmax
      code^=bm
      if code in gray:continue
      gray[code]=j+1
#    if (len(gray)==ncodes)and(code==0)and(bm==bmax):
    if (len(gray)==ncodes)and(code==0):
      yield i1,gray
  
z=[]
for i,x in gen_graycodes(nbit=4):
  if bit_count(i)%2!=0:continue
  y=[None]*17
  y[0]=0
  for j in range(16):
    y[x[j]]=j
#  if bit_count(i)==8:
  z.append((i,y[:]))
#  print(z[-1])

cursor=[3]*len(z)

for k in range(16):
  for j,(i,y) in enumerate(z):
    cursor[j]+=((i>>k)&1)*2-1
    print('{:04b} {:01b} {:1d} '.format(y[k],(i>>k)&1,cursor[j]%4),end='')
  print()
for i,y in z:
  print('    {:2d}   '.format(2*bit_count(i)-16),end='')
print()
n=4
m=2**n
z=[(0,gen_rl_gray(n))]
arr=[[((x|(x<<n))>>j)&1  for i,y in z for x in [y[k]] for j in range(2*n-1,-1,-1)] for k1 in range(2) for k in range(m) ]
plt.imshow(arr, cmap='binary',interpolation="nearest")
x=[2*n-1-j+10*i  for k1 in range(2) for k in range(m)for i,(_,y) in enumerate(z) for x,x1 in [(y[k],y[(k-1)%m])] for x2 in [(x^x1)|((x^x1)<<n)] for j in range(2*n-1,-1,-1) if ((x2>>j)&1)==1]
y=[k+m*k1  for k1 in range(2) for k in range(m)for i,(_,y) in enumerate(z) for x,x1 in [(y[k],y[(k-1)%m])] for x2 in [(x^x1)|((x^x1)<<n)] for j in range(2*n-1,-1,-1) if ((x2>>j)&1)==1]
plt.plot(x,y,marker='.',linestyle='none',color='red')
show_plot()
arr=[[((x2>>j)&1)==1  for i,(_,y) in enumerate(z) for x,x1 in [(y[k],y[(k-1)%m])] for x2 in [(x^x1)|((x^x1)<<n)] for j in range(2*n-1,-1,-1)] for k1 in range(2) for k in range(m)]
plt.imshow(arr,cmap=plt.cm.binary,interpolation="nearest")
#plt.show()
show_plot()
quit()
quit()

for i,y in z:
  print('{:016b}'.format(i))
  cursor=[0]*(len(y))
  for k in range(len(y)-1):
    cursor[k+1]=cursor[k]+(i&1)*2-1
    i>>=1
  plt.plot(cursor)
  plt.show()
  plt.close()
  


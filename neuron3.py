import numpy as np
import pprint

def nonlin(x,deriv=False):
	if(deriv==True):
	    return x*(1-x)

	return 1/(1+np.exp(-x))
	
def inttobin(i,n):
	return [0]*(i-1)+[1]+[0]*(n-i)
def Xfrom_ij(i,j,n=5):
	return inttobin(i,n)+inttobin(j,n)+[1]
X=np.array([Xfrom_ij(i,j) for i in range(1,6) for j in range(1,6) if abs(i-j)==1])
y=np.array([[max(0,i-j),max(0,j-i)] for i in range(1,6) for j in range(1,6) if abs(i-j)==1])
def l2_fromX(X):
    global syn0,syn1
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))
    return l2

np.random.seed(1)

# randomly initialize our weights with mean 0
syn0 = 2*np.random.random((11,3)) - 1
syn1 = 2*np.random.random((3,2)) - 1

for j in range(600):

	# Feed forward through layers 0, 1, and 2
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))
    # how much did we miss the target value?
    l2_error = y - l2
    
    if (j% 100) == 0:
        print("Error:" + str(np.mean(np.abs(l2_error))))
        
    # in what direction is the target value?
    # were we really sure? if so, don't change too much.
    l2_delta = l2_error*nonlin(l2,deriv=True)

    # how much did each l1 value contribute to the l2 error (according to the weights)?
    l1_error = l2_delta.dot(syn1.T)
    
    # in what direction is the target l1?
    # were we really sure? if so, don't change too much.
    l1_delta = l1_error * nonlin(l1,deriv=True)

    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)
    
([[l2_fromX(Xfrom_ij(i+1,j+1))[0] for j in range(5) ]for i in range(5)])

print('  i\j',end='')
for j in range(1,6):
	print('%4d '%j,end='')
print()
for i in range(1,6):
	print('%3d: '%i,end='')
	for j in range(1,6):
		print('%5.2f'%(l2_fromX(Xfrom_ij(i,j))[0]),end="")
	print()

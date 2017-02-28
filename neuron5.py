""" 
TI (transitive inference) 
neural network model, 
non-transitive case circular,(1>5)
10 inputs (5+5), 
2 outputs, 
1 hidden layer with 3 neurons
"""
import numpy as np
import pprint

def nonlin(x,deriv=False):
	if(deriv==True):
	    return x*(1-x)
	return 1/(1+np.exp(-x))
	
def l2_fromX(X):
    global syn0,syn1
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))
    return l2
	
def inttobin(i,n):
	return [0]*(i-1)+[1]+[0]*(n-i)
def Xfrom_ij(i,j,n=5):
	return inttobin(i,n)+inttobin(j,n)+[1]
def printresult():
	for k in range(3):
		print(['  output i (i>j):             ','  output j (j>i):       ','        output i > output j'][k] ,end='')
	print()
	for k in range(3):
		print('  i\j',end='')
		for j in range(1,6):
			print('%4d '%j,end='')
	print()
	for i in range(1,6):
		for k in range(3):
			print('%3d: '%i,end='')
			for j in range(1,6):
				if k<2:
					print('%5.2f'%(l2_fromX(Xfrom_ij(i,j))[k]),end="")
				else:
					print('   %s '%((lambda x:' ' if i==j else '+' if x[0]>x[1] else '-')(l2_fromX(Xfrom_ij(i,j)))),end="")
		print()

np.random.seed(1)
n_input=5+5+1
n_hidden=3
n_output=2
# randomly initialize our weights with mean 0
syn0 = 2*np.random.random((n_input,n_hidden)) - 1
syn1 = 2*np.random.random((n_hidden,n_output)) - 1
print('Result for untrained neural net:')
printresult()
print()
X=[]
y=[]
print('Training Set:')
print(' inputs   outputs')
print('  i   j   i>j  j>i')
for i1 in range(0,6):
	i=i1%5+1
	for j1 in range(0,6):
		j=j1%5+1
		if abs(i1-j1)==1:
			X.append(Xfrom_ij(i,j))
			y.append([max(0,i1-j1),max(0,j1-i1)])
			print('%3d %3d %4d %4d'%(i,j,max(0,i1-j1),max(0,j1-i1)))
print()
print

X=np.array(X)
y=np.array(y)

for j in range(1281):

	# Feed forward through layers 0, 1
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))
    # how much did we miss the target value?
    l2_error = y - l2
    if j in (0,5,10,20,40,80,160,320,640,1280):
        print('After %d training steps:'%(j))
        printresult()
        print("Error:" + str(np.mean(np.abs(l2_error))))
        print()
    # in what direction is the target value?
    l2_delta = l2_error*nonlin(l2,deriv=True)

    # how much did each l1 value contribute to the l2 error (according to the weights)?
    l1_error = l2_delta.dot(syn1.T)
    
    # in what direction is the target l1?
    # were we really sure? if so, don't change too much.
    l1_delta = l1_error * nonlin(l1,deriv=True)

    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)
    
print()
print('Synaptic strengths:')
print(' input  ',end='')
for k in range(n_hidden):
	print('  hidden%d '%(k+1), end='')
print()
for l in range(n_input):
	if l in (5,10):print()
	if l<5:
		print(' i =%2d  '%(l+1),end='')
	elif l<10:
		print(' j =%2d  '%(l-4),end='')
	else:
		print(' bias   ',end='')
	for k in range(n_hidden):
		print('%9.4f '%(syn0[l,k]),end='')
	print()
	
print()	
print(' hidden   ',end='')
for k in range(n_output):
	print(' output %d'%(k+1), end='')
print()
for l in range(n_hidden):
	print(' h =%2d  '%(l+1),end='')
	for k in range(n_output):
		print('%9.4f '%(syn1[l,k]),end='')
	print()

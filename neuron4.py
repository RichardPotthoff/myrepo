""" 
TI (transitive inference) 
neural network model, 
10 inputs (5+5), 
2 outputs, 
no hidden layers
"""
import numpy as np
import pprint

def nonlin(x,deriv=False):
	if(deriv==True):
	    return x*(1-x)
	return 1/(1+np.exp(-x))
	
def l1_fromX(X):
    global syn0
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    return l1
	
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
					print('%5.2f'%(l1_fromX(Xfrom_ij(i,j))[k]),end="")
				else:
					print('   %s '%((lambda x:' ' if i==j else '+' if x[0]>x[1] else '-')(l1_fromX(Xfrom_ij(i,j)))),end="")
		print()

np.random.seed(1)

# randomly initialize our weights with mean 0
syn0 = 2*np.random.random((11,2)) - 1
print('Result for untrained neural net:')
printresult()
print()
X=[]
y=[]
print('Training Set:')
print(' inputs   outputs')
print('  i   j   i>j  j>i')
for i in range(1,6):
	for j in range(1,6):
		if abs(i-j)==1:
			X.append(Xfrom_ij(i,j))
			y.append([max(0,i-j),max(0,j-i)])
			print('%3d %3d %4d %4d'%(i,j,max(0,i-j),max(0,j-i)))
print()
print

X=np.array(X)
y=np.array(y)

for j in range(641):

	# Feed forward through layers 0, 1
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    # how much did we miss the target value?
    l1_error = y - l1
    if j in (0,5,10,20,40,80,160,320,640):
        print('After %d training steps:'%(j))
        printresult()
        print("Error:" + str(np.mean(np.abs(l1_error))))
        print()
    # in what direction is the target value?
    # were we really sure? if so, don't change too much.
    l1_delta = l1_error*nonlin(l1,deriv=True)
    syn0 += l0.T.dot(l1_delta)
print()
print('Synaptic strengths:')
print(' input    output i  output j')
for l in range(11):
	if l in (5,10):print()
	if l<5:
		print(' i =%2d  '%(l+1),end='')
	elif l<10:
		print(' j =%2d  '%(l-4),end='')
	else:
		print(' bias   ',end='')
	for k in range(2):
		print('%9.4f '%(syn0[l,k]),end='')
	print()

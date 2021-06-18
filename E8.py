import numpy as np
np.seterr(divide='ignore')
E8=np.array([[1,-1,0,0,0,0,0,0],[0,1,-1,0,0,0,0,0],[0,0,1,-1,0,0,0,0],[0,0,0,1,-1,0,0,0],[0,0,0,0,1,-1,0,0],[0,0,0,0,0,1,-1,0],[0,0,0,0,0,1,1,0],[-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5]])
E8_odd=np.array([[1,-1,0,0,0,0,0,0],[0,1,-1,0,0,0,0,0],[0,0,1,-1,0,0,0,0],[0,0,0,1,-1,0,0,0],[0,0,0,0,1,-1,0,0],[0,0,0,0,0,1,-1,0],[0,0,0,0,0,0,1,-1],[-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5]])


E8_nsym=np.array([[2*np.pi/np.arccos(sum(E8i*E8j)/2.0) for E8i in E8]for E8j in E8 ])
E8_odd_nsym=np.array([[2*np.pi/np.arccos(sum(E8i*E8j)/2.0) for E8i in E8_odd]for E8j in E8_odd ])

E8_dynkin=[(j,i)for i in range(1,8) for j in range(i) if sum(E8[i]*E8[j])==-1]
E8_odd_dynkin=[(j,i)for i in range(1,8) for j in range(i) if sum(E8_odd[i]*E8_odd[j])==-1]

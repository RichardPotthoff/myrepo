def calcTangent(c1,r1,c2,r2):
    c2_c1=(c2-c1)
    lcc=abs(c2_c1) 
    ec2_c1=c2_c1/lcc
    cosphi=((r1+r2)/lcc)
    phi=-cosphi+1j*(1-cosphi**2)**0.5
    t1=c1-r1*ec2_c1*phi
    t2=c2+r2*ec2_c1*phi
    return [t1,t2]

class NamedList(list): 
    """
    A mutable version of namedtuple.
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args)
        super().__setattr__('_lookup',dict())
        self._lookup.update({ f'_{i}':i for i in range(len(self))})
        self.update(**kwargs)
    def __setattr__(self,name,value):
           self.update(**{name:value})
    def __getattr__(self,name):
        try: 
          return self[self._lookup[name]]
        except:
          raise AttributeError(f"Found no attribute named '{name}'.  ")
    def append(self,value):
        raise IndexError(f"Use the 'update' method to add elements to a {self.__class__.__name}!") 
    def extend(self,value):
        raise IndexError(f"Use the 'update' method to add elements to a {self.__class__.__name}!") 
    def update(self,*args,**kwargs): 
        if len(args)>0:
           if len(args)>len(self):
              self[:]=args[:len(self)]
              self._lookup.update({f'_{i}':i for i in range(len(self),len(args))})
              super().extend(args[len(self):])
           else:
              self[:len(args)]=args
        for name,value in kwargs.items():
            if  not name in self._lookup:
                if name[0]=='_':
                    new_index=int(name[1:])
                    self._lookup.update({f'_{i}':i for i in range(len(self),new_index+1)})
                    super().extend([None]*(new_index-len(self)+1))
                    self[new_index]=value
               #     KeyError(f"Error in 'update': Field '{name}' does not exist.")
                else:
                   self._lookup[f'_{len(self)}']=len(self)
                   self._lookup[name]=len(self)
                   super().append(value)
            else:
                self[self._lookup[name]]=value
        return self
    def alias(self,*args,**kwargs):
        if len(args)>0:
            if len(args)>len(self):
                self._lookup.update({f'_{i}':i for i in range(len(self),len(args))})
                super().extend([None]*(len(args)-len(self)))
            self._lookup.update({name:i for i,name in enumerate(args)})
        for name,alias in kwargs.items():
            if type(alias)!=str:
                raise KeyError(f"Error in 'alias': Field name '{alias}' must be a  valid variable name.")
            if alias[0]=='_':
                raise KeyError(f"Error in 'alias': Field name '{alias}' must not start with an underscore ('_').")
            if alias in self._lookup:
                if self._lookup[alias]==self._lookup[name]:
                    return
                else:
                    raise KeyError(f"The alias name '{alias}' is already used for a different field.")
            self._lookup[alias]=self._lookup[name]
    equivalence=alias
    def rename(self,**kwargs):
        for old_name,new_name in kwargs.items():
            if old_name[0]=='_':
                raise KeyError(f"The name '{old_name}' cannot be renamed.")
            
            if (new_name!=None) and (new_name[0]=='_'):
                raise KeyError(f"Error in 'rename': Field name '{new_name}' must not start with an underscore ('_').")
            old_index=self._lookup.pop(old_name,None)
            if old_index==None:
                raise KeyError(f"The name '{old_name}' does not exist.")
            if new_name in self._lookup:
                if self._lookup[new_name]==old_index:
                    return
                else:
                    raise KeyError(f"The name '{alias}' is already used for a different member of the list.")
            if new_name!=None:
                self._lookup[new_name]=old_index
    def __repr__(self):
        args=", ".join(f'{key}={value}' for key,value in self.as_dict().items())
        return f'{self.__class__.__name__}({args})' 
    def as_dict(self):
        key_for_index={index:key for key,index in self._lookup.items()}
        return {key_for_index.get(index,index):value for index,value in enumerate(self)}
    def copy(self):
        myCopy=self.__class__(*self)
        super(myCopy.__class__,myCopy).__setattr__('_lookup',self._lookup.copy())
        return myCopy


# In[3]:


#from bisect import bisect_right
def bisect_right(a,x,lo=0,hi=None):
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo

def index_frac(x,ax):
    idx=bisect_right(ax,x,1,len(ax)-1)
    return idx-1,(x-ax[idx-1])/(ax[idx]-ax[idx-1])
    
def interp(x,ax,ay):
    idx=bisect_right(ax,x,1,len(ax)-1)
    return ay[idx-1]+(x-ax[idx-1])/(ax[idx]-ax[idx-1])*(ay[idx]-ay[idx-1])

def cumsum(x,x_start=None):
    if x_start!=None:
        csum=[x_start]+x.copy()
    else:
        csum=x.copy()
    for i in range(1,len(csum)):
        csum[i]+=csum[i-1]
    return csum
        


# In[4]:


#interpSegments, Segments2Complex

def polygonArea(p):
  def crossprod(v1,v2):
    return v1.real*v2.imag-v2.real*v1.imag
  return 0.5*np.sum(crossprod(p[range(-1,len(p)-1)],p))

def SegmentsLength(Segs):
    return sum(l for l,*_ in Segs)

def SegmentsArea(Segs):
  nSegs=len(Segs)
  dl,dang,*opts=np.array(Segs).transpose()
  ang=np.cumsum(dang)
  ang=exp(1j*np.insert( ang,0,0))
  dang_2=np.exp(1j*dang/2)
  viSeg=np.sinc(dang/(2*pi))*dl*dang_2*ang[:-1]
  pSeg=np.cumsum(viSeg)
  olderr=np.geterr()
  np.seterr(divide='ignore',invalid='ignore')#suppress the warnings from 0/0 = nan. nansum assumes nan=0, which is the correct value in this case
  area=polygonArea(pSeg) +  np.nansum((dl/dang)**2*(dang/2.0-dang_2.real*dang_2.imag))
  np.seterr(**olderr)
  return area


def Segments2Complex(Segs,p0=0.+0.j,scale=1.0,a0=0+1j,tol=0.05,offs=0,loops=1,return_start=False):
  from math import inf
  from cmath import exp as cmath_exp
  """
  The parameter "tol defines the resolution. It is the maximum allowable
  difference between circular arc segment, and the secant between the
  calculated points on the arc. Smaller values for tol will result in
  more points per segment.
  """
  a=a0
  p=p0
  p-=1j*a*offs
  L=0
  if return_start:
      yield p,a,L,-1 #assuming closed loop: start-point = end-point
  loopcount=0
  while (loops==None) or (loops==inf) or (loopcount<loops):
      loopcount+=1
      for X,(l,da,*_) in enumerate(Segs):
        l=l*scale
        if da!=0:
          r=l/da
          r+=offs
          if r!=0:
            l=r*da
            dl=2*abs(2*r*tol)**0.5
            n=max(int(abs(6*(da/(2*pi)))),int(l//dl)+1)
          else:
            n=1
          dda=cmath_exp(1j*da/n)
          dda2=dda**0.5
          v=(2*r*dda2.imag)*dda2*a
        else:
          n=1
          dda=1
          v=l*a
        for i in range(n):
          L+=l/n
          p+=v
          yield p,a,L,X
          v*=dda
          a*=dda


# In[5]:


def arcChainInterpolator(*,arcChain,p0=0.+0.j,a0=0+1j,scale=1.0,eps=1e-6):
  """
  Segment points are calculated for values of 't', where 't' is the normalized
  length of the path. t is in the range of [0..1[
  """
  from cmath import exp as cmath_exp
  from math import sin
  def sinc(alpha):
    return 1.0 if alpha==0 else sin(alpha)/alpha
  dl=[arc[0] for arc in arcChain]
  dang=[arc[1] for arc in arcChain]  
  L=cumsum(dl,0.0)
  l=[L_/L[-1] for L_ in L]
  ang_=cumsum(dang,0.0)
  ang=[cmath_exp(1j*ang_) for ang_ in ang_]
  viSeg=[sinc(dang/2)*dl*scale*cmath_exp(1j*dang/2)*ang for dang,dl,ang in zip(dang,dl,ang[:-1])]
  pSeg=cumsum(viSeg,0+0j)
  l_idx=list(range(len(l)))
  is_closed_loop=((abs(pSeg[-1])<eps) and (abs(ang[-1]-(1+0j))<eps))
  def interpolateArcChain(t):
      T=int(t)
      if is_closed_loop:
          pr,ar=0.0+0.0j,1.0+0.0j
      else: #endpoint of path != startpoint => repeat path for t>1 by translating and rotating it
          v=pSeg[-1]
          beta=ang_[-1]
          beta2=beta/2
          rot2=cmath_exp(1j*beta2)
          pr=(v*rot2**(T-1)/sinc(beta2) * T * sinc(T*beta2))*a0 #???
          ar=(rot2**(2*T))
      pr+=p0
      ar*=a0
      X,x=index_frac(t-T,l)
      p=pSeg[X] + sinc( dang[X]*x/2)* dl[X]*x *scale*cmath_exp(1j* dang[X]*x /2)*ang[X]
      p=p*ar+pr
      a=ang[X]*cmath_exp(1j*dang[X]*x)*ar
      return p,a,L[-1]*t,X
  return interpolateArcChain


# In[6]:


def ISO_thread(z=None,phi=0.0,*,Pitch,External=False):
    tan60=3**0.5
    cos60=0.5
    sin60=tan60*cos60
    Pitch2=Pitch/2
    H=(Pitch2)*tan60
    flank_start=Pitch2/8
    r_maj=flank_start/sin60
    r_maj2=r_maj**2
    c_maj=-flank_start/tan60
    r_min=2*r_maj    
    r_min2=r_min**2
    c_min=-5/8*H+Pitch2/4/tan60
    flank_end=(3/4)*Pitch2
    if External:
        def ISO_thread_(z,phi=phi,*_,**__):
            dz=abs((z-phi*Pitch+Pitch2)%Pitch-Pitch2)#use symmetries
            if dz<flank_start:
                return 0.0
            if dz<=flank_end:
                return -tan60*(dz-flank_start)
            return  (c_min-(r_min2-(Pitch2-dz)**2)**0.5)
    else:# internal thread
        def ISO_thread_(z,phi=phi,*_,**__):
            dz=abs((z-phi*Pitch+Pitch2)%Pitch-Pitch2)#use symmetries
            if dz<flank_start:
                return c_maj+(r_maj2-dz**2)**0.5
            if dz<=flank_end:
                return -tan60*(dz-flank_start)
            return -5/8*H
    return ISO_thread_(z) if z!= None else ISO_thread_




#transformer, rotor,...
def mesh_transformer(*,  R_rim, R_hub, outline, p0o, n0o, outline_stretch=None, inline,  p0i, n0i, inline_stretch=None, finline_offset=lambda *_:0.0, foutline_offset=lambda *_:0.0, **kwargs):
    from cmath import polar as cmath_polar
    unstretched_outline=cumsum([l for l,*_ in outline],0.0)
    unstretched_outline=[x/unstretched_outline[-1] for x in unstretched_outline]
    outlineInterpolator_=arcChainInterpolator(arcChain=outline,p0=p0o,a0=n0o)
    if outline_stretch!=None:
        stretched_outline=cumsum([l/s for (l,*_),s in zip(outline,outline_stretch)],0.0)
        stretched_outline=[x/stretched_outline[-1] for x in stretched_outline]
        outlineInterpolator=lambda T_mesh:outlineInterpolator_(interp(T_mesh,stretched_outline,unstretched_outline))
    else:
        outlineInterpolator=outlineInterpolator_
    unstretched_inline=cumsum([l for l,*_ in inline],0.0)
    unstretched_inline=[x/unstretched_inline[-1] for x in unstretched_inline]
    inlineInterpolator_=arcChainInterpolator(arcChain=inline,p0=p0i,a0=n0i)
    if inline_stretch!=None:
        stretched_inline=cumsum([l/s for (l,*_),s in zip(inline,inline_stretch)],0.0)
        stretched_inline=[x/stretched_inline[-1] for x in stretched_inline]
        inlineInterpolator=lambda T_mesh:inlineInterpolator_(interp(T_mesh,stretched_inline,unstretched_inline))
    else:
        inlineInterpolator=inlineInterpolator_
    def transform_mesh(pz):
      p=pz[0]
      #transform raw mesh to tripod shape: 
      T_mesh=(cmath_polar(p)[1]/(2*pi))%1.0 #phase angle of mesh points [0..1[
      r_mesh=abs(p)#amplitude of mesh points
      pout,aout,Lout,*_=outlineInterpolator(T_mesh)
      pout+=aout*1j*foutline_offset(pz[1],Lout)
      pin,ain,Lin,*_=inlineInterpolator(T_mesh)
      pin+=ain*1j*finline_offset(pz[1],Lin)
      p_transformed_point=pin+(pout-pin)*((r_mesh-R_hub)/(R_rim-R_hub)) #transform raw mesh to tripod shape
      pz[0]=p_transformed_point
      return pz
    return transform_mesh
        
def calibrator(*,p_center=0.0+0.0j, r_ref, dr_offset=0.0, f_offset=None, dr_rigid=0.0,mesh_compression=2.0, ew_factor=None, **kwargs):
    from cmath import polar as cmath_polar
    r_rigid_max=r_ref+dr_rigid
    r_rigid_min=r_ref-dr_rigid
    def calibrate(p_z_ew):
        p=p_z_ew[0]
        dr=dr_offset
        if ew_factor!=None:
            dr+=p_z_ew[2]*ew_factor
        dp=p-p_center
        r=abs(dp)
        if f_offset==None:
            r_max=r_rigid_max+dr/2+abs(dr)*(0.5+1/(mesh_compression-1))
            r_min=r_rigid_min+dr/2-abs(dr)*(0.5+1/(mesh_compression-1))
            if (r>r_max) or (r<r_min): 
                return p_z_ew#return early if point is outside the affected zone
        phi=dp/r
        if f_offset!=None:
            dr+=f_offset(p_z_ew[1],(cmath_polar(phi)[1]/(2*pi))%1,r=r_ref)
            r_max=r_rigid_max+dr/2+abs(dr)*(0.5+1/(mesh_compression-1))
            r_min=r_rigid_min+dr/2-abs(dr)*(0.5+1/(mesh_compression-1))
            if (r>r_max) or (r<r_min): 
                return p_z_ew#return early if point is outside the affected zone
        if r_rigid_min < r <r_rigid_max: #just shift the point if it is in the rigid zone
            p_z_ew[0]+=dr*phi
            return p_z_ew
        if r>r_ref:#scale the amout of shift down to zero towards r_max
            if (r_max-r_rigid_max)!=0.0: 
              x=(r_max-r)/(r_max-r_rigid_max)
              p_z_ew[0]=p_center+(r_max - x*(r_max - (dr+r_rigid_max)))*phi
            return p_z_ew
        else: #(r<=r_ref) scale the amount of shift down to zero towards r_min
            if (r_rigid_min-r_min)!=0.0: 
              x=(r-r_min)/(r_rigid_min-r_min)
              p_z_ew[0]=p_center+(r_min + x*((dr+r_rigid_min)-r_min))*phi
            return p_z_ew
    return calibrate

    
def rotor(*,center=0+0j,angle=None,phase=None,fphase=None,**kwargs):
    if fphase != None:
        def rotate(pz):
           pz[0]=center+(pz[0]-center)*fphase(pz[1],pz)
           return pz
    else: 
        if angle!=None:
            phase=1j**(angle*2/pi)#same as cmath.exp(1j*angle), but without cmath
        if phase == None:
            raise Exception("Argunent error in call to 'rotor': one of the arguments {phase|angle|fphase} is required") 
        def rotate(pz):
            pz[0]=center+(pz[0]-center)*phase
            return pz
    return rotate
    
def point_shiftor(*,p0,tol,dphi=1.0+0.0j,dang=None,dr=0.0,fblend=None,**kwargs):
    from math import pi
    if dang!=None:
        dphi=1j**(dang*2/pi)#same as cmath.exp(1j*angle), but without cmath
    if fblend != None:
        if dr!=0.0:
            def shift_point(pz):
               if abs(pz[0]-p0)>tol: return pz
               r0=abs(pz[0])
               x=fblend(pz[1])
               pz[0]=p0*dphi**x*(1+dr*x/r0)
               return pz
        else:
            def shift_point(pz):
               if abs(pz[0]-p0)>tol: return pz
               x=fblend(pz[1])
               pz[0]=p0*dphi**x
               return pz
    else:
        if dr!=0.0:
            def shift_point(pz):
               if abs(pz[0]-p0)>tol: return pz
               r0=abs(pz[0])
               pz[0]=p0*dphi*(1+dr/r0)
               return pz
        else:
            def shift_point(pz):
               if abs(pz[0]-p0)>tol: return pz
               pz[0]=p0*dphi
               return pz
                
    return shift_point
    

#groove toolpath
from math import cos,pi
def alpha_blend(x,xstart, xend,f0,f1):
    alpha=0.5+0.5*cos(max(0.0,min(1,(x-xstart)/(xend-xstart)))*pi)
    return [alpha*y0+(1.0-alpha)*y1 for y0,y1 in zip(f0(x),f1(x))]
    
def groove_depth_pattern_factory(*,delta_phi_ramp_start, delta_phi_chamfer_transition, phi_center,    
                                delta_phi_ramp,delta_phi_helix,
                                r_chamfer, z_bottom, dz_chamfer, r_circ, r_cable_ramp, z_top, r_cable, 
                                z_helix_start, groove_pitch, phi_helix_start, h_rim, groove_flank_angle,
                                R_rim,env=None,**_):
    from math import sin,cos,tan,pi
    deg=pi/180
    phi_0=delta_phi_ramp_start-delta_phi_chamfer_transition-phi_center
    phi_1=phi_0+delta_phi_chamfer_transition
    phi_2=phi_1+delta_phi_ramp
    phi_3=phi_2+delta_phi_helix
    phi_4=phi_3+delta_phi_ramp
    phi_5=phi_4+delta_phi_chamfer_transition
    #tool paths:
    #variable input parameters
    def groove_toolpath(phi):
        def bottom_chamfer(phi):  return [ r_chamfer,         z_bottom-dz_chamfer ]
        def bottom_cable(phi):    return [ r_cable_ramp,  z_bottom-r_cable ]
        def helix(phi):           return [ r_circ,            (phi-phi_2)/(2*pi)*groove_pitch+h_rim+r_cable ]
        def top_cable(phi):       return [ r_cable_ramp,  z_top+r_cable ]
        def top_chamfer(phi):     return [ r_chamfer,         z_top+dz_chamfer ]
    
        if    phi<phi_0              : return  bottom_chamfer(phi)
        elif (phi>=phi_0)&(phi<phi_1): return  alpha_blend(phi,phi_0,phi_1,bottom_chamfer,bottom_cable)
        elif (phi>=phi_1)&(phi<phi_2): return  alpha_blend(phi,phi_1,phi_2,bottom_cable,helix)
        elif (phi>=phi_2)&(phi<phi_3): return  helix(phi)
        elif (phi>=phi_3)&(phi<phi_4): return  alpha_blend(phi,phi_3,phi_4,helix,top_cable)
        elif (phi>=phi_4)&(phi<phi_5): return  alpha_blend(phi,phi_4,phi_5,top_cable,top_chamfer)
        elif  phi>=phi_5             : return  top_chamfer(phi)
        else: raise(Exception('This line should never be reached.'))
            
    def groove_tool(dz,r=0.45,a=30*deg):
        flank=abs(dz)>r*cos(a)
        if flank:
          result=abs(dz)/tan(a)-r/sin(a)
        else:
          result=-(r**2 - dz**2)**0.5
        return result
    
    def phi_groove(z):
        return (z-z_helix_start)/groove_pitch*(2*pi)+phi_helix_start
    
    def thread_depth_pattern(z,phi,z0=0.0):
        i_groove=(phi_groove(z)-pi)//(2*pi)
        phi_tool_1=(phi)%(2*pi)+i_groove*(2*pi)
        r_tool_1,z_tool_1=groove_toolpath(phi_tool_1)
        dz_1=z_tool_1-z
        if abs(dz_1)<=(groove_pitch/2):
            return r_tool_1+groove_tool(dz=dz_1,r=r_cable,a=groove_flank_angle)
        phi_tool_2=phi_tool_1+2*pi
        r_tool_2,z_tool_2=groove_toolpath(phi_tool_2)
        dz_2=z_tool_2-z
        if abs(dz_2)<=(groove_pitch/2):
            return r_tool_2+groove_tool(dz=dz_2,r=r_cable,a=groove_flank_angle)
        while dz_1>0:
            phi_tool_2,r_tool_2,z_tool_2,dz_2=phi_tool_1,r_tool_1,z_tool_1,dz_1
            phi_tool_1=phi_tool_1-2*pi
            r_tool_1,z_tool_1=groove_toolpath(phi_tool_1)
            dz_1=z_tool_1-z
        while dz_2<0:
            phi_tool_1,r_tool_1,z_tool_1,dz_1=phi_tool_2,r_tool_2,z_tool_2,dz_2
            phi_tool_2=phi_tool_2+2*pi
            r_tool_2,z_tool_2=groove_toolpath(phi_tool_2)
            dz_2=z_tool_2-z
        r_2=r_tool_2+groove_tool(dz=dz_2,r=r_cable,a=groove_flank_angle)
        r_1=r_tool_1+groove_tool(dz=dz_1,r=r_cable,a=groove_flank_angle)
        return min(r_1,r_2,R_rim)
    if env!=None:
        env.update({key:value for key,value in locals().items() if not key in ['env','args','kwargs']})
    return thread_depth_pattern


# ### cpastan()

# In[17]:


capstan_parameters=dict(n_spokes=13, n_strands=5,
                phi_rim=0.160, r_fillet_rim=0.060, phi_hub=0.10, r_fillet_hub=0.160,
                ew_rim=1.0,ew_fillet_rim=0.8,ew_spokes=0.7,ew_fillet_hub=0.5,ew_hub=0.5,
                spoke_midpoint=0.38,mesh_twist_pitch = -60,
                l_turn= 60.0, l_tot= 600.0, d_cable=0.9, groove_pitch=1.25, left_handed=False, n_cable_tunnels=2,
                tunnel_pos=0.5,
                hub_squeezeout_factor=2.,shaft_type='D', d_shaft=5.0,D_key=0.5, shaft_tolerance=0.0, countersink_chamfer=0.75,
                z_=0.4,
                n_skirt=3,skirt_offset=1.0,hl=0.2,hl_start=0.05,
                #print_parameters
                design_name = 'Capstan',
                nozzle_temp = 220.0, bed_temp = 120.0,
                nominal_print_speed = 10.0*60.0,#10*60 #print slow to give the layer time to cool
                max_print_speed = 15*60,#=speed for ew=0.5mm 
                nominal_ew = 0.75,   # extrusion width
                fan_percent = 0.0,
                #  nominal_eh = 0.2,    # extrusion/layer heigth
                printer_name='generic', # generic / ultimaker2plus / prusa_i3 / ender_3 / cr_10 / bambulab_x1 / toolchanger_T0
                )


def capstan(n_spokes=13, n_strands=5,
                  phi_rim=0.160, r_fillet_rim=0.060, phi_hub=0.160, r_fillet_hub=0.060,
                  ew_rim=1.0,ew_fillet_rim=0.8,ew_spokes=0.7,ew_fillet_hub=0.5,ew_hub=0.5,
                  spoke_midpoint=0.38,mesh_twist_pitch = -60.0,
                  l_turn= 60.0, l_tot= 600.0, d_cable=0.9, groove_pitch=1.25, left_handed=False, n_cable_tunnels=2,
                  tunnel_pos=0.5,
                  hub_squeezeout_factor=2,shaft_type='D', d_shaft=5.0,D_key=0.5, shaft_tolerance=0.0, countersink_chamfer=0.75,
                  z_=0.4,
                  n_skirt=3,skirt_offset=1.0,hl=0.2,hl_start=0.05,
           env=None,**kwargs):
  import math
  import cmath
  from math import pi
  deg=pi/180.0               
      #calculate dependent parameters
  r_cable=d_cable/2
  r_circ=(l_turn**2-groove_pitch**2)**0.5/(2*pi)
  r_shaft=d_shaft/2
  h_rim=2.0*d_cable
  R_rim=r_circ+r_cable
  r_cable_ramp=r_circ-d_cable-ew_rim
  phi_offset_channel2=0 if n_cable_tunnels!=2 else (n_spokes//2)/n_spokes*2*pi
  dz_chamfer=1.75*d_cable#vertical tool position above/below top/bottom
  r_chamfer=r_cable_ramp#horizontal tool position
  groove_flank_angle=30*deg
  delta_phi_ramp_start=1.5*(2*pi)/n_spokes #offset relative to return channel center
  delta_phi_ramp=pi/2 #
  delta_phi_chamfer_transition=pi/16
  dz_ends=2*(h_rim+r_cable)
  phi_ends=2*(delta_phi_ramp_start+delta_phi_ramp)+phi_offset_channel2
  delta_phi_helix_=(l_tot/l_turn)*2*pi#preliminary
  n_rot=(dz_ends*(2*pi)+ delta_phi_helix_*groove_pitch - mesh_twist_pitch*(phi_ends + delta_phi_helix_))/(-mesh_twist_pitch*(2*pi))
  n_rot=int(n_rot+1)
  delta_phi_helix=(-dz_ends*(2*pi) - n_rot*mesh_twist_pitch*2*pi + phi_ends*mesh_twist_pitch)/(groove_pitch -mesh_twist_pitch)
  z_bottom=0.0
  z_top=z_bottom+delta_phi_helix/(2*pi)*groove_pitch+dz_ends
  z_helix_start=z_bottom+h_rim+r_cable
  phi_helix_start=delta_phi_ramp_start+delta_phi_ramp
  phi_center=0.5*2*pi/n_spokes
#  phi_width=2*pi/n_spokes
#  max_phase_advance=0.7*2*pi/n_spokes
    
  phi_tot=2*pi*n_strands
  phi_spoke2=phi_tot/(2*n_spokes)
    
  R_hub=r_shaft
  l1,r1,l2,r2=phi_rim*phi_spoke2*R_rim,r_fillet_rim*phi_spoke2*R_rim,phi_hub*phi_spoke2*R_hub,r_fillet_hub*phi_spoke2*R_hub
  c1=(0-1j*(R_rim-r1))*cmath.exp(1j*phi_rim*phi_spoke2)
  c2=(0-1j*(R_hub+r2))*cmath.exp(1j*((1-phi_hub)*phi_spoke2))
  t1,t2=calcTangent(c1,r1,c2,r2)
  ltan,phitan=cmath.polar(t2-t1)
  phitan%=2*pi #counter-clockwise 0-360deg
  arcs=[(l1,phi_rim*phi_spoke2),(r1*(phitan-phi_rim*phi_spoke2),phitan-phi_rim*phi_spoke2),(ltan*(1-spoke_midpoint),0),(ltan*spoke_midpoint,0),(r2*(phitan-((1-phi_hub)*phi_spoke2)),-phitan+((1-phi_hub)*phi_spoke2)),(l2,phi_hub*phi_spoke2)]
  l_layer=sum(l for l,*_ in arcs)*2*n_spokes #extrusion path length for one complete layer (used to calculate z-coordinate)
  arcs=(arcs+arcs[-1::-1])# add mirrored arc sequence
  arc_ew=[ew_rim,ew_fillet_rim,ew_spokes,0.5*ew_spokes+0.5*ew_fillet_hub,ew_fillet_hub,ew_hub]#extrusion widths for rim...hub arc segments
  arc_ew=arc_ew+arc_ew[-1::-1]
  p_spokes_mid=list(Segments2Complex(arcs[:3],p0=R_rim+0.j,a0=0+1j,tol=0.01))[-1][0]
  r_spokes_mid=abs(p_spokes_mid)
  R_tunnel=R_hub+tunnel_pos*(R_rim-R_hub)
  r_lead_in=h_rim+d_cable
  outline=[(R_rim*2*pi,2*pi),]
  p0o=R_rim+0.0j
  n0o=0.0+1.0j
  if shaft_type.upper()=='O':
    DshaftOutline=[(r_shaft*2*pi,2*pi)]#'plain' shaft outline is a circle
  else:
    Dkeycp = (r_shaft**2-(r_shaft-D_key)**2)**0.5 + 1j*(r_shaft-D_key)#corner point of D-shaft (x+ iy)
    Dkeyang=cmath.polar(Dkeycp)[1]  # angle up to the corner point
    DshaftOutline=[(r_shaft*Dkeyang,Dkeyang),(0,pi/2-Dkeyang),(Dkeycp.real,0)]#1/4 of D-shaft outline
    DshaftOutline=DshaftOutline+DshaftOutline[-1::-1]#add mirror image -> upper half of D-shaft outlone
    DshaftOutline+=DshaftOutline if shaft_type.upper()=='DD' else [(r_shaft*pi,pi)] #add lower half of D-shaft outline
  inline_offset=0.5*ew_hub*hub_squeezeout_factor+shaft_tolerance/2
  inline=[(l+a*inline_offset,a) for l,a in DshaftOutline]
  p0i=R_hub+inline_offset+0.0j
  n0i=0.0+1.0j
#1. generate the points of the raw annular mesh:
  blank_points=lambda:Segments2Complex(arcs,p0=R_rim+0.j,a0=0+1j,tol=0.003,return_start=True,loops=n_spokes if z_!=None else math.inf)
  thread_depth_pattern=groove_depth_pattern_factory(delta_phi_ramp_start=delta_phi_ramp_start, delta_phi_chamfer_transition=delta_phi_chamfer_transition, phi_center=phi_center, delta_phi_ramp=delta_phi_ramp, delta_phi_helix=delta_phi_helix, r_chamfer=r_chamfer, z_bottom=z_bottom, dz_chamfer=dz_chamfer, r_circ=r_circ, r_cable_ramp=r_cable_ramp, z_top=z_top, r_cable=r_cable, z_helix_start=z_helix_start, groove_pitch=groove_pitch, phi_helix_start=phi_helix_start, h_rim=h_rim, groove_flank_angle=groove_flank_angle, R_rim=R_rim)
  transformations=[
      #2a. shift spokes midpoint radially to make room for cable tunnel
            calibrator(r_ref=r_spokes_mid,dr_offset=R_tunnel-r_spokes_mid),
      #2b. shift 1 spoke mid point to round over the cable tunnel in/outlet  
           point_shiftor(p0=R_tunnel,tol=(R_rim-R_hub)/10,dang=0.6*2*pi/n_spokes,dr=0.4*(R_rim-R_tunnel),
                fblend=lambda z:(1.0-(r_lead_in**2-min(max(r_lead_in-(z-z_bottom),0.0),r_lead_in)**2)**0.5/r_lead_in),),
      #2c. shift 1 spoke mid point to round over the cable tunnel in/outlet  
           point_shiftor(p0=R_tunnel*cmath.exp(1j*(-2*phi_center-phi_offset_channel2)),tol=(R_rim-R_hub)/10,dang=-0.6*2*pi/n_spokes,dr=0.4*(R_rim-R_tunnel),
                fblend=lambda z:(1.0-(r_lead_in**2-min(max(r_lead_in-(z_top-z),0.0),r_lead_in)**2)**0.5/r_lead_in),),
      #3. counterssink
           calibrator(r_ref=R_hub,f_offset=lambda z,*_,**__:max(0,countersink_chamfer-(z-z_bottom),countersink_chamfer-1.0*(z_top-z)),ew_factor=0.0),
      #4. rotate the mesh (helical spokes):
           rotor(fphase=lambda z,*_:1j**(z/mesh_twist_pitch*4)),
      #5,6. deform the annular mesh to fit between 'inline' (shaft) and 'outline' (cable groove, and top/bottom chamfer):
           mesh_transformer(R_rim=R_rim,R_hub=R_hub, 
                                  outline=outline,p0o=p0o,n0o=n0o,
                                  foutline_offset=(lambda z,L:R_rim-thread_depth_pattern(z,L/R_rim)+ew_rim/2),#lambda z,*_,**__:0.0,#max(0,w_chamfer-z,w_chamfer-(h-z)),
                                  inline=inline,p0i=p0i,n0i=n0i,),
                 ]   
  def meshpoints():
        point_data=NamedList([None]*4)
        point_data.alias('p','z','ew','a')
        for p,a,l,X in blank_points():
           # calculate the z-coordinate based on the total extrusion length, re-arrange the variables:
            z=z_ if z_!=None else hl*l/l_layer+hl_start
            if z>(z_top+hl):
                return
            point_data[:]=p,z,arc_ew[X],a
            
           # apply all transformations
            for f in transformations:
                point_data=f(point_data)
                
           # convert the complex 2D coordinate to real x, y coordinates, calculate eh, return (x,y,z,eh,ew):
            p,z,ew,a=point_data
            x=p.real
            y=p.imag
            if left_handed: y*=-1
            z=min(z,z_top)
            eh=min(z if z<(hl+hl_start) else hl, z_top-(z-hl))
            yield (x, y, z, eh, ew)
            
  def skirt_and_meshpoints():
        skirt=((p[0].real,p[0].imag,hl,hl,0.6) for offs in range(n_skirt) for p in Segments2Complex(outline,p0=R_rim+0.0j,a0=0+1j,tol=0.005,offs=0.5*offs+skirt_offset,return_start=True) )
        for x,y,z,eh,ew in skirt:#skip the first few points so that the start point of the skirt is not near the start point of the print.
            if y>R_rim/4:
                break
        yield from skirt
        yield R_rim,0,hl,0.0,0.0 #move to start of print
        yield from meshpoints()
        if z_==None:
            yield 0.0,0.0,max(z_top+10,30),0.0,0.0 #move print head go to parking position if not layer preview
  capstan_point_factory=skirt_and_meshpoints if  ((z_==None) and(n_skirt>0)) or ((z_<=hl) and (n_skirt>0)) else meshpoints
  if env!=None:
        env.update({key:value for key,value in locals().items() if not key in ['env','args','kwargs']})
  return capstan_point_factory



#
def main():
  from time import time_ns
  import gc
  time_ms=lambda:time_ns()//1000000
  t0=time_ms()
  my_capstan=capstan(**(capstan_parameters|dict(z_=None))) 
  i=0
  print('Starting...')
  for p in my_capstan():
    if i%1000==0:
      print(f'{i=},' )#{gc.mem_free()=}')
    i+=1
  t1=time_ms()
  print(f'Number of points:{i}, time:{(t1-t0)/1000.0=}s')
      
if __name__=='__main__':
  main()


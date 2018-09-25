from functools import reduce
from operator import __or__
def CountBits(n):
  n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
  n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
  n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
  n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
  n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
  n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
  return n

hex2segnames=['abcdef','bc','abged','abcdg','bcgf','afgcd','acdefg','abc',
            'abcdefg','abcfg','abcefg','cdefg','defa','bcdeg','adefg','aefg']
def segmentsFromByte(value,segmentorder='abcdefgp'):
    return  [c for i,c in enumerate(segmentorder) if value & (1<<i)]

def byteFromSegments(value,segmentorder='abcdefgp'):
    return  reduce(__or__,[0,0]+[1<<(segmentorder.find(c)) for c in value])
    
transitions=[((9,1),'fag'),((8,0),'g'),((7,3),'g'),((6,2),'bf'),((5,1),'bgfa'),((4,0),'age'),((3,1),'ga'),((2,0),'fg'),((1,0),'bafbe')]

d={byteFromSegments(hex2segnames[0],segmentorder='abefgcdp')&31:'0'} 
for (i,j),t in transitions:
  start=byteFromSegments(hex2segnames[j],segmentorder='abefgcdp')&31
  x=start
  for k,s in enumerate(t):
    x^=byteFromSegments(s,segmentorder='abefgcdp')
    d[x]='{:d}{:s}'.format(i,chr(k+97) if k<(len(t)-1) else '')
  end=byteFromSegments(hex2segnames[i],segmentorder='abefgcdp')&31
#  print(x,end)
  assert(x==end)
  
for h7 in ('abc','abcf'):
  for h9 in('abcfg','abcdfg'):      
#    for hc in ('defa','deg'):
      hc='defa'
      hex2segnames[7],hex2segnames[9],hex2segnames[0xc]=h7,h9,hc
      p={i:byteFromSegments(hex2segnames[i],segmentorder='abefgcdp') for i in range(10)}
      p1=[{v&i:k for k,v in p.items()} for i in range(128)]
      p2=[i for i,x in enumerate(p1) if len(x)==10 and CountBits(i)==5]
      print (p2)
      p3=[[CountBits((p[i]^p[j])&k) for (i,j),x in transitions] for k in p2]
      p4=[[len(x) for (i,j),x in transitions] for k in p2]
      print (p3)
      print (p4)
      print([sum(x) for x in p3])
print (d)
d1={''.join(segmentsFromByte(k,segmentorder='abefgcdp')):v for k,v in d.items()}
print (d1 )
      

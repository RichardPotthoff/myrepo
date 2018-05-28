# Sudoku7.py
from __future__ import print_function
from __future__ import absolute_import
from six.moves import range
#True=1
#False=0
class group:
 def __init__(self,id):
  self.id=id
  self.cells=[]
 def findSingles(self):#This function returns a directory of Cell:Value pairs for all values that have only one possible cell left in this group. The cell may still have other possible candidates.
  res={}
  for i in range(9):
   n=0
   id=0
   for cell in self.cells:
    if cell.cands[i]:
     id=cell.id
     n=n+1
   if n==1:
    res[id]=i+1
  return res
class cell:
 def __init__(self,id):
  self.id=id
  self.groups=[]
  self.cands=[True]*9
  self.V=0
 def set(self,value):#This function sets the value of a cell, but only if "value" is still in the "cands" list. Then clears all remaining candidates from the list in the cell, and "value" from all cells in all groups to which this cell belongs.
  i1=value-1
  res=True
  if (self.cands[i1]) & (self.V==0):
   self.V=value
   for j in range(9):
    self.cands[j]=False
   for group in self.groups:#loop through all groups (e.g row, column, subsquare)
    for cell in group.cells:#loop through all cells of each group
     cell.cands[i1]=False #clear the flag for "value"
  else:
   res=False
  return res
 def candList(self):
  res=[]
  for i in range(9):
   if self.cands[i]:
    res.append(i+1)
  return res
 def CalculateCellValue(self):#Returns the value of the cell if there is only one candidate left, or zero otherwise 
  n=0
  for i in range(9):
   if self.cands[i]:
    n=n+1
    val=i+1
  if n==1:
   return val
  else:
   return 0
class sudoku:
 ll=[[]]*(3*9+4)
 for i in range(len(ll)):ll[i]=[0]*9
 for j in range(9):
  for i in range(9):
   ll[i][j]=9*i+j
   ll[i+9][j]=i+9*j
   ll[i+18][j]=i//3*27+i%3*3+j//3*9+j%3
 def link(self,c,g):
  c.groups=c.groups+[g]
  g.cells=g.cells+[c]
 def __init__(self,L={},mode=""):
  self.Windoku=mode.lower()=="windoku"
  self.Extreme=mode.lower()=="extreme"
  ng=27
  if self.Windoku:
   ng=ng+4
   for j in range(9):
    i=0 
    for k in(10,14,46,50):
     sudoku.ll[i+27][j]=k+j//3*9+j%3
     i=i+1
  elif self.Extreme:
   ng=ng+2
   for j in range(9):
    sudoku.ll[27][j]=j*10
    sudoku.ll[28][j]=8+j*8
  else:
   pass  
  self.ng=ng
  self.cols=[None]*9
  self.rows=[None]*9
  self.blocks=[None]*9
  self.cells=[None]*81
  self.groups=[None]*self.ng
  for i in range(81):
   self.cells[i]=cell(i)
  for i in range(ng):
   self.groups[i]=group(i)
   for j in range(9):
    self.link(self.cells[sudoku.ll[i][j]],self.groups[i])
  self.set(L)
 def clear(self):
  for c in self.cells:
   c.V=0
   for i in range(9):
    c.cands[i]=True
 def findCellSingles(self):
  res={}
  for cell in self.cells:
   val=cell.CalculateCellValue()
   if val!=0:
    res[cell.id]=val
  return res
 def findGroupSingles(self):
  res={}
  for group in self.groups:
   res.update(group.findSingles())
  return res
 def set(self,list={}):
  res=True
  for id in list.keys():
   res=self.cells[id].set(list[id])
   if not res:
    break
  return res
 def solved(self):
  for c in self.cells:
   if c.V==0:
    return False
  return True 
 def solve(self,solvelevel=0):
  res=False
  while True:
   cellList=self.findCellSingles()
   if not self.set(cellList):
    return False
   groupList=self.findGroupSingles()
   if not self.set(groupList):
    return False
   if (len(cellList)+len(groupList)==0):break
  if self.solved():
   return True
  else:
   cl=self.candList()
   if len(cl)==0:
    res=False
   else:
    cands=cl[0]
    sL=self.asList()
    for cand in cands[2]:
     trycand={cands[1]:cand}
     print(trycand)
     sLt={}
     sLt.update(sL)
     sLt.update(trycand)
     self.clear()
     self.set(sLt)
     res=self.solve()
     if res!=False:break
  return res  
 def asList(self):
  res={}
  for cell in self.cells:
   if cell.V!=0:
    res.update({cell.id:cell.V})
  return res
 def candList(self):
  res=[]
  for c in self.cells:
   cl=c.candList()
   l=len(cl)
   bCC=[]
   if l>0:
    for group in c.groups:
     n=0
     for gc in group.cells:
      if gc.V==0:
       n=n+1
     bCC.append(n)
    bCC.sort()
    bCC.insert(0,l)
    res.append([bCC,c.id,cl])        
  res.sort()  
  return res  
 def show(self):
  if self.Extreme:
   s="""
 +-------+-------+-------+
 |[.]. . | . . . | . .[.]|
 | .[.]. | . . . | .[.]. |
 | . .[.]| . . . |[.]. . |
 +-------+-------+-------+
 | . . . |[.].[.]| . . . |
 | . . . | .[.]. | . . . |
 | . . . |[.].[.]| . . . |
 +-------+-------+-------+
 | . .[.]| . . . |[.]. . |
 | .[.]. | . . . | .[.]. |
 |[.]. . | . . . | . .[.]|
 +-------+-------+-------+
"""
  elif self.Windoku:
   s="""
 +-------+-------+-------+
 | . . . | . . . | . . . |
 |  +----+--+ +--+----+  |
 | .|. . | .|.|. | . .|. |
 |  |    |  | |  |    |  |
 | .|. . | .|.|. | . .|. |
 +--+----+--+-+--+----+--+
 | .|. . | .|.|. | . .|. |
 |  +----+--+ +--+----+  |
 | . . . | . . . | . . . |
 |  +----+--+ +--+----+  |
 | .|. . | .|.|. | . .|. |
 +--+----+--+-+--+----+--+
 | .|. . | .|.|. | . .|. |
 |  |    |  | |  |    |  |
 | .|. . | .|.|. | . .|. |
 |  +----+--+ +--+----+  |
 | . . . | . . . | . . . |
 +-------+-------+-------+
"""
  else:
   s="""
 +-------+-------+-------+
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 +-------+-------+-------+
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 +-------+-------+-------+
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 | . . . | . . . | . . . |
 +-------+-------+-------+
"""

  i=0
  s1=''
  for c in s:
   if c=='.':
    V=self.cells[i].V
    if V!=0:
     s1=s1+str(V)
    else:
     s1=s1+c
    i=i+1
   else:
    s1=s1+c  
  print(s1)
def str2list(s="",blank=".0_xX"):
 i=0
 res={}
 for c in s:
  if c in "123456789":
   res.update({i:ord(c)-ord("0")})
   i=i+1
  else:
   if c in blank:
    i=i+1
 return res
def mat2list(M=[[]]):
 res={}
 for id in range(81):
  row,col=divmod(id,9)
  val=M[row][col]
  if val!=0:
   res.update({id:val})
 return res   
ts49="""
009000105
050009726
200000004
000102500
090360000
702005000
000800200
005030681
800050000
"""
HT0="""
.........
..3..7.2.
4..2..9.3
.5.4.3...
...6....2
83..2....
.....18..
.6.....97
..5..8...
"""
#Daily Windoku
Windoku=[
"""009020000281000000000500000060010008000000000000056700000000010000295000000060400""",
"""401027000000008100000000040003000024004000003000500000002081005090000000000000001""",
"""000000000009060800530070012050000030000000000040000080410030097003090400000000000""",
"""004010070060004001800500000003000080500000009040000200000006003600700010010020500""",
"""090510023020400005003000000000000002006000019000000008005000000060100007080250046""",
"""000075000070000030008304500602000700800000009001000806003901600060000070000560000""",
"""000000200500000000006004318000000006000006000000000004003002857800000000000000900""",
"""000000000037109850900000003009000200000070000000000000040000090028010560000000000""",
"""005001030607000002000000600000004000400308005000500000001000000700000501060100400""",
"""006870050001004000079000000300010000000000000000030002000000590000100400040089600""",
"""000000080000109000006002040100000000004000300000000008050800700000206000090000000""",
"""800500000953000010000000008600002400000000000004600007400000000020000953000005001""",
"""405030800000000703000001090070008001000000000300900070030100000208000000007080209""",
"""000000020006007409000060010001000030050000100700000000070001040048090000000700000""",
"""000800000000093650000000000600000000020450070007006005000000000019002004000900000""",
"""000000000000900004003076009008000070000080003002000040006012008000500007000000000""",
"""008006100009800000170000080050000000000007050700049000200000030004030605000000020""",
"""000000000070412060000030000050000010019060280080000040000050000090278030000000000""",
"""000400020000001307000750060406000050001000900070000206040017000709600000080005000""",
"""000000000900060007400508002010000070008103200600000008070000080000070000000000000""",
"""030000085520000004000000600000015000000207000000690000003000000700000091640000030""",
"""
..8....3.
......2.7
.5.9...8.
.1.4...7.
.........
..6...52.
....6.31.
.841...9.
........5
"""
]
sux="""
640050007
705040016
002736000
200100400
800000165
010460000
906004031
070090600
020000509
"""
sux="""
950713068
430000017
000000000
500090001
800371009
200040003
000000000
390000054
120534096
"""
sux="""
950713068
430000017
000000000
500090001
800371009
200040003
000000000
390000054
120534096
"""
su17="""
000039065
900602000
306100420
005093076
700000001
640780200
024005307
000304002
160270000
"""
su=sudoku(str2list("""
500006001
010002705
030150802
004070083
080020070
370010400
903047010
806500030
700800004
"""),"Extreme")
su=sudoku(str2list(Windoku[-1]),"Windoku")
su.show()
su.solve()
su.show()
#print(sudoku.ll[27])
#print(sudoku.ll[28])
#print(su.ng)



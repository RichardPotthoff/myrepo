class pegboard():
  def __init__(self,n):
    self.board_=[[True for j in range(i)]for i in range(1,n+1)]
  @property
  def board(self):
    return self.board_
  def drop_mable(self):
    i=0
    for row in self.board_:
      row[i]= not row[i]
      i+=0 if row[i] else 1
    return i
      
pb=pegboard(7)
print(pb.board)
print(sorted([pb.drop_mable()for i in range(128)]))


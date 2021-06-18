import queue
import collections
import sys 
import canvas

maxint=2**sys.int_info.bits_per_digit
class Observable:
    def __init__(self):
        self._observers = []
    
    def register_observer(self, observer):
        self._observers.append(observer)
    
    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)

class Observer:
    def __init__(self, observable):
        observable.register_observer(self)
    
    def notify(self, observable, *args, **kwargs):
        print(self,'Got', args, kwargs, 'From', observable)
        
class outputNode(Observable):
  queue=collections.deque()
  def process_queue():
    while outputNode.queue:
      outputNode.queue.pop()()
  def __init__(self,*args,**kwargs):
    self.queued=False
    super().__init__(*args,**kwargs)
  def notify_observers(self, *args, **kwargs):
    self.args=args
    self.kwargs=kwargs
    if not self.queued:
      def task():
        self.queued=False
        for observer in self._observers:
            observer.notify(self, *self.args, **self.kwargs)
      outputNode.queue.append(task)
      self.queued=True
    
  
class inputNode(Observer):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
  def notify(self, observable, *args, **kwargs):
        print(self,'Got', args, kwargs, 'From', observable)
        observable.notify_observers(args[0]+1)
        
if False:      
  subject = outputNode()
  observer = inputNode(subject)
  observer2 = inputNode(subject)
  subject.notify_observers(1)
  subject.notify_observers(100)
  while True:
    print()
    myqueue=outputNode.queue
    outputNode.queue=collections.deque()
    for action in myqueue:action()

class component:
  def __init__(self):
  
    return

class port:
  def __init__(self):
    self.parent=None
    return
  def on_input_change(self):
    
    return
  
class cell:
  def __init__(self,board=None,col=None,row=None):
    self._alive=False
    self._neighbours=0
    self.board=board
    self.row=row
    self.col=col
    self.input_changed=False
    self.state_changed=False
    self.output_changed=False
    return
  def __lt__(self,other):
    return True
  @property
  def alive(self):
    return self._alive
  @alive.setter
  def alive(self,value):
    if self._alive!=value:
      self._alive=value
      if not self.state_changed:
         self.board.stateQueue.put(self)
         self.state_changed=True
    return
  @property
  def neighbours(self):
    return self._neighbours
  @neighbours.setter
  def neighbours(self,value):
    if value!=self._neighbours:
      self._neighbours=value
      if not(self.input_changed):
        self.input_changed=True
        self.board.inputQueue.put(self)
         
class board:
  def __init__(self,ncols=20,nrows=20):
    self.t=0
    self.nrows=nrows
    self.ncols=ncols
    self.cells=[[cell(self,i,j) for i in range(ncols)] for j in range(nrows)]
    self.inputQueue=queue.Queue()
    self.stateQueue=queue.Queue()
    self.outputQueue=queue.Queue()
    return
  def print(self):
    for row in self.cells:
      print(' '.join([f'x{c.neighbours:d}' if c.alive else f' {c.neighbours:d}' if c.neighbours else '  'for c in row]))
#      print('+-'.join(['-' for c in row]))
    return
  def show(self):
    canvas.begin_updates()
    for i,row in enumerate(self.cells):
      for j,c in enumerate(row):
        canvas.set_fill_color(*((0,0,0)if c.alive else (1.0,1.0,1.0)))
        canvas.fill_rect(j*10,i*10,10,10)
    canvas.end_updates()
    return

  def set_cells(self,coords,offset=[10,10]):
    for c,r in coords:
       self.cells[r+offset[1]][c+offset[0]].alive=True
  def step(self):
    while not self.stateQueue.empty():
      cell=self.stateQueue.get()
      for i,j in ([[i,j]for i in(-1,0,1) for j in (-1,0,1)]):
        self.cells[(j+cell.row)%self.nrows][(i+cell.col)%self.ncols].neighbours+=1
  
acorn=[[-3,-1],[-2,1],[-2,-1],[0,0],[1,-1],[2,-1],[3,-1]]  
b=board(40,20)
b.set_cells(acorn)
b.print()
b.step()
b.print()
canvas.set_size(400,200)
b.show()

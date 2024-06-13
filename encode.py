def encode(s):
  from random import randint
  alphanum='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ123456789'
  global c1,c2
  code1=[None]*len(s)
  code2=[None]*len(s)
  for i,c in enumerate(s):
    ic=ord(c)
    if ic>=127:
      raise Exception(f"Non-ASCII character '\\x{ic:2x}' encountered at position {i}!")
    while True:
      c2=alphanum[randint(0,len(alphanum)-1) ]
      jc=ord(c2)
      ijc=ic^jc
      if ijc!=127:
        c1=chr(ijc)
        if c1 in alphanum:
          break
    code1[i],code2[i]=c1,c2
  return ''.join(code1)+alphanum[randint(0,len(alphanum)-1)]+''.join(code2)
  
def decode(s):
  return''.join(chr(ord(a)^ord(b)) for a,b in zip(s[:len(s)//2],s[len(s)//2+1:]))

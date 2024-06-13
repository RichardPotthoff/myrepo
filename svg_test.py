#!/usr/bin/env python
# coding: utf-8

# In[3]:


from xml.dom import minidom
from svg.path import parse_path

doc = minidom.parse('test.svg')

for ipath, path in enumerate(doc.getElementsByTagName('path')):
    global parsed
    global d
    print('Path', ipath)
    d = path.getAttribute('d')
    parsed = parse_path(d)
    print('Objects:\n', parsed, '\n' + '-' * 20)
    for obj in parsed:
        print(type(obj).__name__, ', start/end coords:', ((round(obj.start.real, 3), round(obj.start.imag, 3)), (round(obj.end.real, 3), round(obj.end.imag, 3))))
    print('-' * 20)
doc.unlink()


# In[5]:





# In[ ]:





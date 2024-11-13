import markdown
from urllib.parse import urlparse, urlunparse
from markdown.extensions.codehilite import CodeHiliteExtension
from mdx_gfm import GithubFlavoredMarkdownExtension
from pygments.formatters import HtmlFormatter
formatter=HtmlFormatter(cssclass='highlight',style='default')
css=formatter.get_style_defs()

import yaml
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler
import socketserver
import io
import os
import sys
import shutil
from urllib.parse import unquote    
def html_page_start(title='PageTitle',style=''):
  result=('<DOCTYPE html>'
          '<html lang="en">'
            '<head>'
              '<meta charset="UTF-8">'
              '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
              '<title>'+title+'</title>'
              '<style>'+style+'</style>'
            '</head>'
            '<body>')
  return result.encode()
def html_page_end():
  result=(  '</body>'
          '</html>'
          )
  return result.encode()
def SitePicker(title='PageTitle',style='',sites={}):#including <body>
  yield('<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>'+title+'</title>\n'
        '<style>\n')
  yield( style+'\n'
        '</style>\n'
        '</head>\n'
        '<body>\n')
  yield from ('<a href="/'+site+'">'+site+'</a><p/>\n' for site in sites)
  yield( '</body>\n'
        '</html>\n')

MIME_lookup={'.glb':'model/gltf-binary', '.gltf':'model/gltf-binary', 
             '.hdr':'application/octet-stream',
             '.html':'text/html; charset=utf-8',
             '.txt':'text/plain',
             '.md': 'text/markdown; charset=UTF-8',
             '.js': 'text/javascript; charset=UTF-8',
             '.css':'text/css; charset=UTF-8',
             '.stl':'model/stl',
             '.png':'image/png',
             '.jpg':'image/jpg',  
             '.jpeg':'image/jpeg',  
             '.gif':'image/gif',  
             '.ico':'image/vnd.microsoft.icon',
             
             }
configfile='/private/var/mobile/Containers/Data/Application/77881549-3FA6-4E4B-803F-D53B172FC865/Documents/www/config.yml'  

def load_config(configfile):
  from pathlib import Path
  with open(configfile,'r') as f:
    on_my_ipad_rootdirs,config=yaml.safe_load(f)
  on_my_ipad_rootdirs={key:Path(value) for key,value in on_my_ipad_rootdirs.items()}
  def str2path(level):
    for key,value in level.items():
      if type(value)==str:
        parts=Path(value).parts
        level[key]= Path(on_my_ipad_rootdirs[parts[0]]).joinpath(*parts[1:])
      else:
        if issubclass(type(value),dict):
          str2path(value)
  str2path(config)
  return config
  
def get_local_path(web_path, config):
    from pathlib import Path,PosixPath
    _,_,web_path,_,_,_=urlparse(web_path)
    path_parts = Path('/' + web_path.strip('/')).resolve().relative_to('/').parts
    current_level = config
    for part in path_parts:
        if issubclass(type(current_level),PosixPath): #leaf node
          raise TypeError(f'{part=}, {current_level=}')
        if part in current_level:
            current_level = current_level[part]
        elif '__any__' in current_level:
            return Path(current_level['__any__']).joinpath(*path_parts[path_parts.index(part):])
        else:
            return None  # No match
    
    # Handle the case where the path ends at a directory level with an index.html
    if issubclass(type(current_level),PosixPath): #leaf node
       return current_level
#    if 'index.html' in current_level:
#        return Path(current_level['index.html'])
# If we've made it here, and there's an '__any__', return that for directory requests
#    if '__any__' in current_level and Path(current_level['__any__']).is_dir():
    if '__any__' in current_level:
        return Path(current_level['__any__'])
    return None  # If no site matches the requested path
         
def subclass(base_class,**class_variables):
  class B(base_class):pass
  B.__name__='subclass_of_'+base_class.__name__
  for key,value in class_variables.items():
    if issubclass(type(key),str) and key.isidentifier() and not key.startswith('_'):
      setattr(B,key,value)
    else:
      raise TypeError("class_variable names need to be valid identifier names that do not start with '_'!")
  return B
  
class GeneratorFile(io.RawIOBase):
    def __init__(self, generator):
        self.generator = generator
        self.a = b''   #buffer for the current generated string
        self.a_ptr = 0 #pointer to th next byte to be transmitted
        self.EOF=False

    def readable(self):
        return True

    def readinto(self, b):
        if self.EOF:
          return 0
        try:
            b_ptr=0
            while b_ptr<len(b):#try to fill the buffer completely
              if self.a_ptr>=len(self.a):
                self.a = next(self.generator).encode()  # Assuming generator yields strings
                self.a_ptr=0
              # Copy the content of the buffer into b
              l=min(len(self.a)-self.a_ptr,len(b)-b_ptr) # the smaller amount of what's left in each buffer
              b[b_ptr:b_ptr+l] = self.a[self.a_ptr:self.a_ptr+l]
              self.a_ptr+=l #update the buffer pointers
              b_ptr+=l
            return b_ptr #should always be len(b) at this point
        except StopIteration:
            self.EOF=True
            return b_ptr
 #'
class BinaryHandler(SimpleHTTPRequestHandler):
    #os.getcwd()  # or set to any specific path where your files are located
    SITE=None
    config=None
    def translate_path(self, path):
        print(f'translate_path: {path=}')
        # This method is responsible for translating the URL path to a file system path
        path = super().translate_path(path)
        print(f'super().translate_path(path): {path}')
 #       rel_path = os.path.relpath(path, os.getcwd())
 #       if not rel_path.startswith('project'):
 #           return os.path.join(os.getcwd(), 'project', rel_path)
        return path
          
    def __new__(cls,*args,configfile='config.yml',**kwargs):
      if cls.config==None:
         cls.config=load_config(configfile)
      return super().__new__(cls)
      
    def __init__(self,*args,**kwargs):
      global myBinaryHandlerInstsnce
      myBinaryHandlerInstance=self
      super().__init__(*args,**kwargs)
      
    def send_headers(self,ext=''):
#        ext=os.path.splitext(self.path)[1].casefold()
        if ext in MIME_lookup:
          self.send_header('Content-Type', MIME_lookup[ext])
        else:
          self.send_header('Content-Type', 'application/octet-stream')#default
          print(f"\n!!! --> Unsupported file extension: {ext} <-- !!!\n",file=sys.stderr)
        super().end_headers()

    def do_GET(self):
        from pathlib import Path
#        print(f'{self.SITE=}, {self.path=}, {self.server.server_address=}')
#        print(f'{self.server.server_address=}')
#        print(f'{self.headers.items()=}')
#        print(f'{self.raw_requestline=}')
        scheme,netloc,path,params,query,fragments=urlparse(self.path)
        cleanpath_parts=Path('/' + path.strip('/')).resolve().relative_to('/').parts
        if 'Referer' in self.headers and self.__class__.SITE!=None:
          _,netloc_r,path_r,*_=urlparse(self.headers['Referer'])
          cleanpath_r_parts=Path('/' + path_r.strip('/')).resolve().relative_to('/').parts
          localpath_r=get_local_path('/'.join((self.__class__.SITE,*cleanpath_r_parts)),self.config) 
          if localpath_r and localpath_r.is_dir(): #this is the case for index.html defaults
#            print(cleanpath_parts)
#            print(cleanpath_r_parts)
            if cleanpath_r_parts[:-1]==cleanpath_parts[:-1]:
              cleanpath_parts=cleanpath_r_parts+cleanpath_parts[-1:] #add the missing parent directory back in
        
        cleanpath = '/'.join(cleanpath_parts)
#        print(f'{cleanpath=}  {cleanpath in self.__class__.config=}')
        if cleanpath in self.__class__.config and self.__class__.SITE==None:   
          print(f'setting site to "{cleanpath}" and redirect')
          self.__class__.SITE=cleanpath
          self.send_response(302)
          self.send_header('Location','http://localhost:8000/')
          self.end_headers()
          return

#          self.__class__.config=self.__class__.config[self.path]
#          self.path=''
        if self.__class__.SITE==None:
           #           print(rootpage)
#           self.path='/_.html'#dummy path (required for end_headers() to determine MIME-type)
           try:
             self.send_response(200)
             self.send_headers(ext='.html')
             shutil.copyfileobj(GeneratorFile(
               SitePicker(title='Site Picker',style='a {font-size: 30px}',sites=self.__class__.config)
               ),
               self.wfile
               )
           except BrokenPipeError as e:
             print(e,'(sending root page)') #do not attempt to send more, wait for next request instead
           except Exception as e:
             print(e,'(sending root page)')
           return    
#        path=self.path
#   
#        print(self.__class__.config)
#        print(f'web path: {self.__class__.SITE=} {self.path=}')
        localpath=get_local_path('/'.join((self.__class__.SITE,cleanpath)),self.__class__.config)
        if localpath and localpath.is_dir():
          localpath=get_local_path('/'.join((self.__class__.SITE,cleanpath,'index.html')),self.__class__.config)
        if not localpath:
           self.send_error(404, 'File Not Found: %s' % cleanpath)
           return
        print(f'{localpath=}')
        try:
          filepath,ext=os.path.splitext(localpath)
          if ext=='.md':
            self.send_response(200)
            self.send_headers(ext='.html')
#            self.wfile.write(markdown.markdown_path(filepath+'.md',extras=["code-friendly", "fenced-code-blocks"]).encode())
            _,filename=os.path.split(filepath)
            self.wfile.write(html_page_start(title=filename,style=css))
            with open(localpath,'rb') as f:
              markdown.markdownFromFile(input=f,
                                  output=self.wfile,
                                  extensions=[GithubFlavoredMarkdownExtension()],#,CodeHiliteExtension(guess_lang=True)],
                                  )
            self.wfile.write(html_page_end())
          else:
            with open(localpath, 'rb')  as f:
              self.send_response(200)
              self.send_headers(ext=ext)
              shutil.copyfileobj(f,self.wfile)     
        except BrokenPipeError as e:
            print(e,'(sending 200 response & data)') #do not attempt to send more, wait for next request instead
        except FileNotFoundError as e:
            print(e,'(sending 200 response & data)')
            try: 
               self.send_error(404, 'File Not Found: %s' % cleanpath)
            except Exception as e:
               print(e,'(sending 404 response)')
        except Exception as e:
            print(e,'(sending 200 response & data)')
            try:
              self.send_error(500, f"Server error: {e}")
            except Exception as e:
              print(e,'(sending 500 response)')
            
        
class ServerThread(threading.Thread):

    def __init__(self, port=8000,site=None): 
        self.port=port
        self.site=site
        super().__init__() 
        self._socket=None

    def run(self):
        socketserver.TCPServer.allow_reuse_address=True
        with socketserver.TCPServer(("", self.port), subclass(BinaryHandler,SITE=self.site,config=None)) as httpd:
            self._socket=httpd
            print("Serving at port", self.port,file=sys.stderr)
            try:
                httpd.serve_forever()
                print(f"Server stopped.",file=sys.stderr)
            except Exception as e:
                print(f"{e}\nServer stopped.",file=sys.stderr)
           
    def stop(self):
        if self._socket!=None:
           self._socket.shutdown()
      
if '__main__'==__name__:
    background_thread=ServerThread(port=8000,site='textastic')
    print(f'{background_thread.is_alive()=}')
    background_thread.start()
    print(f'{background_thread.is_alive()=}')
    webbrowser.open_new_tab('http://localhost:8000')
    try:
      while True:
        pass
    except KeyboardInterrupt:
      background_thread.stop()
      background_thread.join()
      
#    del background_thread



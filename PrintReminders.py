import reminders
import shortcuts
import os
import sys
from objc_util import *   

#@on_main_thread
def CompletionHandler(_cmd,printInteractionController_,BOOL_completed,NSError_p_error):
#  pass
  print('print completed')

@on_main_thread
def print_html_orientation(input, orientation = 'P'):
  '''takes HTML input and formats it for printing. Uses the built in ios UI print dialogue. Orientation should be 'P' or 'L' '''
  html = ObjCClass('UIMarkupTextPrintFormatter').alloc().initWithMarkupText_(ns(input))
  printController = ObjCClass('UIPrintInteractionController').sharedPrintController()
  printInfo = ObjCClass('UIPrintInfo').printInfoWithDictionary_(None)
  printInfo.orientation = int(orientation[0].upper() == 'L')
  printController.printInfo = printInfo
  printController.setPrintFormatter_(html)
  completionHandlerBlock = ObjCBlock(CompletionHandler, restype=None, argtypes=[c_void_p, c_void_p, c_bool, c_void_p])
  printController.presentAnimated_completionHandler_(0, None)#completionHandlerBlock)
  
def main():
  print(sys.argv)
  ListName=sys.argv[1] if len(sys.argv)>1 else 'Shopping'
  calendars={ calendar.title:calendar  for calendar in reminders.get_all_calendars()}
  #print (calendars)
  todo = reminders.get_reminders(calendar=calendars[ListName],completed=False)
  header=False
  #print('TODO List')
  #print('=========')
  #ToDo='\n'.join(r.title for r in todo)
  html=f'''
  <!doctype html>
  <html>
  <head> 
  <title>Our Funky HTML Page</title>
  <meta name="description" content="Our first page">
  <meta name="keywords" content="html tutorial template">
  </head>
  <body>
  <table>
  {'<tr><th> <th/><th>Items</th></tr>' if header else ''}
  {''.join('<tr><td>O<td/><td>'+r.title+'</td></tr>' for r in todo)}
  </table>
  </body>
  </html>'''
  #print(html)
  print_html_orientation(html)
  print(f'{ListName} List Printed!')
  
if __name__=='__main__':
  print(f'argv{sys.argv}')
  main()

#os._exit(0)


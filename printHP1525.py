import reminders
import sys
import socket
import os
import unicodedata

# Printer configuration
PRINTER_IP = "10.0.0.188"  # Your printer's reserved DHCP IP address
PRINTER_PORT = 9100  # HP JetDirect port for raw printing
font_lookup={'CG Times':4101,
             'Univers':4148,
             'AntiqOlive':4168,
             'CG Omega':4113,
             'Garamond':4197,
             'Courier':4099,
             'Letter Gothic':4102,
             'Albertus':4362,
             'Clarendon':4140,
             'Coronet':4116,
             'Marigold':4297,
             'Arial':16602,
             'TimesNewRmn':16901,
             'Symbol':16686,
             'Winddings':31402,
             'ITCAvantGard':24607,
             'ITCBookman':24623,
             'CourierPS':24579,
             'Helvetica':24580,
             'NwCentSchlbk':24703,
             'Palatino':24591,
             'SymbolPS':45358,
             'Times':25093,
             'ZapfChancery':45099,
             'ZapfDingbats':45101,
             'Naskh':4124,
             'Koufi':4264,
             'Line Printer':0
             }
# HP Roman-8 mapping dictionary (Unicode char to Roman-8 byte)
utf8_lookup=[bytes(escape, 'utf-8').decode('unicode_escape') for escape in['\\u0000', '\\u0001', '\\u0002', '\\u0003', '\\u0004', '\\u0005', '\\u0006', '\\u0007', '\\u0008', '\\u0009', '\\u000A', '\\u000B', '\\u000C', '\\u000D', '\\u000E', '\\u000F', '\\u0010', '\\u0011', '\\u0012', '\\u0013', '\\u0014', '\\u0015', '\\u0016', '\\u0017', '\\u0018', '\\u0019', '\\u001A', '\\u001B', '\\u001C', '\\u001D', '\\u001E', '\\u001F', '\\u0020', '\\u0021', '\\u0022', '\\u0023', '\\u0024', '\\u0025', '\\u0026', '\\u0027', '\\u0028', '\\u0029', '\\u002A', '\\u002B', '\\u002C', '\\u002D', '\\u002E', '\\u002F', '\\u0030', '\\u0031', '\\u0032', '\\u0033', '\\u0034', '\\u0035', '\\u0036', '\\u0037', '\\u0038', '\\u0039', '\\u003A', '\\u003B', '\\u003C', '\\u003D', '\\u003E', '\\u003F', '\\u0040', '\\u0041', '\\u0042', '\\u0043', '\\u0044', '\\u0045', '\\u0046', '\\u0047', '\\u0048', '\\u0049', '\\u004A', '\\u004B', '\\u004C', '\\u004D', '\\u004E', '\\u004F', '\\u0050', '\\u0051', '\\u0052', '\\u0053', '\\u0054', '\\u0055', '\\u0056', '\\u0057', '\\u0058', '\\u0059', '\\u005A', '\\u005B', '\\u005C', '\\u005D', '\\u005E', '\\u005F', '\\u0060', '\\u0061', '\\u0062', '\\u0063', '\\u0064', '\\u0065', '\\u0066', '\\u0067', '\\u0068', '\\u0069', '\\u006A', '\\u006B', '\\u006C', '\\u006D', '\\u006E', '\\u006F', '\\u0070', '\\u0071', '\\u0072', '\\u0073', '\\u0074', '\\u0075', '\\u0076', '\\u0077', '\\u0078', '\\u0079', '\\u007A', '\\u007B', '\\u007C', '\\u007D', '\\u007E', '\\u007F', '\\u0080', '\\u0081', '\\u0082', '\\u0083', '\\u0084', '\\u0085', '\\u0086', '\\u0087', '\\u0088', '\\u0089', '\\u008A', '\\u008B', '\\u008C', '\\u008D', '\\u008E', '\\u008F', '\\u0090', '\\u0091', '\\u0092', '\\u0093', '\\u0094', '\\u0095', '\\u0096', '\\u0097', '\\u0098', '\\u0099', '\\u009A', '\\u009B', '\\u009C', '\\u009D', '\\u009E', '\\u009F', '\\u00A0', '\\u00C0', '\\u00C2', '\\u00C8', '\\u00CA', '\\u00CB', '\\u00CE', '\\u00CF', '\\u00B4', '\\u2035', '\\u2227', '\\u00A8', '\\u223C', '\\u00D9', '\\u00DB', '\\u20A4', '\\u00AF', '\\u00DD', '\\u00FD', '\\u00B0', '\\u00C7', '\\u00E7', '\\u00D1', '\\u00F1', '\\u00A1', '\\u00BF', '\\u00A4', '\\u00A3', '\\u00A5', '\\u00A7', '\\u0192', '\\u00A2', '\\u00E2', '\\u00EA', '\\u00F4', '\\u00FB', '\\u00E1', '\\u00E9', '\\u00F3', '\\u00FA', '\\u00E0', '\\u00E8', '\\u00F2', '\\u00F9', '\\u00E4', '\\u00EB', '\\u00F6', '\\u00FC', '\\u00C5', '\\u00EE', '\\u00D8', '\\u00C6', '\\u00E5', '\\u00ED', '\\u00F8', '\\u00E6', '\\u00C4', '\\u00EC', '\\u00D6', '\\u00DC', '\\u00C9', '\\u00EF', '\\u00DF', '\\u00D4', '\\u00C1', '\\u00C3', '\\u00E3', '\\u00D0', '\\u00F0', '\\u00CD', '\\u00CC', '\\u00D3', '\\u00D2', '\\u00D5', '\\u00F5', '\\u0160', '\\u0161', '\\u00DA', '\\u0178', '\\u00FF', '\\u00DE', '\\u00FE', '\\u00B7', '\\u00B5', '\\u00B6', '\\u00BE', '\\u2014', '\\u00BC', '\\u00BD', '\\u00AA', '\\u00BA', '\\u00AB', '\\u25A0', '\\u00BB', '\\u00B1','']]
roman8_map = {key:i for i,key in enumerate(utf8_lookup)}
roman8_map['\u2044']=ord('/') 
def send_to_printer(data,font='Helvetica',proportional=True,pointsize=12,linespacing=1.25,style=0,weight=0,testing=False):
    global all
    """Send raw byte data to the HP CP1525nw via JetDirect."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((PRINTER_IP, PRINTER_PORT))
            
            pcl_header = (
                b"\x1b%-12345X@PJL\n"
                b"@PJL JOB NAME=\"Shopping List\"\n"
                b"@PJL SET ECONOMODE=ON\n"
                b"@PJL SET RESOLUTION=600\n"
                b"@PJL ENTER LANGUAGE=PCL\n"
                b"\x1b&l0O"
                b"\x1b&l0E"
                b"\x1b&a0L"
                b"\x1b*p0x100Y"
                b"\x1b(8U"  # HP Roman-8 symbol set
                #b"\x1b(s1P" # proportional font
                #b"\x1b(s10V"
                +f'\x1b(s{int(proportional)}p{pointsize}v{style}s{weight}b{font_lookup["Helvetica"]}T'.encode()+
                f"\x1b&l{pointsize*linespacing/1.5:.1f}C".encode() # &l=line spacing, 4D=4 lines/inch, C=x/48 inch
            )
            pcl_footer = (
                b"\x1b&l0H"
                b"\x1b%-12345X@PJL EOJ\n"
            )
            if testing:
              print('Testing Testing:')
              all=pcl_header + data + pcl_footer
              print(all.decode(errors='replace').replace('\x1b','<esc>'))
              return False
            else:
              s.sendall(pcl_header + data + pcl_footer)
            
        print("Print job sent successfully!")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to printer: {e}")
        return False

def unicode_to_roman8(text):
    """Convert Unicode string to HP Roman-8 byte string."""
    # Normalize to NFC to handle decomposed characters (e.g., "u\u0308" -> "ü")
    text = unicodedata.normalize('NFC', text)
    
    # Convert each character to Roman-8 bytes
    result = bytearray()
    for char in text:
        if ord(char) < 0x80:  # ASCII range
            result.append(ord(char))
        elif char in roman8_map:  # Extended Roman-8 range
            result.append(roman8_map[char])
        else:  # Fallback for unmapped characters
            result.append(ord('?'))
    return bytes(result)

def main(args):
    ListName = args[1] if len(args) > 1 else 'Shopping'
    
    calendars = {calendar.title: calendar for calendar in reminders.get_all_calendars()}
    if ListName not in calendars:
        print(f'Calendar "{ListName}" not found.')
        return
    
    todo = reminders.get_reminders(calendar=calendars[ListName], completed=False)
    
    # Format shopping list as plain text, only items, with carriage returns
    data = "\r\n".join(r.title for r in todo)
    if not data:
        data = "No items in list"
    data += "\r\n"
    
    # Convert to Roman-8 bytes
    data_roman8 = unicode_to_roman8(data)
    success = send_to_printer(data_roman8,testing=False)
    
    if success:
        print(f'{ListName} List printed!')
    else:
        print(f'Failed to print {ListName} List.')

if __name__ == '__main__':
    if "args" in globals():  # used as PythonistaLab shortcut?  
      args.insert(0,'printHP1525.py')
    else:
      args=sys.argv
    print(f'argv: {sys.argv}')
    main(args)
 

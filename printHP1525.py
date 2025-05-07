import reminders
import sys
import socket
import os

# Printer configuration
PRINTER_IP = "10.0.0.188"  # Your printer's reserved DHCP IP address
PRINTER_PORT = 9100  # HP JetDirect port for raw printing

def send_to_printer(data):
    """Send raw text data to the HP CP1525nw via JetDirect."""
    try:
        # Create a socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5-second timeout for connection
            s.connect((PRINTER_IP, PRINTER_PORT))
            
            # PCL commands for grayscale, minimal margins, and 1.5 line spacing
            pcl_header = (
                "\x1b%-12345X@PJL\n"  # Universal Exit Language (UEL)
                "@PJL JOB NAME=\"Shopping List\"\n"
                "@PJL SET ECONOMODE=ON\n"  # Enable grayscale/economy mode
                "@PJL SET RESOLUTION=600\n"  # 600 DPI resolution
                "@PJL ENTER LANGUAGE=PCL\n"
                "\x1b&l0O"  # Portrait orientation
                "\x1b&l0E"  # Top margin (0 lines)
                "\x1b&a0L"  # Left margin (0 columns)
                "\x1b*p0x150Y"  # Cursor to (0, 150/300 inch = 5mm down) to avoid clipping
                "\x1b(8U"  # Symbol set (Roman-8, suitable for text)
                "\x1b(s0P"  # Fixed pitch font
                "\x1b(s10V"  # Font size (10 points)
                "\x1b&l4D"  # Line spacing (4 lines per inch, ~1.5 spacing for 10-point font)
            )
            pcl_footer = (
                "\x1b&l0H"  # Form feed to eject page
                "\x1b%-12345X@PJL EOJ\n"  # End of job
            )
            
            # Send data
            s.sendall((pcl_header + data + pcl_footer).encode())
            
        print("Print job sent successfully!")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to printer: {e}")
        return False

def main():
    # Get list name from arguments or default to 'Shopping'
    ListName = sys.argv[1] if len(sys.argv) > 1 else 'Shopping'
    
    # Get reminders
    calendars = {calendar.title: calendar for calendar in reminders.get_all_calendars()}
    if ListName not in calendars:
        print(f'Calendar "{ListName}" not found.')
        return
    
    todo = reminders.get_reminders(calendar=calendars[ListName], completed=False)
    
    # Format shopping list as plain text, only items, with carriage returns
    data = "\r\n".join(r.title for r in todo)
    if not data:
        data = "No items in list"
    data += "\r\n"  # Ensure final line break
    
    # Send to printer
    success = send_to_printer(data)
    
    if success:
        print(f'{ListName} List printed!')
    else:
        print(f'Failed to print {ListName} List.')

if __name__ == '__main__':
    print(f'argv: {sys.argv}')
    main()

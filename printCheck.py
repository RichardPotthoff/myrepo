import sys
import socket
import os
from datetime import datetime

# Printer configuration
PRINTER_IP = "10.0.0.188"  # Your printer's reserved DHCP IP address
PRINTER_PORT = 9100  # HP JetDirect port for raw printing

# Check dimensions and centering (in mm)
CHECK_HEIGHT = 70  # Check height in landscape
CHECK_WIDTH = 152.5  # Check width in landscape
CARRIER_WIDTH = 297  # A4 landscape width
CARRIER_HEIGHT = 210  # A4 landscape height
OFFSET_X = (CARRIER_WIDTH - CHECK_WIDTH) / 2  # ~72.25mm
OFFSET_Y = (CARRIER_HEIGHT - CHECK_HEIGHT) / 2  # ~70mm

# Convert mm to 1/300 inch units for PCL
MM_TO_UNITS = 11.81  # 1mm ≈ 11.81 units (300 DPI)

# Field positions (x, y in mm, bottom-left of field) and lengths (mm)
FIELD_POSITIONS = {
    "date": {"pos": (100, 20), "length": 28},
    "payee": {"pos": (22, 30), "length": 90},
    "amount_numeric": {"pos": (121, 30), "length": 23},
    "amount_written": {"pos": (10, 38), "length": 105},
    "memo": {"pos": (16, 57), "length": 50} 
}

# Test mode placeholders
TEST_PLACEHOLDERS = {
    "date": "YYYY/MM/DD",
    "payee": "X" * 36,  # ~90mm at ~2.5mm/char
    "amount_numeric": "9999.99",
    "amount_written": "X" * 42,  # ~105mm
    "memo": "X" * 20  # ~50mm
}

def mm_to_units(mm):
    """Convert mm to 1/300 inch units."""
    return int(mm * MM_TO_UNITS)

def fill_field(text, field_length_mm):
    """Fill field to approximate length with asterisks, except for date."""
    chars_per_mm = 0.4  # ~2.5mm/char at 10-point fixed-pitch (~10 chars/inch)
    max_chars = int(field_length_mm * chars_per_mm)
    #text = text[:max_chars]  # Truncate if too long
    return text + "*" * max(0,(max_chars - len(text)))  # Pad with asterisks

def send_to_printer(data):
    """Send raw text data to the HP CP1525nw via JetDirect."""
    try:
        # Create a socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5-second timeout for connection
            s.connect((PRINTER_IP, PRINTER_PORT))
            
            # PCL commands for grayscale, landscape, minimal margins
            pcl_header = (
                "\x1b%-12345X@PJL\n"  # Universal Exit Language (UEL)
                "@PJL JOB NAME=\"Check\"\n"
                "@PJL SET ECONOMODE=ON\n"  # Enable grayscale/economy mode
                "@PJL SET RESOLUTION=600\n"  # 600 DPI resolution
                "@PJL ENTER LANGUAGE=PCL\n"
                "\x1b&l1O"  # Landscape orientation
                "\x1b&l0E"  # Top margin (0 lines)
                "\x1b&a0L"  # Left margin (0 columns)
                "\x1b*p0x150Y"  # Cursor to 5mm down to avoid clipping
                "\x1b(8U"  # Symbol set (Roman-8, suitable for text)
                "\x1b(s0P"  # Fixed pitch font
                "\x1b(s10V"  # Font size (10 points)
                "\x1b&l4D"  # Line spacing (4 lines per inch, ~1.5 spacing)
            )
            pcl_footer = (
                "\x1b&l0H"  # Form feed to eject page
                "\x1b%-12345X@PJL EOJ\n"  # End of job
            )
            
            # Send data
            s.sendall((pcl_header + data + pcl_footer).encode())
            
        print("Check sent successfully!")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to printer: {e}")
        return False

def main(args):
    # Check if arguments are provided (len=1 means only script name)
    if len(args) == 1:
        # Test mode: Print "+" at corners (centered on corners) and placeholders
        corners = [
            (0, 0),  # Top-left
            (CHECK_WIDTH, 0),  # Top-right
            (0, CHECK_HEIGHT),  # Bottom-left
            (CHECK_WIDTH, CHECK_HEIGHT)  # Bottom-right
        ]
        data = ""
        # Corner markers, shifted 1.25mm left (-15 units), 1.5mm down (+18 units)
        for x, y in corners:
            px = mm_to_units(x + OFFSET_X) - 15  # Shift left 1.25mm
            py = mm_to_units(y + OFFSET_Y) + 18  # Shift down 1.5mm
            data += f"\x1b*p{px}x{py}Y+\r\n"
        # Field markers
        for field, info in FIELD_POSITIONS.items():
            x, y = info["pos"]
            px = mm_to_units(x + OFFSET_X)
            py = mm_to_units(y + OFFSET_Y)
            text=TEST_PLACEHOLDERS[field]
            if field=="amount_numeric":
               text = fill_field(f'{float(text):0,.2f}', info["length"])
            data += f"\x1b*p{px}x{py}Y{text}\r\n"
    else:
        # Real mode: Get check data from arguments, no corner markers
        check_data = {
            "date": args[1] if len(args) > 1 else "TEST_DATE",
            "payee": args[2] if len(args) > 2 else "TEST_PAYEE",
            "amount_numeric": args[3] if len(args) > 3 else "TEST_AMOUNT",
            "amount_written": args[4] if len(args) > 4 else "TEST_AMOUNT_WRITTEN",
            "memo": args[5] if len(args) > 5 else "TEST_MEMO"
        }
        
        # Format check data with PCL cursor positioning
        data = ""
        for field, info in FIELD_POSITIONS.items():
            x, y = info["pos"]
            px = mm_to_units(x + OFFSET_X)
            py = mm_to_units(y + OFFSET_Y)
            text=check_data[field]
            if field=="amount_numeric":
               text = fill_field(f'{float(text):0,.2f}', info["length"])
            data += f"\x1b*p{px}x{py}Y{text}\r\n"
    
    # Send to printer
    success = send_to_printer(data)
    
    if success:
        print("Check printed!" if len(args) > 1 else "Test pattern printed!")
    else:
        print("Failed to print check.")

if __name__ == '__main__':
    if "args" in globals():  # used as PythonistaLab shortcut?  
      args.insert(0,'printCheck.py')
    else:
      args=sys.argv
    print(f'{args = }')
    main(args)

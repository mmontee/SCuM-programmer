#python "C:\Users\mitch\OneDrive\SchoolFiles\_URMP\SCuM\Software\test_bootload.py"
import serial
import random
import argparse
import signal
import sys
import time

# User Defined Parameters ****************************************

# Com port of nRF board 
nRF_port="COM3" 

# Path to SCuM binary
binary_image="C:/Users/mitch/OneDrive/SchoolFiles/_URMP/openWSN/openwsn-fw-2022/projects/scum/03oos_openwsn/Objects/03oos_openwsn.bin"
#binary_image="C:/Users/mitch/OneDrive/SchoolFiles/_URMP/SCuM/repo/scum-test-code/scm_v3c/applications/1_wire/Objects/1_Wire.bin"
#binary_image="C:/Users/mitch/OneDrive/SchoolFiles/_URMP/openWSN/openwsn-fw-develop_FW-892/projects/scum/03oos_openwsn/Objects/03oos_openwsn.bin"
#binary_image="C:/Users/mitch/OneDrive/SchoolFiles/_URMP/openWSN/openwsn-fw-titan-smart_stake\projects/scum/03oos_openwsn/Objects/03oos_openwsn.bin"
# End User Defined Parameters ************************************



def signal_handler(signal, frame):
    nRF_ser.reset_input_buffer()
    nRF_ser.close()
    print("\rBye...")
    exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Serial connections
nRF_ser = None

boot_mode='3wb'
pad_random_payload=False

# Open COM port to nRF
nRF_ser = serial.Serial(
    port=nRF_port,
    baudrate=250000,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS)
    
# Open binary file from Keil
with open(binary_image, 'rb') as f:
    bindata = bytearray(f.read())
    
# Need to know how long the binary payload to pad to 64kB
code_length = len(bindata) - 1
pad_length = 65536 - code_length - 1

#print(code_length)

# Optional: pad out payload with random data if desired
# Otherwise pad out with zeros - uC must receive full 64kB
if(pad_random_payload):
    for i in range(pad_length):
        bindata.append(random.randint(0,255))
    code_length = len(bindata) - 1 - 8
else:
    for i in range(pad_length):
        bindata.append(0)
        
nRF_ser.reset_input_buffer()       

# Send the binary data over uart
print("\r\nScuM nRF Serial Programmer.\r\n")
print("\rPress (Ctrl + c) to Exit\r\n")
nRF_ser.write(bindata)
# and wait for response that writing is complete
print(nRF_ser.read_until())
	
# Display 3WB confirmation message from nRF
print(nRF_ser.read_until())

print("Upload Complete -- Entering UART RX mode.\r\n")
print("\rPress (Ctrl + c) to Exit\r\n")

#set timout or forever be blocked
nRF_ser.timeout = 0.1
# Read bytes from nRF_port until EOL then print and repeat.
message = bytes()
while True:
    char = nRF_ser.read(1);
    message = message + char        
    char = char.decode("utf-8", "ignore")
    if(char == '\n'):
        print(message.decode("utf-8", "ignore"))
        message = bytes()
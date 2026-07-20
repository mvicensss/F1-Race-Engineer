import socket

def get_current_ip():
    #force the system to reveal current local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        #try connecting to external IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

#dynamic config
IP_LOCAL = get_current_ip()
UDP_IP = "0.0.0.0" #listen to every network interface
UDP_PORT = 20777

print("="*55)
print("Starting telemetry server...")
print("="*55)
print(" ⚠VERIFY THE FOLLOWING DATA IN PS4")
print(f" -> IP addres of UDP transmission: {IP_LOCAL}")
print(f" -> UDP transmission port:       {UDP_PORT}")
print("="*55)
print("Waiting for driver to go out...\n")

#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

try:
    while True:
        data, addr = sock.recvfrom(2048)
        print(f"[OK] Packet recieved from {addr[0]} | Size: {len(data)} bytes")
except KeyboardInterrupt:
    print("\nServer closed correctly")
    

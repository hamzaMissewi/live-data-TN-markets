import socket
s = socket.socket()
s.settimeout(2)
result = s.connect_ex(('localhost', 5432))
print('Port 5432 open:', result == 0)
s.close()
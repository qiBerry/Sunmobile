	#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
ip = '192.168.0.106'
port = 1080
message = '0/3/120'

sock = socket.socket()
sock.connect((ip, port))
sock.send(message.encode('utf-8'))

data = sock.recv(32)
sock.close()

print(data)
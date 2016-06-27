import socket                   # Import socket module

port = 9005                    # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.

print 'Server listening....'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    data = conn.recv(1024)
    print('Server received', repr(data))

    filename='key'
    f = open(filename,'wb')
    f.write(data)
    f.close()

    print('Done save key')

    conn.send('Your key is save.')
    conn.close()
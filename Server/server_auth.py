import socket                   # Import socket module

port = 9004              # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.

headerList = ["Recipient: wabesasa@gmail.com", "sam26092357@hotmail.com"]

print 'Server listening....'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    data = conn.recv(1024)
    print('Server received', repr(data))

    if data in headerList:
        filename='key'
        f = open(filename,'wb')
        key = f.readline()
        f.close()
        print('Authenticated.')
        conn.send(key)
    else :
        print('Not Authenticated.')
        conn.send('NotAuthenticated')

    print('Done')
    conn.close()
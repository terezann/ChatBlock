import node
import socket

node1 = node.Node(False)

public_key = node1.wallet['address'].export_key().decode()  # Convert RSA key to string

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

print(public_key)
msg = s.send(public_key.encode()) # send public key

# Receive acknowledgement from the server
ack_msg = s.recv(1024)
print(ack_msg.decode())

# Close the connection
s.close()

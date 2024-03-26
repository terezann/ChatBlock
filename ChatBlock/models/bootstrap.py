import node
import socket


# Number of nodes
n = 2

# Create bootstrap
bootstrap = node.Node(True)

bootstrap.set_id()

# Extract keys
public_key = bootstrap.wallet['address'].publickey().export_key().decode()
public_key = public_key.replace("-----BEGIN PUBLIC KEY-----", "")
public_key = public_key.replace("-----END PUBLIC KEY-----", "")

private_key = bootstrap.wallet['private_key'].export_key().decode()
private_key = private_key.replace("-----BEGIN RSA PRIVATE KEY-----", "")
private_key = private_key.replace("-----END RSA PRIVATE KEY-----", "")

print("Bootstrap Info")
print("----------------")
print(f"Public Key: {public_key}")
print(f"Private Key: {private_key}")


# Append bootsrap to the ring
# set ip = 0
bootstrap.register_node(id, 0, bootstrap.wallet['address'], bootstrap.wallet['private_key'], 100)

# Create genesis block
bootstrap.create_genesis_block(n)

genesis_block = bootstrap.blockchain[0]

print("Genesis block details")
print(f"Index: {genesis_block.index}")
print(f"Previous hash: {genesis_block.previous_hash}")
print(f"Hash: {genesis_block.hash}")
print(f"Validator: {genesis_block.validator}")
print(f"Transaction Value: {genesis_block.list_of_transactions[0].amount}")


x = 1

if x:
    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 1234))
    s.listen(20)

    clientsocket, address = s.accept()
    print(f"Connection with {address} is established!")

    # Send acknowledgement to the client
    clientsocket.send("Connection established with the bootstrap node!".encode())

    # Read data from the client until the connection is closed
    while True:
        msg = clientsocket.recv(1024)
        if not msg:
            break
        print(msg.decode())

    # Close the connection
    clientsocket.close()
    s.close()

import block
import wallet
import random
import transaction
import socket
import pickle
import threading
import time

from Crypto.Signature import PKCS1_v1_5

from binascii import hexlify, unhexlify
from collections import OrderedDict

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

capacity = block.capacity

class Node:
    def __init__(self, ip, port, is_boot = False):
        self.ip = ip
        self.port = port
        self.blockchain=[]
        self.is_boot = is_boot
        self.id = self.set_id()
        self.wallet = self.create_wallet()
        #ring: here we store info for every node, as its id, its address (ip:port), its public  key and its balance
        self.ring = []
        self.transactions = []
        self.stakes = []
        self.balances = []
        self.nonces = []
        
    def set_id(self):
        if self.is_boot:
            return 0
        else: return None

    def send_info(self):
        pass
         
    def POS(self, seed):
        lottery_players = []
        for player, stake in enumerate(self.stakes):
            for i in range(stake):
                lottery_players.append(player)
        ###lottery_sum = self.stakes.sum()
        lottery_sum = sum(self.stakes)
        random.seed(seed)
        winner = random.randint(0, lottery_sum)
        validator = lottery_players[winner]
        return validator

    def mine_block(self):
        last_block = self.blockchain[-1]
        previous_hash = last_block.hash
        seed = previous_hash
        index = last_block.index + 1
        validator = self.POS(seed)
        print(validator)
        if (validator == self.id):
            myblock = block.Block(index, validator, previous_hash, self.transactions.copy())
            self.blockchain.append(myblock)
            self.broadcast_block(myblock)
        self.transactions = []

    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet().new_wallet()
        

    def register_node(self, id, ip, port, public_key, balance, stake):
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking its wallet and ip:port address
        #bootstrap node informs all other nodes and gives the request node an id and 100NBCs.
        if self.id != 0: #if I am not the bootstrap
            print('Oh no, I am not the bootstrap, try again')
            return
        
        #add the node
        self.ring.append({'id' : id,
                          'ip' : ip,
                          'port' : port,
                          'address' : public_key,
                          #'balance' : balance
                        })
        self.balances.append(balance)
        self.stakes.append(stake)
        self.nonces.append(0)

    def create_transaction(self, receiver_address, value, broadcast=True):
        my_transaction = transaction.Transaction(
            self.wallet['address'], 
            self.wallet['private_key'], 
            receiver_address, 
            value,
            'money', 
            self.nonces[self.id])
        #remember to broadcast it
        #self.nonces[self.id] += 1
        if broadcast:
            self.broadcast_transaction(my_transaction)
        return my_transaction

    def verify_signature(self, sender_address, hash, signature):
        verifier = PKCS1_v1_5.new(sender_address)
        verification = verifier.verify(hash, signature)
        return verification

    def validate_transaction(self, transaction:transaction.Transaction):
        #use of signature and NBCs balance
        #verify_sign
        #check the balance, do not forget stakes
        isVerify = self.verify_signature(transaction.sender_address, transaction.hash, transaction.signature)
        #!!!money (add later messages)
        sender_id = [r['id'] for r in self.ring if r['address'] == transaction.sender_address][0]
        receiver_id = [r['id'] for r in self.ring if r['address'] == transaction.receiver_address][0]
        sender_balance = self.balances[sender_id]
        enough_money = (sender_balance - transaction.amount) >= 0
        #check nonce
        noncesOk = self.nonces[sender_id] == transaction.nonce
        combo = isVerify and enough_money and noncesOk
        #allazei to nohma
        if combo:
            self.nonces[sender_id] += 1
            self.balances[sender_id] -= transaction.amount
            self.balances[receiver_id] += transaction.amount
            self.transactions.append(transaction)
            if len(self.transactions) == capacity:
                self.mine_block()

        return combo
    
    # Create genesis block
    def create_genesis_block(self, n):
        if(self.id != 0):
            return
        # Create the first block (genesis block)
        # Customize as per your requirements
        #myblock = block.Block(index, validator, previous_hash, self.transactions.copy())
        genesis_block = block.Block(0, 0, 1, [self.create_transaction(0, 1000*n, broadcast=False)])
        self.blockchain.append(genesis_block)

    # Create new block
    def create_new_block(self, data):
        # Create a new block and add it to the chain
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_hash = self.calculate_hash(new_index, previous_block.hash, new_timestamp, data)
        new_block = Block(new_index, previous_block.hash, new_timestamp, data, new_hash)
        return new_block
            
        

#    def valid_proof(.., difficulty: MINING_DIFFICULTY):
        
    #consensus functions

    def validate_block(self, block):
        last_block = self.blockchain[-1]
        previous_hash = last_block.hash
        validator = self.POS(previous_hash)

        validator_correct = (validator == block.validator)
        hash_correct = (previous_hash == block.previous_hash)

        if validator_correct and hash_correct:
            self.blockchain.append(block)
    

    def validate_chain(self, chain):
        self.blockchain.append(chain[0])  # add genesis block to blockchain
        for block in chain[1:]:
            self.validate_block(block)

    ####### Ola poutana #######

    def start_listener(self):
        server_address = (self.ip, self.port)
        print("server_address: ", server_address)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(server_address)
            sock.listen()
            print(f"Node {self.id} listening on {server_address}")
            while True:
                connection, client_address = sock.accept()
                try:
                    data = b""
                    while True:
                        chunk = connection.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    self.handle_received_data(data)
                except Exception as e:
                    print(f"Error handling data from {client_address}: {e}")
                finally:
                    connection.close()

    def handle_received_data(self, data):
        received_message = pickle.loads(data)
        #public_key = RSA.import_key(public_key_string.encode())
        message_type = received_message[0]
        received_object = received_message[1] 

        if message_type == 'address':
            received_object = RSA.import_key(received_object.encode())

        #elif message_type == 'node_info'

        return

        if isinstance(received_object, transaction.Transaction):
            print(f"Node {self.id} received transaction from Node {received_object.sender_id}: "
                  f"Sender: {received_object.sender_id}, Receiver: {received_object.receiver_id}, "
                  f"Amount: {received_object.amount}")
        else:
            print(f"Node {self.id} received unrecognized data")

    def broadcast_transaction(self, transaction):
        threads = []
        print(self.ring)
        print(transaction)
        for node_info in self.ring:
            thread = threading.Thread(target=self.send_transaction, args=(node_info, transaction))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def send_transaction(self, node_info, transaction):
        print("ip: ", node_info['ip'])
        node_address = (node_info['ip'], node_info['port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_transaction = pickle.dumps(transaction)
                sock.sendall(serialized_transaction)
        except Exception as e:
            print(f"Error sending transaction to {node_address}: {e}")

    def send_wallet_address_to_bootstrap(self, bootstrap_address):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(bootstrap_address)
                serialized_wallet_address = pickle.dumps(('address', self.wallet['address'].export_key().decode()))
                #print(serialized_wallet_address)
                sock.sendall(serialized_wallet_address)
        except ConnectionResetError:
            print("Socket Closed by the other end")
        except Exception as e:
            print(f"Error sending wallet address to bootstrap node at {bootstrap_address}: {e}")

    # Send id from bootstrap to node
    def send_info_to_nodes(self, node_address, id, blockchain):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_id = pickle.dumps(('node_info', id, blockchain))
                sock.sendall(serialized_id)
        except ConnectionResetError:
            print("Socket Closed by the other end")
        except Exception as e:
            print(f"Error sending info to node at {node_address}: {e}")
        
"""
my_node1 = Node()
my_node2 = Node()
my_node_baddie = Node()
my_transaction = my_node1.create_transaction(my_node2.wallet['address'], 10)
verification = my_node2.verify_signature(my_node_baddie.wallet['address'], my_transaction.hash, my_transaction.signature)
print(verification)
"""
n = 10


# Assuming the bootstrap node's address is known
bootstrap_address = ('localhost', 5000)  # Update with the actual address of the bootstrap node

# Create the bootstrap node
bootstrap_node = Node('localhost', 5000, is_boot=True)
bootstrap_node.register_node(bootstrap_node.id, 'localhost', 5000, bootstrap_node.wallet['address'], 0, 0)

# Create the blockchain and genesis block
bootstrap_node.create_genesis_block(n)

# Start listener for bootstrap node
threading.Thread(target=bootstrap_node.start_listener).start()

# Create 9 more nodes and register them with the bootstrap node
nodes = []
for i in range(1, 10):
    node = Node('localhost', 5000+i, is_boot=False)
    nodes.append(node)
    # Start listener for non-bootstrap nodes
    threading.Thread(target=node.start_listener).start()

    # Send wallet address to bootstrap node
    threading.Thread(target=node.send_wallet_address_to_bootstrap, args=(bootstrap_address,)).start()
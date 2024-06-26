import block
import random
import transaction
import socket
import pickle
import threading
import time
import sys

from Crypto.Signature import PKCS1_v1_5

from binascii import hexlify, unhexlify
from collections import OrderedDict

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

#capacity = 10
fee = 0.03

class Node:
    node_id = 0
    def __init__(self, ip, port, bootstrap_address, capacity, is_boot = False, n=1, is_initialized = False, node_info = None):
        self.n = n
        self.ip = ip
        self.port = port
        self.bootstrap_address = bootstrap_address
        self.is_boot = is_boot
        self.capacity = capacity

        if is_initialized:
            if node_info == None:
                print("Error loading node data")
                return
            self.blockchain = node_info[0]
            self.id = node_info[1]
            self.wallet = node_info[2]
            self.ring = node_info[3]
            print("RINGG", self.ring)
            self.transactions = node_info[4]
            self.stakes = node_info[5]
            self.balances = node_info[6]
            self.hard_balances = node_info[7]
            self.nonces = node_info[8]
            self.node_ready = node_info[9]
            return

        self.blockchain=[]
        self.id = self.set_id()
        self.wallet = self.create_wallet()
        #ring: here we store info for every node, as its id, its address (ip:port), its public  key and its balance
        self.ring = []
        self.transactions = []
        self.stakes = [0]*n
        self.balances = [0]*n
        self.hard_balances = [0]*n
        self.nonces = [0]*n
        self.node_ready = False

        print(f"Node with ip {self.ip} generated")
        
        threading.Thread(target=self.start_listener).start()

        # Send wallet address to bootstrap node
        if is_boot == False:
            threading.Thread(target=self.send_wallet_address_to_bootstrap, args=(bootstrap_address,)).start()
        else:
            self.register_node(self.id, self.ip, self.port, self.wallet['address'])
            self.create_genesis_block(n)

    def __reduce__(self):
        return (self.__class__, (self.ip, self.port, self.bootstrap_address, self.capacity, self.is_boot, self.n, True, \
                                 [self.blockchain, self.id, self.wallet, self.ring, self.transactions, self.stakes,     \
                                  self.balances, self.hard_balances, self.nonces, self.node_ready]))


    def set_id(self):
        if self.is_boot:
            return 0
        else: return None
         
    def POS(self, seed):
        lottery_players = []
        for player, stake in enumerate(self.stakes):
            for i in range(stake):
                lottery_players.append(player)
        ###lottery_sum = self.stakes.sum()
        lottery_sum = sum(self.stakes)
        if lottery_sum == 0: return 0
        random.seed(seed)
        winner = random.randint(0, lottery_sum-1)
        validator = lottery_players[winner]
        return validator

    def view_block(self):
        last_block:block.Block = self.blockchain[-1]
        print(f"\nThe validator of the last block was {last_block.validator}")
        print(f"The transactions documented in the last block are presented below.")
        t:transaction.Transaction
        for t in last_block.list_of_transactions:
            print(f"Transaction of {t.type_of_transaction} from node{t.sender_id} to node{t.receiver_id}.\
                    The value of the transaction is {t.value}.\n")


    def mine_block(self):
        last_block = self.blockchain[-1]
        previous_hash = last_block.hash
        seed = previous_hash
        index = last_block.index + 1
        validator = self.POS(seed)
        if (validator == self.id):
            print(f"Node {self.id} is the validator of block {index}.")
            myblock = block.Block(index, validator, previous_hash, self.transactions[:self.capacity].copy())
            self.broadcast_block(myblock)

    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        private_key = key
        public_key = key.publickey()

        # Serialize RSA keys into their string representations
        ser_private_key = key.exportKey().decode('utf-8')
        ser_public_key = public_key.exportKey().decode('utf-8')

        response = {
            'private_key': ser_private_key,
            'address': ser_public_key
        }
        
        return response
        

    def register_node(self, id, ip, port, public_key, balance=0, stake=0):
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

        print(f"Bootstrap added node {id} to ring")

    def create_transaction(self, receiver_id, receiver_address, value, broadcast=True, type_of_transaction='money'):
        my_transaction = transaction.Transaction(
            self.id,
            receiver_id,
            self.wallet['address'], 
            self.wallet['private_key'], 
            receiver_address, 
            value,
            type_of_transaction, 
            self.nonces[self.id],
            )
        #remember to broadcast it
        
        if broadcast:
            self.nonces[self.id] += 1
            print(f"Node {self.id} sends transaction to {receiver_id} with content: {value}.")
            self.broadcast_transaction(my_transaction)
        return my_transaction

    def verify_signature(self, sender_address, hash, signature):
        sender_address = RSA.import_key(sender_address.encode()) # maybe no encoding
        verifier = PKCS1_v1_5.new(sender_address)
        verification = verifier.verify(hash, signature)
        return verification

    def validate_transaction(self, transaction:transaction.Transaction):
        if transaction.type_of_transaction == 'money':
            required_money = transaction.amount*(1+fee)
        elif transaction.type_of_transaction == 'string':
            required_money = transaction.amount
        #use of signature and NBCs balance
        #verify_sign
        #check the balance, do not forget stakes
        isVerify = self.verify_signature(transaction.sender_address, transaction.hash, transaction.signature)
        #!!!money (add later messages)
        sender_id = transaction.sender_id
        receiver_id = transaction.receiver_id
        sender_balance = self.balances[sender_id]
        enough_money = (sender_balance - required_money) >= 0
        #check nonce
        noncesOk = (self.nonces[sender_id] == transaction.nonce or self.id == sender_id)
        combo = isVerify and enough_money and noncesOk
        #allazei to nohma
        if combo:
            print(f"Node {self.id} validates transaction from {sender_id} to {receiver_id} with content: {transaction.value}.") 
            self.balances[sender_id] -= required_money
            if transaction.type_of_transaction == 'money':
                self.balances[receiver_id] += transaction.amount
            if self.id != sender_id: self.nonces[sender_id] += 1
            self.transactions.append(transaction)
            if len(self.transactions) >= self.capacity:
                self.mine_block()
        else: 
            print(f"Node {self.id} does NOT validate transaction from {sender_id} to {receiver_id} with content: {transaction.value}.")
            print(f"Problem: nonces-> {noncesOk}, verify-> {isVerify}, enough_money-> {enough_money}.")
            print(f"Sender node's {sender_id} nonce: {self.nonces[sender_id]}.")
            print(f"Transaction nonce {transaction.nonce}.")

        return combo
    
    
    def stake(self, amount):
        print(f"Node {self.id} is setting the stake to {amount}...")
        threads = []
        for node_info in self.ring:
            thread = threading.Thread(target=self.send_stake, args=(node_info, amount))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def send_stake(self, node_info, amount):
        node_address = (node_info['ip'], node_info['port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_stake = pickle.dumps(('stake', (self.id, amount)))
                sock.sendall(serialized_stake)
        except Exception as e:
            print(f"Error sending stake to {node_address}: {e}")

    
    # Create genesis block
    def create_genesis_block(self, n):
        if(self.id != 0):
            return
        # Create the first block (genesis block)
        # Customize as per your requirements
        #myblock = block.Block(index, validator, previous_hash, self.transactions.copy())
        genesis_block = block.Block(0, 0, 1, [self.create_transaction(-1, 0, 1000*n, broadcast=False)])
        self.balances[0] = 1000*n
        myblockchain = [genesis_block]
        self.validate_chain(myblockchain)
        print("Genesis block is created!")
                    

#    def valid_proof(.., difficulty: MINING_DIFFICULTY):
        
    #consensus functions

    def validate_block(self, block:block.Block):
        last_block = self.blockchain[-1]
        if last_block.index >= block.index:
            print(f"Node {self.id} has already received block {block.index}.")
            return
        previous_hash = last_block.hash
        validator = self.POS(previous_hash)

        validator_correct = (validator == block.validator)
        hash_correct = (previous_hash == block.previous_hash)

        block_correct = validator_correct and hash_correct
        if block_correct:
            print(f"Block {block.index} with validator {block.validator} is checked by node {self.id}.")
            self.blockchain.append(block)
            for t in block.list_of_transactions:
                if t.type_of_transaction == 'money':
                    self.hard_balances[t.receiver_id] += t.amount
                    required_money = t.amount*(1+fee)
                elif t.type_of_transaction == 'string':
                    required_money = t.amount
                self.hard_balances[t.sender_id] -= required_money
                if t.type_of_transaction == 'money':
                    self.hard_balances[validator] += fee*t.amount
                elif t.type_of_transaction == 'string':
                    self.hard_balances[validator] += t.amount
                print("Current transaction value:", t.value)
                print(self.hard_balances)
            self.balances = self.hard_balances.copy()

            '''
            for t2 in self.transactions:    # remove transactions that are already in the blockchain
                if t.hash == t2.hash:
                    self.transactions.remove(t2)
            '''
            self.transactions = []
        else:
            print(f"Block {block.index} is NOT validated by node {self.id}.")
            print(f"Validator: {validator}, Block Validator: {block.validator}.")
            print(f"Previous Hash: {previous_hash}, Block Previous Hash: {block.previous_hash}")

        return block_correct
    

    def validate_chain(self, chain):
        self.hard_balances[0] = 1000*self.n  # since genesis is not validated, we have to add the initial balance to the bootstrap
        self.balances = self.hard_balances.copy()
        self.blockchain.append(chain[0])  # add genesis block to blockchain
        for block in chain[1:]:
            if self.validate_block(block) == False:
                print(f"Node {self.id} does not validate the chain")
                return 
        print(f"Node {self.id} validated the chain correctly!")



    def start_listener(self):
        server_address = (self.ip, self.port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(server_address)
            sock.listen()
            print(f"Node with address {self.port} listening on {server_address}")
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

        if message_type == 'address, ip, port':
            Node.node_id += 1
            #address = RSA.import_key(received_object[0].encode()) # maybe no encoding
            address = received_object[0]
            ip = received_object[1]
            port = received_object[2]
            self.register_node(Node.node_id, ip, port, address)
            print(f"Bootstrap received info from node with ip {ip} and gives to the node the id {Node.node_id}")
            threading.Thread(target=self.send_info_to_nodes((ip, port), Node.node_id))
            self.create_transaction(Node.node_id, address, 1000)
            if Node.node_id == self.n-1:
                self.broadcast_ring()

        elif message_type == 'node_id, bootstrap_blockchain':
            print(f"Node {self.id} received the id and blockchain from bootstrap")
            self.id = received_object[0]
            self.validate_chain(received_object[1])
            self.stakes = received_object[2]
            self.balances = received_object[3]
            self.nonces = received_object[4]
            self.transactions = received_object[5]

        elif message_type == 'transaction':
            self.validate_transaction(received_object)

        elif message_type == 'block':
            print(f"Node {self.id} received block: {received_object.index}.")
            self.validate_block(received_object)
        
        elif message_type == 'ring':
            print(f"Node {self.id} received ring")
            self.ring = received_object
            self.node_ready = True
        
        elif message_type == 'stake':
            id = received_object[0]
            amount = received_object[1]
            total_balance = self.balances[id] + self.stakes[id]
            if amount > total_balance:
                if self.id == id: print(f"Node {id} does not have enough money for the staking :/)")
            else:
                if self.id == id: print(f"Node {id} updates it's stake to {amount}")
                self.stakes[id] = amount
                self.balances[id] = total_balance - amount

        return

    def broadcast_transaction(self, transaction):
        threads = []
        for node_info in self.ring:
            thread = threading.Thread(target=self.send_transaction, args=(node_info, transaction))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def send_transaction(self, node_info, transaction):
        node_address = (node_info['ip'], node_info['port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_transaction = pickle.dumps(('transaction', transaction))
                sock.sendall(serialized_transaction)
        except Exception as e:
            print(f"Error sending transaction to {node_address}: {e}")

    def broadcast_ring(self):
        print(f"Broadcasting ring")
        threads = []
        for node_info in self.ring:
            thread = threading.Thread(target=self.send_ring, args=(node_info, self.ring))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def send_ring(self, node_info, ring):
        node_address = (node_info['ip'], node_info['port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_ring = pickle.dumps(('ring', ring))
                sock.sendall(serialized_ring)
        except Exception as e:
            print(f"Error sending ring to {node_address}: {e}")


    def broadcast_block(self, block):
        print(f"Broadcasting block")
        threads = []
        for node_info in self.ring:
            thread = threading.Thread(target=self.send_block, args=(node_info, block))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def send_block(self, node_info, block):
        node_address = (node_info['ip'], node_info['port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_transaction = pickle.dumps(('block', block))
                sock.sendall(serialized_transaction)
        except Exception as e:
            print(f"Error sending block to {node_address}: {e}")

    def send_wallet_address_to_bootstrap(self, bootstrap_address):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                print(f"Node with ip {self.ip} sends its address to bootstrap")
                sock.connect(bootstrap_address)
                serialized_wallet_address = pickle.dumps(('address, ip, port', (self.wallet['address'], self.ip, self.port)))
                sock.sendall(serialized_wallet_address)
        except ConnectionResetError:
            print("Socket Closed by the other end")
        except Exception as e:
            print(f"Error sending wallet address to bootstrap node at {bootstrap_address}: {e}")

    # Send id from bootstrap to node
    def send_info_to_nodes(self, node_address, id):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node_address)
                serialized_id = pickle.dumps(('node_id, bootstrap_blockchain', (id, self.blockchain, self.stakes, self.balances, self.nonces, self.transactions)))
                sock.sendall(serialized_id)
        except ConnectionResetError:
            print("Socket Closed by the other end")
        except Exception as e:
            print(f"Error sending info to node at {node_address}: {e}")

def process_transactions(node):
    time.sleep(0.5)
    #if node.id == 1: node.stake(100)
    #else: node.stake(10)
    node.stake(10)
    time.sleep(0.5)
    print(f"Balances: {node.balances}")
    start_time = time.time()
    print("Starting timestamp: ", start_time)
    filename = f"./trans{node.id}.txt"
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    receiver_id = int(parts[0][2:])  # Extract the integer part after "id"
                    message = parts[1]  # Extract the string part after the integer
                    receiver_address = node.ring[receiver_id]['address']
                    node.create_transaction(receiver_id, receiver_address, message, True, 'string')
                time.sleep(1)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time - 100
    n = node.n
    blength = len(node.blockchain)
    print(f"Transaction Throuhput: {(n*100)/elapsed_time}")
    print(f"Block Throuhput: {(blength)/elapsed_time}")

if __name__ == "__main__":
    # bootstrap args = [., bootstrap, port, capacity, n]
    # node args = [., ip, port, capacity, n]
    print(sys.argv)
    if len(sys.argv) == 5:
        capacity = int(sys.argv[3])
        n = int(sys.argv[4])
        port = int(sys.argv[2])
        if sys.argv[1] == "bootstrap": is_boot = True 
        else:
            ip = f'{sys.argv[1]}' 
            is_boot = False
        
        bootstrap_address = ('192.168.0.3', 5000) ##83.212.80.198

        if is_boot:
            # Run this block if "bootstrap" argument is provided
            bootstrap_node = Node('192.168.0.3', 5000, bootstrap_address, capacity, is_boot=True, n=n)
            while bootstrap_node.node_ready == False:
                time.sleep(0.0001)
            process_transactions(bootstrap_node)
            time.sleep(5)
            print("--------------------------------------------------------")
            print(f"Balances: {bootstrap_node.balances}")
            print(f"Stakes: {bootstrap_node.stakes}")
            print(f"Blockchain Length: {len(bootstrap_node.blockchain)}")
        else:
            # Run this block if "bootstrap" argument is not provided
            #print(type(ip), type(port))
            node = Node(ip, port, bootstrap_address, capacity, is_boot=False, n=n)
            while node.node_ready == False:
                time.sleep(0.0001)
            process_transactions(node)
            time.sleep(5)
            print("--------------------------------------------------------")
            print(f"Balances: {node.balances}")
            print(f"Stakes: {node.stakes}")
            print(f"Blockchain Length: {len(node.blockchain)}")
    else:
        print("You must give all 4 parameters")
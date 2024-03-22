import block
import wallet
import random
import transaction

from Crypto.Signature import PKCS1_v1_5

capacity = block.capacity

class Node:
    def __init__(self, is_boot = False):
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

    def create_genesis(self):
        pass #broadcast_block

    def send_info(self):
        pass
         
    def POS(self, seed):
        lottery_players = []
        for player, stake in enumerate(self.stakes):
            for i in range(stake):
                lottery_players.append(player)
        lottery_sum = self.stakes.sum()
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
        if (validator == self.id):
            myblock = block.Block(index, validator, previous_hash, self.transactions.copy())
            self.blockchain.append(myblock)
            self.broadcast_block(myblock)
        self.transactions = []


    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet().new_wallet()
        

    def register_node(self, id, ip, public_key, balance, stake):
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking its wallet and ip:port address
        #bootstrap node informs all other nodes and gives the request node an id and 100NBCs.
        if self.id != 0: #if I am not the bootstrap
            print('Oh no, I am not the bootstrap, try again')
            return
        
        #add the node
        self.ring.append({'id' : id,
                          'ip' : ip,
                          'address' : public_key,
                          #'balance' : balance
                        })
        self.balances.append(balance)
        self.stakes.append(stake)
        self.nonces.append(0)

    def create_transaction(self, receiver_address, value):
        my_transaction = transaction.Transaction(
            self.wallet['address'], 
            self.wallet['private_key'], 
            receiver_address, 
            value,
            'money', 
            self.nonces[self.id])
        #remember to broadcast it
        #self.nonces[self.id] += 1
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
            

    # def add_transaction_to_block(self):
        
    def broadcast_transaction(self, transaction):
        return
    
    def broadcast_block(self):
        pass

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
        pass
        #check for the longer chain across all nodes
        
my_node1 = Node()
my_node2 = Node()
my_node_baddie = Node()
my_transaction = my_node1.create_transaction(my_node2.wallet['address'], 10)
verification = my_node2.verify_signature(my_node_baddie.wallet['address'], my_transaction.hash, my_transaction.signature)
print(verification)
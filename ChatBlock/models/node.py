import block
import wallet

class node:
    def __init__(self, is_boot):
        self.NBC=0
        self.blockchain=[]
        self.is_boot = is_boot
        self.id = self.set_id()
        self.wallet = self.create_wallet()
        #ring: here we store info for every node, as its id, its address (ip:port), its public  key and its balance
        self.ring = []
        
    def set_id(self):
        if self.is_boot:
            return 0
        else: return None
         
    def create_new_block(self):
        last_block = self.blockchain[-1]
        previous_hash = last_block.hash
        index = last_block.index + 1


    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet().new_wallet()
        

    def register_node_to_ring(self, id, ip, public_key): #extra arg: balance
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking its wallet and ip:port address
        #bootstrap node informs all other nodes and gives the request node an id and 100NBCs.
        if self.id != 0: #if I am not the bootstrap
            print('Oh no, I am not the bootstrap, try again')
            return
        
        #add the node
        self.ring.append({'id' : id,
                          'ip' : ip,
                          'public_key' : public_key,
                          #'balance' : balance
                        })

    def create_transaction(sender, receiver, signature):
        #remember to broadcast it
    
    def broadcast_transaction():

    def verify_signature():

    def validate_transaction():
        #use of signature and NBCs balance

    def add_transaction_to_block():
        #if enough transactions, mine

    def mine_block():

    def broadcast_block():

    def valid_proof(.., difficulty: MINING_DIFFICULTY):

    #consensus functions

    def valid_chain(self, chain):
        #check for the longer chain across all nodes
        
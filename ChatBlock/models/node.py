import block
import wallet

class node:
    def __init__(self):
        self.NBC=0
        self.chain=[]
        self.id = None
        self.wallet = self.create_wallet()
        #ring: here we store info for every node, as its id, its address (ip:port), its public  key and its balance
        self.ring = []

    def create_new_block():
        pass

    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet()
        

    def register_node_to_ring(self, id, ip, public_key, balance):
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking its wallet and ip:port address
        #bootstrap node informs all other nodes and gives the request node an id and 100NBCs.
        #check if node is bootstrap
        if ()


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
        
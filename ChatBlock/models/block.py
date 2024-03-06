import blockchain
from transaction import Transaction
import wallet
import datetime as date

from collections import OrderedDict
from Crypto.Hash import SHA

capacity = 5

class Block:
    def __init__(self, index, validator, previous_hash):
        ##set
        self.index = index
        #self.previousHash
        self.previous_hash = previous_hash
        #self.timestamp
        self.timestamp = date.datetime.now()
        #self.hash
        self.hash = None 
        #self.listofTransactions
        self.list_of_transactions = []
        self.validator = validator
        self.capacity = capacity
        

    def to_dict(self):
        return OrderedDict({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'validator': self.validator,
            'capacity': self.capacity,
            'list_of_transactions': self.list_of_transactions
            })

    def myHash(self):
        #calculate self.hash
        self.hash = SHA.new(str(self.to_dict).encode("utf-8")).hexdigest()
    
    def add_transaction(self, transaction): #add a blockchain parameter
        #add a transaction to the block
        if len(self.list_of_transactions) == capacity:
            print("the max capacity is reached: ", capacity)
            return
        self.list_of_transactions.append(transaction)
        if len(self.list_of_transactions) == capacity:
            self.myHash()

my_wallet = wallet.Wallet()
key = my_wallet.new_wallet()['private_key']

my_transaction = Transaction(1, key, 2, 6, 'blue', 3)

my_block = Block(1, 2, 4)

for i in range(4):
    my_block.add_transaction(my_transaction)

print(my_block.hash)
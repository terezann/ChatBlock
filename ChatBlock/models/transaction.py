from collections import OrderedDict

import binascii
import wallet

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, value, type_of_transaction, nonce):

        #set
        self.type_of_transaction = type_of_transaction
        self.nonce = nonce
        #self.sender_address: Το public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address
        #self.receiver_address: Το public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = receiver_address
        #self.amount: Το ποσό που θα μεταφερθεί
        self.amount = value
        #self.transaction_id: Το hash του transaction
        self.hash = SHA.new(str(self.to_dict).encode("utf-8"))
        self.transaction_id = self.hash.hexdigest()
        #self.signature με το private key
        self.signature = self.sign_transaction(sender_private_key)


    def to_dict(self):
        return OrderedDict({
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'amount': self.amount,
            'type_of_transaction': self.type_of_transaction,
            'nonce': self.nonce
            #'time' : self.time
            })

    def sign_transaction(self, private_key):
        #sign transaction with private key
        #private_key = RSA.importKey("mytext".encode("utf-8"))
        signer = PKCS1_v1_5.new(private_key)
        signature = signer.sign(self.hash)
        return signature

#sender_private_key = "3081a7301006072a8648ce3d020106052b8104002203620004bb39e0e3d69e6b8d20d8c5a888c7811b7c9d1be4ee08d1ed2b6ee740e2e3dd400220d5e52ef89eeb4bc899ad08d25e50d1b090981c300fbc7fc07515d7330af39e5"
#sender_public_key = "30820122300d06092a864886f70d01010105000382010f003082010a0282010100bf93bbf1e6a9eb511575cc15c4c0784a74a8ef3521db0150e3c9e468535de3a9b7f4745c68e693ef3e7716934a3ebf7d21dbf2f65eb239876b2fcab1192850d282153f5ab9d39b0f3ee0e6a7f4b964c9ff74a565f55ef97d10667f34c723c9c9c687c39f3c9e7258a2d0d189b85a7069de12789e81f361a26b29d0e9d01241a104308c8998f628bc4b858b67a9de57f122e5e20ad9f23d670808a604eaa96e6aeb362c99f16868461f8d14749d8f33a6cb7a26af3c01f18e5fb5efdf3a8fe108fd991f39fe82f262d690f079b208d7b44c80d8e87127636d774c67a2e762ac844e245f0203010001"
#receiver_address = "30819f300d06092a864886f70d010101050003818d0030818902818100c6e4bbac1505a5e7f3b19978b4a7db6d7006873e825acbb3b36dcb31c9b33c72558c7c7aa3b7259ff2eb0d1320c0f597019ae1a870ef69d1bcf1e26a03b130af1ee5ddc77bc5835d0f4084cc88ef55a124d5ef565b2b57ef6f5b33f1a4b259a47b7a5ff29e57a8cc520db6730b2a9c49d84f53e1a91c3c4ff180145b11022100bc050f1361d0f4247e35bb3e86dd74100e5c4219efdc14172a7915167f53bbd8e5022100c29d92b48a896d5f6cd6f97ec2c5c8e20236555b9f3c91c81a1550b7a2a9ec11022100a136205b6f69480e0f85a38c94468f010c3072a2c7e4d4df8a1bbd558d8d4aa022100a758d4392ac0b2e750c8cd9bb11b1be07e02c60a8920e08d399a7e0a4e7316f3022100de5d0d90703e97c030ae3f61b03c4f468e36914201c7a99c34e2b68881017fcf"

# my_wallet = wallet.Wallet()
# key = my_wallet.new_wallet()['private_key']

# my_transaction = Transaction(1, key, 2,6)
# print(my_transaction.signature)


from binascii import hexlify, unhexlify
from collections import OrderedDict

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Wallet:
    def __init__(self):
        self.i = 0

    def new_wallet(self):
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        private_key = key 
        public_key = key.publickey()

        response = {
            'private_key': private_key,
            'address': public_key
        }
        
        return response
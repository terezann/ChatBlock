from binascii import hexlify, unhexlify
from collections import OrderedDict

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

random_gen = Random.new().read
key = RSA.generate(1024, random_gen)

prk = key.exportKey(format='DER')
puk = key.publickey().exportKey(format='DER')

response = {'private_key': hexlify(prk).decode('ascii'),
            'address': hexlify(puk).decode('ascii'),
            #'balance': self.balance,
            }
print(response)
from ocb.aes import AES
from ocb import OCB

aes = AES(128)
ocb = OCB(aes)

key = bytearray().fromhex('A45F5FDEA5C088D1D7C8BE37CABC8C5C')
ocb.setKey(key)

nonce = bytearray(range(16))
ocb.setNonce(nonce)

header = bytearray('Recipient: wabesasa@gmail.com')

f = open('data/tag', 'r')
tag = bytearray(f.read().replace('\n', ''))

f = open('data/ciphertext', 'r')
ciphertext = bytearray(f.read().replace('\n', ''))

(is_authentic, plaintext) = ocb.decrypt(header, ciphertext, tag)
print('Plaintext: ' + plaintext)

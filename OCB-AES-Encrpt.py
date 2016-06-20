from ocb.aes import AES
from ocb import OCB
import struct

aes = AES(128)
ocb = OCB(aes)

key = bytearray().fromhex('A45F5FDEA5C088D1D7C8BE37CABC8C5C')
ocb.setKey(key)

nonce = bytearray(range(16))
ocb.setNonce(nonce)

text = raw_input("Press Enter the plaintext...\n")

plaintext = bytearray(text)
header = bytearray('Recipient: wabesasa@gmail.com')

(tag,ciphertext) = ocb.encrypt(plaintext, header)

f = open('data/tag','w')
f.write(tag)
f.close()

f = open('data/ciphertext','w')
f.write(ciphertext)
f.close()


print('Encrypttion is done...Please check files...and you can decrypt...\n')

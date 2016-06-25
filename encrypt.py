from ocb.aes import AES
from ocb import OCB
import struct

aes = AES(128)
ocb = OCB(aes)

key = bytearray().fromhex('A45F5FDEA5C088D1D7C8BE37CABC8C5C')
ocb.setKey(key)

header = bytearray('Recipient: wabesasa@gmail.com')
 
class Encrypt:
    def __init__(self):
        self.code = 'Yee please do not go!!!'  
        self.tag = ''
        self.ciphertext = ''
     
    def __str__(self):
        return "Test Plaintext: " + "".join(self.code)
     
    def setCiphertext(self, data):
        self.ciphertext = bytearray(list(data))

    def setTag(self, data):
        self.tag = bytearray(list(data))
 
    def getCiphertext(self):
        return self.ciphertext

    def getTag(self):
        return self.tag
    
    def toEncode(self, s):
        plaintext = bytearray(s)
        nonce = bytearray(range(16))
        ocb.setNonce(nonce)
        (tag,ciphertext) = ocb.encrypt(plaintext, header)
        self.tag = tag
        self.ciphertext = ciphertext
        print('Ciphertext: ' + ciphertext)
        print('Tag: ' + tag)
     
        return (ciphertext, tag)
     
    def toDecode(self, s1, s2):
        ciphertext = bytearray(s1)
        tag = bytearray(s2)
        nonce = bytearray(range(16))
        ocb.setNonce(nonce)
        (is_authentic, plaintext) = ocb.decrypt(header, ciphertext, tag)
        print(ciphertext)
        print(tag)
        print('is_authentic?')
        print(is_authentic);
        print('Plaintext: ' + plaintext)

        return plaintext
 
if __name__ == '__main__':
    e = Encrypt()
    print()
    print(e)
    s1 = "There is no spoon."
    print("input: " + s1)
    s2 = e.toEncode(s1)
    print("encode: " + s2[0])
    s3 = e.toDecode(s2[0], s2[1])
    print("decode: " + s3)
    print()
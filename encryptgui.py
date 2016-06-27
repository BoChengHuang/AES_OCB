import sys
sys.path.append('\\Program Files\\Python\\Lib\\python27.zip\\lib-tk')
from Tkinter import *
from encrypt import Encrypt
import socket
import os
 
class EncryptGUI(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.e = None
        self.userinput = ""
        self.result = ""
        self.isRecv = False
        self.isAuth = False
        self.recvKey = ""

        self.e = Encrypt() 
        self.displayText["text"] = self.e
        print("Current key is: " + self.e.key)
 
    def createWidgets(self):
        self.inputText = Label(self)
        self.inputText["text"] = "Input:"
        self.inputText.grid(row=0, column=0)
        self.inputField = Entry(self)
        self.inputField["width"] = 80
        self.inputField.grid(row=0, column=1, columnspan=6)
 
        # self.outputText = Label(self)
        # self.outputText["text"] = "Output:"
        # self.outputText.grid(row=1, column=0)
        # self.outputField = Entry(self)
        # self.outputField["width"] = 50
        # self.outputField.grid(row=1, column=1, columnspan=6)
         
        # self.new = Button(self)
        # self.new["text"] = "Load EncrytFunction"
        # self.new.grid(row=2, column=0)
        # self.new["command"] =  self.newMethod
        self.load = Button(self)
        self.load["text"] = "Load from server"
        self.load.grid(row=2, column=1)
        self.load["command"] =  self.loadMethod
        self.save = Button(self)
        self.save["text"] = "Save to Server"
        self.save.grid(row=2, column=2)
        self.save["command"] =  self.saveMethod
        self.encode = Button(self)
        self.encode["text"] = "Encode"
        self.encode.grid(row=2, column=3)
        self.encode["command"] =  self.encodeMethod
        self.decode = Button(self)
        self.decode["text"] = "Decode from files"
        self.decode.grid(row=2, column=4)
        self.decode["command"] =  self.decodeMethod
        self.clear = Button(self)
        self.clear["text"] = "Clear"
        self.clear.grid(row=2, column=5)
        self.clear["command"] =  self.clearMethod
        self.copy = Button(self)
        self.copy["text"] = "Copy"
        self.copy.grid(row=2, column=6)
        self.copy["command"] =  self.copyMethod
        self.auth = Button(self)
        self.auth["text"] = "Auth"
        self.auth.grid(row=2, column=7)
        self.auth["command"] =  self.authFromServer
 
        self.displayText = Label(self)
        self.displayText["text"] = "something will happen."
        self.displayText.grid(row=3, column=0, columnspan=7)
     
    def newMethod(self):
        self.e = Encrypt() 
        self.displayText["text"] = self.e
 
    def loadMethod(self):
        if os.path.exists("./data/tag.txt"):
            f = open('./data/tag.txt', 'r')
            code = f.readline()
            #self.e = Encrypt()
            self.e.setTag(code)
            self.displayText["text"] = "Tag includeed!"

            if os.path.exists("./data/ciphertext.txt"):
                f = open('./data/ciphertext.txt', 'r')
                code = f.readline()
                self.e.setCiphertext(code)
                self.displayText["text"] = "Ciphertext includeed!"

        else:
            self.displayText["text"] = "Load denied!!"
        self.getCiphertextTag()
        self.e.setKey(self.recvKey)
 
    def saveMethod(self):
        
        if self.e == None:
            self.displayText["text"] = "No Encrypt object can save!!"
        else:
            f = open('./data/ciphertext.txt', 'w')
            f.write(self.e.getCiphertext())
            f.closed

            f = open('./data/tag.txt', 'w')
            f.write(self.e.getTag())
            f.closed

            self.displayText["text"] = "The code is saved."
            self.sendCiphertextTag(self.e.getCiphertext(), self.e.getTag())
 
    def encodeMethod(self):
        self.userinput = self.inputField.get()
         
        if self.userinput == "":
            self.displayText["text"] = "No input string!!"
        else:
            if self.e == None:
                self.displayText["text"] = "No encrypt object!!"
            else:
                self.result = self.e.toEncode(self.userinput)
                self.displayText["text"] = "Encrypt successful!!"
         
 
    def decodeMethod(self):
        self.userinput = self.inputField.get()
        
        if self.userinput == "":
            if self.isRecv:
                self.result = self.e.toDecode(self.e.ciphertext, self.e.tag)
                self.displayText["text"] = self.result
            else :
                self.displayText["text"] = "No input string!!"
        else:
            if self.e == None:
                self.displayText["text"] = "No encrypt object!!"
            else:
                self.result = self.e.toDecode(self.e.ciphertext, self.e.tag)
                self.displayText["text"] = self.result
 
    def clearMethod(self):
        self.e = None
        self.userinput = ""
        self.result = ""
        self.inputField.delete(0, 200)
        #self.outputField.delete(0, 200)
 
        self.displayText["text"] = "It's done."
 
    def copyMethod(self):
        if self.result == "":
            self.displayText["text"] = "Copy denied!!"
        else:
            self.clipboard_clear()
            self.clipboard_append(self.result)
            self.displayText["text"] = "It is already copied to the clipboard."

    def getCiphertextTag(self):
        if self.isAuth:

            TCP_IP = "140.118.155.49"
            TCP_PORT = 9000
            BUFFER_SIZE = 1024

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            with open('data/ciphertext.txt', 'wb') as f:
                print 'file opened'
                while True:
                    #print('receiving data...')
                    data = s.recv(BUFFER_SIZE)
                    print('data=%s', (data))
                    if not data:
                        f.close()
                        print 'file close()'
                        break
                    # write data to a file
                    f.write(data)

            s.close()
            print('Successfully get the ciphertext file, connection closed...')

            TCP_PORT = 9001
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            with open('data/tag.txt', 'wb') as f:
                print 'file opened'
                while True:
                    #print('receiving data...')
                    data = s.recv(BUFFER_SIZE)
                    print('data=%s', (data))
                    if not data:
                        f.close()
                        print 'file close()'
                        break
                    # write data to a file
                    f.write(data)

            s.close()
            print('Successfully get the tag file, connection closed...')
            self.isRecv = True
        else :
            self.displayText["text"] = "You don't have the right to use."
    
        
    def sendCiphertextTag(self, s1, s2):
        if self.isAuth:
            s = socket.socket()             # Create a socket object
            host = '140.118.155.49'     # Get local machine name
            port = 9002                    # Reserve a port for your service.

            s.connect((host, port))
            s.send(s1)

            s.close()
            print('Successfully send the ciphertext file, connection closed...')

            s = socket.socket()             # Create a socket object
            host = '140.118.155.49'     # Get local machine name
            port = 9003                   # Reserve a port for your service.

            s.connect((host, port))
            s.send(s2)

            s.close()
            print('Successfully send the tag file, connection closed...')
            self.sendKeyToServer()
        else :
            self.displayText["text"] = "You don't have the right to use."
        

    def authFromServer(self):
        TCP_IP = "140.118.155.49"
        TCP_PORT = 9004
        BUFFER_SIZE = 1024

        header = self.e.header
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(header)

        data = s.recv(1024)
        print(data)
        if data != "Not Authenticated":
            self.displayText["text"] = "Authenticated!!"
            self.recvKey = data
            self.isAuth = True
        else :
            self.displayText["text"] = "You are a bad guy!!"
        s.close()
        print("Current key is: " + self.e.key)
        
    def sendKeyToServer(self):
        s = socket.socket()             # Create a socket object
        host = '140.118.155.49'     # Get local machine name
        port = 9005                   # Reserve a port for your service.

        s.connect((host, port))

        s.send(self.e.key)

        msg = s.recv(1024)
        s.close()
        print(msg)
        


if __name__ == '__main__':
    root = Tk()
    app = EncryptGUI(master=root)
    app.master.title('802.11i by AES in OCB')
    app.mainloop()
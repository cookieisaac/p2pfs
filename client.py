from xmlrpclib import ServerProxy, Fault
from string import lowercase
from random import choice
from cmd import Cmd
from node import Node, UNHANDLED
from threading import Thread
from time import sleep
import sys

SECRET_LENGTH = 100
HEAD_START = 0.1 #Seconds

def randomString(length):
    chars = []
    letters = lowercase[:26]
    while length > 0:
        length -= 1
        chars.append(choice(letters))
    return ''.join(chars)
    
class Client(Cmd):
    prompt = '>'
    
    def __init__(self, url, dirname, urlfile):
        Cmd.__init__(self)
        self.secret = randomString(SECRET_LENGTH)
        node = Node(url, dirname, self.secret)
        thread = Thread(target=node._start)
        thread.setDaemon(1)
        thread.start()
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        for line in open(urlfile):
            line = line.strip()
            self.server.hello(line)
            
    def do_fetch(self, arg):
        try:
            self.server.fetch(arg, self.secret)
        except Fault as f:
            if f.faultCode != UNHANDLED:
                raise
            print("Couldn't find the file %s" % arg)
        
    def do_exit(self, arg):
        print("Exit the program")
        sys.exit()
        
    do_EOF = do_exit
    
    def do_hello(self, url):
        self.server.hello(url)
        
def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()
    
if __name__ == '__main__':
    main()
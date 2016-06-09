import logging
import sys
from xmlrpclib import ServerProxy
from os.path import join, isfile
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse

OK = 1
FAIL = 2
EMPTY = ''
MAX_HISTORY_LENGTH = 6

def getPort(url):
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])

class Node:
                
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()
        
    def query(self, query, history=[]):
        '''
        Look for a file by asking neighbours, and return it as a string
        '''
        code, data = self._handle(query)
        if code == OK:
            return code, data
        else:
            history = history + [self.url]
            if len(history) >= MAX_HISTORY_LENGTH:
                return FAIL, EMPTY
            return self._broadcast(query, history)
        
    def fetch(self, query, secret):
        '''
        If the secret is correct, perform a regular query and store
        the file, a.k.a, make the Node find the file and download it.
        '''
        if secret != self.secret:
            return FAIL
        code, data = self.query(query)
        if code == OK:
            f = open(join(self.dirname, query), 'w')
            f.write(data)
            f.close()
            return OK
        else:
            return FAIL

    def hello(self, other):
        '''
        Add the otehr Node as known peers
        '''
        self.known.add(other)
        return OK
        
    def _start(self):
        s = SimpleXMLRPCServer(("", getPort(self.url)), logRequests=False)
        s.register_instance(self)
        s.serve_forever()
        
    def _handle(self, query):
        dir = self.dirname
        name = join(dir, query)
        if not isfile(name):
            return FAIL, EMPTY
        return OK, open(name).read()
        
    def _broadcast(self, query, history):
        for other in self.known.copy():
            if other in history:
                continue
            try:
                s = ServerProxy(other)
                code, data = s.query(query, history)
                if code == OK:
                    return code, data
            except:
                self.known.remove(other)
        return FAIL, EMPTY
        
def main():
    logging.basicConfig(filename="node.log", level=logging.DEBUG, format='[%(asctime)s ][%(levelname)s][%(message)s]', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    url, directory, secret = sys.argv[1:]
    n = Node(url, directory, secret)
    n._start()
    
if __name__ == '__main__':
    main()
    
    
import time #strftime()
import os #getcwd()
import socket #gethostname()
import sys
import logging
from cloghandler import ConcurrentRotatingFileHandler
from xmlrpclib import ServerProxy, Fault
from os.path import join, isfile, abspath
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse


MAX_HISTORY_LENGTH = 6

OK = 0
UNHANDLED = 100
ACCESS_DENIED = 200

SimpleXMLRPCServer.allow_reuse_address = 1

class UnhandledQuery(Fault):
    def __init__(self, message="Couldn't handle the query"):
        Fault.__init__(self, UNHANDLED, message)
        
class AccessDenied(Fault):
    def __init__(self, message="Access denied"):
        Fault.__init__(self, ACCESS_DENIED, message)
        
def inside(dir, name):
    """
    Check whether a given file name lies within a given directory
    Prevent case such as dir="/Shared/Owned/", name="../secret.file"
    """
    dir = abspath(dir)
    name = abspath(name)
    return name.startswith(join(dir,''))

def getPort(url):
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])

class Node:
                
    def __init__(self, url, dirname, secret):
        log_level = logging.DEBUG 
        log_dir = os.getcwd()
        log_max_size = 78 * 1024 * 1024
        log_max_rotate = 9
        
        LOG_LONG_FORMAT = '[%(module)s][%(funcName)s][%(lineno)d][%(levelname)s][%(message)s]'
        LOG_RECORD_TIME = '[%(asctime)s]'
        LOG_ROOT_NAME = 'server-node.log'
        
        log = logging.getLogger()
        log_format = LOG_RECORD_TIME + \
                    '[' + time.strftime("%Z", time.localtime()) + ']' + \
                    '[%(process)d]' + \
                    LOG_LONG_FORMAT
        log_name = LOG_ROOT_NAME + '.' + str(socket.gethostname())
        log_file = os.path.join(log_dir, log_name)
        rotate_handler = ConcurrentRotatingFileHandler(log_file, mode="a",
           maxBytes=log_max_size, backupCount=log_max_rotate)
        formatter = logging.Formatter(log_format)
        rotate_handler.setFormatter(formatter)
        log.addHandler(rotate_handler)
        log.setLevel(log_level)
        logging.info('Logging level has been set to DEBUG mode')
        logging.info('New node started with url <{}> serving directory <{}> with secret<{}>'.format(url, dirname, secret))
    
        #log_file = "server-node.log"
        #logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s ][%(levelname)s][%(message)s]', datefmt='%m/%d/%Y %I:%M:%S %p')

        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()
        
    def query(self, query, history=[]):
        '''
        Look for a file by asking neighbours, and return it as a string
        '''
        try:
            logging.debug("Current query in function query() is {} with history {}".format(query, history))
            return self._handle(query)
        except UnhandledQuery:
            history = history = [self.url]
            if len(history) >= MAX_HISTORY_LENGTH:
                raise
            return self._broadcast(query, history)
        
    def fetch(self, query, secret):
        '''
        If the secret is correct, perform a regular query and store
        the file, a.k.a, make the Node find the file and download it.
        '''
        if secret != self.secret:
            raise AccessDenied
        result = self.query(query)
        f = open(join(self.dirname, query), 'w')
        f.write(result)
        f.close()
        return OK

    def hello(self, other):
        '''
        Add the other Node as known peers
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
        logging.debug("Current dir is <{}> and final resolved name is <{}>".format(dir, name))
        if not isfile(name):
            logging.warning("<{}> is not a file".format(name))
            raise UnhandledQuery
        if not inside(dir, name):
            logging.warning("<{}> is not inside <{}>".foramt(name, dir))
            raise AccessDenied
        return open(name).read()
        
    def _broadcast(self, query, history):
        for other in self.known.copy():
            if other in history:
                continue
            try:
                s = ServerProxy(other)
                return s.query(query, history)
            except Fault as f:
                if f.faultCode == UNHANDLED:
                    pass
                else:
                    self.known.remove(other)
            except:
                self.known.remove(other)
        raise UnhandledQuery

def unittest():
    n = Node('http://localhost:4242', 'test/peer2', 'secret1')
    n.fetch('test.txt', 'secret1')
    
def main():    
    url, directory, secret = sys.argv[1:]
    n = Node(url, directory, secret)
    n._start()
    
if __name__ == '__main__':
    #unittest()
    main()
    
    
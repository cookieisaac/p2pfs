# p2pfs

A simple peer-to-peer file sharing system based on Python standard library `xmlrpclib`

## Usage

### 
Node 1 
```bash
mkdir -p test/peer1
python node.py http://localhost:4242 test/peer1 secret1
```

Node 2
```bash
mkdir -p test/peer2
echo "Test string from peer2" >> test/peer2/test.txt
python node.py http://localhost:4243 test/peer2 secret2
```

Node 3
```python
from xmlrpclib import *
mypeer = ServerProxy('http://localhost:4242')
code, data = mypeer.query('test.txt')
mypeer2 = ServerProxy('http://localhost:4243')
code, data = mypeer2.query('test.txt')
```


### Barebone
Node1 | Node2
--- | ---
>>> from SimpleXMLRPCServer import SimpleXMLRPCServer | >>> from xmlrpclib import ServerProxy
>>> s = SimpleXMLRPCServer(("", 4242)) | >>> s = ServerProxy('http://ikeblue3:4242')
>>> def twice(x): | >>> s.twice(4)
...     return x*2 | 8
... |  
>>> s.register_function(twice) |  
>>> s.serve_forever() |  
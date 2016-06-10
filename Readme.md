# p2pfs

A simple peer-to-peer file sharing system based on Python standard library `xmlrpclib`

## Usage

### Demo
In the first console, launch `peer1` 

```bash
mkdir -p test/peer1
python node.py http://localhost:4242 test/peer1 secret1
```

In the second console, launch `peer2`

```bash
mkdir -p test/peer2
echo "Test string from peer2" >> test/peer2/test.txt
python node.py http://localhost:4243 test/peer2 secret2
```

In the third console, open an interactive Python shell

```python
#Connect to peer1 and fail to retrieve data
from xmlrpclib import *
mypeer1 = ServerProxy('http://localhost:4242')
code, data = mypeer1.query('test.txt')

#Connect to peer2 and succeed in retrieving data
mypeer2 = ServerProxy('http://localhost:4243')
code, data = mypeer2.query('test.txt')

#Introduce peer2 to peer1 and succeed in retrieving data
mypeer1.hello('http://localhost:4243')
code, data = mypeer1.query('test.txt')

#Download test file from peer2 to peer1
mypeer1.fetch('test.txt', 'secret1')
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
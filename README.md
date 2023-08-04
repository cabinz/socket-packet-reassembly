# Packet Reassembly Problem

In socket-level network programming, two common challenges that can arise are the packet coalescing and the fragmentation. These two challenges are collectively referred to as packet reassembly problem, for requiring receiver side to reassemble the packets received to solve them. 

## Packet Coalescing Problem

Packet coalescing occurs when multiple small packets sent from the sender side are combined or merged into a single larger packet before reaching the receiver side.
This can happen due to network optimizations, such as TCP/IP offloading or hardware-level packet aggregation.

Run the `naive_server.py` and then `naive_client.py` in the repo to observe the coalescing problem on the server side. Logs on your console may be similar to the one as below:
```
Server started at localhost:31974 with buffer size 1024.
Connected to 127.0.0.1:53698.
Receive:  b'Sending interval = 1s'
Receive:  b'Msg 0 from client.'
Receive:  b'Msg 1 from client.'
Receive:  b'Msg 2 from client.'
Receive:  b'Msg 3 from client.'
Receive:  b'Msg 4 from client.'
Receive:  b'Sending interval = 1e-06s'
Receive:  b'Msg 0 from client.Msg 1 from client.'
Receive:  b'Msg 2 from client.Msg 3 from client.'
Receive:  b'Msg 4 from client.'
Receive:  b'Sending interval = 0s'
Receive:  b'Msg 0 from client.Msg 1 from client.Msg 2 from client.Msg 3 from client.Msg 4 from client.'
Received a null msg, socket has been closed on remote end.
```

The smaller the sending interval from the client is, the more serious packet coalescing will take place. All the message sent separately will be unexpectedly merged together end retrieved by a single socket `.recv()`.

## Fragmentation Problem

Fragmentation occurs when the data sent from the sender (client) side exceeds the reading buffer size of `.recv()`, or the maximum transmission unit (MTU) size allowed by the underlying network infrastructure.
This will cause an incomplete message returns from a single call of  `.recv()`.

To observe fragmentation problem, change the code of `naive_server.py` to use the smaller recv buffer size `SMALL_RECV_BUF_SIZE`, and run the naive versions of server and client.
```

Server started at localhost:31974 with buffer size 10.
Connected to 127.0.0.1:53762.
Receive:  b'Sending in'
Receive:  b'terval = 1'
Receive:  b's'
Receive:  b'Msg 0 from'
Receive:  b' client.'
Receive:  b'Msg 1 from'
Receive:  b' client.'
Receive:  b'Msg 2 from'
Receive:  b' client.'
Receive:  b'Msg 3 from'
Receive:  b' client.'
Receive:  b'Msg 4 from'
Receive:  b' client.'
Receive:  b'Sending in'
...
Receive:  b' client.'
Received a null msg, socket has been closed on remote end.
```

The message retrieved by each `.recv()` call can be a segment chopped from the original one.

As the successful case before modifying the buffer size hints, increasing the socket's send buffer and receive buffer sizes may help to prevent fragmentation. 
However, increasing the buffer size is to blindly allocate more memory resources on the receiving (server) side whenever a message needs to be received, while the actual message being transmitted may not always be a huge one.
This may bring heavy memory resource consumption especially if the data volume or the number of connections is high.


# Solutions

To solve both problems mentioned above, common strategies are to implement an application-level packet transmission protocol (agreed by both the server and client) for buffering and reassembling the packets received by socket. 

The application-level protocol should be able to detect and handle packet coalescing by using packet headers or delimiters to separate individual message units.
For example, techniques like message framing, where message units are encapsulated with headers indicating the size or sequence information to ensure proper reassembly at the receiver's end, allowing for more precise control over how the data is divided into packets logically and reassembled, which also reduces the need for large buffer sizes.

The repo contains a simple implementations of framing transmission protocol based on delimiter. Run `delimiter_server.py` and `delimiter_client.py` to check its effects:
```
Server started at localhost:31974. Buffer size = 1024.
Connected to 127.0.0.1:54052.
Receive:  b'Sending interval = 1s'
Receive:  b'Message 0 from client.'
Receive:  b'Message 1 from client.'
Receive:  b'Message 2 from client.'
Receive:  b'Message 3 from client.'
Receive:  b'Message 4 from client.'
Receive:  b'Sending interval = 1e-06s'
Receive:  b'Message 0 from client.'
Receive:  b'Message 1 from client.'
Receive:  b'Message 2 from client.'
Receive:  b'Message 3 from client.'
Receive:  b'Message 4 from client.'
Receive:  b'Sending interval = 0s'
Receive:  b'Message 0 from client.'
Receive:  b'Message 1 from client.'
Receive:  b'Message 2 from client.'
Receive:  b'Message 3 from client.'
Receive:  b'Message 4 from client.'
Socket has been closed on remote end.
```

All the messages from client side can be correctly retrieved in order, no matter what sending interval of the sending side or what receive buffer size of the receiver side (the recv buffer can be changed to be smaller for observation).

The delimiter separating consecutive messages being transmitted is `DELIM` defined in the `config.py` file, which is shared by the server and client. Note that every occurrence of delimiter in the actual message content should be encoded somehow on the sender side, and then be decoded in the receiver side, otherwise message may be wrongly chopped up.

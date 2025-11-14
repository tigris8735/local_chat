# local_chat

## **about this repo/project**
 wanted to try to create a local chat for two people with end-to-end encryption, 
 where the first user is the server and the second is the client.
The second one connects to the server via a local network and can communicate with each other without fear of being overheard .

## **structure**
```
secure_chat/
├── requirements.txt
├── crypto_utils.py
├── network_utils.py
├── server_client.py
└── client.py
```
when:
- crypto_utils.py - is the file for setting up encryption
- network_utils.py - is a file for working with ports and connection
- server_client.py - is the server file , as well as the first client file
- client.py - is the client file
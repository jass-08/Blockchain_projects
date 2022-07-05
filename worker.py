# /**
#  * worker.py
#  * COMP 3010
#  * INSTRUCTOR : Robert Guiderian
#  *
#  * @author Jaspreeet Singh, 7859706
#  * @version 26th may,2022
#  * PURPOSE: The Purpose of this class is to make a 
#   a tcp for server that holds the database for our clients
#  **/
import socket
import sys
import json
import time
HOST = ''                           # Symbolic name meaning all available interfaces
PORT = int(sys.argv[1])             # non-privileged port assigned from the arguments provided
 
Database = {}                        #dictionary to store our database we can use get/set on it
def setDictionary(key,value):
    print("Got request for SETTING key and value: ", key, value)
    if key in Database:
        print("KEY already set")
        return { "type": "SET-RESPONSE", "success": False}
    else:
        Database[key] = value
        return { "type": "SET-RESPONSE", "success": True}
def getDictionary(key):
    if key in Database:
        print("Got request for GETTING value at key: ", key)
        result=Database.get(key)
        return { "type": "GET-RESPONSE", "key": key, "value": result}
    else:
        print("KEY NOT FOUND IN DATABASE")
        return { "type": "GET-RESPONSE", "key": key, "value": None}

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print("Worker Started at Port: "+sys.argv[1])
print("Timeout set to 60 everytime")
while True:
    try:
        conn, addr = s.accept()
        print('Connected by', addr)
        while True:
            conn.settimeout(60)
            query = conn.recv(1024)
            data=json.loads(query)
            if data['type']=='GET':
                myvalue=getDictionary(data['key'])
                myvalueJson=json.dumps(myvalue).encode()
                conn.sendall(myvalueJson)
            if data['type']=='SET':
                myResponse=setDictionary(data['key'],data['value'])
                myResponseJson=json.dumps(myResponse).encode()
                conn.sendall(myResponseJson)
    except socket.timeout as e:
        pass
    except KeyboardInterrupt as e:
        print("RIP")
        sys.exit(0)
    except Exception as e:
        print("Something happened... I guess...")
        print(e)
 

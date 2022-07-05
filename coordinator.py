# /**
#  * coordinatoy.py
#  * COMP 3010
#  * INSTRUCTOR : Robert Guiderian
#  *
#  * @author Jaspreeet Singh, 7859706
#  * @version 26th may,2022
#  * PURPOSE: The Purpose of this assignment is to make a 
#   2 phase commit database between serveral clients and serveral servers with 
#   having a coordiantor client/server in between
#  **/
import json
import socket
import sys
import select
import random
HOST = ''                           # Symbolic name meaning all available interfaces
PORT = int(sys.argv[1])             # non-privileged port assigned from the arguments provided

# Setting up serverSocket for clients
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((HOST, PORT))
serverSocket.listen()
print("Coordinator successfuly started at port: "+sys.argv[1])

workerSocket=[]                     #List of all the worker Sockets

#For workers provided through arguments 2 to m
for i in range(2,len(sys.argv)):
    try:
        #connect to the workers
        workerinfo=sys.argv[i].split(":")
        newWorker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newWorker.connect((workerinfo[0], int(workerinfo[1])))
        workerSocket.append(newWorker)          
    except KeyboardInterrupt as e:
        print("RIP")
        sys.exit(0)
    except Exception as e:
        print("Something happened in the for LOOPP!!!... ")
        print(e)

#lists for select
myReadables = [serverSocket, ] # not transient
myWriteables = []
myClients = [] # are transient

while True:
    try:
        readable, writeable, exceptions = select.select(
            myReadables + myClients+workerSocket,
            myWriteables,
            myReadables,
            5
        )
        for eachSocket in readable:
            if eachSocket is serverSocket:              # accept new client and append to the list
                # new client
                conn, addr = serverSocket.accept()
                print('Connected by', addr)
                myClients.append(conn)  
            elif eachSocket in myClients:               # recieve the queries and forward them to workers appropriately
                query = eachSocket.recv(1024)
                data=json.loads(query)
                if data:
                    print("Query recieved:")
                    print(data)
                    if(data['type']=='GET'):
                        myRandom=random.randint(0,len(workerSocket)-1)
                        workerSocket[myRandom].sendall(query)
                    elif(data['type']=='SET'):
                        for worker in workerSocket:
                            worker.sendall(query)
                else:
                    myClients.remove(eachSocket)
            elif eachSocket in workerSocket:            # accept requests and act on them appropriately
                newData=eachSocket.recv(1024)
                for client in myClients:
                    client.sendall(newData)

                
        for problem in exceptions:
            # ... probably a client socket
            print("has problem")
            if problem in myClients:
                myClients.remove(problem)

    except socket.timeout as e:
        print('timeout')
        pass
    except KeyboardInterrupt as e:
        print("RIP")
        serverSocket.close()
        sys.exit(0)
    except Exception as e:
        print("Something happened... I guess...")
        print(e)


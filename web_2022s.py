# /**
#  * web_2022s.py
#  * COMP 3010
#  * INSTRUCTOR : Robert Guiderian
#  *
#  * @author Jaspreeet Singh, 7859706
#  * @version 6th June,2022
#  * PURPOSE: The Purpose of this class is to make a 
#   multi threaded web server that takes input using xml files
#   
#   Notes: I print something in each block of if/else to the cmd
#    to make debugging easier :)))
#  **/
import socket
import threading
import json

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8165              # Arbitrary non-privileged port

header  = """HTTP/1.1 200 OK
Content-Length: {}

"""
headerLog  = """HTTP/1.1 {} OK
Content-Length: {}
Set-Cookie: username={}; Max-Age=3600: Path=/

"""

headerError = """HTTP/1.1 {} {}
Content-Length: {}

"""
#userDb in the format of user:pass
userDatabase = {"Username1":"Password1","Username2":"Password2",
                "Username3":"Password3","Username4":"Password4"}  

def handle(conn:socket.socket, ):
    with conn:
            print('Connected by', addr)
            try:
                data = conn.recv(1024)
                data=data.decode('utf-8')
                headerLine=data.split("\n")
                query=headerLine[0].split(" ")
                print(query)
                if "/" in query[1]:
                    #if its the first header of "/"
                    if "/" == query[1]:
                        fileBody=open("firstFile.html","rb")
                        body=fileBody.read()
                        thisHeader = header.format(len(body))
                        conn.sendall(thisHeader.encode())
                        conn.sendall(body)
                
                    if "/api/login" in query:
                        if "POST" in query:
                            print("Credential Entered by User: ",headerLine[-1])
                            uname=headerLine[-1].split(":")[0]
                            password=headerLine[-1].split(":")[1]
                            try:
                                if uname in userDatabase and userDatabase[uname]==password :
                                    print("LOGIN SUCCESS")
                                    loginMessage="Welcome {}".format(uname)
                                    # this sets the cookie to uname 
                                    newHeader=headerLog.format(200,len(loginMessage),uname)#{I have unique username for now}
                                    conn.sendall(newHeader.encode())
                                    conn.sendall(loginMessage.encode())
                                else:
                                    print("INVALID USERNAME/PASSWORD")
                                    loginMessage="INVALID USERNAME/PASSWORD"
                                    newHeader=headerError.format(401,"Unauthorized",len(loginMessage))
                                    conn.sendall(newHeader.encode())
                                    conn.sendall(loginMessage.encode())
                                
                            except:
                                print("ERROR 400's SOMETHING WENT WRONG WHILE LOGGING IN")
                        elif "DELETE" in query:
                            try :
                                print("NOW LOGGING OUT>>>>>>")
                                loginMessage="Logging out "
                                newHeader=headerLog.format(200,len(loginMessage),"") #This deletes the cookie
                                conn.sendall(newHeader.encode())
                                conn.sendall(loginMessage.encode())
                            except:
                                print("INTERNAL SERVER ERROR WHILE LOGGING OUT>>>>>>")
                                loginMessage="ERROR Logging out "
                                newHeader=headerError.format(401,"Unauthorized",len(loginMessage)) 
                                conn.sendall(newHeader.encode())
                                conn.sendall(loginMessage.encode())

                    if "/api/tweet" in query:
                        tweetFile = open("twitterDatabase.json", "rb")
                        tweetsFile = tweetFile.read()
                        tweets=json.loads(tweetsFile)
                        if "GET" in query:
                            print("Now getting tweets ............",)
                            newHeader=header.format(len(tweetsFile))
                            conn.sendall(newHeader.encode())
                            conn.sendall(tweetsFile)
                            
                        elif "POST" in query:
                            print("Now posting new tweet............",headerLine[-1])
                            uname=headerLine[-1].split(":")[0]
                            newTweet=headerLine[-1].split(":")[1]
                            try:
                                if uname in tweets:
                                    tweets[uname].append(newTweet)
                                else:
                                    tweets[uname]=[newTweet]
                                tweetWriteFile = open("twitterDatabase.json", "w")         
                                tweetWriteFile.write(json.dumps(tweets))
                                tweetMessage="Posting new tweet {}".format(newTweet)
                                newHeader=header.format(len(tweetMessage))
                                conn.sendall(header.encode())
                                conn.sendall(tweetMessage.encode())
                            except:
                                print("ERROR 400's SOMETHING WENT WRONG WHILE POSTING IT")
                        tweetFile.close()
                    else:
                        try:
                            filePath=query[1]
                            fileBody=open(filePath,"rb")
                            body=fileBody.read()
                            thisHeader = header.format(len(body))
                            conn.sendall(thisHeader.encode())
                            conn.sendall(body)
                        except:
                            print("ERROR 404: FILE NOT FOUND")
                            body="ERROR 404 FILE NOT FOUND"
                            thisHeader = headerError.format(401,"Unauthorized",len(body))
                            conn.sendall(thisHeader.encode())
                            conn.sendall(body.encode())
            except:
                print("ERROR 404: FILE NOT FOUND")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        newThread = threading.Thread(target=handle, args=(conn,))
        newThread.start()
        

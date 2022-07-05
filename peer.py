# /**
#  * peer.py
#  * COMP 3010
#  * INSTRUCTOR : Robert Guiderian
#  *
#  * @author Jaspreeet Singh, 7859706
#  * @version 16th June,2022
#  * PURPOSE: The purpose of this class is to make a 
#  * a blockchain peer that keeps and tracks of the the blockchain implemented
#  * and stores messages in blocks
#  **/
import hashlib
import socket
import json
import sys 
import uuid
import time
import random
import copy
# server host and port that we send flooding to
serverHost = 'eagle.cs.umanitoba.ca'
serverPort = 8999

# create an INET, STREAMing socket
peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peerSocket.bind(('', 8165))

# Dictionaries to keep track of the peers, consensus, peer that sent stats of the max hash/height
# chain and verified blockchain respectively
peerDict={}
statCountList={}
statsReplyList={}
heightList={}
validBlockchain={}

# variable that triggeres to do consensus upon joining the network
doConsunsus=30
# Our peer hostname and given port
hostname = socket.gethostbyname(socket.gethostname())
print("listening on interface " + hostname)
port = peerSocket.getsockname()[1]
print('listening on port:', port)

# Following are the messages type that we send to peer and the server hosts
floodMessage={
   "type": "FLOOD",
   "host": hostname,
   "port": 8165,
   "id": str(uuid.uuid4()),
   "name": "Jass's ultimate peer "
}

floodReply={
   "type": "FLOOD_REPLY",
   "host": hostname,
   "port": 8165,
   "name": "Jass's ultimate peer "
}

getBlockMessage={
   "type": "GET_BLOCK",
   "height": 0
}

statsMessage = {
    "type": "STATS"
}

sendStatsReply={
   "type": "STATS_REPLY",
   "height": 0,
   "hash": "" 
}

#validate function to 
def validate(blockStats):
    print("Validating the chain..........")
    for block in blockStats:
        if(block==0):
            m = hashlib.sha256()
            # Who
            m.update(str(blockStats[block]['minedBy']).encode())
            # messages
            for message in blockStats[block]['messages']:
                # print(message)    
                m.update(str(message).encode())
            # timestamp
            m.update(int(blockStats[block]['timestamp']).to_bytes(8, 'big'))
            # nonce
            m.update(str(blockStats[block]['nonce']).encode())
            if(m.hexdigest()==blockStats[block]['hash']):
                validBlockchain[blockStats[block]['height']]=blockStats[block]
            else:
                print("\n===========================================")
                print("INVALID BLOCK SENT AT HASH",blockStats[block]['hash'])
        else:
            m = hashlib.sha256()
            # previous hash
            m.update(str(blockStats[block-1]['hash']).encode())
            # Who
            m.update(str(blockStats[block]['minedBy']).encode())
            # messages
            for message in blockStats[block]['messages']:
                # print(message)    
                m.update(str(message).encode())
            # timestamp
            m.update(int(blockStats[block]['timestamp']).to_bytes(8, 'big'))
            # nonce
            m.update(str(blockStats[block]['nonce']).encode())
            if(m.hexdigest()==blockStats[block]['hash']):
                validBlockchain[blockStats[block]['height']]=blockStats[block]
            else:
                print("\n===========================================")
                print("INVALID BLOCK SENT AT HASH",blockStats[block]['hash'])
    return(validBlockchain)
# with connection
with peerSocket:
    try:
        peerDict={}                                                     # empty the peer list before flooding# this removes dead peer
        heightList={}                                                   # empty the chain before flooding
        peerSocket.settimeout(500)                                        #Timeout set to 5 secs
        # To send out the initial flooding to all the peers
        print("Flooding .........")
        floodmsg=json.dumps(floodMessage)
        peerSocket.sendto(floodmsg.encode(), (serverHost, serverPort))
        floodResponse = peerSocket.recvfrom(1024)
        floodStats = json.loads(floodResponse[0])
        startTime=time.time()                                           #statTime to keep track of time and flood every 30secs
        consensusStartTime=time.time()                                  #used to do consesus every few minutes
        timeout=time.time()                                             # to od timeout of the while loop inside
        while floodResponse:                                            #while there is response from peers
            floodResponse = peerSocket.recvfrom(1024)
            floodStats = json.loads(floodResponse[0])
            currentTime=time.time()
            # if its more than 30 secs flood again
            if((currentTime-startTime)>30):                             
                floodMessage['id']=str(uuid.uuid4())
                floodmsg=json.dumps(floodMessage)
                peerSocket.sendto(floodmsg.encode(), (serverHost, serverPort))# send the floodmessage again so that I am not dropped                
                if(len(peerDict)!=0):
                    # I am using deepcopy here to prevent the loop terminate 
                    # when a peer is deleted from the same list
                    newPeerDict=copy.deepcopy(peerDict)
                    for peer in newPeerDict:
                        #BONUS FLOODING it sends floodmessage to all known peers
                        peerSocket.sendto(floodmsg.encode(), (peer))
                        #To delete the non-active peers
                        if((time.time()-int(peerDict[peer]['ping']))>90):
                            print(f"Removing peer: {peerDict.pop(peer)} due to inactiveness")
                        
                floodResponse = peerSocket.recvfrom(1024)
                floodStats = json.loads(floodResponse[0])
                startTime=time.time()                                           #reset the start time
            
            #if there is more than 180 secs or CONSENSUS command is sent, do consensus
            if(floodStats['type']== "CONSENSUS"):
                print("Consesus message Recieved:   ")
            if((time.time()-consensusStartTime)> doConsunsus or floodStats['type']== "CONSENSUS"): 
                doConsunsus=180                                                 #every other consensus time is after 180secs
                #empty the consensus lists
                statCountList={}                                                #this list saves the hash/hieght combo and thier votes
                statsReplyList={}                                               #this list saves the peers that send those hash/height combo
                # for every peer active on the network send stat message and wait for stat reply
                print("TIME to do consensus......................")
                for peer in peerDict:
                    try:
                        statmsg = json.dumps(statsMessage)
                        peerSocket.sendto(statmsg.encode(), (peer))
                        response = peerSocket.recv(1024)
                        stats = json.loads(response)
                        #below code is timeout
                        while(stats['type']!='STATS_REPLY'):
                            response = peerSocket.recv(1024)
                            stats = json.loads(response)
                            currTime=time.time()
                            # to timeout every 5 sec
                            if(currTime-timeout>5):
                                timeout=time.time()
                                break
                        # if the reply sent if of type STATS_REPLY save hash/hieght commbo and peers that sent them
                        if(stats['type']=='STATS_REPLY'):
                            if(stats['height']!= 0 and stats['hash']!= None):               #if the height and hash is valid
                                #if the combo already exixts increase the count else initialise new one
                                if((stats['height'],stats['hash']) in statCountList):       
                                    statCountList[(stats['height'],stats['hash'])]+=1
                                else:
                                    statCountList[(stats['height'],stats['hash'])]=1
                                #if the combo already in the peer list append else create a new one
                                if((stats['height'],stats['hash']) in statsReplyList):
                                    statsReplyList[(stats['height'],stats['hash'])].append(peerDict[peer])
                                else:
                                    statsReplyList[(stats['height'],stats['hash'])]=[peerDict[peer]]
                    except peerSocket.timeout:
                        print("Timed out! Peer not responding to stat message: ", peer)
                consensusStartTime=time.time()                                  #reset the consesStartTime   
                # when the above lists are set, we then loadbalance send get block messages
                # if the cosensus list is not empty
                if(len(statCountList)!=0):
                    print("Votes count list : \n",statCountList)
                    #get the hash/height combo with max votes
                    maxVotes = max(statCountList, key=statCountList.get)
                    print("\nConcensus Given to chain of height: ", maxVotes[0],"and hash: ",maxVotes[1])
                    print("Sending get Block requests to random peers")
                    # for height 0 to n-1 send get block request to random peer in our list
                    for i in range(maxVotes[0]):
                        #Loadbalnce using random 
                        #it sends get block message to a random peer
                        statsList=statsReplyList[maxVotes]
                        randomPeer = random.choice(statsList)
                        getBlockMessage['height']=i                     #Set the height and send the request                
                        BlockMessage=json.dumps(getBlockMessage)
                        peerSocket.sendto(BlockMessage.encode(), floodResponse[1])
                        response = peerSocket.recvfrom(1024)            #This gives the tuple of message and details of the sender
                        blockStats = json.loads(response[0])
                        # if the reply is of type GET_BLOCK_REPLY
                        if(blockStats['type']=='GET_BLOCK_REPLY'):
                            heightList[blockStats['height']]=blockStats     # add it to our list of height
                            # print(blockStats)
                            print("\n Got block: ",blockStats)
                    #for the missing block in our list
                    #we resend the same request again 
                    #I know it is another loop but it will only run a few times at max for missing hieghts
                    for i in range(maxVotes[0]):
                        getBlockTimeout=time.time()
                        if(len(heightList)!=0):
                            if  i not in heightList:
                                print("Resending request for missing height: ",i)
                                statsList=statsReplyList[maxVotes]
                                randomPeer = random.choice(statsList)
                                getBlockMessage['height']=i                                
                                BlockMessage=json.dumps(getBlockMessage)
                                peerSocket.sendto(BlockMessage.encode(), floodResponse[1])
                                response = peerSocket.recvfrom(1024)            
                                blockStats = json.loads(response[0])
                                #timeout for the GET_BLOCK_REPLY
                                #only proceed if we either have GET_BLOCK_REPLY or 5 secs are done
                                while(blockStats['type']!='GET_BLOCK_REPLY'):
                                    response = peerSocket.recv(1024)
                                    blockStats = json.loads(response)
                                    currTime=time.time()
                                    # to timeout every 5 sec
                                    if(currTime-getBlockTimeout>5):
                                        getBlockTimeout=time.time()
                                        break
                                if(blockStats['type']=='GET_BLOCK_REPLY'):
                                    heightList[blockStats['height']]=blockStats  
                                    print("\n Got block: ",blockStats)
                        else:
                            print("Empty hieght list")
                        # if there is still some blocks left to add
                        # it won't run 99.99999999% of the time
                        if(len(heightList)<maxVotes[0]):
                            for i in range(maxVotes[0]):
                                if  i not in heightList:
                                    print("Resending request for missing height: ",i)
                                    statsList=statsReplyList[maxVotes]
                                    randomPeer = random.choice(statsList)
                                    getBlockMessage['height']=i                                
                                    BlockMessage=json.dumps(getBlockMessage)
                                    peerSocket.sendto(BlockMessage.encode(), floodResponse[1])
                                    response = peerSocket.recvfrom(1024)            
                                    blockStats = json.loads(response[0])
                                    if(blockStats['type']=='GET_BLOCK_REPLY'):
                                        heightList[blockStats['height']]=blockStats  
                                        print("\n Got block: ",blockStats)
                    validBlockchain=validate(heightList)
                    print("My Blockchain after validation is: \n",validBlockchain)
            #if stats received is of type FLOOD_REPLY 
            # if(floodStats['type']=='FLOOD_REPLY'):
            #     print(floodStats)   
            # if stats recieved is of type STATS send our hash/height combo to the sneder    
            if(floodStats['type']=='STATS'):
                if(len(statCountList)!=0):
                    print("Request recieved: ",floodStats)
                    #count the max votes
                    maxVotes = max(statCountList, key=statCountList.get)
                    sendStatsReply['height']=maxVotes[0]
                    sendStatsReply['hash']=maxVotes[1]
                    #send out the stat reply to that peer
                    print("Sent: ",sendStatsReply)
                    sendStatsReplyMessage=json.dumps(sendStatsReply)
                    peerSocket.sendto(sendStatsReplyMessage.encode(), floodResponse[1])   #floodResponse[1] gives the host and port of the sender 
                    peerSocket.sendto(sendStatsReplyMessage.encode(), (serverHost, serverPort))   #to show it up on the website UDP:))
            #if the stats is of type FLOOD update our peers list
            # and send flood Reply to them 
            if(floodStats['type']=='FLOOD'):
                # only add a new one using unique combo of host and port except not me
                # note that id's are not unique (trid that already)
                if((floodStats['host'],floodStats['port']) not in peerDict and floodStats['name'] != "Jass's ultimate peer "):
                    peerDict[(floodStats['host'],floodStats['port'])]={'name':floodStats['name'],'id':floodStats['id'],'ping':time.time()}
                    print("We have a new peer:",floodStats) 
                    #send the flood Reply message to them
                    floodReplyMessage=json.dumps(floodReply)
                    peerSocket.sendto(floodReplyMessage.encode(), (floodStats['host'], floodStats['port']))
                elif(floodStats['host'],floodStats['port'])  in peerDict and floodStats['name'] != "Jass's ultimate peer ":
                    peerDict[(floodStats['host'],floodStats['port'])]['ping']=time.time()
            #if we get a block message send out the block details from our chain    
            if(floodStats['type']=='GET_BLOCK'):
                #sends out blocks to other peer who requested them
                if(len(validBlockchain)!=0):
                    height=floodStats['height']
                    if(height <=len(validBlockchain)):
                        sendblockReplyMessage=json.dumps(validBlockchain[height])
                        peerSocket.sendto(sendblockReplyMessage.encode(), floodResponse[1]) 
            #if someone annouced a new block
            if(floodStats['type']=='ANNOUNCE'):
                print("Somebody announced a new block")
                #check if we have validated the list or not
                if(len(heightList)!=0):
                    #if we did
                    heightList[floodStats['height']]=floodStats
                    #add and validate the new block
                    validate(heightList)
    except Exception as e:
        print("general exception")
        print(e)
        sys.exit(1)
    except peerSocket.timeout:
        print("Timed out! Peer not responding?")
        sys.exit(1)

